""" methods to contact APIs and refresh, update and store data"""

import pandas as pd
import requests

from src.config import RAW_DATA_DIR, API_TIMEOUT_SECONDS, OSRS_GEMW_CPI_ENDPOINTS
from src.data_helper import save_csv

#===========================
#CPI Data aquisition
#===========================

def refresh_cpi_data() -> bool:
    """ contacts APIs, converts to pandas dataframe and 
        saves responses in CSV format per index in /data,
        Returns:
            bool: was the update a success.
    """
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

    return successful_update
