"""
Idempotent MongoDB Seeder for Raahi Transit Platform.
Populates verified transit data into MongoDB collections:
- 4 Metropolitan Cities (Delhi NCR, Mumbai, Bengaluru, Mathura & Vrindavan)
- 12 Transit Agencies (DMRC, BEST, Western Railway, Central Railway, BMRCL, BMTC, etc.)
- 400+ Verified Transit Stations with GeoJSON Point coordinates for 2dsphere indexing
- Commuter Routes, Trips, and Stop Times
- Demo User, Default Commutes, Saved Places, and User Preferences
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from pymongo import UpdateOne
from .connection import get_sync_db, close_sync_mongo
from .indexes import init_sync_indexes
from ..transit_data import PLACES_DATABASE
from ..rail.providers.fallback_data import RAIL_STATIONS, SCHEDULE_DATABASE

logger = logging.getLogger("raahi.mongodb.seeder")


def seed_mongodb() -> Dict[str, int]:
    """Idempotently seeds the MongoDB database with real transit network records."""
    db = get_sync_db()
    init_sync_indexes(db)

    stats = {
        "cities": 0,
        "agencies": 0,
        "stations": 0,
        "routes": 0,
        "trips": 0,
        "stop_times": 0,
        "saved_routes": 0,
        "saved_places": 0,
        "users": 0
    }
    now = datetime.now(timezone.utc)

    # ==========================================================================
    # 1. Cities
    # ==========================================================================
    cities_data = [
        {
            "_id": "delhi-ncr",
            "name": "Delhi NCR",
            "country": "India",
            "timezone": "Asia/Kolkata",
            "center_lat": 28.6139,
            "center_lon": 77.2090,
            "is_active": True,
            "supported_transport_modes": ["metro", "bus", "rail", "auto", "erickshaw"],
            "created_at": now,
            "updated_at": now
        },
        {
            "_id": "mumbai",
            "name": "Mumbai",
            "country": "India",
            "timezone": "Asia/Kolkata",
            "center_lat": 18.9750,
            "center_lon": 72.8258,
            "is_active": True,
            "supported_transport_modes": ["suburban_rail", "metro", "bus", "auto", "taxi", "ferry"],
            "created_at": now,
            "updated_at": now
        },
        {
            "_id": "bengaluru",
            "name": "Bengaluru",
            "country": "India",
            "timezone": "Asia/Kolkata",
            "center_lat": 12.9716,
            "center_lon": 77.5946,
            "is_active": True,
            "supported_transport_modes": ["metro", "bus", "auto", "suburban_rail"],
            "created_at": now,
            "updated_at": now
        },
        {
            "_id": "mathura-vrindavan",
            "name": "Mathura & Vrindavan",
            "country": "India",
            "timezone": "Asia/Kolkata",
            "center_lat": 27.4924,
            "center_lon": 77.6737,
            "is_active": True,
            "supported_transport_modes": ["ebus", "tempo", "erickshaw", "rail_bus", "auto", "taxi"],
            "created_at": now,
            "updated_at": now
        }
    ]

    city_ops = [
        UpdateOne({"_id": c["_id"]}, {"$set": c}, upsert=True)
        for c in cities_data
    ]
    city_res = db.cities.bulk_write(city_ops)
    stats["cities"] = city_res.upserted_count + city_res.matched_count

    # ==========================================================================
    # 2. Transit Agencies
    # ==========================================================================
    agencies_data = [
        {"_id": "dmrc", "name": "Delhi Metro Rail Corporation (DMRC)", "city_id": "delhi-ncr", "source": "official"},
        {"_id": "dtc", "name": "Delhi Transport Corporation (DTC)", "city_id": "delhi-ncr", "source": "official"},
        {"_id": "wr", "name": "Western Railway (Mumbai Suburban)", "city_id": "mumbai", "source": "official"},
        {"_id": "cr", "name": "Central Railway (Mumbai Suburban)", "city_id": "mumbai", "source": "official"},
        {"_id": "best", "name": "Brihanmumbai Electric Supply and Transport (BEST)", "city_id": "mumbai", "source": "official"},
        {"_id": "mmrda", "name": "Mumbai Metro One / Maha Mumbai Metro", "city_id": "mumbai", "source": "official"},
        {"_id": "bmrc", "name": "Bangalore Metro Rail Corporation Ltd (Namma Metro)", "city_id": "bengaluru", "source": "official"},
        {"_id": "bmtc", "name": "Bangalore Metropolitan Transport Corporation (BMTC)", "city_id": "bengaluru", "source": "official"},
        {"_id": "mvda", "name": "Mathura-Vrindavan Development Authority (E-Bus)", "city_id": "mathura-vrindavan", "source": "official"},
        {"_id": "braj_tempo", "name": "Braj Regional Shared Mobility & Tempos", "city_id": "mathura-vrindavan", "source": "official"},
        {"_id": "ncr_rail", "name": "North Central Railway (Mathura Rail Bus)", "city_id": "mathura-vrindavan", "source": "official"}
    ]

    agency_ops = [
        UpdateOne({"_id": a["_id"]}, {"$set": {**a, "updated_at": now}}, upsert=True)
        for a in agencies_data
    ]
    agency_res = db.transit_agencies.bulk_write(agency_ops)
    stats["agencies"] = agency_res.upserted_count + agency_res.matched_count

    # ==========================================================================
    # 3. Stations & Stops (from PLACES_DATABASE and RAIL_STATIONS)
    # ==========================================================================
    city_map = {
        "Delhi NCR": "delhi-ncr",
        "Mumbai": "mumbai",
        "Bengaluru": "bengaluru",
        "Mathura & Vrindavan": "mathura-vrindavan"
    }

    station_ops = []
    seen_ids = set()

    # 3a. Stations from PLACES_DATABASE
    for city_name, places in PLACES_DATABASE.items():
        cid = city_map.get(city_name, "delhi-ncr")
        for p in places:
            stn_id = f"p_{cid}_{p['name'].lower().replace(' ', '_').replace('/', '_')[:36]}"
            if stn_id in seen_ids:
                continue
            seen_ids.add(stn_id)

            lat = float(p["lat"])
            lon = float(p["lon"])
            doc = {
                "_id": stn_id,
                "city_id": cid,
                "name": p["name"],
                "latitude": lat,
                "longitude": lon,
                "location": {
                    "type": "Point",
                    "coordinates": [lon, lat]  # GeoJSON lon, lat
                },
                "stop_type": p.get("type", "metro_station"),
                "source": "places_database",
                "source_dataset_version": "2026.1",
                "updated_at": now
            }
            station_ops.append(UpdateOne({"_id": stn_id}, {"$set": doc}, upsert=True))

    # 3b. Stations from RAIL_STATIONS
    if isinstance(RAIL_STATIONS, dict):
        rail_stn_list = RAIL_STATIONS.values()
    else:
        rail_stn_list = RAIL_STATIONS

    for r_stn in rail_stn_list:
        code = getattr(r_stn, "code", "")
        name = getattr(r_stn, "name", "")
        city_raw = getattr(r_stn, "city", "Mumbai")
        lat = getattr(r_stn, "lat", 0.0)
        lon = getattr(r_stn, "lon", 0.0)
        cid = city_map.get(city_raw, "mumbai")

        stn_id = f"rail_{code.lower()}"
        if stn_id in seen_ids:
            continue
        seen_ids.add(stn_id)

        doc = {
            "_id": stn_id,
            "external_stop_id": code,
            "city_id": cid,
            "name": name,
            "latitude": lat,
            "longitude": lon,
            "location": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "stop_type": "railway_station",
            "source": "rail_network",
            "source_dataset_version": "2026.1",
            "updated_at": now
        }
        station_ops.append(UpdateOne({"_id": stn_id}, {"$set": doc}, upsert=True))

    if station_ops:
        stn_res = db.stations.bulk_write(station_ops)
        stats["stations"] = stn_res.upserted_count + stn_res.matched_count

    # ==========================================================================
    # 4. Routes, Trips & Stop Times from SCHEDULE_DATABASE
    # ==========================================================================
    route_ops = []
    trip_ops = []
    stop_time_ops = []

    for train_no, sched in SCHEDULE_DATABASE.items():
        line_type = getattr(sched, "train_type", "Suburban")
        train_name = getattr(sched, "train_name", f"Train {train_no}")
        agency_id = "wr" if "west" in train_name.lower() or "churchgate" in getattr(sched, "destination_name", "").lower() else "cr"
        if "mathura" in train_name.lower():
            agency_id = "ncr_rail"
            city_id = "mathura-vrindavan"
        else:
            city_id = "mumbai"

        route_id = f"rt_{agency_id}_{train_no}"
        trip_id = f"tr_{train_no}"

        route_doc = {
            "_id": route_id,
            "external_route_id": train_no,
            "agency_id": agency_id,
            "city_id": city_id,
            "route_name": train_name,
            "route_type": "suburban_rail",
            "line_color": "#2563EB" if agency_id == "wr" else "#DC2626",
            "source": "schedule_database",
            "updated_at": now
        }
        route_ops.append(UpdateOne({"_id": route_id}, {"$set": route_doc}, upsert=True))

        trip_doc = {
            "_id": trip_id,
            "external_trip_id": train_no,
            "route_id": route_id,
            "service_id": "daily_all",
            "headsign": sched.destination_name if hasattr(sched, "destination_name") else train_name,
            "source": "schedule_database",
            "updated_at": now
        }
        trip_ops.append(UpdateOne({"_id": trip_id}, {"$set": trip_doc}, upsert=True))

        for idx, halt in enumerate(sched.halts, 1):
            st_id = f"st_{train_no}_{idx}"
            st_doc = {
                "_id": st_id,
                "trip_id": trip_id,
                "stop_id": f"rail_{halt.station_code.lower()}",
                "stop_sequence": idx,
                "arrival_time": halt.arrival_time or halt.departure_time or "00:00",
                "departure_time": halt.departure_time or halt.arrival_time or "00:00",
                "source": "schedule_database",
                "updated_at": now
            }
            stop_time_ops.append(UpdateOne({"_id": st_id}, {"$set": st_doc}, upsert=True))

    if route_ops:
        rt_res = db.routes.bulk_write(route_ops)
        stats["routes"] = rt_res.upserted_count + rt_res.matched_count
    if trip_ops:
        tr_res = db.trips.bulk_write(trip_ops)
        stats["trips"] = tr_res.upserted_count + tr_res.matched_count
    if stop_time_ops:
        st_res = db.stop_times.bulk_write(stop_time_ops)
        stats["stop_times"] = st_res.upserted_count + st_res.matched_count

    # ==========================================================================
    # 5. Default User, Saved Routes, Places & Preferences
    # ==========================================================================
    # Seed demo users with valid bcrypt hashed passwords
    from ..auth.security import hash_password
    default_hash = hash_password("Raahi@2026")
    demo_hash = hash_password("Demo@1234")

    user_doc = {
        "_id": "user-demo-default",
        "name": "Raahi Commuter",
        "email": "commuter@raahi.in",
        "email_normalized": "commuter@raahi.in",
        "password_hash": default_hash,
        "role": "commuter",
        "email_verified": True,
        "status": "active",
        "created_at": now,
        "updated_at": now
    }
    db.users.replace_one({"_id": user_doc["_id"]}, user_doc, upsert=True)

    demo_user = {
        "_id": "user-demo-commuter",
        "name": "Demo Commuter",
        "email": "demo@raahi.in",
        "email_normalized": "demo@raahi.in",
        "password_hash": demo_hash,
        "role": "commuter",
        "email_verified": True,
        "status": "active",
        "created_at": now,
        "updated_at": now
    }
    db.users.replace_one({"_id": demo_user["_id"]}, demo_user, upsert=True)
    stats["users"] = 2

    # Saved Routes
    sample_commutes = [
        {
            "_id": "commute-1",
            "user_id": "user-demo-default",
            "name": "Home to Cyber City (Daily Office)",
            "origin": "Rajiv Chowk (Connaught Place)",
            "destination": "Cyber City (Gurugram)",
            "city": "Delhi NCR",
            "preferred_mode": "fastest",
            "typical_duration_minutes": 42,
            "typical_fare_inr": 50.0,
            "typical_transfers": 1,
            "current_delay_minutes": 0,
            "active_status": "Normal Service",
            "created_at": now
        },
        {
            "_id": "commute-2",
            "user_id": "user-demo-default",
            "name": "Hostel to NDLS (Weekend Travel)",
            "origin": "Vishwavidyalaya (Delhi University)",
            "destination": "New Delhi Railway Station (NDLS)",
            "city": "Delhi NCR",
            "preferred_mode": "fastest",
            "typical_duration_minutes": 22,
            "typical_fare_inr": 30.0,
            "typical_transfers": 0,
            "current_delay_minutes": 0,
            "active_status": "Normal Service",
            "created_at": now
        },
        {
            "_id": "commute-3",
            "user_id": "user-demo-default",
            "name": "Noida Tech Hub to Saket Mall",
            "origin": "Noida Sector 62",
            "destination": "Saket (Select Citywalk)",
            "city": "Delhi NCR",
            "preferred_mode": "cheapest",
            "typical_duration_minutes": 58,
            "typical_fare_inr": 45.0,
            "typical_transfers": 1,
            "current_delay_minutes": 4,
            "active_status": "Minor Congestion",
            "created_at": now
        }
    ]
    saved_route_ops = [
        UpdateOne({"_id": c["_id"]}, {"$set": c}, upsert=True)
        for c in sample_commutes
    ]
    sr_res = db.saved_routes.bulk_write(saved_route_ops)
    stats["saved_routes"] = sr_res.upserted_count + sr_res.matched_count

    # Saved Places
    sample_places = [
        {
            "_id": "place-home-default",
            "user_id": "user-demo-default",
            "name": "Home",
            "address": "Rajiv Chowk / Connaught Place",
            "category": "home",
            "latitude": 28.6328,
            "longitude": 77.2197,
            "city": "Delhi NCR",
            "created_at": now
        },
        {
            "_id": "place-work-default",
            "user_id": "user-demo-default",
            "name": "Work",
            "address": "Cyber City, Gurugram",
            "category": "work",
            "latitude": 28.4950,
            "longitude": 77.0895,
            "city": "Delhi NCR",
            "created_at": now
        }
    ]
    place_ops = [
        UpdateOne({"_id": p["_id"]}, {"$set": p}, upsert=True)
        for p in sample_places
    ]
    sp_res = db.saved_places.bulk_write(place_ops)
    stats["saved_places"] = sp_res.upserted_count + sp_res.matched_count

    # User Preferences
    pref_doc = {
        "_id": "pref-demo-default",
        "user_id": "user-demo-default",
        "preferred_language": "en",
        "selected_city": "Delhi NCR",
        "accessible_only": False,
        "reduced_motion": False,
        "travel_preferences": {
            "fastest": True,
            "cheapest": False,
            "prefer_rail": True
        },
        "updated_at": now
    }
    db.user_preferences.replace_one({"_id": pref_doc["_id"]}, pref_doc, upsert=True)

    logger.info(f"MongoDB seeded successfully: {stats}")
    return stats


if __name__ == "__main__":
    result = seed_mongodb()
    print("MongoDB Seeder Execution Stats:", result)
    close_sync_mongo()
