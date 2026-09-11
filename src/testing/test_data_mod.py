import pandas as pd
import requests

from unittest.mock import Mock, patch

from src.data.economy_loader import refresh_cpi_data
from src.data.exogenous_events_loader import (contact_wiki_for_dates, contact_wiki_for_updates, create_event_blacklist, initialise_events_data)
from src.data.exogenous_events_cleaner import ( merge_classified_updates, blacklist_check, create_event_index)
from src.data.economy_cleaner import ( clean_index, convert_timestamp, load_all_indices, merge_indices)

#--------------------
#economy_loader.py
#--------------------

# T05 - Test successful CPI data refresh
@patch("src.data.economy_loader.save_csv")
@patch("src.data.economy_loader.requests.get")
def test_refresh_cpi_data_success(mock_get, mock_save_csv):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "2025-01-01": [
            {"timestamp": 1234567890, "price": 100}
        ]
    }

    mock_get.return_value = mock_response

    result = refresh_cpi_data()

    assert result is True
    assert mock_get.called
    assert mock_save_csv.called



# T06 - Test CPI refresh handles an invalid API response
@patch("src.data.economy_loader.save_csv")
@patch("src.data.economy_loader.requests.get")
def test_refresh_cpi_data_invalid_response(mock_get, mock_save_csv):
    mock_response = Mock()
    mock_response.status_code = 500

    mock_get.return_value = mock_response

    result = refresh_cpi_data()

    assert result is False
    mock_save_csv.assert_not_called()

# T07 - Test unwanted columns are removed from index data
def test_clean_index():
    data = pd.DataFrame({
        "timestamp": [1234567890],
        "price": [100],
        "id": [123],
        "volume": [50]
    })

    result = clean_index(data)

    assert "id" not in result.columns
    assert "volume" not in result.columns
    assert "timestamp" in result.columns
    assert "price" in result.columns

#--------------------
#economy_cleaner.py
#--------------------

# T08 - Test timestamps are converted into dates
def test_convert_timestamp():
    data = pd.DataFrame({
        "timestamp": [1234567890, 9876543210],
        "price": [100, 110]
    })

    result = convert_timestamp(data)

    assert "date" in result.columns
    assert "timestamp" not in result.columns
    assert "price" in result.columns
    assert list(result.columns) == ["date", "price"]
    assert len(result) == 2
    assert pd.api.types.is_datetime64_any_dtype(result["date"])

# T09 - Test all requested indices are loaded
@patch("src.data.economy_cleaner.load_csv")
def test_load_all_indices(mock_load_csv):
    mock_load_csv.side_effect = [
        pd.DataFrame({
            "date": ["2025-01-01"],
            "price": [100]
        }),
        pd.DataFrame({
            "date": ["2025-01-01"],
            "price": [200]
        })
    ]

    index_names = [
        "common trade index",
        "rune index"
    ]

    result = load_all_indices(index_names)

    assert isinstance(result, dict)
    assert len(result) == 2
    assert "common trade index" in result
    assert "rune index" in result

# T10 - Test multiple indices are merged by date
def test_merge_indices():
    common_trade = pd.DataFrame({
        "date": pd.to_datetime(["2025-01-01", "2025-01-02"]),
        "price": [100, 110]
    })

    rune = pd.DataFrame({
        "date": pd.to_datetime(["2025-01-01", "2025-01-02"]),
        "price": [200, 220]
    })

    data = {
        "common trade index": common_trade,
        "rune index": rune
    }

    result = merge_indices(data)

    assert result is not None
    assert len(result) == 2
    assert "date" in result.columns
    assert "common trade index" in result.columns
    assert "rune index" in result.columns
    assert result.loc[0, "common trade index"] == 100
    assert result.loc[0, "rune index"] == 200


#--------------------
#exogenous_events_loader
#--------------------

