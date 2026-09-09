""" contains configuration settings for the application """

from pathlib import Path
from datetime import date

#-----------------------
#Analysis Cut offs
#-----------------------
OSRS_RELEASE_DATE = date(2013,2,17)
OSRS_GE_DATA_START_DATE = date(2020, 6, 9)

#TODO: IMPLEMENT A STABLE WAY TO SET THIS and decide on a time period to end analysis
CAPTURE_END_DATE = date(2026,7,27) 

#-----------------------
# Directory locations
#-----------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"
STREAMLIT_DIR =  PROJECT_ROOT / "streamlit"

RAW_DATA_DIR = DATA_DIR / "raw_data"
PROCESSED_DATA_DIR = DATA_DIR / "processed_data"
ANALYSIS_DATA_DIR = DATA_DIR / "analysis_data"

METADATA_JSON = DATA_DIR / "metadata" / "metadata.json"

EVENTS_MASTER_DATA = ANALYSIS_DATA_DIR / "events index.csv"
ECONOMY_MASTER_DATA = ANALYSIS_DATA_DIR / "master.csv"
RETURNS_DATA = ANALYSIS_DATA_DIR / "returns.csv"
SQ_RETURNS_DATA = ANALYSIS_DATA_DIR / "sq_returns.csv"

VOL7_DATA = ANALYSIS_DATA_DIR / "vol_7.csv"
VOL30_DATA = ANALYSIS_DATA_DIR / "vol_30.csv"

ADF_DATA = ANALYSIS_DATA_DIR / "adf_data.csv"
LM_DATA = ANALYSIS_DATA_DIR / "lm_data.csv"


 
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
    "common trade index":
        "https://api.weirdgloop.org/exchange/history/osrs/all?id=GE%20Common%20Trade%20Index",
    "rune index":
        "https://api.weirdgloop.org/exchange/history/osrs/all?id=GE%20Rune%20Index",
    "log index":
        "https://api.weirdgloop.org/exchange/history/osrs/all?id=GE%20Log%20Index",
    "food index":
        "https://api.weirdgloop.org/exchange/history/osrs/all?id=GE%20Food%20Index",
    "metal index":
        "https://api.weirdgloop.org/exchange/history/osrs/all?id=GE%20Metal%20Index",
    "herb index":
        "https://api.weirdgloop.org/exchange/history/osrs/all?id=GE%20Herb%20Index"
}

SUPPORTED_INDEX_LIST= OSRS_GEMW_CPI_ENDPOINTS.keys()

#-----------------------
# Exogenous events
#-----------------------
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
