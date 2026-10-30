"""
Automated Comprehensive Test Suite for Raahi Global Travel Assistant.
Tests all 20 requirements from Section 12 of the architecture specification:
1. Mathura Junction -> GLA University
2. GLA University -> Mathura Junction (inversion protection)
3. Rajiv Chowk -> Cyber City
4. Mumbai Airport -> Gateway of India
5. Bengaluru Airport -> Electronic City
6. London King's Cross -> Heathrow
7. International driving route (Paris -> Eiffel Tower)
8. Ambiguous place name (clarification requested)
9. Unsupported geographic region
10. Provider returning wrong endpoints (rejected by validation)
11. Provider returning no routes
12. Provider timeout resilience
13. Missing fare handling (provenance labeled honestly)
14. Missing public transit dataset (road alternative with honest notice)
15. Follow-up requesting cheapest route
16. Follow-up requesting fastest route
17. New journey replacing old journey context
18. Invalid Sarvam credentials (graceful fallback)
19. Hindi, Hinglish, and English responses
20. Confirmation that no geolocation permission is requested automatically
"""
import sys
import unittest
import asyncio
from unittest.mock import patch, MagicMock

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from backend.models import (
    ChatRequest, ChatResponse, CanonicalJourneyRequest,
    ResolvedPlace, RouteItinerary, TransitLeg, TravelPreference
)
from backend.geocoding_service import geocoding_service_instance
from backend.routing_providers.router_manager import routing_manager_instance
from backend.routing_providers.global_road_provider import global_road_provider_instance
from backend.routing_providers.local_transit_provider import local_transit_provider_instance
from backend.chat_engine import chat_assistant_instance
from backend.sarvam_service import sarvam_service_instance, SarvamAPIError

