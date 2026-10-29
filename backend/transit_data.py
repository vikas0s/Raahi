"""
Real transit network nodes, coordinates, routes, and transit lines for Raahi.
Default primary network: Delhi NCR (DMRC Metro, DTC Electric Buses, Airport Express, Northern Suburban Rail).
Also includes key transit nodes for Mumbai and Bengaluru to support multi-city switching.
"""
from typing import Dict, List, Any

# Transit Places by City
PLACES_DATABASE: Dict[str, List[Dict[str, Any]]] = {
    "Delhi NCR": [
        # --- Central & New Delhi ---
        {
            "name": "Rajiv Chowk (Connaught Place)",
            "lat": 28.6328,
            "lon": 77.2197,
            "category": "metro_station",
            "aliases": ["cp", "connaught place", "central delhi", "rajiv chowk", "inner circle", "cp inner circle"],
            "lines": ["Yellow Line", "Blue Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Connaught Place (Outer Circle & Janpath)",
            "lat": 28.6285,
            "lon": 77.2190,
            "category": "landmark",
            "aliases": ["janpath", "cp outer circle", "outer circle cp", "janpath market", "tibetan market", "scindia house"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Yellow Line", "Blue Line"],
            "has_direct_metro": False,
            "nearest_metro": "Rajiv Chowk (Connaught Place)",
            "metro_dist_km": 0.5
        },
        {
            "name": "Palika Bazaar (Connaught Place)",
            "lat": 28.6315,
            "lon": 77.2180,
            "category": "landmark",
            "aliases": ["palika bazaar", "palika", "underground market cp", "palika underground"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Yellow Line", "Blue Line"],
            "has_direct_metro": True
        },
        {
            "name": "India Gate & Kartavya Path",
            "lat": 28.6129,
            "lon": 77.2295,
            "category": "landmark",
            "aliases": ["india gate", "kartavya path", "rajpath", "central vista", "war memorial", "national war memorial", "childrens park"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "DTC Electric Bus 534"],
            "has_direct_metro": False,
            "nearest_metro": "Rajiv Chowk (Connaught Place)",
            "metro_dist_km": 2.2
        },
        {
            "name": "Rashtrapati Bhavan (Central Vista)",
            "lat": 28.6143,
            "lon": 77.1995,
            "category": "landmark",
            "aliases": ["rashtrapati bhavan", "president house", "north block", "south block", "raisina hill", "mughal gardens", "amrit udyan"],
            "lines": ["Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Rajiv Chowk (Connaught Place)",
            "metro_dist_km": 2.6
        },
        {
            "name": "Khan Market",
            "lat": 28.6003,
            "lon": 77.2270,
            "category": "landmark",
            "aliases": ["khan market", "sujan singh park", "rabindra nagar", "prithviraj market", "khan market cafes"],
            "lines": ["Violet Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Lodhi Garden & India Habitat Centre",
            "lat": 28.5933,
            "lon": 77.2197,
            "category": "landmark",
            "aliases": ["lodhi garden", "lodhi road", "india habitat centre", "ihc", "lodhi colony", "sai baba mandir lodhi"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Violet Line (JLN Stadium)"],
            "has_direct_metro": False,
            "nearest_metro": "Khan Market",
            "metro_dist_km": 1.2
        },
        {
            "name": "Bangla Sahib Gurudwara",
            "lat": 28.6263,
            "lon": 77.2090,
            "category": "landmark",
            "aliases": ["bangla sahib", "gurudwara bangla sahib", "ashoka road", "sarovar bangla sahib"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Blue Line (Patel Chowk / Shivaji Stadium)"],
            "has_direct_metro": False,
            "nearest_metro": "Rajiv Chowk (Connaught Place)",
            "metro_dist_km": 1.1
        },
        {
            "name": "Gole Market",
            "lat": 28.6335,
            "lon": 77.2030,
            "category": "landmark",
            "aliases": ["gole market", "gol market", "baba kharak singh marg", "peshwa road"],
            "lines": ["Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Rajiv Chowk (Connaught Place)",
            "metro_dist_km": 1.6
        },

        # --- Old Delhi & North Delhi ---
        {
            "name": "Chandni Chowk (Main Bazaar)",
            "lat": 28.6562,
            "lon": 77.2301,
            "category": "landmark",
            "aliases": ["chandni chowk", "paranthe wali gali", "old delhi bazaar", "dariba kalan", "khari baoli", "spice market", "sis ganj gurudwara", "fatehpuri"],
            "lines": ["Yellow Line", "Delhi Govt Metered Auto (TSR)", "Yamuna Braj Heritage Cycle Rickshaw"],
            "has_direct_metro": True
        },
        {
            "name": "Red Fort (Lal Qila)",
            "lat": 28.6562,
            "lon": 77.2410,
            "category": "landmark",
            "aliases": ["red fort", "lal qila", "lahori gate", "netaji subhash marg", "meena bazaar lal qila"],
            "lines": ["Violet Line (Lal Quila)", "Yellow Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Jama Masjid (Old Delhi)",
            "lat": 28.6507,
            "lon": 77.2334,
            "category": "landmark",
            "aliases": ["jama masjid", "karim restaurant", "al jawahar", "matia mahal", "meena bazaar jama masjid"],
            "lines": ["Violet Line (Jama Masjid)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Kashmere Gate ISBT",
            "lat": 28.6675,
            "lon": 77.2285,
            "category": "metro_station",
            "aliases": ["kashmere gate", "isbt", "old delhi interstate bus", "st james church", "maharana pratap isbt"],
            "lines": ["Yellow Line", "Red Line", "Violet Line", "DTC Terminal", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Old Delhi Railway Station (DLI)",
            "lat": 28.6619,
            "lon": 77.2280,
            "category": "railway_station",
            "aliases": ["old delhi railway station", "dli", "delhi jn", "purani dilli station", "kashmere gate railway"],
            "lines": ["Yellow Line (Chandni Chowk)", "Northern Railway", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "New Delhi Railway Station (NDLS)",
            "lat": 28.6431,
            "lon": 77.2223,
            "category": "railway_station",
            "aliases": ["ndls", "new delhi station", "paharganj", "ajmeri gate", "ndls platform 1", "ndls platform 16"],
            "lines": ["Yellow Line", "Airport Express", "Northern Railway", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Majnu Ka Tila (Tibetan Colony)",
            "lat": 28.7005,
            "lon": 77.2275,
            "category": "landmark",
            "aliases": ["majnu ka tila", "mkt", "tibetan market", "little tibet", "aruna nagar", "tibetan monastery"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Yellow Line (Vidhan Sabha)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Vishwavidyalaya (Delhi University)",
            "metro_dist_km": 1.6
        },
        {
            "name": "Vishwavidyalaya (Delhi University North Campus)",
            "lat": 28.6974,
            "lon": 77.2144,
            "category": "metro_station",
            "aliases": ["du north campus", "vishwavidyalaya", "arts faculty", "university of delhi", "st stephens", "hindu college", "srcc", "kirori mal"],
            "lines": ["Yellow Line", "Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": True
        },
        {
            "name": "Kamla Nagar (Bungalow Road & Clock Tower)",
            "lat": 28.6815,
            "lon": 77.2025,
            "category": "landmark",
            "aliases": ["kamla nagar", "k nagar", "bungalow road", "spark mall", "kamla nagar market", "clock tower subzi mandi"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)", "Yellow Line"],
            "has_direct_metro": False,
            "nearest_metro": "Vishwavidyalaya (Delhi University North Campus)",
            "metro_dist_km": 1.2
        },
        {
            "name": "Hudson Lane & GTB Nagar (North Campus)",
            "lat": 28.6930,
            "lon": 77.2065,
            "category": "landmark",
            "aliases": ["hudson lane", "gtb nagar", "north campus cafes", "kingsway camp", "hudson cafe street"],
            "lines": ["Yellow Line (GTB Nagar)", "Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Civil Lines",
            "lat": 28.6790,
            "lon": 77.2220,
            "category": "metro_station",
            "aliases": ["civil lines", "old secretariat", "delhi vidhana sabha", "alipur road"],
            "lines": ["Yellow Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Burari (Transport Authority & ARU Unit)",
            "lat": 28.7420,
            "lon": 77.2020,
            "category": "landmark",
            "aliases": ["burari", "burari transport authority", "aru taxi unit burari", "burari crossing", "sant nagar burari"],
            "lines": ["DTC Bus 185", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Vishwavidyalaya (Delhi University North Campus)",
            "metro_dist_km": 4.6
        },

        # --- South Delhi (Colonies, Markets & Heritage) ---
        {
            "name": "Sarojini Nagar Market",
            "lat": 28.5750,
            "lon": 77.1985,
            "category": "landmark",
            "aliases": ["sarojini nagar", "sn market", "babu market", "sarojini export market", "sarojini nagar market"],
            "lines": ["Pink Line (Sarojini Nagar)", "Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": True
        },
        {
            "name": "Dilli Haat & INA Market",
            "lat": 28.5732,
            "lon": 77.2090,
            "category": "landmark",
            "aliases": ["dilli haat", "ina market", "dilli haat ina", "crafts village delhi", "ina food market"],
            "lines": ["Yellow Line (Dilli Haat INA)", "Pink Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "AIIMS Delhi & Safdarjung Hospital",
            "lat": 28.5672,
            "lon": 77.2100,
            "category": "landmark",
            "aliases": ["aiims", "aiims hospital", "safdarjung hospital", "ansari nagar", "aiims trauma centre"],
            "lines": ["Yellow Line (AIIMS)", "Delhi Govt Metered Auto (TSR)", "DTC Bus 534"],
            "has_direct_metro": True
        },
        {
            "name": "South Extension (Part 1 & 2)",
            "lat": 28.5695,
            "lon": 77.2225,
            "category": "landmark",
            "aliases": ["south ex", "south extension", "south ex 1", "south ex 2", "ring road south ex", "south extension market"],
            "lines": ["Pink Line (South Extension)", "Delhi Govt Metered Auto (TSR)", "DTC Bus 534"],
            "has_direct_metro": True
        },
        {
            "name": "Lajpat Nagar Central Market",
            "lat": 28.5708,
            "lon": 77.2373,
            "category": "landmark",
            "aliases": ["lajpat nagar", "central market", "defence colony flyover", "pushpa market", "3cs lajpat", "lajpat 2"],
            "lines": ["Violet Line", "Pink Line", "DTC Bus 534", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Defence Colony (Main Market)",
            "lat": 28.5740,
            "lon": 77.2310,
            "category": "landmark",
            "aliases": ["defence colony", "def col", "def col market", "defence colony flyover market"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Violet Line (Lajpat Nagar)"],
            "has_direct_metro": False,
            "nearest_metro": "Lajpat Nagar Central Market",
            "metro_dist_km": 0.8
        },
        {
            "name": "Hauz Khas Village (HKV & Deer Park)",
            "lat": 28.5535,
            "lon": 77.1945,
            "category": "landmark",
            "aliases": ["hauz khas village", "hkv", "deer park", "hauz khas lake", "hkv cafes", "hauz khas fort"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": False,
            "nearest_metro": "Hauz Khas",
            "metro_dist_km": 1.4
        },
        {
            "name": "Hauz Khas",
            "lat": 28.5434,
            "lon": 77.2064,
            "category": "metro_station",
            "aliases": ["hauz khas interchange", "south delhi interchange", "aurobindo marg", "iit crossing"],
            "lines": ["Yellow Line", "Magenta Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Green Park Market",
            "lat": 28.5585,
            "lon": 77.2065,
            "category": "landmark",
            "aliases": ["green park", "green park main market", "urobindo place", "green park extension"],
            "lines": ["Yellow Line (Green Park)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "IIT Delhi (Hauz Khas Campus)",
            "lat": 28.5450,
            "lon": 77.1925,
            "category": "landmark",
            "aliases": ["iit delhi", "iit campus", "iit gate", "iit flyover", "bharti school iit"],
            "lines": ["Magenta Line (IIT)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Malviya Nagar & Shivalik",
            "lat": 28.5340,
            "lon": 77.2120,
            "category": "landmark",
            "aliases": ["malviya nagar", "shivalik", "malviya nagar main market", "corner market malviya", "geetanjali enclave"],
            "lines": ["Yellow Line (Malviya Nagar)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Saket (Select Citywalk & DLF Avenue Malls)",
            "lat": 28.5285,
            "lon": 77.2195,
            "category": "landmark",
            "aliases": ["select citywalk", "saket malls", "dlf avenue saket", "citywalk", "max hospital saket", "south court mall saket", "saket"],
            "lines": ["Yellow Line (Malviya Nagar / Saket)", "Delhi Govt Metered Auto (TSR)", "DTC Bus 419"],
            "has_direct_metro": False,
            "nearest_metro": "Malviya Nagar & Shivalik",
            "metro_dist_km": 1.1
        },
        {
            "name": "Qutub Minar & Mehrauli Archaeological Park",
            "lat": 28.5244,
            "lon": 77.1855,
            "category": "landmark",
            "aliases": ["qutub minar", "qutab minar", "mehrauli", "iron pillar", "mehrauli archaeological park", "qutub complex"],
            "lines": ["Yellow Line (Qutab Minar)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Chhatarpur Mandir",
            "lat": 28.5025,
            "lon": 77.1820,
            "category": "landmark",
            "aliases": ["chhatarpur mandir", "katyayani mandir", "chhatarpur temple", "chhatarpur road"],
            "lines": ["Yellow Line (Chhattarpur)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Greater Kailash 1 (GK-1 M-Block Market)",
            "lat": 28.5490,
            "lon": 77.2345,
            "category": "landmark",
            "aliases": ["gk1", "gk 1", "gk 1 m block", "greater kailash 1", "m block market gk 1", "n block gk 1"],
            "lines": ["Magenta Line (Greater Kailash)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Greater Kailash 2 (GK-2 M-Block Market)",
            "lat": 28.5335,
            "lon": 77.2435,
            "category": "landmark",
            "aliases": ["gk2", "gk 2", "gk 2 m block", "greater kailash 2", "savitri cinema", "m block gk 2 cafes"],
            "lines": ["Magenta Line (Greater Kailash)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Greater Kailash 1 (GK-1 M-Block Market)",
            "metro_dist_km": 1.5
        },
        {
            "name": "Chittaranjan Park (CR Park Markets)",
            "lat": 28.5390,
            "lon": 77.2520,
            "category": "landmark",
            "aliases": ["cr park", "chittaranjan park", "cr park market 1", "cr park market 2", "bengali sweets cr park", "fish market cr park"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Magenta Line (Nehru Enclave)"],
            "has_direct_metro": False,
            "nearest_metro": "Nehru Place IT Hub",
            "metro_dist_km": 1.4
        },
        {
            "name": "Nehru Place IT Hub",
            "lat": 28.5493,
            "lon": 77.2526,
            "category": "landmark",
            "aliases": ["nehru place", "computer market", "electronics hub", "eros cinema nehru place", "nehru place bus terminal"],
            "lines": ["Violet Line", "Magenta Line (Kalkaji)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Lotus Temple (Bahai House of Worship)",
            "lat": 28.5535,
            "lon": 77.2588,
            "category": "landmark",
            "aliases": ["lotus temple", "bahai temple", "lotus mandir", "kalkaji lotus temple"],
            "lines": ["Violet Line (Kalkaji Mandir)", "Magenta Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "ISKCON Temple Delhi (East of Kailash)",
            "lat": 28.5562,
            "lon": 77.2535,
            "category": "landmark",
            "aliases": ["iskcon delhi", "iskcon east of kailash", "hare krishna temple delhi", "sant nagar iskcon"],
            "lines": ["Violet Line (Nehru Place)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Nehru Place IT Hub",
            "metro_dist_km": 0.9
        },
        {
            "name": "Kalkaji Mandir",
            "lat": 28.5505,
            "lon": 77.2610,
            "category": "landmark",
            "aliases": ["kalkaji mandir", "kalka ji", "kalkaji temple", "maa kalka mandir"],
            "lines": ["Violet Line", "Magenta Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Vasant Kunj (DLF Promenade & Ambience Mall)",
            "lat": 28.5410,
            "lon": 77.1555,
            "category": "landmark",
            "aliases": ["vasant kunj malls", "dlf promenade", "ambience mall vasant kunj", "dlf emporio", "nelson mandela marg", "vasant kunj"],
            "lines": ["DTC Electric Bus 534", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Chhatarpur Mandir",
            "metro_dist_km": 3.4
        },
        {
            "name": "Vasant Vihar (Priya Cinema / Basant Lok)",
            "lat": 28.5570,
            "lon": 77.1620,
            "category": "landmark",
            "aliases": ["vasant vihar", "priya cinema", "basant lok market", "pvr priya", "vasant vihar market"],
            "lines": ["Magenta Line (Vasant Vihar)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Chanakyapuri (Diplomatic Enclave)",
            "lat": 28.5985,
            "lon": 77.1885,
            "category": "landmark",
            "aliases": ["chanakyapuri", "embassy area", "diplomatic enclave", "shanti path", "malcha marg", "yashwant place"],
            "lines": ["Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Rajiv Chowk (Connaught Place)",
            "metro_dist_km": 3.8
        },
        {
            "name": "Satya Niketan (DU South Campus Hub)",
            "lat": 28.5875,
            "lon": 77.1685,
            "category": "landmark",
            "aliases": ["satya niketan", "du south campus", "south campus cafes", "venky college", "benito juarez marg"],
            "lines": ["Pink Line (Durgabai Deshmukh South Campus)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Delhi Cantt (Army Cantonment & Railway Station)",
            "lat": 28.5940,
            "lon": 77.1260,
            "category": "railway_station",
            "aliases": ["delhi cantt", "delhi cantt station", "dec railway station", "cantonment delhi", "sadar bazaar cantt"],
            "lines": ["Pink Line (Delhi Cantt)", "Northern Railway", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },

        # --- West Delhi ---
        {
            "name": "Karol Bagh (Ajmal Khan Road & Gaffar Market)",
            "lat": 28.6515,
            "lon": 77.1905,
            "category": "landmark",
            "aliases": ["karol bagh", "gaffar market", "ajmal khan road", "karol bagh market", "electronic market gaffar", "roop vatika"],
            "lines": ["Blue Line (Karol Bagh)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Rajouri Garden (Main Market & Malls)",
            "lat": 28.6475,
            "lon": 77.1215,
            "category": "landmark",
            "aliases": ["rajouri garden", "rajouri market", "tdi mall rajouri", "city square mall", "rajouri ring road", "west gate mall"],
            "lines": ["Blue Line", "Pink Line (Rajouri Garden)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Punjabi Bagh (Club Road)",
            "lat": 28.6675,
            "lon": 77.1320,
            "category": "landmark",
            "aliases": ["punjabi bagh", "club road", "punjabi bagh central market", "punjabi bagh club cafes", "rohtak road"],
            "lines": ["Green Line", "Pink Line (Punjabi Bagh West)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Janakpuri District Centre",
            "lat": 28.6294,
            "lon": 77.0778,
            "category": "landmark",
            "aliases": ["janakpuri", "district centre janakpuri", "dc janakpuri", "piccadilly mall", "west delhi junction"],
            "lines": ["Blue Line (Janakpuri West)", "Magenta Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Tilak Nagar (Central Market & Jail Road)",
            "lat": 28.6365,
            "lon": 77.0965,
            "category": "landmark",
            "aliases": ["tilak nagar", "jail road", "tilak nagar market", "jail road food street", "fateh nagar"],
            "lines": ["Blue Line (Tilak Nagar)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Paschim Vihar (Jwala Heri Market)",
            "lat": 28.6720,
            "lon": 77.1025,
            "category": "landmark",
            "aliases": ["paschim vihar", "jwala heri", "jwala heri market", "bhera enclave", "peeragarhi"],
            "lines": ["Green Line (Paschim Vihar West)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Pitampura (Netaji Subhash Place & TV Tower)",
            "lat": 28.6980,
            "lon": 77.1520,
            "category": "landmark",
            "aliases": ["nsp", "netaji subhash place", "pitampura", "dilli haat pitampura", "pitampura tv tower", "max hospital pitampura"],
            "lines": ["Red Line", "Pink Line (Netaji Subhash Place)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Rohini Sector 10 (Swarn Jayanti Park / Metro Walk)",
            "lat": 28.7150,
            "lon": 77.1160,
            "category": "landmark",
            "aliases": ["rohini", "rohini sector 10", "swarn jayanti park", "metro walk mall", "adventure island rohini", "rohini west"],
            "lines": ["Red Line (Rithala / Rohini West)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Dwarka Sector 10 & 21 (City Centre)",
            "lat": 28.5815,
            "lon": 77.0585,
            "category": "landmark",
            "aliases": ["dwarka", "dwarka sector 10", "dwarka sector 21", "dwarka city centre", "vegas mall dwarka"],
            "lines": ["Blue Line", "Airport Express (Dwarka Sector 21)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Dwarka Ramphal Chowk (Sector 7)",
            "lat": 28.5870,
            "lon": 77.0740,
            "category": "landmark",
            "aliases": ["ramphal chowk", "dwarka sector 7", "ramphal market", "dwarka food street"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Blue Line (Dwarka Sector 9)"],
            "has_direct_metro": False,
            "nearest_metro": "Dwarka Sector 10 & 21 (City Centre)",
            "metro_dist_km": 1.8
        },
        {
            "name": "Mayapuri Industrial Area",
            "lat": 28.6315,
            "lon": 77.1325,
            "category": "landmark",
            "aliases": ["mayapuri", "mayapuri phase 1", "mayapuri phase 2", "mayapuri industrial"],
            "lines": ["Pink Line (Mayapuri)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },

        # --- East Delhi ---
        {
            "name": "Akshardham Temple (Swaminarayan Complex)",
            "lat": 28.6127,
            "lon": 77.2773,
            "category": "landmark",
            "aliases": ["akshardham", "akshardham temple", "swaminarayan temple", "akshardham mandir", "yamuna sports complex"],
            "lines": ["Blue Line (Akshardham)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Laxmi Nagar (Vikas Marg)",
            "lat": 28.6310,
            "lon": 77.2775,
            "category": "landmark",
            "aliases": ["laxmi nagar", "vikas marg", "ca hub delhi", "laxmi nagar market", "east delhi market", "shakarpur"],
            "lines": ["Blue Line (Laxmi Nagar)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Mayur Vihar Phase 1 (Pocket 1 Market)",
            "lat": 28.6050,
            "lon": 77.2950,
            "category": "landmark",
            "aliases": ["mayur vihar", "mayur vihar 1", "pocket 1 mayur vihar", "acharyaniketan", "mayur vihar market"],
            "lines": ["Blue Line", "Pink Line (Mayur Vihar 1)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Anand Vihar ISBT & Railway Terminal (ANVT)",
            "lat": 28.6469,
            "lon": 77.3160,
            "category": "railway_station",
            "aliases": ["anand vihar", "east delhi terminal", "anvt", "anand vihar isbt", "anand vihar railway station"],
            "lines": ["Blue Line", "Pink Line", "Northern Railway", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Shahdara (Main Market & Railway Station)",
            "lat": 28.6730,
            "lon": 77.2885,
            "category": "railway_station",
            "aliases": ["shahdara", "shahdara station", "shahdara market", "chhota bazaar shahdara"],
            "lines": ["Red Line (Shahdara)", "Northern Railway", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Dilshad Garden",
            "lat": 28.6780,
            "lon": 77.3150,
            "category": "metro_station",
            "aliases": ["dilshad garden", "gtb hospital", "east delhi border", "shahdara border"],
            "lines": ["Red Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Sarai Kale Khan ISBT & Hazrat Nizamuddin Station",
            "lat": 28.5885,
            "lon": 77.2530,
            "category": "railway_station",
            "aliases": ["nizamuddin", "hazrat nizamuddin", "nizamuddin station", "sarai kale khan", "sarai kale khan isbt", "nizamuddin dargah"],
            "lines": ["Pink Line (Sarai Kale Khan - Nizamuddin)", "Northern Railway", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },

        # --- Outer Local Hubs ---
        {
            "name": "Sangam Vihar (Devli More)",
            "lat": 28.5020,
            "lon": 77.2410,
            "category": "landmark",
            "aliases": ["sangam vihar", "devli", "tigdri", "hamdard", "devli more"],
            "lines": ["DTC Electric Bus 419", "Delhi Govt Metered Auto (TSR)", "Auto to Saket Metro"],
            "has_direct_metro": False,
            "nearest_metro": "Saket (Select Citywalk & DLF Avenue Malls)",
            "metro_dist_km": 4.1
        },
        {
            "name": "Najafgarh (BDO Complex)",
            "lat": 28.6130,
            "lon": 76.9850,
            "category": "landmark",
            "aliases": ["najafgarh", "thana road", "dehat", "dichau kalan", "najafgarh bazaar"],
            "lines": ["DTC Bus 729", "Grey Line (Dhansa Bus Stand)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Janakpuri District Centre",
            "metro_dist_km": 6.8
        },
        {
            "name": "Bawana Industrial Area Sector 1",
            "lat": 28.7980,
            "lon": 77.0510,
            "category": "landmark",
            "aliases": ["bawana", "bawana industrial", "dsiidc bawana", "outer delhi", "narela road"],
            "lines": ["DTC Bus 114", "DTC Electric Express", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Kashmere Gate ISBT",
            "metro_dist_km": 14.2
        },

        # --- NCR Extensions & Airports ---
        {
            "name": "IGI Airport Terminal 3",
            "lat": 28.5562,
            "lon": 77.0864,
            "category": "landmark",
            "aliases": ["igi", "airport", "t3", "delhi airport", "aerocity", "terminal 3 igi"],
            "lines": ["Airport Express", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "IGI Airport Terminal 1 (Domestic)",
            "lat": 28.5665,
            "lon": 77.1180,
            "category": "landmark",
            "aliases": ["t1", "terminal 1", "igi t1", "domestic airport delhi", "t1d"],
            "lines": ["Magenta Line (Terminal 1 IGI Airport)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Cyber City (Gurugram)",
            "lat": 28.4950,
            "lon": 77.0895,
            "category": "landmark",
            "aliases": ["cyber hub", "dlf cyber city", "gurgaon tech park", "cyber city", "dlf phase 2"],
            "lines": ["Rapid Metro Gurugram", "Yellow Line (via Sikanderpur)"],
            "has_direct_metro": True
        },
        {
            "name": "Millennium City Centre (Gurugram)",
            "lat": 28.4593,
            "lon": 77.0725,
            "category": "metro_station",
            "aliases": ["huda city centre", "millennium city", "gurgaon south", "sector 29 gurgaon"],
            "lines": ["Yellow Line"],
            "has_direct_metro": True
        },
        {
            "name": "Noida Sector 18 (Atta Market & Mall of India)",
            "lat": 28.5700,
            "lon": 77.3210,
            "category": "landmark",
            "aliases": ["noida 18", "atta market", "mall of india", "dlf mall of india", "great india place", "gip noida"],
            "lines": ["Blue Line (Noida Sector 18)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True
        },
        {
            "name": "Noida Sector 62 (Electronic City IT Hub)",
            "lat": 28.6279,
            "lon": 77.3622,
            "category": "metro_station",
            "aliases": ["noida 62", "electronic city", "noida it hub", "fortis noida", "sector 62"],
            "lines": ["Blue Line"],
            "has_direct_metro": True
        },
        {
            "name": "Botanical Garden (Noida)",
            "lat": 28.5641,
            "lon": 77.3342,
            "category": "metro_station",
            "aliases": ["botanical", "noida interchange", "sector 38 noida"],
            "lines": ["Blue Line", "Magenta Line"],
            "has_direct_metro": True
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
    ],
    "Mathura & Vrindavan": [
        {
            "name": "Mathura Junction Railway Station (MTJ)",
            "lat": 27.4855,
            "lon": 77.6737,
            "category": "railway_station",
            "aliases": ["mathura junction", "mtj", "mathura station", "railway station mathura", "cantt side exit", "platform 1 mathura", "station"],
            "lines": ["Shared Tempo / Vikram (Braj Corridor)", "Mathura-Vrindavan Electric Nagar Seva Bus", "Shared E-Rickshaw Feeder (Toto)", "Reserved Auto-Rickshaw (निजी ऑटो)"]
        },
        {
            "name": "Mathura Cantt Railway Station",
            "lat": 27.5028,
            "lon": 77.7011,
            "category": "railway_station",
            "aliases": ["mathura cantt", "cantt station", "mrt", "sadar bazaar mathura"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Reserved Auto-Rickshaw (निजी ऑटो)"]
        },
        {
            "name": "Shri Krishna Janmabhoomi (Janmasthan)",
            "lat": 27.5050,
            "lon": 77.6698,
            "category": "landmark",
            "aliases": ["janmabhoomi", "krishna janmabhoomi", "janmasthan", "shri krishna janmasthan", "keshavdev mandir", "bhagwat bhavan", "deeg gate", "malla pura"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Shared Tempo / Vikram (Braj Corridor)", "Reserved Auto-Rickshaw (निजी ऑटो)"]
        },
        {
            "name": "Potra Kund (Janmabhoomi)",
            "lat": 27.5062,
            "lon": 77.6685,
            "category": "landmark",
            "aliases": ["potra kund", "pavitra kund", "janmasthan kund"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)"]
        },
        {
            "name": "Shri Dwarkadhish Temple (Mathura)",
            "lat": 27.5042,
            "lon": 77.6845,
            "category": "landmark",
            "aliases": ["dwarkadhish", "dwarkadheesh temple", "dwarka dham mathura", "rajaadhiraj mandir", "asikunda"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Cycle Rickshaw & Kunj Gali Walk"]
        },
        {
            "name": "Vishram Ghat (Yamuna River)",
            "lat": 27.5048,
            "lon": 77.6860,
            "category": "landmark",
            "aliases": ["vishram ghat", "yamuna ji", "yamuna maha aarti", "mathura ghats", "boating ghat mathura", "yamuna pujan"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Cycle Rickshaw & Kunj Gali Walk"]
        },
        {
            "name": "Kans Qila & Bengali Ghat",
            "lat": 27.4995,
            "lon": 77.6890,
            "category": "landmark",
            "aliases": ["kans qila", "kans fort", "bengali ghat", "dhruva ghat"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)"]
        },
        {
            "name": "Holi Gate & Chhatta Bazaar",
            "lat": 27.4988,
            "lon": 77.6806,
            "category": "landmark",
            "aliases": ["holi gate", "chhatta bazaar", "tilak dwar", "mathura market", "pedewala chowk", "brijwasi peda"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Shared Tempo / Vikram (Braj Corridor)"]
        },
        {
            "name": "Dampier Nagar (City Center)",
            "lat": 27.4938,
            "lon": 77.6766,
            "category": "landmark",
            "aliases": ["dampier nagar", "dampier park", "city center mathura", "court road", "head post office mathura"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Reserved Auto-Rickshaw (निजी ऑटो)"]
        },
        {
            "name": "Old Bus Stand / Bhuteshwar ISBT",
            "lat": 27.5074,
            "lon": 77.6625,
            "category": "bus_stop",
            "aliases": ["old bus stand", "bhuteshwar bus stand", "upsrtc bus stand mathura", "isbt bhuteshwar", "purana bus adda"],
            "lines": ["Mathura-Vrindavan Electric Nagar Seva Bus", "Shared Tempo / Vikram (Braj Corridor)", "Shared E-Rickshaw Feeder (Toto)"]
        },
        {
            "name": "New Bus Stand (Masani Highway ISBT)",
            "lat": 27.5255,
            "lon": 77.6780,
            "category": "bus_stop",
            "aliases": ["new bus stand", "masani bus stand", "highway bus stand mathura", "upsrtc new isbt", "naya bus adda"],
            "lines": ["Mathura-Vrindavan Electric Nagar Seva Bus", "Shared Tempo / Vikram (Braj Corridor)"]
        },
        {
            "name": "Bhuteshwar Mahadev Mandir & Station",
            "lat": 27.5115,
            "lon": 77.6630,
            "category": "landmark",
            "aliases": ["bhuteshwar", "bhuteshwar mandir", "bhuteshwar station", "kankali road mathura"],
            "lines": ["Shared Tempo / Vikram (Braj Corridor)", "Shared E-Rickshaw Feeder (Toto)"]
        },
        {
            "name": "Goverdhan Chauraha (NH-19 Mathura Entry)",
            "lat": 27.4920,
            "lon": 77.6525,
            "category": "landmark",
            "aliases": ["goverdhan chauraha", "goverdhan chowk", "nh19 mathura entry", "highway auto stand mathura", "delhi agra highway mathura"],
            "lines": ["Shared Tempo / Vikram (Braj Corridor)", "Shared E-Rickshaw Feeder (Toto)", "Reserved Auto-Rickshaw (निजी ऑटो)"]
        },
        {
            "name": "Birla Temple (Gita Mandir)",
            "lat": 27.5350,
            "lon": 77.6815,
            "category": "landmark",
            "aliases": ["birla mandir mathura", "gita mandir", "mathura vrindavan road", "birla temple"],
            "lines": ["Mathura-Vrindavan Electric Nagar Seva Bus", "Shared Tempo / Vikram (Braj Corridor)", "Shared E-Rickshaw Feeder (Toto)"]
        },
        {
            "name": "Pagal Baba Mandir (Mathura-Vrindavan Marg)",
            "lat": 27.5518,
            "lon": 77.6845,
            "category": "landmark",
            "aliases": ["pagal baba", "pagal baba temple", "multi storey mandir", "pagal baba vrindavan road"],
            "lines": ["Mathura-Vrindavan Electric Nagar Seva Bus", "Shared Tempo / Vikram (Braj Corridor)", "Shared E-Rickshaw Feeder (Toto)"]
        },
        {
            "name": "Jai Gurudev Ashram (NH-19)",
            "lat": 27.4640,
            "lon": 77.6680,
            "category": "landmark",
            "aliases": ["jai gurudev", "jai gurudev temple", "gurudev ashram", "naam yog"],
            "lines": ["Shared Tempo / Vikram (Braj Corridor)", "Reserved Auto-Rickshaw (निजी ऑटो)"]
        },
        {
            "name": "Chatikara Road Junction (NH-19 Highway Cut)",
            "lat": 27.5685,
            "lon": 77.6355,
            "category": "landmark",
            "aliases": ["chatikara", "chhatikara morh", "nh19 vrindavan cut", "delhi agra highway vrindavan", "chatikara auto stand"],
            "lines": ["Mathura-Vrindavan Electric Nagar Seva Bus", "Shared Tempo / Vikram (Braj Corridor)", "Shared E-Rickshaw Feeder (Toto)"]
        },
        {
            "name": "Maa Vaishno Devi Dham (Chatikara Road)",
            "lat": 27.5710,
            "lon": 77.6430,
            "category": "landmark",
            "aliases": ["vaishno devi mandir vrindavan", "chatikara road vaishno dham", "maa vaishno devi temple"],
            "lines": ["Mathura-Vrindavan Electric Nagar Seva Bus", "Shared E-Rickshaw Feeder (Toto)"]
        },
        {
            "name": "Vrindavan Chandrodaya Mandir & Akshaya Patra",
            "lat": 27.5830,
            "lon": 77.6520,
            "category": "landmark",
            "aliases": ["chandrodaya mandir", "akshaya patra", "chandrodaya temple vrindavan", "sunrakh road"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Reserved Auto-Rickshaw (निजी ऑटो)"]
        },
        {
            "name": "Prem Mandir (Vrindavan)",
            "lat": 27.5724,
            "lon": 77.6710,
            "category": "landmark",
            "aliases": ["prem mandir", "kripalu parishat", "light show mandir vrindavan", "bhaktivedanta marg", "prem temple"],
            "lines": ["Mathura-Vrindavan Electric Nagar Seva Bus", "Shared Tempo / Vikram (Braj Corridor)", "Shared E-Rickshaw Feeder (Toto)", "Reserved Auto-Rickshaw (निजी ऑटो)"]
        },
        {
            "name": "ISKCON Temple (Krishna Balaram Mandir, Vrindavan)",
            "lat": 27.5729,
            "lon": 77.6755,
            "category": "landmark",
            "aliases": ["iskcon", "iskcon vrindavan", "krishna balaram mandir", "raman reti", "bhaktivedanta swami prabhupada samadhi"],
            "lines": ["Mathura-Vrindavan Electric Nagar Seva Bus", "Shared Tempo / Vikram (Braj Corridor)", "Shared E-Rickshaw Feeder (Toto)"]
        },
        {
            "name": "Shri Bankey Bihari Ji Mandir (Vrindavan)",
            "lat": 27.5816,
            "lon": 77.7011,
            "category": "landmark",
            "aliases": ["bankey bihari", "bihari ji", "banke bihari mandir", "jugal kishore", "kunj gali bihari ji", "vip gali vrindavan", "thakur ji"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Cycle Rickshaw & Kunj Gali Walk"]
        },
        {
            "name": "Nidhivan (Vrindavan)",
            "lat": 27.5818,
            "lon": 77.7042,
            "category": "landmark",
            "aliases": ["nidhivan", "nidhi van", "swami haridas samadhi", "raas sthal vrindavan", "pavitra van"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Cycle Rickshaw & Kunj Gali Walk"]
        },
        {
            "name": "Radha Raman Temple (Vrindavan)",
            "lat": 27.5847,
            "lon": 77.7032,
            "category": "landmark",
            "aliases": ["radha raman", "radharaman mandir", "gopal bhatta goswami", "ancient vrindavan temple"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Cycle Rickshaw & Kunj Gali Walk"]
        },
        {
            "name": "Radha Vallabh Temple (Vrindavan)",
            "lat": 27.5835,
            "lon": 77.7018,
            "category": "landmark",
            "aliases": ["radha vallabh", "radhavallabh mandir", "hit harivansh mahaprabhu"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Cycle Rickshaw & Kunj Gali Walk"]
        },
        {
            "name": "Shahji Temple (Vrindavan)",
            "lat": 27.5812,
            "lon": 77.7038,
            "category": "landmark",
            "aliases": ["shahji mandir", "tede khambe mandir", "marble temple vrindavan", "basanti kamra"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Cycle Rickshaw & Kunj Gali Walk"]
        },
        {
            "name": "Rangji Mandir (Shri Vaikuntha Nath Ji, Vrindavan)",
            "lat": 27.5802,
            "lon": 77.6975,
            "category": "landmark",
            "aliases": ["rangji temple", "rangnath mandir", "south indian temple vrindavan", "gopuram temple", "brahmotsav"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Shared Tempo / Vikram (Braj Corridor)"]
        },
        {
            "name": "Kesi Ghat & Yamuna Parikrama Marg (Vrindavan)",
            "lat": 27.5878,
            "lon": 77.7025,
            "category": "landmark",
            "aliases": ["kesi ghat", "keshi ghat", "vrindavan parikrama", "cheer ghat", "yamuna ji vrindavan"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Cycle Rickshaw & Kunj Gali Walk"]
        },
        {
            "name": "Vrindavan Railway Station / Gandhi Park",
            "lat": 27.5755,
            "lon": 77.6910,
            "category": "railway_station",
            "aliases": ["vrindavan station", "vrindavan rail", "gandhi park vrindavan", "attalla chungi vrindavan"],
            "lines": ["Mathura-Vrindavan Electric Nagar Seva Bus", "Shared Tempo / Vikram (Braj Corridor)", "Shared E-Rickshaw Feeder (Toto)"]
        },
        {
            "name": "GLA University (NH-19, Chaumuhan)",
            "lat": 27.6052,
            "lon": 77.5935,
            "category": "landmark",
            "aliases": ["gla university", "gla mathura", "chaumuhan", "gla campus"],
            "lines": ["Shared Tempo / Vikram (Braj Corridor)", "Reserved Auto-Rickshaw (निजी ऑटो)"]
        },
        {
            "name": "Govardhan - Daan Ghati Mandir & Mansi Ganga",
            "lat": 27.4985,
            "lon": 77.4645,
            "category": "landmark",
            "aliases": ["govardhan", "daan ghati", "mansi ganga", "giriraj ji", "parikrama marg govardhan", "goverdhan bus stand", "giriraj temple"],
            "lines": ["Shared Tempo / Vikram (Braj Corridor)", "Shared E-Rickshaw Feeder (Toto)", "Reserved Auto-Rickshaw (निजी ऑटो)"]
        },
        {
            "name": "Radha Kund & Shyam Kund",
            "lat": 27.5250,
            "lon": 77.4930,
            "category": "landmark",
            "aliases": ["radha kund", "shyam kund", "radhakund", "chaitanya mahaprabhu sthal"],
            "lines": ["Shared Tempo / Vikram (Braj Corridor)", "Shared E-Rickshaw Feeder (Toto)"]
        },
        {
            "name": "Jatipura - Mukharvind Mandir (Govardhan)",
            "lat": 27.4785,
            "lon": 77.4475,
            "category": "landmark",
            "aliases": ["jatipura", "mukharvind", "giriraj mukharvind", "poochhari ka lauta"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Reserved Auto-Rickshaw (निजी ऑटो)"]
        },
        {
            "name": "Barsana - Shri Radha Rani Mandir (Ladli Ji)",
            "lat": 27.6495,
            "lon": 77.3755,
            "category": "landmark",
            "aliases": ["barsana", "radha rani mandir", "ladli ji", "rangeeli mahal", "bhanugarh", "lathmar holi sthal", "barsana temple"],
            "lines": ["Shared Tempo / Vikram (Braj Corridor)", "Shared E-Rickshaw Feeder (Toto)", "Reserved Auto-Rickshaw (निजी ऑटो)"]
        },
        {
            "name": "Nandgaon - Nand Bhavan",
            "lat": 27.7125,
            "lon": 77.3885,
            "category": "landmark",
            "aliases": ["nandgaon", "nand bhavan", "nand baba mandir", "panchajanya"],
            "lines": ["Shared Tempo / Vikram (Braj Corridor)", "Reserved Auto-Rickshaw (निजी ऑटो)"]
        },
        {
            "name": "Gokul - Raman Reti & Chaurasi Khamba",
            "lat": 27.4410,
            "lon": 77.7180,
            "category": "landmark",
            "aliases": ["gokul", "raman reti gokul", "chaurasi khamba", "mahavaan", "baldeo road gokul", "gokul dham"],
            "lines": ["Shared Tempo / Vikram (Braj Corridor)", "Shared E-Rickshaw Feeder (Toto)", "Reserved Auto-Rickshaw (निजी ऑटो)"]
        },
        {
            "name": "Baldeo - Shri Dauji Maharaj Mandir",
            "lat": 27.4105,
            "lon": 77.8185,
            "category": "landmark",
            "aliases": ["baldeo", "dauji mandir", "balram ji", "kshir sagar baldeo", "dau ji temple"],
            "lines": ["Shared Tempo / Vikram (Braj Corridor)", "Reserved Auto-Rickshaw (निजी ऑटो)"]
        },
        {
            "name": "Mathura IOCL Refinery & Township (Baad)",
            "lat": 27.4120,
            "lon": 77.6890,
            "category": "landmark",
            "aliases": ["mathura refinery", "iocl refinery", "baad station", "refinery township", "delhi agra bypass mathura"],
            "lines": ["Shared Tempo / Vikram (Braj Corridor)", "Reserved Auto-Rickshaw (निजी ऑटो)"]
        }
    ]
}

# ==============================================================================
# Transit Operating Hours (24h format)
# DMRC Metro: First train ~6:00 AM, Last train ~11:00 PM (last entry ~11:30 PM)
# DTC Buses: Most routes 5:00 AM – 11:30 PM; Night Service (limited) 11 PM – 5 AM
# Airport Express: 4:45 AM – 11:40 PM
# ==============================================================================
TRANSIT_OPERATING_HOURS: Dict[str, Dict[str, Any]] = {
    "dmrc_metro": {
        "first_service_hour": 6,    # 6:00 AM
        "first_service_minute": 0,
        "last_entry_hour": 23,      # 11:00 PM (last metro departs ~11:00-11:15 PM)
        "last_entry_minute": 0,
        "label": "DMRC Metro",
        "closed_message": "Metro service closed (11 PM – 6 AM). Last train has departed.",
    },
    "airport_express": {
        "first_service_hour": 4,
        "first_service_minute": 45,
        "last_entry_hour": 23,
        "last_entry_minute": 40,
        "label": "Airport Express Line",
        "closed_message": "Airport Express closed. Last service at 11:40 PM.",
    },
    "dtc_bus": {
        "first_service_hour": 5,
        "first_service_minute": 0,
        "last_entry_hour": 23,
        "last_entry_minute": 30,
        "label": "DTC Bus",
        "closed_message": "Regular DTC bus service ended (11:30 PM – 5 AM). Limited night service on select routes.",
        "has_night_service": True,  # Limited night service exists
    },
    "mathura_ebus": {
        "first_service_hour": 6,
        "first_service_minute": 0,
        "last_entry_hour": 21,
        "last_entry_minute": 30,
        "label": "Mathura-Vrindavan Electric Nagar Seva Bus",
        "closed_message": "Mathura-Vrindavan Electric Bus service ended (9:30 PM – 6 AM). Use 24/7 Station Auto or Shared Tempo.",
    },
    "mathura_shared_tempo": {
        "first_service_hour": 5,
        "first_service_minute": 0,
        "last_entry_hour": 22,
        "last_entry_minute": 30,
        "label": "Shared Tempo / Vikram (Braj Corridor)",
        "closed_message": "Regular Shared Tempo corridor service closed for night (10:30 PM – 5 AM). Reserved Auto available.",
    },
    "mathura_erickshaw": {
        "first_service_hour": 5,
        "first_service_minute": 30,
        "last_entry_hour": 23,
        "last_entry_minute": 0,
        "label": "Shared E-Rickshaw Feeder (Toto)",
        "closed_message": "Local E-Rickshaw frequency reduced for night. Available near Mathura Junction 24/7.",
    },
}


def is_transit_operational(service_key: str, current_hour: int, current_minute: int) -> bool:
    """Check if a transit service is currently operational based on operating hours."""
    hours = TRANSIT_OPERATING_HOURS.get(service_key)
    if not hours:
        return True  # Default to available if no schedule defined (auto, cab, etc.)

    first_h, first_m = hours["first_service_hour"], hours["first_service_minute"]
    last_h, last_m = hours["last_entry_hour"], hours["last_entry_minute"]

    current_total = current_hour * 60 + current_minute
    first_total = first_h * 60 + first_m
    last_total = last_h * 60 + last_m

    return first_total <= current_total <= last_total


def get_closed_message(service_key: str) -> str:
    """Get the user-facing closed message for a transit service."""
    hours = TRANSIT_OPERATING_HOURS.get(service_key)
    if hours:
        return hours["closed_message"]
    return "Service currently unavailable."


# Line colors & standard operating info
TRANSIT_LINES: Dict[str, Dict[str, Any]] = {
    "Yellow Line": {
        "color": "#E5A919",
        "mode": "metro",
        "fare_type": "dmrc",
        "avg_speed_kmh": 34,
        "operator": "Delhi Metro Rail Corporation",
        "service_key": "dmrc_metro"
    },
    "Blue Line": {
        "color": "#1976D2",
        "mode": "metro",
        "fare_type": "dmrc",
        "avg_speed_kmh": 34,
        "operator": "Delhi Metro Rail Corporation",
        "service_key": "dmrc_metro"
    },
    "Magenta Line": {
        "color": "#C2185B",
        "mode": "metro",
        "fare_type": "dmrc",
        "avg_speed_kmh": 38,
        "operator": "Delhi Metro Rail Corporation",
        "service_key": "dmrc_metro"
    },
    "Violet Line": {
        "color": "#7B1FA2",
        "mode": "metro",
        "fare_type": "dmrc",
        "avg_speed_kmh": 32,
        "operator": "Delhi Metro Rail Corporation",
        "service_key": "dmrc_metro"
    },
    "Airport Express": {
        "color": "#FF6F00",
        "mode": "metro",
        "fare_type": "airport_express",
        "avg_speed_kmh": 80,
        "operator": "Delhi Airport Metro Express",
        "service_key": "airport_express"
    },
    "Rapid Metro Gurugram": {
        "color": "#43A047",
        "mode": "metro",
        "fare_type": "rapid_metro",
        "avg_speed_kmh": 30,
        "operator": "DMRC / Rapid Metro",
        "service_key": "dmrc_metro"
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
    },
    "Mathura-Vrindavan Electric Nagar Seva Bus": {
        "color": "#00A86B",
        "mode": "ebus",
        "fare_type": "upsrtc_ebus",
        "avg_speed_kmh": 24,
        "operator": "Directorate of Urban Transport UP (Mathura-Vrindavan)",
        "service_key": "mathura_ebus"
    },
    "Shared Tempo / Vikram (Braj Corridor)": {
        "color": "#E68A00",
        "mode": "auto",
        "fare_type": "shared_tempo",
        "avg_speed_kmh": 28,
        "operator": "Mathura-Vrindavan Auto Union (Fixed Corridor)",
        "service_key": "mathura_shared_tempo"
    },
    "Shared E-Rickshaw Feeder (Toto)": {
        "color": "#00897B",
        "mode": "erickshaw",
        "fare_type": "mathura_erickshaw",
        "avg_speed_kmh": 16,
        "operator": "Mathura-Vrindavan E-Rickshaw Commuter Fleet",
        "service_key": "mathura_erickshaw"
    },
    "Reserved Auto-Rickshaw (निजी ऑटो)": {
        "color": "#D97706",
        "mode": "auto",
        "fare_type": "mathura_reserved_auto",
        "avg_speed_kmh": 28,
        "operator": "Mathura Local Pre-paid / Negotiated Auto",
        "service_key": "reserved_auto"
    },
    "Private Tourist Taxi (मथुरा टूरिस्ट टैक्सी)": {
        "color": "#475569",
        "mode": "taxi",
        "fare_type": "tourist_taxi",
        "avg_speed_kmh": 32,
        "operator": "Mathura-Vrindavan Tourist Agency Cabs",
        "service_key": "taxi"
    },
    "Yamuna Braj Heritage Cycle Rickshaw": {
        "color": "#8D6E63",
        "mode": "walk",
        "fare_type": "cycle_rickshaw",
        "avg_speed_kmh": 10,
        "operator": "Braj Heritage Kunj Gali Rickshaw Pullers",
        "service_key": "cycle_rickshaw"
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
    """
    Calculates official Delhi Government regulated metered TSR Auto-Rickshaw fare
    strictly as per Delhi Gazette Notification F. No. 23(488)/TPT/ARU/2010/452/4673 dated 09.01.2023:
    - ₹30.00 for first 1.5 km (upon downing meter)
    - ₹11.00 per km for every additional km thereafter
    - Night Charges: 25% of fare (11.00 PM to 05.00 AM)
    - Waiting Charges: ₹0.75 per minute for slow moving/jam (<1 km in 10 mins)
    """
    base_km = 1.5
    base_fare = 30.0
    per_km = 11.0
    
    if dist_km <= base_km:
        fare = base_fare
    else:
        fare = base_fare + (dist_km - base_km) * per_km
        
    if is_night:
        fare *= 1.25
        night_str = " (incl. 25% GNCTD Night Surcharge 11PM-5AM)"
    else:
        night_str = ""
        
    rounded_fare = round(fare, 1)
    return float(rounded_fare), f"GNCTD Gazetted Meter: ₹{base_fare:.0f} (first 1.5km) + ₹{per_km:.0f}/km{night_str} (ARU Burari Notification)"


def calculate_delhi_taxi_fare(dist_km: float, is_ac: bool = True, is_night: bool = False):
    """
    Calculates official Delhi Gazette regulated Black & Yellow Top Taxi (Pili Chhat) fare:
    - Base Fare: ₹40.00 for first 1.0 km
    - Non-AC: ₹17.00 per km | AC: ₹20.00 per km
    - Night Charges: 25% (11.00 PM to 05.00 AM)
    """
    base_km = 1.0
    base_fare = 40.0
    per_km = 20.0 if is_ac else 17.0
    
    if dist_km <= base_km:
        fare = base_fare
    else:
        fare = base_fare + (dist_km - base_km) * per_km
        
    if is_night:
        fare *= 1.25
        night_str = " (incl. 25% Night Surcharge)"
    else:
        night_str = ""
        
    rounded_fare = round(fare, 1)
    tag_name = "AC Taxi" if is_ac else "Non-AC Taxi"
    return float(rounded_fare), f"Delhi Govt Taxi Meter ({tag_name}): ₹{base_fare:.0f} (first 1km) + ₹{per_km:.0f}/km{night_str}"

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


# ==============================================================================
# Mathura & Vrindavan Local Transit Regimes & Fare Calculations
# ==============================================================================

def calculate_mathura_erickshaw_fare(dist_km: float):
    """
    Shared E-Rickshaw (Toto / Battery Rickshaw) fare in Mathura & Vrindavan.
    The primary transit lifeline inside Vrindavan and Mathura city lanes.
    Standard market rate:
    - 0 to 2.2 km (Short hop, e.g. Prem Mandir to ISKCON, Holi Gate to Dwarkadhish): Flat ₹10
    - 2.2 to 4.5 km (Standard hop, e.g. Chatikara to Prem Mandir, Mathura Jn to Janmasthan): ₹15
    - 4.5 to 8 km (Extended hop): ₹20
    """
    if dist_km <= 2.2:
        return 10.0, "Shared E-Rickshaw (Toto): Flat ₹10 (Short hop)"
    elif dist_km <= 4.8:
        return 15.0, "Shared E-Rickshaw (Toto): ₹15 (Standard hop)"
    else:
        return 20.0, "Shared E-Rickshaw (Toto): ₹20 (Extended hop)"


def calculate_mathura_shared_tempo_fare(dist_km: float):
    """
    Shared CNG Auto / Tempo / Vikram fare in Mathura-Vrindavan.
    Fixed per-passenger tariff for major Braj transport corridors:
    - 0 to 4 km (Intra-city): ₹15
    - 4 to 10 km (Inter-chauraha): ₹25
    - 10 to 18 km (Mathura Jn ⇄ Vrindavan Attalla Chungi / Gandhi Park / Chatikara): ₹35
    - 18 to 28 km (Mathura ⇄ Govardhan / Gokul): ₹45
    - 28 to 45 km (Mathura / Govardhan ⇄ Barsana / Nandgaon): ₹60
    """
    if dist_km <= 4.0:
        return 15.0, "Shared Tempo / Vikram: ₹15 (Local Mathura/Vrindavan corridor)"
    elif dist_km <= 10.0:
        return 25.0, "Shared Tempo / Vikram: ₹25 (Inter-hub feeder)"
    elif dist_km <= 18.0:
        return 35.0, "Shared Tempo / Vikram: ₹35 (Mathura Jn ⇄ Vrindavan Attalla / Gandhi Park)"
    elif dist_km <= 28.0:
        return 45.0, "Shared Tempo / Vikram: ₹45 (Mathura ⇄ Govardhan / Gokul)"
    else:
        return 60.0, "Shared Tempo / Vikram: ₹60 (Mathura / Govardhan ⇄ Barsana / Nandgaon)"


def calculate_mathura_ebus_fare(dist_km: float):
    """
    Official UP Urban Transport Directorate Electric AC City Bus Fare Slabs (Mathura-Vrindavan City EV Bus).
    100% Zero-Emission fleet protecting the Taj Trapezium & Braj heritage zone.
    Slabs:
    0-3 km: ₹10 | 3-6 km: ₹15 | 6-10 km: ₹20 | 10-14 km: ₹25 | 14-19 km: ₹30 | 19-25 km: ₹35 | >25 km: ₹40
    """
    if dist_km <= 3.0:
        return 10.0, "Mathura-Vrindavan Electric Bus (UP Urban Transport): ₹10 (0-3 km)"
    elif dist_km <= 6.0:
        return 15.0, "Mathura-Vrindavan Electric Bus (UP Urban Transport): ₹15 (3-6 km)"
    elif dist_km <= 10.0:
        return 20.0, "Mathura-Vrindavan Electric Bus (UP Urban Transport): ₹20 (6-10 km)"
    elif dist_km <= 14.0:
        return 25.0, "Mathura-Vrindavan Electric Bus (UP Urban Transport): ₹25 (10-14 km)"
    elif dist_km <= 19.0:
        return 30.0, "Mathura-Vrindavan Electric Bus (UP Urban Transport): ₹30 (14-19 km)"
    elif dist_km <= 25.0:
        return 35.0, "Mathura-Vrindavan Electric Bus (UP Urban Transport): ₹35 (19-25 km)"
    else:
        return 40.0, "Mathura-Vrindavan Electric Bus (UP Urban Transport): ₹40 (>25 km)"


def calculate_mathura_reserved_auto_fare(dist_km: float, is_night: bool = False):
    """
    Reserved (Private Full-Booking) Auto-Rickshaw fare in Mathura / Vrindavan.
    Base fare: ₹50 (first 1.5 km), ₹14/km thereafter.
    Benchmark rates:
    - Mathura Jn to Janmasthan / Dwarkadhish: ~₹80-₹120
    - Mathura Jn to Vrindavan Prem Mandir / ISKCON: ~₹220-₹260
    - Mathura Jn to Bankey Bihari: ~₹240-₹280
    - Mathura to Govardhan: ~₹380-₹450
    - Mathura to Barsana: ~₹550-₹650
    """
    base_km = 1.5
    base_fare = 50.0
    per_km = 14.0
    if dist_km <= base_km:
        fare = base_fare
    else:
        fare = base_fare + (dist_km - base_km) * per_km

    if is_night:
        fare *= 1.20
        night_str = " (incl. 20% late night rate 10PM-5AM)"
    else:
        night_str = ""

    rounded = round(fare / 10) * 10
    final_fare = float(max(60.0, rounded))
    return final_fare, f"Reserved Auto (Full Booking): ~₹{final_fare:.0f}{night_str}"


def calculate_mathura_taxi_fare(dist_km: float):
    """
    Private Tour Taxi / Travel Agency Car tariff in Mathura-Vrindavan.
    Note: On-demand app cabs (Ola/Uber) have very scarce local fleet in Mathura.
    """
    fare = 250.0 + max(0, dist_km - 3.0) * 18.0
    rounded = round(fare / 10) * 10
    return float(rounded), f"Private Tour Taxi (Limited App Cabs): ~₹{rounded:.0f}"


