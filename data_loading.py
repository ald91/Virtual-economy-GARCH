""" methods to contact APIs and refresh, update and store data"""

import re
import time

import pandas as pd
import requests

from config import RAW_DATA_DIR, CACHE_DURATION_MS, API_TIMEOUT_SECONDS, API_CALL_SLEEP, OSRS_GEMW_CPI_ENDPOINTS, OSRS_WIKI_API
from data_helper import save_csv, load_csv

UNIX_TIME_LAST_UPDATE = int(0)

#==========================
# Cache refreshing rules
#==========================
def is_data_old(unix_time_last_update_ms:int) -> bool:
    """ checks the current time in ms since the last successful update,
        Returns:
            boolean: based on if the date since is > one day (ms).
    """
    current_time = int(time.time() * 1000)
    if current_time - unix_time_last_update_ms  > CACHE_DURATION_MS:
        return True
    print("an update is not required, previous update was too recent")
    return False


#===========================
#CPI Data aquisition
#===========================

def refresh_data() -> int:
    """ contacts APIs, converts to pandas dataframe and 
        saves responses in CSV format per index in /data,
        Returns:
            int: the last succesful update time in unix ms.
    """
    last_updated_ms = int(0)
    successful_update = True

    for index_name, url in OSRS_GEMW_CPI_ENDPOINTS.items():

        record = []

        try:
            response = requests.get(
                url,
                timeout=API_TIMEOUT_SECONDS
            )

            if response.status_code != 200:
                print("an invalid response code was returned, the update operation has stopped")
                successful_update = False
                continue

            data = response.json()
            for _, observations in data.items():
                record.extend(observations)

            dataframe = pd.DataFrame(record)
            save_csv(index_name,dataframe,RAW_DATA_DIR)
            print(f"succesfully updated {index_name} and saved to CSV")

        except requests.exceptions.Timeout as e:
            successful_update = False
            print(f"{index_name} timed out.")
            print(e)

        except requests.exceptions.RequestException as e:
            successful_update = False
            print(f"Failed to retrieve {index_name}.")
            print(e )
    if successful_update:
        last_updated_ms = int(time.time() * 1000)
    print(f"last update time: {last_updated_ms} ms")
    return last_updated_ms

#===========================
#Exogenous Events Data Aquisition
#===========================

def get_game_update_list() -> pd.DataFrame:
    """
    Contacts the OSRS Wiki Api and requests a complete list of all documented game updates.
    Saves the responce as a CSV titles "Updates Raw.csv" in the "raw data" DIR.

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
    save_csv("Updates Raw",updates,RAW_DATA_DIR,True)
    return updates

#only use this to initialize if updates raw.csv does not exist (takes 15+ mins to run to prevent API shut out)
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

    save_csv("Updates Dated", update_data, RAW_DATA_DIR)
    return update_data


#use this if updates dated.csv already exists to only call for updates without dates
#TODO: can then use new data
def update_game_update_list():
    return

def update_updates_dates():
    return

#=======================
#Running commands
#=======================


#update_data = get_game_update_list()
#update_data = load_csv("Updates Raw",RAW_DATA_DIR)
#get_full_updates_date(update_data)

#UPDATE_NEEDED = is_data_old(UNIX_TIME_LAST_UPDATE)
#if UPDATE_NEEDED:
#    refresh_data()
