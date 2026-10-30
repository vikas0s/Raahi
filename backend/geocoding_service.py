"""
Global Location Understanding and Geocoding Service for Raahi.
Multi-tiered place resolution:
1. High-accuracy verified local transit hubs and landmark aliases.
2. Indian Railways national station network (RailConnect).
3. OpenStreetMap Nominatim global geocoding for cities worldwide.
Provides structured ResolvedPlace objects and handles disambiguation.
"""
import re
import json
import logging
import urllib.request
import urllib.parse
from typing import Dict, List, Optional, Tuple, Any

from .models import ResolvedPlace
from .transit_data import PLACES_DATABASE

logger = logging.getLogger("raahi.geocoding")

# Common Global Landmark & Station Aliases
GLOBAL_ALIAS_MAP: Dict[str, Dict[str, Any]] = {
    # Mathura & Vrindavan
    "mathura junction": {"name": "Mathura Junction Railway Station (MTJ)", "lat": 27.4924, "lon": 77.6737, "city": "Mathura", "state": "Uttar Pradesh", "country": "India", "category": "railway_station"},
    "mtj": {"name": "Mathura Junction Railway Station (MTJ)", "lat": 27.4924, "lon": 77.6737, "city": "Mathura", "state": "Uttar Pradesh", "country": "India", "category": "railway_station"},
    "mathura stn": {"name": "Mathura Junction Railway Station (MTJ)", "lat": 27.4924, "lon": 77.6737, "city": "Mathura", "state": "Uttar Pradesh", "country": "India", "category": "railway_station"},
    "mathura station": {"name": "Mathura Junction Railway Station (MTJ)", "lat": 27.4924, "lon": 77.6737, "city": "Mathura", "state": "Uttar Pradesh", "country": "India", "category": "railway_station"},
    "gla university": {"name": "GLA University (NH-19, Chaumuhan)", "lat": 27.6057, "lon": 77.5933, "city": "Mathura", "state": "Uttar Pradesh", "country": "India", "category": "university"},
    "gla": {"name": "GLA University (NH-19, Chaumuhan)", "lat": 27.6057, "lon": 77.5933, "city": "Mathura", "state": "Uttar Pradesh", "country": "India", "category": "university"},
    "bankey bihari": {"name": "Shri Bankey Bihari Ji Mandir (Vrindavan)", "lat": 27.5815, "lon": 77.7018, "city": "Vrindavan", "state": "Uttar Pradesh", "country": "India", "category": "landmark"},
    "bihari ji": {"name": "Shri Bankey Bihari Ji Mandir (Vrindavan)", "lat": 27.5815, "lon": 77.7018, "city": "Vrindavan", "state": "Uttar Pradesh", "country": "India", "category": "landmark"},
    "prem mandir": {"name": "Prem Mandir (Vrindavan)", "lat": 27.5715, "lon": 77.6735, "city": "Vrindavan", "state": "Uttar Pradesh", "country": "India", "category": "landmark"},
    "iskcon vrindavan": {"name": "ISKCON Temple (Krishna Balaram Mandir, Vrindavan)", "lat": 27.5735, "lon": 77.6780, "city": "Vrindavan", "state": "Uttar Pradesh", "country": "India", "category": "landmark"},
    "janmasthan": {"name": "Shri Krishna Janmabhoomi (Janmasthan)", "lat": 27.5050, "lon": 77.6690, "city": "Mathura", "state": "Uttar Pradesh", "country": "India", "category": "landmark"},
    "janmabhoomi": {"name": "Shri Krishna Janmabhoomi (Janmasthan)", "lat": 27.5050, "lon": 77.6690, "city": "Mathura", "state": "Uttar Pradesh", "country": "India", "category": "landmark"},
    "krishna janmasthan": {"name": "Shri Krishna Janmabhoomi (Janmasthan)", "lat": 27.5050, "lon": 77.6690, "city": "Mathura", "state": "Uttar Pradesh", "country": "India", "category": "landmark"},
    "krishna janmabhoomi": {"name": "Shri Krishna Janmabhoomi (Janmasthan)", "lat": 27.5050, "lon": 77.6690, "city": "Mathura", "state": "Uttar Pradesh", "country": "India", "category": "landmark"},
    "jait": {"name": "Jait (NH-19 Village)", "lat": 27.5620, "lon": 77.6180, "city": "Mathura", "state": "Uttar Pradesh", "country": "India", "category": "locality"},
    "mant": {"name": "Mant (Tehsil & Block Headquarters)", "lat": 27.6100, "lon": 77.7600, "city": "Mathura", "state": "Uttar Pradesh", "country": "India", "category": "locality"},
    "govardhan": {"name": "Govardhan - Daan Ghati Mandir & Mansi Ganga", "lat": 27.5020, "lon": 77.4640, "city": "Govardhan", "state": "Uttar Pradesh", "country": "India", "category": "landmark"},
    
    # Delhi NCR
    "rohini": {"name": "Rohini (Delhi NCR)", "lat": 28.7150, "lon": 77.1160, "city": "Delhi NCR", "state": "Delhi", "country": "India", "category": "locality"},
    "rohni": {"name": "Rohini (Delhi NCR)", "lat": 28.7150, "lon": 77.1160, "city": "Delhi NCR", "state": "Delhi", "country": "India", "category": "locality"},
    "pari chowk": {"name": "Pari Chowk (Greater Noida)", "lat": 28.4631, "lon": 77.5081, "city": "Delhi NCR", "state": "Uttar Pradesh", "country": "India", "category": "landmark"},
    "greater noida": {"name": "Greater Noida (Pari Chowk)", "lat": 28.4631, "lon": 77.5081, "city": "Delhi NCR", "state": "Uttar Pradesh", "country": "India", "category": "locality"},
    "noida": {"name": "Noida City Centre", "lat": 28.5747, "lon": 77.3560, "city": "Delhi NCR", "state": "Uttar Pradesh", "country": "India", "category": "locality"},
    "gurugram": {"name": "Cyber City (Gurugram)", "lat": 28.4950, "lon": 77.0890, "city": "Delhi NCR", "state": "Haryana", "country": "India", "category": "locality"},
    "gurgaon": {"name": "Cyber City (Gurugram)", "lat": 28.4950, "lon": 77.0890, "city": "Delhi NCR", "state": "Haryana", "country": "India", "category": "locality"},
    "rajiv chowk": {"name": "Rajiv Chowk (Connaught Place)", "lat": 28.6328, "lon": 77.2197, "city": "Delhi", "state": "Delhi", "country": "India", "category": "metro_station"},
    "cp": {"name": "Rajiv Chowk (Connaught Place)", "lat": 28.6328, "lon": 77.2197, "city": "Delhi", "state": "Delhi", "country": "India", "category": "metro_station"},
    "connaught place": {"name": "Rajiv Chowk (Connaught Place)", "lat": 28.6328, "lon": 77.2197, "city": "Delhi", "state": "Delhi", "country": "India", "category": "landmark"},
    "cyber city": {"name": "Cyber City (Gurugram)", "lat": 28.4950, "lon": 77.0890, "city": "Gurugram", "state": "Haryana", "country": "India", "category": "landmark"},
    "delhi airport": {"name": "IGI Airport T3 (Airport Express Line)", "lat": 28.5562, "lon": 77.0999, "city": "Delhi", "state": "Delhi", "country": "India", "category": "airport"},
    "igi airport": {"name": "IGI Airport T3 (Airport Express Line)", "lat": 28.5562, "lon": 77.0999, "city": "Delhi", "state": "Delhi", "country": "India", "category": "airport"},
    "noida electronic city": {"name": "Noida Electronic City (Blue Line)", "lat": 28.6279, "lon": 77.3725, "city": "Noida", "state": "Uttar Pradesh", "country": "India", "category": "metro_station"},

    # Mumbai
    "mumbai airport": {"name": "Mumbai Airport (Chhatrapati Shivaji Maharaj International BOM)", "lat": 19.0896, "lon": 72.8656, "city": "Mumbai", "state": "Maharashtra", "country": "India", "category": "airport"},
    "mumbai central": {"name": "Mumbai Central Railway Station", "lat": 18.9696, "lon": 72.8193, "city": "Mumbai", "state": "Maharashtra", "country": "India", "category": "railway_station"},
    "gateway of india": {"name": "Gateway of India (Colaba)", "lat": 18.9220, "lon": 72.8347, "city": "Mumbai", "state": "Maharashtra", "country": "India", "category": "landmark"},
    "marine drive": {"name": "Marine Drive (Netaji Subhash Chandra Bose Road)", "lat": 18.9432, "lon": 72.8234, "city": "Mumbai", "state": "Maharashtra", "country": "India", "category": "landmark"},
    "csmt": {"name": "Chhatrapati Shivaji Maharaj Terminus (CSMT)", "lat": 18.9400, "lon": 72.8353, "city": "Mumbai", "state": "Maharashtra", "country": "India", "category": "railway_station"},
    "bkc": {"name": "Bandra Kurla Complex (BKC)", "lat": 19.0657, "lon": 72.8687, "city": "Mumbai", "state": "Maharashtra", "country": "India", "category": "landmark"},

    # Bengaluru
    "bengaluru airport": {"name": "Kempegowda International Airport (BLR)", "lat": 13.1986, "lon": 77.7066, "city": "Bengaluru", "state": "Karnataka", "country": "India", "category": "airport"},
    "bangalore airport": {"name": "Kempegowda International Airport (BLR)", "lat": 13.1986, "lon": 77.7066, "city": "Bengaluru", "state": "Karnataka", "country": "India", "category": "airport"},
    "electronic city": {"name": "Electronic City Phase 1", "lat": 12.8452, "lon": 77.6602, "city": "Bengaluru", "state": "Karnataka", "country": "India", "category": "landmark"},
    "majestic": {"name": "Majestic (KSR Bengaluru Station)", "lat": 12.9778, "lon": 77.5713, "city": "Bengaluru", "state": "Karnataka", "country": "India", "category": "railway_station"},

    # Global / International Landmarks
    "london kings cross": {"name": "London King's Cross Station", "lat": 51.5324, "lon": -0.1230, "city": "London", "state": "England", "country": "United Kingdom", "category": "railway_station"},
    "kings cross": {"name": "London King's Cross Station", "lat": 51.5324, "lon": -0.1230, "city": "London", "state": "England", "country": "United Kingdom", "category": "railway_station"},
    "heathrow": {"name": "Heathrow Airport (LHR)", "lat": 51.4700, "lon": -0.4543, "city": "London", "state": "England", "country": "United Kingdom", "category": "airport"},
    "london heathrow": {"name": "Heathrow Airport (LHR)", "lat": 51.4700, "lon": -0.4543, "city": "London", "state": "England", "country": "United Kingdom", "category": "airport"},
    "new york penn station": {"name": "Pennsylvania Station (Penn Station, NYC)", "lat": 40.7505, "lon": -73.9934, "city": "New York", "state": "New York", "country": "United States", "category": "railway_station"},
    "penn station": {"name": "Pennsylvania Station (Penn Station, NYC)", "lat": 40.7505, "lon": -73.9934, "city": "New York", "state": "New York", "country": "United States", "category": "railway_station"},
    "jfk": {"name": "John F. Kennedy International Airport (JFK)", "lat": 40.6413, "lon": -73.7781, "city": "New York", "state": "New York", "country": "United States", "category": "airport"},
    "jfk airport": {"name": "John F. Kennedy International Airport (JFK)", "lat": 40.6413, "lon": -73.7781, "city": "New York", "state": "New York", "country": "United States", "category": "airport"},
    "paris": {"name": "Paris Central", "lat": 48.8566, "lon": 2.3522, "city": "Paris", "state": "Île-de-France", "country": "France", "category": "locality"},
    "eiffel tower": {"name": "Eiffel Tower (Tour Eiffel, Paris)", "lat": 48.8584, "lon": 2.2945, "city": "Paris", "state": "Île-de-France", "country": "France", "category": "landmark"},
    "louvre": {"name": "Louvre Museum (Musée du Louvre)", "lat": 48.8606, "lon": 2.3376, "city": "Paris", "state": "Île-de-France", "country": "France", "category": "landmark"},
    
    # Regional Indian Cities
    "jaipur": {"name": "Jaipur City Center / Railway Station", "lat": 26.9196, "lon": 75.7878, "city": "Jaipur", "state": "Rajasthan", "country": "India", "category": "locality"},
    "agra": {"name": "Agra Cantt Railway Station (AGC)", "lat": 27.1583, "lon": 77.9904, "city": "Agra", "state": "Uttar Pradesh", "country": "India", "category": "railway_station"},
    "taj mahal": {"name": "Taj Mahal (Agra)", "lat": 27.1751, "lon": 78.0421, "city": "Agra", "state": "Uttar Pradesh", "country": "India", "category": "landmark"}
}

