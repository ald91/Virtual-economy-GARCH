import pandas as pd
from unittest.mock import Mock, patch

from src.analysis.statistical_analysis import ( calculate_returns, calculate_returns_squared, calculate_rolling_volatility, calculate_statistics)
from src.analysis.garch_modelling import (arch_lm_test, adf_test, garch_analysis)

from src.config import SUPPORTED_INDEX_LIST

# ------------------------
# statistical_analysis.py
# ------------------------

# T15 - Test daily returns are calculated correctly
def test_calculate_returns():

    data = pd.DataFrame({
        "date": pd.to_datetime([
            "2025-01-01",
            "2025-01-02",
            "2025-01-03"
        ]),
        "common trade index": [10, 20, 10],
        "rune index": [10, 20, 30]
    })

    result = calculate_returns(data)

    assert "date" in result.columns
    assert list(result.columns) == ["date", "common trade index", "rune index"]

    # First observation has no previous value
    assert pd.isna(result.loc[0, "common trade index"])

    # (20 - 10) / 10 = 1
    assert result.loc[1, "common trade index"] == 1

    # (10 - 20) / 20 = -0.5
    assert result.loc[2, "common trade index"] == -0.5


# T16 - Test returns are squared correctly
def test_calculate_returns_squared():

    data = pd.DataFrame({
        "date": pd.to_datetime([
            "2025-01-01",
            "2025-01-02"
        ]),
        "common trade index": [1, -2],
        "rune index": [2, -3]
    })

    result = calculate_returns_squared(data)

    # 1 x 1 = 1
    assert result.loc[0, "common trade index"] == 1

    # -2 x -2 = 4
    assert result.loc[1, "common trade index"] == 4

    # -3 x -3 = 9
    assert result.loc[1, "rune index"] == 9

    # Date should remain unchanged
    assert "date" in result.columns


# T17 - Test rolling volatility is calculated
def test_calculate_rolling_volatility():

    data = pd.DataFrame({
        "date": pd.date_range("2025-01-01", periods=3),
        "common trade index": [1, 2, 3]
    })

    result = calculate_rolling_volatility(
        data,
        time_window=2
    )

    assert "date" in result.columns

    # First observation cannot have a 2-day rolling value
    assert pd.isna(result.loc[0, "common trade index"])
    # Second observation should have a calculated value
    assert not pd.isna(result.loc[1, "common trade index"])
    # Third observation should also have a calculated value
    assert not pd.isna(result.loc[2, "common trade index"])


# T18 - Test descriptive statistics are calculated
def test_calculate_statistics():

    data = pd.DataFrame({
        "common trade index": [1, 2, 3, 4],
        "rune index": [2, 4, 6, 8]
    })

    result = calculate_statistics(data)

    expected_columns = [
        "mean",
        "std_dev",
        "variance",
        "min",
        "max",
        "skewness",
        "kurtosis"
    ]

    for column in expected_columns:
        assert column in result.columns

    assert result.index.name == "Market Index"

    # Mean of 1, 2, 3, 4 = 2.5
    assert result.loc["common trade index", "mean"] == 2.5

    assert result.loc["common trade index", "min"] == 1
    assert result.loc["common trade index", "max"] == 4

    # Mean of 2, 4, 6, 8 = 5
    assert result.loc["rune index", "mean"] == 5


# ------------------------
# garch_modelling.py
# ------------------------

# T19 - Test ARCH-LM analysis
@patch("src.analysis.garch_modelling.save_csv")
@patch("src.analysis.garch_modelling.load_csv")
@patch("src.analysis.garch_modelling.het_arch")
def test_arch_lm_test(mock_het_arch, mock_load_csv, mock_save_csv):

    dates = pd.date_range("2025-01-01", periods=4)

    returns = pd.DataFrame({
        "date": dates
    })

    # Add all supported indices so the function can test each one
    for index in SUPPORTED_INDEX_LIST:
        returns[index.lower()] = [1, 2, 3, 4]

    mock_load_csv.return_value = returns

    # Mock result returned by the ARCH-LM test
    mock_het_arch.return_value = (
        1,      # LM statistic
        0.01,   # p-value
        2,      # F statistic
        0.02    # F p-value
    )

    result = arch_lm_test()

    assert isinstance(result, pd.DataFrame)

    assert "index" in result.columns
    assert "lm_statistic" in result.columns
    assert "p_value" in result.columns
    assert "f_statistic" in result.columns
    assert "f_p_value" in result.columns
    assert "arch_effects" in result.columns

    assert len(result) == len(SUPPORTED_INDEX_LIST)

    # p-value is below 0.05, so ARCH effects should be True
    assert result["arch_effects"].all()

    mock_save_csv.assert_called_once()


