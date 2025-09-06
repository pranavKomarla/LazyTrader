# Newspage package
from .news_router import router as news_router
from .summarize_router import router as summarize_router

__all__ = ["news_router", "summarize_router"]
