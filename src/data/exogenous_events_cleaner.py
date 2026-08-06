""" Obtains and classifies OSRS Update information for use with CPI data and statistics from OSRS Wiki """

import pandas as pd
from src.config import EXOGENOUS_EVENT_CATEGORIES, EVENT_SCOPE, ECONOMIC_EFFECTS, RAW_DATA_DIR, PROCESSED_DATA_DIR,ANALYSIS_DATA_DIR
from src.data_helper import save_csv,load_csv

event_categories = EXOGENOUS_EVENT_CATEGORIES

#=====================
# Helper Function
#=====================
def event_category_classification(update_title:str) -> str:
    """ prompts the user to manually assign a category for the event providing
        information to help them and a prompt
    """
                
    categories = EXOGENOUS_EVENT_CATEGORIES
    osrs_wiki = "https://oldschool.runescape.wiki/w/"
    update_title = update_title.replace(" ", "_")

    print(f"\nClassify: {update_title}, \n page address: {osrs_wiki}/{update_title}")

    for index, category in enumerate(categories, start=0):
        print(f"{index}: {category}")

    while True:
        choice = input("Enter category number: ")

        try:

            choice = int(choice)

            if 0 <= choice < len(categories):
                return categories[choice]

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

def merge_classified_updates(existing_data:pd.DataFrame, new_data:pd.DataFrame) -> pd.DataFrame:
    """ merges 2 dataframes ensuring columns are preserved if they dont fully match"""
    combined = pd.concat([existing_data, new_data], axis=0,sort=False)
    combined = combined[~combined.index.duplicated(keep="last")]
    combined.index = combined.index.astype("Int64")
    combined.index.name = "pageid"
    combined = combined.sort_index()
    return combined

#=====================
# function definitions
#=====================
def blacklist_check()-> pd.DataFrame | None:
    """ performs a small re-check on data before classification,
    removing any events that are on the blacklist to save time"""

    BLACKLIST_EVENTS = load_csv("updates blacklist",RAW_DATA_DIR,"pageid")
    data = load_csv("updates dated", RAW_DATA_DIR,"pageid")

    if data is not None:
        data = data[~data.index.isin(BLACKLIST_EVENTS.index)]
        save_csv("updates dated",data, RAW_DATA_DIR,True)
        return data

    return data

def classify_events(partial: bool = True) -> None:
    """Classifies events and adds category, scope and economic effects."""

    data = load_csv("updates dated", RAW_DATA_DIR, "pageid")
    data.index = data.index.astype("Int64")

    existing_data = None

    if partial:
        existing_data = load_csv("updates classified", PROCESSED_DATA_DIR, "pageid")

        if existing_data is None:
            existing_data = pd.DataFrame()

        # Keep only events that haven't already been classified
        data = data[~data.index.isin(existing_data.index)]

        if data.empty:
            print("No new events to classify.")
            return

    # Initialise columns
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

    # Go through the unclassified updates
    try:
        for index, row in data.iterrows():

            update_title = row["title"]
            update_category = row["category"]
            update_scope = row["scope"]

            update_economic_impact = [
                bool(row[effect])
                for effect in ECONOMIC_EFFECTS
            ]

            # Classification procedure
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

            # Save every 10 newly classified events
            if classification_count > 0 and classification_count % 10 == 0:

                if partial:
                    temp = merge_classified_updates(existing_data, data)
                    save_csv("updates classified", temp, PROCESSED_DATA_DIR, True)
                else:
                    save_csv("updates classified", data, PROCESSED_DATA_DIR, True)

                choice = input("\n10 updates classified. Continue? (y/n): ").lower()

                if choice != "y":
                    print("Classification stopped.")
                    break
    # allows a manual escape and forces a save
    except KeyboardInterrupt:
        print("stopping process, saving classified events")
    # Final save
    finally:
        if partial:
            combined = merge_classified_updates(existing_data, data)
            save_csv("updates classified", combined, PROCESSED_DATA_DIR,True)
    # Only runs on FALSE partial update (initialization)
        else:
            data = data.sort_index()
            save_csv("updates classified", data, PROCESSED_DATA_DIR,True)
            print("data successfully saved.")
    return

def create_event_index() -> None:
    """takes a processed dataframe and removes undeeded columns, making it ready
        for analysis and use with graphs"""

    data = load_csv("updates classified",PROCESSED_DATA_DIR,"pageid")
    data = data.drop(columns=["ns"])
    data["date"] = pd.to_datetime(data["date"])
    data = data.set_index("date")
    data = data.sort_index()
    save_csv("events index",data,ANALYSIS_DATA_DIR,True)
    return
