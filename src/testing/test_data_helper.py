import pandas as pd

from src.data_helper import load_csv,save_csv
#----------------
#load_csv
#----------------

# T01 - Test loading a valid CSV file
def test_load_csv(tmp_path):
    data = pd.DataFrame({
        "date": ["2025-01-01", "2025-01-02"],
        "value": [100, 110]
    })

    data.to_csv(tmp_path / "test_data.csv", index=False)

    result = load_csv("test_data", tmp_path)

    assert result is not None
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert list(result.columns) == ["date", "value"]


# T02 - Test behaviour when the CSV file does not exist
def test_load_csv_missing_file(tmp_path):
    result = load_csv("does_not_exist", tmp_path)

    assert result is None

#----------------
#save_csv
#----------------

# T03 - Test saving a valid CSV file
def test_save_csv(tmp_path):
    data = pd.DataFrame({
        "date": ["2025-01-01", "2025-01-02"],
        "value": [100, 110]
    })

    result = save_csv("test_output", data, tmp_path)

    assert result is True
    assert (tmp_path / "test_output.csv").exists()


# T04 - Test saving to an invalid location
def test_save_csv_invalid_location(tmp_path):
    data = pd.DataFrame({
        "date": ["2025-01-01"],
        "value": [100]
    })

    invalid_path = tmp_path / "does_not_exist"
    result = save_csv("test_output", data, invalid_path)

    assert result is False