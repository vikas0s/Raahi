# build_rail_dataset.py
"""
Builds comprehensive, authentic suburban railway datasets for:
1. Mumbai Suburban Railway (Western, Central & Harbour Lines)
2. Bengaluru Suburban / Commuter Rail Network (South Western Railway MEMU/DEMU)
3. Delhi NCR Suburban Railway & Ring Railway Network (Northern Railway EMU)
4. Mathura & Vrindavan Heritage Commuter Shuttle Network
"""
import sys

def generate_fallback_data():
    content = '''"""
Comprehensive verified ground-truth railway dataset for Raahi RailConnect.
Covers authentic suburban railway networks, EMU locals, MEMU, DEMU, and heritage commuter services for:
1. Mumbai Suburban Railway (Western, Central & Harbour Lines — Lifeline of Mumbai)
2. Bengaluru Suburban / Commuter Rail Network (South Western Railway SWR)
3. Delhi NCR Suburban Railway & Ring Railway Network (Northern Railway NR)
4. Mathura-Vrindavan Commuter & Heritage Rail Bus Corridor (North Central Railway NCR)
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ..schemas import (
    RailStation, TrainSummary, TrainSchedule, TrainHalt, LiveRunningStatus, StationBoardItem
)

RAIL_STATIONS: Dict[str, RailStation] = {
    # =========================================================================
    # MUMBAI SUBURBAN RAILWAY (Western, Central & Harbour Lines)
    # =========================================================================
    # Western Line
    "CCG": RailStation(
        code="CCG",
        name="Churchgate Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=18.9322,
        lon=72.8264,
        platforms_count=4,
        category="railway_station",
        aliases=["churchgate", "ccg", "churchgate station", "churchgate local", "church gate", "fort south mumbai"],
        zone="WR"
    ),
    "MEL": RailStation(
        code="MEL",
        name="Marine Lines Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=18.9436,
        lon=72.8242,
        platforms_count=4,
        category="railway_station",
        aliases=["marine lines", "mel", "marine drive local"],
        zone="WR"
    ),
    "CYR": RailStation(
        code="CYR",
        name="Charni Road Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=18.9519,
        lon=72.8188,
        platforms_count=4,
        category="railway_station",
        aliases=["charni road", "cyr", "girgaon chowpatty station"],
        zone="WR"
    ),
    "GTR": RailStation(
        code="GTR",
        name="Grant Road Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=18.9631,
        lon=72.8164,
        platforms_count=4,
        category="railway_station",
        aliases=["grant road", "gtr", "lamington road station"],
        zone="WR"
    ),
    "MMCT": RailStation(
        code="MMCT",
        name="Mumbai Central Station (Local & Main)",
        city="Mumbai",
        state="Maharashtra",
        lat=18.9696,
        lon=72.8193,
        platforms_count=9,
        category="railway_station",
        aliases=["mumbai central", "mmct", "bcl", "bombay central", "mumbai central local"],
        zone="WR"
    ),
    "MX": RailStation(
        code="MX",
        name="Mahalaxmi Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=18.9828,
        lon=72.8236,
        platforms_count=3,
        category="railway_station",
        aliases=["mahalaxmi", "mx", "dhobi ghat station", "haji ali railway"],
        zone="WR"
    ),
    "PL": RailStation(
        code="PL",
        name="Lower Parel Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=18.9950,
        lon=72.8300,
        platforms_count=3,
        category="railway_station",
        aliases=["lower parel", "pl", "high street phoenix station", "lower parel local"],
        zone="WR"
    ),
    "PBHD": RailStation(
        code="PBHD",
        name="Prabhadevi Railway Station (Elphinstone Road)",
        city="Mumbai",
        state="Maharashtra",
        lat=19.0100,
        lon=72.8350,
        platforms_count=2,
        category="railway_station",
        aliases=["prabhadevi", "pbhd", "elphinstone road", "elphinstone station", "siddhivinayak railway"],
        zone="WR"
    ),
    "DDR": RailStation(
        code="DDR",
        name="Dadar Western Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=19.0178,
        lon=72.8431,
        platforms_count=7,
        category="railway_station",
        aliases=["dadar western", "ddr", "dadar wr", "dadar local", "dadar station", "dadar"],
        zone="WR"
    ),
    "BA": RailStation(
        code="BA",
        name="Bandra Railway Station (Suburban)",
        city="Mumbai",
        state="Maharashtra",
        lat=19.0544,
        lon=72.8406,
        platforms_count=7,
        category="railway_station",
        aliases=["bandra station", "ba", "bandra local", "bandra west", "bandra suburban", "linking road station"],
        zone="WR"
    ),
    "KHAR": RailStation(
        code="KHAR",
        name="Khar Road Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=19.0694,
        lon=72.8389,
        platforms_count=4,
        category="railway_station",
        aliases=["khar road", "khar", "khar station"],
        zone="WR"
    ),
    "STC": RailStation(
        code="STC",
        name="Santacruz Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=19.0817,
        lon=72.8419,
        platforms_count=4,
        category="railway_station",
        aliases=["santacruz station", "stc", "mumbai domestic airport station", "santacruz local"],
        zone="WR"
    ),
    "VLP": RailStation(
        code="VLP",
        name="Vile Parle Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=19.0989,
        lon=72.8439,
        platforms_count=4,
        category="railway_station",
        aliases=["vile parle", "vlp", "juhu beach station", "parle station"],
        zone="WR"
    ),
    "ADH": RailStation(
        code="ADH",
        name="Andheri Railway Station (Suburban Interchange)",
        city="Mumbai",
        state="Maharashtra",
        lat=19.1197,
        lon=72.8464,
        platforms_count=9,
        category="railway_station",
        aliases=["andheri station", "adh", "andheri local", "andheri railway station", "andheri west", "andheri east"],
        zone="WR"
    ),
    "JOS": RailStation(
        code="JOS",
        name="Jogeshwari Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=19.1356,
        lon=72.8489,
        platforms_count=4,
        category="railway_station",
        aliases=["jogeshwari station", "jos", "jogeshwari local"],
        zone="WR"
    ),
    "GMN": RailStation(
        code="GMN",
        name="Goregaon Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=19.1644,
        lon=72.8494,
        platforms_count=7,
        category="railway_station",
        aliases=["goregaon station", "gmn", "goregaon local", "nesco exhibition centre station"],
        zone="WR"
    ),
    "MDD": RailStation(
        code="MDD",
        name="Malad Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=19.1864,
        lon=72.8483,
        platforms_count=4,
        category="railway_station",
        aliases=["malad station", "mdd", "malad local", "inorbit mall station malad"],
        zone="WR"
    ),
    "KNDV": RailStation(
        code="KNDV",
        name="Kandivali Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=19.2047,
        lon=72.8525,
        platforms_count=4,
        category="railway_station",
        aliases=["kandivali station", "kndv", "kandivali local"],
        zone="WR"
    ),
    "BVI": RailStation(
        code="BVI",
        name="Borivali Railway Station (Major Suburban Hub)",
        city="Mumbai",
        state="Maharashtra",
        lat=19.2294,
        lon=72.8569,
        platforms_count=10,
        category="railway_station",
        aliases=["borivali station", "bvi", "borivali local", "borivali railway station", "borivali west", "sanjay gandhi national park station"],
        zone="WR"
    ),
    "BSR": RailStation(
        code="BSR",
        name="Vasai Road Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=19.3814,
        lon=72.8331,
        platforms_count=8,
        category="railway_station",
        aliases=["vasai road", "bsr", "vasai station", "vasai local"],
        zone="WR"
    ),
    "VR": RailStation(
        code="VR",
        name="Virar Railway Station (Western Line Terminal)",
        city="Mumbai",
        state="Maharashtra",
        lat=19.4539,
        lon=72.8114,
        platforms_count=8,
        category="railway_station",
        aliases=["virar station", "vr", "virar local", "virar terminal"],
        zone="WR"
    ),

    # Central Line (Main)
    "CSMT": RailStation(
        code="CSMT",
        name="Chhatrapati Shivaji Maharaj Terminus",
        city="Mumbai",
        state="Maharashtra",
        lat=18.9400,
        lon=72.8353,
        platforms_count=18,
        category="railway_station",
        aliases=["csmt", "vt", "victoria terminus", "csmt local", "mumbai csmt", "chhatrapati shivaji terminus", "cst", "cst station"],
        zone="CR"
    ),
    "BY": RailStation(
        code="BY",
        name="Byculla Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=18.9753,
        lon=72.8333,
        platforms_count=4,
        category="railway_station",
        aliases=["byculla station", "by", "byculla local", "jijamata udyan station"],
        zone="CR"
    ),
    "DR": RailStation(
        code="DR",
        name="Dadar Central Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=19.0178,
        lon=72.8478,
        platforms_count=8,
        category="railway_station",
        aliases=["dadar central", "dr", "dadar cr", "dadar central railway", "dadar interchange"],
        zone="CR"
    ),
    "SIN": RailStation(
        code="SIN",
        name="Sion Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=19.0400,
        lon=72.8622,
        platforms_count=4,
        category="railway_station",
        aliases=["sion station", "sin", "sion local"],
        zone="CR"
    ),
    "CLA": RailStation(
        code="CLA",
        name="Kurla Junction Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=19.0653,
        lon=72.8794,
        platforms_count=8,
        category="railway_station",
        aliases=["kurla junction", "cla", "kurla station", "kurla local", "kurla central", "bkc east station"],
        zone="CR"
    ),
    "GC": RailStation(
        code="GC",
        name="Ghatkopar Railway Station (Metro Interchange)",
        city="Mumbai",
        state="Maharashtra",
        lat=19.0863,
        lon=72.9084,
        platforms_count=5,
        category="railway_station",
        aliases=["ghatkopar station", "gc", "ghatkopar local", "ghatkopar railway", "ghatkopar east", "ghatkopar west"],
        zone="CR"
    ),
    "VK": RailStation(
        code="VK",
        name="Vikhroli Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=19.1100,
        lon=72.9297,
        platforms_count=4,
        category="railway_station",
        aliases=["vikhroli station", "vk", "godrej colony station"],
        zone="CR"
    ),
    "MLND": RailStation(
        code="MLND",
        name="Mulund Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=19.1728,
        lon=72.9564,
        platforms_count=4,
        category="railway_station",
        aliases=["mulund station", "mlnd", "mulund local"],
        zone="CR"
    ),
    "TNA": RailStation(
        code="TNA",
        name="Thane Railway Station (Major Central Hub)",
        city="Mumbai",
        state="Maharashtra",
        lat=19.1860,
        lon=72.9759,
        platforms_count=10,
        category="railway_station",
        aliases=["thane station", "tna", "thane local", "thane railway station", "thane junction"],
        zone="CR"
    ),
    "DIVA": RailStation(
        code="DIVA",
        name="Diva Junction Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=19.1883,
        lon=73.0422,
        platforms_count=8,
        category="railway_station",
        aliases=["diva junction", "diva", "diva station"],
        zone="CR"
    ),
    "DI": RailStation(
        code="DI",
        name="Dombivli Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=19.2183,
        lon=73.0867,
        platforms_count=5,
        category="railway_station",
        aliases=["dombivli station", "di", "dombivli local", "dombivali"],
        zone="CR"
    ),
    "KYN": RailStation(
        code="KYN",
        name="Kalyan Junction Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=19.2364,
        lon=73.1306,
        platforms_count=8,
        category="railway_station",
        aliases=["kalyan junction", "kyn", "kalyan station", "kalyan local", "kalyan terminal"],
        zone="CR"
    ),

    # Harbour Line
    "VDLR": RailStation(
        code="VDLR",
        name="Wadala Road Railway Station (Harbour Interchange)",
        city="Mumbai",
        state="Maharashtra",
        lat=19.0189,
        lon=72.8594,
        platforms_count=4,
        category="railway_station",
        aliases=["wadala road", "vdlr", "wadala station", "wadala local"],
        zone="CR"
    ),
    "CMBR": RailStation(
        code="CMBR",
        name="Chembur Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=19.0622,
        lon=72.8997,
        platforms_count=2,
        category="railway_station",
        aliases=["chembur station", "cmbr", "chembur local", "chembur monorail"],
        zone="CR"
    ),
    "VSH": RailStation(
        code="VSH",
        name="Vashi Railway Station (Navi Mumbai Gateway)",
        city="Mumbai",
        state="Maharashtra",
        lat=19.0772,
        lon=72.9986,
        platforms_count=4,
        category="railway_station",
        aliases=["vashi station", "vsh", "vashi local", "vashi railway station", "navi mumbai vashi"],
        zone="CR"
    ),
    "NEU": RailStation(
        code="NEU",
        name="Nerul Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=19.0336,
        lon=73.0186,
        platforms_count=6,
        category="railway_station",
        aliases=["nerul station", "neu", "nerul local", "dy patil stadium station"],
        zone="CR"
    ),
    "BEPR": RailStation(
        code="BEPR",
        name="CBD Belapur Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=19.0183,
        lon=73.0397,
        platforms_count=4,
        category="railway_station",
        aliases=["belapur station", "bepr", "cbd belapur", "belapur local"],
        zone="CR"
    ),
    "PNVL": RailStation(
        code="PNVL",
        name="Panvel Junction Railway Station",
        city="Mumbai",
        state="Maharashtra",
        lat=18.9900,
        lon=73.1189,
        platforms_count=7,
        category="railway_station",
        aliases=["panvel station", "pnvl", "panvel local", "panvel junction", "navi mumbai airport railway"],
        zone="CR"
    ),

    # =========================================================================
    # BENGALURU SUBURBAN / COMMUTER RAIL NETWORK (South Western Railway - SWR)
    # =========================================================================
    "SBC": RailStation(
        code="SBC",
        name="KSR Bengaluru City Junction (Majestic)",
        city="Bengaluru",
        state="Karnataka",
        lat=12.9781,
        lon=77.5695,
        platforms_count=10,
        category="railway_station",
        aliases=["ksr bengaluru", "sbc", "bangalore city", "majestic railway station", "majestic station", "bengaluru city junction", "kempegowda majestic railway"],
        zone="SWR"
    ),
    "BNC": RailStation(
        code="BNC",
        name="Bengaluru Cantt Railway Station",
        city="Bengaluru",
        state="Karnataka",
        lat=12.9936,
        lon=77.5986,
        platforms_count=4,
        category="railway_station",
        aliases=["bangalore cantt", "bnc", "cantonment railway station", "bengaluru cantt", "cantonment station"],
        zone="SWR"
    ),
    "BNCE": RailStation(
        code="BNCE",
        name="Bengaluru East Railway Station",
        city="Bengaluru",
        state="Karnataka",
        lat=12.9997,
        lon=77.6169,
        platforms_count=2,
        category="railway_station",
        aliases=["bangalore east", "bnce", "frazer town station"],
        zone="SWR"
    ),
    "BYPL": RailStation(
        code="BYPL",
        name="Baiyyappanahalli Railway Station (Metro Interchange)",
        city="Bengaluru",
        state="Karnataka",
        lat=12.9931,
        lon=77.6528,
        platforms_count=4,
        category="railway_station",
        aliases=["baiyappanahalli station", "bypl", "baiyyappanahalli railway", "old madras road station"],
        zone="SWR"
    ),
    "SMVB": RailStation(
        code="SMVB",
        name="Sir M. Visvesvaraya Terminal (SMVB)",
        city="Bengaluru",
        state="Karnataka",
        lat=12.9961,
        lon=77.6597,
        platforms_count=8,
        category="railway_station",
        aliases=["smvb", "visvesvaraya terminal", "bypl terminal", "sir m visvesvaraya station"],
        zone="SWR"
    ),
    "KJM": RailStation(
        code="KJM",
        name="Krishnarajapuram Railway Station (K.R. Puram)",
        city="Bengaluru",
        state="Karnataka",
        lat=13.0003,
        lon=77.6764,
        platforms_count=4,
        category="railway_station",
        aliases=["kr puram station", "kjm", "krishnarajapuram railway station", "kr puram junction"],
        zone="SWR"
    ),
    "HDIH": RailStation(
        code="HDIH",
        name="Hoodi Halt Railway Station",
        city="Bengaluru",
        state="Karnataka",
        lat=12.9922,
        lon=77.7167,
        platforms_count=2,
        category="railway_station",
        aliases=["hoodi station", "hdih", "hoodi halt", "itpl station"],
        zone="SWR"
    ),
    "WFD": RailStation(
        code="WFD",
        name="Whitefield Railway Station (Kadugodi)",
        city="Bengaluru",
        state="Karnataka",
        lat=12.9961,
        lon=77.7601,
        platforms_count=4,
        category="railway_station",
        aliases=["whitefield station", "wfd", "whitefield railway station", "kadugodi station", "whitefield suburban"],
        zone="SWR"
    ),
    "YPR": RailStation(
        code="YPR",
        name="Yesvantpur Junction Railway Station",
        city="Bengaluru",
        state="Karnataka",
        lat=13.0236,
        lon=77.5500,
        platforms_count=6,
        category="railway_station",
        aliases=["yesvantpur junction", "ypr", "yeshwanthpur station", "yeshwantpur railway", "yeshwanthpur metro interchange"],
        zone="SWR"
    ),
    "MWM": RailStation(
        code="MWM",
        name="Malleswaram Railway Station",
        city="Bengaluru",
        state="Karnataka",
        lat=13.0033,
        lon=77.5678,
        platforms_count=2,
        category="railway_station",
        aliases=["malleswaram station", "mwm", "malleswaram local"],
        zone="SWR"
    ),
    "HEB": RailStation(
        code="HEB",
        name="Hebbal Railway Station",
        city="Bengaluru",
        state="Karnataka",
        lat=13.0361,
        lon=77.5900,
        platforms_count=2,
        category="railway_station",
        aliases=["hebbal station", "heb", "hebbal railway", "manyata commuter station"],
        zone="SWR"
    ),
    "BAND": RailStation(
        code="BAND",
        name="Banaswadi Railway Station",
        city="Bengaluru",
        state="Karnataka",
        lat=13.0114,
        lon=77.6369,
        platforms_count=3,
        category="railway_station",
        aliases=["banaswadi station", "band", "banaswadi railway"],
        zone="SWR"
    ),
    "YNK": RailStation(
        code="YNK",
        name="Yelahanka Junction Railway Station",
        city="Bengaluru",
        state="Karnataka",
        lat=13.1006,
        lon=77.5964,
        platforms_count=5,
        category="railway_station",
        aliases=["yelahanka junction", "ynk", "yelahanka station", "north bengaluru commuter junction"],
        zone="SWR"
    ),
    "HLE": RailStation(
        code="HLE",
        name="Heelalige Railway Station (Electronic City Feeder)",
        city="Bengaluru",
        state="Karnataka",
        lat=12.8250,
        lon=77.7272,
        platforms_count=2,
        category="railway_station",
        aliases=["heelalige station", "hle", "electronic city commuter station", "chandapura railway", "bommasandra commuter rail"],
        zone="SWR"
    ),
    "CRLM": RailStation(
        code="CRLM",
        name="Karmelaram Railway Station (Sarjapur Road)",
        city="Bengaluru",
        state="Karnataka",
        lat=12.9097,
        lon=77.7011,
        platforms_count=2,
        category="railway_station",
        aliases=["karmelaram station", "crlm", "sarjapur road railway", "bellandur east railway"],
        zone="SWR"
    ),
    "HSRA": RailStation(
        code="HSRA",
        name="Hosur Railway Station (Bengaluru Metropolitan Region)",
        city="Bengaluru",
        state="Tamil Nadu",
        lat=12.7408,
        lon=77.8258,
        platforms_count=4,
        category="railway_station",
        aliases=["hosur station", "hsra", "hosur railway station", "hosur commuter terminal"],
        zone="SWR"
    ),

    # =========================================================================
    # DELHI NCR SUBURBAN RAILWAY & RING RAILWAY NETWORK
    # =========================================================================
    "NDLS": RailStation(
        code="NDLS",
        name="New Delhi Railway Station",
        city="Delhi NCR",
        state="Delhi",
        lat=28.6431,
        lon=77.2223,
        platforms_count=16,
        category="railway_station",
        aliases=["new delhi railway station", "ndls", "paharganj station", "ajmeri gate station", "ndls suburban emu"],
        zone="NR"
    ),
    "DLI": RailStation(
        code="DLI",
        name="Old Delhi Railway Station (Delhi Junction)",
        city="Delhi NCR",
        state="Delhi",
        lat=28.6619,
        lon=77.2280,
        platforms_count=16,
        category="railway_station",
        aliases=["old delhi station", "dli", "delhi jn", "purani dilli railway station", "chandni chowk railway"],
        zone="NR"
    ),
    "NZM": RailStation(
        code="NZM",
        name="Hazrat Nizamuddin Railway Station",
        city="Delhi NCR",
        state="Delhi",
        lat=28.5888,
        lon=77.2533,
        platforms_count=8,
        category="railway_station",
        aliases=["hazrat nizamuddin", "nzm", "nizamuddin station", "sarai kale khan railway station", "ring railway nizamuddin"],
        zone="NR"
    ),
    "ANVT": RailStation(
        code="ANVT",
        name="Anand Vihar Terminal Railway Station",
        city="Delhi NCR",
        state="Delhi",
        lat=28.6508,
        lon=77.3153,
        platforms_count=7,
        category="railway_station",
        aliases=["anand vihar terminal", "anvt", "anand vihar railway station", "east delhi terminal", "anand vihar emu"],
        zone="NR"
    ),
    "DEE": RailStation(
        code="DEE",
        name="Delhi Sarai Rohilla Railway Station",
        city="Delhi NCR",
        state="Delhi",
        lat=28.6622,
        lon=77.1856,
        platforms_count=5,
        category="railway_station",
        aliases=["sarai rohilla", "dee", "delhi sarai rohilla", "shastri nagar railway"],
        zone="NR"
    ),
    "DEC": RailStation(
        code="DEC",
        name="Delhi Cantt Railway Station",
        city="Delhi NCR",
        state="Delhi",
        lat=28.5940,
        lon=77.1260,
        platforms_count=4,
        category="railway_station",
        aliases=["delhi cantt railway", "dec", "cantonment railway station", "ring railway brar square connect"],
        zone="NR"
    ),
    "GZB": RailStation(
        code="GZB",
        name="Ghaziabad Junction Railway Station",
        city="Delhi NCR",
        state="Uttar Pradesh",
        lat=28.6644,
        lon=77.4330,
        platforms_count=6,
        category="railway_station",
        aliases=["ghaziabad junction", "gzb", "ghaziabad station", "ghaziabad emu terminal"],
        zone="NR"
    ),
    "SBB": RailStation(
        code="SBB",
        name="Sahibabad Junction Railway Station",
        city="Delhi NCR",
        state="Uttar Pradesh",
        lat=28.6731,
        lon=77.3756,
        platforms_count=4,
        category="railway_station",
        aliases=["sahibabad junction", "sbb", "sahibabad station", "sahibabad rapidx connect"],
        zone="NR"
    ),
    "FDB": RailStation(
        code="FDB",
        name="Faridabad Railway Station",
        city="Delhi NCR",
        state="Haryana",
        lat=28.4089,
        lon=77.3178,
        platforms_count=4,
        category="railway_station",
        aliases=["faridabad station", "fdb", "old faridabad railway station", "faridabad emu local"],
        zone="NR"
    ),
    "BVH": RailStation(
        code="BVH",
        name="Ballabhgarh Railway Station",
        city="Delhi NCR",
        state="Haryana",
        lat=28.3372,
        lon=77.3228,
        platforms_count=4,
        category="railway_station",
        aliases=["ballabhgarh station", "bvh", "ballabgarh railway"],
        zone="NR"
    ),
    "PWL": RailStation(
        code="PWL",
        name="Palwal Railway Station",
        city="Delhi NCR",
        state="Haryana",
        lat=28.1436,
        lon=77.3262,
        platforms_count=5,
        category="railway_station",
        aliases=["palwal station", "pwl", "palwal railway junction", "delhi palwal emu"],
        zone="NR"
    ),
    "TKJ": RailStation(
        code="TKJ",
        name="Tilak Bridge Railway Station",
        city="Delhi NCR",
        state="Delhi",
        lat=28.6231,
        lon=77.2405,
        platforms_count=4,
        category="railway_station",
        aliases=["tilak bridge", "tkj", "ito railway station", "supreme court railway stop"],
        zone="NR"
    ),
    "CSB": RailStation(
        code="CSB",
        name="Shivaji Bridge Railway Station",
        city="Delhi NCR",
        state="Delhi",
        lat=28.6315,
        lon=77.2312,
        platforms_count=2,
        category="railway_station",
        aliases=["shivaji bridge", "csb", "connaught place railway stop", "mandi house rail stop"],
        zone="NR"
    ),
    "OKA": RailStation(
        code="OKA",
        name="Okhla Railway Station",
        city="Delhi NCR",
        state="Delhi",
        lat=28.5478,
        lon=77.2711,
        platforms_count=3,
        category="railway_station",
        aliases=["okhla station", "oka", "okhla railway", "okhla industrial area rail"],
        zone="NR"
    ),
    "SSB": RailStation(
        code="SSB",
        name="Shakurbasti Railway Station",
        city="Delhi NCR",
        state="Delhi",
        lat=28.6811,
        lon=77.1350,
        platforms_count=4,
        category="railway_station",
        aliases=["shakurbasti station", "ssb", "punjabi bagh railway", "shakurbasti emu shed"],
        zone="NR"
    ),
    "PTNR": RailStation(
        code="PTNR",
        name="Patel Nagar Railway Station (Ring Railway)",
        city="Delhi NCR",
        state="Delhi",
        lat=28.6567,
        lon=77.1611,
        platforms_count=4,
        category="railway_station",
        aliases=["patel nagar railway", "ptnr", "shadipur railway connect"],
        zone="NR"
    ),
    "DSJ": RailStation(
        code="DSJ",
        name="Delhi Safdarjung Railway Station (Ring Railway)",
        city="Delhi NCR",
        state="Delhi",
        lat=28.5772,
        lon=77.2089,
        platforms_count=3,
        category="railway_station",
        aliases=["safdarjung station", "dsj", "delhi safdarjung", "aiims south campus railway"],
        zone="NR"
    ),
    "SOJ": RailStation(
        code="SOJ",
        name="Sarojini Nagar Railway Station (Ring Railway)",
        city="Delhi NCR",
        state="Delhi",
        lat=28.5739,
        lon=77.2000,
        platforms_count=2,
        category="railway_station",
        aliases=["sarojini nagar station", "soj", "sarojini market railway"],
        zone="NR"
    ),
    "LDC": RailStation(
        code="LDC",
        name="Lodhi Colony Railway Station (Ring Railway)",
        city="Delhi NCR",
        state="Delhi",
        lat=28.5811,
        lon=77.2256,
        platforms_count=2,
        category="railway_station",
        aliases=["lodhi colony station", "ldc", "jawaharlal nehru stadium rail"],
        zone="NR"
    ),
    "LPNR": RailStation(
        code="LPNR",
        name="Lajpat Nagar Railway Station (Ring Railway)",
        city="Delhi NCR",
        state="Delhi",
        lat=28.5714,
        lon=77.2433,
        platforms_count=2,
        category="railway_station",
        aliases=["lajpat nagar station", "lpnr", "moolchand railway", "ring railway lajpat nagar"],
        zone="NR"
    ),
    "CNKP": RailStation(
        code="CNKP",
        name="Chanakyapuri Railway Station (Ring Railway)",
        city="Delhi NCR",
        state="Delhi",
        lat=28.5889,
        lon=77.1800,
        platforms_count=2,
        category="railway_station",
        aliases=["chanakyapuri station", "cnkp", "embassy area rail"],
        zone="NR"
    ),
    "BRSQ": RailStation(
        code="BRSQ",
        name="Brar Square Railway Station (Ring Railway)",
        city="Delhi NCR",
        state="Delhi",
        lat=28.6044,
        lon=77.1472,
        platforms_count=2,
        category="railway_station",
        aliases=["brar square", "brsq", "dhaula kuan railway connect"],
        zone="NR"
    ),

    # =========================================================================
    # MATHURA & VRINDAVAN HERITAGE COMMUTER NETWORK
    # =========================================================================
    "MTJ": RailStation(
        code="MTJ",
        name="Mathura Junction Railway Station",
        city="Mathura & Vrindavan",
        state="Uttar Pradesh",
        lat=27.4855,
        lon=77.6737,
        platforms_count=10,
        category="railway_station",
        aliases=["mathura junction", "mtj", "mathura jn", "mathura station", "railway station mathura"],
        zone="NCR"
    ),
    "BDB": RailStation(
        code="BDB",
        name="Vrindavan Railway Station (Heritage Rail Bus)",
        city="Mathura & Vrindavan",
        state="Uttar Pradesh",
        lat=27.5755,
        lon=77.6910,
        platforms_count=2,
        category="railway_station",
        aliases=["vrindavan station", "bdb", "vrindavan railway station", "gandhi park vrindavan", "rail bus vrindavan"],
        zone="NCR"
    ),
    "MRT": RailStation(
        code="MRT",
        name="Mathura Cantt Railway Station",
        city="Mathura & Vrindavan",
        state="Uttar Pradesh",
        lat=27.5028,
        lon=77.7011,
        platforms_count=3,
        category="railway_station",
        aliases=["mathura cantt", "mrt", "cantt station mathura"],
        zone="NER"
    ),
    "BTSR": RailStation(
        code="BTSR",
        name="Bhuteshwar Railway Station",
        city="Mathura & Vrindavan",
        state="Uttar Pradesh",
        lat=27.5089,
        lon=77.6694,
        platforms_count=3,
        category="railway_station",
        aliases=["bhuteshwar station", "btsr", "bhuteshwar railway", "bhuteshwar"],
        zone="NCR"
    ),
    "CHJ": RailStation(
        code="CHJ",
        name="Chhata Railway Station",
        city="Mathura & Vrindavan",
        state="Uttar Pradesh",
        lat=27.7214,
        lon=77.5028,
        platforms_count=3,
        category="railway_station",
        aliases=["chhata railway station", "chj", "chhata station", "chhata railway", "chata station", "chata", "chhata"],
        zone="NCR"
    ),
    "KSV": RailStation(
        code="KSV",
        name="Kosi Kalan Railway Station",
        city="Mathura & Vrindavan",
        state="Uttar Pradesh",
        lat=27.7925,
        lon=77.4328,
        platforms_count=4,
        category="railway_station",
        aliases=["kosi kalan railway station", "ksv", "kosi station", "kosi kalan", "kosi"],
        zone="NCR"
    ),
    "AJH": RailStation(
        code="AJH",
        name="Ajhai Railway Station",
        city="Mathura & Vrindavan",
        state="Uttar Pradesh",
        lat=27.6667,
        lon=77.5450,
        platforms_count=2,
        category="railway_station",
        aliases=["ajhai station", "ajh", "ajhai railway", "ajhai"],
        zone="NCR"
    ),
    "BAAD": RailStation(
        code="BAAD",
        name="Baad Railway Station (Refinery)",
        city="Mathura & Vrindavan",
        state="Uttar Pradesh",
        lat=27.4200,
        lon=77.7100,
        platforms_count=2,
        category="railway_station",
        aliases=["baad station", "baad", "mathura refinery station"],
        zone="NCR"
    ),
    "AGC": RailStation(
        code="AGC",
        name="Agra Cantt Railway Station",
        city="Agra",
        state="Uttar Pradesh",
        lat=27.1587,
        lon=78.0094,
        platforms_count=6,
        category="railway_station",
        aliases=["agra cantt", "agc", "agra railway station"],
        zone="NCR"
    )
}
'''
    return content

print("Template ready")
'''