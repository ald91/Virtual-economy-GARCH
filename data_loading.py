""" methods to contact APIs and refresh, update and store data"""

import time
import requests

import pandas as pd

from config import RAW_DATA_DIR, CACHE_DURATION_MS, API_TIMEOUT_SECONDS, API_ENDPOINTS

UNIX_TIME_LAST_UPDATE = int(0)

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

def refresh_data() -> int:
    """ contacts APIs, converts to pandas dataframe and 
        saves responses in CSV format per index in /data,
        Returns:
            int: the last succesful update time in unix ms.
    """
    last_updated_ms = int(0)
    successful_update = True

    for index_name, url in API_ENDPOINTS.items():

        record = []

        try:
            response = requests.get(url, timeout=API_TIMEOUT_SECONDS)
            if response.status_code != 200:
                print("an invalid response code was returned, the update operation has stopped")
                successful_update = False
                continue

            data = response.json()
            for _, observations in data.items():
                record.extend(observations)

            dataframe = pd.DataFrame(record)
            dataframe.to_csv(f"{RAW_DATA_DIR}/{index_name}.csv", index=False)
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

UPDATE_NEEDED = is_data_old(UNIX_TIME_LAST_UPDATE)
if UPDATE_NEEDED:
    refresh_data()
