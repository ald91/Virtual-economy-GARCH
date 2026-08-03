""" Obtains and classifies OSRS Update information for use with CPI data and statistics from OSRS Wiki,"""

import pandas as pd
from src.config import OSRS_GE_DATA_START_DATE, EXOGENOUS_EVENT_CATEGORIES, EVENT_SCOPE, ECONOMIC_EFFECTS

event_categories = EXOGENOUS_EVENT_CATEGORIES

#=====================
# Helper Function
#=====================
def event_category_classification(update_title:str) -> str:
    """ prompts the user to manually assign a category for the event providing
        information to help them and a prompt
    """
                
    categories = list(EXOGENOUS_EVENT_CATEGORIES)
    osrs_wiki = "https://oldschool.runescape.wiki/w/"
    update_title = update_title.replace(" ", "_")

    print(f"\nClassify: {update_title}, \n page address: {osrs_wiki}/{update_title}")

    for index, category in enumerate(categories, start=0):
        print(f"{index}: {category}")

    while True:
        choice = input("Enter category number: ")

        try:

            choice = int(choice)

            if 0 <= choice <= len(categories):
                return categories[choice - 1]

            print("Invalid choice.")

        except ValueError:
            print("Please enter a number.")

def event_scope_classification(update_title: str) -> str:
    """
    Allows the user to manually select the economic scope of an event.
    """
    print("\nSelect event scope:")

    for index, scope in enumerate(EVENT_SCOPE):
        print(f"{index}: {scope}")

    while True:
        choice = input("Enter scope number: ")

        if choice.isdigit():
            choice = int(choice)

            if 0 <= choice < len(EVENT_SCOPE):
                return EVENT_SCOPE[choice]

        print("Invalid selection, try again.")

def event_economic_effects_classification(update_title: str) -> list[bool]:
    """
    Allows the user to select multiple economic effects.
    Returns a boolean list matching ECONOMIC_EFFECTS.
    """

    print("\nSelect economic effects (enter numbers separated by commas):")

    for index, effect in enumerate(ECONOMIC_EFFECTS):
        print(f"{index}: {effect}")

    while True:
        choices = input("Enter effects: ")

        try:
            selections = [
                int(choice.strip())
                for choice in choices.split(",")
            ]

            if all(0 <= choice < len(ECONOMIC_EFFECTS) for choice in selections):

                effects = [
                    False
                    for _ in ECONOMIC_EFFECTS
                ]

                for selection in selections:
                    effects[selection] = True

                return effects

        except ValueError:
            pass

        print("Invalid selection, try again.")

#=====================
# function definitions
#=====================

def classify_events(updates_dated_dataframe: pd.DataFrame) -> pd.DataFrame:
    """Classifies events and adds category, scope and economic effects."""

    data = updates_dated_dataframe.copy()

    # initialise columns
    if "category" not in data.columns:
        data["category"] = ""
    else:
        data["category"] = data["category"].fillna("")

    if "scope" not in data.columns:
        data["scope"] = ""
    else:
        data["scope"] = data["scope"].fillna("")

    for effect in ECONOMIC_EFFECTS:
        if effect not in data.columns:
            data[effect] = 0
        else:
            data[effect] = data[effect].fillna(0)

    classification_count = 0

    for index, row in data.iterrows():

        update_title = row["title"]
        update_category = row["category"]
        update_scope = row["scope"]

        update_economic_impact = [
            bool(row[effect])
            for effect in ECONOMIC_EFFECTS
        ]

        # classification procedure
        if update_category == "":
            update_category = event_category_classification(update_title)
            update_scope = event_scope_classification(update_title)
            update_economic_impact = event_economic_effects_classification(update_title)

            classification_count += 1

        data.loc[index, "category"] = update_category
        data.loc[index, "scope"] = update_scope

        for column, value in zip(ECONOMIC_EFFECTS, update_economic_impact):
            data.loc[index, column] = int(value)

        print(
            f"{index}: {update_title} -> {update_category} "
            f"-> {update_scope} with impacts {update_economic_impact}"
        )

        # ask every 10 newly classified events
        if classification_count > 0 and classification_count % 10 == 0:
            save_csv("events classified", data, RAW_DATA_DIR)
            choice = input(
                "\n10 events classified. Continue? (y/n): "
            ).lower()

            if choice != "y":
                print("Classification stopped.")
                break

    return data

def remove_data_out_of_timeframe(updates_dated_frame: pd.DataFrame) -> pd.DataFrame:
    """Removes updates which occurred before the data snapshot, set in CONFIG.PY."""

    #TODO: Implement update cut off to prevent redundant event naming
    data = updates_dated_frame.copy()
    print(f" current event's in dataframe: {len(data)}")
    data = data[
        data["date"] >= OSRS_GE_DATA_START_DATE
    ]
    data = data.sort_index(axis=0)
    print(f"completed current event's in dataframe: {len(data)} occuring after: {OSRS_GE_DATA_START_DATE}")
    return data

def create_event_index(updates_frame_dated_and_categorized: pd.DataFrame) -> pd.DataFrame:
    """takes a processed dataframe and removes undeeded columns, making it ready
        for analysis and use with graphs"""

    data = updates_frame_dated_and_categorized.copy()
    data = data.drop(columns=["ns", "pageid"])
    data["date"] = pd.to_datetime(data["date"])
    data = data.set_index("date")
    data = data.sort_index()
    return data