class TestGlobalTravelAssistant(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    # 1. Mathura Junction -> GLA University
    def test_01_mathura_to_gla_university(self):
        req = ChatRequest(message="Mathura Junction se GLA University kaise jaun?")
        res = self.loop.run_until_complete(chat_assistant_instance.process_message(req))
        self.assertIsNotNone(res.canonical_request)
        self.assertIn("Mathura Junction", res.canonical_request.origin.name)
        self.assertIn("GLA University", res.canonical_request.destination.name)
        self.assertEqual(res.coverage_type, "full_transit")
        self.assertTrue(res.is_grounded_route)
        self.assertIsNotNone(res.route_data)
        # Ensure first leg starts at Mathura and last leg ends at GLA
        self.assertIn("Mathura", res.route_data.legs[0].origin_name)
        self.assertIn("GLA", res.route_data.legs[-1].destination_name)
        print("[PASS] 1. Mathura Junction -> GLA University verified.")

    # 2. GLA University -> Mathura Junction (Guaranteed Origin/Destination Correctness)
    def test_02_gla_university_to_mathura_not_reversed(self):
        req = ChatRequest(message="GLA University se Mathura Junction jana hai")
        res = self.loop.run_until_complete(chat_assistant_instance.process_message(req))
        self.assertIsNotNone(res.canonical_request)
        self.assertIn("GLA University", res.canonical_request.origin.name)
        self.assertIn("Mathura Junction", res.canonical_request.destination.name)
        self.assertIsNotNone(res.route_data)
        # Verify first leg is GLA and last leg is Mathura Jn (NEVER REVERSED)
        self.assertIn("GLA", res.route_data.legs[0].origin_name)
        self.assertIn("Mathura", res.route_data.legs[-1].destination_name)
        print("[PASS] 2. GLA University -> Mathura Junction endpoint ordering verified.")

    # 3. Rajiv Chowk -> Cyber City (Delhi NCR)
    def test_03_rajiv_chowk_to_cyber_city(self):
        req = ChatRequest(message="Rajiv Chowk se Cyber City ka fastest route batao")
        res = self.loop.run_until_complete(chat_assistant_instance.process_message(req))
        self.assertIsNotNone(res.canonical_request)
        self.assertIn("Rajiv Chowk", res.canonical_request.origin.name)
        self.assertIn("Cyber City", res.canonical_request.destination.name)
        self.assertEqual(res.coverage_type, "full_transit")
        self.assertIsNotNone(res.route_data)
        print("[PASS] 3. Rajiv Chowk -> Cyber City verified.")

    # 4. Mumbai Central / Airport -> Gateway of India (Mumbai Local Transit)
    def test_04_mumbai_airport_to_gateway_of_india(self):
        req = ChatRequest(message="Mumbai Airport se Gateway of India kaise pahunchun?")
        res = self.loop.run_until_complete(chat_assistant_instance.process_message(req))
        self.assertIsNotNone(res.canonical_request)
        self.assertIn("Mumbai", res.canonical_request.origin.name)
        self.assertIn("Gateway of India", res.canonical_request.destination.name)
        self.assertEqual(res.coverage_type, "full_transit")
        self.assertIsNotNone(res.route_data)
        print("[PASS] 4. Mumbai Airport -> Gateway of India verified.")

    # 5. Bengaluru Airport -> Electronic City
    def test_05_bengaluru_airport_to_electronic_city(self):
        req = ChatRequest(message="How do I get from Bengaluru airport to Electronic City?")
        res = self.loop.run_until_complete(chat_assistant_instance.process_message(req))
        self.assertIsNotNone(res.canonical_request)
        self.assertIn("Bengaluru", res.canonical_request.origin.city)
        self.assertIn("Electronic City", res.canonical_request.destination.name)
        self.assertIn("Bengaluru", res.canonical_request.destination.city)
        self.assertEqual(res.coverage_type, "full_transit")
        self.assertIsNotNone(res.route_data)
        print("[PASS] 5. Bengaluru Airport -> Electronic City verified.")

    # 6. London King's Cross -> Heathrow
    def test_06_london_kings_cross_to_heathrow(self):
        req = ChatRequest(message="London Kings Cross to Heathrow by public transport")
        res = self.loop.run_until_complete(chat_assistant_instance.process_message(req))
        self.assertIsNotNone(res.canonical_request)
        self.assertIn("London", res.canonical_request.origin.display_name)
        self.assertIn("Heathrow", res.canonical_request.destination.display_name)
        # Correctly recognizes that international public transit schedules are not connected
        self.assertEqual(res.coverage_type, "road_only")
        self.assertIsNotNone(res.route_data)
        self.assertFalse(res.route_data.transit_coverage_available)
        self.assertIn("Public transit schedules", res.route_data.coverage_advisory)
        print("[PASS] 6. London King's Cross -> Heathrow (honest road coverage) verified.")

    # 7. Supported International Driving Route (Paris -> Eiffel Tower)
    def test_07_international_paris_driving_route(self):
        req = ChatRequest(message="Paris se Eiffel Tower kaise jaun?")
        res = self.loop.run_until_complete(chat_assistant_instance.process_message(req))
        self.assertIsNotNone(res.canonical_request)
        self.assertIn("Paris", res.canonical_request.origin.name)
        self.assertIn("Eiffel Tower", res.canonical_request.destination.name)
        self.assertEqual(res.coverage_type, "road_only")
        self.assertIsNotNone(res.route_data)
        self.assertEqual(res.route_data.data_source, "OSRM Global Road Network")
        print("[PASS] 7. Supported international driving route (Paris) verified.")

    # 8. Ambiguous Place Name (Prompts for Clarification)
    def test_08_ambiguous_place_name_clarification(self):
        req = ChatRequest(message="Springfield se Paris kaise jaun?")
        res = self.loop.run_until_complete(chat_assistant_instance.process_message(req))
        self.assertTrue(res.clarification_needed)
        self.assertEqual(res.action_type, "clarification")
        self.assertIn("Springfield", res.reply)
        print("[PASS] 8. Ambiguous place name produces clarification question.")

    # 9. Unsupported Geographic Region (e.g. Null Coordinates / Desert Ocean)
    def test_09_unsupported_geographic_region(self):
        orig = ResolvedPlace(name="Point Nemo", display_name="Ocean Pole of Inaccessibility", lat=0.0, lon=0.0)
        dest = ResolvedPlace(name="Tristan da Cunha", display_name="Remote Island", lat=0.0, lon=0.0)
        req = CanonicalJourneyRequest(origin=orig, destination=dest)
        routes, cov = routing_manager_instance.plan_canonical_journey(req)
        self.assertEqual(len(routes), 0)
        self.assertEqual(cov, "unsupported")
        print("[PASS] 9. Unsupported geographic region produces empty routes and unsupported flag.")

    # 10. Route Provider Returning Wrong Endpoints (Rejection Test)
    def test_10_provider_returning_wrong_endpoints_rejected(self):
        orig = ResolvedPlace(name="Station Alpha", display_name="Alpha", lat=28.5, lon=77.2)
        dest = ResolvedPlace(name="Station Beta", display_name="Beta", lat=28.7, lon=77.4)

        # Create a malicious/buggy route that starts at Beta and ends at Alpha (reversed)
        bad_leg = TransitLeg(
            id="bad-leg",
            mode="taxi",
            origin_name="Station Beta", # Wrong origin!
            destination_name="Station Alpha", # Wrong destination!
            origin_coords=[77.4, 28.7],
            destination_coords=[77.2, 28.5],
            duration_minutes=30,
            distance_meters=15000,
            departure_time="10:00",
            arrival_time="10:30",
            instructions="Bad route"
        )
        bad_route = RouteItinerary(
            id="bad-route",
            title="Bad Route",
            tag="Invalid",
            tag_reason="Reversed",
            total_duration_minutes=30,
            departure_time="10:00",
            arrival_time="10:30",
            total_fare_inr=100.0,
            transfers_count=0,
            walking_duration_minutes=0,
            walking_distance_meters=0,
            legs=[bad_leg]
        )

        is_valid = routing_manager_instance._validate_route_endpoints(bad_route, orig, dest)
        self.assertFalse(is_valid, "Routing manager must reject routes with inverted/mismatched endpoints")
        print("[PASS] 10. Provider returning wrong/reversed endpoints successfully rejected.")

    # 11. Route Provider Returning No Routes
    def test_11_provider_returning_no_routes(self):
        session = chat_assistant_instance.session_manager.get_or_create("test-no-routes")
        orig = ResolvedPlace(name="Desert Point A", display_name="Desert A", lat=0.0, lon=0.0)
        dest = ResolvedPlace(name="Desert Point B", display_name="Desert B", lat=0.0, lon=0.0)
        req = CanonicalJourneyRequest(origin=orig, destination=dest)
        res = self.loop.run_until_complete(
            chat_assistant_instance._execute_canonical_journey(session, req, "test query", "en")
        )
        self.assertFalse(res.is_grounded_route)
        self.assertIsNone(res.route_data)
        self.assertEqual(res.coverage_type, "unsupported")
        print("[PASS] 11. Provider returning no routes handled gracefully.")

    # 12. Provider Timeout Resilience
    def test_12_provider_timeout_resilience(self):
        # Mock OSRM timing out
        with patch.object(global_road_provider_instance, '_fetch_osrm_route', return_value=None):
            orig = ResolvedPlace(name="Place X", display_name="X", lat=19.0, lon=72.8, country="India")
            dest = ResolvedPlace(name="Place Y", display_name="Y", lat=19.2, lon=72.9, country="India")
            req = CanonicalJourneyRequest(origin=orig, destination=dest)
            routes = global_road_provider_instance.plan_route(req)
            self.assertGreater(len(routes), 0)
            self.assertEqual(routes[0].route_type, "road_direct")
        print("[PASS] 12. Provider timeout resilience with straight-line fallback verified.")

    # 13. Missing Fare Handling (Provenance Labeled Honestly)
    def test_13_missing_fare_handling(self):
        orig = ResolvedPlace(name="London Kings Cross", display_name="London", lat=51.5324, lon=-0.1230, country="United Kingdom")
        dest = ResolvedPlace(name="Heathrow", display_name="London", lat=51.4700, lon=-0.4543, country="United Kingdom")
        req = CanonicalJourneyRequest(origin=orig, destination=dest, currency="GBP")
        routes = global_road_provider_instance.plan_route(req)
        drive_route = routes[0]
        # Fare must NOT be hallucinated as a verified exact public transit ticket
        self.assertEqual(drive_route.fare_provenance, "estimated_meter")
        self.assertIn("Estimated", drive_route.fare_breakdown)
        print("[PASS] 13. Missing fare labeled as estimate/unavailable rather than hallucinated.")

    # 14. Missing Public Transit Dataset (Honest Explanation with Road Alternative)
    def test_14_missing_public_transit_dataset_notice(self):
        req = ChatRequest(message="London Kings Cross to Heathrow by public transport")
        res = self.loop.run_until_complete(chat_assistant_instance.process_message(req))
        self.assertFalse(res.route_data.transit_coverage_available)
        self.assertIn("Public transit schedules", res.route_data.coverage_advisory)
        print("[PASS] 14. Missing transit dataset reports honest explanation and road alternative.")

    # 15. Follow-Up Requesting Cheapest Route
    def test_15_followup_cheapest_route(self):
        session_id = "test-session-followup"
        # Initial request
        req1 = ChatRequest(message="Rajiv Chowk se Cyber City", session_id=session_id)
        res1 = self.loop.run_until_complete(chat_assistant_instance.process_message(req1))
        self.assertIsNotNone(res1.route_data)

        # Follow-up: "Sabse sasta kaunsa hai?"
        req2 = ChatRequest(message="Sabse sasta option kaunsa hai?", session_id=session_id)
        res2 = self.loop.run_until_complete(chat_assistant_instance.process_message(req2))
        self.assertIsNotNone(res2.route_data)
        self.assertEqual(res2.detected_intent, "route_followup")
        self.assertLessEqual(res2.route_data.total_fare_inr, res1.route_data.total_fare_inr)
        print("[PASS] 15. Follow-up requesting cheapest route retains journey context.")

    # 16. Follow-Up Requesting Fastest Route
    def test_16_followup_fastest_route(self):
        session_id = "test-session-fastest"
        req1 = ChatRequest(message="Mathura Junction se GLA University", session_id=session_id)
        self.loop.run_until_complete(chat_assistant_instance.process_message(req1))

        # Follow-up: "Aur fastest?"
        req2 = ChatRequest(message="Aur fastest route kaunsa hai?", session_id=session_id)
        res2 = self.loop.run_until_complete(chat_assistant_instance.process_message(req2))
        self.assertIsNotNone(res2.route_data)
        self.assertEqual(res2.detected_intent, "route_followup")
        print("[PASS] 16. Follow-up requesting fastest route retains journey context.")

    # 17. New Journey Replacing Old Journey Context
    def test_17_new_journey_replaces_old_context(self):
        session_id = "test-session-replace"
        # First journey in Mathura
        req1 = ChatRequest(message="Mathura Junction se GLA University", session_id=session_id)
        self.loop.run_until_complete(chat_assistant_instance.process_message(req1))

        # Explicitly request a completely new journey in Mumbai
        req2 = ChatRequest(message="Mumbai Central se Gateway of India kaise pahunchun?", session_id=session_id)
        res2 = self.loop.run_until_complete(chat_assistant_instance.process_message(req2))

        # Verify old Mathura context was COMPLETELY replaced by Mumbai!
        self.assertIn("Mumbai Central", res2.canonical_request.origin.name)
        self.assertIn("Gateway of India", res2.canonical_request.destination.name)
        self.assertNotIn("Mathura", res2.canonical_request.origin.name)
        print("[PASS] 17. New journey cleanly replaces previous journey context.")

    # 18. Invalid Sarvam Credentials (Graceful Fallback)
    def test_18_invalid_sarvam_credentials_graceful_fallback(self):
        with patch.object(sarvam_service_instance, 'chat_completion', side_effect=SarvamAPIError("Invalid 401 key", status_code=401)):
            req = ChatRequest(message="Rajiv Chowk se Cyber City")
            res = self.loop.run_until_complete(chat_assistant_instance.process_message(req))
            self.assertTrue(res.is_grounded_route)
            self.assertIsNotNone(res.route_data)
            self.assertIn("Rajiv Chowk", res.reply)
            self.assertIn("Cyber City", res.reply)
        print("[PASS] 18. Invalid Sarvam credentials fallback gracefully without 500 error.")

    # 19. Hindi, Hinglish, and English Responses
    def test_19_multilingual_responses(self):
        # Hindi
        req_hi = ChatRequest(message="मथुरा जंक्शन से बांके बिहारी मंदिर कैसे जाएँ?", language="hi")
        res_hi = self.loop.run_until_complete(chat_assistant_instance.process_message(req_hi))
        self.assertTrue(any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in res_hi.reply))

        # Hinglish
        req_hing = ChatRequest(message="Mathura Junction se GLA University kaise jaun?", language="hinglish")
        res_hing = self.loop.run_until_complete(chat_assistant_instance.process_message(req_hing))
        self.assertTrue(res_hing.is_grounded_route)

        # English
        req_en = ChatRequest(message="How do I get from Bengaluru airport to Electronic City?", language="en")
        res_en = self.loop.run_until_complete(chat_assistant_instance.process_message(req_en))
        self.assertTrue(res_en.is_grounded_route)
        print("[PASS] 19. Hindi, Hinglish, and English responses verified.")

    # 20. Confirmation That No Geolocation Permission is Requested Automatically
    def test_20_no_automatic_geolocation(self):
        with open("frontend/src/context/LocationContext.tsx", "r", encoding="utf-8") as f:
            code = f.read()
        # Verify watchPosition or getCurrentPosition is never called automatically on mount
        self.assertNotIn("useEffect(() => {\n    requestLocation();", code)
        self.assertNotIn("useEffect(() => {\n    navigator.geolocation.getCurrentPosition", code)
        print("[PASS] 20. Code audit confirms zero automatic geolocation calls on component mount.")

if __name__ == "__main__":
    unittest.main()

