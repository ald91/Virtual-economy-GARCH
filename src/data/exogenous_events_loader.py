""" methods to contact APIs and refresh, update and store data"""

import re
import time

import pandas as pd
import requests

from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, API_TIMEOUT_SECONDS, API_CALL_SLEEP, OSRS_WIKI_API, OSRS_GE_DATA_START_DATE
from src.data_helper import save_csv,load_csv

#===========================
# Helper Functions
#===========================
def contact_wiki_for_updates() -> pd.DataFrame:
    """
    Contacts the OSRS Wiki Api and requests a complete list of all documented game updates.
    This list is compared to the existing events list and new enteries are added to a new
    dataframe that can be joined using another function.

    """
    new_updates = []

    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": "Category:Game_updates",
        "cmnamespace": 112,
        "cmlimit": "500",
        "format": "json"
    }

    while True:
        try:
            response = requests.get(
                OSRS_WIKI_API,
                params=params,
                timeout=API_TIMEOUT_SECONDS
            ).json()

            new_updates.extend(
                response["query"]["categorymembers"]
            )

            if "continue" not in response:
                break

            params.update(
                response["continue"]
            )

        except requests.exceptions.Timeout as e:
            print(f"The request timed out: {e}")
            return pd.DataFrame(new_updates).iloc[0:0]
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve the update list: {e}")
            return pd.DataFrame(new_updates).iloc[0:0]
        
    new_updates = pd.DataFrame(new_updates)
    print(f"found a list of ({len(new_updates)}) update items")

    EXISTING_EVENTS =  load_csv("updates classified",PROCESSED_DATA_DIR,"pageid")
    BLACKLIST_EVENTS = load_csv("updates blacklist",RAW_DATA_DIR,"pageid")

    if EXISTING_EVENTS is None:
        EXISTING_EVENTS = pd.DataFrame(columns=["pageid","ns","title","date"])

    if BLACKLIST_EVENTS is None:
        BLACKLIST_EVENTS = pd.DataFrame(columns=["pageid","ns","title","date"])

    new_updates = new_updates[~new_updates["pageid"].isin(EXISTING_EVENTS.index)]
    new_updates = new_updates[~new_updates["pageid"].isin(BLACKLIST_EVENTS.index)]

    if "date" not in new_updates.columns:
        new_updates["date"] = pd.NaT

    print(f"after checking against existing and blacklisted, final list of: ({len(new_updates)}) update items. An update isn't required.")

    return new_updates

def contact_wiki_for_dates(update_data:pd.DataFrame) -> pd.DataFrame:
    """
    Contacts the OSRS Wiki API and requests all pages in the provided dataframe missing dates.
    Adds the update date per record.

    CAUTION: This function creates a lot of API calls (1000+).
    """

    for index, update_page_id in update_data["pageid"].items():
        if pd.isna(update_data.loc[index,"date"]):
            page_id = update_page_id

            params = {
                "action": "query",
                "pageids": page_id,
                "prop": "revisions",
                "rvprop": "content",
                "rvslots": "main",
                "format": "json"
            }

            try:
                response = requests.get(
                    OSRS_WIKI_API,
                    params=params,
                    timeout=API_TIMEOUT_SECONDS  #make sure config is set to 1sec +
                ).json()

                page = response["query"]["pages"][str(page_id)]

                content = page["revisions"][0]["slots"]["main"]["*"]

                match = re.search(
                    r"\|date\s*=\s*([^|]+)",
                    content
                )

                if match:
                    match = match.group(1).strip()
                    update_data.loc[index, "date"] = (pd.to_datetime(match,format="%d %B %Y"))

                    print(f"Added date: {update_data.loc[index, 'date'].date()} for page_id: {page_id}")

                else:
                    print(f"No date found for page_id {page_id}")

            except requests.exceptions.Timeout as e:
                print(f"Timeout retrieving page_id {page_id}: {e}")
                return update_data.iloc[0:0]
            except requests.exceptions.RequestException as e:
                print(f"API request failed for page_id {page_id}: {e}")
                return update_data.iloc[0:0]
            except KeyError:
                print(f"Missing page data for page_id: {page_id}")
                return update_data.iloc[0:0]

            time.sleep(API_CALL_SLEEP)
        continue

    save_csv("updates dated", update_data, RAW_DATA_DIR)
    return update_data

def create_event_blacklist(update_data:pd.DataFrame, GE_data_start_date=OSRS_GE_DATA_START_DATE) -> pd.DataFrame:
    """ creates a event blacklist that informs the application that these
    events occurred before OSRS existed and should be ignored."""

    blacklist = load_csv("updates blacklist",RAW_DATA_DIR,"pageid")
    blacklist.index = blacklist.index.astype("Int64")

    if len(blacklist) > 1:
        print(f"located blacklist so initialized a table\n {blacklist.head(5)}")
    elif not isinstance(blacklist, pd.DataFrame):
        blacklist = pd.DataFrame(columns=["pageid","ns","title","date"])
        print(f"could not locate a blacklist so initialized a table\n {blacklist.head(0)}")

    GE_data_start_date = pd.to_datetime(GE_data_start_date)

    blacklist = update_data[pd.to_datetime(update_data["date"]) < GE_data_start_date][["ns","title","date"]]
    blacklist.index = blacklist.index.astype("Int64")
    blacklist.sort_index(inplace=True)

    save_csv("updates blacklist",blacklist,RAW_DATA_DIR,save_index=True)
    return blacklist

#only use this to initialize if STORED_EVENTS_ANALYSIS.csv does not exist (takes 15+ mins to run to prevent API shut out)
def refresh_events_data() -> bool:
    """ contacts APIs, converts to pandas dataframe and 
        saves responses in CSV format per event in /data,
        Returns:
            bool: was the update a success.
    """
    EXISTING_EVENTS =  load_csv("updates dated", RAW_DATA_DIR,"pageid")
    successful_update = True

    new_updates = contact_wiki_for_updates()

    # if the function above has an exception len == 0 stops this function.
    if len(new_updates) == 0:
        print("Update aborted. data is either too recent or the API is down and new data could be not located.")
        successful_update = True
        return successful_update

    #save first step
    save_csv("updates raw", new_updates, RAW_DATA_DIR)

    dated_updates = contact_wiki_for_dates(new_updates)

    # if the function above has an exception len == 0 stops this function.
    if len(dated_updates) == 0:
        successful_update = False
        return successful_update

    save_csv("updates dated new",dated_updates,RAW_DATA_DIR)

    # checked if data has previously been initialized and combines if it has
    if len(EXISTING_EVENTS) > 0:
        dated_updates = pd.concat([EXISTING_EVENTS, dated_updates])
        dated_updates = dated_updates.set_index("pageid")
        dated_updates.index.astype("Int64")
        dated_updates = dated_updates[~dated_updates.index.duplicated(keep="last")]


    save_csv("updates dated",dated_updates,RAW_DATA_DIR)
    print("succesfully updated updates list, including dates and saved to CSV")

    return successful_update
