from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
import asyncio
from typing import List
from datetime import datetime, timezone
import json
from app.domain.llm_summarization.services.llm_prompts import map_prompt, reduce_article_prompt, reduce_category_prompt
from app.domain.llm_summarization.models.llm_summarization_model import CategoryBrief
from app.core.config import config
from app.domain.llm_summarization.services.llm_prompts import parser


def build_map_chain(llm: ChatOpenAI, n_bullets: int):
    return map_prompt.partial(n_bullets=str(n_bullets)) | llm | parser # "pipe the output of one step to the next" prompt -> llm -> parser


def build_reduce_article_chain(llm: ChatOpenAI):
    return reduce_article_prompt | llm | parser

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