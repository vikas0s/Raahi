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
            "lines": ["Yellow Line"]
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
    }
}
