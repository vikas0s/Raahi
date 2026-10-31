"""
MongoDB connection manager and lifecycle handler for Raahi Transit Platform.
Uses the official PyMongo driver with AsyncMongoClient for asynchronous FastAPI request
handling, and MongoClient for synchronous background/seeding tasks.
"""
import os
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient, AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.database import Database

# Load root .env
root_env = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=root_env)

logger = logging.getLogger("raahi.mongodb")

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017").strip()
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "raahi").strip()

import asyncio

# Global async client and database references
_async_client: Optional[AsyncMongoClient] = None
_client_loop: Optional[asyncio.AbstractEventLoop] = None
_sync_client: Optional[MongoClient] = None


def get_mongo_uri() -> str:
    return MONGODB_URI


def get_mongo_db_name() -> str:
    return MONGODB_DATABASE


def get_async_client() -> AsyncMongoClient:
    """Returns the singleton official PyMongo AsyncMongoClient for the active event loop."""
    global _async_client, _client_loop
    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None

    if _async_client is None or (_client_loop is not None and current_loop is not None and _client_loop != current_loop):
        _async_client = AsyncMongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=4000,
            connectTimeoutMS=4000,
            socketTimeoutMS=5000,
            maxPoolSize=int(os.getenv("MONGO_MAX_POOL_SIZE", "50")),
            minPoolSize=int(os.getenv("MONGO_MIN_POOL_SIZE", "5"))
        )
        _client_loop = current_loop
    return _async_client


def get_async_db() -> AsyncDatabase:
    """Returns the singleton AsyncDatabase instance from PyMongo."""
    client = get_async_client()
    return client[MONGODB_DATABASE]


def get_sync_client() -> MongoClient:
    """Returns a synchronous PyMongo client (e.g. for seeders or offline scripts)."""
    global _sync_client
    if _sync_client is None:
        _sync_client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=4000,
            connectTimeoutMS=4000
        )
    return _sync_client


def get_sync_db() -> Database:
    """Returns synchronous PyMongo Database instance."""
    client = get_sync_client()
    return client[MONGODB_DATABASE]


async def close_mongo_connection():
    """Closes async MongoDB connection gracefully."""
    global _async_client, _client_loop
    if _async_client is not None:
        try:
            logger.info("Closing PyMongo AsyncMongoClient connection...")
            await _async_client.close()
        except Exception:
            pass
        finally:
            _async_client = None
            _client_loop = None
            logger.info("PyMongo AsyncMongoClient closed.")


def close_sync_mongo():
    """Closes sync MongoDB client."""
    global _sync_client
    if _sync_client is not None:
        _sync_client.close()
        _sync_client = None


async def check_mongo_health() -> Dict[str, Any]:
    """
    Checks MongoDB connectivity and latency without exposing credentials.
    Returns status, latency_ms, database name, and collection statistics.
    """
    start_time = time.perf_counter()
    try:
        db = get_async_db()
        pong = await db.command("ping")
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        collections = await db.list_collection_names()
        
        return {
            "status": "connected",
            "database": MONGODB_DATABASE,
            "engine": "MongoDB (PyMongo AsyncMongoClient)",
            "latency_ms": latency_ms,
            "collections_count": len(collections),
            "ping": bool(pong.get("ok")),
            "is_connected": True
        }
    except Exception as e:
        logger.warning(f"MongoDB health check failed: {e}")
        return {
            "status": "disconnected",
            "database": MONGODB_DATABASE,
            "engine": "MongoDB (PyMongo AsyncMongoClient)",
            "latency_ms": -1,
            "collections_count": 0,
            "ping": False,
            "is_connected": False,
            "error": "MongoDB service unreachable or connection timed out"
        }
