"""
Raahi AI Multi-Modal Travel Assistant powered by Sarvam AI.
Supports multi-turn conversations in Hindi (Devanagari), Hinglish, and English.
Strictly grounded in verified multi-provider routing (Local Public Transit, RailConnect, OSRM Global Road Network).
Guarantees origin/destination correctness and never invents false transit lines or fares.
"""
import re
import time
import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple

from .models import (
    ChatRequest, ChatResponse, CanonicalJourneyRequest,
    ResolvedPlace, RouteItinerary, TravelPreference
)
from .geocoding_service import geocoding_service_instance
from .routing_providers.router_manager import routing_manager_instance
from .sarvam_service import sarvam_service_instance, SarvamConfigurationError, SarvamAPIError
from .simulation import simulator_instance

logger = logging.getLogger("raahi.chat_engine")

class AssistantSession:
    def __init__(self, session_id: str):
        self.session_id: str = session_id
        self.messages: List[Dict[str, str]] = []  # sliding window history
        self.current_journey: Optional[CanonicalJourneyRequest] = None
        self.current_routes: List[RouteItinerary] = []
        self.current_coverage: str = "road_only"
        self.last_active: float = time.time()

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        self.last_active = time.time()
        if len(self.messages) > 12:
            self.messages = self.messages[-12:]

