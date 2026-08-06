""" builds csv files on application init"""

ECONOMY_MASTER_SCHEMA = [
    "date",
    "common trade index",
    "rune index,log index",
    "food index",
    "metal index",
    "herb index"
    ]

UPDATES_MASTER_SCHEMA = [
    "date",
    "title",
    "category",
    "scope",
    "no expected Impact",
    "new item",
    "item supply change",
    "item demand change",
    "resource availability change",
    "new Resource",
    "drop rate change",
    "temporary demand"
    ]

UPDATES_BLACKLIST_SCHEMA = [
    "pageid",
    "ns",
    "title",
    "date"
    ]

METADATA_SCHEMA = {
        "economic_data": {
            "last_updated": None,
            "earliest_date": None
        },
        "event_data": {
            "last_updated": None,
            "earliest_date": None,
            "total_events": 0
        },
        "GARCH_info" : {
            "common trade index": None,
            "rune index": None,
            "log index": None,
            "food_index": None,
            "metal_index": None,
            "herb_index": None
        }
    }