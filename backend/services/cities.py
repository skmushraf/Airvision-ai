"""
AirVision AI — City Catalog
===========================
Static catalog of every monitored city with latitude/longitude, country,
country code and continent. Coordinates are real geographic coordinates
(not dummy data) and are used for both the OpenWeather API calls and the
interactive global map.
"""

# Continents: AS=Asia, EU=Europe, NA=North America, SA=South America,
#             AF=Africa, OC=Oceania, ME=Middle East
CITIES = [
    # ---------------- India (Asia) ----------------
    {"id": "delhi",          "name": "Delhi",           "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 28.6139,  "lon": 77.2090},
    {"id": "mumbai",         "name": "Mumbai",          "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 19.0760,  "lon": 72.8777},
    {"id": "bengaluru",      "name": "Bengaluru",       "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 12.9716,  "lon": 77.5946},
    {"id": "hyderabad",      "name": "Hyderabad",       "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 17.3850,  "lon": 78.4867},
    {"id": "guntur",         "name": "Guntur",          "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 16.3067,  "lon": 80.4365},
    {"id": "tenali",         "name": "Tenali",          "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 16.2438,  "lon": 80.6463},
    {"id": "kadapa",         "name": "Kadapa",          "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 14.4674,  "lon": 78.8241},
    {"id": "bapatla",        "name": "Bapatla",         "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 15.9041,  "lon": 80.4673},
    {"id": "ponnur",         "name": "Ponnur",          "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 16.0711,  "lon": 80.5494},
    {"id": "chirala",        "name": "Chirala",         "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 15.8239,  "lon": 80.3521},
    {"id": "chennai",        "name": "Chennai",         "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 13.0827,  "lon": 80.2707},
    {"id": "kolkata",        "name": "Kolkata",         "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 22.5726,  "lon": 88.3639},
    {"id": "pune",           "name": "Pune",            "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 18.5204,  "lon": 73.8567},
    {"id": "ahmedabad",      "name": "Ahmedabad",       "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 23.0225,  "lon": 72.5714},
    {"id": "jaipur",         "name": "Jaipur",          "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 26.9124,  "lon": 75.7873},
    {"id": "lucknow",        "name": "Lucknow",         "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 26.8467,  "lon": 80.9462},
    {"id": "visakhapatnam",  "name": "Visakhapatnam",   "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 17.6868,  "lon": 83.2185},
    {"id": "vijayawada",     "name": "Vijayawada",      "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 16.5062,  "lon": 80.6480},
    {"id": "nagpur",         "name": "Nagpur",          "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 21.1458,  "lon": 79.0882},
    {"id": "indore",         "name": "Indore",          "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 22.7196,  "lon": 75.8577},
    {"id": "kochi",          "name": "Kochi",           "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 9.9312,   "lon": 76.2673},
    {"id": "patna",          "name": "Patna",           "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 25.5941,  "lon": 85.1376},
    {"id": "bhopal",         "name": "Bhopal",          "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 23.2599,  "lon": 77.4126},
    {"id": "chandigarh",     "name": "Chandigarh",      "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 30.7333,  "lon": 76.7794},
    {"id": "bhubaneswar",    "name": "Bhubaneswar",     "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 20.2961,  "lon": 85.8245},
    {"id": "surat",          "name": "Surat",           "country": "India",          "cc": "IN", "continent": "Asia",          "lat": 21.1702,  "lon": 72.8311},

    # ---------------- North America ----------------
    {"id": "new-york",       "name": "New York",        "country": "United States",  "cc": "US", "continent": "North America", "lat": 40.7128,  "lon": -74.0060},
    {"id": "los-angeles",    "name": "Los Angeles",     "country": "United States",  "cc": "US", "continent": "North America", "lat": 34.0522,  "lon": -118.2437},
    {"id": "toronto",        "name": "Toronto",         "country": "Canada",         "cc": "CA", "continent": "North America", "lat": 43.6532,  "lon": -79.3832},
    {"id": "mexico-city",    "name": "Mexico City",     "country": "Mexico",         "cc": "MX", "continent": "North America", "lat": 19.4326,  "lon": -99.1332},

    # ---------------- South America ----------------
    {"id": "sao-paulo",      "name": "São Paulo",       "country": "Brazil",         "cc": "BR", "continent": "South America", "lat": -23.5505, "lon": -46.6333},
    {"id": "buenos-aires",   "name": "Buenos Aires",    "country": "Argentina",      "cc": "AR", "continent": "South America", "lat": -34.6037, "lon": -58.3816},
    {"id": "lima",           "name": "Lima",            "country": "Peru",           "cc": "PE", "continent": "South America", "lat": -12.0464, "lon": -77.0428},

    # ---------------- Europe ----------------
    {"id": "london",         "name": "London",          "country": "United Kingdom", "cc": "GB", "continent": "Europe",       "lat": 51.5074,  "lon": -0.1278},
    {"id": "paris",          "name": "Paris",           "country": "France",         "cc": "FR", "continent": "Europe",       "lat": 48.8566,  "lon": 2.3522},
    {"id": "berlin",         "name": "Berlin",          "country": "Germany",        "cc": "DE", "continent": "Europe",       "lat": 52.5200,  "lon": 13.4050},
    {"id": "madrid",         "name": "Madrid",          "country": "Spain",          "cc": "ES", "continent": "Europe",       "lat": 40.4168,  "lon": -3.7038},
    {"id": "rome",           "name": "Rome",            "country": "Italy",          "cc": "IT", "continent": "Europe",       "lat": 41.9028,  "lon": 12.4964},
    {"id": "amsterdam",      "name": "Amsterdam",       "country": "Netherlands",    "cc": "NL", "continent": "Europe",       "lat": 52.3676,  "lon": 4.9041},
    {"id": "moscow",         "name": "Moscow",          "country": "Russia",         "cc": "RU", "continent": "Europe",       "lat": 55.7558,  "lon": 37.6173},

    # ---------------- Middle East ----------------
    {"id": "dubai",          "name": "Dubai",           "country": "UAE",            "cc": "AE", "continent": "Middle East",  "lat": 25.2048,  "lon": 55.2708},
    {"id": "riyadh",         "name": "Riyadh",          "country": "Saudi Arabia",   "cc": "SA", "continent": "Middle East",  "lat": 24.7136,  "lon": 46.6753},
    {"id": "doha",           "name": "Doha",            "country": "Qatar",          "cc": "QA", "continent": "Middle East",  "lat": 25.2854,  "lon": 51.5310},

    # ---------------- Africa ----------------
    {"id": "cairo",          "name": "Cairo",           "country": "Egypt",          "cc": "EG", "continent": "Africa",       "lat": 30.0444,  "lon": 31.2357},
    {"id": "lagos",          "name": "Lagos",           "country": "Nigeria",        "cc": "NG", "continent": "Africa",       "lat": 6.5244,   "lon": 3.3792},
    {"id": "nairobi",        "name": "Nairobi",         "country": "Kenya",          "cc": "KE", "continent": "Africa",       "lat": -1.2921,  "lon": 36.8219},
    {"id": "johannesburg",   "name": "Johannesburg",    "country": "South Africa",   "cc": "ZA", "continent": "Africa",       "lat": -26.2041, "lon": 28.0473},

    # ---------------- Asia (rest) ----------------
    {"id": "beijing",        "name": "Beijing",         "country": "China",          "cc": "CN", "continent": "Asia",         "lat": 39.9042,  "lon": 116.4074},
    {"id": "shanghai",       "name": "Shanghai",        "country": "China",          "cc": "CN", "continent": "Asia",         "lat": 31.2304,  "lon": 121.4737},
    {"id": "tokyo",          "name": "Tokyo",           "country": "Japan",          "cc": "JP", "continent": "Asia",         "lat": 35.6762,  "lon": 139.6503},
    {"id": "seoul",          "name": "Seoul",           "country": "South Korea",    "cc": "KR", "continent": "Asia",         "lat": 37.5665,  "lon": 126.9780},
    {"id": "bangkok",        "name": "Bangkok",         "country": "Thailand",       "cc": "TH", "continent": "Asia",         "lat": 13.7563,  "lon": 100.5018},
    {"id": "singapore",      "name": "Singapore",       "country": "Singapore",      "cc": "SG", "continent": "Asia",         "lat": 1.3521,   "lon": 103.8198},
    {"id": "kuala-lumpur",   "name": "Kuala Lumpur",    "country": "Malaysia",       "cc": "MY", "continent": "Asia",         "lat": 3.1390,   "lon": 101.6869},
    {"id": "jakarta",        "name": "Jakarta",         "country": "Indonesia",      "cc": "ID", "continent": "Asia",         "lat": -6.2088,  "lon": 106.8456},

    # ---------------- Oceania ----------------
    {"id": "sydney",         "name": "Sydney",          "country": "Australia",      "cc": "AU", "continent": "Oceania",      "lat": -33.8688, "lon": 151.2093},
    {"id": "melbourne",      "name": "Melbourne",       "country": "Australia",      "cc": "AU", "continent": "Oceania",      "lat": -37.8136, "lon": 144.9631},
    {"id": "auckland",       "name": "Auckland",        "country": "New Zealand",    "cc": "NZ", "continent": "Oceania",      "lat": -36.8485, "lon": 174.7633},
]

CITY_INDEX = {c["id"]: c for c in CITIES}
COUNTRIES = sorted({c["country"] for c in CITIES})


def get_city(city_id: str):
    """Look up a city by its slug id."""
    return CITY_INDEX.get(city_id)


# ---------------------------------------------------------------------------
# CPCB (data.gov.in) name reconciliation
# ---------------------------------------------------------------------------
# The CPCB feed labels cities slightly differently from our catalog. Two
# distinct mechanisms, deliberately kept apart so data is never misattributed:
#
#   CPCB_ALIASES  — genuine alternative spellings of the SAME city. Readings
#                   are attributed to the city directly.
#   CPCB_NEAREST  — towns with no CPCB monitoring station of their own. We may
#                   borrow the nearest monitored city's reading, but the record
#                   is flagged (`cpcb_proxy: True` + a note naming the station
#                   city) so the UI never pretends it is a local measurement.
CPCB_ALIASES = {
    "bengaluru": ["Bengaluru", "Bangalore"],
    "kochi": ["Kochi", "Ernakulam", "Eloor"],
    "visakhapatnam": ["Visakhapatnam", "Vishakhapatnam", "Vizag"],
    "vijayawada": ["Vijayawada", "Bezawada"],
    "delhi": ["Delhi", "New Delhi"],
    "mumbai": ["Mumbai", "Navi Mumbai", "Bombay"],
    "chennai": ["Chennai", "Madras"],
    "kolkata": ["Kolkata", "Calcutta"],
    "patna": ["Patna"],
    "bhubaneswar": ["Bhubaneswar", "Bhubaneshwar"],
    "chandigarh": ["Chandigarh"],
}

# town id → monitored CPCB city used as a proxy (clearly labelled in the UI)
CPCB_NEAREST = {
    "guntur": "Amaravati",
    "tenali": "Amaravati",
    "ponnur": "Amaravati",
    "bapatla": "Amaravati",
    "chirala": "Amaravati",
    "kadapa": "Tirupati",
}


def cpcb_lookup_names(city: dict) -> list:
    """Exact CPCB names to try for a catalog city (no proxies)."""
    return CPCB_ALIASES.get(city["id"], [city["name"]])


def cpcb_proxy_name(city: dict):
    """Nearest monitored CPCB city for a town with no station, else None."""
    return CPCB_NEAREST.get(city["id"])


def get_city_by_name(name: str):
    """Case-insensitive lookup by display name."""
    needle = name.strip().lower()
    for c in CITIES:
        if c["name"].lower() == needle or c["id"] == needle:
            return c
    return None


def search_cities(query: str, limit: int = 10) -> list:
    """Search cities by name, country or country code."""
    q = query.strip().lower()
    if not q:
        return CITIES[:limit]
    return [
        c for c in CITIES
        if q in c["name"].lower()
        or q in c["country"].lower()
        or q in c["cc"].lower()
    ][:limit]


def cities_by_country(country: str) -> list:
    return [c for c in CITIES if c["country"].lower() == country.lower()]


def cities_by_continent(continent: str) -> list:
    return [c for c in CITIES if c["continent"].lower() == continent.lower()]
