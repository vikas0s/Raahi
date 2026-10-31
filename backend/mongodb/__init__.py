"""
MongoDB module for Raahi Multi-Modal Mobility Platform.
"""
from .connection import (
    get_async_client,
    get_async_db,
    get_sync_client,
    get_sync_db,
    close_mongo_connection,
    check_mongo_health,
    get_mongo_uri,
    get_mongo_db_name
)
from .indexes import init_async_indexes, init_sync_indexes
from .seeder import seed_mongodb

__all__ = [
    "get_async_client",
    "get_async_db",
    "get_sync_client",
    "get_sync_db",
    "close_mongo_connection",
    "check_mongo_health",
    "init_async_indexes",
    "init_sync_indexes",
    "seed_mongodb",
    "get_mongo_uri",
    "get_mongo_db_name"
]

