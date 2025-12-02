from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

parser = StrOutputParser()


map_prompt = ChatPromptTemplate.from_messages([
    ("system", (
    "You extract factual bullets from text. For any numbers, dates, or named entities, "
    "quote a short span (≤13 words). Output exactly {n_bullets} bullets. No preamble."
    )),
    ("human", "TEXT:\n{chunk}")
])


reduce_article_prompt = ChatPromptTemplate.from_messages([
    ("system", (
    "You are a precise summarizer. Combine bullets into a concise brief. "
    "Output sections exactly as:\n"
    "- Key Points (as many bullets you see fit, though we want to emphasize conciseness)\n"
    "- Takeaway (1 short paragraph)\n"
    "- Source: {url}"
    )),
    ("human", "TITLE: {title}\nBULLETS:\n{bullets}")
])


# Category long brief: ask for strict JSON to avoid heuristic parsing
reduce_category_prompt = ChatPromptTemplate.from_messages([
    ("system", (
    "You are an editor creating a long, structured brief for one news subtopic.\n"
    "You MUST return STRICT JSON with keys: overview, key_themes, implications, notable_data_points, top_sources.\n"
    "- overview: 2-3 sentences.\n"
    "- key_themes: 3-7 items; each has headline (≤10 words) and 2-4 bullets (short).\n"
    "- implications: 3-6 concise bullets, action-oriented if possible.\n"
    "- notable_data_points: 3-8 short facts with figures/dates if present.\n"
    "- top_sources: up to 5 objects {name, count}.\n"
    "Keep total under ~350 tokens. Return ONLY valid JSON."
    )),
    ("human", "CATEGORY: {category}\nDATE_RANGE: {since} → {until}\nBULLETS (one per line):\n{all_bullets}")
])