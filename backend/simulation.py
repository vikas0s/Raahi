"""
Transit Incident and Disruption Simulation Engine for Raahi.
Allows demo scenarios (signal delay, bus disruption, peak crowd, monsoon rain, reset)
with honest data provenance labeling ("SIMULATED" / "DEMO DATA").
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import TransitIncident, SimulateDelayRequest

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
            "DTC Express Bus 419": 0
        }
        self.current_scenario = "normal"

    def get_incidents(self) -> List[TransitIncident]:
        return list(self.active_incidents.values())

    def get_delays_map(self) -> Dict[str, int]:
        return self.active_delays.copy()

    def apply_scenario(self, req: SimulateDelayRequest) -> Dict[str, Any]:
        now_str = datetime.now().strftime("%H:%M:%S")

        if req.scenario == "reset":
            self._seed_default_state()
            return {
                "scenario": "reset",
                "message": "All transit lines reset to standard schedule. No active disruptions.",
                "active_incidents": [],
                "delays": self.active_delays
            }

        elif req.scenario == "metro_signal_delay":
            delay = req.delay_minutes or 14
            line = req.target_line or "Yellow Line"
            self.active_delays[line] = delay
            self.current_scenario = "metro_signal_delay"

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
                "scenario": "metro_signal_delay",
                "message": f"Injected +{delay} min delay on {line}.",
                "active_incidents": self.get_incidents(),
                "delays": self.active_delays
            }

        elif req.scenario == "bus_breakdown":
            delay = req.delay_minutes or 20
            line = "DTC Electric Bus 534"
            self.active_delays[line] = delay
            self.current_scenario = "bus_breakdown"

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
                "scenario": "bus_breakdown",
                "message": f"Injected disruption on {line}.",
                "active_incidents": self.get_incidents(),
                "delays": self.active_delays
            }

        elif req.scenario == "peak_hour_surge":
            self.active_delays["Yellow Line"] = 6
            self.active_delays["Blue Line"] = 8
            self.current_scenario = "peak_hour_surge"

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
                "scenario": "peak_hour_surge",
                "message": "Peak-hour crowd surge simulated across primary interchange corridors.",
                "active_incidents": self.get_incidents(),
                "delays": self.active_delays
            }

        elif req.scenario == "monsoon_rain":
            self.active_delays["DTC Electric Bus 534"] = 15
            self.active_delays["DTC Express Bus 419"] = 18
            self.active_delays["Yellow Line"] = 4
            self.current_scenario = "monsoon_rain"

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
                "scenario": "monsoon_rain",
                "message": "Rain weather scenario active. Road transit slowed, underground metro prioritized.",
                "active_incidents": self.get_incidents(),
                "delays": self.active_delays
            }

        return {
            "scenario": req.scenario,
            "message": "Unknown scenario",
            "active_incidents": self.get_incidents(),
            "delays": self.active_delays
        }

simulator_instance = TransitSimulator()
