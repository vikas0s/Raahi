"""
Verification tests for Raahi FastAPI backend modules.
"""
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    print("[PASS] Health check passed")


def test_search_places():
    res = client.get("/places/search?q=rajiv")
    assert res.status_code == 200
    data = res.json()
    assert len(data["results"]) > 0
    assert "Rajiv Chowk" in data["results"][0]["name"]
    print("[PASS] Place search passed")

def test_plan_journey():
    req = {
        "origin": "Rajiv Chowk (Connaught Place)",
        "destination": "Cyber City (Gurugram)",
        "city": "Delhi NCR",
        "preferences": {
            "fastest": True,
            "cheapest": False,
            "less_crowded": False
        }
    }
    res = client.post("/plan", json=req)
    assert res.status_code == 200
    data = res.json()
    assert len(data["routes"]) >= 3
    assert data["origin"]["name"] == "Rajiv Chowk (Connaught Place)"
    assert data["destination"]["name"] == "Cyber City (Gurugram)"
    first_route = data["routes"][0]
    assert len(first_route["legs"]) > 0
    assert len(first_route["legs"][1]["path_coords"]) > 0
    print(f"[PASS] Journey planning passed: {len(data['routes'])} routes computed")

def test_chat_hinglish():
    req = {
        "message": "Rajiv Chowk se Cyber City sabse sasta route batao",
        "language": "hinglish"
    }
    res = client.post("/chat", json=req)
    assert res.status_code == 200
    data = res.json()
    assert data["reply"] is not None
    print("[PASS] Hinglish chat assistant passed")

def test_delays_and_simulation():
    res = client.post("/simulate/delay", json={"scenario": "metro_signal_delay", "delay_minutes": 12})
    assert res.status_code == 200
    
    delays_res = client.get("/delays")
    assert delays_res.status_code == 200
    delays_data = delays_res.json()
    assert delays_data["total_disruptions"] > 0
    assert delays_data["delays_summary"]["Yellow Line"] == 12
    print("[PASS] Incident simulation & live delays passed")

    # Reset
    reset_res = client.post("/simulate/delay", json={"scenario": "reset"})
    assert reset_res.status_code == 200
    print("[PASS] Simulation reset passed")

def test_saved_routes():
    res = client.get("/saved-routes")
    assert res.status_code == 200
    routes = res.json()
    assert len(routes) >= 1
    print(f"[PASS] Saved routes retrieved ({len(routes)} items)")

def test_railconnect():
    # 1. Search stations
    res = client.get("/api/rail/stations?query=Mathura")
    assert res.status_code == 200
    stations = res.json()
    assert len(stations) >= 1
    print(f"[PASS] RailConnect station search passed ({len(stations)} stations found)")

    # 2. Trains between stations
    res = client.get("/api/rail/trains?from_station=MTJ&to_station=BDB")
    assert res.status_code == 200
    trains_data = res.json()
    assert trains_data["trains_count"] >= 1
    print(f"[PASS] RailConnect trains between MTJ & BDB passed ({trains_data['trains_count']} trains)")

    # 3. Schedule
    res = client.get("/api/rail/schedule/12002")
    assert res.status_code == 200
    schedule = res.json()
    assert len(schedule["halts"]) >= 2
    print(f"[PASS] RailConnect schedule for Shatabdi passed ({len(schedule['halts'])} halts)")

    # 4. Live Running Status
    res = client.get("/api/rail/live-status/12002")
    assert res.status_code == 200
    live = res.json()
    assert live["train_number"] == "12002"
    print("[PASS] RailConnect live running status passed")

    # 5. Station Departure Board
    res = client.get("/api/rail/station-board/MTJ")
    assert res.status_code == 200
    board = res.json()
    assert len(board["departures"]) >= 1
    print(f"[PASS] RailConnect MTJ station board passed ({len(board['departures'])} departures)")

    # 6. Integrated routing in Plan Journey
    plan_res = client.post("/plan", json={
        "origin": "Mathura Junction Railway Station (MTJ)",
        "destination": "Vrindavan Railway Station / Gandhi Park",
        "city": "Mathura & Vrindavan"
    })
    assert plan_res.status_code == 200
    routes = plan_res.json()["routes"]
    has_train = any("rail_connect" in r.get("route_type", "") or "🚆" in r.get("tag", "") for r in routes)
    assert has_train, "Expected Indian Railways / Rail Bus route in journey comparison options"
    print("[PASS] RailConnect integrated journey planning comparison passed")

def test_reverse_geocode():
    # Test Mathura coordinates
    res = client.get("/places/reverse-geocode?lat=27.4924&lon=77.6737")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "Mathura" in data["city"]
    assert data["matched_transit_city"] == "Mathura & Vrindavan"
    print(f"[PASS] Reverse geocoding passed (detected: {data['city']})")

if __name__ == "__main__":
    test_health()
    test_search_places()
    test_plan_journey()
    test_chat_hinglish()
    test_delays_and_simulation()
    test_saved_routes()
    test_railconnect()
    test_reverse_geocode()
    print("\nALL BACKEND UNIT TESTS PASSED SUCCESSFULLY!")

