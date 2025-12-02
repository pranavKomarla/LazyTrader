from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
import asyncio
from typing import List, Optional
from datetime import datetime, timezone
import json
from app.domain.llm.services.llm_prompts import map_prompt, reduce_article_prompt, reduce_category_prompt
from app.domain.llm.models.llm_summarization_model import CategoryBrief
from app.core.config import config
from app.domain.llm.services.llm_prompts import parser
from app.domain.alerts.models.nl_alerts import IntentResult, Intent, Alert, AlertType, AlertStatus, create_event_alert, create_metric_alert, create_percent_change_alert, create_price_alert, normalize_metric_name






# News related routines

def build_map_chain(llm: ChatOpenAI, n_bullets: int):
    return map_prompt.partial(n_bullets=str(n_bullets)) | llm | parser # "pipe the output of one step to the next" prompt -> llm -> parser


def build_reduce_article_chain(llm: ChatOpenAI):
    return reduce_article_prompt | llm | parser

def build_reduce_category_chain(llm: ChatOpenAI): 
    return reduce_category_prompt | llm | parser

async def summarize_article_text(llm: ChatOpenAI, splitter: RecursiveCharacterTextSplitter, *, title: str, url: str | None, content: str, n_map_bullets: int) -> str:
    chunks = splitter.split_text(content) # splitting the content into chunks
    map_chain = build_map_chain(llm, n_bullets=n_map_bullets) # building the map chain
    sem = asyncio.Semaphore(config.MAX_MAP_CONCURRENCY) # semaphore to limit the number of concurrent map tasks

    async def _map_one(txt: str) -> str:
        async with sem: # acquiring a semaphore slot
            return await asyncio.to_thread(map_chain.invoke, {"chunk": txt}) # invoking the map chain which is synchronous but runs in a thread, so we use a to_thread to run it asynchronously


    mapped = await asyncio.gather(*(_map_one(c) for c in chunks)) # gathering the results of the map tasks
    bullet_block = "\n".join(mapped)

    reduce_chain = build_reduce_article_chain(llm)
    reduced: str = await asyncio.to_thread(
        reduce_chain.invoke,
        {"title": title or "(untitled)", "url": url or "", "bullets": bullet_block},
    )
    return reduced.strip()

# This function is designed for quick, lightweight summarization when you don't need the full Map-Reduce pipeline:
async def quick_tldr_bullets(llm: ChatOpenAI, splitter: RecursiveCharacterTextSplitter, *, content: str, n_bullets: int = 3) -> str:
    chunks = splitter.split_text(content)
    head = "\n\n".join(chunks[:2]) if chunks else content
    chain = build_map_chain(llm, n_bullets=n_bullets)
    return await asyncio.to_thread(chain.invoke, {"chunk": head})


async def reduce_category_long_brief(llm: ChatOpenAI, *, category: str, since_iso: str, until_iso: str, bullets_lines: List[str]) -> CategoryBrief:
    all_bullets = "\n".join(bullets_lines)
    chain = build_reduce_category_chain(llm)
    raw = await asyncio.to_thread(chain.invoke, {"category": category, "since": since_iso, "until": until_iso, "all_bullets": all_bullets})


    # Ensure strict JSON
    try:
        data = json.loads(raw)
    except Exception as e:
        # Attempt a simple fix (trim code fences etc.)
        raw2 = raw.strip().removeprefix("```").removesuffix("```")
        data = json.loads(raw2)


    # Validate shape lightly
    brief = CategoryBrief(
        overview=data.get("overview", ""),
        key_themes=data.get("key_themes", []),
        implications=data.get("implications", []),
        notable_data_points=data.get("notable_data_points", []),
        top_sources=data.get("top_sources", []),
        article_count=0, # filled by caller
        generated_at=datetime.now(timezone.utc),
    )
    return brief

# Alert Related Routines

# TODO Perhaps create a basemodel for the llm, idk though