# T11 - Test update API response is processed correctly
@patch("src.data.exogenous_events_loader.load_csv")
@patch("src.data.exogenous_events_loader.requests.get")
def test_contact_wiki_for_updates(mock_get, mock_load_csv):

    mock_get.return_value.json.return_value = {
        "query": {
            "categorymembers": [
                {"pageid": 1, "ns": 112, "title": "Update One"},
                {"pageid": 2, "ns": 112, "title": "Update Two"},
                {"pageid": 3, "ns": 112, "title": "Update Three"}
            ]
        }
    }

    existing_events = pd.DataFrame(
        {"title": ["Update One"]},
        index=pd.Index([1], name="pageid")
    )

    blacklist = pd.DataFrame(
        {"title": ["Update Two"]},
        index=pd.Index([2], name="pageid")
    )

    mock_load_csv.side_effect = [existing_events, blacklist]

    result = contact_wiki_for_updates()

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert result.iloc[0]["pageid"] == 3
    assert result.iloc[0]["title"] == "Update Three"
    assert "date" in result.columns


# T12 - Test API failure returns empty DataFrame
@patch("src.data.exogenous_events_loader.requests.get")
def test_contact_wiki_for_updates_api_failure(mock_get):

    mock_get.side_effect = requests.exceptions.RequestException()

    result = contact_wiki_for_updates()

    assert isinstance(result, pd.DataFrame)
    assert result.empty

# T13 - Test dates are extracted from API response
@patch("src.data.exogenous_events_loader.time.sleep")
@patch("src.data.exogenous_events_loader.save_csv")
@patch("src.data.exogenous_events_loader.requests.get")
@patch("src.data.exogenous_events_loader.load_csv")
def test_contact_wiki_for_dates(
    mock_load_csv,
    mock_get,
    mock_save_csv,
    mock_sleep
):

    update_data = pd.DataFrame(
        {
            "date": [pd.NaT],
            "title": ["Test Update"]
        },
        index=pd.Index([123], name="pageid")
    )

    mock_load_csv.side_effect = [
        update_data,
        None
    ]

    mock_get.return_value.json.return_value = {
        "query": {
            "pages": {
                "123": {
                    "revisions": [
                        {
                            "slots": {
                                "main": {
                                    "*": "|date = 15 January 2025\n"
                                }
                            }
                        }
                    ]
                }
            }
        }
    }

    result = contact_wiki_for_dates()

    assert isinstance(result, pd.DataFrame)
    assert result.loc[123, "date"] == pd.Timestamp("2025-01-15")

    mock_save_csv.assert_called_once()


# T14 - Test missing update data returns None
@patch("src.data.exogenous_events_loader.load_csv")
def test_contact_wiki_for_dates_no_data(mock_load_csv):

    mock_load_csv.return_value = None

    result = contact_wiki_for_dates()

    assert result is None

# T15 - Test events before the GE start date are blacklisted
@patch("src.data.exogenous_events_loader.save_csv")
@patch("src.data.exogenous_events_loader.load_csv")
def test_create_event_blacklist(mock_load_csv, mock_save_csv):

    mock_load_csv.return_value = None

    update_data = pd.DataFrame(
        {
            "ns": [112, 112, 112],
            "title": [
                "Old Update",
                "Valid Update",
                "Another Old Update"
            ],
            "date": [
                "2018-01-01",
                "2020-01-01",
                "2019-01-01"
            ]
        },
        index=pd.Index([1, 2, 3], name="pageid")
    )

    result = create_event_blacklist(
        update_data,
        GE_data_start_date="2019-01-01"
    )

    assert isinstance(result, pd.DataFrame)

    assert list(result.index) == [1]

    assert result.iloc[0]["title"] == "Old Update"

    mock_save_csv.assert_called_once()

