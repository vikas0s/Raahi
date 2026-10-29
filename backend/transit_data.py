"""
Real transit network nodes, coordinates, routes, and transit lines for Raahi.
Default primary network: Delhi NCR (DMRC Metro, DTC Electric Buses, Airport Express, Northern Suburban Rail).
Also includes key transit nodes for Mumbai and Bengaluru to support multi-city switching.
"""
from typing import Dict, List, Any

# Transit Places by City
PLACES_DATABASE: Dict[str, List[Dict[str, Any]]] = {
    "Delhi NCR": [
        {
            "name": "Rajiv Chowk (Connaught Place)",
            "lat": 28.6328,
            "lon": 77.2197,
            "category": "metro_station",
            "aliases": ["cp", "connaught place", "central delhi", "rajiv chowk", "inner circle"],
            "lines": ["Yellow Line", "Blue Line"]
        },
        {
            "name": "Kashmere Gate ISBT",
            "lat": 28.6675,
            "lon": 77.2285,
            "category": "metro_station",
            "aliases": ["kashmere gate", "isbt", "old delhi", "interstate bus terminal"],
            "lines": ["Yellow Line", "Red Line", "Violet Line", "DTC Terminal"]
        },
        {
            "name": "New Delhi Railway Station (NDLS)",
            "lat": 28.6431,
            "lon": 77.2223,
            "category": "railway_station",
            "aliases": ["ndls", "new delhi station", "paharganj", "ajmeri gate"],
            "lines": ["Yellow Line", "Airport Express", "Northern Railway"]
        },
        {
            "name": "Hauz Khas",
            "lat": 28.5434,
            "lon": 77.2064,
            "category": "metro_station",
            "aliases": ["hauz khas", "iit delhi", "hkv", "south delhi interchange"],
            "lines": ["Yellow Line", "Magenta Line"]
        },
        {
            "name": "Cyber City (Gurugram)",
            "lat": 28.4950,
            "lon": 77.0895,
            "category": "landmark",
            "aliases": ["cyber hub", "dlf cyber city", "gurgaon tech park", "cyber city"],
            "lines": ["Rapid Metro Gurugram", "Yellow Line (via Sikanderpur)"]
        },
        {
            "name": "Millennium City Centre (Gurugram)",
            "lat": 28.4593,
            "lon": 77.0725,
            "category": "metro_station",
            "aliases": ["huda city centre", "millennium city", "gurgaon south", "sector 29"],
            "lines": ["Yellow Line"]
        },
        {
            "name": "Noida Sector 62",
            "lat": 28.6279,
            "lon": 77.3622,
            "category": "metro_station",
            "aliases": ["noida 62", "electronic city", "noida it hub", "fortis noida"],
            "lines": ["Blue Line"]
        },
        {
            "name": "Botanical Garden (Noida)",
            "lat": 28.5641,
            "lon": 77.3342,
            "category": "metro_station",
            "aliases": ["botanical", "noida interchange", "sector 38"],
            "lines": ["Blue Line", "Magenta Line"]
        },
        {
            "name": "IGI Airport Terminal 3",
            "lat": 28.5562,
            "lon": 77.0864,
            "category": "landmark",
            "aliases": ["igi", "airport", "t3", "delhi airport", "aerocity"],
            "lines": ["Airport Express"]
        },
        {
            "name": "Anand Vihar ISBT",
            "lat": 28.6469,
            "lon": 77.3160,
            "category": "railway_station",
            "aliases": ["anand vihar", "east delhi terminal", "anvt"],
            "lines": ["Blue Line", "Pink Line", "Northern Railway"]
        },
        {
            "name": "Chandni Chowk",
            "lat": 28.6579,
            "lon": 77.2301,
            "category": "landmark",
            "aliases": ["red fort", "lal qila", "old delhi bazaar", "chandni chowk"],
            "lines": ["Yellow Line"]
        },
        {
            "name": "Lajpat Nagar Central Market",
            "lat": 28.5708,
            "lon": 77.2373,
            "category": "metro_station",
            "aliases": ["lajpat nagar", "central market", "defence colony"],
            "lines": ["Violet Line", "Pink Line", "DTC Bus 534"]
        },
        {
            "name": "Nehru Place IT Hub",
            "lat": 28.5493,
            "lon": 77.2526,
            "category": "metro_station",
            "aliases": ["nehru place", "electronics market", "kalkaji"],
            "lines": ["Violet Line", "Magenta Line (Kalkaji)"]
        },
        {
            "name": "Saket (Select Citywalk)",
            "lat": 28.5222,
            "lon": 77.2148,
            "category": "landmark",
            "aliases": ["saket", "citywalk", "max hospital saket", "south court"],
            "lines": ["Yellow Line", "DTC Bus 419"]
        },
        {
            "name": "Janakpuri West",
            "lat": 28.6294,
            "lon": 77.0778,
            "category": "metro_station",
            "aliases": ["janakpuri", "west delhi junction"],
            "lines": ["Blue Line", "Magenta Line"]
        },
        {
            "name": "Vishwavidyalaya (Delhi University)",
            "lat": 28.6974,
            "lon": 77.2144,
            "category": "metro_station",
            "aliases": ["du north campus", "vishwavidyalaya", "arts faculty", "university"],
            "lines": ["Yellow Line"],
            "has_direct_metro": True
        },
        {
            "name": "Vasant Kunj (Sector C-9)",
            "lat": 28.5284,
            "lon": 77.1512,
            "category": "landmark",
            "aliases": ["vasant kunj", "promenade", "ambience vasant kunj", "vk sector c"],
            "lines": ["DTC Electric Bus 534", "Auto / E-Rickshaw to Chhatarpur Metro"],
            "has_direct_metro": False,
            "nearest_metro": "Chhatarpur",
            "metro_dist_km": 3.8
        },
        {
            "name": "Sangam Vihar (Devli More)",
            "lat": 28.5020,
            "lon": 77.2410,
            "category": "landmark",
            "aliases": ["sangam vihar", "devli", "tigdri", "hamdard"],
            "lines": ["DTC Electric Bus 419", "Auto / E-Rickshaw to Saket Metro"],
            "has_direct_metro": False,
            "nearest_metro": "Saket (Select Citywalk)",
            "metro_dist_km": 4.1
        },
        {
            "name": "Najafgarh (BDO Complex)",
            "lat": 28.6130,
            "lon": 76.9850,
            "category": "landmark",
            "aliases": ["najafgarh", "thana road", "dehat", "dichau kalan"],
            "lines": ["DTC Bus 729", "Auto to Dhansa Bus Stand Metro"],
            "has_direct_metro": False,
            "nearest_metro": "Janakpuri West",
            "metro_dist_km": 6.8
        },
        {
            "name": "Bawana Industrial Area Sector 1",
            "lat": 28.7980,
            "lon": 77.0510,
            "category": "landmark",
            "aliases": ["bawana", "bawana industrial", "dsiidc bawana", "outer delhi"],
            "lines": ["DTC Bus 114", "DTC Electric Express", "Auto to Samaypur Badli"],
            "has_direct_metro": False,
            "nearest_metro": "Kashmere Gate ISBT",
            "metro_dist_km": 14.2
        },
        {
            "name": "Burari (Transport Authority)",
            "lat": 28.7420,
            "lon": 77.2020,
            "category": "landmark",
            "aliases": ["burari", "burari crossing", "sant nagar burari"],
            "lines": ["DTC Bus 185", "Auto to Vishwavidyalaya Metro"],
            "has_direct_metro": False,
            "nearest_metro": "Vishwavidyalaya (Delhi University)",
            "metro_dist_km": 4.6
        }
    ],
    "Mumbai": [
        {
            "name": "Chhatrapati Shivaji Maharaj Terminus (CSMT)",
            "lat": 18.9400,
            "lon": 72.8353,
            "category": "railway_station",
            "aliases": ["csmt", "vt", "victoria terminus", "south mumbai"],
            "lines": ["Central Railway", "Harbour Line"]
        },
        {
            "name": "Bandra Kurla Complex (BKC)",
            "lat": 19.0657,
            "lon": 72.8687,
            "category": "landmark",
            "aliases": ["bkc", "bandra east", "financial district"],
            "lines": ["Mumbai Metro Line 3", "BEST Electric Feeder"]
        },
        {
            "name": "Andheri Station",
            "lat": 19.1197,
            "lon": 72.8464,
            "category": "metro_station",
            "aliases": ["andheri", "western suburbs", "andheri west"],
            "lines": ["Western Railway", "Metro Line 1 (Versova-Ghatkopar)"]
        },
        {
            "name": "Ghatkopar Station",
            "lat": 19.0863,
            "lon": 72.9084,
            "category": "metro_station",
            "aliases": ["ghatkopar", "metro 1 terminal"],
            "lines": ["Central Railway", "Metro Line 1"]
        }
    ],
    "Bengaluru": [
        {
            "name": "Majestic (KSR Bengaluru)",
            "lat": 12.9781,
            "lon": 77.5695,
            "category": "railway_station",
            "aliases": ["majestic", "kempegowda station", "ksr", "central bus stand"],
            "lines": ["Purple Line", "Green Line", "BMTC Hub"]
        },
        {
            "name": "Indiranagar 100ft Road",
            "lat": 12.9784,
            "lon": 77.6408,
            "category": "landmark",
            "aliases": ["indiranagar", "cmh road", "100 ft"],
            "lines": ["Purple Line", "BMTC Feeder"]
        },
        {
            "name": "Electronic City Phase 1",
            "lat": 12.8452,
            "lon": 77.6602,
            "category": "landmark",
            "aliases": ["ecity", "infosys gate", "wipro ecity"],
            "lines": ["Yellow Line (Namma Metro)", "BMTC Vayu Vajra"]
        },
        {
            "name": "Whitefield (Kadugodi)",
            "lat": 12.9961,
            "lon": 77.7601,
            "category": "metro_station",
            "aliases": ["whitefield", "itpl", "kadugodi metro"],
            "lines": ["Purple Line"]
        }
    ]
}

