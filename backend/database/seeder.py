"""
Idempotent Database Seeder for Raahi Transit Platform.
Imports official transit records:
- 4 Metropolitan Cities (Delhi NCR, Mumbai, Bengaluru, Mathura & Vrindavan)
- 12 Transit Agencies (DMRC, BEST, Western Railway, Central Railway, BMRCL, BMTC, etc.)
- 180+ Authentic Transit Stations & Railway Hubs (from PLACES_DATABASE and RAIL_STATIONS)
- Commuter Routes, Trips, and Halts (from SCHEDULE_DATABASE)
- Default User Commutes & Preferences
"""
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any

from sqlalchemy.orm import Session
from .connection import SessionLocal, init_db
from .models import (
    User, City, TransitAgency, Station, Route, Trip, StopTime,
    CalendarService, SavedJourney, SavedPlace, UserPreference
)
from ..transit_data import PLACES_DATABASE
from ..rail.providers.fallback_data import RAIL_STATIONS, SCHEDULE_DATABASE

logger = logging.getLogger("raahi.seeder")


def seed_database(db: Session) -> Dict[str, int]:
    """Populates the database with real transit network entities idempotently."""
    stats = {
        "cities": 0,
        "agencies": 0,
        "stations": 0,
        "routes": 0,
        "trips": 0,
        "stop_times": 0,
        "saved_journeys": 0,
        "users": 0
    }

    # 1. Default User
    default_user = db.query(User).filter(User.id == "user-demo-default").first()
    if not default_user:
        default_user = User(
            id="user-demo-default",
            name="Raahi Commuter",
            email="commuter@raahi.in"
        )
        db.add(default_user)
        stats["users"] += 1

    # 2. Cities
    cities_data = [
        {"id": "delhi-ncr", "name": "Delhi NCR", "lat": 28.6139, "lon": 77.2090},
        {"id": "mumbai", "name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
        {"id": "bengaluru", "name": "Bengaluru", "lat": 12.9716, "lon": 77.5946},
        {"id": "mathura-vrindavan", "name": "Mathura & Vrindavan", "lat": 27.4924, "lon": 77.6737},
    ]

    city_map = {}
    for c in cities_data:
        obj = db.query(City).filter(City.id == c["id"]).first()
        if not obj:
            obj = City(
                id=c["id"],
                name=c["name"],
                country="India",
                timezone="Asia/Kolkata",
                center_lat=c["lat"],
                center_lon=c["lon"],
                is_active=True
            )
            db.add(obj)
            stats["cities"] += 1
        city_map[c["name"]] = c["id"]
        city_map[c["id"]] = c["id"]

    db.flush()

    # 3. Transit Agencies
    agencies_data = [
        # Delhi NCR
        {"id": "dmrc", "name": "Delhi Metro Rail Corporation", "city_id": "delhi-ncr", "source": "official"},
        {"id": "dtc", "name": "Delhi Transport Corporation", "city_id": "delhi-ncr", "source": "delhi_otd"},
        {"id": "nr", "name": "Northern Railway (Suburban EMU / Ring Rail)", "city_id": "delhi-ncr", "source": "ir_railradar"},
        # Mumbai
        {"id": "mmrda", "name": "Maha Mumbai Metro (MMRDA / MMRC)", "city_id": "mumbai", "source": "official"},
        {"id": "wr", "name": "Western Railway (Mumbai Suburban Local)", "city_id": "mumbai", "source": "ir_railradar"},
        {"id": "cr", "name": "Central Railway (Mumbai Suburban & Harbour)", "city_id": "mumbai", "source": "ir_railradar"},
        {"id": "best", "name": "Brihanmumbai Electric Supply & Transport (BEST)", "city_id": "mumbai", "source": "official"},
        # Bengaluru
        {"id": "bmrcl", "name": "Bangalore Metro Rail Corporation (Namma Metro)", "city_id": "bengaluru", "source": "official"},
        {"id": "bmtc", "name": "Bangalore Metropolitan Transport Corporation", "city_id": "bengaluru", "source": "official"},
        {"id": "swr", "name": "South Western Railway (Bengaluru Commuter)", "city_id": "bengaluru", "source": "ir_railradar"},
        # Mathura & Vrindavan
        {"id": "mvcta", "name": "Mathura-Vrindavan Smart City Transport Authority", "city_id": "mathura-vrindavan", "source": "official"},
        {"id": "ncr", "name": "North Central Railway (Mathura - Vrindavan Rail Bus)", "city_id": "mathura-vrindavan", "source": "ir_railradar"}
    ]

    for a in agencies_data:
        obj = db.query(TransitAgency).filter(TransitAgency.id == a["id"]).first()
        if not obj:
            obj = TransitAgency(
                id=a["id"],
                name=a["name"],
                city_id=a["city_id"],
                source=a["source"],
                active_status="active"
            )
            db.add(obj)
            stats["agencies"] += 1

    db.flush()

    # 4. Stations & Stops (from PLACES_DATABASE)
    existing_stn_ids = {s.id for s in db.query(Station.id).all()}

    for city_name, places in PLACES_DATABASE.items():
        c_id = city_map.get(city_name, "delhi-ncr")
        for p in places:
            stn_id = f"stn_{c_id}_{abs(hash(p['name'])) % 1000000}"
            if stn_id not in existing_stn_ids:
                ext_id = None
                if "NDLS" in p["name"]:
                    ext_id = "NDLS"
                elif "MTJ" in p["name"]:
                    ext_id = "MTJ"
                elif "CSMT" in p["name"]:
                    ext_id = "CSMT"

                stn_obj = Station(
                    id=stn_id,
                    external_stop_id=ext_id,
                    city_id=c_id,
                    name=p["name"],
                    latitude=float(p["lat"]),
                    longitude=float(p["lon"]),
                    stop_type=p.get("category", "metro_station"),
                    source="places_catalog"
                )
                db.add(stn_obj)
                existing_stn_ids.add(stn_id)
                stats["stations"] += 1

    # 5. Stations from RAIL_STATIONS (87 Suburban Railway Stations)
    for r_stn in RAIL_STATIONS.values():
        r_id = f"rail_{r_stn.code.lower()}"
        if r_id not in existing_stn_ids:
            # Map station city
            c_lower = r_stn.city.lower()
            if "mumbai" in c_lower:
                c_id = "mumbai"
            elif "bengaluru" in c_lower or "bangalore" in c_lower:
                c_id = "bengaluru"
            elif "mathura" in c_lower or "vrindavan" in c_lower:
                c_id = "mathura-vrindavan"
            else:
                c_id = "delhi-ncr"

            stn_obj = Station(
                id=r_id,
                external_stop_id=r_stn.code,
                city_id=c_id,
                name=r_stn.name,
                latitude=float(r_stn.lat),
                longitude=float(r_stn.lon),
                stop_type="railway_station",
                source="ir_railradar"
            )
            db.add(stn_obj)
            existing_stn_ids.add(r_id)
            stats["stations"] += 1

    db.flush()

    # 6. Commuter Train Routes, Trips & Stop Times (from SCHEDULE_DATABASE)
    existing_routes = {r.id for r in db.query(Route.id).all()}
    existing_trips = {t.id for t in db.query(Trip.id).all()}

    # Service calendar
    if not db.query(CalendarService).filter(CalendarService.service_id == "daily_all").first():
        db.add(CalendarService(
            service_id="daily_all",
            operating_days="Mon,Tue,Wed,Thu,Fri,Sat,Sun",
            start_date="2026-01-01",
            end_date="2026-12-31"
        ))

    for train_no, sched in SCHEDULE_DATABASE.items():
        # Determine Agency and City
        sched_name_lower = sched.train_name.lower()
        if "western" in sched_name_lower or "churchgate" in sched_name_lower or "borivali" in sched_name_lower or "virar" in sched_name_lower:
            agency_id = "wr"
            city_id = "mumbai"
            route_type = "suburban_rail"
            line_color = "#0284C7"
        elif "central" in sched_name_lower or "csmt" in sched_name_lower or "thane" in sched_name_lower or "kalyan" in sched_name_lower:
            agency_id = "cr"
            city_id = "mumbai"
            route_type = "suburban_rail"
            line_color = "#DC2626"
        elif "harbour" in sched_name_lower or "panvel" in sched_name_lower:
            agency_id = "cr"
            city_id = "mumbai"
            route_type = "suburban_rail"
            line_color = "#0D9488"
        elif "swr" in sched_name_lower or "whitefield" in sched_name_lower or "ksr" in sched_name_lower:
            agency_id = "swr"
            city_id = "bengaluru"
            route_type = "suburban_rail"
            line_color = "#7C3AED"
        elif "rail bus" in sched_name_lower or "04419" in train_no or "04420" in train_no:
            agency_id = "ncr"
            city_id = "mathura-vrindavan"
            route_type = "rail_bus"
            line_color = "#059669"
        else:
            agency_id = "nr"
            city_id = "delhi-ncr"
            route_type = "suburban_rail"
            line_color = "#16A34A"

        route_id = f"route_train_{train_no}"
        if route_id not in existing_routes:
            db_route = Route(
                id=route_id,
                external_route_id=train_no,
                agency_id=agency_id,
                city_id=city_id,
                name=sched.train_name,
                route_type=route_type,
                line_color=line_color,
                source="ir_railradar"
            )
            db.add(db_route)
            existing_routes.add(route_id)
            stats["routes"] += 1

        trip_id = f"trip_train_{train_no}"
        if trip_id not in existing_trips:
            db_trip = Trip(
                id=trip_id,
                external_trip_id=train_no,
                route_id=route_id,
                service_id="daily_all",
                trip_headsign=sched.destination_name,
                direction_id=0
            )
            db.add(db_trip)
            existing_trips.add(trip_id)
            stats["trips"] += 1

            # Insert halts as stop_times
            for idx, h in enumerate(sched.halts, 1):
                stn_record = db.query(Station).filter(Station.external_stop_id == h.station_code).first()
                if not stn_record:
                    # fallback by name search
                    stn_record = db.query(Station).filter(Station.name.ilike(f"%{h.station_name}%")).first()

                if stn_record:
                    stop_time_obj = StopTime(
                        id=f"st_{trip_id}_{idx}",
                        trip_id=trip_id,
                        stop_id=stn_record.id,
                        stop_sequence=idx,
                        arrival_time=h.arrival_time or "00:00",
                        departure_time=h.departure_time or "00:00"
                    )
                    db.add(stop_time_obj)
                    stats["stop_times"] += 1

    db.flush()

    # 7. Saved Journeys (Sample Commutes across all cities)
    existing_journeys = {j.id for j in db.query(SavedJourney.id).all()}
    now_str = datetime.now(timezone.utc).isoformat()

    sample_journeys = [
        # Delhi
        {"id": "delhi-commute-1", "name": "Rajiv Chowk to Cyber City (Office)", "origin": "Rajiv Chowk (Connaught Place)", "dest": "Cyber City (Gurugram)", "city": "Delhi NCR", "mode": "fastest", "dur": 42, "fare": 50.0, "transfers": 1},
        {"id": "delhi-commute-2", "name": "Delhi University to NDLS Station", "origin": "Vishwavidyalaya (Delhi University)", "dest": "New Delhi Railway Station (NDLS)", "city": "Delhi NCR", "mode": "fastest", "dur": 22, "fare": 30.0, "transfers": 0},
        # Mumbai
        {"id": "mumbai-commute-1", "name": "CSMT to BKC (Corporate Corridor)", "origin": "Chhatrapati Shivaji Maharaj Terminus (CSMT)", "dest": "Bandra Kurla Complex (BKC)", "city": "Mumbai", "mode": "fastest", "dur": 26, "fare": 35.0, "transfers": 1},
        {"id": "mumbai-commute-2", "name": "Churchgate to Borivali Fast Local", "origin": "Churchgate Railway Station", "dest": "Borivali Railway Station", "city": "Mumbai", "mode": "fastest", "dur": 55, "fare": 10.0, "transfers": 0},
        # Bengaluru
        {"id": "blr-commute-1", "name": "Majestic to Whitefield (Purple Line)", "origin": "Majestic (KSR Bengaluru)", "dest": "Whitefield (Kadugodi)", "city": "Bengaluru", "mode": "fastest", "dur": 44, "fare": 60.0, "transfers": 0},
        # Mathura & Vrindavan
        {"id": "mathura-commute-1", "name": "Mathura Jn to Bankey Bihari Ji (Darshan)", "origin": "Mathura Junction Railway Station (MTJ)", "dest": "Shri Bankey Bihari Ji Mandir (Vrindavan)", "city": "Mathura & Vrindavan", "mode": "fastest", "dur": 32, "fare": 45.0, "transfers": 1},
    ]

    for sj in sample_journeys:
        if sj["id"] not in existing_journeys:
            db.add(SavedJourney(
                id=sj["id"],
                user_id="user-demo-default",
                name=sj["name"],
                origin=sj["origin"],
                destination=sj["dest"],
                city=sj["city"],
                preferred_mode=sj["mode"],
                created_at=now_str,
                typical_duration_minutes=sj["dur"],
                typical_fare_inr=sj["fare"],
                typical_transfers=sj["transfers"],
                current_delay_minutes=0,
                active_status="Normal Service"
            ))
            existing_journeys.add(sj["id"])
            stats["saved_journeys"] += 1

    # 8. User Preference
    user_pref = db.query(UserPreference).filter(UserPreference.user_id == "user-demo-default").first()
    if not user_pref:
        db.add(UserPreference(
            id="pref-demo-default",
            user_id="user-demo-default",
            preferred_language="en",
            selected_city="Delhi NCR",
            accessible_only=False,
            reduced_motion=False,
            travel_preferences_json='{"fastest": true, "cheapest": false, "prefer_rail": true}'
        ))

    # 9. Saved Places (Home & Work)
    home_place = db.query(SavedPlace).filter(SavedPlace.user_id == "user-demo-default", SavedPlace.category == "home").first()
    if not home_place:
        db.add(SavedPlace(
            id="place-home-default",
            user_id="user-demo-default",
            name="Home",
            address="Rajiv Chowk / Connaught Place",
            category="home",
            latitude=28.6328,
            longitude=77.2197,
            city="Delhi NCR"
        ))
        db.add(SavedPlace(
            id="place-work-default",
            user_id="user-demo-default",
            name="Work",
            address="Cyber City, Gurugram",
            category="work",
            latitude=28.4950,
            longitude=77.0895,
            city="Delhi NCR"
        ))

    db.commit()
    logger.info(f"Database seeding completed successfully: {stats}")
    return stats


if __name__ == "__main__":
    init_db()
    with SessionLocal() as session:
        result = seed_database(session)
        print("Seeder executed successfully. Stats:", result)
