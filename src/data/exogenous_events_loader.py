""" methods to contact APIs and refresh, update and store data"""

import re
import time

import pandas as pd
import requests

from src.config import RAW_DATA_DIR, API_TIMEOUT_SECONDS, API_CALL_SLEEP, OSRS_WIKI_API
from src.data_helper import save_csv

#===========================
#Exogenous Events Data Aquisition
#===========================

def get_game_update_list() -> pd.DataFrame:
    """
    Contacts the OSRS Wiki Api and requests a complete list of all documented game updates.
    Saves the responce as a CSV titles "exogenous_events_raw.csv" in the "raw data" DIR.

    """
    updates = []

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

            updates.extend(
                response["query"]["categorymembers"]
            )

            if "continue" not in response:
                break

            params.update(
                response["continue"]
            )

        except requests.exceptions.Timeout as e:
            print(f"The request timed out: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve the update list: {e}")

    updates = pd.DataFrame(updates)
    save_csv("exogenous_events_raw",updates,RAW_DATA_DIR)
    return updates

#only use this to initialize if exogenous_events_raw.csv does not exist (takes 15+ mins to run to prevent API shut out)
def get_full_updates_date(update_data: pd.DataFrame) -> pd.DataFrame:
    """
    Contacts the OSRS Wiki API and requests all pages missing dates in the Updates_Raw.csv file.
    Adds the update date per record.

    CAUTION: This function creates a lot of API calls (1000+).
    """
    for index, update_page_id in update_data["pageid"].items():

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

                update_data.loc[index, "date"] = (
                    pd.to_datetime(
                        match,
                        format="%d %B %Y"
                    )
                    .normalize()
                )

                print(f"Added date: {update_data.loc[index, 'date'].date()} for page_id: {page_id}")

            else:
                print(f"No date found for page_id {page_id}")

        except requests.exceptions.Timeout as e:
            print(f"Timeout retrieving page_id {page_id}: {e}")
        except requests.exceptions.RequestException as e:
            print(f"API request failed for page_id {page_id}: {e}")
        except KeyError:
            print(f"Missing page data for page_id: {page_id}")

        time.sleep(API_CALL_SLEEP)

    save_csv("exogenous_events_dated", update_data, RAW_DATA_DIR)
    return update_data


#use this if exogenous_events_dated.csv already exists to only call for updates without dates
#TODO: can then use new data
def update_game_update_list():
    """ x """
    return

def update_updates_dates():
    """ x """
    return


#""" update_data = get_game_update_list()
#update_data = load_csv("exogenous_events_raw",RAW_DATA_DIR)
#get_full_updates_date(update_data)
#refresh_data() """
