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

if __name__ == "__main__":
    test_health()
    test_search_places()
    test_plan_journey()
    test_chat_hinglish()
    test_delays_and_simulation()
    test_saved_routes()
    print("\nALL BACKEND UNIT TESTS PASSED SUCCESSFULLY!")

