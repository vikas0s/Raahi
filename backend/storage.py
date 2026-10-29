"""
Persistent SQLite storage for Saved Routes and User Commutes.
"""
import sqlite3
import os
import uuid
from typing import List, Optional
from datetime import datetime
from .models import SavedRoute, SavedRouteCreate

DB_PATH = os.path.join(os.path.dirname(__file__), "raahi_transit.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_routes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            city TEXT NOT NULL,
            preferred_mode TEXT NOT NULL,
            created_at TEXT NOT NULL,
            typical_duration_minutes INTEGER NOT NULL,
            typical_fare_inr REAL NOT NULL,
            typical_transfers INTEGER NOT NULL,
            current_delay_minutes INTEGER DEFAULT 0,
            active_status TEXT DEFAULT 'Normal Service'
        )
    """)
    conn.commit()
    
    # Pre-populate sample commutes if table is empty
    cursor.execute("SELECT COUNT(*) FROM saved_routes")
    count = cursor.fetchone()[0]
    if count == 0:
        now_str = datetime.now().isoformat()
        sample_commutes = [
            (
                "commute-1",
                "Home to Cyber City (Daily Office)",
                "Rajiv Chowk (Connaught Place)",
                "Cyber City (Gurugram)",
                "Delhi NCR",
                "fastest",
                now_str,
                42,
                50.0,
                1,
                0,
                "Normal Service"
            ),
            (
                "commute-2",
                "Hostel to NDLS (Weekend Travel)",
                "Vishwavidyalaya (Delhi University)",
                "New Delhi Railway Station (NDLS)",
                "Delhi NCR",
                "fastest",
                now_str,
                22,
                30.0,
                0,
                0,
                "Normal Service"
            ),
            (
                "commute-3",
                "Noida Tech Hub to Saket Mall",
                "Noida Sector 62",
                "Saket (Select Citywalk)",
                "Delhi NCR",
                "cheapest",
                now_str,
                58,
                45.0,
                1,
                4,
                "Minor Congestion"
            )
        ]
        cursor.executemany("""
            INSERT INTO saved_routes (
                id, name, origin, destination, city, preferred_mode,
                created_at, typical_duration_minutes, typical_fare_inr,
                typical_transfers, current_delay_minutes, active_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_commutes)
        conn.commit()
    conn.close()

def get_all_saved_routes(city: Optional[str] = None) -> List[SavedRoute]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if city:
        cursor.execute("SELECT * FROM saved_routes WHERE city = ? ORDER BY created_at DESC", (city,))
    else:
        cursor.execute("SELECT * FROM saved_routes ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    routes = []
    for r in rows:
        routes.append(SavedRoute(
            id=r["id"],
            name=r["name"],
            origin=r["origin"],
            destination=r["destination"],
            city=r["city"],
            preferred_mode=r["preferred_mode"],
            created_at=r["created_at"],
            typical_duration_minutes=r["typical_duration_minutes"],
            typical_fare_inr=r["typical_fare_inr"],
            typical_transfers=r["typical_transfers"],
            current_delay_minutes=r["current_delay_minutes"],
            active_status=r["active_status"]
        ))

    # If city is Mathura and no saved routes exist in DB yet, return default authentic Braj commutes
    if (not routes) and city and ("mathura" in city.lower() or "vrindavan" in city.lower()):
        now_str = datetime.now().isoformat()
        routes = [
            SavedRoute(
                id="mathura-saved-1",
                name="Mathura Jn to Bankey Bihari Ji (Darshan)",
                origin="Mathura Junction Railway Station (MTJ)",
                destination="Shri Bankey Bihari Ji Mandir (Vrindavan)",
                city=city,
                preferred_mode="fastest",
                created_at=now_str,
                typical_duration_minutes=32,
                typical_fare_inr=45.0,
                typical_transfers=1,
                current_delay_minutes=0,
                active_status="Normal Service (E-Rickshaw Running)"
            ),
            SavedRoute(
                id="mathura-saved-2",
                name="Janmabhoomi to Prem Mandir (Evening Light Show)",
                origin="Shri Krishna Janmabhoomi (Janmasthan)",
                destination="Prem Mandir (Vrindavan)",
                city=city,
                preferred_mode="fastest",
                created_at=now_str,
                typical_duration_minutes=24,
                typical_fare_inr=35.0,
                typical_transfers=1,
                current_delay_minutes=0,
                active_status="Normal Service"
            ),
            SavedRoute(
                id="mathura-saved-3",
                name="Mathura Jn to Govardhan (Daan Ghati Parikrama)",
                origin="Mathura Junction Railway Station (MTJ)",
                destination="Govardhan - Daan Ghati Mandir & Mansi Ganga",
                city=city,
                preferred_mode="cheapest",
                created_at=now_str,
                typical_duration_minutes=42,
                typical_fare_inr=45.0,
                typical_transfers=0,
                current_delay_minutes=0,
                active_status="Normal Service (Tempo Available)"
            )
        ]
        
    return routes

def create_saved_route(item: SavedRouteCreate, duration: int = 35, fare: float = 40.0, transfers: int = 1) -> SavedRoute:
    new_id = f"route-{uuid.uuid4().hex[:8]}"
    created_at = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO saved_routes (
            id, name, origin, destination, city, preferred_mode,
            created_at, typical_duration_minutes, typical_fare_inr,
            typical_transfers, current_delay_minutes, active_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 'Normal Service')
    """, (
        new_id, item.name, item.origin, item.destination, item.city, item.preferred_mode,
        created_at, duration, fare, transfers
    ))
    conn.commit()
    conn.close()
    return SavedRoute(
        id=new_id,
        name=item.name,
        origin=item.origin,
        destination=item.destination,
        city=item.city,
        preferred_mode=item.preferred_mode,
        created_at=created_at,
        typical_duration_minutes=duration,
        typical_fare_inr=fare,
        typical_transfers=transfers,
        current_delay_minutes=0,
        active_status="Normal Service"
    )

def delete_saved_route(route_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM saved_routes WHERE id = ?", (route_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

# Initialize DB at import time
init_db()
