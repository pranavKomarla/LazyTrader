import httpx
from typing import List, Optional
from app.core.config import config
from pydantic import ValidationError
from app.domain.news.models.alphavantage_model import AlphavantageAPINewsResponse

class AlphaVantageClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.ALPHAVANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"
        self.client = httpx.AsyncClient()
    
    async def get_news_sentiment(self, tickers: Optional[str] = None, topics: Optional[str] = None, limit: int = 50) -> AlphavantageAPINewsResponse:
        """Get news sentiment for specific tickers"""
        params = {
            "function": "NEWS_SENTIMENT",
            "apikey": self.api_key,
            "limit": limit
        }
        
        if tickers is not None:
            params["tickers"] = tickers
        if topics is not None:
            params["topics"] = topics
        
        resp = await self.client.get(self.base_url, params=params)
        resp.raise_for_status()
        data = resp.json()

        # Pydantic v2 preferred entry-point:
        try:
            return AlphavantageAPINewsResponse.model_validate(data)
        except ValidationError as e:
            # log and re-raise with context (or convert to your domain error)
            # logger.exception("AlphaVantage response validation failed: %s", e)
            raise
    
    async def get_company_news(self, symbol: str, limit: int = 50) -> AlphavantageAPINewsResponse:
        """Get company-specific news"""
        return await self.get_news_sentiment(tickers=symbol, limit=limit)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()