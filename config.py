""" contains configuration settings for the application """

from pathlib import Path

#-----------------------
#Analysis Cut offs
#-----------------------
CAPTURE_START_DATE = "2020-06-09" #TODO: IS A STRING OKAY?
CAPTURE_END_DATE = "2026-07-25" #TODO: IMPLEMENT A STABLE WAY TO SET THIS and decide on a time period to end analysis

#-----------------------
# Directory locations
#-----------------------
BASE_DIR = Path(__file__).resolve().parent
RAW_DATA_DIR = BASE_DIR / "raw_data"
PROCESSED_DATA_DIR = BASE_DIR / "processed_data"
ANALYSIS_DATA_DIR = BASE_DIR / "analysis_data"

#-----------------------
# Cache & Timeouts
#-----------------------
CACHE_DURATION_MS = 86400000
API_TIMEOUT_SECONDS = 10
API_CALL_SLEEP = 1.5

#-----------------------
# Supported API endpoints
#-----------------------
OSRS_WIKI_API = "https://oldschool.runescape.wiki/api.php"

OSRS_GEMW_CPI_ENDPOINTS = {
    "Common Trade Index":
        "https://api.weirdgloop.org/exchange/history/osrs/all?id=GE%20Common%20Trade%20Index",
    "Rune Index":
        "https://api.weirdgloop.org/exchange/history/osrs/all?id=GE%20Rune%20Index",
    "Log Index":
        "https://api.weirdgloop.org/exchange/history/osrs/all?id=GE%20Log%20Index",
    "Food Index":
        "https://api.weirdgloop.org/exchange/history/osrs/all?id=GE%20Food%20Index",
    "Metal Index":
        "https://api.weirdgloop.org/exchange/history/osrs/all?id=GE%20Metal%20Index",
    "Herb Index":
        "https://api.weirdgloop.org/exchange/history/osrs/all?id=GE%20Herb%20Index"
}

SUPPORTED_INDEX_LIST= OSRS_GEMW_CPI_ENDPOINTS.keys()

#-----------------------
# Exogenous events
#-----------------------
"""
EXOGENOUS_EVENT_CATEGORIES = {
    "Economy": [
        "Grand Exchange",
        "Tax",
        "Item Sink",
        "Drop Rates",
        "Trade"
        "Bank"
    ],

    "Combat": [
        #generic
        "Weapon",
        "Armour",
        "Combat",
        "Slayer",
        "Spellbook",
        "Prayer",
        "Special Attack",
        #pvp
        "Bouny Hunter",
        "Wilderness",
        "PvP",
        #bosses
        "Ahrim",
        "Karil",
        "Torag",
        "Dharok",
        "Guthan",
        "Verac",
        "Gemstone Crab",
        "Scurrius",
        "Giant mole",
        "Deranged archaeologist",
        "Dagannoth kings",
        "Dagannoth supereme",
        "Dagannoth rex",
        "Dagannoth prime",
        "Sarachnis",
        "Blood moon",
        "Blue moon",
        "Eclipse moon",
        "moons of peril",
        "kalphite queen",
        "kree'arra",
        "commander Ziliyana",
        "K'ril tsutsaroth",
        "Hueycoatl",
        "corporeal beast",
        "wilderness bosses",
        "chaos fanatic",
        "crazy archaeologist",
        "scorpia",
        "king black dragon",
        "kbd",
        "chaos elemental",
        "revenant maledictus",
        "calavar'ion",
        "vet'ion",
        "spindel",
        "venenatis",
        "artio",
        "callisto",
        "brutus",
        "demonic brutus",
        "obor",
        "amoxliatl",
        "royal titans",
        "doom of mokhaiotl",
        "zulrah",
        "vorkath",
        "muspah",
        "Chambers of Xeric",
        "Tombs of Amascut",
        "Theater of Blood",
        "the nightmare",
        "Nex",
        "God Wars",
        "yama",
        "duke sucullus",
        "leviathan",
        "whiperer",
        "vardorvis",
        "the forgotten four",
        "mimic",
        "hespori",
        "skotizo",
        "shellbane gryphon",
        "groutesque gardians",
        "abyssal sire",
        "kraken",
        "cerberus",
        "araxxor",
        "thermonuclear smoke devil",
        "alchemical hydra",
        "gauntlet",
        "hunllef",
        "Jad",
        "Zuk",
        "fight cave",
        "inferno",
        "Sol Heredit",
        "colosseum",
        "temopoross",
        "wintertodt",
        "zolcano",
        "tekton",
        "vanguard",
        "vespula",
        "vasa",
        "muttadile",
        "olm",
        "maiden",
        "pestilent bloat",
        "nycolas",
        "sotetseg",
        "xarpus",
        "verzik",
        "akkha",
        "ba-ba",
        "kephri",
        "zebak",
        "tumeken's warden",
        "elidinis' warden"

    ],
   
    "Resource": [
        "Mining",
        "Fishing",
        "Woodcutting",
        "Farming",
        "Herblore",
        "yield",

    ],

    "Seasonal": [
        "Christmas",
        "Halloween",
        "Easter",
        "Birthday"
    ],

    "Content": [
        "Quest",
        "Dungeon",
        "Area",
        "Achievement"
    ],

    "QoL": [
        "QoL",
        "Quality",
        "Fix",
        "Bug"
    ],

    "Poll" :[
        "poll"
    ],

    "Multi" : [
        "multiple"
    ],

    "Other" : [
        "other"
    ]
}
"""

EXOGENOUS_EVENT_CATEGORIES = [
    "Other",
    "New Content",
    "Content Update",
    "Balance Change",
    "Economy Change",
    "Resource Change",
    "Seasonal Event",
    "QoL Update",
    "Bug Fix",
    "Multiple",
]

EVENT_SCOPE = [
    "No Economic Scope",
    "Specific Item",
    "Item Group",
    "Skill Market",
    "Whole Economy",

]

ECONOMIC_EFFECTS = [
    "No Expected Impact",
    "New Item",
    "Item Supply Change",
    "Item Demand Change",
    "Resource Availability Change",
    "New Resource",
    "Drop Rate Change",
    "Temporary Demand",
]
