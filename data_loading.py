""" methods to contact APIs and refresh, update and store data"""

import time
import requests

import pandas as pd

from api import API_ENDPOINTS

TARGET_DIR = "./data/"
UNIX_TIME_LAST_UPDATE = int(0)
UNIX_TIME_ONE_DAY_MS = 86400000

def is_data_old(unix_time_last_update_ms:int):
    """ checks to see if the current time in ms is 1 day greater than the last update time,
        returns a boolean.
    """
    current_time = int(time.time() * 1000)
    if current_time - unix_time_last_update_ms  > UNIX_TIME_ONE_DAY_MS:
        return True
    print("an update is not required, previous update was too recent")
    return False

def refresh_data():
    """ contacts APIs, converts to pandas dataframe and 
        saves responses in CSV format per index in /data,
        returns the last updated in unix ms.
    """
    last_updated_ms = int(0)
    successful_update = True

    for index_name, url in API_ENDPOINTS.items():

        record = []

        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                print("an invalid response code was returned, the update operation has stopped")
                successful_update = False
                continue
            else:
                data = response.json()               
                for _, observations in data.items():
                    record.extend(observations)
    
            dataframe = pd.DataFrame(record)
            dataframe.to_csv(f"{TARGET_DIR}/{index_name}.csv", index=False)
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
 