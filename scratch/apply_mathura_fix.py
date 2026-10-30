import re
import sys

with open("backend/router.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update _build_mathura_shared_popular_route with Goverdhan Chauraha corridors
target_cond = 'if is_gla and is_bankey_bihari:'
replacement_cond = """is_mathura_city = any(k in orig_name_lower for k in ["junction", "mtj", "station", "cantt", "janmabhoomi", "holi gate", "dampier", "bus stand", "mathura"]) and not ("gla" in orig_name_lower or "chaumuhan" in orig_name_lower or "vrindavan" in orig_name_lower)
            is_dest_gla_nh19 = any(k in dest_name_lower for k in ["gla", "chaumuhan", "chhata", "kosi", "akbarpur"])
            is_orig_gla_nh19 = any(k in orig_name_lower for k in ["gla", "chaumuhan", "chhata", "kosi", "akbarpur"])
            is_dest_mathura_city = any(k in dest_name_lower for k in ["junction", "mtj", "station", "cantt", "janmabhoomi", "holi gate", "dampier", "bus stand", "mathura"]) and not ("gla" in dest_name_lower or "chaumuhan" in dest_name_lower or "vrindavan" in dest_name_lower)
            is_dest_govardhan = any(k in dest_name_lower for k in ["govardhan", "goverdhan", "daan ghati", "mansi ganga", "jatipura"])

            if is_mathura_city and is_dest_gla_nh19:
                # Mathura Junction/City -> Goverdhan Chauraha -> GLA University / NH-19 Highway
                gov_chauraha_pt = [77.6525, 27.4920]
                leg1_dur = 8
                arr1 = curr_time + timedelta(minutes=leg1_dur)
                legs.append(TransitLeg(
                    id=str(uuid.uuid4())[:8],
                    mode="auto",
                    line_name="Goverdhan Chauraha Feeder Auto",
                    line_color="#E68A00",
                    origin_name=orig["name"],
                    destination_name="Goverdhan Chauraha (NH-19 Mathura Entry)",
                    origin_coords=start_pt,
                    destination_coords=gov_chauraha_pt,
                    path_coords=get_road_geometry(start_pt, gov_chauraha_pt, mode="driving"),
                    duration_minutes=leg1_dur,
                    distance_meters=3400,
                    departure_time=curr_time.strftime("%H:%M"),
                    arrival_time=arr1.strftime("%H:%M"),
                    stops_count=2,
                    intermediate_stops=[f"{orig['name']} Outside Gate", "Goverdhan Chauraha Stand"],
                    instructions="Board high-frequency shared Auto / E-Rickshaw outside station gate directly to Goverdhan Chauraha (NH-19 Highway Cut). Flat ₹15.",
                    crowd_level="Low",
                    fare_inr=15.0,
                    fare_details="Station Feeder Auto: Flat ₹15 (Station ➔ Goverdhan Chauraha)"
                ))
                curr_time = arr1

                leg2_dur = 23
                arr2 = curr_time + timedelta(minutes=leg2_dur)
                legs.append(TransitLeg(
                    id=str(uuid.uuid4())[:8],
                    mode="ebus",
                    line_name="UP Urban Electric Bus / NH-19 Highway Tempo",
                    line_color="#00A86B",
                    origin_name="Goverdhan Chauraha (NH-19 Mathura Entry)",
                    destination_name=dest["name"],
                    origin_coords=gov_chauraha_pt,
                    destination_coords=end_pt,
                    path_coords=get_road_geometry(gov_chauraha_pt, end_pt, mode="driving"),
                    duration_minutes=leg2_dur,
                    distance_meters=18200,
                    departure_time=curr_time.strftime("%H:%M"),
                    arrival_time=arr2.strftime("%H:%M"),
                    stops_count=5,
                    intermediate_stops=["Goverdhan Chauraha (NH-19)", "Maholi Road Cut", "Chatikara Road Cut", "Akbarpur Highway Stop", dest["name"]],
                    instructions=f"Board direct UP Urban Electric Bus or NH-19 Shared Tempo towards Chaumuhan/Kosi Kalan. Smooth express run along Delhi-Agra Highway with direct doorstep drop at {dest['name']}.",
                    crowd_level="Moderate",
                    fare_inr=25.0,
                    fare_details=f"UP Electric Bus / Shared Tempo: ₹25 (Goverdhan Chauraha ➔ {dest['name']})"
                ))

                total_mins = leg1_dur + leg2_dur
                total_fare = 15.0 + 25.0
                title = "Feeder Auto ➔ NH-19 E-Bus / Tempo (via Goverdhan Chauraha)"
                tag_reason = "🚀 Arterial Highway Commute: Feeder Auto to Goverdhan Chauraha (₹15) + High-frequency NH-19 Electric Bus / Tempo direct to destination (₹25)."
                transfers = 1
                walk_mins = 0
                walk_dist = 0

            elif is_orig_gla_nh19 and is_dest_mathura_city:
                # GLA University / NH-19 -> Goverdhan Chauraha -> Mathura Junction
                gov_chauraha_pt = [77.6525, 27.4920]
                leg1_dur = 23
                arr1 = curr_time + timedelta(minutes=leg1_dur)
                legs.append(TransitLeg(
                    id=str(uuid.uuid4())[:8],
                    mode="ebus",
                    line_name="UP Urban Electric Bus / NH-19 Highway Tempo",
                    line_color="#00A86B",
                    origin_name=orig["name"],
                    destination_name="Goverdhan Chauraha (NH-19 Mathura Entry)",
                    origin_coords=start_pt,
                    destination_coords=gov_chauraha_pt,
                    path_coords=get_road_geometry(start_pt, gov_chauraha_pt, mode="driving"),
                    duration_minutes=leg1_dur,
                    distance_meters=18200,
                    departure_time=curr_time.strftime("%H:%M"),
                    arrival_time=arr1.strftime("%H:%M"),
                    stops_count=5,
                    intermediate_stops=[orig["name"], "Akbarpur Highway Stop", "Chatikara Road Cut", "Maholi Road Cut", "Goverdhan Chauraha (NH-19)"],
                    instructions=f"Board UP Urban Electric Bus or NH-19 Shared Tempo towards Mathura at {orig['name']}. Disembark at Goverdhan Chauraha (NH-19).",
                    crowd_level="Moderate",
                    fare_inr=25.0,
                    fare_details=f"UP Electric Bus / Shared Tempo: ₹25 ({orig['name']} ➔ Goverdhan Chauraha)"
                ))
                curr_time = arr1

                leg2_dur = 8
                arr2 = curr_time + timedelta(minutes=leg2_dur)
                legs.append(TransitLeg(
                    id=str(uuid.uuid4())[:8],
                    mode="auto",
                    line_name="Goverdhan Chauraha Feeder Auto",
                    line_color="#E68A00",
                    origin_name="Goverdhan Chauraha (NH-19 Mathura Entry)",
                    destination_name=dest["name"],
                    origin_coords=gov_chauraha_pt,
                    destination_coords=end_pt,
                    path_coords=get_road_geometry(gov_chauraha_pt, end_pt, mode="driving"),
                    duration_minutes=leg2_dur,
                    distance_meters=3400,
                    departure_time=curr_time.strftime("%H:%M"),
                    arrival_time=arr2.strftime("%H:%M"),
                    stops_count=2,
                    intermediate_stops=["Goverdhan Chauraha Stand", f"{dest['name']} Outside Gate"],
                    instructions=f"Take high-frequency shared Auto / E-Rickshaw from Goverdhan Chauraha to {dest['name']} gate. Flat ₹15.",
                    crowd_level="Low",
                    fare_inr=15.0,
                    fare_details="Station Feeder Auto: Flat ₹15 (Goverdhan Chauraha ➔ Station)"
                ))

                total_mins = leg1_dur + leg2_dur
                total_fare = 25.0 + 15.0
                title = "NH-19 E-Bus / Tempo ➔ Feeder Auto to Mathura Station (via Goverdhan Chauraha)"
                tag_reason = "🚀 Arterial Highway Commute: NH-19 Electric Bus / Tempo to Goverdhan Chauraha (₹25) + Feeder Auto to Mathura Junction (₹15)."
                transfers = 1
                walk_mins = 0
                walk_dist = 0

            elif is_dest_govardhan and is_mathura_city:
                # Mathura City -> Goverdhan Chauraha -> Govardhan Daan Ghati / Mansi Ganga
                gov_chauraha_pt = [77.6525, 27.4920]
                leg1_dur = 8
                arr1 = curr_time + timedelta(minutes=leg1_dur)
                legs.append(TransitLeg(
                    id=str(uuid.uuid4())[:8],
                    mode="auto",
                    line_name="Goverdhan Chauraha Feeder Auto",
                    line_color="#E68A00",
                    origin_name=orig["name"],
                    destination_name="Goverdhan Chauraha (NH-19 Mathura Entry)",
                    origin_coords=start_pt,
                    destination_coords=gov_chauraha_pt,
                    path_coords=get_road_geometry(start_pt, gov_chauraha_pt, mode="driving"),
                    duration_minutes=leg1_dur,
                    distance_meters=3400,
                    departure_time=curr_time.strftime("%H:%M"),
                    arrival_time=arr1.strftime("%H:%M"),
                    stops_count=2,
                    intermediate_stops=[f"{orig['name']} Outside Gate", "Goverdhan Chauraha Stand"],
                    instructions="Board shared Auto / E-Rickshaw outside station gate to Goverdhan Chauraha. Flat ₹15.",
                    crowd_level="Low",
                    fare_inr=15.0,
                    fare_details="Feeder Auto: Flat ₹15"
                ))
                curr_time = arr1

                leg2_dur = 30
                arr2 = curr_time + timedelta(minutes=leg2_dur)
                legs.append(TransitLeg(
                    id=str(uuid.uuid4())[:8],
                    mode="auto",
                    line_name="Shared Tempo / Vikram (Govardhan Road Corridor)",
                    line_color="#E68A00",
                    origin_name="Goverdhan Chauraha (NH-19 Mathura Entry)",
                    destination_name=dest["name"],
                    origin_coords=gov_chauraha_pt,
                    destination_coords=end_pt,
                    path_coords=get_road_geometry(gov_chauraha_pt, end_pt, mode="driving"),
                    duration_minutes=leg2_dur,
                    distance_meters=21000,
                    departure_time=curr_time.strftime("%H:%M"),
                    arrival_time=arr2.strftime("%H:%M"),
                    stops_count=4,
                    intermediate_stops=["Goverdhan Chauraha Stand", "Pali Khera", "Govardhan Bus Stand", dest["name"]],
                    instructions="Board high-frequency Shared Vikram Tempo along Govardhan Road straight to Govardhan Mandir / Parikrama Marg.",
                    crowd_level="Moderate",
                    fare_inr=35.0,
                    fare_details="Shared Vikram Tempo: Flat ₹35"
                ))

                total_mins = leg1_dur + leg2_dur
                total_fare = 15.0 + 35.0
                title = "Feeder Auto to Goverdhan Chauraha ➔ Shared Vikram to Govardhan"
                tag_reason = "🚀 Most Popular Govardhan Route: Auto to Goverdhan Chauraha (₹15) + Direct Vikram Tempo along Govardhan Road (₹35)."
                transfers = 1
                walk_mins = 0
                walk_dist = 0

            elif is_gla and is_bankey_bihari:"""

if target_cond in text:
    text = text.replace(target_cond, replacement_cond, 1)
    print("Replaced target_cond in _build_mathura_shared_popular_route successfully!")
else:
    print("ERROR: target_cond not found in content!")
    sys.exit(1)

# 2. Update tag in _build_mathura_shared_popular_route
tag_old = 'tag="Most Popular",'
tag_new = 'tag=("⭐ Fastest via Goverdhan Chauraha" if "Goverdhan Chauraha" in title else "Most Popular"),'

if tag_old in text:
    text = text.replace(tag_old, tag_new, 1)
    print("Updated tag in _build_mathura_shared_popular_route!")

# 3. Update default sort in _plan_mathura_journey
sort_old = "routes.sort(key=lambda r: (_avail_key(r), r.total_duration_minutes, r.total_fare_inr))"
sort_new = """def _mathura_rank(r):
                prio = 2
                if "Goverdhan Chauraha" in r.title or "Goverdhan Chauraha" in r.tag:
                    prio = 0
                elif r.route_type in ["mathura_shared", "mathura_ebus", "mathura_tempo"]:
                    prio = 1
                return (_avail_key(r), prio, r.total_duration_minutes, r.total_fare_inr)
            routes.sort(key=_mathura_rank)"""

if sort_old in text:
    text = text.replace(sort_old, sort_new, 1)
    print("Updated sort in _plan_mathura_journey!")

# 4. Add Google Maps check to _plan_mathura_journey
mathura_pop_comment = '# 1. OPTION 1: SHARED E-RICKSHAW / MULTIMODAL TEMPO (MOST POPULAR)'
mathura_pop_replacement = """# Query Google Maps Live Routes if configured
        try:
            from .google_maps_service import google_maps_service_instance
            if google_maps_service_instance.is_configured():
                g_routes = google_maps_service_instance.fetch_routes(
                    orig_lat=origin_dict["lat"],
                    orig_lon=origin_dict["lon"],
                    dest_lat=dest_dict["lat"],
                    dest_lon=dest_dict["lon"],
                    orig_name=origin_dict["name"],
                    dest_name=dest_dict["name"],
                    city="Mathura & Vrindavan",
                    base_time=base_time,
                    mode="transit"
                )
                if not g_routes:
                    g_routes = google_maps_service_instance.fetch_routes(
                        orig_lat=origin_dict["lat"],
                        orig_lon=origin_dict["lon"],
                        dest_lat=dest_dict["lat"],
                        dest_lon=dest_dict["lon"],
                        orig_name=origin_dict["name"],
                        dest_name=dest_dict["name"],
                        city="Mathura & Vrindavan",
                        base_time=base_time,
                        mode="driving"
                    )
                if g_routes:
                    routes.extend(g_routes)
        except Exception:
            pass

        # 1. OPTION 1: SHARED E-RICKSHAW / MULTIMODAL TEMPO (MOST POPULAR)"""

if mathura_pop_comment in text:
    text = text.replace(mathura_pop_comment, mathura_pop_replacement, 1)
    print("Added Google Maps check to _plan_mathura_journey!")

compile(text, "backend/router.py", "exec")
with open("backend/router.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated backend/router.py successfully!")

