"""
Comprehensive Integration & Verification Test Suite for Raahi Suburban Railway Networks.
Tests local trains, station resolution, multimodal routing, city isolation, and AI assistant.
"""
import sys
import unittest
import asyncio
from datetime import datetime

# Enforce UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

from backend.rail.service import rail_service_instance
from backend.rail.providers.fallback_data import RAIL_STATIONS, get_fallback_trains_between
from backend.router import router_instance
from backend.models import PlanRequest, ChatRequest
from backend.chat_engine import chat_assistant_instance


class TestSuburbanRailwayIntegration(unittest.TestCase):

    def test_01_station_directory_coverage(self):
        """Verify all supported cities have authentic suburban stations registered."""
        stations = RAIL_STATIONS
        self.assertGreater(len(stations), 50, "Should have 50+ authentic railway stations")

        mumbai_stations = [s for s in stations.values() if s.city == "Mumbai"]
        blr_stations = [s for s in stations.values() if s.city == "Bengaluru"]
        delhi_stations = [s for s in stations.values() if s.city == "Delhi NCR"]
        mathura_stations = [s for s in stations.values() if s.city == "Mathura & Vrindavan"]

        print(f"\n[Test 1] Station Coverage:")
        print(f"  - Mumbai Suburban Stations: {len(mumbai_stations)}")
        print(f"  - Bengaluru SWR Stations: {len(blr_stations)}")
        print(f"  - Delhi NCR / Ring Rail Stations: {len(delhi_stations)}")
        print(f"  - Mathura & Vrindavan Stations: {len(mathura_stations)}")

        self.assertGreaterEqual(len(mumbai_stations), 20, "Mumbai should have Western, Central, Harbour stations")
        self.assertGreaterEqual(len(blr_stations), 8, "Bengaluru should have SWR commuter stations")
        self.assertGreaterEqual(len(delhi_stations), 10, "Delhi should have EMU and Ring Railway stations")
        self.assertGreaterEqual(len(mathura_stations), 6, "Mathura should have Rail Bus & commuter halts")

    def test_02_city_aware_station_disambiguation(self):
        """Verify station lookups respect city scoping and prevent cross-city confusion."""
        # Search 'Central' in Mumbai vs Bengaluru
        mum_st = rail_service_instance.find_nearest_rail_station(18.97, 72.82, city="Mumbai")
        self.assertIsNotNone(mum_st)
        self.assertEqual(mum_st[0].city, "Mumbai")

        blr_st = rail_service_instance.find_nearest_rail_station(12.97, 77.57, city="Bengaluru")
        self.assertIsNotNone(blr_st)
        self.assertEqual(blr_st[0].city, "Bengaluru")

        delhi_st = rail_service_instance.find_nearest_rail_station(28.64, 77.21, city="Delhi NCR")
        self.assertIsNotNone(delhi_st)
        self.assertEqual(delhi_st[0].city, "Delhi NCR")

        # Looking for a Mumbai station within Delhi NCR must return None
        dadar_in_delhi = rail_service_instance.resolve_station_from_place({"name": "Dadar Junction"}, city="Delhi NCR")
        self.assertIsNone(dadar_in_delhi, "Dadar must never resolve within Delhi NCR")
        print("\n[Test 2] City-aware disambiguation verified: Dadar not matched in Delhi NCR.")

    def test_03_mumbai_suburban_local_routes(self):
        """Test Mumbai Western Line and Central Line local train itineraries."""
        req = PlanRequest(
            origin="Churchgate Railway Station",
            destination="Borivali Railway Station",
            city="Mumbai"
        )
        resp = router_instance.plan_journey(req)
        rail_routes = [r for r in resp.routes if r.route_type == "rail_connect"]
        self.assertGreater(len(rail_routes), 0, "Mumbai Churchgate to Borivali must return rail_connect routes")
        top = rail_routes[0]
        self.assertIn("Western Line", top.tag)
        self.assertGreater(top.total_fare_inr, 0)
        self.assertLessEqual(top.total_fare_inr, 25.0, "Mumbai local 2nd class fare should be ₹10-₹20")
        print(f"\n[Test 3] Mumbai Local: {top.title} | {top.tag} | ₹{top.total_fare_inr} | {top.total_duration_minutes}m")

    def test_04_bengaluru_swr_commuter_routes(self):
        """Test Bengaluru SWR Commuter rail itinerary from KSR Bengaluru to Whitefield."""
        req = PlanRequest(
            origin="Majestic (KSR Bengaluru)",
            destination="Whitefield (Kadugodi)",
            city="Bengaluru"
        )
        resp = router_instance.plan_journey(req)
        rail_routes = [r for r in resp.routes if r.route_type == "rail_connect"]
        self.assertGreater(len(rail_routes), 0, "Bengaluru Majestic to Whitefield must return SWR commuter rail")
        top = rail_routes[0]
        self.assertIn("SWR Commuter", top.tag)
        self.assertLessEqual(top.total_fare_inr, 30.0, "SWR MEMU fare should be unreserved slab ₹15-₹25")
        print(f"\n[Test 4] Bengaluru Commuter: {top.title} | {top.tag} | ₹{top.total_fare_inr} | {top.total_duration_minutes}m")

    def test_05_delhi_suburban_emu_and_ring_railway(self):
        """Test Delhi NCR EMU commuter itinerary between Nizamuddin and New Delhi."""
        req = PlanRequest(
            origin="Hazrat Nizamuddin (NZM)",
            destination="New Delhi Railway Station (NDLS)",
            city="Delhi NCR"
        )
        resp = router_instance.plan_journey(req)
        rail_routes = [r for r in resp.routes if r.route_type == "rail_connect"]
        self.assertGreater(len(rail_routes), 0, "Delhi NZM to NDLS must return suburban EMU")
        top = rail_routes[0]
        self.assertIn("Delhi Suburban", top.tag)
        self.assertEqual(top.total_fare_inr, 10.0, "Northern Railway suburban unreserved fare is ₹10")
        print(f"\n[Test 5] Delhi EMU: {top.title} | {top.tag} | ₹{top.total_fare_inr} | {top.total_duration_minutes}m")

    def test_06_mathura_vrindavan_rail_bus(self):
        """Test Mathura Junction to Vrindavan heritage rail bus (#04419)."""
        req = PlanRequest(
            origin="Mathura Junction Railway Station",
            destination="Vrindavan Railway Station",
            city="Mathura & Vrindavan"
        )
        resp = router_instance.plan_journey(req)
        rail_routes = [r for r in resp.routes if r.route_type == "rail_connect"]
        self.assertGreater(len(rail_routes), 0, "Mathura to Vrindavan must return Rail Bus")
        top = rail_routes[0]
        self.assertIn("Rail Bus", top.tag)
        self.assertTrue("04419" in top.tag or "04419" in top.title or any(l.train_number == "04419" for l in top.legs if l.mode == "rail"))
        print(f"\n[Test 6] Mathura Rail Bus: {top.title} | {top.tag} | ₹{top.total_fare_inr} | {top.total_duration_minutes}m")

    def test_07_multimodal_suburban_transfer(self):
        """Test 1-interchange multi-line transfer in Mumbai (Western Line to Central Line via Dadar)."""
        mel = rail_service_instance.get_station_by_code("MEL")
        tna = rail_service_instance.get_station_by_code("TNA")
        route = rail_service_instance._build_suburban_transfer_route(
            {"name": mel.name, "lat": mel.lat, "lon": mel.lon},
            {"name": tna.name, "lat": tna.lat, "lon": tna.lon},
            mel,
            tna,
            datetime.now(),
            28.0,
            "Mumbai"
        )
        self.assertIsNotNone(route, "Should compute transfer route via Dadar")
        self.assertIn("Interchange", route.tag)
        self.assertEqual(len([l for l in route.legs if l.mode == 'rail']), 2, "Should have 2 rail legs")
        self.assertTrue(any("FOB" in l.instructions or "transfer" in l.line_name.lower() for l in route.legs if l.mode == 'walk'))
        print(f"\n[Test 7] Suburban Interchange: {route.title} | Legs: {[l.mode + ' (' + l.line_name + ')' for l in route.legs]}")

    def test_08_cross_city_leakage_prevention(self):
        """Verify cross-city local transit requests fail gracefully without cross-contaminating cities."""
        req = PlanRequest(
            origin="Connaught Place",
            destination="Dadar",
            city="Delhi NCR"
        )
        resp = router_instance.plan_journey(req)
        # Should NOT contain mumbai_local or Western Line
        for r in resp.routes:
            self.assertNotEqual(r.route_type, "mumbai_local", "Delhi journey must not include mumbai_local")
            self.assertNotIn("Western Line", r.title, "Delhi journey must not include Western Line")
        print("\n[Test 8] Cross-city prevention verified: No Mumbai local trains in Delhi searches.")

    def test_09_ai_assistant_suburban_rail_query(self):
        """Test AI Travel Assistant handling suburban railway inquiries in Hindi and English."""
        async def run_chat():
            # Hindi inquiry
            req_hi = ChatRequest(
                message="Delhi mein railway station se dusre area tak local train aur metro se kaise jaun?",
                session_id="test_suburban_hi",
                city="Delhi NCR",
                language="hi"
            )
            resp_hi = await chat_assistant_instance.process_message(req_hi)
            self.assertIsNotNone(resp_hi.reply)
            self.assertGreater(len(resp_hi.reply), 50)
            print(f"\n[Test 9A] AI Assistant (Hindi): {resp_hi.reply[:180]}...")

            # English inquiry for Mumbai local
            req_en = ChatRequest(
                message="How can I take Mumbai local train from Churchgate to Borivali?",
                session_id="test_suburban_en",
                city="Mumbai",
                language="en"
            )
            resp_en = await chat_assistant_instance.process_message(req_en)
            self.assertIsNotNone(resp_en.reply)
            self.assertGreater(len(resp_en.reply), 50)
            print(f"\n[Test 9B] AI Assistant (English): {resp_en.reply[:180]}...")

        asyncio.run(run_chat())


if __name__ == '__main__':
    unittest.main()
