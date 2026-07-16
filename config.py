""" contains configuration settings for the application """

from pathlib import Path


#-----------------------
# Directory locations
#-----------------------
BASE_DIR = Path(__file__).resolve().parent
RAW_DATA_DIR = BASE_DIR / "raw_data"
PROCESSED_DATA_DIR = BASE_DIR / "processed_data"


#-----------------------
# Cache & Timeouts
#-----------------------
CACHE_DURATION_MS = 86400000
API_TIMEOUT_SECONDS = 10


#-----------------------
# Supported CPI Indecies from OSRS GE MW API
#-----------------------

API_ENDPOINTS = {
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

SUPPORTED_INDEX_LIST = API_ENDPOINTS.keys()