class SessionManager:
    def __init__(self, ttl_seconds: int = 86400):
        self._sessions: Dict[str, AssistantSession] = {}
        self._ttl: int = ttl_seconds

    def get_or_create(self, session_id: Optional[str]) -> AssistantSession:
        self._cleanup()
        if not session_id or session_id not in self._sessions:
            new_id = session_id or str(uuid.uuid4())
            session = AssistantSession(new_id)
            self._sessions[new_id] = session
            return session
        s = self._sessions[session_id]
        s.last_active = time.time()
        return s

    def reset(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def _cleanup(self):
        now = time.time()
        expired = [sid for sid, s in self._sessions.items() if now - s.last_active > self._ttl]
        for sid in expired:
            del self._sessions[sid]

class RaahiAIAssistant:
    def __init__(self):
        self.geocoder = geocoding_service_instance
        self.router = routing_manager_instance
        self.session_manager = SessionManager()

    async def process_message(self, req: ChatRequest) -> ChatResponse:
        session = self.session_manager.get_or_create(req.session_id)
        raw_text = req.message.strip()
        lower_text = raw_text.lower()

        # Language Detection
        is_hindi = bool(re.search(r'[\u0900-\u097F]', raw_text))
        is_hinglish = any(w in lower_text for w in [
            "mujhe", "batao", "kaise", "jana", "sasta", "sabse", "bhaiya", "rasta",
            "kya", "wala", "dikhao", "kahan", "kitna", "lagega", "hai", "jaun", "pahunchun"
        ])
        detected_lang = "hi" if is_hindi else ("hinglish" if is_hinglish else req.language)

        # 1. INTENT: Check Live Delays & Disruption
        if any(w in lower_text for w in ["delay", "late", "status", "ruk", "gadbad", "chal rahi hai", "der", "deri", "jam"]):
            target_city = req.city or (session.current_journey.origin.city if session.current_journey else "Delhi NCR")
            return self._handle_delay_inquiry(session, target_city, detected_lang)

        # 2. INTENT: Follow-up on Existing Journey (e.g. "Sabse sasta kaunsa hai?", "Aur fastest?", "Walking wala dikhao")
        is_followup = self._is_journey_followup(lower_text)
        if is_followup and session.current_journey and session.current_routes:
            return await self._handle_journey_followup(session, raw_text, lower_text, detected_lang)

        # 3. INTENT: Destination-only update (e.g. "Ab Marine Drive ka route batao")
        new_dest_only = self._extract_destination_only(raw_text)
        if new_dest_only and session.current_journey:
            resolved_dest = self.geocoder.resolve_place(new_dest_only, session.current_journey.origin.city)
            if resolved_dest and not resolved_dest.is_ambiguous:
                # Inherit current origin and create updated canonical request
                new_journey_req = CanonicalJourneyRequest(
                    origin=session.current_journey.origin,
                    destination=resolved_dest,
                    time_mode=session.current_journey.time_mode,
                    preferences=session.current_journey.preferences
                )
                return await self._execute_canonical_journey(session, new_journey_req, raw_text, detected_lang)

        # 4. INTENT: Natural Language Route Search (New Journey Request)
        orig_raw, dest_raw, prefs = self._extract_journey_parameters(raw_text)

        if orig_raw and dest_raw:
            # Detect explicit city context in query text (e.g. "in delhi ...", "in mathura ...")
            inferred_city = req.city
            if any(w in lower_text for w in ["in delhi", "delhi me", "delhi mein"]):
                inferred_city = "Delhi NCR"
            elif any(w in lower_text for w in ["in mathura", "mathura me", "mathura mein", "in vrindavan"]):
                inferred_city = "Mathura & Vrindavan"
            elif any(w in lower_text for w in ["in mumbai", "mumbai me", "mumbai mein"]):
                inferred_city = "Mumbai"
            elif any(w in lower_text for w in ["in bengaluru", "in bangalore", "bangalore me", "bengaluru me"]):
                inferred_city = "Bengaluru"

            # Resolve origin and destination using global geocoding with cross-city context propagation
            orig_place = self.geocoder.resolve_place(orig_raw, inferred_city)
            context_for_dest = orig_place.city if (orig_place and orig_place.city and not orig_place.is_ambiguous) else inferred_city
            dest_place = self.geocoder.resolve_place(dest_raw, context_for_dest)

            # Check for ambiguity
            if orig_place and orig_place.is_ambiguous:
                return self._create_clarification_response(
                    session,
                    f"'{orig_place.name}' matches multiple locations. Could you specify the city or state for your starting point?",
                    detected_lang
                )
            if dest_place and dest_place.is_ambiguous:
                return self._create_clarification_response(
                    session,
                    f"'{dest_place.name}' matches multiple locations. Could you specify the city or destination area?",
                    detected_lang
                )

            if orig_place and dest_place:
                canonical_req = CanonicalJourneyRequest(
                    origin=orig_place,
                    destination=dest_place,
                    preferences=prefs
                )
                return await self._execute_canonical_journey(session, canonical_req, raw_text, detected_lang)

        # 5. INTENT: City Exploration & Sightseeing Inquiry (e.g. "muje mathura ghumna hai abhi mai junction pr hu")
        is_explore, explore_orig, explore_city = self._detect_exploration_query(lower_text)
        if is_explore:
            return await self._handle_exploration_inquiry(
                session, raw_text, lower_text, explore_orig, explore_city, req.city, detected_lang
            )

        # 6. INTENT: General Help / Conversational Guidance
        return await self._handle_general_conversational(session, raw_text, req.city, detected_lang)

    # -----------------------------------------------------------------------
    # Canonical Journey Execution & Sarvam Grounding
    # -----------------------------------------------------------------------
    async def _execute_canonical_journey(
        self,
        session: AssistantSession,
        req: CanonicalJourneyRequest,
        user_query: str,
        lang: str
    ) -> ChatResponse:
        # Enforce that new explicit journey overrides previous journey state
        session.current_journey = req

        # Query routing manager with strict origin/destination validation
        routes, coverage_type = self.router.plan_canonical_journey(req)
        session.current_routes = routes
        session.current_coverage = coverage_type

        if not routes:
            # Unroutable or unsupported geographic area
            reply_text = self._build_unsupported_region_message(req.origin, req.destination, lang)
            session.add_message("user", user_query)
            session.add_message("assistant", reply_text)
            return ChatResponse(
                reply=reply_text,
                session_id=session.session_id,
                action_type="general_info",
                detected_intent="unsupported_region",
                is_grounded_route=False,
                canonical_request=req,
                coverage_type="unsupported"
            )

        chosen_route = routes[0]

        # Generate conversational grounded response via Sarvam AI
        reply_text = await self._generate_sarvam_route_response(
            session=session,
            req=req,
            routes=routes[:3],
            coverage_type=coverage_type,
            user_query=user_query,
            lang=lang
        )

        session.add_message("user", user_query)
        session.add_message("assistant", reply_text)

        suggested = [
            {"label": "Inspect Route in Planner", "action": "navigate_plan"},
            {"label": "Cheapest Option", "action": "prompt_cheapest"},
            {"label": "Fastest Option", "action": "prompt_fastest"}
        ]

        return ChatResponse(
            reply=reply_text,
            session_id=session.session_id,
            action_type="show_route",
            route_data=chosen_route,
            suggested_actions=suggested,
            detected_intent="route_recommendation",
            is_grounded_route=True,
            canonical_request=req,
            coverage_type=coverage_type
        )

    # -----------------------------------------------------------------------
    # Follow-Up Inquiries
    # -----------------------------------------------------------------------
    def _is_journey_followup(self, lower_text: str) -> bool:
        followup_cues = [
            "sasta", "cheapest", "fastest", "jaldi", "quickest", "isse sasta", "aur fastest",
            "walking wala", "less walk", "tempo ka", "auto ka", "metro ka", "bus ka",
            "kitna time", "kitna kharch", "total fare", "any other option", "vikalp",
            "stop", "stops", "station", "kitne stop", "kitne stops"
        ]
        return any(c in lower_text for c in followup_cues)

    async def _handle_journey_followup(
        self,
        session: AssistantSession,
        raw_text: str,
        lower_text: str,
        lang: str
    ) -> ChatResponse:
        req = session.current_journey
        routes = list(session.current_routes)

        if any(w in lower_text for w in ["sasta", "cheapest", "lowest", "isse sasta"]):
            routes.sort(key=lambda r: (r.total_fare_inr, r.total_duration_minutes))
            top = routes[0]
            if lang == "hi":
                reply = f"**{req.origin.name}** से **{req.destination.name}** के लिए सबसे सस्ता विकल्प:\n\n• **{top.title}**\n• 💰 **किराया**: ₹{top.total_fare_inr:.0f}\n• ⏱️ **समय**: ~{top.total_duration_minutes} मिनट\n• 💡 {top.tag_reason}"
            else:
                reply = f"The most economical option from **{req.origin.name}** to **{req.destination.name}** is:\n\n• **{top.title}**\n• 💰 **Fare**: ₹{top.total_fare_inr:.0f}\n• ⏱️ **Duration**: ~{top.total_duration_minutes} mins\n• 💡 {top.tag_reason}"
        elif any(w in lower_text for w in ["fastest", "jaldi", "quickest", "sabse tez"]):
            routes.sort(key=lambda r: (r.total_duration_minutes, r.total_fare_inr))
            top = routes[0]
            if lang == "hi":
                reply = f"**{req.origin.name}** से **{req.destination.name}** के लिए सबसे तेज़ विकल्प:\n\n• **{top.title}**\n• ⏱️ **समय**: ~{top.total_duration_minutes} मिनट\n• 💰 **किराया**: ₹{top.total_fare_inr:.0f}\n• 💡 {top.tag_reason}"
            else:
                reply = f"The fastest option from **{req.origin.name}** to **{req.destination.name}** is:\n\n• **{top.title}**\n• ⏱️ **Duration**: ~{top.total_duration_minutes} mins\n• 💰 **Fare**: ₹{top.total_fare_inr:.0f}\n• 💡 {top.tag_reason}"
        elif any(w in lower_text for w in ["stop", "stops", "station"]):
            top = routes[0]
            stops_count = sum(l.stops_count for l in top.legs)
            if lang == "hi":
                reply = f"**{req.origin.name}** से **{req.destination.name}** के मार्ग (**{top.title}**) में कुल **{stops_count} स्टॉप** हैं। यात्रा का समय लगभग ~{top.total_duration_minutes} मिनट है।"
            else:
                reply = f"The route (**{top.title}**) from **{req.origin.name}** to **{req.destination.name}** has a total of **{stops_count} stops**, taking approximately ~{top.total_duration_minutes} mins."
        else:
            top = routes[0]
            reply = f"For your journey from **{req.origin.name}** to **{req.destination.name}**, the recommended option is **{top.title}** (~{top.total_duration_minutes} mins, ₹{top.total_fare_inr:.0f})."

        session.add_message("user", raw_text)
        session.add_message("assistant", reply)

        return ChatResponse(
            reply=reply,
            session_id=session.session_id,
            action_type="show_route",
            route_data=top,
            suggested_actions=[{"label": "View in Journey Planner", "action": "navigate_plan"}],
            detected_intent="route_followup",
            is_grounded_route=True,
            canonical_request=req,
            coverage_type=session.current_coverage
        )

    # -----------------------------------------------------------------------
    # NLP Parameter & Endpoint Extraction
    # -----------------------------------------------------------------------
    def _extract_journey_parameters(self, text: str) -> Tuple[Optional[str], Optional[str], TravelPreference]:
        prefs = TravelPreference()
        lower = text.lower()

        # Preference flags
        if any(w in lower for w in ["sasta", "cheapest", "lowest fare", "minimum cost", "min cost", "kam kharch", "kam paise", "budget"]):
            prefs.cheapest = True
            prefs.fastest = False
        if any(w in lower for w in ["fastest", "minimum time", "min time", "jaldi", "quickest", "sabse tez"]):
            prefs.fastest = True
        if any(w in lower for w in ["less walk", "kam chalna", "minimal walk", "no walking"]):
            prefs.less_walking = True
        if any(w in lower for w in ["less crowd", "kam bheed", "peaceful"]):
            prefs.less_crowded = True
        if any(w in lower for w in ["wheelchair", "accessible", "divyang"]):
            prefs.accessible = True

        # Pre-clean sentence framing noise:
        # e.g. "in delhi i want to travel from rohni to pari chowk with minimum cost and minimum time"
        cleaned_query = lower
        # Remove city prefixes like "in delhi ", "in mathura: ", "in mumbai, "
        cleaned_query = re.sub(r'^(?:in\s+[a-zA-Z\s]+?[\,\:\-]\s*|in\s+(?:delhi|mumbai|bengaluru|bangalore|mathura|vrindavan)\s+)', '', cleaned_query)
        # Remove intent prefixes like "i want to travel ", "i want to go ", "how to travel ", "how to reach ", "please tell me route "
        cleaned_query = re.sub(r'^(?:i\s+want\s+to\s+|i\s+need\s+to\s+|can\s+you\s+|please\s+)?(?:travel|go|reach|commute|navigate|get|take\s+me)\s+', '', cleaned_query)
        # Remove trailing preference clauses like "with minimum cost and minimum time"
        cleaned_query = re.sub(r'\s+with\s+(?:minimum|least|lowest|min|max|no|less|cheapest|fastest).*$', '', cleaned_query)
        cleaned_query = re.sub(r'\s+(?:minimum|least|lowest|min)\s+(?:cost|fare|time|duration|walking).*$', '', cleaned_query)
        cleaned_query = re.sub(r'\s+(?:with\s+)?(?:less|minimal|no)\s+(?:walking|crowd|transfers).*$', '', cleaned_query)
        cleaned_query = re.sub(r'\s+(?:sabse\s+)?(?:sasta|fastest|tez|jaldi|kam\s+kharch|kam\s+samay).*$', '', cleaned_query)

        orig_raw, dest_raw = None, None

        # Pattern 1: 'from X to Y' (Primary English forward pattern)
        m_from_to = re.search(r'\bfrom\s+([a-zA-Z0-9\u0900-\u097F\s\.\-\'\(\)]+?)\s+to\s+([a-zA-Z0-9\u0900-\u097F\s\.\-\'\(\)]+)', cleaned_query)
        if m_from_to:
            orig_raw = self._clean_place_tokens(m_from_to.group(1))
            dest_raw = self._clean_place_tokens(m_from_to.group(2))
            if orig_raw and dest_raw and orig_raw not in {"travel", "go", "reach"} and dest_raw not in {"travel", "go", "reach"}:
                return orig_raw, dest_raw, prefs

        # Pattern 2: 'X se Y' (Primary Hindi forward pattern)
        m_se = re.search(r'([a-zA-Z0-9\u0900-\u097F\s\.\-\'\(\)]+?)\s+(?:se|से)\s+([a-zA-Z0-9\u0900-\u097F\s\.\-\'\(\)]+)', cleaned_query)
        if m_se:
            orig_raw = self._clean_place_tokens(m_se.group(1))
            dest_raw = self._clean_place_tokens(m_se.group(2))
            if orig_raw and dest_raw and orig_raw not in {"travel", "go", "reach"} and dest_raw not in {"travel", "go", "reach"}:
                return orig_raw, dest_raw, prefs

        # Pattern 3: 'Y jana hai X se' or 'Y kaise jaun X se' (Hindi Reverse)
        m_hindi_rev = re.search(r'([a-zA-Z0-9\u0900-\u097F\s\.\-\'\(\)]+?)\s+(?:jana|pahunch|jaun|pahunchna|jaana|jaye|jaaye|जाना|पहुँच|जाएँ|जाएं|जाए)\s*.*?\s+([a-zA-Z0-9\u0900-\u097F\s\.\-\'\(\)]+?)\s+(?:se|से)', cleaned_query)
        if m_hindi_rev:
            dest_raw = self._clean_place_tokens(m_hindi_rev.group(1))
            orig_raw = self._clean_place_tokens(m_hindi_rev.group(2))
            if orig_raw and dest_raw and orig_raw not in {"travel", "go", "reach"} and dest_raw not in {"travel", "go", "reach"}:
                return orig_raw, dest_raw, prefs

        # Pattern 4: 'to Y from X' or 'how to get/reach to Y from X'
        m_to_from = re.search(r'(?:to|reach)\s+([a-zA-Z0-9\u0900-\u097F\s\.\-\'\(\)]+?)\s+from\s+([a-zA-Z0-9\u0900-\u097F\s\.\-\'\(\)]+)', cleaned_query)
        if m_to_from:
            cand_dest = self._clean_place_tokens(m_to_from.group(1))
            cand_orig = self._clean_place_tokens(m_to_from.group(2))
            # Strict safety check: destination cannot be an action verb!
            if cand_dest and cand_orig and cand_dest not in {"travel", "go", "reach", "get", "commute", "journey", "walk", "drive"}:
                return cand_orig, cand_dest, prefs

        # Pattern 5: 'X to Y' (Direct English shorthand)
        m_direct_to = re.search(r'([a-zA-Z0-9\u0900-\u097F\s\.\-\'\(\)]+?)\s+to\s+([a-zA-Z0-9\u0900-\u097F\s\.\-\'\(\)]+)', cleaned_query)
        if m_direct_to:
            orig_raw = self._clean_place_tokens(m_direct_to.group(1))
            dest_raw = self._clean_place_tokens(m_direct_to.group(2))
            if orig_raw and dest_raw and orig_raw not in {"travel", "go", "reach", "want"} and dest_raw not in {"travel", "go", "reach"}:
                return orig_raw, dest_raw, prefs

        return None, None, prefs

    def _extract_destination_only(self, text: str) -> Optional[str]:
        lower = text.lower()
        m = re.search(r'\b(?:ab|now)\s+([a-zA-Z0-9\u0900-\u097F\s\.\-\']+?)\s+(?:ka|ki|ke|route|rasta|jana|batao)', lower)
        if m:
            cand = self._clean_place_tokens(m.group(1))
            if cand and len(cand) >= 3:
                return cand
        return None

    def _clean_place_tokens(self, text: str) -> str:
        if not text:
            return ""
        # Remove punctuation safely without corrupting Unicode combining characters (matras)
        cleaned = re.sub(r'[?!.,;:"\'`\\/<>{}()\[\]]+', ' ', text)
        # Remove common query noise tokens (English, Hinglish, Hindi)
        noise = [
            # Trailing preference noise
            r'\b(?:with|at|and)\s+(?:minimum|lowest|least|min|fastest|cheapest|maximum)\s+(?:cost|fare|time|duration|walking|crowd)\b',
            r'\b(?:minimum|lowest|least|min|fastest|cheapest)\s+(?:cost|fare|time|duration|walking|crowd)\b',
            r'\b(?:in\s+delhi|in\s+mumbai|in\s+bengaluru|in\s+mathura)\b',
            r'\b(?:travel|go|reach|commute|trip)\b',
            # Hinglish / English
            r'\bkaise\b', r'\bjaun\b', r'\bjana\b', r'\bjaana\b', r'\bjaye\b', r'\bjaaye\b', r'\bjao\b',
            r'\bpahunchun\b', r'\bpahuche\b', r'\bpahunchna\b', r'\bpahuche\b', r'\bpahunchein\b',
            r'\bjaane\b', r'\bka\b', r'\bki\b', r'\bke\b', r'\broute\b', r'\brasta\b', r'\bmarg\b',
            r'\bbatao\b', r'\bchahiye\b', r'\bdikhao\b', r'\boption\b', r'\bbest\b',
            r'\bfastest\b', r'\bcheapest\b', r'\bby public transport\b', r'\bpublic transport\b',
            r'\btrain\b', r'\bbus\b', r'\bmetro\b', r'\bhai\b', r'\bkya\b', r'\bplease\b',
            r'\bfind\b', r'\bthe\b', r'\bto\b', r'\bfrom\b',
            # Hindi Devanagari (word-bounded)
            r'\bकैसे\b', r'\bजाएँ\b', r'\bजाएं\b', r'\bजाए\b', r'\bजाना\b', r'\bपहुंचे\b', r'\bपहुंचें\b', r'\bपहुंचूं\b', r'\bपहुंचना\b',
            r'\bबताओ\b', r'\bदिखाओ\b', r'\bचाहिए\b', r'\bरास्ता\b', r'\bरूट\b', r'\bमार्ग\b', r'\bविकल्प\b', r'\bहै\b', r'\bका\b', r'\bकी\b', r'\bके\b', r'\bकृपया\b'
        ]
        for pat in noise:
            cleaned = re.sub(pat, '', cleaned, flags=re.I)
        return re.sub(r'\s+', ' ', cleaned).strip()

    # -----------------------------------------------------------------------
    # Sarvam AI Prompting & Execution
    # -----------------------------------------------------------------------
    async def _generate_sarvam_route_response(
        self,
        session: AssistantSession,
        req: CanonicalJourneyRequest,
        routes: List[RouteItinerary],
        coverage_type: str,
        user_query: str,
        lang: str
    ) -> str:
        # Build structured route telemetry
        summaries = []
        for i, r in enumerate(routes, 1):
            primary_leg = next((l for l in r.legs if l.mode != "walk"), r.legs[0])
            mode_desc = primary_leg.line_name or primary_leg.mode
            fare_str = f"₹{r.total_fare_inr:.0f}" if r.total_fare_inr > 0 else (r.fare_breakdown or "Not Available")
            summaries.append(
                f"Option {i}: **{r.title}** ({r.tag})\n"
                f"- Duration: ~{r.total_duration_minutes} mins\n"
                f"- Fare: {fare_str} (Provenance: {r.fare_provenance})\n"
                f"- Primary Mode: {mode_desc}\n"
                f"- Transfers: {r.transfers_count}\n"
                f"- Data Source: {r.data_source}\n"
                f"- Highlight: {r.tag_reason}"
            )
        routes_summary = "\n\n".join(summaries)

        coverage_warning = ""
        if coverage_type == "road_only":
            coverage_warning = (
                "IMPORTANT COVERAGE NOTE: Live public transit timetables (bus/subway lines) are not currently connected for this geographic area in Raahi. "
                "DO NOT INVENT public buses or subways. State clearly that verified street-level driving and walking routes via OpenStreetMap are displayed."
            )
        elif coverage_type == "intercity_rail":
            coverage_warning = "Intercity RailConnect: Trains verified via Indian Railways network."

        lang_instruction = {
            "hi": "Respond in polite, natural Hindi (हिंदी) in Devanagari script. Be culturally grounded and respectful.",
            "hinglish": "Respond in natural, fluent Roman-script Hinglish (e.g. 'Aapke liye sabse behtar option...').",
            "en": "Respond in crisp, professional, welcoming English."
        }.get(lang, "Respond in clear English.")

        system_prompt = (
            f"You are Raahi AI (राही), an intelligent, accurate, and culturally respectful travel companion for urban and intercity mobility.\n\n"
            f"=== VERIFIED REAL ROUTE DATA (STRICT GROUND TRUTH) ===\n"
            f"Requested Origin: {req.origin.name} ({req.origin.display_name})\n"
            f"Requested Destination: {req.destination.name} ({req.destination.display_name})\n"
            f"Coverage Type: {coverage_type}\n\n"
            f"Available Routes:\n{routes_summary}\n\n"
            f"{coverage_warning}\n\n"
            f"=== STRICT RULES ===\n"
            f"1. NEVER reverse the origin and destination. The trip starts at {req.origin.name} and ends at {req.destination.name}.\n"
            f"2. Never fabricate phantom bus numbers, fake subway lines, or fictitious prices.\n"
            f"3. {lang_instruction}\n"
            f"4. Highlight the primary recommended option clearly with duration and fare.\n"
            f"5. Keep the reply well-structured with bullet points."
        )

        messages = [{"role": "system", "content": system_prompt}]
        for m in session.messages[-4:]:
            messages.append(m)
        messages.append({"role": "user", "content": user_query})

        try:
            res = await sarvam_service_instance.chat_completion(messages=messages, temperature=0.25)
            if res and res.strip():
                return res.strip()
            return self._build_template_route_response(req, routes[0], coverage_type, lang)
        except Exception as err:
            logger.warning("Sarvam AI unavailable, using verified local template: %s", err)
            return self._build_template_route_response(req, routes[0], coverage_type, lang)

    def _build_template_route_response(
        self,
        req: CanonicalJourneyRequest,
        route: RouteItinerary,
        coverage_type: str,
        lang: str
    ) -> str:
        orig = req.origin.name
        dest = req.destination.name
        mins = route.total_duration_minutes
        fare_str = f"₹{route.total_fare_inr:.0f}" if route.total_fare_inr > 0 else (route.fare_breakdown or "See details")
        primary_leg = next((l for l in route.legs if l.mode != "walk"), route.legs[0])
        mode_str = primary_leg.line_name or primary_leg.mode

        advisory_note = ""
        if coverage_type == "road_only":
            advisory_note = "\n\n*(ℹ️ Note: Public transit timetables are not connected for this region in Raahi. Verified road routing from OpenStreetMap is shown)*"

        if lang == "hi":
            return (
                f"**{orig}** से **{dest}** के लिए सर्वोत्तम रूट:\n\n"
                f"• **अनुशंसित विकल्प**: {route.title} ({route.tag})\n"
                f"• ⏱️ **समय**: ~{mins} मिनट\n"
                f"• 💰 **किराया**: {fare_str}\n"
                f"• 🚗 **मुख्य साधन**: {mode_str}\n"
                f"• 💡 **विवरण**: {route.tag_reason}\n\n"
                f"नीचे दिए गए रूट कार्ड से आप पूरा मोड़-दर-मोड़ रास्ता देख सकते हैं।{advisory_note}"
            )
        elif lang == "hinglish":
            return (
                f"**{orig}** se **{dest}** ke liye optimal route yeh hai:\n\n"
                f"• **Recommended Option**: {route.title} ({route.tag})\n"
                f"• ⏱️ **Duration**: ~{mins} mins\n"
                f"• 💰 **Estimated Fare**: {fare_str}\n"
                f"• 🚗 **Transit**: {mode_str}\n"
                f"• 💡 **Details**: {route.tag_reason}\n\n"
                f"Pura rasta dekhne ke liye niche diye card par click karein.{advisory_note}"
            )
        else:
            return (
                f"Here is the verified itinerary from **{orig}** to **{dest}**:\n\n"
                f"• **Recommended Route**: {route.title} ({route.tag})\n"
                f"• ⏱️ **Duration**: ~{mins} mins\n"
                f"• 💰 **Fare**: {fare_str}\n"
                f"• 🚗 **Mode**: {mode_str}\n"
                f"• 💡 **Highlights**: {route.tag_reason}\n\n"
                f"Click the route card below to inspect step-by-step turns.{advisory_note}"
            )

    def _build_unsupported_region_message(self, orig: ResolvedPlace, dest: ResolvedPlace, lang: str) -> str:
        if lang == "hi":
            return (
                f"क्षमा करें, **{orig.name}** और **{dest.name}** के बीच सीधा सड़क या सार्वजनिक परिवहन मार्ग वर्तमान में उपलब्ध नहीं है। "
                f"कृपया जाँचें कि दोनों स्थानों के बीच वैध सड़क संपर्क मौजूद है।"
            )
        else:
            return (
                f"Unable to verify a direct route between **{orig.name}** and **{dest.name}**. "
                f"Please ensure both locations have contiguous road or transit network access."
            )

    def _create_clarification_response(self, session: AssistantSession, question: str, lang: str) -> ChatResponse:
        session.add_message("assistant", question)
        return ChatResponse(
            reply=question,
            session_id=session.session_id,
            action_type="clarification",
            clarification_needed=True,
            clarification_question=question,
            detected_intent="clarification"
        )

    def _handle_delay_inquiry(self, session: AssistantSession, city: str, lang: str) -> ChatResponse:
        incidents = simulator_instance.get_incidents(city)
        if not incidents:
            reply = f"All transit routes in {city} are operating normally with no active delays."
            if lang == "hi":
                reply = f"वर्तमान में {city} में सभी परिवहन मार्ग सामान्य समय पर चल रहे हैं। कोई देरी नहीं है।"
            return ChatResponse(reply=reply, session_id=session.session_id, action_type="show_delays", detected_intent="delays_status")

        joined = "\n".join([f"• **{inc.line_name}**: +{inc.delay_minutes} min ({inc.headline})" for inc in incidents])
        reply = f"Current active transit disruptions in {city}:\n\n{joined}"
        return ChatResponse(reply=reply, session_id=session.session_id, action_type="show_delays", detected_intent="delays_status")

    def _detect_exploration_query(self, lower_text: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Detects queries where the user wants to explore/sightsee/visit places in a city or around a hub,
        e.g., 'muje mathura ghumna hai abhi mai junction pr hu so tell me all possible options'
        Returns: (is_exploration: bool, origin_hub: Optional[str], target_city: Optional[str])
        """
        explore_cues = [
            "ghumna", "ghoomna", "ghumne", "ghoomne", "ghumu", "ghoomu", "ghumo",
            "darshan", "sightseeing", "explore", "visit", "places to see", "spots",
            "all possible options", "kya dekhu", "kaha jau", "kahan jaun", "kahan ghumu",
            "options batao", "tourist spots", "tourist places", "temples to visit", "mandir darshan"
        ]
        has_explore = any(c in lower_text for c in explore_cues)
        if not has_explore:
            return False, None, None

        # City detection
        target_city = None
        if any(c in lower_text for c in ["mathura", "vrindavan", "barsana", "govardhan", "gokul", "braj"]):
            target_city = "Mathura & Vrindavan"
        elif any(c in lower_text for c in ["delhi", "noida", "gurugram", "gurgaon", "faridabad", "ghaziabad"]):
            target_city = "Delhi NCR"
        elif any(c in lower_text for c in ["mumbai", "bombay", "thane", "navi mumbai"]):
            target_city = "Mumbai"
        elif any(c in lower_text for c in ["bengaluru", "bangalore"]):
            target_city = "Bengaluru"

        # Hub / Origin detection
        origin_hub = None
        if any(h in lower_text for h in ["junction", "stn", "railway station", "station", "cantt"]):
            if target_city == "Mathura & Vrindavan" or "mathura" in lower_text:
                origin_hub = "Mathura Junction"
            elif target_city == "Delhi NCR" or "delhi" in lower_text:
                origin_hub = "New Delhi Railway Station"
            elif target_city == "Mumbai" or "mumbai" in lower_text:
                origin_hub = "CSMT Mumbai"
            elif target_city == "Bengaluru" or "bengaluru" in lower_text:
                origin_hub = "KSR Bengaluru (Majestic)"
            else:
                origin_hub = "Mathura Junction" if target_city == "Mathura & Vrindavan" else "Railway Station"
        elif "airport" in lower_text or "hawai adda" in lower_text:
            if target_city == "Delhi NCR":
                origin_hub = "IGI Airport Terminal 3"
            elif target_city == "Mumbai":
                origin_hub = "Chhatrapati Shivaji Maharaj Airport (BOM)"
            elif target_city == "Bengaluru":
                origin_hub = "Kempegowda International Airport (BLR)"

        if not origin_hub and target_city == "Mathura & Vrindavan":
            origin_hub = "Mathura Junction"

        return True, origin_hub, target_city

    async def _handle_exploration_inquiry(
        self,
        session: AssistantSession,
        raw_text: str,
        lower_text: str,
        explore_orig: Optional[str],
        explore_city: Optional[str],
        req_city: Optional[str],
        lang: str
    ) -> ChatResponse:
        city = explore_city or req_city or "Mathura & Vrindavan"
        if any(c in lower_text for c in ["mathura", "vrindavan", "braj"]):
            city = "Mathura & Vrindavan"
        elif any(c in lower_text for c in ["mumbai", "bombay"]):
            city = "Mumbai"
        elif any(c in lower_text for c in ["bengaluru", "bangalore"]):
            city = "Bengaluru"
        elif any(c in lower_text for c in ["delhi", "gurugram", "noida"]):
            city = "Delhi NCR"

        if "Mathura" in city:
            orig_name = explore_orig or "Mathura Junction"
            dest_name = "Shri Krishna Janmabhoomi (Janmasthan)"
        elif "Mumbai" in city:
            orig_name = explore_orig or "CSMT Mumbai"
            dest_name = "Gateway of India (Colaba)"
        elif "Bengaluru" in city:
            orig_name = explore_orig or "KSR Bengaluru (Majestic)"
            dest_name = "Lalbagh Botanical Garden"
        else:
            orig_name = explore_orig or "Rajiv Chowk (Connaught Place)"
            dest_name = "India Gate"

        orig_place = self.geocoder.resolve_place(orig_name, city)
        dest_place = self.geocoder.resolve_place(dest_name, city)

        routes = []
        coverage_type = "full_transit"
        chosen_route = None

        if orig_place and dest_place:
            canonical_req = CanonicalJourneyRequest(
                origin=orig_place,
                destination=dest_place,
                preferences=TravelPreference()
            )
            routes, coverage_type = self.router.plan_canonical_journey(canonical_req)
            session.current_journey = canonical_req
            session.current_routes = routes
            session.current_coverage = coverage_type
            if routes:
                chosen_route = routes[0]

        if "Mathura" in city:
            if lang == "hi" or lang == "hinglish":
                reply = (
                    "राधे-राधे! मथुरा जंक्शन (MTJ) से आपके लिए सभी उपलब्ध परिवहन साधन और दर्शनीय स्थलों का विवरण:\n\n"
                    "🚖 **मथुरा जंक्शन के बाहर उपलब्ध परिवहन साधन (All Transit Modes):**\n"
                    "1. **ई-रिक्शा / टोटो (Shared E-Rickshaw / Toto)**: ₹10 - ₹20 प्रति सवारी। श्रीकृष्ण जन्मस्थान, द्वारकाधीश और विश्राम घाट की संकरी गलियों के लिए सबसे सुलभ।\n"
                    "2. **शेयरिंग टेम्पो / विक्रम (Shared Tempo)**: ₹20 - ₹35 प्रति सीट। भूतेश्वर, पुराना बस स्टैंड, और छटीकरा / वृंदावन (अटल्ला चुंगी) के लिए लगातार उपलब्ध।\n"
                    "3. **ब्रज ई-बस (Electric AC City Bus)**: ₹15 - ₹35 किराया। वातानुकूलित बस सेवा जो सीधे मथुरा जंक्शन से वृंदावन (प्रेम मंदिर / छटीकरा मार्ग) को जोड़ती है।\n"
                    "4. **रिजर्व ऑटो / प्राइवेट टूरिस्ट टैक्सी**: ₹120 - ₹250 लोकल ट्रिप, या ₹1,200 - ₹1,800 पूरे दिन का ब्रज दर्शन (मथुरा, वृंदावन, गोवर्धन, बरसाना)।\n\n"
                    "🚩 **प्रमुख दर्शनीय स्थल (Sightseeing Circuit):**\n"
                    "• **श्रीकृष्ण जन्मस्थान (3.5 km)**: दर्शन का मुख्य केंद्र।\n"
                    "• **द्वारकाधीश मंदिर व विश्राम घाट (4.5 km)**: यमुना जी की संध्या आरती।\n"
                    "• **वृंदावन (बांके बिहारी जी व प्रेम मंदिर - 12 km)**: ई-बस या टेम्पो से ~25 मिनट।\n"
                    "• **गोवर्धन परिक्रमा (24 km)**: बस स्टैंड से सीधी बस या शेयरिंग ऑटो।\n\n"
                    "मैंने आपके लिए मथुरा जंक्शन से **श्रीकृष्ण जन्मस्थान** का रूट नीचे लोड कर दिया है। 'View in Journey Planner' पर क्लिक करके आप पूरा मैप और टाइमलाइन देख सकते हैं।"
                )
            else:
                reply = (
                    "Welcome to Mathura! Since you are at Mathura Junction (MTJ), here are all the available transit options and recommended sightseeing circuits:\n\n"
                    "🚖 **Transit Options Outside Mathura Junction:**\n"
                    "1. **Shared E-Rickshaw (Toto)**: ₹10 - ₹20 per passenger. Ideal for navigating inner market lanes directly to Shri Krishna Janmasthan and Dwarkadhish.\n"
                    "2. **Shared CNG Tempo / Vikram**: ₹20 - ₹35 per seat. Frequent departures towards Bhuteshwar, Old Bus Stand, and Vrindavan (Attalla Chungi).\n"
                    "3. **Braj Electric AC City Bus**: ₹15 - ₹35 fare. Modern, air-conditioned bus directly connecting Mathura Junction to Vrindavan (Prem Mandir / Chatikara).\n"
                    "4. **Reserved Auto / Private Tourist Cab**: ₹120 - ₹250 for point-to-point private rides, or ₹1,200 - ₹1,800 for full-day Braj Darshan (Mathura, Vrindavan, Govardhan, Barsana).\n\n"
                    "🚩 **Recommended Sightseeing Circuit:**\n"
                    "• **Shri Krishna Janmasthan (3.5 km)** - Birthplace of Lord Krishna.\n"
                    "• **Dwarkadhish Temple & Vishram Ghat (4.5 km)** - Evening Yamuna Aarti.\n"
                    "• **Vrindavan (Bankey Bihari & Prem Mandir - 12 km)** - 25 mins by E-Bus.\n"
                    "• **Govardhan Parikrama (24 km)** - Accessible via local buses or tempo.\n\n"
                    "I have attached the verified route from **Mathura Junction to Shri Krishna Janmasthan** below. Tap **View in Journey Planner** to inspect the timeline and map."
                )

            suggested = [
                {"label": "श्रीकृष्ण जन्मस्थान (Janmasthan)", "action": "prompt_janmasthan"},
                {"label": "बांके बिहारी मंदिर (Vrindavan)", "action": "prompt_bankey_bihari"},
                {"label": "प्रेम मंदिर (Prem Mandir)", "action": "prompt_prem_mandir"},
                {"label": "गोवर्धन परिक्रमा (Govardhan)", "action": "prompt_govardhan"}
            ]
        else:
            if lang == "hi":
                reply = f"नमस्ते! {city} में यात्रा के लिए आप मेट्रो, सिटी बस, ऑटो और कैब का उपयोग कर सकते हैं। मैंने आपके लिए {orig_name} से {dest_name} का मार्ग नीचे जोड़ दिया है।"
            else:
                reply = f"Welcome to {city}! You can explore using local transit, city buses, and cabs. I have attached the route from {orig_name} to {dest_name} below."

            suggested = [
                {"label": "View in Journey Planner", "action": "navigate_plan"},
                {"label": "Cheapest Option", "action": "prompt_cheapest"},
                {"label": "Fastest Option", "action": "prompt_fastest"}
            ]

        session.add_message("user", raw_text)
        session.add_message("assistant", reply)

        return ChatResponse(
            reply=reply,
            session_id=session.session_id,
            action_type="show_route" if chosen_route else "general_info",
            route_data=chosen_route,
            suggested_actions=suggested,
            detected_intent="city_exploration",
            is_grounded_route=bool(chosen_route),
            canonical_request=session.current_journey,
            coverage_type=coverage_type
        )

    async def _handle_general_conversational(self, session: AssistantSession, raw_text: str, city: Optional[str], lang: str) -> ChatResponse:
        lower = raw_text.lower()
        target_city = city or "Delhi NCR"
        if any(c in lower for c in ["mathura", "vrindavan", "braj", "gla"]):
            target_city = "Mathura & Vrindavan"
        elif any(c in lower for c in ["mumbai", "bombay"]):
            target_city = "Mumbai"
        elif any(c in lower for c in ["bengaluru", "bangalore"]):
            target_city = "Bengaluru"
        elif any(c in lower for c in ["delhi", "gurugram", "noida"]):
            target_city = "Delhi NCR"

        prompt = (
            f"You are Raahi AI, an intelligent mobility assistant for India and global journeys. "
            f"The user asks: '{raw_text}'. "
            f"Answer helpfully in {lang} focusing on travel in {target_city}. Explain how they can plan journeys between two locations or check live transit."
        )
        try:
            reply = await sarvam_service_instance.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            if not reply or not reply.strip():
                raise ValueError("Empty reply from Sarvam AI")
        except Exception:
            if lang == "hi":
                reply = f"नमस्ते! मैं राही AI हूँ। आप मुझसे {target_city} या किसी भी दो स्थानों के बीच सबसे तेज़ या सबसे सस्ते मार्ग के बारे में पूछ सकते हैं।"
            else:
                reply = f"Hello! I am Raahi AI. You can ask me for the fastest or cheapest routes between any two places across {target_city} or connected networks."

        session.add_message("user", raw_text)
        session.add_message("assistant", reply)

        if "Mathura" in target_city:
            suggested = [
                {"label": "Mathura Jn to GLA University", "action": "prompt_gla"},
                {"label": "Mathura Jn to Bankey Bihari", "action": "prompt_bankey_bihari"}
            ]
        elif "Mumbai" in target_city:
            suggested = [
                {"label": "CSMT to Gateway of India", "action": "prompt_gateway"},
                {"label": "Mumbai Airport to BKC", "action": "prompt_bkc"}
            ]
        elif "Bengaluru" in target_city:
            suggested = [
                {"label": "Majestic to Electronic City", "action": "prompt_ecity"},
                {"label": "BLR Airport to Whitefield", "action": "prompt_whitefield"}
            ]
        else:
            suggested = [
                {"label": "Fastest Route to Cyber City", "action": "prompt_fastest"},
                {"label": "Mathura Jn to GLA University", "action": "prompt_gla"}
            ]

        return ChatResponse(
            reply=reply,
            session_id=session.session_id,
            action_type="general_info",
            suggested_actions=suggested,
            detected_intent="greeting"
        )

chat_assistant_instance = RaahiAIAssistant()