# Line colors & standard operating info
TRANSIT_LINES: Dict[str, Dict[str, Any]] = {
    "Yellow Line": {
        "color": "#E5A919",
        "mode": "metro",
        "fare_type": "dmrc",
        "avg_speed_kmh": 34,
        "operator": "Delhi Metro Rail Corporation"
    },
    "Blue Line": {
        "color": "#1976D2",
        "mode": "metro",
        "fare_type": "dmrc",
        "avg_speed_kmh": 34,
        "operator": "Delhi Metro Rail Corporation"
    },
    "Magenta Line": {
        "color": "#C2185B",
        "mode": "metro",
        "fare_type": "dmrc",
        "avg_speed_kmh": 38,
        "operator": "Delhi Metro Rail Corporation"
    },
    "Violet Line": {
        "color": "#7B1FA2",
        "mode": "metro",
        "fare_type": "dmrc",
        "avg_speed_kmh": 32,
        "operator": "Delhi Metro Rail Corporation"
    },
    "Airport Express": {
        "color": "#FF6F00",
        "mode": "metro",
        "fare_type": "airport_express",
        "avg_speed_kmh": 80,
        "operator": "Delhi Airport Metro Express"
    },
    "Rapid Metro Gurugram": {
        "color": "#43A047",
        "mode": "metro",
        "fare_type": "rapid_metro",
        "avg_speed_kmh": 30,
        "operator": "DMRC / Rapid Metro"
    },
    "DTC Electric Bus 534": {
        "color": "#2E7D32",
        "mode": "bus",
        "fare_type": "dtc",
        "avg_speed_kmh": 18,
        "operator": "Delhi Transport Corporation"
    },
    "DTC Express Bus 419": {
        "color": "#388E3C",
        "mode": "bus",
        "fare_type": "dtc",
        "avg_speed_kmh": 20,
        "operator": "Delhi Transport Corporation"
    },
    "Northern Suburban Rail": {
        "color": "#5D4037",
        "mode": "rail",
        "fare_type": "railway",
        "avg_speed_kmh": 40,
        "operator": "Indian Railways (Northern Zone)"
    },
    "Delhi Govt Metered Auto (TSR)": {
        "color": "#E68A00",
        "mode": "auto",
        "fare_type": "govt_meter",
        "avg_speed_kmh": 26,
        "operator": "Delhi Transport Dept (Regulated Auto)"
    },
    "Shared E-Rickshaw Feeder": {
        "color": "#00897B",
        "mode": "erickshaw",
        "fare_type": "fixed_hop",
        "avg_speed_kmh": 16,
        "operator": "Delhi Metro Last-Mile E-Rickshaw"
    },
    "BluSmart / Ride-Hailing Cab": {
        "color": "#3B5360",
        "mode": "taxi",
        "fare_type": "app_cab",
        "avg_speed_kmh": 32,
        "operator": "BluSmart EV / On-Demand Taxi"
    },
    "Delhi Metro E-Feeder Bus": {
        "color": "#00A86B",
        "mode": "ebus",
        "fare_type": "dmrc_feeder",
        "avg_speed_kmh": 22,
        "operator": "Delhi Metro Rail Corporation"
    }
}

