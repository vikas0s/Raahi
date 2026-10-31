"""
Persistent MongoDB and SQLite storage for Saved Routes and User Commutes.
Uses MongoDB as primary persistent data store with automatic SQLite fallback.
"""
import os
import uuid
import logging
from typing import List, Optional
from datetime import datetime, timezone
from .models import SavedRoute, SavedRouteCreate

logger = logging.getLogger("raahi.storage")

def _get_mongo_coll():
    try:
        from .mongodb.connection import get_sync_db
        db = get_sync_db()
        return db.saved_routes
    except Exception as e:
        logger.warning(f"Could not connect to MongoDB for storage: {e}")
        return None

def init_db():
    """Initializes storage in MongoDB and fallback SQLite."""
    try:
        from .mongodb.seeder import seed_mongodb
        seed_mongodb()
        logger.info("MongoDB storage initialized successfully.")
    except Exception as e:
        logger.warning(f"MongoDB init failed, falling back to SQLite: {e}")

    # Initialize SQLite fallback
    try:
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), "raahi_transit.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_routes (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                city TEXT NOT NULL,
                preferred_mode TEXT NOT NULL,
                created_at TEXT NOT NULL,
                typical_duration_minutes INTEGER NOT NULL,
                typical_fare_inr REAL NOT NULL,
                typical_transfers INTEGER NOT NULL,
                current_delay_minutes INTEGER DEFAULT 0,
                active_status TEXT DEFAULT 'Normal Service'
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Fallback SQLite init error: {e}")


def get_all_saved_routes(city: Optional[str] = None) -> List[SavedRoute]:
    """Retrieve saved routes from MongoDB with fallback to SQLite."""
    # 1. Try MongoDB
    coll = _get_mongo_coll()
    if coll is not None:
        try:
            q = {"user_id": "user-demo-default"}
            if city:
                q["city"] = city
            docs = list(coll.find(q).sort("created_at", -1))
            if docs:
                return [
                    SavedRoute(
                        id=str(d.get("_id") or d.get("id")),
                        name=d.get("name", "Saved Commute"),
                        origin=d.get("origin", ""),
                        destination=d.get("destination", ""),
                        city=d.get("city", "Delhi NCR"),
                        preferred_mode=d.get("preferred_mode", "fastest"),
                        created_at=str(d.get("created_at", "")),
                        typical_duration_minutes=int(d.get("typical_duration_minutes", 30)),
                        typical_fare_inr=float(d.get("typical_fare_inr", 25.0)),
                        typical_transfers=int(d.get("typical_transfers", 0)),
                        current_delay_minutes=int(d.get("current_delay_minutes", 0)),
                        active_status=d.get("active_status", "Normal Service")
                    )
                    for d in docs
                ]
        except Exception as e:
            logger.warning(f"MongoDB fetch failed, falling back to SQLite: {e}")

    # 2. SQLite Fallback
    try:
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), "raahi_transit.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if city:
            cursor.execute("SELECT * FROM saved_routes WHERE city = ? ORDER BY created_at DESC", (city,))
        else:
            cursor.execute("SELECT * FROM saved_routes ORDER BY created_at DESC")
        rows = cursor.fetchall()
        routes = [SavedRoute(**dict(row)) for row in rows]
        conn.close()
        return routes
    except Exception as e:
        logger.error(f"SQLite fetch error: {e}")
        return []


def create_saved_route(route: SavedRouteCreate) -> SavedRoute:
    """Save a route into MongoDB and SQLite."""
    route_id = f"sr-{uuid.uuid4().hex[:10]}"
    now_str = datetime.now(timezone.utc).isoformat()
    now_dt = datetime.now(timezone.utc)

    # 1. Save into MongoDB
    coll = _get_mongo_coll()
    if coll is not None:
        try:
            doc = {
                "_id": route_id,
                "id": route_id,
                "user_id": "user-demo-default",
                "name": route.name,
                "origin": route.origin,
                "destination": route.destination,
                "city": route.city,
                "preferred_mode": route.preferred_mode,
                "created_at": now_dt,
                "typical_duration_minutes": route.typical_duration_minutes,
                "typical_fare_inr": route.typical_fare_inr,
                "typical_transfers": route.typical_transfers,
                "current_delay_minutes": route.current_delay_minutes,
                "active_status": route.active_status
            }
            coll.replace_one({"_id": route_id}, doc, upsert=True)
        except Exception as e:
            logger.warning(f"Could not persist saved route to MongoDB: {e}")

    # 2. Save into SQLite
    try:
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), "raahi_transit.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO saved_routes (
                id, name, origin, destination, city, preferred_mode,
                created_at, typical_duration_minutes, typical_fare_inr,
                typical_transfers, current_delay_minutes, active_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            route_id,
            route.name,
            route.origin,
            route.destination,
            route.city,
            route.preferred_mode,
            now_str,
            getattr(route, "typical_duration_minutes", 30),
            getattr(route, "typical_fare_inr", 40.0),
            getattr(route, "typical_transfers", 0),
            getattr(route, "current_delay_minutes", 0),
            getattr(route, "active_status", "Normal Service")
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"SQLite save error: {e}")

    return SavedRoute(
        id=route_id,
        name=route.name,
        origin=route.origin,
        destination=route.destination,
        city=route.city,
        preferred_mode=route.preferred_mode,
        created_at=now_str,
        typical_duration_minutes=getattr(route, "typical_duration_minutes", 30),
        typical_fare_inr=getattr(route, "typical_fare_inr", 40.0),
        typical_transfers=getattr(route, "typical_transfers", 0),
        current_delay_minutes=getattr(route, "current_delay_minutes", 0),
        active_status=getattr(route, "active_status", "Normal Service")
    )


def delete_saved_route(route_id: str) -> bool:
    """Delete a saved route from MongoDB and SQLite."""
    deleted_mongo = False
    coll = _get_mongo_coll()
    if coll is not None:
        try:
            res = coll.delete_one({"_id": route_id})
            deleted_mongo = res.deleted_count > 0
        except Exception as e:
            logger.warning(f"MongoDB delete error: {e}")

    deleted_sqlite = False
    try:
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), "raahi_transit.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM saved_routes WHERE id = ?", (route_id,))
        conn.commit()
        deleted_sqlite = cursor.rowcount > 0
        conn.close()
    except Exception as e:
        logger.warning(f"SQLite delete error: {e}")

    return deleted_mongo or deleted_sqlite
