"""Reference data for the synthetic Games operations sample.

National committee codes and country names are public three-letter codes. Everything
else (venues, athletes, assets, suppliers, thresholds) is fictional.
"""

# (code, name, region, winter_strength 0..1)
NOCS = [
    ("NOR", "Norway", "Europe", 1.00), ("GER", "Germany", "Europe", 0.95),
    ("USA", "United States", "Americas", 0.90), ("CAN", "Canada", "Americas", 0.88),
    ("AUT", "Austria", "Europe", 0.86), ("SUI", "Switzerland", "Europe", 0.84),
    ("SWE", "Sweden", "Europe", 0.82), ("NED", "Netherlands", "Europe", 0.80),
    ("FRA", "France", "Europe", 0.78), ("ITA", "Italy", "Europe", 0.76),
    ("JPN", "Japan", "Asia", 0.72), ("KOR", "Republic of Korea", "Asia", 0.68),
    ("CHN", "China", "Asia", 0.70), ("FIN", "Finland", "Europe", 0.66),
    ("CZE", "Czechia", "Europe", 0.60), ("SLO", "Slovenia", "Europe", 0.58),
    ("POL", "Poland", "Europe", 0.52), ("GBR", "Great Britain", "Europe", 0.50),
    ("AUS", "Australia", "Oceania", 0.45), ("NZL", "New Zealand", "Oceania", 0.40),
    ("EST", "Estonia", "Europe", 0.38), ("LAT", "Latvia", "Europe", 0.38),
    ("SVK", "Slovakia", "Europe", 0.36), ("BEL", "Belgium", "Europe", 0.34),
    ("ESP", "Spain", "Europe", 0.32), ("KAZ", "Kazakhstan", "Asia", 0.32),
    ("UKR", "Ukraine", "Europe", 0.34), ("BUL", "Bulgaria", "Europe", 0.26),
    ("ROU", "Romania", "Europe", 0.24), ("CRO", "Croatia", "Europe", 0.24),
    ("DEN", "Denmark", "Europe", 0.22), ("HUN", "Hungary", "Europe", 0.22),
    ("LTU", "Lithuania", "Europe", 0.18), ("ISL", "Iceland", "Europe", 0.14),
    ("AND", "Andorra", "Europe", 0.12), ("LIE", "Liechtenstein", "Europe", 0.16),
    ("GEO", "Georgia", "Europe", 0.14), ("ARG", "Argentina", "Americas", 0.12),
    ("BRA", "Brazil", "Americas", 0.10), ("MEX", "Mexico", "Americas", 0.08),
]

# Venues. wind_limit_ms / density limit are synthetic operating thresholds used by the
# manuals, the ontology rules and the evaluation questions; they are not real federation rules.
# (venue_id, name, cluster, environment, capacity, gates, wind_limit_ms or None)
VENUES = [
    ("V01", "Valmont Ice Arena", "Valmont Ice Cluster", "indoor", 11000, 6, None),
    ("V02", "Valmont Skating Oval", "Valmont Ice Cluster", "indoor", 7500, 4, None),
    ("V03", "Figure Skating Palace", "Valmont Ice Cluster", "indoor", 9000, 5, None),
    ("V04", "Valmont Curling Centre", "Valmont Ice Cluster", "indoor", 3500, 3, None),
    ("V05", "Ridge Biathlon Stadium", "Ridge Mountain Cluster", "outdoor", 12000, 5, 12.0),
    ("V06", "Ridge Nordic Centre", "Ridge Mountain Cluster", "outdoor", 10000, 4, 14.0),
    ("V07", "Ridge Ski Jumping Hill", "Ridge Mountain Cluster", "outdoor", 8000, 4, 4.5),
    ("V08", "Summit Alpine Centre", "Summit Mountain Cluster", "outdoor", 9000, 4, 15.0),
    ("V09", "Summit Snow Park", "Summit Mountain Cluster", "outdoor", 6000, 3, 10.0),
    ("V10", "Summit Sliding Centre", "Summit Mountain Cluster", "outdoor", 5000, 3, 16.0),
]

CROWD_DENSITY_LIMIT = 4.0  # persons per square metre, sustained 5 minutes (synthetic)

# (discipline_code, discipline, sport, venue_id, kind)  kind: timed | judged | team | distance
DISCIPLINES = [
    ("BTH", "Biathlon", "Biathlon", "V05", "timed"),
    ("CCS", "Cross-Country Skiing", "Skiing", "V06", "timed"),
    ("SJP", "Ski Jumping", "Skiing", "V07", "judged"),
    ("ALP", "Alpine Skiing", "Skiing", "V08", "timed"),
    ("SBD", "Snowboard", "Skiing", "V09", "judged"),
    ("SSK", "Speed Skating", "Skating", "V02", "timed"),
    ("FSK", "Figure Skating", "Skating", "V03", "judged"),
    ("IHO", "Ice Hockey", "Ice Hockey", "V01", "team"),
    ("CUR", "Curling", "Curling", "V04", "team"),
    ("BOB", "Bobsleigh and Luge", "Sliding", "V10", "timed"),
]

