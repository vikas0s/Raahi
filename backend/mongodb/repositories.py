"""
Repository query layer for Raahi MongoDB integration.
Provides clean async operations, projections, input sanitization, and error handling.
"""
import re
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from .models import (
    CityDocument, StationDocument, RouteDocument, SavedRouteDocument,
    SavedPlaceDocument, UserPreferenceDocument, AIConversationDocument,
    current_utc_time
)


def _clean_doc(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not doc:
        return None
    # Ensure _id is mapped to id
    if "_id" in doc and "id" not in doc:
        doc["id"] = str(doc["_id"])
    return doc


class CityRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.coll = db.cities

    async def get_all(self, active_only: bool = True) -> List[Dict[str, Any]]:
        query = {"is_active": True} if active_only else {}
        cursor = self.coll.find(query).sort("name", 1)
        results = []
        async for doc in cursor:
            results.append(_clean_doc(doc))
        return results

    async def get_by_id_or_name(self, identifier: str) -> Optional[Dict[str, Any]]:
        if not identifier:
            return None
        clean = identifier.strip()
        doc = await self.coll.find_one({
            "$or": [
                {"_id": clean.lower()},
                {"name": {"$regex": f"^{re.escape(clean)}$", "$options": "i"}},
                {"name": {"$regex": re.escape(clean), "$options": "i"}}
            ]
        })
        return _clean_doc(doc)


class StationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.coll = db.stations

    async def get_by_city(
        self,
        city_id: Optional[str] = None,
        stop_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {}
        if city_id:
            query["city_id"] = city_id
        if stop_type:
            query["stop_type"] = stop_type

        cursor = self.coll.find(query).sort("name", 1).skip(offset).limit(limit)
        results = []
        async for doc in cursor:
            results.append(_clean_doc(doc))
        return results

    async def search(
        self,
        query: str,
        city_id: Optional[str] = None,
        limit: int = 15
    ) -> List[Dict[str, Any]]:
        if not query or len(query.strip()) < 2:
            return []
        pattern = re.escape(query.strip())
        filter_q: Dict[str, Any] = {
            "$or": [
                {"name": {"$regex": pattern, "$options": "i"}},
                {"external_stop_id": {"$regex": f"^{pattern}$", "$options": "i"}}
            ]
        }
        if city_id:
            filter_q["city_id"] = city_id

        cursor = self.coll.find(filter_q).limit(limit)
        results = []
        async for doc in cursor:
            results.append(_clean_doc(doc))
        return results

    async def find_nearby(
        self,
        lat: float,
        lon: float,
        max_distance_meters: float = 3000,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Geospatial proximity query using MongoDB $near with GeoJSON Point."""
        cursor = self.coll.find({
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    "$maxDistance": max_distance_meters
                }
            }
        }).limit(limit)
        results = []
        async for doc in cursor:
            results.append(_clean_doc(doc))
        return results

    async def get_by_id(self, station_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.coll.find_one({"_id": station_id})
        return _clean_doc(doc)


class RouteRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.coll = db.routes

    async def get_by_city(
        self,
        city_id: Optional[str] = None,
        route_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {}
        if city_id:
            query["city_id"] = city_id
        if route_type:
            query["route_type"] = route_type

        cursor = self.coll.find(query).sort("route_name", 1)
        results = []
        async for doc in cursor:
            results.append(_clean_doc(doc))
        return results


class SavedRouteRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.coll = db.saved_routes

    async def get_by_user(
        self,
        user_id: str = "user-demo-default",
        city: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {"user_id": user_id}
        if city:
            query["city"] = city
        cursor = self.coll.find(query).sort("created_at", -1)
        results = []
        async for doc in cursor:
            results.append(_clean_doc(doc))
        return results

    async def create(self, data: Dict[str, Any], user_id: str = "user-demo-default") -> Dict[str, Any]:
        route_id = data.get("id") or f"sr-{uuid.uuid4().hex[:10]}"
        doc = {
            "_id": route_id,
            "id": route_id,
            "user_id": user_id,
            "name": data.get("name", "Saved Journey"),
            "origin": data.get("origin", ""),
            "destination": data.get("destination", ""),
            "city": data.get("city", "Delhi NCR"),
            "preferred_mode": data.get("preferred_mode", "fastest"),
            "typical_duration_minutes": data.get("typical_duration_minutes", 30),
            "typical_fare_inr": float(data.get("typical_fare_inr", 25.0)),
            "typical_transfers": int(data.get("typical_transfers", 0)),
            "current_delay_minutes": int(data.get("current_delay_minutes", 0)),
            "active_status": data.get("active_status", "Normal Service"),
            "created_at": current_utc_time()
        }
        await self.coll.replace_one({"_id": route_id}, doc, upsert=True)
        return _clean_doc(doc)

    async def delete(self, route_id: str, user_id: str = "user-demo-default") -> bool:
        res = await self.coll.delete_one({"_id": route_id, "user_id": user_id})
        return res.deleted_count > 0


class SavedPlaceRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.coll = db.saved_places

    async def get_by_user(self, user_id: str = "user-demo-default") -> List[Dict[str, Any]]:
        cursor = self.coll.find({"user_id": user_id}).sort("created_at", 1)
        results = []
        async for doc in cursor:
            results.append(_clean_doc(doc))
        return results

    async def create(self, data: Dict[str, Any], user_id: str = "user-demo-default") -> Dict[str, Any]:
        place_id = data.get("id") or f"place-{uuid.uuid4().hex[:8]}"
        doc = {
            "_id": place_id,
            "id": place_id,
            "user_id": user_id,
            "name": data.get("name", "Saved Place"),
            "address": data.get("address", ""),
            "category": data.get("category", "favorite"),
            "latitude": float(data.get("latitude", 0.0)),
            "longitude": float(data.get("longitude", 0.0)),
            "city": data.get("city", "Delhi NCR"),
            "created_at": current_utc_time()
        }
        await self.coll.replace_one({"_id": place_id}, doc, upsert=True)
        return _clean_doc(doc)

    async def delete(self, place_id: str, user_id: str = "user-demo-default") -> bool:
        res = await self.coll.delete_one({"_id": place_id, "user_id": user_id})
        return res.deleted_count > 0


class UserPreferenceRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.coll = db.user_preferences

    async def get_by_user(self, user_id: str = "user-demo-default") -> Dict[str, Any]:
        doc = await self.coll.find_one({"user_id": user_id})
        if not doc:
            default_pref = {
                "_id": f"pref-{user_id}",
                "user_id": user_id,
                "preferred_language": "en",
                "selected_city": "Delhi NCR",
                "accessible_only": False,
                "reduced_motion": False,
                "travel_preferences": {
                    "fastest": True,
                    "cheapest": False,
                    "prefer_rail": True
                },
                "updated_at": current_utc_time()
            }
            await self.coll.insert_one(default_pref)
            return _clean_doc(default_pref)
        return _clean_doc(doc)

    async def update(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        updates["updated_at"] = current_utc_time()
        await self.coll.update_one(
            {"user_id": user_id},
            {"$set": updates},
            upsert=True
        )
        return await self.get_by_user(user_id)


class AIConversationRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.coll = db.ai_conversations

    async def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        doc = await self.coll.find_one({"session_id": session_id})
        if doc and "messages" in doc:
            return doc["messages"]
        return []

    async def append_message(
        self,
        session_id: str,
        role: str,
        content: str,
        user_id: str = "user-demo-default",
        city: Optional[str] = None
    ):
        new_msg = {
            "role": role,
            "content": content,
            "timestamp": current_utc_time()
        }
        await self.coll.update_one(
            {"session_id": session_id},
            {
                "$push": {"messages": new_msg},
                "$setOnInsert": {
                    "_id": f"conv-{session_id}",
                    "session_id": session_id,
                    "user_id": user_id,
                    "conversation_title": f"Journey Query {datetime.now().strftime('%d %b')}",
                    "city": city,
                    "created_at": current_utc_time()
                },
                "$set": {"updated_at": current_utc_time()}
            },
            upsert=True
        )

    async def reset(self, session_id: str):
        await self.coll.delete_one({"session_id": session_id})