# Devanagari Hindi Place Names
HINDI_GEO_MAP: Dict[str, Dict[str, Any]] = {
    "मथुरा": GLOBAL_ALIAS_MAP["mathura junction"],
    "मथुरा जंक्शन": GLOBAL_ALIAS_MAP["mathura junction"],
    "जीएलए": GLOBAL_ALIAS_MAP["gla university"],
    "जीएलए यूनिवर्सिटी": GLOBAL_ALIAS_MAP["gla university"],
    "बांके बिहारी": GLOBAL_ALIAS_MAP["bankey bihari"],
    "बिहारी जी": GLOBAL_ALIAS_MAP["bankey bihari"],
    "प्रेम मंदिर": GLOBAL_ALIAS_MAP["prem mandir"],
    "इस्कॉन": GLOBAL_ALIAS_MAP["iskcon vrindavan"],
    "जन्मभूमि": GLOBAL_ALIAS_MAP["janmasthan"],
    "जैत": GLOBAL_ALIAS_MAP["jait"],
    "गोवर्धन": GLOBAL_ALIAS_MAP["govardhan"],
    "राजीव चौक": GLOBAL_ALIAS_MAP["rajiv chowk"],
    "कनॉट प्लेस": GLOBAL_ALIAS_MAP["connaught place"],
    "साइबर सिटी": GLOBAL_ALIAS_MAP["cyber city"],
    "दिल्ली एयरपोर्ट": GLOBAL_ALIAS_MAP["delhi airport"],
    "मुंबई एयरपोर्ट": GLOBAL_ALIAS_MAP["mumbai airport"],
    "मुंबई सेंट्रल": GLOBAL_ALIAS_MAP["mumbai central"],
    "गेटवे ऑफ इंडिया": GLOBAL_ALIAS_MAP["gateway of india"],
    "मरीन ड्राइव": GLOBAL_ALIAS_MAP["marine drive"],
    "बेंगलुरु एयरपोर्ट": GLOBAL_ALIAS_MAP["bengaluru airport"],
    "इलेक्ट्रॉनिक सिटी": GLOBAL_ALIAS_MAP["electronic city"],
    "पेरिस": GLOBAL_ALIAS_MAP["paris"],
    "एफिल टॉवर": GLOBAL_ALIAS_MAP["eiffel tower"],
    "जयपुर": GLOBAL_ALIAS_MAP["jaipur"],
    "आगरा": GLOBAL_ALIAS_MAP["agra"]
}