# T20 - Test ADF stationarity analysis
@patch("src.analysis.garch_modelling.save_csv")
@patch("src.analysis.garch_modelling.load_csv")
@patch("src.analysis.garch_modelling.adfuller")
def test_adf_test(mock_adfuller, mock_load_csv, mock_save_csv):

    dates = pd.date_range("2025-01-01", periods=4)

    returns = pd.DataFrame({
        "date": dates
    })

    # Add all supported indices
    for index in SUPPORTED_INDEX_LIST:
        returns[index.lower()] = [1, 2, 3, 4]

    mock_load_csv.return_value = returns

    # Mock ADF result
    mock_adfuller.return_value = (
        -1,        # ADF statistic
        0.01,      # p-value
        1,         # used lags
        3,         # observations
        {"5%": -2},
        1          # information criterion
    )

    result = adf_test()

    assert isinstance(result, pd.DataFrame)

    assert "index" in result.columns
    assert "adf statistic" in result.columns
    assert "adf_p_value" in result.columns
    assert "stationary" in result.columns

    assert len(result) == len(SUPPORTED_INDEX_LIST)

    # p-value is below 0.05, so the series should be marked stationary
    assert result["stationary"].all()

    mock_save_csv.assert_called_once()


# T21 - Test GARCH analysis and returned diagnostics
@patch("src.analysis.garch_modelling.het_arch")
@patch("src.analysis.garch_modelling.arch_model")
@patch("src.analysis.garch_modelling.load_csv")
def test_garch_analysis(mock_load_csv, mock_arch_model, mock_het_arch):

    # Mock returns data
    returns = pd.DataFrame({
        "date": pd.to_datetime([
            "2025-01-01",
            "2025-01-02",
            "2025-01-03",
            "2025-01-04"
        ]),
        "common trade index": [1, 2, 3, 4]
    })

    # Mock event data
    events = pd.DataFrame({
        "date": pd.to_datetime(["2025-01-02"]),
        "title": ["Test Event"],
        "category": ["Content"],
        "scope": ["Game-wide"]
    })

    # garch_analysis() loads events first, then returns
    mock_load_csv.side_effect = [events, returns]

    # Mock fitted GARCH results
    mock_results = Mock()

    mock_results.std_resid = pd.Series([1, 2, 3, 4])

    mock_results.params = pd.Series({
        "alpha[1]": 1,
        "beta[1]": 2,
        "omega": 3,
        "nu": 4,
        "mu": 5
    })

    mock_results.pvalues = pd.Series({
        "alpha[1]": 1,
        "beta[1]": 2,
        "omega": 3,
        "nu": 4,
        "mu": 5
    })

    mock_results.aic = 1
    mock_results.bic = 2
    mock_results.loglikelihood = 3

    mock_results.conditional_volatility = pd.Series(
        [1, 2, 3, 4],
        index=returns["date"]
    )

    # Mock GARCH model and fit
    mock_model = Mock()
    mock_model.fit.return_value = mock_results
    mock_arch_model.return_value = mock_model

    # Mock residual ARCH-LM test
    mock_het_arch.return_value = (1, 2, 3, 4)

    # Run function
    figure, metrics = garch_analysis("common trade index",1,1)

    # Check outputs
    assert figure is not None
    assert isinstance(metrics, dict)

    # Check GARCH parameters were extracted correctly
    assert metrics["alpha"] == 1
    assert metrics["beta"] == 2
    assert metrics["omega"] == 3
    assert metrics["nu"] == 4
    assert metrics["mu"] == 5

    # Check persistence calculation
    # alpha + beta = 1 + 2 = 3
    assert metrics["persistence"] == 3

    # Check model statistics
    assert metrics["aic"] == 1
    assert metrics["bic"] == 2
    assert metrics["log_likelihood"] == 3

    # Check p-values were extracted
    assert metrics["alpha_p"] == 1
    assert metrics["beta_p"] == 2
    assert metrics["omega_p"] == 3
    assert metrics["nu_p"] == 4
    assert metrics["mu_p"] == 5

    # Check residual ARCH-LM results
    assert metrics["residual_arch_lm"] == 1
    assert metrics["residual_arch_p"] == 2
    assert metrics["residual_arch_f"] == 3
    assert metrics["residual_arch_f_p"] == 4

    # Check residual autocorrelation calculations exist
    assert metrics["residual_autocorrelation"] is not None
    assert metrics["squared_residual_autocorrelation"] is not None

    # Check the GARCH model was created and fitted
    mock_arch_model.assert_called_once()
    mock_model.fit.assert_called_once_with(disp="off")