# LLM summarization service
from typing import List
from app.domain.news.models import Article, ArticleSummary, PageRecap
from datetime import datetime

async def summarize_article(article: Article) -> ArticleSummary:
    """
    Summarize a single article using LLM
    For now, return a stub summary
    """
    # TODO: Implement actual LLM summarization
    return ArticleSummary(
        article_id=article.id,
        tldr=f"Summary of: {article.title}",
        model="stub-llm-0.1",
        created_at=datetime.utcnow()
    )

async def summarize_page(articles: List[Article]) -> PageRecap:
    """
    Summarize a page of articles using LLM
    For now, return a stub recap
    """
    # TODO: Implement actual LLM page summarization
    return PageRecap(
        recap_text=f"Recap of {len(articles)} articles",
        themes=[{"topic": "general", "description": "Market news"}],
        model="stub-llm-0.1",
        created_at=datetime.utcnow()
    )