_GEOCODING_CACHE: Dict[str, Optional[ResolvedPlace]] = {}

class GeocodingService:
    def __init__(self):
        self._cache = _GEOCODING_CACHE

    def resolve_place(self, query: str, context_city: Optional[str] = None) -> Optional[ResolvedPlace]:
        """
        Resolves a natural language place query to a structured ResolvedPlace.
        Checks:
        1. Local aliases and pre-mapped hubs (Tier 1).
        2. Database search in PLACES_DATABASE across all cities.
        3. Indian Railways Station network (Tier 2).
        4. Global OpenStreetMap Nominatim geocoding (Tier 3).
        """
        raw = (query or "").strip()
        if not raw or len(raw) < 2:
            return None

        # Check in-memory cache
        cache_key = f"{raw.lower()}::{context_city or ''}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 1. Check Devanagari Hindi direct mapping
        for h_k, h_val in HINDI_GEO_MAP.items():
            if h_k in raw:
                place = self._create_resolved_place(h_val, raw)
                self._cache[cache_key] = place
                return place

        # Clean query for alias matching
        q_norm = raw.lower()
        q_norm = re.sub(r'\b(station|stn|mandir|temple|airport|junction|jn)\b', '', q_norm).strip()
        q_clean = re.sub(r'[,.\s]+(mathura|vrindavan|delhi|mumbai|bengaluru|bangalore|london|paris|new york|nyc)\b', '', q_norm, flags=re.I).strip()

        # 2. Check Global Alias Map with precision ranking
        # Step 2A: Exact match matching context_city
        if context_city:
            c_low = context_city.lower()
            for alias_key, alias_data in GLOBAL_ALIAS_MAP.items():
                if (q_norm == alias_key or q_clean == alias_key) and c_low in (alias_data.get("city") or "").lower():
                    place = self._create_resolved_place(alias_data, raw)
                    self._cache[cache_key] = place
                    return place

        # Step 2B: Exact alias match
        for alias_key, alias_data in GLOBAL_ALIAS_MAP.items():
            if q_norm == alias_key or q_clean == alias_key:
                place = self._create_resolved_place(alias_data, raw)
                self._cache[cache_key] = place
                return place

        # Step 2C: Substring match with context_city
        if context_city:
            c_low = context_city.lower()
            for alias_key, alias_data in GLOBAL_ALIAS_MAP.items():
                if (alias_key in q_norm or q_norm in alias_key) and c_low in (alias_data.get("city") or "").lower():
                    place = self._create_resolved_place(alias_data, raw)
                    self._cache[cache_key] = place
                    return place

        # Step 2D: Substring match general
        for alias_key, alias_data in GLOBAL_ALIAS_MAP.items():
            if len(alias_key) >= 4 and (alias_key in q_norm or q_norm in alias_key):
                place = self._create_resolved_place(alias_data, raw)
                self._cache[cache_key] = place
                return place

        # 3. Check PLACES_DATABASE across cities
        candidate = self._search_places_database(raw, context_city)
        if candidate:
            place = self._create_resolved_place(candidate, raw)
            self._cache[cache_key] = place
            return place

        # 4. Check Indian Railways Stations
        try:
            from .rail.service import rail_service_instance
            rail_stns = rail_service_instance.search_stations_sync(raw)
            if rail_stns:
                top_stn = rail_stns[0]
                place = ResolvedPlace(
                    name=top_stn.name,
                    display_name=f"{top_stn.name} ({top_stn.code}), {top_stn.city}",
                    lat=top_stn.lat,
                    lon=top_stn.lon,
                    category="railway_station",
                    city=top_stn.city,
                    state="India",
                    country="India",
                    place_id=top_stn.code,
                    raw_query=raw
                )
                self._cache[cache_key] = place
                return place
        except Exception:
            pass

        # Ambiguous place check (e.g. "Springfield", "Gandhi Nagar")
        if self._is_ambiguous_place_name(raw):
            ambiguous_place = ResolvedPlace(
                name=raw.title(),
                display_name=f"Ambiguous location: '{raw}'",
                lat=0.0,
                lon=0.0,
                category="ambiguous",
                raw_query=raw,
                is_ambiguous=True,
                disambiguation_options=[
                    f"{raw.title()}, IL, USA",
                    f"{raw.title()}, MO, USA",
                    f"{raw.title()}, MA, USA"
                ] if "springfield" in raw.lower() else [
                    f"{raw.title()} (City/State specification needed)"
                ]
            )
            self._cache[cache_key] = ambiguous_place
            return ambiguous_place

        # 5. Global OpenStreetMap Nominatim Geocoding
        global_result = self._geocode_nominatim(raw, context_city)
        if global_result:
            self._cache[cache_key] = global_result
            return global_result

        return None

    def _create_resolved_place(self, data: Dict[str, Any], raw_query: str) -> ResolvedPlace:
        city_val = data.get("city")
        state_val = data.get("state")
        country_val = data.get("country", "India")
        display_parts = [data.get("name", "")]
        if city_val:
            display_parts.append(city_val)
        if country_val and country_val != city_val:
            display_parts.append(country_val)
        display_name = ", ".join(p for p in display_parts if p)

        return ResolvedPlace(
            name=data.get("name", "Unknown Place"),
            display_name=display_name,
            lat=float(data.get("lat", 0.0)),
            lon=float(data.get("lon", 0.0)),
            category=data.get("category", "place"),
            city=city_val,
            state=state_val,
            country=country_val,
            place_id=data.get("name", "").lower().replace(" ", "-"),
            raw_query=raw_query
        )

    def _search_places_database(self, query: str, context_city: Optional[str]) -> Optional[Dict[str, Any]]:
        q_low = query.lower().strip()
        # Search target city first if provided
        cities = list(PLACES_DATABASE.keys())
        if context_city and context_city in PLACES_DATABASE:
            cities.remove(context_city)
            cities.insert(0, context_city)

        for c in cities:
            for p in PLACES_DATABASE[c]:
                p_name = p["name"].lower()
                if q_low == p_name or p_name.startswith(q_low) or q_low in p_name:
                    res = dict(p)
                    res["city"] = c
                    res["country"] = "India"
                    return res
                for alias in p.get("aliases", []):
                    a = alias.lower()
                    if len(a) >= 3 and (a == q_low or a in q_low or q_low in a):
                        res = dict(p)
                        res["city"] = c
                        res["country"] = "India"
                        return res
        return None

    def _geocode_nominatim(self, query: str, context_city: Optional[str]) -> Optional[ResolvedPlace]:
        """Query OpenStreetMap Nominatim with retry and timeout."""
        clean_q = query.strip()
        VERB_STOPWORDS = {"travel", "go", "reach", "get", "commute", "from", "to", "want", "need", "please", "route", "rasta"}
        if clean_q.lower() in VERB_STOPWORDS:
            return None

        if context_city and context_city.lower() not in clean_q.lower():
            search_str = f"{clean_q}, {context_city}"
        else:
            search_str = clean_q

        try:
            encoded = urllib.parse.quote(search_str)
            url = f"https://nominatim.openstreetmap.org/search?q={encoded}&format=jsonv2&addressdetails=1&limit=3"
            req = urllib.request.Request(url, headers={"User-Agent": "RaahiGlobalTransit/1.0"})
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                data = json.loads(resp.read().decode())
                if not data:
                    # Retry with bare query if context city was appended
                    if search_str != clean_q:
                        encoded_bare = urllib.parse.quote(clean_q)
                        url_bare = f"https://nominatim.openstreetmap.org/search?q={encoded_bare}&format=jsonv2&addressdetails=1&limit=3"
                        req_bare = urllib.request.Request(url_bare, headers={"User-Agent": "RaahiGlobalTransit/1.0"})
                        with urllib.request.urlopen(req_bare, timeout=3.0) as resp2:
                            data = json.loads(resp2.read().decode())

                if not data:
                    return None

                top = data[0]
                addr = top.get("address", {})
                city = addr.get("city") or addr.get("town") or addr.get("municipality") or addr.get("state_district") or addr.get("county")
                state = addr.get("state")
                country = addr.get("country")
                place_type = top.get("type", "place")
                
                # Check for ambiguity: if top 2 results are from completely different countries/states
                is_ambiguous = False
                disambiguation_opts = []
                if len(data) >= 2:
                    c1 = (data[0].get("address", {}).get("country") or "").lower()
                    c2 = (data[1].get("address", {}).get("country") or "").lower()
                    s1 = (data[0].get("address", {}).get("state") or "").lower()
                    s2 = (data[1].get("address", {}).get("state") or "").lower()
                    if c1 and c2 and c1 != c2:
                        is_ambiguous = True
                        disambiguation_opts = [d.get("display_name", "") for d in data[:3]]

                name = top.get("name") or top.get("display_name", "").split(",")[0]
                return ResolvedPlace(
                    name=name,
                    display_name=top.get("display_name", name),
                    lat=float(top["lat"]),
                    lon=float(top["lon"]),
                    category=place_type,
                    city=city,
                    state=state,
                    country=country,
                    place_id=str(top.get("place_id", name)),
                    raw_query=query,
                    is_ambiguous=is_ambiguous,
                    disambiguation_options=disambiguation_opts
                )
        except Exception as e:
            logger.warning("Nominatim geocode failed for '%s': %s", query, e)
            return None

    def _is_ambiguous_place_name(self, name: str) -> bool:
        common_ambiguous = {"springfield", "gandhi nagar", "nehru nagar", "victoria", "central station", "main station"}
        return name.lower().strip() in common_ambiguous

geocoding_service_instance = GeocodingService()

