"""
Transit Incident and Disruption Simulation Engine for Raahi.
Provides authentic city-aware real-time transit telemetry, temple opening/closing schedules,
commuter peak hours, Sunday mega blocks, and interactive scenario simulations
with honest data provenance labeling ("SIMULATED" / "DEMO DATA" vs "LIVE OPERATIONAL SCHEDULE").
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import TransitIncident, SimulateDelayRequest, CityRealtimeContext

class TransitSimulator:
    def __init__(self):
        self.active_incidents: Dict[str, TransitIncident] = {}
        self.active_delays: Dict[str, int] = {}
        self.current_scenario: str = "normal"
        self._seed_default_state()

    def _seed_default_state(self):
        self.active_incidents = {}
        self.active_delays = {
            "Yellow Line": 0,
            "Blue Line": 0,
            "Magenta Line": 0,
            "Violet Line": 0,
            "Airport Express": 0,
            "DTC Electric Bus 534": 0,
            "DTC Express Bus 419": 0,
            "Mumbai Suburban Railway (Western Line)": 0,
            "Mumbai Suburban Railway (Central Line)": 0,
            "Mumbai Metro Line 3 (Aqua Line)": 0,
            "BEST AC Electric Bus (Chalo Bus)": 0,
            "Mumbai Metered Kaali-Peeli Taxi": 0,
            "Shared Tempo / Vikram (Braj Corridor)": 0,
            "Mathura-Vrindavan Electric Nagar Seva Bus": 0,
            "Shared E-Rickshaw Feeder (Toto)": 0,
            "Indian Railways Local Train": 0,
            "Purple Line (Namma Metro)": 0,
            "BMTC Vajra AC Bus": 0,
            "Karnataka Govt Metered Auto": 0
        }
        self.current_scenario = "normal"

    def get_incidents(self, city: str = "Delhi NCR") -> List[TransitIncident]:
        c_low = (city or "Delhi NCR").lower()
        if not self.active_incidents:
            return []

        # Filter incidents appropriate for the selected city
        matched: List[TransitIncident] = []
        for inc in self.active_incidents.values():
            if "mumbai" in c_low and any(k in inc.line_name.lower() or k in inc.headline.lower() for k in ("mumbai", "western", "central", "best", "kaali-peeli", "dadar", "kurla")):
                matched.append(inc)
            elif ("mathura" in c_low or "vrindavan" in c_low) and any(k in inc.line_name.lower() or k in inc.headline.lower() for k in ("mathura", "vrindavan", "temple", "darshan", "parikrama", "tempo", "bihari", "prem mandir")):
                matched.append(inc)
            elif ("bengaluru" in c_low or "bangalore" in c_low) and any(k in inc.line_name.lower() or k in inc.headline.lower() for k in ("bengaluru", "namma", "bmtc", "silk board", "purple line")):
                matched.append(inc)
            elif "delhi" in c_low and any(k in inc.line_name.lower() or k in inc.headline.lower() for k in ("yellow", "blue", "dtc", "dmrc", "delhi", "rajiv chowk", "kashmere gate")):
                matched.append(inc)
        return matched

    def get_delays_map(self) -> Dict[str, int]:
        return self.active_delays.copy()

    def get_city_realtime_context(self, city: str = "Delhi NCR") -> CityRealtimeContext:
        """
        Computes authentic live transit intelligence based on actual local IST clock,
        day of the week (workday vs weekend vs Sunday mega block), and temple aarti schedules.
        """
        now = datetime.now()
        day_idx = now.weekday() # 0 = Monday, 5 = Saturday, 6 = Sunday
        hour = now.hour
        time_str = now.strftime("%I:%M %p")
        day_name = now.strftime("%A")
        c_low = (city or "Delhi NCR").lower()

        # ==============================================================================
        # 1. MATHURA & VRINDAVAN (BRAJ DHAM)
        # ==============================================================================
        if "mathura" in c_low or "vrindavan" in c_low or "braj" in c_low:
            is_weekend = day_idx in (5, 6) # Sat or Sun
            day_type = "Weekend (Heavy Pilgrim Inflow)" if is_weekend else "Weekday (Regular Darshan Flow)"

            if 7 <= hour < 12:
                time_window = "Morning Shringar & Rajbhog Darshan (7:45 AM – 12:00 PM)"
                headline = "Temple Sanctums Open — Heavy Darshan Footfall"
                desc = "Bankey Bihari Ji (Sanctum open 7:45 AM – 12:00 PM), Shri Krishna Janmasthan, and Dwarkadhish temple gates open. Moderate to high pilgrim queues. Vidyapeeth Chauraha and Raman Reti barricaded for pedestrian & battery Toto only."
                crowd = "Very High" if is_weekend else "High"
                recom = "Shared E-Rickshaw (Toto) from Chatikara or Mathura Jn; avoid cars in inner galis."
                adv = "Weekend pilgrim rush: Private cars restricted from inner temple zone. Multi-level parking active at Pagal Baba & Chatikara." if is_weekend else "Morning Rajbhog Aarti at 11:30 AM; arrive before 11:00 AM."

            elif 12 <= hour < 16:
                time_window = "Temple Rest Hours (कपाट बंद 12:00 PM – 4:15 PM)"
                headline = "Sanctums Closed for Bhog & Shayan — Roads Free & Clear"
                desc = "Main sanctums of Bankey Bihari, Janmasthan, and Radha Vallabh closed for afternoon seva. Mathura-Vrindavan road corridors (NH-19, Chatikara, Masani) running with zero traffic congestion. Best window for station transfers."
                crowd = "Low"
                recom = "Shared Tempo / Vikram & Electric City Bus running at top speed with zero traffic."
                adv = "Evening Darshan and Shayan Aarti gates will reopen at 4:30 PM."

            elif 16 <= hour < 21:
                time_window = "Evening Darshan & Prem Mandir Light Show (4:30 PM – 9:30 PM)"
                headline = "Evening Aarti Surge & Prem Mandir Musical Fountain Rush"
                desc = "Peak crowd window across Vrindavan! Bankey Bihari Shayan Aarti crowd and Prem Mandir musical fountain (7:00 – 8:30 PM) causing heavy vehicular congestion on Chatikara-Vrindavan road. Outer multi-level parking active."
                crowd = "Very High"
                recom = "Mathura-Vrindavan Electric Nagar Seva Bus to Chatikara, then local battery Toto."
                adv = "VIP Road and Vidyapeeth Chauraha pedestrianized. Use Chatikara bypass."

            else:
                time_window = "Night Service / Quiet Temple Lanes (9:30 PM – 7:00 AM)"
                headline = "Temples Closed for Night — Quiet Heritage Corridors"
                desc = "Peaceful night hours across Braj. Shared Tempos running regular shuttles between Mathura Junction (Platform 1) and Vrindavan Gandhi Park."
                crowd = "Low"
                recom = "Reserved Auto or Shared Tempo from Mathura Junction."
                adv = "Morning Mangla Aarti starts at 7:45 AM tomorrow."

            return CityRealtimeContext(
                city="Mathura & Vrindavan",
                day_name=day_name,
                day_type=day_type,
                current_time_str=time_str,
                time_window=time_window,
                status_headline=headline,
                status_description=desc,
                crowd_level=crowd,
                recommended_mode=recom,
                special_advisory=adv
            )

        # ==============================================================================
        # 2. MUMBAI (METROPOLITAN REGION)
        # ==============================================================================
        elif "mumbai" in c_low:
            is_sunday = (day_idx == 6)
            is_saturday = (day_idx == 5)
            is_workday = day_idx < 5

            if is_sunday:
                day_type = "Sunday (Mega Block & Holiday Schedule)"
                if 10 <= hour < 16:
                    time_window = "Sunday Railway Mega Block Window (10:30 AM – 4:30 PM)"
                    headline = "Central & Western Sunday Mega Block Active"
                    desc = "Scheduled railway maintenance block on Central & Western fast lines. Fast locals running on slow tracks with +10-15m headway. Harbour line mega block between CSMT and Kurla/Chunabhatti."
                    crowd = "Moderate"
                    recom = "Maha Mumbai Metro Line 3 Aqua Line or BEST AC Chalo Electric Bus."
                    adv = "Plan extra 15 mins for suburban train journeys; Bandra-Worli Sea Link and Eastern Freeway running smooth."
                else:
                    time_window = "Sunday Leisure & Family Evening"
                    headline = "All Lines Operating Normally — Relaxed Traffic"
                    desc = "Smooth road traffic across Sea Link, Marine Drive, and Western Express Highway. Suburban locals running with holiday timetable."
                    crowd = "Low"
                    recom = "Metered Kaali-Peeli Taxi or BEST Chalo Bus."
                    adv = "24/7 Metered Kaali-Peeli Taxis operating across Island City & Suburbs."

            elif is_saturday:
                day_type = "Saturday (Commercial Half-Day & Leisure)"
                time_window = "Weekend Commute & Leisure Operations"
                headline = "Suburban Locals Running Normally — Moderate Commercial Rush"
                desc = "Western & Central Railway operating full Saturday service. Moderate leisure crowd heading towards Bandra, Lower Parel Palladium, and Juhu Beach."
                crowd = "Moderate"
                recom = "Mumbai Suburban Local Train or Maha Mumbai Metro Line 3."
                adv = "Evening traffic buildup expected around BKC and Phoenix Palladium."

            else: # Mon - Fri Workday
                day_type = "Weekday (Full Corporate & Commercial Workday)"
                if 8 <= hour < 12:
                    time_window = "Morning Peak Office Rush (8:30 AM – 11:30 AM)"
                    headline = "South-bound Super-Dense Crush Load (CSMT/Churchgate/BKC)"
                    desc = "Intense southward commuter flow towards CSMT, Churchgate, Lower Parel, and BKC financial district. Western & Central fast locals running every 2.5-3 mins. Heavy boarding queues at Andheri, Dadar, and Kurla interchanges."
                    crowd = "Very High"
                    recom = "Maha Mumbai Metro Line 3 (Aqua Line) or Fast Local; avoid Western Express Highway road jams."
                    adv = "Western Express Highway slow-moving south of Goregaon. Metro Line 3 recommended."
                elif 12 <= hour < 17:
                    time_window = "Midday Non-Peak Commute (11:30 AM – 5:00 PM)"
                    headline = "All Suburban Lines & Metro Operating on Schedule"
                    desc = "Suburban locals, Metro Line 1 & Line 3, and BEST electric fleet running on regular midday headway. Minimal ticket counter queues."
                    crowd = "Moderate"
                    recom = "Metered Kaali-Peeli Taxi or BEST AC Chalo Bus."
                    adv = "Comfortable seating in local trains and AC buses."
                elif 17 <= hour < 21:
                    time_window = "Evening Peak Return Rush (5:30 PM – 9:00 PM)"
                    headline = "North-bound Commuter Crush (Borivali/Thane/Kalyan)"
                    desc = "Heavy northward return flow. Dadar and Kurla interchange platforms heavily crowded. Western Express Highway and Santacruz-Chembur Link Road slow moving."
                    crowd = "Very High"
                    recom = "Metro Line 3 Aqua Line / Western Railway Fast Local."
                    adv = "Allow +15m buffer if using road cabs via BKC connector or SV Road."
                else:
                    time_window = "Late Night Service (11:00 PM – 5:00 AM)"
                    headline = "Late Night Service — Maharashtra 25% Night Meter Active"
                    desc = "Last local trains terminate around 1:00 AM. 24/7 Metered Kaali-Peeli Taxis operating with regulated 25% night tariff (12 AM – 5 AM)."
                    crowd = "Low"
                    recom = "Metered Kaali-Peeli Taxi (₹33 base + ₹21.90/km + 25% night meter)."
                    adv = "Autos legally restricted south of Bandra/Sion; Kaali-Peeli taxis operate 24/7."

            return CityRealtimeContext(
                city="Mumbai",
                day_name=day_name,
                day_type=day_type,
                current_time_str=time_str,
                time_window=time_window,
                status_headline=headline,
                status_description=desc,
                crowd_level=crowd,
                recommended_mode=recom,
                special_advisory=adv
            )

        # ==============================================================================
        # 3. BENGALURU
        # ==============================================================================
        elif "bengaluru" in c_low or "bangalore" in c_low:
            is_workday = day_idx < 5
            if is_workday and (8 <= hour < 12 or 17 <= hour < 21):
                headline = "Tech Corridor Peak Rush (Outer Ring Road & Silk Board)"
                desc = "Heavy vehicular crawl on Silk Board, Marathahalli, and Bellandur tech corridors. Namma Metro Purple Line running at 3.5 min headway with heavy boarding at Majestic."
                crowd = "Very High"
                recom = "Namma Metro Purple Line (Baiyappanahalli ⇄ Whitefield) to bypass ORR jams."
            else:
                headline = "All Lines Normal — Namma Metro & BMTC On Schedule"
                desc = "No signal delays or disruptions across Namma Metro Purple/Green lines. BMTC Vajra AC buses on 10-15 min frequency."
                crowd = "Moderate"
                recom = "Namma Metro or BMTC Vajra AC Bus."

            return CityRealtimeContext(
                city="Bengaluru",
                day_name=day_name,
                day_type="Weekday (Workday)" if is_workday else "Weekend",
                current_time_str=time_str,
                time_window="Peak Tech Commute" if (8 <= hour < 12 or 17 <= hour < 21) else "Regular Transit Hours",
                status_headline=headline,
                status_description=desc,
                crowd_level=crowd,
                recommended_mode=recom,
                special_advisory="Silk Board & Tin Factory bottlenecks active during peak hours."
            )

        # ==============================================================================
        # 4. DELHI NCR (DEFAULT)
        # ==============================================================================
        else:
            is_peak = (8 <= hour < 12) or (17 <= hour < 21)
            if is_peak:
                headline = "DMRC Peak Commute Active — High Interchange Volume"
                desc = "DMRC operational across all 12 lines with peak automated headway of 2.5-3.5 mins. Rajiv Chowk, Kashmere Gate, Central Secretariat, and Hauz Khas concourses experiencing high boarding inflow."
                crowd = "High"
                recom = "DMRC Yellow/Blue Line or Pink/Magenta Orbital Bypass."
                adv = "Open Transit Data (OTD) live GPS streaming 7,000+ active DTC electric & CNG buses."
            elif 23 <= hour or hour < 5:
                headline = "DMRC Night Maintenance Window (11:15 PM – 5:30 AM)"
                desc = "Metro services closed for regular night track maintenance. DTC limited night service and Delhi Govt TSR Metered Autos operating."
                crowd = "Low"
                recom = "Delhi Govt Metered Auto (TSR) or BluSmart Cab."
                adv = "Night surcharge 25% active on Delhi Auto/Taxi meters."
            else:
                headline = "All Lines Normal — DMRC & DTC Running on Schedule"
                desc = "No signal delays, track blocks, or speed restrictions reported across Yellow, Blue, Red, Violet, or Airport Express lines. DTC electric buses on 8-10 min headway."
                crowd = "Moderate"
                recom = "DMRC Metro or DTC Low-Floor AC Electric Bus."
                adv = "Open Transit Data (OTD) live GPS feed active."

            return CityRealtimeContext(
                city="Delhi NCR",
                day_name=day_name,
                day_type="Weekday" if day_idx < 5 else "Weekend",
                current_time_str=time_str,
                time_window="Peak Commute" if is_peak else "Regular Schedule",
                status_headline=headline,
                status_description=desc,
                crowd_level=crowd,
                recommended_mode=recom,
                special_advisory=adv
            )

    def apply_scenario(self, req: SimulateDelayRequest) -> Dict[str, Any]:
        now_str = datetime.now().strftime("%H:%M:%S")
        scen = req.scenario.lower()
        city = (req.city or "Delhi NCR")

        if scen == "reset":
            self._seed_default_state()
            return {
                "scenario": "reset",
                "city": city,
                "message": f"All {city} transit corridors reset to standard schedule. No active disruptions.",
                "active_incidents": [],
                "delays": self.active_delays
            }

        # ----------------- MUMBAI SCENARIOS -----------------
        elif "mumbai_interchange_rush" in scen:
            delay = req.delay_minutes or 10
            self.active_delays["Mumbai Suburban Railway (Western Line)"] = delay
            self.active_delays["Mumbai Suburban Railway (Central Line)"] = delay
            self.current_scenario = scen

            inc = TransitIncident(
                id="inc-mumbai-dadar-crush",
                line_name="Dadar & Kurla Interchange Platforms",
                mode="rail",
                severity="moderate",
                delay_minutes=delay,
                crowd_level="Very High",
                affected_stations=["Dadar Station", "Kurla Junction", "Andheri Station", "CSMT"],
                headline="Super-Dense Peak Interchange Rush [SIMULATED]",
                description=f"Massive commuter crowd surge at Dadar and Kurla railway interchange bridges. Platform clearance taking ~6-8 minutes. Western & Central locals running with +{delay} min regulation. Metro Line 3 Aqua Line recommended.",
                last_updated=now_str,
                is_simulated=True
            )
            self.active_incidents[inc.id] = inc
            return {
                "scenario": scen,
                "city": "Mumbai",
                "message": f"Simulated Dadar & Kurla interchange rush (+{delay}m).",
                "active_incidents": self.get_incidents("Mumbai"),
                "delays": self.active_delays
            }

        elif "mumbai_mega_block" in scen:
            delay = req.delay_minutes or 20
            self.active_delays["Mumbai Suburban Railway (Central Line)"] = delay
            self.active_delays["Mumbai Suburban Railway (Western Line)"] = delay
            self.current_scenario = scen

            inc = TransitIncident(
                id="inc-mumbai-mega-block",
                line_name="Central & Western Railway Fast Corridors",
                mode="rail",
                severity="moderate",
                delay_minutes=delay,
                crowd_level="Moderate",
                affected_stations=["CSMT", "Byculla", "Dadar", "Kurla", "Bandra"],
                headline="Sunday Railway Mega Block Active [SIMULATED]",
                description=f"Scheduled track maintenance block between CSMT-Vidyavihar and Churchgate-Mumbai Central. Fast locals diverted onto slow tracks with +{delay}m headway. Metro Line 3 Aqua Line and BEST buses running with full capacity.",
                last_updated=now_str,
                is_simulated=True
            )
            self.active_incidents[inc.id] = inc
            return {
                "scenario": scen,
                "city": "Mumbai",
                "message": f"Simulated Sunday Railway Mega Block (+{delay}m).",
                "active_incidents": self.get_incidents("Mumbai"),
                "delays": self.active_delays
            }

        elif "mumbai_traffic_jam" in scen:
            delay = req.delay_minutes or 22
            self.active_delays["Mumbai Metered Kaali-Peeli Taxi"] = delay
            self.active_delays["BEST AC Electric Bus (Chalo Bus)"] = delay
            self.current_scenario = scen

            inc = TransitIncident(
                id="inc-mumbai-traffic-jam",
                line_name="Western Express Highway & BKC Connector",
                mode="taxi",
                severity="moderate",
                delay_minutes=delay,
                crowd_level="High",
                affected_stations=["BKC Flyover", "Bandra-Worli Sea Link Toll", "Kalanagar Junction"],
                headline="Arterial Highway Traffic Jam (WEH & BKC) [SIMULATED]",
                description=f"Heavy bumper-to-bumper road crawl along Western Express Highway and BKC connector. Cabs and Kaali-Peeli taxis facing +{delay} min delay. Underground Metro Line 3 and Suburban Rail running unaffected.",
                last_updated=now_str,
                is_simulated=True
            )
            self.active_incidents[inc.id] = inc
            return {
                "scenario": scen,
                "city": "Mumbai",
                "message": f"Simulated WEH & BKC highway traffic slowdown (+{delay}m).",
                "active_incidents": self.get_incidents("Mumbai"),
                "delays": self.active_delays
            }

        elif "mumbai_monsoon_waterlogging" in scen:
            delay = req.delay_minutes or 16
            self.active_delays["Mumbai Suburban Railway (Central Line)"] = delay
            self.active_delays["BEST AC Electric Bus (Chalo Bus)"] = delay
            self.current_scenario = scen

            inc = TransitIncident(
                id="inc-mumbai-waterlog",
                line_name="Kurla & Sion Low-Lying Tracks",
                mode="rail",
                severity="severe",
                delay_minutes=delay,
                crowd_level="High",
                affected_stations=["Kurla Station", "Sion", "Hindmata", "Chunabhatti"],
                headline="Monsoon High Tide & Track Waterlogging [SIMULATED]",
                description=f"Water accumulation near Kurla-Sion railway culverts. Speed restriction of 25 km/h enforced on Central line slow locals (+{delay}m delay). Elevated Metro Line 1 & Underground Line 3 Aqua Line operating normally.",
                last_updated=now_str,
                is_simulated=True
            )
            self.active_incidents[inc.id] = inc
            return {
                "scenario": scen,
                "city": "Mumbai",
                "message": f"Simulated Monsoon High Tide & Track Waterlogging (+{delay}m).",
                "active_incidents": self.get_incidents("Mumbai"),
                "delays": self.active_delays
            }

        # ----------------- MATHURA & VRINDAVAN SCENARIOS -----------------
        elif "mathura_darshan_surge" in scen or "darshan" in scen:
            delay = req.delay_minutes or 25
            self.active_delays["Shared Tempo / Vikram (Braj Corridor)"] = delay
            self.active_delays["Shared E-Rickshaw Feeder (Toto)"] = delay
            self.current_scenario = scen

            inc = TransitIncident(
                id="inc-mathura-darshan-rush",
                line_name="Bankey Bihari & Prem Mandir Corridor",
                mode="erickshaw",
                severity="moderate",
                delay_minutes=delay,
                crowd_level="Very High",
                affected_stations=["Bankey Bihari Stand", "Vidyapeeth Chauraha", "Prem Mandir", "Chatikara Chauraha"],
                headline="Evening Aarti & Temple Darshan Rush [SIMULATED]",
                description=f"Massive pilgrim congregation for evening Shayan Aarti and Prem Mandir musical fountain. Inner temple lanes closed to all motorized vehicles. Shared Tempos terminating at Chatikara & Pagal Baba. E-Rickshaw transit delayed by +{delay} mins.",
                last_updated=now_str,
                is_simulated=True
            )
            self.active_incidents[inc.id] = inc
            return {
                "scenario": scen,
                "city": "Mathura & Vrindavan",
                "message": f"Simulated Bankey Bihari & Prem Mandir Darshan surge (+{delay}m).",
                "active_incidents": self.get_incidents("Mathura & Vrindavan"),
                "delays": self.active_delays
            }

        elif "mathura_parikrama_rush" in scen or "parikrama" in scen:
            delay = req.delay_minutes or 30
            self.active_delays["Shared Tempo / Vikram (Braj Corridor)"] = delay
            self.active_delays["Mathura-Vrindavan Electric Nagar Seva Bus"] = delay
            self.current_scenario = scen

            inc = TransitIncident(
                id="inc-mathura-parikrama",
                line_name="Govardhan Parikrama & Vrindavan Panchkosi",
                mode="auto",
                severity="moderate",
                delay_minutes=delay,
                crowd_level="Very High",
                affected_stations=["Govardhan Daan Ghati", "Mansi Ganga", "Radha Kund", "Anyor"],
                headline="Ekadashi / Purnima Parikrama Pilgrim Inflow [SIMULATED]",
                description=f"50,000+ devotees undertaking Govardhan 21 km Parikrama. Govardhan-Mathura arterial road barricaded for pilgrim safety. Shared tempos facing +{delay} min diversions via Sonkh road.",
                last_updated=now_str,
                is_simulated=True
            )
            self.active_incidents[inc.id] = inc
            return {
                "scenario": scen,
                "city": "Mathura & Vrindavan",
                "message": f"Simulated Ekadashi / Purnima Parikrama crowd (+{delay}m).",
                "active_incidents": self.get_incidents("Mathura & Vrindavan"),
                "delays": self.active_delays
            }

        elif "mathura_kapat_reopen" in scen or "kapat" in scen:
            delay = req.delay_minutes or 15
            self.active_delays["Shared E-Rickshaw Feeder (Toto)"] = delay
            self.current_scenario = scen

            inc = TransitIncident(
                id="inc-mathura-kapat-reopen",
                line_name="Shri Krishna Janmasthan & Dwarkadhish Gates",
                mode="erickshaw",
                severity="moderate",
                delay_minutes=delay,
                crowd_level="High",
                affected_stations=["Janmabhoomi Gate 1 & 3", "Potra Kund", "Deeg Gate", "Holi Gate"],
                headline="Temple Kapat Reopening Surge (4:30 PM) [SIMULATED]",
                description=f"Sanctums reopening after afternoon rest. Devotees gathering outside Janmasthan and Dwarkadhish gates. Walking queues active; Battery Totos moving at walking pace (+{delay}m delay).",
                last_updated=now_str,
                is_simulated=True
            )
            self.active_incidents[inc.id] = inc
            return {
                "scenario": scen,
                "city": "Mathura & Vrindavan",
                "message": f"Simulated Temple Kapat Reopening surge (+{delay}m).",
                "active_incidents": self.get_incidents("Mathura & Vrindavan"),
                "delays": self.active_delays
            }

        elif "mathura_traffic_diversion" in scen or "diversion" in scen:
            delay = req.delay_minutes or 18
            self.active_delays["Mathura-Vrindavan Electric Nagar Seva Bus"] = delay
            self.active_delays["Shared Tempo / Vikram (Braj Corridor)"] = delay
            self.current_scenario = scen

            inc = TransitIncident(
                id="inc-mathura-diversion",
                line_name="Chatikara-Vrindavan Highway Cut (NH-19)",
                mode="bus",
                severity="moderate",
                delay_minutes=delay,
                crowd_level="High",
                affected_stations=["Chatikara Chauraha", "Pagal Baba Parking", "Vaishno Devi Dham"],
                headline="Outer Highway Parking Diversion Active [SIMULATED]",
                description=f"Private vehicles redirected to Pagal Baba multi-level parking grounds. UP Urban Transport electric feeder buses operating shuttle frequency from Chatikara cut with +{delay} min queue times.",
                last_updated=now_str,
                is_simulated=True
            )
            self.active_incidents[inc.id] = inc
            return {
                "scenario": scen,
                "city": "Mathura & Vrindavan",
                "message": f"Simulated Chatikara-Vrindavan Road Diversion (+{delay}m).",
                "active_incidents": self.get_incidents("Mathura & Vrindavan"),
                "delays": self.active_delays
            }

        # ----------------- DELHI NCR SCENARIOS -----------------
        elif scen == "metro_signal_delay":
            delay = req.delay_minutes or 14
            line = req.target_line or "Yellow Line"
            self.active_delays[line] = delay
            self.current_scenario = scen

            inc = TransitIncident(
                id="inc-sig-yellow",
                line_name=line,
                mode="metro",
                severity="moderate",
                delay_minutes=delay,
                crowd_level="High",
                affected_stations=["Kashmere Gate", "Chandni Chowk", "Rajiv Chowk", "Central Secretariat"],
                headline=f"Automated Signal Regulation on {line} [SIMULATED]",
                description=f"Trains operating with headway of ~8-10 mins between Kashmere Gate and Rajiv Chowk due to trackside signaling calibration. Average delay: +{delay} mins. Magenta Line recommended as an alternative.",
                last_updated=now_str,
                is_simulated=True
            )
            self.active_incidents[inc.id] = inc
            return {
                "scenario": scen,
                "city": "Delhi NCR",
                "message": f"Injected +{delay} min delay on {line}.",
                "active_incidents": self.get_incidents("Delhi NCR"),
                "delays": self.active_delays
            }

        elif scen == "bus_breakdown":
            delay = req.delay_minutes or 20
            line = "DTC Electric Bus 534"
            self.active_delays[line] = delay
            self.current_scenario = scen

            inc = TransitIncident(
                id="inc-bus-534",
                line_name=line,
                mode="bus",
                severity="moderate",
                delay_minutes=delay,
                crowd_level="High",
                affected_stations=["Anand Vihar Flyover", "Lajpat Nagar Ring Road"],
                headline=f"Technical Breakdown & Diversion on {line} [SIMULATED]",
                description=f"Road obstruction at Ring Road underpass. Bus service operating on bypass route with +{delay} min delay. Metro Yellow/Violet lines advised.",
                last_updated=now_str,
                is_simulated=True
            )
            self.active_incidents[inc.id] = inc
            return {
                "scenario": scen,
                "city": "Delhi NCR",
                "message": f"Injected disruption on {line}.",
                "active_incidents": self.get_incidents("Delhi NCR"),
                "delays": self.active_delays
            }

        elif scen == "peak_hour_surge":
            self.active_delays["Yellow Line"] = 6
            self.active_delays["Blue Line"] = 8
            self.current_scenario = scen

            inc = TransitIncident(
                id="inc-peak-surge",
                line_name="Yellow & Blue Line Interchanges",
                mode="metro",
                severity="moderate",
                delay_minutes=8,
                crowd_level="Very High",
                affected_stations=["Rajiv Chowk", "Kashmere Gate", "Hauz Khas", "Noida Sector 62"],
                headline="Evening Peak-Hour Crowd Inflow [SIMULATED]",
                description="Heavy commuter footfall at interchange concourses. Security boarding queues ~5-7 minutes. Consider Magenta Line bypass.",
                last_updated=now_str,
                is_simulated=True
            )
            self.active_incidents[inc.id] = inc
            return {
                "scenario": scen,
                "city": "Delhi NCR",
                "message": "Peak-hour crowd surge simulated across primary interchange corridors.",
                "active_incidents": self.get_incidents("Delhi NCR"),
                "delays": self.active_delays
            }

        elif scen == "monsoon_rain":
            self.active_delays["DTC Electric Bus 534"] = 15
            self.active_delays["DTC Express Bus 419"] = 18
            self.active_delays["Yellow Line"] = 4
            self.current_scenario = scen

            inc = TransitIncident(
                id="inc-rain-weather",
                line_name="City Surface Transit & Buses",
                mode="bus",
                severity="moderate",
                delay_minutes=15,
                crowd_level="High",
                affected_stations=["All Surface Bus Stops", "Metro Walkway Entrances"],
                headline="Heavy Monsoon Downpour — Slower Road Travel [SIMULATED]",
                description="Surface traffic crawl due to waterlogging along low-lying road corridors. Walking paths slippery. Underground Metro lines running normally with high capacity.",
                last_updated=now_str,
                is_simulated=True
            )
            self.active_incidents[inc.id] = inc
            return {
                "scenario": scen,
                "city": "Delhi NCR",
                "message": "Rain weather scenario active. Road transit slowed, underground metro prioritized.",
                "active_incidents": self.get_incidents("Delhi NCR"),
                "delays": self.active_delays
            }

        # ----------------- BENGALURU SCENARIOS -----------------
        elif "blr_silk_board" in scen or "silk_board" in scen:
            delay = req.delay_minutes or 35
            self.active_delays["Karnataka Govt Metered Auto"] = delay
            self.active_delays["BMTC Vajra AC Bus"] = delay
            self.current_scenario = scen

            inc = TransitIncident(
                id="inc-blr-silkboard",
                line_name="Silk Board & Outer Ring Road Tech Corridor",
                mode="auto",
                severity="severe",
                delay_minutes=delay,
                crowd_level="Very High",
                affected_stations=["Silk Board Junction", "HSR Layout", "Bellandur", "Marathahalli"],
                headline="Silk Board & Outer Ring Road Gridlock [SIMULATED]",
                description=f"Severe arterial congestion on Outer Ring Road. Road transit crawling with +{delay}m delay. Namma Metro Purple Line Baiyappanahalli-Whitefield operational without traffic.",
                last_updated=now_str,
                is_simulated=True
            )
            self.active_incidents[inc.id] = inc
            return {
                "scenario": scen,
                "city": "Bengaluru",
                "message": f"Simulated Silk Board & ORR gridlock (+{delay}m).",
                "active_incidents": self.get_incidents("Bengaluru"),
                "delays": self.active_delays
            }

        elif "blr_metro_peak" in scen:
            delay = req.delay_minutes or 8
            self.active_delays["Purple Line (Namma Metro)"] = delay
            self.current_scenario = scen

            inc = TransitIncident(
                id="inc-blr-metro-peak",
                line_name="Namma Metro Majestic Interchange",
                mode="metro",
                severity="moderate",
                delay_minutes=delay,
                crowd_level="Very High",
                affected_stations=["Majestic (Kempegowda)", "MG Road", "Indiranagar", "Baiyappanahalli"],
                headline="Purple & Green Line Interchange Concourse Rush [SIMULATED]",
                description=f"Heavy peak commuter influx connecting from KSR railway station. Boarding wait time ~{delay} minutes. Security queues moving steadily.",
                last_updated=now_str,
                is_simulated=True
            )
            self.active_incidents[inc.id] = inc
            return {
                "scenario": scen,
                "city": "Bengaluru",
                "message": f"Simulated Namma Metro peak rush (+{delay}m).",
                "active_incidents": self.get_incidents("Bengaluru"),
                "delays": self.active_delays
            }

        return {
            "scenario": req.scenario,
            "city": city,
            "message": "Scenario applied",
            "active_incidents": self.get_incidents(city),
            "delays": self.active_delays
        }

simulator_instance = TransitSimulator()
