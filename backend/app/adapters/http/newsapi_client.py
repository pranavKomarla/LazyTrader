import httpx
from typing import Optional, List
from datetime import datetime, date, timedelta
from app.core.config import config
from app.domain.news.models.newsapi_model import NewsAPIResponse
from pydantic import ValidationError

'''
q='earnings', #earnings, ipo, merger, acquisition, etc.
sources='bbc-news,bloomberg,business-insider,financial-post,fortune,the-wall-street-journal,reuters',
domains='bbc.co.uk,techcrunch.com,bloomberg.com,businessinsider.com,financialpost.com,fortune.com,wsj.com,reuters.com,engadget.com,cnbc.com,theguardian.com,nytimes.com',
'''
class NewsAPIClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
        self.client = httpx.AsyncClient()
    
    async def get_everything(
        self,
        q: Optional[str] = None,
        sources: str = 'bbc-news,bloomberg,business-insider,financial-post,fortune,the-wall-street-journal,reuters',
        domains: str = 'bbc.co.uk,techcrunch.com,bloomberg.com,businessinsider.com,financialpost.com,fortune.com,wsj.com,reuters.com,engadget.com,cnbc.com,theguardian.com,nytimes.com',
        from_param: Optional[str] = None,
        to: Optional[str] = None,
        language: str = "en",
        sort_by: str = "publishedAt", #publishedAt, relevance, popularity -> publishedAt is the default, will return the most recent articles
        page_size: int = 100,
        page: int = 1,
        days_back: int = 7
    ) -> NewsAPIResponse:
        """Get articles from all sources"""

        current_date = datetime.now()
        start_date = current_date - timedelta(days=days_back)

        params = {
            "apiKey": self.api_key,
            "q": q,
            "sources": sources,
            "domains": domains,
            "from": start_date.isoformat(),
            "to": current_date.isoformat(),
            "language": language,
            "sortBy": sort_by,
            "pageSize": page_size,
            "page": page
        }
        
        # Only add parameters if they're provided
        if q is not None:
            params["q"] = q
        if from_param is not None:
            params["from"] = from_param
        if to is not None:
            params["to"] = to
        
        response = await self.client.get(f"{self.base_url}/everything", params=params)
        response.raise_for_status()
        data = response.json()
        # Pydantic v2 preferred entry-point:
        try:
            return NewsAPIResponse.model_validate(data)
        except ValidationError as e:
            # log and re-raise with context (or convert to your domain error)
            # logger.exception("AlphaVantage response validation failed: %s", e)
            raise
    
    async def get_top_headlines(
        self,
        country: str = None,
        category: str = None,
        sources: str = None,
        q: str = None,
        page_size: int = 100,
        page: int = 1
    ) -> NewsAPIResponse:
        """Get top headlines"""
        params = {
            "apiKey": self.api_key,
            "pageSize": page_size,
            "page": page
        }
        
        # Only add parameters if they're provided
        if country:
            params["country"] = country
        if category:
            params["category"] = category
        if sources:
            params["sources"] = sources
        if q:
            params["q"] = q
        
        response = await self.client.get(f"{self.base_url}/top-headlines", params=params)
        response.raise_for_status()
        data = response.json()
        
        # Pydantic v2 preferred entry-point:
        try:
            return NewsAPIResponse.model_validate(data)
        except ValidationError as e:
            # log and re-raise with context (or convert to your domain error)
            # logger.exception("AlphaVantage response validation failed: %s", e)
            raise
    
    async def get_sources(
        self,
        category: str = None,
        language: str = "en",
        country: str = None
    ) -> dict:
        """Get available news sources"""
        params = {
            "apiKey": self.api_key,
            "language": language
        }
        
        if category:
            params["category"] = category
        if country:
            params["country"] = country
        
        response = await self.client.get(f"{self.base_url}/sources", params=params)
        response.raise_for_status()
        return response.json()
    
    async def get_company_news(
        self,
        company: str,
        from_date: str = None,
        to_date: str = None,
        limit: int = 100
    ) -> NewsAPIResponse:
        """Get news about a specific company"""
        return await self.get_everything(
            q=company,
            from_param=from_date,
            to=to_date,
            page_size=limit
        )
    
    # async def get_financial_news(
    #     self,
    #     from_date: str = None,
    #     to_date: str = None,
    #     limit: int = 100
    # ) -> NewsAPIResponse:
    #     """Get financial news from business sources"""
    #     return await self.get_everything(
    #         q="finance OR stock OR market OR economy",
    #         sources="bloomberg,reuters,financial-times,cnbc,marketwatch",
    #         from_param=from_date,
    #         to=to_date,
    #         page_size=limit
    #     )
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