# (event_code, discipline_code, name, gender, team_event, medal_day, has_qualification)
EVENTS = [
    ("BTH-M20I", "BTH", "Men's 20 km Individual", "M", False, 3, False),
    ("BTH-W15I", "BTH", "Women's 15 km Individual", "W", False, 4, False),
    ("BTH-M10S", "BTH", "Men's 10 km Sprint", "M", False, 5, False),
    ("BTH-W75S", "BTH", "Women's 7.5 km Sprint", "W", False, 6, False),
    ("BTH-M125P", "BTH", "Men's 12.5 km Pursuit", "M", False, 8, False),
    ("BTH-W10P", "BTH", "Women's 10 km Pursuit", "W", False, 9, False),
    ("BTH-XREL", "BTH", "Mixed Relay", "X", True, 12, False),
    ("CCS-M10", "CCS", "Men's 10 km Classic", "M", False, 2, False),
    ("CCS-W10", "CCS", "Women's 10 km Classic", "W", False, 3, False),
    ("CCS-MSP", "CCS", "Men's Sprint Free", "M", False, 6, True),
    ("CCS-WSP", "CCS", "Women's Sprint Free", "W", False, 7, True),
    ("SJP-MNH", "SJP", "Men's Normal Hill Individual", "M", False, 3, True),
    ("SJP-WNH", "SJP", "Women's Normal Hill Individual", "W", False, 6, True),
    ("SJP-MLH", "SJP", "Men's Large Hill Individual", "M", False, 10, True),
    ("ALP-MDH", "ALP", "Men's Downhill", "M", False, 2, False),
    ("ALP-WDH", "ALP", "Women's Downhill", "W", False, 4, False),
    ("ALP-MGS", "ALP", "Men's Giant Slalom", "M", False, 7, False),
    ("ALP-WGS", "ALP", "Women's Giant Slalom", "W", False, 8, False),
    ("ALP-MSL", "ALP", "Men's Slalom", "M", False, 11, False),
    ("ALP-WSL", "ALP", "Women's Slalom", "W", False, 12, False),
    ("SBD-MHP", "SBD", "Men's Halfpipe", "M", False, 5, True),
    ("SBD-WHP", "SBD", "Women's Halfpipe", "W", False, 6, True),
    ("SBD-MSS", "SBD", "Men's Slopestyle", "M", False, 9, True),
    ("SBD-WSS", "SBD", "Women's Slopestyle", "W", False, 10, True),
    ("SSK-M500", "SSK", "Men's 500 m", "M", False, 4, False),
    ("SSK-W500", "SSK", "Women's 500 m", "W", False, 5, False),
    ("SSK-M1500", "SSK", "Men's 1500 m", "M", False, 9, False),
    ("SSK-W1500", "SSK", "Women's 1500 m", "W", False, 10, False),
    ("FSK-MS", "FSK", "Men's Single Skating", "M", False, 7, True),
    ("FSK-WS", "FSK", "Women's Single Skating", "W", False, 11, True),
    ("FSK-PR", "FSK", "Pair Skating", "X", False, 9, True),
    ("IHO-M", "IHO", "Men's Tournament", "M", True, 14, False),
    ("IHO-W", "IHO", "Women's Tournament", "W", True, 13, False),
    ("CUR-M", "CUR", "Men's Tournament", "M", True, 13, False),
    ("CUR-W", "CUR", "Women's Tournament", "W", True, 12, False),
    ("CUR-XD", "CUR", "Mixed Doubles", "X", True, 6, False),
    ("BOB-2M", "BOB", "Two-man Bobsleigh", "M", True, 12, False),
    ("BOB-WMB", "BOB", "Women's Monobob", "W", False, 10, False),
    ("BOB-MLS", "BOB", "Men's Luge Singles", "M", False, 6, False),
    ("BOB-WLS", "BOB", "Women's Luge Singles", "W", False, 7, False),
]

