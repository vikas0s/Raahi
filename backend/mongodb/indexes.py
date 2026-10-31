"""
MongoDB index initialization and verification for Raahi Transit Platform.
Establishes 2dsphere geospatial indexes, uniqueness constraints, and compound query indexes.
"""
import logging
from pymongo import ASCENDING, DESCENDING, GEOSPHERE, TEXT, IndexModel
from pymongo.database import Database
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("raahi.mongodb.indexes")


async def init_async_indexes(db: AsyncIOMotorDatabase):
    """Initializes all necessary MongoDB indexes asynchronously."""
    logger.info("Initializing MongoDB indexes...")

    try:
        # 1. Cities
        await db.cities.create_index([("name", ASCENDING)], unique=True)
        await db.cities.create_index([("is_active", ASCENDING)])

        # 2. Stations (Geospatial & Search)
        await db.stations.create_index([("location", GEOSPHERE)])
        await db.stations.create_index([("city_id", ASCENDING), ("name", ASCENDING)])
        await db.stations.create_index([("external_stop_id", ASCENDING)], sparse=True)
        await db.stations.create_index([("stop_type", ASCENDING)])

        # 3. Transit Agencies
        await db.transit_agencies.create_index([("city_id", ASCENDING)])

        # 4. Routes
        await db.routes.create_index([("city_id", ASCENDING)])
        await db.routes.create_index([("agency_id", ASCENDING)])

        # 5. Trips
        await db.trips.create_index([("route_id", ASCENDING)])
        await db.trips.create_index([("service_id", ASCENDING)])

        # 6. Stop Times
        await db.stop_times.create_index([("trip_id", ASCENDING), ("stop_sequence", ASCENDING)])
        await db.stop_times.create_index([("stop_id", ASCENDING)])

        # 7. Users
        await db.users.create_index([("email", ASCENDING)], unique=True)
        await db.users.create_index([("email_normalized", ASCENDING)], unique=True, sparse=True)

        # 8. Saved Routes
        await db.saved_routes.create_index([("user_id", ASCENDING), ("city", ASCENDING)])
        await db.saved_routes.create_index([("created_at", DESCENDING)])

        # 9. Saved Places
        await db.saved_places.create_index([("user_id", ASCENDING)])

        # 10. User Preferences
        await db.user_preferences.create_index([("user_id", ASCENDING)], unique=True)

        # 11. AI Conversations
        await db.ai_conversations.create_index([("session_id", ASCENDING)], unique=True)
        await db.ai_conversations.create_index([("user_id", ASCENDING)])

        # 12. Recent Searches
        await db.recent_searches.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])

        logger.info("MongoDB indexes successfully created/verified.")
    except Exception as e:
        logger.error(f"Error initializing MongoDB indexes: {e}")


def init_sync_indexes(db: Database):
    """Initializes indexes synchronously (for seeder or migration scripts)."""
    logger.info("Initializing MongoDB indexes synchronously...")
    try:
        db.cities.create_index([("name", ASCENDING)], unique=True)
        db.cities.create_index([("is_active", ASCENDING)])

        db.stations.create_index([("location", GEOSPHERE)])
        db.stations.create_index([("city_id", ASCENDING), ("name", ASCENDING)])
        db.stations.create_index([("external_stop_id", ASCENDING)], sparse=True)
        db.stations.create_index([("stop_type", ASCENDING)])

        db.transit_agencies.create_index([("city_id", ASCENDING)])

        db.routes.create_index([("city_id", ASCENDING)])
        db.routes.create_index([("agency_id", ASCENDING)])

        db.trips.create_index([("route_id", ASCENDING)])
        db.trips.create_index([("service_id", ASCENDING)])

        db.stop_times.create_index([("trip_id", ASCENDING), ("stop_sequence", ASCENDING)])
        db.stop_times.create_index([("stop_id", ASCENDING)])

        db.users.create_index([("email", ASCENDING)], unique=True)
        db.users.create_index([("email_normalized", ASCENDING)], unique=True, sparse=True)

        db.saved_routes.create_index([("user_id", ASCENDING), ("city", ASCENDING)])
        db.saved_routes.create_index([("created_at", DESCENDING)])

        db.saved_places.create_index([("user_id", ASCENDING)])
        db.user_preferences.create_index([("user_id", ASCENDING)], unique=True)

        db.ai_conversations.create_index([("session_id", ASCENDING)], unique=True)
        db.recent_searches.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])

        logger.info("Sync MongoDB indexes verified successfully.")
    except Exception as e:
        logger.error(f"Error in init_sync_indexes: {e}")

