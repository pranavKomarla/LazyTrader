from __future__ import annotations
from typing import Iterable, Optional, List, Any, Dict
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import UpdateOne, ASCENDING, DESCENDING
from pymongo.errors import BulkWriteError

from app.domain.news.models.base_model import Article

class ArticleRepository:
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        self.db = db
        self.collection: AsyncIOMotorCollection = db[collection_name]

    async def create_indexes(self) -> None:
        # _id index is created automatically by MongoDB, no need to create it manually
        await self.collection.create_index([("source", ASCENDING), ("published_at", DESCENDING)])
        await self.collection.create_index([("category", ASCENDING), ("published_at", DESCENDING)])
        await self.collection.create_index([("tickers", ASCENDING), ("published_at", DESCENDING)])
        await self.collection.create_index([("published_at", DESCENDING)])

    # ---- model <-> mongo ----
    # Converts a pydantic article into a mongo document
    @staticmethod
    def _to_mongo(article: Article) -> Dict[str, Any]:
        # Use Python mode so datetimes stay as datetime; HttpUrl/AnyUrl are str-like
        doc = article.model_dump(mode="python", exclude_none=True) 
        doc["_id"] = doc.pop("id")
        return doc

    # Converts a mongo document into a pydantic article
    @staticmethod
    def _from_mongo(doc: Optional[Dict[str, Any]]) -> Optional[Article]:
        if not doc:
            return None
        d = dict(doc)
        d["id"] = d.pop("_id")
        return Article.model_validate(d)

    # ---- CRUD ----
    async def upsert_one(self, article: Article) -> Article:
        doc = self._to_mongo(article)
        now = datetime.now(timezone.utc)
        doc.setdefault("created_at", now)
        doc["updated_at"] = now

        await self.collection.update_one(
            {"_id": doc["_id"]},
            {"$set": doc, "$setOnInsert": {"created_at": doc["created_at"]}},
            upsert=True,
        )
        saved = await self.collection.find_one({"_id": doc["_id"]})
        return self._from_mongo(saved)

    async def upsert_many(self, articles: Iterable[Article]) -> dict:
        ops = []
        now = datetime.now(timezone.utc)
        for a in articles:
            doc = self._to_mongo(a)
            doc.setdefault("created_at", now)
            doc["updated_at"] = now
            ops.append(
                UpdateOne(
                    {"_id": doc["_id"]},
                    {"$set": doc, "$setOnInsert": {"created_at": doc["created_at"]}},
                    upsert=True,
                )
            )
        if not ops:
            return {"matched": 0, "modified": 0, "upserted": 0}
        try:
            res = await self.collection.bulk_write(ops, ordered=False)
            return {
                "matched": res.matched_count,
                "modified": res.modified_count,
                "upserted": len(res.upserted_ids or []),
            }
        except BulkWriteError as e:
            # surface the first error; in prod you might log richer details
            raise e

    async def get_by_id(self, id_: str) -> Optional[Article]:
        doc = await self.collection.find_one({"_id": id_})
        return self._from_mongo(doc)

    async def delete_by_id(self, id_: str) -> int:
        res = await self.collection.delete_one({"_id": id_})
        return res.deleted_count

    async def list(
        self,
        *,
        category: Optional[str] = None,
        source: Optional[str] = None,
        ticker: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 50,
        skip: int = 0,
    ) -> List[Article]:
        q: Dict[str, Any] = {}
        if category:
            q["category"] = category
        if source:
            q["source"] = source
        if ticker:
            q["tickers"] = ticker
        if since:
            q["published_at"] = {"$gte": since}

        cursor = (
            self.collection.find(q)
            .sort([("published_at", DESCENDING), ("_id", ASCENDING)])
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [self._from_mongo(d) for d in docs]
