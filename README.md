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
- **Persistence**: SQLite (`raahi_transit.db`) for saved commutes
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
