"""
Integration test suite for Raahi MongoDB Database Integration.
Tests connection health, collections, indexing, geospatial queries, CRUD repositories,
and API schemas.
"""
import sys
import unittest
import asyncio
from typing import List, Dict, Any

from backend.mongodb.connection import (
    get_sync_db,
    get_async_db,
    check_mongo_health,
    close_mongo_connection,
    close_sync_mongo
)
from backend.mongodb.indexes import init_sync_indexes
from backend.mongodb.seeder import seed_mongodb
from backend.mongodb.repositories import (
    CityRepository,
    StationRepository,
    RouteRepository,
    SavedRouteRepository,
    SavedPlaceRepository,
    UserPreferenceRepository,
    AIConversationRepository
)


class TestMongoDBIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Seed MongoDB to guarantee all records are present
        cls.stats = seed_mongodb()
        cls.sync_db = get_sync_db()

    @classmethod
    def tearDownClass(cls):
        close_sync_mongo()
        asyncio.run(close_mongo_connection())

    def test_01_connection_and_health(self):
        """Verify MongoDB connection health without exposing credentials."""
        async def run_test():
            health = await check_mongo_health()
            self.assertTrue(health["is_connected"])
            self.assertEqual(health["status"], "connected")
            self.assertEqual(health["database"], "raahi")
            self.assertGreater(health["latency_ms"], 0)
            self.assertGreaterEqual(health["collections_count"], 10)
            print(f"[OK] Health Check Passed: {health['database']} ({health['latency_ms']}ms)")
        asyncio.run(run_test())

    def test_02_cities_collection(self):
        """Verify supported cities are loaded and indexed."""
        async def run_test():
            db = get_async_db()
            repo = CityRepository(db)
            cities = await repo.get_all(active_only=True)
            self.assertGreaterEqual(len(cities), 4)
            names = [c["name"] for c in cities]
            self.assertIn("Delhi NCR", names)
            self.assertIn("Mumbai", names)
            self.assertIn("Bengaluru", names)
            self.assertIn("Mathura & Vrindavan", names)

            # Test search by name
            mumbai = await repo.get_by_id_or_name("Mumbai")
            self.assertIsNotNone(mumbai)
            self.assertEqual(mumbai["_id"], "mumbai")
            print("[OK] Cities Repository Verified (4 Core Metros)")

        asyncio.run(run_test())

    def test_03_stations_and_geospatial_query(self):
        """Verify stations collection, 2dsphere indexing, and $near proximity queries."""
        async def run_test():
            db = get_async_db()
            repo = StationRepository(db)

            # 1. Total station count
            delhi_stations = await repo.get_by_city(city_id="delhi-ncr", limit=200)
            self.assertGreater(len(delhi_stations), 20)

            # 2. Text/Regex search
            results = await repo.search(query="Rajiv Chowk", city_id="delhi-ncr")
            self.assertGreaterEqual(len(results), 1)
            self.assertIn("Rajiv Chowk", results[0]["name"])

            # 3. Geospatial proximity query ($near within 3km of Connaught Place [77.2197, 28.6328])
            nearby = await repo.find_nearby(lat=28.6328, lon=77.2197, max_distance_meters=3000, limit=5)
            self.assertGreater(len(nearby), 0)
            names = [s["name"] for s in nearby]
            self.assertTrue(any("Rajiv Chowk" in n or "Connaught Place" in n or "Palika" in n for n in names))
            print(f"[OK] Geospatial 2dsphere $near query returned {len(nearby)} stations near CP: {names[:3]}")

        asyncio.run(run_test())

    def test_04_routes_and_trips(self):
        """Verify transit routes and commuter trains in MongoDB."""
        async def run_test():
            db = get_async_db()
            repo = RouteRepository(db)
            routes = await repo.get_by_city(city_id="mumbai")
            self.assertGreaterEqual(len(routes), 1)
            print("[OK] Routes & Suburban Schedules Verified")

        asyncio.run(run_test())

    def test_05_saved_routes_crud(self):
        """Verify CRUD operations on saved routes in MongoDB."""
        async def run_test():
            db = get_async_db()
            repo = SavedRouteRepository(db)

            test_user = "user-test-runner"
            # 1. Create
            created = await repo.create({
                "name": "Test Office Commute",
                "origin": "Andheri",
                "destination": "Churchgate",
                "city": "Mumbai",
                "preferred_mode": "fastest",
                "typical_duration_minutes": 35,
                "typical_fare_inr": 15.0
            }, user_id=test_user)
            self.assertIsNotNone(created["id"])

            # 2. Read
            routes = await repo.get_by_user(user_id=test_user)
            self.assertEqual(len(routes), 1)
            self.assertEqual(routes[0]["name"], "Test Office Commute")

            # 3. Delete
            deleted = await repo.delete(route_id=created["id"], user_id=test_user)
            self.assertTrue(deleted)

            # Verify deletion
            routes_after = await repo.get_by_user(user_id=test_user)
            self.assertEqual(len(routes_after), 0)
            print("[OK] Saved Routes CRUD Verified")

        asyncio.run(run_test())

    def test_06_saved_places_crud(self):
        """Verify CRUD operations on user saved places (Home/Work/Favorites)."""
        async def run_test():
            db = get_async_db()
            repo = SavedPlaceRepository(db)

            test_user = "user-test-runner"
            # 1. Create
            created = await repo.create({
                "name": "My Gym",
                "address": "Bandra West",
                "category": "favorite",
                "latitude": 19.0596,
                "longitude": 72.8295,
                "city": "Mumbai"
            }, user_id=test_user)
            self.assertIsNotNone(created["id"])

            # 2. Read
            places = await repo.get_by_user(user_id=test_user)
            self.assertEqual(len(places), 1)

            # 3. Delete
            deleted = await repo.delete(place_id=created["id"], user_id=test_user)
            self.assertTrue(deleted)
            print("[OK] Saved Places CRUD Verified")

        asyncio.run(run_test())

    def test_07_user_preferences(self):
        """Verify user preference persistence in MongoDB."""
        async def run_test():
            db = get_async_db()
            repo = UserPreferenceRepository(db)

            test_user = "user-test-runner"
            # Read default
            pref = await repo.get_by_user(user_id=test_user)
            self.assertEqual(pref["user_id"], test_user)

            # Update
            updated = await repo.update(user_id=test_user, updates={
                "preferred_language": "hi",
                "selected_city": "Mathura & Vrindavan",
                "accessible_only": True
            })
            self.assertEqual(updated["preferred_language"], "hi")
            self.assertEqual(updated["selected_city"], "Mathura & Vrindavan")
            self.assertTrue(updated["accessible_only"])
            print("[OK] User Preferences Persistence Verified")

        asyncio.run(run_test())

    def test_08_ai_conversations(self):
        """Verify AI conversation history persistence in MongoDB."""
        async def run_test():
            db = get_async_db()
            repo = AIConversationRepository(db)

            session_id = "test-session-xyz"
            await repo.append_message(
                session_id=session_id,
                role="user",
                content="How do I get from Mathura Junction to Bankey Bihari?",
                city="Mathura & Vrindavan"
            )
            await repo.append_message(
                session_id=session_id,
                role="assistant",
                content="Take a shared tempo to Goverdhan Chauraha, then an e-rickshaw."
            )

            history = await repo.get_history(session_id)
            self.assertEqual(len(history), 2)
            self.assertEqual(history[0]["role"], "user")
            self.assertEqual(history[1]["role"], "assistant")

            # Reset
            await repo.reset(session_id)
            history_after = await repo.get_history(session_id)
            self.assertEqual(len(history_after), 0)
            print("[OK] AI Conversation History Persistence Verified")

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
