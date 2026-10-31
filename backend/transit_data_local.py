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
        },
        {
            "name": "Lajpat Nagar 1 (Krishna Market & Block A-O)",
            "lat": 28.572,
            "lon": 77.2385,
            "category": "residential_block",
            "aliases": ["lajpat nagar 1", "lajpat nagar i", "krishna market", "block a lajpat nagar 1", "lajpat 1"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Pink Line", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": True,
            "nearest_metro": "Lajpat Nagar",
            "metro_dist_km": 0.4
        },
        {
            "name": "Lajpat Nagar 2 (Central Market & Block B-K)",
            "lat": 28.5695,
            "lon": 77.242,
            "category": "market",
            "aliases": ["lajpat nagar 2", "lajpat nagar ii", "central market lajpat nagar", "central market", "lajpat 2"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Pink Line", "Violet Line"],
            "has_direct_metro": True,
            "nearest_metro": "Lajpat Nagar",
            "metro_dist_km": 0.3
        },
        {
            "name": "Lajpat Nagar 3 (Ring Road & Feroze Gandhi Road)",
            "lat": 28.566,
            "lon": 77.2405,
            "category": "residential_block",
            "aliases": ["lajpat nagar 3", "lajpat nagar iii", "feroze gandhi road", "block c lajpat nagar 3", "lajpat 3"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "DTC Bus 534"],
            "has_direct_metro": False,
            "nearest_metro": "Lajpat Nagar",
            "metro_dist_km": 0.8
        },
        {
            "name": "Lajpat Nagar 4 (Dayanand Colony & National Park)",
            "lat": 28.558,
            "lon": 77.2415,
            "category": "residential_block",
            "aliases": ["lajpat nagar 4", "lajpat nagar iv", "dayanand colony", "national park lajpat nagar", "lajpat 4"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": False,
            "nearest_metro": "Moolchand",
            "metro_dist_km": 0.9
        },
        {
            "name": "Amar Colony (Lajpat Nagar IV)",
            "lat": 28.557,
            "lon": 77.2435,
            "category": "locality",
            "aliases": ["amar colony", "amar colony market", "amar colony furniture", "amar colony street food", "dayanand colony market"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": False,
            "nearest_metro": "Moolchand",
            "metro_dist_km": 1.1
        },
        {
            "name": "Defence Colony (Blocks A, B, C & Flyover Market)",
            "lat": 28.5735,
            "lon": 77.231,
            "category": "residential_block",
            "aliases": ["defence colony", "def col", "def col market", "defence colony main market", "block a defence colony", "block c def col"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Violet Line"],
            "has_direct_metro": False,
            "nearest_metro": "Lajpat Nagar",
            "metro_dist_km": 0.9
        },
        {
            "name": "South Extension Part 1 (South Ex 1 - Blocks A-G)",
            "lat": 28.5685,
            "lon": 77.2215,
            "category": "market",
            "aliases": ["south extension 1", "south ex 1", "south ex part 1", "f block south ex 1", "south ex market"],
            "lines": ["Pink Line (South Extension)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "South Extension",
            "metro_dist_km": 0.2
        },
        {
            "name": "South Extension Part 2 (South Ex 2 - Blocks A-E)",
            "lat": 28.562,
            "lon": 77.2235,
            "category": "residential_block",
            "aliases": ["south extension 2", "south ex 2", "south ex part 2", "masjid moth south ex", "leela galleria"],
            "lines": ["Pink Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "South Extension",
            "metro_dist_km": 0.7
        },
        {
            "name": "Greater Kailash 1 (GK-1 - M Block & N Block Market)",
            "lat": 28.5525,
            "lon": 77.2395,
            "category": "residential_block",
            "aliases": ["greater kailash 1", "gk 1", "gk1", "m block market gk1", "n block market gk 1", "greater kailash part 1"],
            "lines": ["Magenta Line (Greater Kailash)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Greater Kailash",
            "metro_dist_km": 0.5
        },
        {
            "name": "Greater Kailash 2 (GK-2 - M Block Market & Savitri)",
            "lat": 28.5345,
            "lon": 77.2425,
            "category": "residential_block",
            "aliases": ["greater kailash 2", "gk 2", "gk2", "m block market gk2", "savitri cinema", "greater kailash part 2", "jahanpanah city forest"],
            "lines": ["Magenta Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Greater Kailash",
            "metro_dist_km": 1.4
        },
        {
            "name": "Chittaranjan Park (CR Park - Markets 1, 2, 3, 4)",
            "lat": 28.5385,
            "lon": 77.2515,
            "category": "locality",
            "aliases": ["cr park", "chittaranjan park", "market 1 cr park", "market 2 cr park", "b block cr park", "kali mandir cr park"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": False,
            "nearest_metro": "Nehru Enclave",
            "metro_dist_km": 1.1
        },
        {
            "name": "Kalkaji (Blocks A-M & Kalkaji Main Market)",
            "lat": 28.544,
            "lon": 77.258,
            "category": "residential_block",
            "aliases": ["kalkaji", "kalkaji main market", "block a kalkaji", "deshbandhu college", "dda flats kalkaji", "kalkaji extension"],
            "lines": ["Violet Line", "Magenta Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Kalkaji Mandir",
            "metro_dist_km": 0.6
        },
        {
            "name": "Govindpuri (Gali 1-13 & Govindpuri Extension)",
            "lat": 28.5365,
            "lon": 77.2625,
            "category": "locality",
            "aliases": ["govindpuri", "govindpuri extension", "gali no 1 govindpuri", "govindpuri gali", "transit camp govindpuri"],
            "lines": ["Violet Line (Govindpuri)", "Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Govindpuri",
            "metro_dist_km": 0.3
        },
        {
            "name": "Alaknanda (Tara Apartments & Nilgiri)",
            "lat": 28.5295,
            "lon": 77.249,
            "category": "residential_block",
            "aliases": ["alaknanda", "tara apartments", "nilgiri apartments", "mandakini enclave", "narmada alaknanda", "dda sfs alaknanda"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": False,
            "nearest_metro": "Greater Kailash",
            "metro_dist_km": 1.5
        },
        {
            "name": "Shahpur Jat (Fashion Village & Siri Fort)",
            "lat": 28.548,
            "lon": 77.2185,
            "category": "village",
            "aliases": ["shahpur jat", "shahpur jat fashion street", "asiad village", "siri fort complex", "shahpur jat cafes"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Hauz Khas",
            "metro_dist_km": 1.2
        },
        {
            "name": "Hauz Khas Village (HKV & Deer Park)",
            "lat": 28.5535,
            "lon": 77.1945,
            "category": "village",
            "aliases": ["hauz khas village", "hkv", "deer park", "hauz khas fort", "hauz khas lake", "hkv cafes"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": False,
            "nearest_metro": "Green Park",
            "metro_dist_km": 1.3
        },
        {
            "name": "Khirki Village & Khirki Extension",
            "lat": 28.531,
            "lon": 77.218,
            "category": "village",
            "aliases": ["khirki village", "khirki extension", "khirki gaon", "khirki masjid", "khirki more"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Malviya Nagar",
            "metro_dist_km": 0.9
        },
        {
            "name": "Malviya Nagar (Main Market & Corner Market)",
            "lat": 28.536,
            "lon": 77.2085,
            "category": "market",
            "aliases": ["malviya nagar", "malviya nagar main market", "corner market malviya nagar", "geeta bhawan", "shivalik malviya nagar"],
            "lines": ["Yellow Line (Malviya Nagar)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Malviya Nagar",
            "metro_dist_km": 0.4
        },
        {
            "name": "Saket (J-Block, Press Enclave & PVR Anupam)",
            "lat": 28.5225,
            "lon": 77.214,
            "category": "residential_block",
            "aliases": ["saket", "saket j block", "pvr anupam", "press enclave", "saket district centre", "select citywalk", "dlf avenue saket"],
            "lines": ["Yellow Line (Saket)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Saket",
            "metro_dist_km": 0.5
        },
        {
            "name": "Sainik Farm (Western Avenue & Country Club)",
            "lat": 28.5065,
            "lon": 77.2055,
            "category": "locality",
            "aliases": ["sainik farm", "sainik farms", "western avenue", "country club sainik farm", "central avenue sainik farm", "lane 1 sainik farm"],
            "lines": ["Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Saket",
            "metro_dist_km": 2.2
        },
        {
            "name": "Neb Sarai & IGNOU Road",
            "lat": 28.508,
            "lon": 77.2005,
            "category": "village",
            "aliases": ["neb sarai", "ignou road", "neb sarai village", "harijan basti neb sarai", "freedom fighter enclave"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Saket",
            "metro_dist_km": 1.8
        },
        {
            "name": "Maidangarhi & IGNOU Campus",
            "lat": 28.498,
            "lon": 77.208,
            "category": "village",
            "aliases": ["maidangarhi", "maidan garhi", "ignou campus", "ignou headquarters", "maidan garhi gaon"],
            "lines": ["DTC Bus 427", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Chhatarpur",
            "metro_dist_km": 2.5
        },
        {
            "name": "Chhatarpur Enclave (100 Feet Road & Phase 1-2)",
            "lat": 28.501,
            "lon": 77.1775,
            "category": "locality",
            "aliases": ["chhatarpur enclave", "100 feet road chhatarpur", "chhatarpur phase 1", "chhatarpur phase 2", "chhatarpur mandir road"],
            "lines": ["Yellow Line (Chhatarpur)", "Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Chhatarpur",
            "metro_dist_km": 0.8
        },
        {
            "name": "Sultanpur Village & MG Road Furniture Market",
            "lat": 28.494,
            "lon": 77.161,
            "category": "village",
            "aliases": ["sultanpur", "sultanpur village", "sultanpur mg road", "sultanpur furniture market", "sultanpur depot"],
            "lines": ["Yellow Line (Sultanpur)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Sultanpur",
            "metro_dist_km": 0.2
        },
        {
            "name": "Ghitorni Village (MG Road Corridor)",
            "lat": 28.486,
            "lon": 77.148,
            "category": "village",
            "aliases": ["ghitorni", "ghitorni village", "metro pillar 130 ghitorni", "ghitorni market", "ghitorni interior corridor"],
            "lines": ["Yellow Line (Ghitorni)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Ghitorni",
            "metro_dist_km": 0.2
        },
        {
            "name": "Aya Nagar (Arjan Garh Border & Extension)",
            "lat": 28.477,
            "lon": 77.135,
            "category": "village",
            "aliases": ["aya nagar", "arjan garh", "aya nagar extension", "aya nagar border", "air force station arjan garh"],
            "lines": ["Yellow Line (Arjan Garh)", "Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Arjan Garh",
            "metro_dist_km": 0.3
        },
        {
            "name": "Fatehpur Beri & Asola",
            "lat": 28.468,
            "lon": 77.175,
            "category": "village",
            "aliases": ["fatehpur beri", "asola", "asola bhati sanctuary", "fatehpur beri gaon", "dera mandi road"],
            "lines": ["DTC Bus 519", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Chhatarpur",
            "metro_dist_km": 4.5
        },
        {
            "name": "Bhati Mines (Sanjay Colony)",
            "lat": 28.448,
            "lon": 77.185,
            "category": "village",
            "aliases": ["bhati mines", "sanjay colony bhati mines", "bhati gaon", "radha soami satsang bhati"],
            "lines": ["DTC Bus 519", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Chhatarpur",
            "metro_dist_km": 6.8
        },
        {
            "name": "Mehrauli (Village, Ward 1-8 & 100 Foota Road)",
            "lat": 28.518,
            "lon": 77.182,
            "category": "town",
            "aliases": ["mehrauli", "mehrauli village", "bhool bhulaiya", "ward 1 mehrauli", "100 foota road mehrauli", "dada bari mehrauli", "jamali kamali"],
            "lines": ["Yellow Line (Qutab Minar)", "Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": True,
            "nearest_metro": "Qutab Minar",
            "metro_dist_km": 0.8
        },
        {
            "name": "Sangam Vihar (Blocks A to L & Ratia Marg)",
            "lat": 28.502,
            "lon": 77.242,
            "category": "residential_block",
            "aliases": ["sangam vihar", "ratia marg sangam vihar", "block a sangam vihar", "block g sangam vihar", "bandh road sangam vihar", "sangam vihar bus terminal"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "DTC Bus 469", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Saket",
            "metro_dist_km": 3.2
        },
        {
            "name": "Deoli & Durga Vihar",
            "lat": 28.498,
            "lon": 77.228,
            "category": "village",
            "aliases": ["deoli", "deoli gaon", "durga vihar", "deoli more", "deoli extension"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Saket",
            "metro_dist_km": 2.8
        },
        {
            "name": "Madangir & Pushp Vihar (Sectors 1-7)",
            "lat": 28.526,
            "lon": 77.226,
            "category": "residential_block",
            "aliases": ["madangir", "pushp vihar", "pushp vihar sector 1", "central market madangir", "saket district court pushp vihar"],
            "lines": ["DTC Bus 522", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Saket",
            "metro_dist_km": 1.4
        },
        {
            "name": "Khanpur (Extension & Ambedkar Nagar Depot)",
            "lat": 28.514,
            "lon": 77.234,
            "category": "locality",
            "aliases": ["khanpur", "khanpur extension", "ambedkar nagar depot", "khanpur t point", "tigri road"],
            "lines": ["DTC Bus 534", "Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": False,
            "nearest_metro": "Saket",
            "metro_dist_km": 2.0
        },
        {
            "name": "Badarpur (Border & Tajpur Pahari)",
            "lat": 28.502,
            "lon": 77.302,
            "category": "town",
            "aliases": ["badarpur", "badarpur border", "badarpur flyover", "tajpur pahari", "molarband extension", "mehrauli badarpur road"],
            "lines": ["Violet Line (Badarpur Border)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Badarpur Border",
            "metro_dist_km": 0.3
        },
        {
            "name": "Jaitpur & Saurabh Vihar",
            "lat": 28.512,
            "lon": 77.321,
            "category": "locality",
            "aliases": ["jaitpur", "jaitpur part 1", "jaitpur part 2", "saurabh vihar", "khadda colony jaitpur"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Badarpur Border",
            "metro_dist_km": 2.4
        },
        {
            "name": "Mithapur & Prahladpur Bangar",
            "lat": 28.492,
            "lon": 77.318,
            "category": "village",
            "aliases": ["mithapur", "mithapur chowk", "prahladpur bangar", "mithapur extension"],
            "lines": ["Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Badarpur Border",
            "metro_dist_km": 2.1
        },
        {
            "name": "Okhla Phase 1 (Industrial Area & Crown Plaza)",
            "lat": 28.528,
            "lon": 77.279,
            "category": "industrial_area",
            "aliases": ["okhla phase 1", "okhla industrial area phase 1", "crown plaza okhla", "dd motors okhla", "okhla factory zone"],
            "lines": ["Violet Line (Harkesh Nagar Okhla)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Harkesh Nagar Okhla",
            "metro_dist_km": 0.6
        },
        {
            "name": "Okhla Phase 2 (Industrial Area & Sanjay Colony)",
            "lat": 28.523,
            "lon": 77.271,
            "category": "industrial_area",
            "aliases": ["okhla phase 2", "okhla industrial area phase 2", "sanjay colony okhla", "okhla more"],
            "lines": ["Violet Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Harkesh Nagar Okhla",
            "metro_dist_km": 1.1
        },
        {
            "name": "Okhla Phase 3 (NSIC Okhla & Modi Flour Mills)",
            "lat": 28.548,
            "lon": 77.271,
            "category": "industrial_area",
            "aliases": ["okhla phase 3", "nsic okhla", "modi mill flyover", "okhla estate", "lotus temple okhla"],
            "lines": ["Magenta Line (NSIC Okhla)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "NSIC Okhla",
            "metro_dist_km": 0.3
        },
        {
            "name": "Batla House & Zakir Nagar (Jamia)",
            "lat": 28.561,
            "lon": 77.288,
            "category": "locality",
            "aliases": ["batla house", "zakir nagar", "batla house chowk", "jamia nagar police station", "goga market batla house"],
            "lines": ["Magenta Line (Jamia Millia Islamia)", "Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Jamia Millia Islamia",
            "metro_dist_km": 0.6
        },
        {
            "name": "Shaheen Bagh (40 Feet Road & Thokar 3-8)",
            "lat": 28.544,
            "lon": 77.302,
            "category": "locality",
            "aliases": ["shaheen bagh", "40 feet road shaheen bagh", "thokar 4 shaheen bagh", "thokar 8 shaheen bagh", "high tension road shaheen bagh"],
            "lines": ["Magenta Line (Shaheen Bagh / Jasola Vihar)", "Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Jasola Vihar Shaheen Bagh",
            "metro_dist_km": 0.5
        },
        {
            "name": "Abul Fazal Enclave (Part 1 & 2)",
            "lat": 28.549,
            "lon": 77.308,
            "category": "residential_block",
            "aliases": ["abul fazal enclave", "afe", "abul fazal part 1", "abul fazal part 2", "thokar 7 abul fazal"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Jasola Vihar Shaheen Bagh",
            "metro_dist_km": 1.2
        },
        {
            "name": "Jasola Vihar & Jasola District Centre",
            "lat": 28.539,
            "lon": 77.291,
            "category": "residential_block",
            "aliases": ["jasola", "jasola vihar", "jasola district centre", "living style mall jasola", "apollo hospital jasola"],
            "lines": ["Violet Line (Jasola Apollo)", "Magenta Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Jasola Apollo",
            "metro_dist_km": 0.4
        },
        {
            "name": "Sarita Vihar (Pockets A to L)",
            "lat": 28.528,
            "lon": 77.299,
            "category": "residential_block",
            "aliases": ["sarita vihar", "pocket a sarita vihar", "pocket b sarita vihar", "pocket c sarita vihar", "sarita vihar main market"],
            "lines": ["Violet Line (Sarita Vihar)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Sarita Vihar",
            "metro_dist_km": 0.4
        },
        {
            "name": "Madanpur Khadar (Village & Extension)",
            "lat": 28.519,
            "lon": 77.315,
            "category": "village",
            "aliases": ["madanpur khadar", "madanpur khadar extension", "jj colony madanpur khadar", "madanpur gaon"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Sarita Vihar",
            "metro_dist_km": 2.2
        },
        {
            "name": "Tughlakabad Fort & Extension (TKD)",
            "lat": 28.514,
            "lon": 77.261,
            "category": "village",
            "aliases": ["tughlakabad", "tughlakabad fort", "tughlakabad extension", "tkd village", "container depot tughlakabad"],
            "lines": ["Violet Line (Tughlakabad)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Tughlakabad",
            "metro_dist_km": 0.7
        },
        {
            "name": "Vasant Vihar (Blocks A to E & Priya Cinema)",
            "lat": 28.558,
            "lon": 77.159,
            "category": "residential_block",
            "aliases": ["vasant vihar", "priya cinema", "basant lok", "block a vasant vihar", "block c vasant vihar", "paschimi marg vasant vihar", "poorvi marg"],
            "lines": ["Magenta Line (Vasant Vihar)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Vasant Vihar",
            "metro_dist_km": 0.3
        },
        {
            "name": "Vasant Kunj Sector A (Pocket B & C)",
            "lat": 28.528,
            "lon": 77.161,
            "category": "residential_block",
            "aliases": ["vasant kunj sector a", "sector a vasant kunj", "pocket b sector a", "pocket c sector a vasant kunj"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "DTC Bus 604"],
            "has_direct_metro": False,
            "nearest_metro": "Chhatarpur",
            "metro_dist_km": 2.4
        },
        {
            "name": "Vasant Kunj Sector B (Pockets 1-11 & Fortis Hospital)",
            "lat": 28.523,
            "lon": 77.153,
            "category": "residential_block",
            "aliases": ["vasant kunj sector b", "sector b vasant kunj", "fortis vasant kunj", "pocket 1 sector b vasant kunj", "pocket 7 sector b"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "DTC Bus 604"],
            "has_direct_metro": False,
            "nearest_metro": "Chhatarpur",
            "metro_dist_km": 2.8
        },
        {
            "name": "Vasant Kunj Sector C (Pockets 1-9 & Ambience Mall)",
            "lat": 28.539,
            "lon": 77.155,
            "category": "residential_block",
            "aliases": ["vasant kunj sector c", "sector c vasant kunj", "ambience mall vasant kunj", "dlf promenade", "dlf emporio", "pocket 9 sector c vasant kunj"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "DTC Bus 604"],
            "has_direct_metro": False,
            "nearest_metro": "Vasant Vihar",
            "metro_dist_km": 2.2
        },
        {
            "name": "Vasant Kunj Sector D (Pockets 1-8 & Kishangarh)",
            "lat": 28.518,
            "lon": 77.165,
            "category": "residential_block",
            "aliases": ["vasant kunj sector d", "sector d vasant kunj", "pocket 1 sector d vasant kunj", "kishangarh vasant kunj"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": False,
            "nearest_metro": "Chhatarpur",
            "metro_dist_km": 1.9
        },
        {
            "name": "Safdarjung Enclave (Blocks A, B & Kamal Cinema)",
            "lat": 28.563,
            "lon": 77.195,
            "category": "residential_block",
            "aliases": ["safdarjung enclave", "b6 market safdarjung", "kamal cinema", "block a safdarjung enclave", "block b safdarjung enclave"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Pink Line (Bhikaji Cama Place)"],
            "has_direct_metro": True,
            "nearest_metro": "Bhikaji Cama Place",
            "metro_dist_km": 0.5
        },
        {
            "name": "Munirka Village & DDA Flats",
            "lat": 28.557,
            "lon": 77.174,
            "category": "village",
            "aliases": ["munirka", "munirka village", "dda flats munirka", "munirka market", "rama market munirka"],
            "lines": ["Magenta Line (Munirka)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Munirka",
            "metro_dist_km": 0.2
        },
        {
            "name": "Ber Sarai & JNU Gate",
            "lat": 28.548,
            "lon": 77.181,
            "category": "village",
            "aliases": ["ber sarai", "ber sarai market", "jnu north gate", "old jnu campus", "iit flyover ber sarai"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Magenta Line (IIT Delhi)"],
            "has_direct_metro": True,
            "nearest_metro": "IIT",
            "metro_dist_km": 0.6
        },
        {
            "name": "Katwaria Sarai & Qutub Institutional Area",
            "lat": 28.541,
            "lon": 77.185,
            "category": "village",
            "aliases": ["katwaria sarai", "katwaria sarai village", "qutub institutional area", "ncert katwaria sarai"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": False,
            "nearest_metro": "IIT",
            "metro_dist_km": 1.2
        },
        {
            "name": "RK Puram Sector 1 to 12 (Sangam Cinema & Mohammadpur)",
            "lat": 28.566,
            "lon": 77.179,
            "category": "residential_block",
            "aliases": ["rk puram", "r k puram", "rk puram sector 1", "rk puram sector 4", "rk puram sector 8", "rk puram sector 12", "sangam cinema rk puram"],
            "lines": ["Magenta Line (RK Puram)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "RK Puram",
            "metro_dist_km": 0.4
        },
        {
            "name": "Moti Bagh (North & South Moti Bagh)",
            "lat": 28.583,
            "lon": 77.172,
            "category": "residential_block",
            "aliases": ["moti bagh", "north moti bagh", "south moti bagh", "shanti path moti bagh", "charak palika hospital"],
            "lines": ["Pink Line (Sir M. Vishweshwaraiah Moti Bagh)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Sir Vishweshwaraiah Moti Bagh",
            "metro_dist_km": 0.3
        },
        {
            "name": "Janakpuri Block A (A1, A2, A3 & Chhoti Subzi Mandi)",
            "lat": 28.628,
            "lon": 77.091,
            "category": "residential_block",
            "aliases": ["janakpuri block a", "janakpuri a block", "a1 janakpuri", "a2 janakpuri", "a3 janakpuri", "chhoti subzi mandi janakpuri"],
            "lines": ["Blue Line (Janakpuri East)", "Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": True,
            "nearest_metro": "Janakpuri East",
            "metro_dist_km": 0.4
        },
        {
            "name": "Janakpuri Block B (B1, B2, B3 & Community Centre)",
            "lat": 28.621,
            "lon": 77.085,
            "category": "residential_block",
            "aliases": ["janakpuri block b", "janakpuri b block", "b1 janakpuri", "b2 janakpuri", "b3 janakpuri", "b block market janakpuri"],
            "lines": ["Blue Line (Janakpuri West)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Janakpuri West",
            "metro_dist_km": 0.5
        },
        {
            "name": "Janakpuri Block C (C1, C2, C3, C4 & St Marks)",
            "lat": 28.618,
            "lon": 77.095,
            "category": "residential_block",
            "aliases": ["janakpuri block c", "janakpuri c block", "c1 janakpuri", "c2 janakpuri", "c3 janakpuri", "c4 janakpuri", "c block dda market janakpuri"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": False,
            "nearest_metro": "Janakpuri East",
            "metro_dist_km": 1.1
        },
        {
            "name": "Janakpuri District Centre (D-Block & Westend Mall)",
            "lat": 28.6295,
            "lon": 77.078,
            "category": "market",
            "aliases": ["district centre janakpuri", "janakpuri dc", "westend mall janakpuri", "janakpuri block d", "d1 janakpuri"],
            "lines": ["Blue Line (Janakpuri West)", "Magenta Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Janakpuri West",
            "metro_dist_km": 0.3
        },
        {
            "name": "Vikaspuri (Blocks A to M & PVR Vikaspuri)",
            "lat": 28.638,
            "lon": 77.071,
            "category": "residential_block",
            "aliases": ["vikaspuri", "vikas puri", "pvr vikaspuri", "block a vikaspuri", "block f vikaspuri", "shankar garden", "bodella village"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": False,
            "nearest_metro": "Janakpuri West",
            "metro_dist_km": 1.3
        },
        {
            "name": "Uttam Nagar East & Arya Samaj Road",
            "lat": 28.622,
            "lon": 77.065,
            "category": "locality",
            "aliases": ["uttam nagar east", "uttam nagar", "arya samaj road uttam nagar", "uttam nagar terminal", "milap nagar"],
            "lines": ["Blue Line (Uttam Nagar East)", "Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": True,
            "nearest_metro": "Uttam Nagar East",
            "metro_dist_km": 0.2
        },
        {
            "name": "Uttam Nagar West & Mohan Garden",
            "lat": 28.62,
            "lon": 77.054,
            "category": "locality",
            "aliases": ["uttam nagar west", "mohan garden", "pipal wala road", "gandhi chowk mohan garden", "bhagwati garden"],
            "lines": ["Blue Line (Uttam Nagar West)", "Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Uttam Nagar West",
            "metro_dist_km": 0.3
        },
        {
            "name": "Tilak Nagar (Main Market & Mall Road)",
            "lat": 28.636,
            "lon": 77.1,
            "category": "market",
            "aliases": ["tilak nagar", "tilak nagar main market", "mall road tilak nagar", "fateh nagar", "chaukhandi tilak nagar"],
            "lines": ["Blue Line (Tilak Nagar)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Tilak Nagar",
            "metro_dist_km": 0.2
        },
        {
            "name": "Jail Road Furniture & Food Street (Tilak Nagar)",
            "lat": 28.631,
            "lon": 77.108,
            "category": "market",
            "aliases": ["jail road", "jail road furniture market", "jail road food street", "prem nagar jail road", "fateh nagar gurudwara"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": False,
            "nearest_metro": "Tilak Nagar",
            "metro_dist_km": 0.8
        },
        {
            "name": "Hari Nagar (Clock Tower, Beriwala Bagh & DDU)",
            "lat": 28.625,
            "lon": 77.118,
            "category": "locality",
            "aliases": ["hari nagar", "clock tower hari nagar", "beriwala bagh", "ddu hospital", "deen dayal upadhyay hospital", "block be hari nagar"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": False,
            "nearest_metro": "Subhash Nagar",
            "metro_dist_km": 1.2
        },
        {
            "name": "Subhash Nagar (Blocks 1-12 & Pacific Mall)",
            "lat": 28.641,
            "lon": 77.114,
            "category": "residential_block",
            "aliases": ["subhash nagar", "pacific mall subhash nagar", "subhash nagar metro", "block 1 subhash nagar", "ajanta cinema subhash nagar"],
            "lines": ["Blue Line (Subhash Nagar)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Subhash Nagar",
            "metro_dist_km": 0.2
        },
        {
            "name": "Rajouri Garden (Main Market & Blocks A-J)",
            "lat": 28.648,
            "lon": 77.123,
            "category": "market",
            "aliases": ["rajouri garden", "rajouri market", "block f rajouri garden", "block a rajouri garden", "nehru market rajouri"],
            "lines": ["Blue Line (Rajouri Garden)", "Pink Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Rajouri Garden",
            "metro_dist_km": 0.3
        },
        {
            "name": "Vishal Enclave (Wave Cinema & Food Corridor)",
            "lat": 28.652,
            "lon": 77.118,
            "category": "locality",
            "aliases": ["vishal enclave", "wave cinema rajouri", "vishal cinema", "rajouri garden extension"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Blue Line"],
            "has_direct_metro": False,
            "nearest_metro": "Rajouri Garden",
            "metro_dist_km": 0.7
        },
        {
            "name": "Punjabi Bagh (Club Road Market & West/East)",
            "lat": 28.667,
            "lon": 77.129,
            "category": "residential_block",
            "aliases": ["punjabi bagh", "punjabi bagh club road", "west punjabi bagh", "east punjabi bagh", "central market punjabi bagh"],
            "lines": ["Green Line (Punjabi Bagh)", "Pink Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Punjabi Bagh West",
            "metro_dist_km": 0.4
        },
        {
            "name": "Paschim Vihar (Jwalaheri Market & B-Block)",
            "lat": 28.672,
            "lon": 77.098,
            "category": "market",
            "aliases": ["paschim vihar", "jwalaheri market", "jwala heri", "b block paschim vihar", "radisson blu paschim vihar", "bhera enclave"],
            "lines": ["Green Line (Paschim Vihar West)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Paschim Vihar West",
            "metro_dist_km": 0.5
        },
        {
            "name": "Kirti Nagar (Furniture Market & Industrial Area)",
            "lat": 28.651,
            "lon": 77.142,
            "category": "industrial_area",
            "aliases": ["kirti nagar", "kirti nagar furniture market", "kirti nagar industrial area", "mansarover garden", "timber market kirti nagar"],
            "lines": ["Blue Line (Kirti Nagar)", "Green Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Kirti Nagar",
            "metro_dist_km": 0.3
        },
        {
            "name": "Moti Nagar & DLF Capital Greens",
            "lat": 28.658,
            "lon": 77.151,
            "category": "residential_block",
            "aliases": ["moti nagar", "dlf capital greens", "karampura", "fun cinemas moti nagar", "moti nagar crossing"],
            "lines": ["Blue Line (Moti Nagar)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Moti Nagar",
            "metro_dist_km": 0.3
        },
        {
            "name": "Patel Nagar (East, West & South Patel Nagar)",
            "lat": 28.654,
            "lon": 77.168,
            "category": "residential_block",
            "aliases": ["patel nagar", "east patel nagar", "west patel nagar", "south patel nagar", "shadipur depot"],
            "lines": ["Blue Line (Patel Nagar)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Patel Nagar",
            "metro_dist_km": 0.3
        },
        {
            "name": "Naraina Vihar & Naraina Industrial Area",
            "lat": 28.629,
            "lon": 77.138,
            "category": "industrial_area",
            "aliases": ["naraina", "naraina vihar", "naraina industrial area", "pvr naraina", "naraina phase 1", "naraina phase 2"],
            "lines": ["Pink Line (Naraina Vihar)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Naraina Vihar",
            "metro_dist_km": 0.3
        },
        {
            "name": "Palam Village & Colony (Sadh Nagar & Raj Nagar)",
            "lat": 28.587,
            "lon": 77.085,
            "category": "village",
            "aliases": ["palam", "palam village", "palam colony", "sadh nagar palam", "raj nagar palam", "manglapuri palam"],
            "lines": ["Magenta Line (Palam)", "Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": True,
            "nearest_metro": "Palam",
            "metro_dist_km": 0.4
        },
        {
            "name": "Delhi Cantt (Sadar Bazar & Gopinath Bazar)",
            "lat": 28.598,
            "lon": 77.126,
            "category": "town",
            "aliases": ["delhi cantt", "sadar bazar cantt", "gopinath bazar", "kirby place", "delhi cantt railway station", "uri enclave"],
            "lines": ["Pink Line (Delhi Cantt)", "Northern Railway", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Delhi Cantt",
            "metro_dist_km": 0.5
        },
        {
            "name": "Dwarka Sector 1 & 2 (Palam Flyover Link)",
            "lat": 28.591,
            "lon": 77.072,
            "category": "residential_block",
            "aliases": ["dwarka sector 1", "dwarka sector 2", "palam flyover dwarka", "dda sfs flats sector 1"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": False,
            "nearest_metro": "Palam",
            "metro_dist_km": 1.2
        },
        {
            "name": "Dwarka Sector 3 & Matiala (NSUT Campus)",
            "lat": 28.608,
            "lon": 77.039,
            "category": "locality",
            "aliases": ["dwarka sector 3", "nsut dwarka", "nsit", "matiala road dwarka", "sector 3 dwarka"],
            "lines": ["Blue Line (Dwarka Mor)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Dwarka Mor",
            "metro_dist_km": 1.3
        },
        {
            "name": "Dwarka Sector 4 & 5 (Ashirwad Chowk & DDA Market)",
            "lat": 28.599,
            "lon": 77.049,
            "category": "residential_block",
            "aliases": ["dwarka sector 4", "dwarka sector 5", "ashirwad chowk dwarka", "dda market sector 4", "sector 4 market dwarka"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": False,
            "nearest_metro": "Dwarka Sector 11",
            "metro_dist_km": 1.4
        },
        {
            "name": "Dwarka Sector 6 & 10 (Sports Complex & Venkateshwar)",
            "lat": 28.586,
            "lon": 77.058,
            "category": "residential_block",
            "aliases": ["dwarka sector 6", "dwarka sector 10", "central market sector 6", "sports complex dwarka", "venkateshwar hospital dwarka"],
            "lines": ["Blue Line (Dwarka Sector 10)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Dwarka Sector 10",
            "metro_dist_km": 0.4
        },
        {
            "name": "Dwarka Sector 7 (Rampal Chowk Market)",
            "lat": 28.583,
            "lon": 77.072,
            "category": "market",
            "aliases": ["dwarka sector 7", "rampal chowk", "rampal chowk dwarka", "shiksha bharati dwarka", "sector 7 market"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": False,
            "nearest_metro": "Palam",
            "metro_dist_km": 1.3
        },
        {
            "name": "Dwarka Sector 11 (Main Market & Metro)",
            "lat": 28.588,
            "lon": 77.046,
            "category": "residential_block",
            "aliases": ["dwarka sector 11", "sector 11 market dwarka", "ramphal chowk link", "sector 11 metro"],
            "lines": ["Blue Line (Dwarka Sector 11)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Dwarka Sector 11",
            "metro_dist_km": 0.2
        },
        {
            "name": "Dwarka Sector 12 (City Centre Mall & KM Chowk)",
            "lat": 28.592,
            "lon": 77.039,
            "category": "market",
            "aliases": ["dwarka sector 12", "city centre mall dwarka", "km chowk dwarka", "sector 12 metro dwarka"],
            "lines": ["Blue Line (Dwarka Sector 12)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Dwarka Sector 12",
            "metro_dist_km": 0.2
        },
        {
            "name": "Dwarka Sector 14 (Vegas Mall & NLU / GGSIPU)",
            "lat": 28.601,
            "lon": 77.026,
            "category": "market",
            "aliases": ["dwarka sector 14", "vegas mall", "vegas mall dwarka", "national law university dwarka", "nlu delhi", "sector 14 metro"],
            "lines": ["Blue Line (Dwarka Sector 14)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Dwarka Sector 14",
            "metro_dist_km": 0.3
        },
        {
            "name": "Dwarka Sector 21 (Interchange Terminal & Pacific D21)",
            "lat": 28.552,
            "lon": 77.058,
            "category": "metro_station",
            "aliases": ["dwarka sector 21", "pacific d21 mall", "airport express dwarka", "sector 21 terminal"],
            "lines": ["Blue Line", "Airport Express", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Dwarka Sector 21",
            "metro_dist_km": 0.1
        },
        {
            "name": "Dwarka Sector 25 (IICC Yashobhoomi Convention Centre)",
            "lat": 28.541,
            "lon": 77.038,
            "category": "landmark",
            "aliases": ["yashobhoomi", "iicc dwarka", "india international convention centre", "dwarka sector 25", "yashobhoomi dwarka sector 25"],
            "lines": ["Airport Express (Yashobhoomi)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Yashobhoomi Dwarka Sector 25",
            "metro_dist_km": 0.2
        },
        {
            "name": "Najafgarh (Firni Road, Thana Road & Delhi Gate)",
            "lat": 28.609,
            "lon": 76.985,
            "category": "town",
            "aliases": ["najafgarh", "najafgarh town", "delhi gate najafgarh", "firni road najafgarh", "thana road najafgarh", "roshanpura najafgarh"],
            "lines": ["Grey Line (Najafgarh)", "Delhi Govt Metered Auto (TSR)", "DTC Bus Terminal Najafgarh"],
            "has_direct_metro": True,
            "nearest_metro": "Najafgarh",
            "metro_dist_km": 0.4
        },
        {
            "name": "Chhawla Village & BSF Camp",
            "lat": 28.568,
            "lon": 76.995,
            "category": "village",
            "aliases": ["chhawla", "chhawla village", "bsf camp chhawla", "goyla dairy", "chhawla bridge"],
            "lines": ["DTC Bus 828", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Najafgarh",
            "metro_dist_km": 4.5
        },
        {
            "name": "Nangloi (Rohtak Road & Nangloi Chowk)",
            "lat": 28.683,
            "lon": 77.065,
            "category": "town",
            "aliases": ["nangloi", "nangloi chowk", "rohtak road nangloi", "kamruddin nagar", "sultanpuri road nangloi"],
            "lines": ["Green Line (Nangloi)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Nangloi",
            "metro_dist_km": 0.3
        },
        {
            "name": "Mundka Village & Industrial Area",
            "lat": 28.684,
            "lon": 77.028,
            "category": "industrial_area",
            "aliases": ["mundka", "mundka village", "mundka industrial area", "mundka metro", "swarn park mundka"],
            "lines": ["Green Line (Mundka)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Mundka",
            "metro_dist_km": 0.3
        },
        {
            "name": "Rohini Sector 3 & 4 (Jaipur Golden & Madhuban Chowk)",
            "lat": 28.703,
            "lon": 77.118,
            "category": "residential_block",
            "aliases": ["rohini sector 3", "rohini sector 4", "jaipur golden hospital", "madhuban chowk", "ayodhya chowk rohini"],
            "lines": ["Red Line (Rohini East / Pitampura)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Rohini East",
            "metro_dist_km": 0.5
        },
        {
            "name": "Rohini Sector 7 & 8 (M2K Cinema & Sai Mandir)",
            "lat": 28.708,
            "lon": 77.126,
            "category": "residential_block",
            "aliases": ["rohini sector 7", "rohini sector 8", "m2k rohini", "m2k cinema sector 8", "deepali chowk", "sai baba mandir rohini sector 7"],
            "lines": ["Red Line (Rohini East)", "Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": True,
            "nearest_metro": "Rohini East",
            "metro_dist_km": 0.6
        },
        {
            "name": "Rohini Sector 9 & 13 (DC Chowk & Prashant Vihar)",
            "lat": 28.718,
            "lon": 77.131,
            "category": "market",
            "aliases": ["rohini sector 9", "rohini sector 13", "dc chowk", "dc chowk market rohini", "prashant vihar", "mount abu school rohini"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": False,
            "nearest_metro": "Rohini East",
            "metro_dist_km": 1.4
        },
        {
            "name": "Rohini Sector 10 & 11 (Rohini Court & Japanese Park)",
            "lat": 28.715,
            "lon": 77.112,
            "category": "residential_block",
            "aliases": ["rohini sector 10", "rohini sector 11", "rohini court", "japanese park rohini", "swarna jayanti park rohini", "rithala road"],
            "lines": ["Red Line (Rohini West / Rithala)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Rohini West",
            "metro_dist_km": 0.4
        },
        {
            "name": "Rohini Sector 16 & 17 (DTU / DCE Campus)",
            "lat": 28.749,
            "lon": 77.118,
            "category": "locality",
            "aliases": ["rohini sector 16", "rohini sector 17", "dtu", "delhi technological university", "dce", "shahbad daulatpur dtu"],
            "lines": ["DTC Bus 943", "Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Samaypur Badli",
            "metro_dist_km": 2.1
        },
        {
            "name": "Rohini Sector 21 & 22 (Begumpur & Pooth Kalan)",
            "lat": 28.718,
            "lon": 77.078,
            "category": "residential_block",
            "aliases": ["rohini sector 21", "rohini sector 22", "begumpur", "pooth kalan", "braham shakti hospital rohini"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": False,
            "nearest_metro": "Rithala",
            "metro_dist_km": 2.6
        },
        {
            "name": "Pitampura (Netaji Subhash Place & Kohat Enclave)",
            "lat": 28.699,
            "lon": 77.148,
            "category": "market",
            "aliases": ["pitampura", "netaji subhash place", "nsp", "kohat enclave", "dilli haat pitampura", "max hospital pitampura"],
            "lines": ["Red Line (Netaji Subhash Place)", "Pink Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Netaji Subhash Place",
            "metro_dist_km": 0.2
        },
        {
            "name": "Rani Bagh (Main Market & Shakur Basti)",
            "lat": 28.689,
            "lon": 77.135,
            "category": "market",
            "aliases": ["rani bagh", "rani bagh market", "shakur basti", "rishi nagar rani bagh", "sant nagar rani bagh"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": False,
            "nearest_metro": "Netaji Subhash Place",
            "metro_dist_km": 1.3
        },
        {
            "name": "Shalimar Bagh (Blocks AA to BP & Max Hospital)",
            "lat": 28.712,
            "lon": 77.158,
            "category": "residential_block",
            "aliases": ["shalimar bagh", "block aa shalimar bagh", "block bp shalimar bagh", "max hospital shalimar bagh", "club road shalimar bagh"],
            "lines": ["Pink Line (Shalimar Bagh)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Shalimar Bagh",
            "metro_dist_km": 0.4
        },
        {
            "name": "Ashok Vihar (Phase 1, 2, 3 & Satyawati College)",
            "lat": 28.694,
            "lon": 77.178,
            "category": "residential_block",
            "aliases": ["ashok vihar", "ashok vihar phase 1", "ashok vihar phase 2", "ashok vihar phase 3", "deep cinema ashok vihar", "satyawati college"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Red Line (Keshav Puram)"],
            "has_direct_metro": False,
            "nearest_metro": "Keshav Puram",
            "metro_dist_km": 1.2
        },
        {
            "name": "Wazirpur Industrial Area (Bartan Market)",
            "lat": 28.698,
            "lon": 77.165,
            "category": "industrial_area",
            "aliases": ["wazirpur", "wazirpur industrial area", "bartan market wazirpur", "wazirpur depot"],
            "lines": ["Pink Line", "Red Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Netaji Subhash Place",
            "metro_dist_km": 0.6
        },
        {
            "name": "Model Town (Part 1, 2, 3 & Gujranwala Town)",
            "lat": 28.705,
            "lon": 77.192,
            "category": "residential_block",
            "aliases": ["model town", "model town 1", "model town 2", "model town 3", "gujranwala town", "derawal nagar"],
            "lines": ["Yellow Line (Model Town)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Model Town",
            "metro_dist_km": 0.3
        },
        {
            "name": "Mukherjee Nagar (Batra Cinema & Coaching Hub)",
            "lat": 28.711,
            "lon": 77.214,
            "category": "locality",
            "aliases": ["mukherjee nagar", "batra cinema mukherjee nagar", "ias coaching mukherjee nagar", "nehru vihar", "indira vihar mukherjee nagar"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "GTB Nagar",
            "metro_dist_km": 1.4
        },
        {
            "name": "Narela (Anaj Mandi & Industrial Area)",
            "lat": 28.852,
            "lon": 77.092,
            "category": "town",
            "aliases": ["narela", "narela anaj mandi", "narela industrial area", "lampur border narela", "tikri khurd narela"],
            "lines": ["Northern Railway (Narela)", "DTC Bus 131", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Samaypur Badli",
            "metro_dist_km": 14.5
        },
        {
            "name": "Bawana (Industrial Area & Village)",
            "lat": 28.798,
            "lon": 77.042,
            "category": "town",
            "aliases": ["bawana", "bawana industrial area", "bawana village", "dsidc bawana", "bawana chowk"],
            "lines": ["DTC Bus 114", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Rithala",
            "metro_dist_km": 11.0
        },
        {
            "name": "Alipur & Singhu Border (GT Karnal Road)",
            "lat": 28.802,
            "lon": 77.135,
            "category": "town",
            "aliases": ["alipur", "alipur block", "singhu border", "bakoli alipur", "gt karnal road alipur", "kundli border"],
            "lines": ["DTC Bus 131", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Samaypur Badli",
            "metro_dist_km": 8.5
        },
        {
            "name": "Burari (Sant Nagar & Kaushik Enclave)",
            "lat": 28.748,
            "lon": 77.198,
            "category": "locality",
            "aliases": ["sant nagar burari", "kaushik enclave burari", "burari chowk", "tomar colony burari", "burari village"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "DTC Bus 185", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Majlis Park",
            "metro_dist_km": 3.8
        },
        {
            "name": "Jahangirpuri (Blocks A to K & Resettlement Colony)",
            "lat": 28.732,
            "lon": 77.171,
            "category": "residential_block",
            "aliases": ["jahangirpuri", "block a jahangirpuri", "block d jahangirpuri", "jahangirpuri bus terminal", "bhalaswa dairy"],
            "lines": ["Yellow Line (Jahangirpuri)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Jahangirpuri",
            "metro_dist_km": 0.3
        },
        {
            "name": "Laxmi Nagar (Vikas Marg & Guru Nanak Pura)",
            "lat": 28.631,
            "lon": 77.278,
            "category": "market",
            "aliases": ["laxmi nagar", "guru nanak pura laxmi nagar", "mangal bazar laxmi nagar", "vijay chowk laxmi nagar", "ca coaching hub laxmi nagar"],
            "lines": ["Blue Line (Laxmi Nagar)", "Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": True,
            "nearest_metro": "Laxmi Nagar",
            "metro_dist_km": 0.2
        },
        {
            "name": "Shakarpur (School Block & WA Block)",
            "lat": 28.627,
            "lon": 77.282,
            "category": "locality",
            "aliases": ["shakarpur", "school block shakarpur", "wa block shakarpur", "shakarpur khas", "mother dairy plant shakarpur"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)", "Blue Line"],
            "has_direct_metro": False,
            "nearest_metro": "Laxmi Nagar",
            "metro_dist_km": 0.6
        },
        {
            "name": "Preet Vihar (Blocks A, B, C, D & Gagan Vihar)",
            "lat": 28.641,
            "lon": 77.294,
            "category": "residential_block",
            "aliases": ["preet vihar", "block a preet vihar", "block c preet vihar", "gagan vihar", "bharati artist colony", "v3s mall preet vihar"],
            "lines": ["Blue Line (Preet Vihar)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Preet Vihar",
            "metro_dist_km": 0.3
        },
        {
            "name": "Anand Vihar (ISBT & Railway Terminal)",
            "lat": 28.6505,
            "lon": 77.3155,
            "category": "railway_station",
            "aliases": ["anand vihar", "anand vihar isbt", "anand vihar railway terminal", "surajmal vihar", "vivek vihar link"],
            "lines": ["Blue Line", "Pink Line", "Northern Railway", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Anand Vihar ISBT",
            "metro_dist_km": 0.1
        },
        {
            "name": "Karkardooma (Court Complex & Dayanand Vihar)",
            "lat": 28.655,
            "lon": 77.303,
            "category": "locality",
            "aliases": ["karkardooma", "karkardooma court", "dayanand vihar", "arya nagar karkardooma", "karkardooma metro"],
            "lines": ["Blue Line (Karkardooma)", "Pink Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Karkardooma",
            "metro_dist_km": 0.2
        },
        {
            "name": "Mayur Vihar Phase 1 (Pockets 1-5 & Acharya Niketan)",
            "lat": 28.604,
            "lon": 77.292,
            "category": "residential_block",
            "aliases": ["mayur vihar phase 1", "acharya niketan market", "pocket 1 mayur vihar 1", "pocket 4 mayur vihar 1", "samachar apartments"],
            "lines": ["Blue Line (Mayur Vihar 1)", "Pink Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Mayur Vihar 1",
            "metro_dist_km": 0.4
        },
        {
            "name": "Mayur Vihar Phase 2 (Pockets A to F & Kalyanvas)",
            "lat": 28.618,
            "lon": 77.308,
            "category": "residential_block",
            "aliases": ["mayur vihar phase 2", "pocket a mayur vihar 2", "pocket c mayur vihar 2", "kalyanvas", "sanjay jheel mayur vihar 2"],
            "lines": ["Pink Line (Mayur Vihar Pocket 1)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Mayur Vihar Pocket 1",
            "metro_dist_km": 0.5
        },
        {
            "name": "Mayur Vihar Phase 3 (Pockets A1-A3, PKT 1-6 & Kondli)",
            "lat": 28.608,
            "lon": 77.338,
            "category": "residential_block",
            "aliases": ["mayur vihar phase 3", "pocket a1 mayur vihar 3", "pocket 1 mayur vihar 3", "kondli", "gharoli dairy mayur vihar 3", "sfs flats mv 3"],
            "lines": ["DTC Bus 347", "Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Noida Sector 62",
            "metro_dist_km": 2.4
        },
        {
            "name": "Vasundhara Enclave (DDA SFS Flats & Chilla Border)",
            "lat": 28.601,
            "lon": 77.324,
            "category": "residential_block",
            "aliases": ["vasundhara enclave", "dashmesh public school vasundhara", "chilla border vasundhara", "mansara apartments"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "New Ashok Nagar",
            "metro_dist_km": 1.6
        },
        {
            "name": "IP Extension (Patparganj & Madhu Vihar)",
            "lat": 28.631,
            "lon": 77.305,
            "category": "residential_block",
            "aliases": ["ip extension", "indraprastha extension", "madhu vihar market", "balco apartments", "patparganj societies"],
            "lines": ["Pink Line (IP Extension)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "IP Extension",
            "metro_dist_km": 0.3
        },
        {
            "name": "Patparganj Industrial Area & Hasanpur Depot",
            "lat": 28.638,
            "lon": 77.315,
            "category": "industrial_area",
            "aliases": ["patparganj industrial area", "hasanpur depot", "max hospital patparganj", "patparganj dda shed"],
            "lines": ["Pink Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "IP Extension",
            "metro_dist_km": 1.1
        },
        {
            "name": "Geeta Colony (Blocks 1 to 17 & Jheel Khurenja)",
            "lat": 28.651,
            "lon": 77.272,
            "category": "residential_block",
            "aliases": ["geeta colony", "block 1 geeta colony", "block 7 geeta colony", "jheel khurenja", "rani garden geeta colony", "taj enclave"],
            "lines": ["Delhi Govt Metered Auto (TSR)", "Shared E-Rickshaw Feeder (Toto)"],
            "has_direct_metro": False,
            "nearest_metro": "Shastri Park",
            "metro_dist_km": 1.6
        },
        {
            "name": "Gandhi Nagar (Readymade Garment Wholesale Market)",
            "lat": 28.658,
            "lon": 77.269,
            "category": "market",
            "aliases": ["gandhi nagar", "gandhi nagar market", "gandhi nagar cloth market", "mahavir mohalla gandhi nagar", "subhash mohalla"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Seelampur",
            "metro_dist_km": 1.4
        },
        {
            "name": "Krishna Nagar (Lal Quarter Market)",
            "lat": 28.658,
            "lon": 77.284,
            "category": "market",
            "aliases": ["krishna nagar", "lal quarter market", "lal quarter krishna nagar", "chander nagar krishna nagar", "radhey puri"],
            "lines": ["Pink Line (Krishna Nagar)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Krishna Nagar",
            "metro_dist_km": 0.4
        },
        {
            "name": "Shahdara (Chhota & Bada Bazar, Rohtas Nagar)",
            "lat": 28.673,
            "lon": 77.291,
            "category": "town",
            "aliases": ["shahdara", "chhota bazar shahdara", "bada bazar shahdara", "rohtas nagar shahdara", "babarpur shahdara", "mansarovar park"],
            "lines": ["Red Line (Shahdara)", "Northern Railway", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Shahdara",
            "metro_dist_km": 0.3
        },
        {
            "name": "Seelampur & Welcome",
            "lat": 28.669,
            "lon": 77.275,
            "category": "town",
            "aliases": ["seelampur", "welcome", "seelampur market", "jafrabad road seelampur", "welcome metro junction"],
            "lines": ["Red Line (Seelampur)", "Pink Line", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Seelampur",
            "metro_dist_km": 0.2
        },
        {
            "name": "Yamuna Vihar (Blocks B, C, D & Gokulpuri)",
            "lat": 28.701,
            "lon": 77.278,
            "category": "residential_block",
            "aliases": ["yamuna vihar", "block b yamuna vihar", "block c yamuna vihar", "gokulpuri", "yamuna vihar b block market"],
            "lines": ["Pink Line (Gokulpuri)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Gokulpuri",
            "metro_dist_km": 0.6
        },
        {
            "name": "Bhajanpura & Khajuri Khas",
            "lat": 28.708,
            "lon": 77.268,
            "category": "locality",
            "aliases": ["bhajanpura", "bhajanpura chowk", "khajuri khas", "wazirabad road bhajanpura", "bhajanpura market"],
            "lines": ["Shared E-Rickshaw Feeder (Toto)", "DTC Bus 212", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Gokulpuri",
            "metro_dist_km": 1.7
        },
        {
            "name": "Dilshad Garden (Pockets A-R & GTB Hospital)",
            "lat": 28.682,
            "lon": 77.319,
            "category": "residential_block",
            "aliases": ["dilshad garden", "gtb hospital", "seemapuri dilshad garden", "pocket a dilshad garden", "dilshad colony"],
            "lines": ["Red Line (Dilshad Garden)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Dilshad Garden",
            "metro_dist_km": 0.3
        },
        {
            "name": "Karawal Nagar & Shiv Vihar",
            "lat": 28.729,
            "lon": 77.289,
            "category": "town",
            "aliases": ["karawal nagar", "shiv vihar", "sadatpur karawal nagar", "johripur", "shiv vihar terminal"],
            "lines": ["Pink Line (Shiv Vihar)", "Shared E-Rickshaw Feeder (Toto)", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": True,
            "nearest_metro": "Shiv Vihar",
            "metro_dist_km": 0.5
        },
        {
            "name": "Sonia Vihar (Pushta 1 to 5)",
            "lat": 28.735,
            "lon": 77.255,
            "category": "locality",
            "aliases": ["sonia vihar", "sonia vihar pushta", "pushta 1 sonia vihar", "pushta 4 sonia vihar", "wazirabad water works"],
            "lines": ["DTC Bus 258", "Delhi Govt Metered Auto (TSR)"],
            "has_direct_metro": False,
            "nearest_metro": "Shiv Vihar",
            "metro_dist_km": 3.6
        }
    ],
    "Mumbai": [
        {
            "name": "Chhatrapati Shivaji Maharaj Terminus (CSMT)",
            "lat": 18.9400,
            "lon": 72.8353,
            "category": "railway_station",
            "aliases": ["csmt", "vt", "victoria terminus", "south mumbai", "fort"],
            "lines": ["Central Railway", "Harbour Line", "Mumbai Metered Kaali-Peeli Taxi", "BEST AC Electric Bus (Chalo Bus)"]
        },
        {
            "name": "Churchgate Railway Station",
            "lat": 18.9322,
            "lon": 72.8264,
            "category": "railway_station",
            "aliases": ["churchgate", "wr terminus", "nariman point station", "marine lines"],
            "lines": ["Western Railway", "Mumbai Metered Kaali-Peeli Taxi", "BEST AC Electric Bus (Chalo Bus)"]
        },
        {
            "name": "Bandra Kurla Complex (BKC)",
            "lat": 19.0657,
            "lon": 72.8687,
            "category": "landmark",
            "aliases": ["bkc", "bandra east", "financial district", "mmrda grounds", "icici bkc"],
            "lines": ["Mumbai Metro Line 3 (Aqua Line)", "BEST AC Electric Bus (Chalo Bus)", "Maharashtra Govt Metered Auto", "Mumbai Metered Kaali-Peeli Taxi"]
        },
        {
            "name": "Dadar Station (Central & Western interchange)",
            "lat": 19.0178,
            "lon": 72.8478,
            "category": "railway_station",
            "aliases": ["dadar", "dadar tt", "dadar western", "dadar central", "plaza cinema"],
            "lines": ["Western Railway", "Central Railway", "Mumbai Metered Kaali-Peeli Taxi", "BEST AC Electric Bus (Chalo Bus)"]
        },
        {
            "name": "Andheri Station",
            "lat": 19.1197,
            "lon": 72.8464,
            "category": "metro_station",
            "aliases": ["andheri", "western suburbs", "andheri west", "andheri east", "andheri local"],
            "lines": ["Western Railway", "Harbour Line", "Mumbai Metro Line 1 (Versova-Ghatkopar)", "Maharashtra Govt Metered Auto", "Mumbai Metered Kaali-Peeli Taxi"]
        },
        {
            "name": "Ghatkopar Station",
            "lat": 19.0863,
            "lon": 72.9084,
            "category": "metro_station",
            "aliases": ["ghatkopar", "metro 1 terminal", "ghatkopar west", "ghatkopar east"],
            "lines": ["Central Railway", "Mumbai Metro Line 1 (Versova-Ghatkopar)", "Maharashtra Govt Metered Auto", "BEST AC Electric Bus (Chalo Bus)"]
        },
        {
            "name": "Bandra Terminus & Bandra West (Linking Rd)",
            "lat": 19.0544,
            "lon": 72.8402,
            "category": "railway_station",
            "aliases": ["bandra", "bandra west", "linking road", "hill road", "bandra terminus", "bandra station"],
            "lines": ["Western Railway", "Harbour Line", "Maharashtra Govt Metered Auto", "Mumbai Metered Kaali-Peeli Taxi", "BEST AC Electric Bus (Chalo Bus)"]
        },
        {
            "name": "Lower Parel / High Street Phoenix",
            "lat": 18.9953,
            "lon": 72.8306,
            "category": "landmark",
            "aliases": ["lower parel", "phoenix palladium", "high street phoenix", "currey road", "kamala mills"],
            "lines": ["Western Railway", "Mumbai Monorail", "Mumbai Metered Kaali-Peeli Taxi", "BEST AC Electric Bus (Chalo Bus)"]
        },
        {
            "name": "Mumbai Central Station (MMCT)",
            "lat": 18.9696,
            "lon": 72.8194,
            "category": "railway_station",
            "aliases": ["mumbai central", "mmct", "bct", "tardeo"],
            "lines": ["Western Railway", "Mumbai Metro Line 3 (Aqua Line)", "Mumbai Metered Kaali-Peeli Taxi", "BEST AC Electric Bus (Chalo Bus)"]
        },
        {
            "name": "Chhatrapati Shivaji Maharaj Int. Airport T2",
            "lat": 19.0974,
            "lon": 72.8742,
            "category": "landmark",
            "aliases": ["t2", "mumbai airport", "international airport", "csmi airport", "sahar"],
            "lines": ["Mumbai Metro Line 3 (Aqua Line)", "Maharashtra Govt Metered Auto", "Mumbai Metered Kaali-Peeli Taxi", "BEST Airport Express Chalo"]
        },
        {
            "name": "Mumbai Domestic Airport Terminal 1 (Santacruz)",
            "lat": 19.0886,
            "lon": 72.8535,
            "category": "landmark",
            "aliases": ["t1", "domestic airport", "santacruz airport", "vile parle airport"],
            "lines": ["Maharashtra Govt Metered Auto", "Mumbai Metered Kaali-Peeli Taxi", "BEST AC Electric Bus (Chalo Bus)"]
        },
        {
            "name": "Borivali Railway Station",
            "lat": 19.2290,
            "lon": 72.8574,
            "category": "railway_station",
            "aliases": ["borivali", "borivali west", "borivali east", "national park borivali"],
            "lines": ["Western Railway", "Maharashtra Govt Metered Auto", "Mumbai Metered Kaali-Peeli Taxi", "BEST AC Electric Bus (Chalo Bus)"]
        },
        {
            "name": "Thane Railway Station",
            "lat": 19.1860,
            "lon": 72.9759,
            "category": "railway_station",
            "aliases": ["thane", "thane junction", "thane west", "naupada", "ghodbunder"],
            "lines": ["Central Railway", "Trans-Harbour Line", "Maharashtra Govt Metered Auto", "BEST AC Electric Bus (Chalo Bus)"]
        },
        {
            "name": "Kurla Junction",
            "lat": 19.0653,
            "lon": 72.8794,
            "category": "railway_station",
            "aliases": ["kurla", "kurla west", "kurla terminus", "lokmanya tilak terminus", "ltt"],
            "lines": ["Central Railway", "Harbour Line", "Maharashtra Govt Metered Auto", "Mumbai Metered Kaali-Peeli Taxi", "BEST AC Electric Bus (Chalo Bus)"]
        },
        {
            "name": "Colaba & Gateway of India",
            "lat": 18.9220,
            "lon": 72.8347,
            "category": "landmark",
            "aliases": ["colaba", "gateway of india", "taj hotel", "regal cinema", "cuffe parade"],
            "lines": ["Mumbai Metered Kaali-Peeli Taxi", "BEST AC Electric Bus (Chalo Bus)"]
        },
        {
            "name": "Marine Drive & Nariman Point",
            "lat": 18.9268,
            "lon": 72.8234,
            "category": "landmark",
            "aliases": ["marine drive", "nariman point", "queens necklace", "ncpa", "air india building"],
            "lines": ["Mumbai Metered Kaali-Peeli Taxi", "BEST AC Electric Bus (Chalo Bus)"]
        },
        {
            "name": "Versova Metro Station",
            "lat": 19.1317,
            "lon": 72.8176,
            "category": "metro_station",
            "aliases": ["versova", "versova beach", "yari road", "seven bungalows"],
            "lines": ["Mumbai Metro Line 1 (Versova-Ghatkopar)", "Maharashtra Govt Metered Auto", "BEST AC Electric Bus (Chalo Bus)"]
        },
        {
            "name": "Juhu Beach (Vile Parle)",
            "lat": 19.0988,
            "lon": 72.8264,
            "category": "landmark",
            "aliases": ["juhu", "juhu beach", "juhu circle", "jw marriott juhu"],
            "lines": ["Maharashtra Govt Metered Auto", "Mumbai Metered Kaali-Peeli Taxi", "BEST AC Electric Bus (Chalo Bus)"]
        },
        {
            "name": "Powai (Hiranandani & IIT Bombay)",
            "lat": 19.1197,
            "lon": 72.9051,
            "category": "landmark",
            "aliases": ["powai", "hiranandani powai", "iit bombay", "powai lake"],
            "lines": ["Maharashtra Govt Metered Auto", "Mumbai Metered Kaali-Peeli Taxi", "BEST AC Electric Bus (Chalo Bus)"]
        },
        {
            "name": "Worli & Bandra-Worli Sea Link",
            "lat": 19.0166,
            "lon": 72.8183,
            "category": "landmark",
            "aliases": ["worli", "sea link", "worli sea face", "nehru planetarium", "atria mall"],
            "lines": ["Mumbai Metro Line 3 (Aqua Line)", "Mumbai Metered Kaali-Peeli Taxi", "BEST AC Electric Bus (Chalo Bus)"]
        },
        {
            "name": "Vashi (Navi Mumbai Gateway)",
            "lat": 19.0771,
            "lon": 72.9986,
            "category": "railway_station",
            "aliases": ["vashi", "vashi plaza", "navi mumbai", "inorbit vashi"],
            "lines": ["Harbour Line", "Trans-Harbour Line", "Maharashtra Govt Metered Auto", "BEST AC Electric Bus (Chalo Bus)"]
        },
        {
            "name": "Kalyan Junction",
            "lat": 19.2437,
            "lon": 73.1355,
            "category": "railway_station",
            "aliases": ["kalyan", "kalyan station", "kalyan west"],
            "lines": ["Central Railway", "Maharashtra Govt Metered Auto"]
        },
        {
            "name": "Malad West & Inorbit Mall",
            "lat": 19.1864,
            "lon": 72.8488,
            "category": "landmark",
            "aliases": ["malad", "malad west", "inorbit malad", "link road malad"],
            "lines": ["Western Railway", "Mumbai Metro Line 2A", "Maharashtra Govt Metered Auto", "BEST AC Electric Bus (Chalo Bus)"]
        },
        {
            "name": "Goregaon (Nesco & Western Express)",
            "lat": 19.1551,
            "lon": 72.8493,
            "category": "landmark",
            "aliases": ["goregaon", "nesco", "bombay exhibition centre", "oberoi mall goregaon"],
            "lines": ["Western Railway", "Harbour Line", "Mumbai Metro Line 7", "Maharashtra Govt Metered Auto", "BEST AC Electric Bus (Chalo Bus)"]
        }
    ],
    "Bengaluru": [
        {
            "name": "Majestic (KSR Bengaluru)",
            "lat": 12.9781,
            "lon": 77.5695,
            "category": "railway_station",
            "aliases": ["majestic", "kempegowda station", "ksr", "central bus stand"],
            "lines": ["Purple Line", "Green Line", "BMTC Hub", "Karnataka Govt Metered Auto"]
        },
        {
            "name": "Indiranagar 100ft Road",
            "lat": 12.9784,
            "lon": 77.6408,
            "category": "landmark",
            "aliases": ["indiranagar", "cmh road", "100 ft", "indiranagar metro"],
            "lines": ["Purple Line", "BMTC Feeder", "Karnataka Govt Metered Auto"]
        },
        {
            "name": "Electronic City Phase 1",
            "lat": 12.8452,
            "lon": 77.6602,
            "category": "landmark",
            "aliases": ["ecity", "infosys gate", "wipro ecity", "electronic city"],
            "lines": ["Yellow Line (Namma Metro)", "BMTC Vayu Vajra", "Karnataka Govt Metered Auto"]
        },
        {
            "name": "Whitefield (Kadugodi)",
            "lat": 12.9961,
            "lon": 77.7601,
            "category": "metro_station",
            "aliases": ["whitefield", "itpl", "kadugodi metro", "hopefarm"],
            "lines": ["Purple Line", "BMTC Feeder", "Karnataka Govt Metered Auto"]
        },
        {
            "name": "MG Road Metro Station",
            "lat": 12.9756,
            "lon": 77.6066,
            "category": "metro_station",
            "aliases": ["mg road", "brigade road", "trinity", "church street"],
            "lines": ["Purple Line", "BMTC Hub", "Karnataka Govt Metered Auto"]
        },
        {
            "name": "Koramangala Sony World Signal",
            "lat": 12.9352,
            "lon": 77.6245,
            "category": "landmark",
            "aliases": ["koramangala", "sony world", "80ft road koramangala", "forum mall"],
            "lines": ["BMTC Vajra AC Bus", "Karnataka Govt Metered Auto"]
        },
        {
            "name": "Kempegowda Int. Airport (KIA T1)",
            "lat": 13.1986,
            "lon": 77.7066,
            "category": "landmark",
            "aliases": ["kia", "bangalore airport", "bial", "kempegowda airport"],
            "lines": ["BMTC Vayu Vajra Airport Express", "Airport Taxi"]
        },
        {
            "name": "Yeshwanthpur Junction",
            "lat": 13.0238,
            "lon": 77.5501,
            "category": "railway_station",
            "aliases": ["yeshwanthpur", "ypr", "yeshvantpur station"],
            "lines": ["Green Line", "Indian Railways (SWR)", "BMTC Feeder", "Karnataka Govt Metered Auto"]
        },
        {
            "name": "Jayanagar 4th Block",
            "lat": 12.9299,
            "lon": 77.5838,
            "category": "landmark",
            "aliases": ["jayanagar", "4th block", "jayanagar complex", "south bangalore"],
            "lines": ["Green Line", "BMTC Feeder", "Karnataka Govt Metered Auto"]
        },
        {
            "name": "Hebbal Flyover",
            "lat": 13.0358,
            "lon": 77.5970,
            "category": "landmark",
            "aliases": ["hebbal", "manyata tech park feeder", "bellary road"],
            "lines": ["BMTC Hub", "Airport Corridor", "Karnataka Govt Metered Auto"]
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
        },
        {
            "name": "Chhata (Tehsil, Block & Railway Station)",
            "lat": 27.7214,
            "lon": 77.5028,
            "category": "railway_station",
            "aliases": [
                        "chhata",
                        "chata",
                        "chatha",
                        "chhata railway station",
                        "chj",
                        "chhata tehsil",
                        "chhata block",
                        "chhata mandi",
                        "chhata chauraha",
                        "nh-19 chhata"
            ],
            "lines": [
                        "Northern Railway (EMU / Passenger)",
                        "Shared Tempo / Vikram (Braj Corridor)",
                        "Mathura-Kosi Electric Nagar Seva Bus",
                        "Reserved Auto-Rickshaw (निजी ऑटो)"
            ]
},
        {
            "name": "Kosi Kalan (Town, Mandi & Railway Station)",
            "lat": 27.7925,
            "lon": 77.4328,
            "category": "railway_station",
            "aliases": [
                        "kosi kalan",
                        "kosi",
                        "kosi station",
                        "ksv",
                        "kosi mandi",
                        "kosi tehsil",
                        "kosi kalan chauraha"
            ],
            "lines": [
                        "Northern Railway (EMU / Passenger)",
                        "Shared Tempo / Vikram (Braj Corridor)",
                        "Mathura-Kosi Electric Nagar Seva Bus"
            ]
},
        {
            "name": "Chaumuhan (Block & Market)",
            "lat": 27.6086,
            "lon": 77.595,
            "category": "landmark",
            "aliases": [
                        "chaumuhan",
                        "chaumuha",
                        "chomuha",
                        "chaumuhan block",
                        "chaumuhan market",
                        "chaumuhan chauraha"
            ],
            "lines": [
                        "Shared Tempo / Vikram (Braj Corridor)",
                        "Shared E-Rickshaw Feeder (Toto)"
            ]
},
        {
            "name": "Akbarpur (NH-19 Village)",
            "lat": 27.7011,
            "lon": 77.5189,
            "category": "landmark",
            "aliases": [
                        "akbarpur",
                        "akbarpur chhata",
                        "akbarpur village",
                        "nh-19 akbarpur"
            ],
            "lines": [
                        "Shared Tempo / Vikram (Braj Corridor)"
            ]
},
        {
            "name": "Ajhai (Village & Railway Station)",
            "lat": 27.6667,
            "lon": 77.545,
            "category": "railway_station",
            "aliases": [
                        "ajhai",
                        "ajhai station",
                        "ajh",
                        "ajhai village",
                        "ajhai khurd",
                        "ajhai kalan"
            ],
            "lines": [
                        "Northern Railway (EMU / Passenger)",
                        "Shared Tempo / Vikram (Braj Corridor)"
            ]
},
        {
            "name": "Vrindavan Road Railway Station (VRBD)",
            "lat": 27.5789,
            "lon": 77.6328,
            "category": "railway_station",
            "aliases": [
                        "vrindavan road",
                        "vrbd",
                        "vrindavan road station",
                        "vrindavan road railway"
            ],
            "lines": [
                        "Northern Railway (EMU / Passenger)",
                        "Shared E-Rickshaw Feeder (Toto)"
            ]
},
        {
            "name": "Bhuteshwar Railway Station (BTSR)",
            "lat": 27.5011,
            "lon": 77.6711,
            "category": "railway_station",
            "aliases": [
                        "bhuteshwar station",
                        "btsr",
                        "bhuteshwar railway",
                        "bhuteshwar halt"
            ],
            "lines": [
                        "Northern Railway (EMU / Passenger)",
                        "Shared E-Rickshaw Feeder (Toto)"
            ]
},
        {
            "name": "Farah (Block, Deendayal Dham & Station)",
            "lat": 27.3236,
            "lon": 77.7656,
            "category": "railway_station",
            "aliases": [
                        "farah",
                        "farah station",
                        "far",
                        "deendayal dham",
                        "pt deendayal dham",
                        "farah block",
                        "farah town"
            ],
            "lines": [
                        "Northern Railway (EMU / Passenger)",
                        "Shared Tempo / Vikram (Braj Corridor)"
            ]
},
        {
            "name": "Raya (Block, Town & Railway Station)",
            "lat": 27.5583,
            "lon": 77.7889,
            "category": "railway_station",
            "aliases": [
                        "raya",
                        "raya station",
                        "raya junction",
                        "raya town",
                        "raya block",
                        "raya sadabad road"
            ],
            "lines": [
                        "North Eastern Railway (Passenger / Express)",
                        "Shared Tempo / Vikram (Braj Corridor)"
            ]
},
        {
            "name": "Mant (Tehsil & Block Headquarters)",
            "lat": 27.6186,
            "lon": 77.7328,
            "category": "landmark",
            "aliases": [
                        "mant",
                        "mat",
                        "mant tehsil",
                        "mant block",
                        "mant town",
                        "mat block"
            ],
            "lines": [
                        "Shared Tempo / Vikram (Braj Corridor)",
                        "Shared E-Rickshaw Feeder (Toto)"
            ]
},
        {
            "name": "Naujheel (Block & Rural Center)",
            "lat": 27.8464,
            "lon": 77.6433,
            "category": "landmark",
            "aliases": [
                        "naujheel",
                        "naujhil",
                        "naujheel block",
                        "naujhil town",
                        "bajna naujheel"
            ],
            "lines": [
                        "Shared Tempo / Vikram (Braj Corridor)"
            ]
},
        {
            "name": "Mahavan (Historic Tehsil & Town)",
            "lat": 27.435,
            "lon": 77.7478,
            "category": "landmark",
            "aliases": [
                        "mahavan",
                        "mahavaan",
                        "mahavan tehsil",
                        "mahavan town",
                        "chaurasi khamba mahavan"
            ],
            "lines": [
                        "Shared Tempo / Vikram (Braj Corridor)",
                        "Shared E-Rickshaw Feeder (Toto)"
            ]
},
        {
            "name": "Sonkh (Historic Town & Kila)",
            "lat": 27.4778,
            "lon": 77.5361,
            "category": "landmark",
            "aliases": [
                        "sonkh",
                        "sonkh town",
                        "sonkh kila",
                        "sonkh mandi"
            ],
            "lines": [
                        "Shared Tempo / Vikram (Braj Corridor)"
            ]
},
        {
            "name": "Aring (Town & Market)",
            "lat": 27.4967,
            "lon": 77.5611,
            "category": "landmark",
            "aliases": [
                        "aring",
                        "ading",
                        "aring town",
                        "aring govardhan road"
            ],
            "lines": [
                        "Shared Tempo / Vikram (Braj Corridor)"
            ]
},
        {
            "name": "Jait (NH-19 Village)",
            "lat": 27.5611,
            "lon": 77.6389,
            "category": "landmark",
            "aliases": [
                        "jait",
                        "jayt",
                        "jait village",
                        "nh-19 jait"
            ],
            "lines": [
                        "Shared Tempo / Vikram (Braj Corridor)"
            ]
},
        {
            "name": "Bati (Village)",
            "lat": 27.5611,
            "lon": 77.6189,
            "category": "landmark",
            "aliases": [
                        "bati",
                        "bati village",
                        "bati mathura"
            ],
            "lines": [
                        "Shared E-Rickshaw Feeder (Toto)"
            ]
},
        {
            "name": "Maghera (Village)",
            "lat": 27.5911,
            "lon": 77.5811,
            "category": "landmark",
            "aliases": [
                        "maghera",
                        "maghera village"
            ],
            "lines": [
                        "Shared E-Rickshaw Feeder (Toto)"
            ]
},
        {
            "name": "Mora (Village)",
            "lat": 27.5211,
            "lon": 77.5711,
            "category": "landmark",
            "aliases": [
                        "mora",
                        "mora village"
            ],
            "lines": [
                        "Shared E-Rickshaw Feeder (Toto)"
            ]
},
        {
            "name": "Datiya (Village)",
            "lat": 27.5089,
            "lon": 77.5911,
            "category": "landmark",
            "aliases": [
                        "datiya",
                        "datiya village"
            ],
            "lines": [
                        "Shared E-Rickshaw Feeder (Toto)"
            ]
},
        {
            "name": "Phenchari (Village)",
            "lat": 27.5411,
            "lon": 77.5611,
            "category": "landmark",
            "aliases": [
                        "phenchari",
                        "phenchari village"
            ],
            "lines": [
                        "Shared E-Rickshaw Feeder (Toto)"
            ]
},
        {
            "name": "Khamini (Village)",
            "lat": 27.4811,
            "lon": 77.5811,
            "category": "landmark",
            "aliases": [
                        "khamini",
                        "khamini village"
            ],
            "lines": [
                        "Shared E-Rickshaw Feeder (Toto)"
            ]
},
        {
            "name": "Asgarpur (Village)",
            "lat": 27.495,
            "lon": 77.6089,
            "category": "landmark",
            "aliases": [
                        "asgarpur",
                        "asgarpur village"
            ],
            "lines": [
                        "Shared E-Rickshaw Feeder (Toto)"
            ]
},
        {
            "name": "Ral (Village)",
            "lat": 27.5111,
            "lon": 77.5389,
            "category": "landmark",
            "aliases": [
                        "ral",
                        "ral village"
            ],
            "lines": [
                        "Shared Tempo / Vikram (Braj Corridor)"
            ]
},
        {
            "name": "Magorra (Town & Thana)",
            "lat": 27.3811,
            "lon": 77.5189,
            "category": "landmark",
            "aliases": [
                        "magorra",
                        "magora",
                        "magorra thana"
            ],
            "lines": [
                        "Shared Tempo / Vikram (Braj Corridor)"
            ]
},
        {
            "name": "Lohaban (Village)",
            "lat": 27.5028,
            "lon": 77.7389,
            "category": "landmark",
            "aliases": [
                        "lohaban",
                        "lohaban village"
            ],
            "lines": [
                        "Shared Tempo / Vikram (Braj Corridor)"
            ]
},
        {
            "name": "Daharuwa & Kaliyanpur (Villages)",
            "lat": 27.5311,
            "lon": 77.7511,
            "category": "landmark",
            "aliases": [
                        "daharuwa",
                        "kaliyanpur",
                        "dahrua"
            ],
            "lines": [
                        "Shared Tempo / Vikram (Braj Corridor)"
            ]
},
        {
            "name": "Diwana Khurd & Diwana Kalan (Villages)",
            "lat": 27.5489,
            "lon": 77.7689,
            "category": "landmark",
            "aliases": [
                        "diwana khurd",
                        "diwana kalan",
                        "diwana"
            ],
            "lines": [
                        "Shared Tempo / Vikram (Braj Corridor)"
            ]
},
        {
            "name": "Panigaon (Village & Bridge)",
            "lat": 27.5889,
            "lon": 77.7289,
            "category": "landmark",
            "aliases": [
                        "panigaon",
                        "panigaon pul",
                        "panigaon bridge"
            ],
            "lines": [
                        "Shared Tempo / Vikram (Braj Corridor)",
                        "Shared E-Rickshaw Feeder (Toto)"
            ]
},
        {
            "name": "Sihora & Khirari (Villages)",
            "lat": 27.5211,
            "lon": 77.8389,
            "category": "landmark",
            "aliases": [
                        "sihora",
                        "khirari",
                        "itauli"
            ],
            "lines": [
                        "Shared Tempo / Vikram (Braj Corridor)"
            ]
},
        {
            "name": "Dholi Pyau (City Hub)",
            "lat": 27.4789,
            "lon": 77.6711,
            "category": "landmark",
            "aliases": [
                        "dholi pyau",
                        "dholi pyau mathura",
                        "dholi pyau railway colony"
            ],
            "lines": [
                        "Shared E-Rickshaw Feeder (Toto)",
                        "Reserved Auto-Rickshaw (निजी ऑटो)"
            ]
},
        {
            "name": "Krishna Nagar (Commercial Center)",
            "lat": 27.4989,
            "lon": 77.665,
            "category": "landmark",
            "aliases": [
                        "krishna nagar",
                        "krishna nagar mathura",
                        "krishna nagar market"
            ],
            "lines": [
                        "Shared E-Rickshaw Feeder (Toto)",
                        "Reserved Auto-Rickshaw (निजी ऑटो)"
            ]
},
        {
            "name": "Aurangabad (Mathura South)",
            "lat": 27.465,
            "lon": 77.685,
            "category": "landmark",
            "aliases": [
                        "aurangabad",
                        "aurangabad mathura",
                        "aurangabad thana"
            ],
            "lines": [
                        "Shared Tempo / Vikram (Braj Corridor)",
                        "Shared E-Rickshaw Feeder (Toto)"
            ]
},
        {
            "name": "Baad Railway Station (BAAD)",
            "lat": 27.4111,
            "lon": 77.7089,
            "category": "railway_station",
            "aliases": [
                        "baad station",
                        "baad",
                        "bad railway station",
                        "bad station mathura"
            ],
            "lines": [
                        "Northern Railway (EMU / Passenger)",
                        "Shared Tempo / Vikram (Braj Corridor)"
            ]
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
        "closed_message": "Metro service closed for the night (11 PM – 6 AM). First morning service starts at 06:00 AM.",
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
    },
    "Mumbai Suburban Railway (Western Line)": {
        "color": "#1E3A8A",
        "mode": "rail",
        "fare_type": "mumbai_local",
        "avg_speed_kmh": 42,
        "operator": "Western Railway (Suburban)"
    },
    "Mumbai Suburban Railway (Central Line)": {
        "color": "#B91C1C",
        "mode": "rail",
        "fare_type": "mumbai_local",
        "avg_speed_kmh": 40,
        "operator": "Central Railway (Suburban)"
    },
    "Mumbai Suburban Railway (Harbour Line)": {
        "color": "#047857",
        "mode": "rail",
        "fare_type": "mumbai_local",
        "avg_speed_kmh": 38,
        "operator": "Central Railway (Harbour)"
    },
    "Mumbai Metro Line 1 (Versova-Ghatkopar)": {
        "color": "#0284C7",
        "mode": "metro",
        "fare_type": "mumbai_metro",
        "avg_speed_kmh": 32,
        "operator": "MMOPL / Maha Mumbai Metro"
    },
    "Mumbai Metro Line 2A & 7": {
        "color": "#F59E0B",
        "mode": "metro",
        "fare_type": "mumbai_metro",
        "avg_speed_kmh": 35,
        "operator": "Maha Mumbai Metro (MMMOCL)"
    },
    "Mumbai Metro Line 3 (Aqua Line)": {
        "color": "#0D9488",
        "mode": "metro",
        "fare_type": "mumbai_metro",
        "avg_speed_kmh": 40,
        "operator": "MMRC Underground Aqua Line"
    },
    "BEST AC Electric Bus (Chalo Bus)": {
        "color": "#15803D",
        "mode": "bus",
        "fare_type": "best_bus",
        "avg_speed_kmh": 20,
        "operator": "Brihanmumbai Electric Supply & Transport (BEST)"
    },
    "BEST Ordinary Bus": {
        "color": "#B45309",
        "mode": "bus",
        "fare_type": "best_bus",
        "avg_speed_kmh": 18,
        "operator": "Brihanmumbai Electric Supply & Transport (BEST)"
    },
    "Maharashtra Govt Metered Auto": {
        "color": "#E68A00",
        "mode": "auto",
        "fare_type": "mumbai_auto",
        "avg_speed_kmh": 26,
        "operator": "Maharashtra Transport Dept (Regulated Meter)"
    },
    "Mumbai Metered Kaali-Peeli Taxi": {
        "color": "#EAB308",
        "mode": "taxi",
        "fare_type": "mumbai_taxi",
        "avg_speed_kmh": 30,
        "operator": "Maharashtra Transport Dept (Metered Black & Yellow Taxi)"
    },
    "Purple Line (Namma Metro)": {
        "color": "#7E22CE",
        "mode": "metro",
        "fare_type": "namma_metro",
        "avg_speed_kmh": 34,
        "operator": "Bangalore Metro Rail Corporation (BMRCL)"
    },
    "Green Line (Namma Metro)": {
        "color": "#15803D",
        "mode": "metro",
        "fare_type": "namma_metro",
        "avg_speed_kmh": 34,
        "operator": "Bangalore Metro Rail Corporation (BMRCL)"
    },
    "BMTC Vajra AC Bus": {
        "color": "#0284C7",
        "mode": "bus",
        "fare_type": "bmtc_bus",
        "avg_speed_kmh": 20,
        "operator": "Bangalore Metropolitan Transport Corporation"
    },
    "Karnataka Govt Metered Auto": {
        "color": "#E68A00",
        "mode": "auto",
        "fare_type": "bengaluru_auto",
        "avg_speed_kmh": 25,
        "operator": "Karnataka Transport Dept (Regulated Meter)"
    },
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




# ==============================================================================
# Official Maharashtra Government (Mumbai) Gazetted Tariffs & Fare Regimes
# ==============================================================================
# Regulated strictly as per Maharashtra Transport Department revised tariff (Sept 2026):
# 1. Metered Auto-Rickshaw:
#    - Minimum Fare: ₹27.00 for first 1.5 km
#    - Subsequent Rate: ₹18.22 per km
#    - Night Surcharge: 25% (12:00 AM - 5:00 AM)
# 2. Mumbai Black & Yellow Taxi (Kaali-Peeli Taxi):
#    - Minimum Fare: ₹33.00 for first 1.5 km
#    - Subsequent Rate: ₹21.90 per km
#    - Night Surcharge: 25% (12:00 AM - 5:00 AM)
#    - AC Taxi Surcharge: 10% over regular taxi fare
# 3. BEST Bus Slabs (AC Electric Chalo & Non-AC Ordinary)
# 4. Mumbai Suburban Railway (Western / Central / Harbour 2nd Class & AC Local)
# 5. Mumbai Metro (Line 1 / 2A / 7 / 3 Aqua Line)
# ==============================================================================

MAHARASHTRA_GOVT_FARES = {
    "auto_rickshaw": {
        "base_fare": 27.0,
        "base_km": 1.5,
        "per_km": 18.22,
        "night_surcharge_pct": 25,
        "night_start_hour": 0,
        "night_end_hour": 5
    },
    "kaali_peeli_taxi": {
        "base_fare": 33.0,
        "base_km": 1.5,
        "per_km": 21.90,
        "night_surcharge_pct": 25,
        "ac_surcharge_pct": 10,
        "night_start_hour": 0,
        "night_end_hour": 5
    },
    "best_bus": {
        "ac_slabs": [
            (5.0, 6.0),
            (10.0, 13.0),
            (15.0, 19.0),
            (999.0, 25.0)
        ],
        "non_ac_slabs": [
            (5.0, 5.0),
            (10.0, 10.0),
            (15.0, 15.0),
            (999.0, 20.0)
        ]
    },
    "suburban_rail": {
        "second_class": [
            (10.0, 5.0),
            (35.0, 10.0),
            (45.0, 15.0),
            (999.0, 20.0)
        ],
        "ac_local": [
            (10.0, 35.0),
            (20.0, 65.0),
            (35.0, 90.0),
            (999.0, 115.0)
        ]
    },
    "metro": {
        "slabs": [
            (3.0, 10.0),
            (12.0, 20.0),
            (18.0, 30.0),
            (25.0, 40.0),
            (999.0, 50.0)
        ]
    }
}

def calculate_mumbai_auto_fare(dist_km: float, is_night: bool = False):
    """
    Calculates official Maharashtra Transport Department regulated Auto-Rickshaw meter fare:
    - ₹27.00 for first 1.5 km (downing meter)
    - ₹18.22 per km thereafter
    - Night surcharge: 25% (12:00 AM to 5:00 AM)
    Source: Maharashtra Transport Department tariff revision, September 2026.
    """
    base_km = 1.5
    base_fare = 27.0
    per_km = 18.22
    
    if dist_km <= base_km:
        fare = base_fare
    else:
        fare = base_fare + (dist_km - base_km) * per_km
        
    if is_night:
        fare *= 1.25
        night_str = " (incl. 25% Night Surcharge 12AM-5AM)"
    else:
        night_str = ""
        
    rounded_fare = round(fare, 1)
    return float(rounded_fare), f"Maharashtra Transport Dept Meter: ₹{base_fare:.0f} (first 1.5km) + ₹{per_km:.2f}/km{night_str}"


def calculate_mumbai_taxi_fare(dist_km: float, is_ac: bool = False, is_night: bool = False):
    """
    Calculates official Mumbai Black & Yellow Taxi (Metered Kaali-Peeli Taxi) fare:
    - ₹33.00 for first 1.5 km minimum fare
    - ₹21.90 per km thereafter
    - Night surcharge: 25% (12:00 AM to 5:00 AM)
    - AC taxi surcharge: 10% over regular taxi fare
    Source: revised metered taxi tariff, September 2026.
    """
    base_km = 1.5
    base_fare = 33.0
    per_km = 21.90
    
    if dist_km <= base_km:
        fare = base_fare
    else:
        fare = base_fare + (dist_km - base_km) * per_km
        
    if is_ac:
        fare *= 1.10
        ac_str = " AC"
    else:
        ac_str = " Non-AC"
        
    if is_night:
        fare *= 1.25
        night_str = " (incl. 25% Night Surcharge 12AM-5AM)"
    else:
        night_str = ""
        
    rounded_fare = round(fare, 1)
    return float(rounded_fare), f"Mumbai Kaali-Peeli Taxi Meter{ac_str}: ₹{base_fare:.0f} (first 1.5km) + ₹{per_km:.2f}/km{night_str}"


def calculate_best_bus_fare(dist_km: float, is_electric: bool = True):
    """Calculates official BEST AC Chalo / Ordinary bus fare slabs."""
    slabs = MAHARASHTRA_GOVT_FARES["best_bus"]["ac_slabs"] if is_electric else MAHARASHTRA_GOVT_FARES["best_bus"]["non_ac_slabs"]
    bus_name = "BEST AC Electric Chalo Bus" if is_electric else "BEST Ordinary Bus"
    for max_km, fare in slabs:
        if dist_km <= max_km:
            return fare, f"{bus_name}: ₹{int(fare)} (up to {int(max_km) if max_km < 900 else 'all'} km)"
    return (25.0 if is_electric else 20.0), f"{bus_name} Max Fare"


def calculate_mumbai_local_fare(dist_km: float, is_ac: bool = False):
    """Calculates Mumbai Suburban Railway (Western/Central/Harbour) fare."""
    slabs = MAHARASHTRA_GOVT_FARES["suburban_rail"]["ac_local"] if is_ac else MAHARASHTRA_GOVT_FARES["suburban_rail"]["second_class"]
    type_name = "Mumbai Suburban AC Local" if is_ac else "Mumbai Suburban Local (2nd Class)"
    for max_km, fare in slabs:
        if dist_km <= max_km:
            return fare, f"{type_name}: ₹{int(fare)}"
    return (115.0 if is_ac else 20.0), f"{type_name} Max Fare"


def calculate_mumbai_metro_fare(dist_km: float):
    """Calculates Mumbai Metro (MMRDA / MMRC Line 3 Aqua Line) fare."""
    slabs = MAHARASHTRA_GOVT_FARES["metro"]["slabs"]
    for max_km, fare in slabs:
        if dist_km <= max_km:
            return fare, f"Mumbai Metro (MMRDA/MMRC Slab): ₹{int(fare)}"
    return 50.0, "Mumbai Metro Max Fare"


# ==============================================================================
# Official Karnataka Government (Bengaluru) Gazetted Tariffs & Fare Regimes
# ==============================================================================

KARNATAKA_GOVT_FARES = {
    "auto_rickshaw": {
        "base_fare": 30.0,
        "base_km": 2.0,
        "per_km": 15.0,
        "night_surcharge_pct": 50,
        "night_start_hour": 22,
        "night_end_hour": 6
    },
    "bmtc_bus": {
        "vajra_ac_slabs": [
            (3.0, 10.0),
            (7.0, 15.0),
            (12.0, 20.0),
            (18.0, 25.0),
            (25.0, 30.0),
            (999.0, 35.0)
        ],
        "ordinary_slabs": [
            (2.0, 5.0),
            (6.0, 10.0),
            (11.0, 15.0),
            (17.0, 20.0),
            (999.0, 25.0)
        ]
    },
    "namma_metro": {
        "slabs": [
            (3.0, 10.0),
            (6.0, 15.0),
            (10.0, 25.0),
            (15.0, 35.0),
            (25.0, 50.0),
            (999.0, 60.0)
        ]
    }
}

def calculate_bengaluru_auto_fare(dist_km: float, is_night: bool = False):
    base_km = 2.0
    base_fare = 30.0
    per_km = 15.0
    fare = base_fare if dist_km <= base_km else base_fare + (dist_km - base_km) * per_km
    night_str = ""
    if is_night:
        fare *= 1.5
        night_str = " (incl. 50% Karnataka Govt Night Surcharge 10PM-6AM)"
    return float(round(fare, 1)), f"Karnataka Transport Dept Meter: ₹{base_fare:.0f} (first 2km) + ₹{per_km:.0f}/km{night_str}"


def calculate_bmtc_bus_fare(dist_km: float, is_vajra: bool = True):
    slabs = KARNATAKA_GOVT_FARES["bmtc_bus"]["vajra_ac_slabs"] if is_vajra else KARNATAKA_GOVT_FARES["bmtc_bus"]["ordinary_slabs"]
    name = "BMTC Vajra AC Bus" if is_vajra else "BMTC Ordinary Bus"
    for max_km, fare in slabs:
        if dist_km <= max_km:
            return fare, f"{name}: ₹{int(fare)}"
    return 35.0 if is_vajra else 25.0, f"{name} Max Fare"


def calculate_namma_metro_fare(dist_km: float):
    for max_km, fare in KARNATAKA_GOVT_FARES["namma_metro"]["slabs"]:
        if dist_km <= max_km:
            return fare, f"Namma Metro (BMRCL Slab): ₹{int(fare)}"
    return 60.0, "Namma Metro Max Fare"