# (asset_type, criticality, monitored, count_range, applies_to: "all" | "indoor" | "outdoor" | discipline list)
ASSET_TYPES = [
    ("Timing and scoring system", "Critical", False, (1, 2), "all"),
    ("Venue scoreboard", "High", False, (1, 2), "all"),
    ("Public address system", "High", False, (1, 1), "all"),
    ("Broadcast camera position", "Medium", False, (3, 6), "all"),
    ("Medical station", "Critical", False, (1, 2), "all"),
    ("Turnstile bank", "High", False, (2, 3), "all"),
    ("Floodlight rig", "High", False, (2, 4), "all"),
    ("Backup generator", "Critical", True, (1, 1), "all"),
    ("Ice refrigeration plant", "Critical", True, (1, 1), "indoor"),
    ("Ice resurfacer", "High", False, (2, 3), "indoor"),
    ("HVAC and dehumidification unit", "High", True, (1, 2), "indoor"),
    ("Snowmaking unit", "High", True, (2, 4), "outdoor"),
    ("Weather station", "Critical", True, (1, 1), "outdoor"),
    ("Safety netting section", "Critical", False, (2, 4), ["ALP", "SBD", "SJP"]),
    ("Track refrigeration plant", "Critical", True, (1, 1), ["BOB"]),
    ("Shooting range target system", "Critical", False, (1, 1), ["BTH"]),
    ("Inrun and landing grooming unit", "High", False, (1, 2), ["SJP"]),
]

SUPPLIERS = [
    ("SUP01", "Alpenline Timing (fictional)", "Timing and scoring"),
    ("SUP02", "Northwind Displays (fictional)", "Displays and audio"),
    ("SUP03", "ClearView Broadcast Services (fictional)", "Broadcast"),
    ("SUP04", "MedAlpine Services (fictional)", "Medical"),
    ("SUP05", "GateFlow Systems (fictional)", "Access control"),
    ("SUP06", "Lumen Event Lighting (fictional)", "Lighting"),
    ("SUP07", "PowerSure Energy (fictional)", "Power"),
    ("SUP08", "Glacier Ice Engineering (fictional)", "Refrigeration"),
    ("SUP09", "Polar Fleet Equipment (fictional)", "Ice and snow equipment"),
    ("SUP10", "AirCore Climate (fictional)", "HVAC"),
    ("SUP11", "SnowTech Mountain (fictional)", "Snowmaking"),
    ("SUP12", "MeteoPeak Instruments (fictional)", "Weather"),
    ("SUP13", "SafeSlope Barriers (fictional)", "Safety netting"),
    ("SUP14", "TargetLine Range Systems (fictional)", "Shooting range"),
    ("SUP15", "SlopeWorks Grooming (fictional)", "Grooming"),
]

ASSET_SUPPLIER = {
    "Timing and scoring system": "SUP01", "Venue scoreboard": "SUP02",
    "Public address system": "SUP02", "Broadcast camera position": "SUP03",
    "Medical station": "SUP04", "Turnstile bank": "SUP05", "Floodlight rig": "SUP06",
    "Backup generator": "SUP07", "Ice refrigeration plant": "SUP08",
    "Ice resurfacer": "SUP09", "HVAC and dehumidification unit": "SUP10",
    "Snowmaking unit": "SUP11", "Weather station": "SUP12",
    "Safety netting section": "SUP13", "Track refrigeration plant": "SUP08",
    "Shooting range target system": "SUP14", "Inrun and landing grooming unit": "SUP15",
}

FIRST_NAMES = ["Alex", "Sam", "Robin", "Kim", "Jo", "Noa", "Mika", "Eli", "Ari", "Toni",
               "Lou", "Charlie", "Remy", "Sasha", "Nico", "Jules", "Kai", "Luca", "Mara", "Ines",
               "Lena", "Oskar", "Freya", "Emil", "Ida", "Hugo", "Elin", "Milo", "Vera", "Anton",
               "Livia", "Tomas", "Hanna", "Jonas", "Sofia", "Matteo", "Clara", "Felix", "Nora", "Leon"]
LAST_NAMES = ["Alder", "Birchwood", "Calloway", "Dunmore", "Eastwick", "Fairholm", "Glenrock",
              "Hartfield", "Ivers", "Jansby", "Kestrel", "Lindqvist", "Marlowe", "Northcote",
              "Oakridge", "Pembrook", "Quarrie", "Rosslyn", "Stenvik", "Thornby", "Ulvsund",
              "Valecourt", "Westerly", "Ystad", "Zellweg", "Brightwater", "Coldbrook", "Frostvik",
              "Hallström", "Moorland", "Snowden", "Winterberg", "Ashgrove", "Stillwater", "Ravensby"]

INSPECTORS = ["Inspector A. Marlowe", "Inspector K. Ivers", "Inspector T. Rosslyn",
              "Inspector J. Fairholm", "Inspector M. Stenvik", "Inspector L. Quarrie"]