# ==============================================================================
# Official Delhi Government Fare Regimes & Gazetted Fare Slabs
# ==============================================================================

DELHI_GOVT_FARES = {
    # DTC AC Low-Floor & Electric Buses (Tata Ultra EV, JBM Ecolife, PMI Electro)
    "dtc_ebus": {
        "slabs": [
            (4.0, 10.0),
            (8.0, 15.0),
            (12.0, 20.0),
            (999.0, 25.0),
        ],
        "pink_ticket_free": True,
        "operator": "Delhi Transport Corporation (DTC)",
    },
    # DTC Non-AC / Cluster Green Buses
    "dtc_non_ac": {
        "slabs": [
            (4.0, 5.0),
            (10.0, 10.0),
            (999.0, 15.0),
        ],
        "pink_ticket_free": True,
        "operator": "Delhi Transport Corporation (DTC)",
    },
    # Delhi Metro E-Feeder Buses (DMRC D-Line)
    "metro_feeder": {
        "slabs": [
            (4.0, 10.0),
            (8.0, 15.0),
            (999.0, 20.0),
        ],
        "pink_ticket_free": False,
        "operator": "DMRC Feeder EV",
    },
    # Delhi Govt Auto-Rickshaw (TSR - Three-Wheeler Scooter Rickshaw)
    # Gazetted Tariff: Base ₹30 for first 1.5 km, ₹11 per km thereafter
    "auto_rickshaw": {
        "base_fare": 30.0,
        "base_km": 1.5,
        "per_km": 11.0,
        "waiting_per_min": 0.75,
        "night_surcharge_pct": 25,
    },
    # E-Rickshaw (Shared Metro Last-Mile / Local Hopper)
    "erickshaw": {
        "short_hop_km": 1.5,
        "short_hop_fare": 10.0,
        "extended_hop_fare": 15.0,
    },
    # App-based Cab / Taxi (BluSmart Electric / Economy Cab)
    "taxi_cab": {
        "base_fare": 50.0,
        "base_km": 2.0,
        "per_km": 14.50,
        "per_min": 1.50,
    }
}

