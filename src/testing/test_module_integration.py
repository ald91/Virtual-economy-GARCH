
import pytest
import pandas as pd

from unittest.mock import patch

from src.config import SUPPORTED_INDEX_LIST, DATA_DIR
from src.data_helper import load_csv, save_csv

from src.data.data_management import clean_economic_data, clean_events_data
from src.analysis.analysis_data_generation import generate_statistical_data

TEST_DIR = DATA_DIR/"test_data"

# IT01 - DATA MODULE / Economic data cleaning pipeline
def test_economic_data_pipeline():
    with patch("src.data.economy_cleaner.load_all_indices") as mock_load_all, \
        patch("src.data.data_management.PROCESSED_DATA_DIR", TEST_DIR), \
        patch("src.data.data_management.ANALYSIS_DATA_DIR", TEST_DIR):

        #test load csv and use non-jagex data so testinh can be uploaded repo
        cti_data = load_csv("IT01 - CTI", TEST_DIR)
        fi_data = load_csv("IT01 - FI", TEST_DIR)
        he_data = load_csv("IT01 - HE", TEST_DIR)
        li_data = load_csv("IT01 - LI", TEST_DIR)
        mi_data = load_csv("IT01 - MI", TEST_DIR)
        ri_data = load_csv("IT01 - RI", TEST_DIR)

        #emulate load_all_indices due to function programming choices
        mock_data = [cti_data,fi_data, he_data, li_data, mi_data, ri_data]
        mock_load_all.return_value = dict(zip(SUPPORTED_INDEX_LIST, mock_data))

        clean_economic_data()

        mock_load_all.assert_called_once_with(SUPPORTED_INDEX_LIST)
      # Check processed files were created
        for index in SUPPORTED_INDEX_LIST:
            assert (TEST_DIR / f"{index}.csv").exists()

        # Check final master file
        assert (TEST_DIR / "master.csv").exists()
        master = load_csv("master", TEST_DIR)

        assert "date" in master.columns
        assert all(index in master.columns for index in SUPPORTED_INDEX_LIST)

#IT02 - DATA MODULE / Event Data cleaning pipeline
#NOTE: patches required due to keyboard input bypass
def test_event_data_pipeline():
    with patch("src.data.exogenous_events_cleaner.RAW_DATA_DIR", TEST_DIR), \
    patch("src.data.exogenous_events_cleaner.PROCESSED_DATA_DIR", TEST_DIR), \
    patch("src.data.exogenous_events_cleaner.ANALYSIS_DATA_DIR",TEST_DIR), \
    patch("src.data.exogenous_events_cleaner.event_category_classification", return_value="New Content"), \
    patch("src.data.exogenous_events_cleaner.event_scope_classification", return_value="No Economic Impact"), \
    patch("src.data.exogenous_events_cleaner.event_economic_effects_classification", return_value=[False,False,False,False,False,False,False,True]):

        clean_events_data(mode=False)

        # Check intermediate and final files
        assert (TEST_DIR / "updates dated.csv").exists()
        assert (TEST_DIR / "updates classified.csv").exists()
        assert (TEST_DIR / "events index.csv").exists()

        events = load_csv("events index", TEST_DIR, set_index="date")

        assert events.index.name == "date"
        assert "ns" not in events.columns

#IT03 - check statistical generation works together
def test_statistical_data_pipeline():
    with patch("src.analysis.analysis_data_generation.ANALYSIS_DATA_DIR",TEST_DIR):

        generate_statistical_data()

        # Check expected output files
        assert (TEST_DIR / "returns.csv").exists()
        assert (TEST_DIR / "sq_returns.csv").exists()
        assert (TEST_DIR / "vol_7.csv").exists()
        assert (TEST_DIR / "vol_30.csv").exists()

        # Check statistics files
        assert (TEST_DIR / "returns_stats.csv").exists()
        assert (TEST_DIR / "sq_returns_stats.csv").exists()
        assert (TEST_DIR / "vol_7_stats.csv").exists()
        assert (TEST_DIR / "vol_30_stats.csv").exists()

        returns = load_csv("returns", TEST_DIR)
        assert "date" in returns.columns
        assert all(index in returns.columns for index in SUPPORTED_INDEX_LIST)