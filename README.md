# Raahi — Your City, Effortlessly Connected
### AI Public Transit Route Assistant • MISSION BHARAT DEV-P05

**Raahi** is a production-quality, responsive web application designed for Indian urban commuters. It unifies travel across Metro, Electric Buses, Suburban Rail, and walking legs, providing multi-criteria comparisons (Fastest, Lowest Fare, Least Crowded), delay awareness, persistent saved commutes, and an AI Travel Assistant fluent in English, Hindi, and Hinglish.

---

## Visual Identity & Design Philosophy
- **Palette**: Warm ivory (`#F7F5EF`), soft cream (`#EEECE3`), sage green (`#64836D`), forest green (`#304B3C`), muted terracotta (`#C8795A`), and soft saffron (`#E7B75B`).
- **Typography**: Plus Jakarta Sans (headings) and Manrope (interface body).
- **Aesthetic**: Minimalist, calm, editorial, responsive, and distinctly Indian without generic dashboard styling or neon gradients.

---

## Architecture & Tech Stack

### Frontend (`/frontend`)
- **Framework**: React 19 + TypeScript + Vite
- **Styling**: Tailwind CSS v4 with custom tokens and typography
- **3D City Scene**: React Three Fiber & Drei with drifting camera, moving metro, electric bus, and static fallback
- **Mapping**: MapLibre GL JS with OpenStreetMap tiles, transit polylines, and stop markers
- **Icons & Motion**: Lucide React & Framer Motion

### Backend (`/backend`)
- **Framework**: FastAPI (Python 3.14) + Uvicorn + Pydantic v2
- **Routing Engine**: Multi-criteria routing calculating Fastest, Lowest Fare, and Least Crowded routes with realistic lat/lon coordinates
- **Simulation**: Incident simulator for trackside signal delays, bus breakdowns, peak surges, and monsoon weather
- **Persistent Database**: MongoDB (using official `pymongo` with `AsyncMongoClient` connection pooling and fallback SQLite)
- **Geospatial Indexing**: MongoDB `2dsphere` index on GeoJSON coordinates for high-speed spatial proximity searches (`/api/stations/nearby`)
- **Collections Architecture**: `cities`, `stations`, `transit_agencies`, `routes`, `trips`, `stop_times`, `service_calendars`, `users`, `saved_routes`, `saved_places`, `user_preferences`, `ai_conversations`, `recent_searches`
- **Live Telemetry**: WebSockets (`/ws/telemetry`) broadcasting live disruption updates
- **Conversational AI**: Grounded Raahi AI engine handling English, Hindi, and Roman-script Hinglish

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health status and supported transit cities |
| `GET` | `/places/search?q={query}&city={city}` | Station and landmark autocomplete search |
| `POST` | `/plan` | Computes Fastest, Lowest Fare, and Least Crowded itineraries |
| `GET` | `/itinerary/{id}` | Fetches stored journey itinerary |
| `GET` | `/delays` | Active transit service advisories and crowd levels |
| `POST` | `/simulate/delay` | Demo disruption trigger (signal delay, bus diversion, surge, reset) |
| `POST` | `/chat` | Raahi AI conversational endpoint (English, Hindi, Hinglish) |
| `GET` | `/saved-routes` | Lists persisted saved commutes |
| `POST` | `/saved-routes` | Creates a new saved commute |
| `DELETE` | `/saved-routes/{id}` | Deletes a saved commute |
| `GET` | `/stops/{id}/departures` | Live departure board for a transit stop |
| `WS` | `/ws/telemetry` | WebSocket for real-time disruption broadcasting |

---

## Running the Application Locally

### 1. Start the Backend API Server
```powershell
# From workspace root
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Start the Frontend Development Server
```powershell
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Open `http://127.0.0.1:5173/` in your browser.

---

## Testing & Verification
Run the backend automated test suite:
```powershell
python -m backend.test_backend
```

Run the frontend TypeScript & production build check:
```powershell
cd frontend
npm run build
```


---

## Database Architecture & MongoDB Integration

Raahi connects to MongoDB via the official `pymongo` driver with asynchronous connection pooling via `AsyncMongoClient` in FastAPI request handlers.

### Key MongoDB Collections & Indexes
1. `cities`: Unique index on `name`, index on `is_active`.
2. `stations`: `2dsphere` index on `location`, compound index on `city_id` + `name`, sparse unique on `external_stop_id`.
3. `transit_agencies`: Index on `city_id`.
4. `routes`: Index on `city_id` and `agency_id`.
5. `trips`: Index on `route_id` and `service_id`.
6. `stop_times`: Compound index on `trip_id` + `stop_sequence`, index on `stop_id`.
7. `saved_routes`: Index on `user_id` + `city`, index on `created_at`.
8. `saved_places`: Index on `user_id`.
9. `user_preferences`: Unique index on `user_id`.
10. `ai_conversations`: Unique index on `session_id`, index on `user_id`.

### MongoDB Commands
- **Idempotent Data Seeder**:
  ```powershell
  python -m backend.mongodb.seeder
  ```
- **Run MongoDB Integration Test Suite**:
  ```powershell
  python -m backend.test_mongodb_integration
  ```