def calculate_dtc_fare(dist_km: float, is_electric: bool = True, is_pink_pass: bool = False):
    """Calculates official Delhi Govt DTC bus fare based on gazetted distance slabs."""
    if is_pink_pass:
        return 0.0, "Delhi Govt Pink Ticket (₹0 Free for Women Commuters)"
    mode_key = "dtc_ebus" if is_electric else "dtc_non_ac"
    slabs = DELHI_GOVT_FARES[mode_key]["slabs"]
    for max_km, fare in slabs:
        if dist_km <= max_km:
            bus_type = "DTC Electric Bus (Govt Slab)" if is_electric else "DTC Non-AC (Govt Slab)"
            return fare, f"{bus_type}: ₹{int(fare)} (up to {int(max_km)} km)"
    return 25.0 if is_electric else 15.0, "DTC Max Fare Slab"

def calculate_auto_fare(dist_km: float, is_night: bool = False):
    """Calculates official Delhi Government regulated metered TSR Auto-Rickshaw fare."""
    rates = DELHI_GOVT_FARES["auto_rickshaw"]
    base_km = rates["base_km"]
    base_fare = rates["base_fare"]
    per_km = rates["per_km"]
    
    if dist_km <= base_km:
        fare = base_fare
    else:
        fare = base_fare + (dist_km - base_km) * per_km
        
    if is_night:
        fare *= 1.25
        night_str = " (incl. 25% Night Surcharge 11PM-5AM)"
    else:
        night_str = ""
        
    rounded_fare = round(fare)
    return float(rounded_fare), f"Delhi Govt Meter: ₹{base_fare:.0f} (first 1.5km) + ₹{per_km:.0f}/km{night_str}"

def calculate_erickshaw_fare(dist_km: float):
    """Calculates shared E-Rickshaw fare for metro first/last mile hopper."""
    rates = DELHI_GOVT_FARES["erickshaw"]
    if dist_km <= rates["short_hop_km"]:
        return rates["short_hop_fare"], "Shared E-Rickshaw Feeder: Flat ₹10"
    return rates["extended_hop_fare"], "Shared E-Rickshaw Hopper: ₹15"

def calculate_cab_fare(dist_km: float, duration_mins: int):
    """Calculates realistic BluSmart / app-based ride-hailing taxi fare."""
    rates = DELHI_GOVT_FARES["taxi_cab"]
    base_fare = rates["base_fare"]
    base_km = rates["base_km"]
    per_km = rates["per_km"]
    per_min = rates["per_min"]
    
    fare = base_fare
    if dist_km > base_km:
        fare += (dist_km - base_km) * per_km
    fare += max(0, duration_mins - 10) * per_min
    rounded = round(fare / 5) * 5 # Round to nearest 5
    return float(rounded), f"BluSmart / App Taxi: ₹{base_fare:.0f} base + ₹{per_km:.1f}/km"

