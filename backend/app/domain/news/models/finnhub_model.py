from typing import Optional
from pydantic import BaseModel, HttpUrl
from datetime import datetime, timezone


class FinnhubAPIArticle(BaseModel):
    category: str
    datetime: int  # UNIX timestamp
    headline: str
    id: int
    image: Optional[HttpUrl] = None
    related: Optional[str] = None
    source: Optional[str] = None
    summary: Optional[str] = None
    url: HttpUrl

    # If you want datetime converted to a Python datetime automatically:
    @property
    def published_at(self) -> datetime:
        return datetime.fromtimestamp(self.datetime, tz=timezone.utc)
