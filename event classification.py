import pandas as pd
from data_helper import save_csv, load_csv

#==============================
#Event categorisation
#==============================

event_categories = {
    "Economy": [
        "Grand Exchange",
        "Tax",
        "Item Sink",
        "Drop Rates",
        "Trade"
    ],

    "Combat": [
        "Weapon",
        "Armour",
        "Boss",
        "Combat",
        "Buff",
        "Nerf"
    ],

    "Resource": [
        "Mining",
        "Fishing",
        "Woodcutting",
        "Farming",
        "Herblore"
    ],

    "Seasonal": [
        "Christmas",
        "Halloween",
        "Easter",
        "Birthday"
    ],

    "Content": [
        "Quest",
        "Raid",
        "Dungeon",
        "Area",
        "Boss"
    ],

    "QoL": [
        "QoL",
        "Quality",
        "Fix",
        "Bug"
    ]
}

#=====================
# function definitions
#=====================

def auto_classify_events(updates_dated_dataframe:pd.DataFrame) -> pd.DataFrame:
    """ uses event_categories dict to automatically classify events adds, category to dataframe"""
    data = updates_dated_dataframe
    return data
