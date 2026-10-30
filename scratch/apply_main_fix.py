with open("backend/main.py", "r", encoding="utf-8") as f:
    text = f.read()

# Add from pydantic import BaseModel if not present
if "from pydantic import BaseModel" not in text:
    text = "from pydantic import BaseModel\n" + text

target = '@app.websocket("/ws/telemetry")'
insertion = """class GoogleMapsKeyPayload(BaseModel):
    api_key: str

@app.get("/api/settings/google-maps-status")
def get_google_maps_status():
    \"\"\"Check if Google Maps API key is configured.\"\"\"
    from .google_maps_service import google_maps_service_instance
    return {
        "configured": google_maps_service_instance.is_configured(),
        "masked_key": google_maps_service_instance.get_api_key_masked()
    }

@app.post("/api/settings/google-maps-key")
def update_google_maps_key(payload: GoogleMapsKeyPayload):
    \"\"\"Dynamically save and activate Google Maps API key.\"\"\"
    from .google_maps_service import google_maps_service_instance
    success = google_maps_service_instance.set_api_key(payload.api_key)
    return {
        "success": success,
        "configured": google_maps_service_instance.is_configured(),
        "masked_key": google_maps_service_instance.get_api_key_masked()
    }

"""

if target in text and "@app.get(\"/api/settings/google-maps-status\")" not in text:
    text = text.replace(target, insertion + target, 1)

compile(text, "backend/main.py", "exec")
with open("backend/main.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated backend/main.py successfully!")

