""" Obtains and classifies OSRS Update information for use with CPI data and statistics from OSRS Wiki"""

import pandas as pd
from data_helper import save_csv, load_csv
from config import RAW_DATA_DIR

#==============================
#Event categorisation
#==============================

#TODO: FINALIZE EVENT CLASSIFICATIONS
event_categories = {
    "Economy": [
        "Grand Exchange",
        "Tax",
        "Item Sink",
        "Drop Rates",
        "Trade"
        "Bank"
    ],

    "Combat": [
        "Weapon",
        "Armour",
        "Combat",
        "Slayer",
        "Spellbook",
        "Prayer",
        "Special Attack"
    ],
    #all bosses in the game, spelt with variants and colloquialisms
    "Boss": [
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

    "PvP" : [
        "Bouny Hunter",
        "Wilderness"
    ]
}

#=====================
# Helper Function
#=====================

def classify_event(update_title_string: str) -> str:
    """ classifies events by searching the event_categories dictionary"""
    for category, terms in event_categories.items():
        if any(term.lower() in update_title_string.lower() for term in terms):
            return category
    return ""


#=====================
# function definitions
#=====================

def auto_classify_events(updates_dated_dataframe:pd.DataFrame) -> pd.DataFrame:
    """ uses event_categories dict to automatically classify events adds, category to dataframe"""
    data = updates_dated_dataframe.copy()

    if "category" not in data.columns:
        data["category"] = ""
    else:
        data["category"] = data["category"].fillna("")

    for index, row in data.iterrows():
        update_title = row["title"]
        update_category = data.loc[index, "category"]
        if  update_category == "":
            update_category = classify_event(update_title)
            data.loc[index, "category"] = update_category
            print(f"{index}: {update_title} -> {update_category}")
        
    return data


def remove_data_out_of_timeframe(updates_dated_frame:pd.DataFrame) -> pd.DataFrame:
    """removes updates which occursed before the data snapshot, can be set in CONFIG.PY"""
    data = updates_dated_frame.copy()



    #TODO: Implement update cut off to prevent redundant event naming
    #NYI



    return data


df = load_csv("test", RAW_DATA_DIR)
df2 = auto_classify_events(df)
save_csv("test", df2,RAW_DATA_DIR)