# T16 - Test successful event data initialisation
@patch("src.data.exogenous_events_loader.save_csv")
@patch("src.data.exogenous_events_loader.contact_wiki_for_dates")
@patch("src.data.exogenous_events_loader.contact_wiki_for_updates")
@patch("src.data.exogenous_events_loader.load_csv")
def test_initialise_events_data(
    mock_load_csv,
    mock_updates,
    mock_dates,
    mock_save_csv
):

    existing_events = pd.DataFrame(
        {
            "pageid": [1],
            "ns": [112],
            "title": ["Existing Update"],
            "date": ["2024-01-01"]
        }
    )

    new_updates = pd.DataFrame(
        {
            "pageid": [2],
            "ns": [112],
            "title": ["New Update"]
        }
    )

    dated_updates = pd.DataFrame(
        {
            "pageid": [2],
            "ns": [112],
            "title": ["New Update"],
            "date": ["2025-01-01"]
        }
    )

    mock_load_csv.return_value = existing_events
    mock_updates.return_value = new_updates
    mock_dates.return_value = dated_updates

    result = initialise_events_data()

    assert result is True

    mock_updates.assert_called_once()
    mock_dates.assert_called_once()

    assert mock_save_csv.call_count >= 2

#--------------------
#exogenous_events_cleaner.py
#--------------------

# T17 - Test classified event data is merged correctly
def test_merge_classified_updates():

    existing_data = pd.DataFrame(
        {
            "title": ["Old Event"],
            "category": ["Content"]
        },
        index=pd.Index([1], name="pageid")
    )

    new_data = pd.DataFrame(
        {
            "title": ["New Event"],
            "category": ["Economic"]
        },
        index=pd.Index([2], name="pageid")
    )

    result = merge_classified_updates(existing_data, new_data)

    assert len(result) == 2
    assert result.index.name == "pageid"
    assert 1 in result.index
    assert 2 in result.index


# T18 - Test duplicate event IDs keep the newest record
def test_merge_classified_updates_duplicate():

    existing_data = pd.DataFrame(
        {
            "title": ["Old Event"],
            "category": ["Content"]
        },
        index=pd.Index([1], name="pageid")
    )

    new_data = pd.DataFrame(
        {
            "title": ["Updated Event"],
            "category": ["Economic"]
        },
        index=pd.Index([1], name="pageid")
    )

    result = merge_classified_updates(existing_data, new_data)

    assert len(result) == 1
    assert result.loc[1, "title"] == "Updated Event"


# T19 - Test blacklist removes blacklisted events
@patch("src.data.exogenous_events_cleaner.save_csv")
@patch("src.data.exogenous_events_cleaner.load_csv")
def test_blacklist_check(mock_load_csv, mock_save_csv):

    blacklist = pd.DataFrame(
        {"title": ["Blacklisted Event"]},
        index=pd.Index([1], name="pageid")
    )

    events = pd.DataFrame(
        {
            "title": ["Blacklisted Event", "Valid Event"],
            "date": pd.to_datetime(["2025-01-01", "2025-01-02"])
        },
        index=pd.Index([1, 2], name="pageid")
    )

    mock_load_csv.side_effect = [blacklist, events]

    result = blacklist_check()

    assert len(result) == 1
    assert 1 not in result.index
    assert 2 in result.index
    mock_save_csv.assert_called_once()


# T20 - Test event index creation
@patch("src.data.exogenous_events_cleaner.save_csv")
@patch("src.data.exogenous_events_cleaner.load_csv")
def test_create_event_index(mock_load_csv, mock_save_csv):

    events = pd.DataFrame(
        {
            "ns": [112, 112],
            "title": ["Event A", "Event B"],
            "date": ["2025-01-02", "2025-01-01"]
        },
        index=pd.Index([1, 2], name="pageid")
    )

    mock_load_csv.return_value = events

    create_event_index()

    mock_save_csv.assert_called_once()

    saved_data = mock_save_csv.call_args[0][1]

    assert "ns" not in saved_data.columns
    assert saved_data.index.name == "date"
    assert list(saved_data.index) == [
        pd.Timestamp("2025-01-01"),
        pd.Timestamp("2025-01-02")
    ]