async def parse_alert_prompt(
    llm: ChatOpenAI,
    user_id: str,
    prompt: str,
    *,
    default_channel: str = "email",
    default_channel_target: Optional[str] = None,
) -> Alert:
    """
    Main function: take a free-form user prompt and return a structured Alert.

    Does NOT persist anything yet. You can call `save_alert(alert)` after this.
    Raises ValueError if nothing parseable is found.
    """

    llm_tools = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0,
    ).bind_tools([create_price_alert, create_metric_alert, create_event_alert]) 

    msg = await llm_tools.ainvoke(prompt)

    if not msg.tool_calls:
        # You can get fancier: ask follow-up questions, etc.
        raise ValueError("Could not understand alert request from prompt.")

    # For now, just use the first tool call
    tool_call = msg.tool_calls[0]
    name = tool_call["name"]
    args = tool_call["args"]

    ticker = args.get("ticker", "").upper()

    # Map the tool call to your internal Alert object
    if name == "create_price_alert":
        alert = Alert(
            user_id=user_id,
            type=AlertType.PRICE_THRESHOLD,
            ticker=ticker,
            metric="price",
            operator=args["operator"],
            threshold=float(args["target"]),
            channel=default_channel,          # e.g. "email"
            channel_target=default_channel_target,
        )

    elif name == "create_metric_alert":
        metric_raw = args["metric"]
        normalized_metric = normalize_metric_name(metric_raw)

        alert = Alert(
            user_id=user_id,
            type=AlertType.METRIC_THRESHOLD,
            ticker=ticker,
            metric=normalized_metric,         # e.g. "pe"
            operator=args["operator"],
            threshold=float(args["target"]),
            channel=default_channel,
            channel_target=default_channel_target,
        )

    elif name == "create_event_alert":
        alert = Alert(
            user_id=user_id,
            type=AlertType.EVENT,
            ticker=ticker,
            event_type=args["event_type"],     # currently only "earnings"
            event_offset_days=int(args["offset_days"]),
            channel=default_channel,
            channel_target=default_channel_target,
        )

    elif name == "create_percent_change_alert":
        alert = Alert(
            user_id=user_id,
            type=AlertType.PERCENT_CHANGE,
            ticker=ticker,
            percent_change=float(args["percent"]),
            change_direction=args["direction"],
            change_period=args["period"],
            channel=default_channel,
            channel_target=default_channel_target,
        )

    # If using "from_creation", capture baseline_price now
    # if alert.change_period == "from_creation":
    #     current_price = await get_current_price(alert.ticker) # TODO create a get_current_price method
    #     alert.baseline_price = current_price

    else:
        raise ValueError(f"Unknown tool called: {name}")

    return alert


async def classify_intent(llm: ChatOpenAI, user_id: str, prompt: str) -> IntentResult:

    """
    Use the LLM to classify a raw user prompt into a high-level intent.

    The `llm` should be a ChatOpenAI (or compatible) model.
    """

    
    intent_llm = llm.with_structured_output(IntentResult)

    system_instructions = """
    You are an intent classifier for a stock assistant.

    You MUST choose exactly one of these intents for each user message:

    - create_alert: The user wants to create a new alert (price, P/E, earnings, etc.)
    - list_alerts: The user wants to see existing alerts that they have already created.
    - modify_alert: The user wants to change or cancel an existing alert.
    - info_question: The user is asking for information (e.g. what's the P/E, explain RSI, summarize news).
    - other: Anything else that does not fit the above categories.

    Return ONLY the intent field. Do not include any explanation in the output.
    """

    messages = [
        SystemMessage(content=system_instructions),
        HumanMessage(content=prompt),
    ]

    # This returns an IntentResult Pydantic model directly
    result: IntentResult = await intent_llm.ainvoke(messages)
    return result



async def handle_user_prompt(llm: ChatOpenAI, user_id: str, prompt: str):
    intent_result = await classify_intent(llm, prompt)

    if intent_result.intent == Intent.CREATE_ALERT:
        alert = await parse_alert_prompt(llm, user_id, prompt)
        # save_alert(alert), return confirmation message, etc.

    elif intent_result.intent == Intent.LIST_ALERTS:
        # list_alerts_for_user(user_id), maybe filter by ticker in prompt
        pass

    elif intent_result.intent == Intent.MODIFY_ALERT:
        # parse which alert they mean (by ticker / id) and cancel/modify
        pass

    elif intent_result.intent == Intent.INFO_QUESTION:
        # route to your “answer stock question / summarizer” pipeline
        pass

    else:
        # generic "I'm not sure" / fallback response
        pass


    
