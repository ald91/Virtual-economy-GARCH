""" methods to contact APIs and refresh, update and store data"""

import requests
import pandas as panda
from api import API_ENDPOINTS

TARGET_DIR = "./data/"
record = []

def Refresh_Data(API_ENDPOINTS:dict, UnixDate:int):
    """ contacts APIs, converts to pandas dataframe and saves responses in CSV format per index in /data"""
    for index_name, url in API_ENDPOINTS.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                for _, observations in data.items():
                    record.extend(observations)

            dataframe = panda.DataFrame(record)
            dataframe.to_csv(f"{TARGET_DIR}/{index_name}.csv", index=False)

        except requests.exceptions.Timeout as e:
            print(f"{index_name} timed out.")
            print(e)

        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve {index_name}.")
            print(e)