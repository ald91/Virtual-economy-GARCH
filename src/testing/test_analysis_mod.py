import pytest
import pandas as pd
from unittest.mock import Mock, patch

from src.analysis.statistical_analysis import ( calculate_returns, calculate_returns_squared, calculate_rolling_volatility, calculate_statistics)
from src.analysis.garch_modelling import ( arch_lm_test, adf_test, garch_analysis)

from src.config import SUPPORTED_INDEX_LIST

#------------------------
#statistical analysis.py
#------------------------

# T22- Test daily returns are calculated correctly
def test_calculate_returns():
    data = pd.DataFrame({
        "date": pd.to_datetime([
            "2025-01-01",
            "2025-01-02",
            "2025-01-03"
        ]),
        "common trade index": [100, 110, 99],
        "rune index": [200, 220, 242]
    })

    result = calculate_returns(data)

    assert "date" in result.columns
    assert list(result.columns) == [
        "date",
        "common trade index",
        "rune index"
    ]

    # First observation has no previous value
    assert pd.isna(result.loc[0, "common trade index"])

    # (110 - 100) / 100 = 0.10
    assert result.loc[1, "common trade index"] == pytest.approx(0.1) #floating point issue, maths correct

    # (99 - 110) / 110 = -0.10
    assert result.loc[2, "common trade index"] == pytest.approx(-0.1) #floating point issue, maths correct

# T23 - Test returns are squared correctly
def test_calculate_returns_squared():
    data = pd.DataFrame({
        "date": pd.to_datetime([
            "2025-01-01",
            "2025-01-02"
        ]),
        "common trade index": [0.10, -0.20],
        "rune index": [0.05, -0.10]
    })

    result = calculate_returns_squared(data)

    # 0.10 x 0.10 = 0.01
    assert result.loc[0, "common trade index"] == pytest.approx(0.01) #fp issue

    # -0.20 x -0.20 = 0.04
    assert result.loc[1, "common trade index"] == pytest.approx(0.04) #fp issue

    # Check negative returns become positive
    assert result.loc[1, "rune index"] == pytest.approx(0.01) #fp issue
 
    # Date should remain unchanged
    assert "date" in result.columns


# T24 - Test rolling volatility is calculated
def test_calculate_rolling_volatility():
    data = pd.DataFrame({
        "date": pd.date_range("2025-01-01", periods=4),
        "common trade index": [0.01, 0.02, 0.03, 0.04]
    })

    result = calculate_rolling_volatility(
        data,
        time_window=2
    )

    assert "date" in result.columns

    # First observation cannot have a 2-day rolling standard deviation as it is x = 1
    assert pd.isna(result.loc[0, "common trade index"])

    # Second observation should have a calculated value from 1 and 2
    assert not pd.isna(result.loc[1, "common trade index"])

    # Check the expected sample standard deviation
    expected = pd.Series([0.01, 0.02]).std()
    assert result.loc[1, "common trade index"] == pytest.approx(expected) #fp issue


# T25 - Test descriptive statistics are calculated
def test_calculate_statistics():
    data = pd.DataFrame({
        "common trade index": [0.01, 0.02, 0.03, 0.04],
        "rune index": [0.02, 0.04, 0.06, 0.08]
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

    assert result.loc["common trade index", "mean"] == 0.025
    assert result.loc["common trade index", "min"] == 0.01
    assert result.loc["common trade index", "max"] == 0.04

    assert result.loc["rune index", "mean"] == 0.05

#-----------------------------
#garch_modeling.py
#-----------------------------

# T26 - Test ARCH-LM analysis outputs required metrics (not mathematical)
@patch("src.analysis.garch_modelling.save_csv")
@patch("src.analysis.garch_modelling.load_csv")
@patch("src.analysis.garch_modelling.het_arch")
def test_arch_lm_test(mock_het_arch, mock_load_csv, mock_save_csv):

    dates = pd.date_range("2025-01-01", periods=4)
    returns = pd.DataFrame({"date": dates})

    for index in SUPPORTED_INDEX_LIST:
        returns[index.lower()] = [1, 2, 3, 4]

    mock_load_csv.return_value = returns
    mock_het_arch.return_value = (1, 0.01, 2, 0.02)
    result = arch_lm_test()

    assert isinstance(result, pd.DataFrame)
    assert "index" in result.columns
    assert "lm_statistic" in result.columns
    assert "p_value" in result.columns
    assert "f_statistic" in result.columns
    assert "f_p_value" in result.columns
    assert "arch_effects" in result.columns

    assert len(result) == len(SUPPORTED_INDEX_LIST)
    assert result["arch_effects"].all()

    mock_save_csv.assert_called_once()


# T27 - Test ADF stationarity analysis outputs required metrics (not mathematical)
@patch("src.analysis.garch_modelling.save_csv")
@patch("src.analysis.garch_modelling.load_csv")
@patch("src.analysis.garch_modelling.adfuller")
def test_adf_test(mock_adfuller, mock_load_csv, mock_save_csv):

    dates = pd.date_range("2025-01-01", periods=4)

    returns = pd.DataFrame({"date": dates})

    for index in SUPPORTED_INDEX_LIST:
        returns[index.lower()] = [1, 2, 3, 4]

    mock_load_csv.return_value = returns

    mock_adfuller.return_value = (
        1,              # ADF statistic
        0.02,           # p-value (need <0.05 to pass)
        3,              # used lags
        4,              # observations
        {"5%": -5},     # critical values
        6               # information criterion
    )

    result = adf_test()

    assert isinstance(result, pd.DataFrame)

    assert "index" in result.columns
    assert "adf statistic" in result.columns
    assert "adf_p_value" in result.columns
    assert "stationary" in result.columns

    assert len(result) == len(SUPPORTED_INDEX_LIST)

    assert result["stationary"].all()

    mock_save_csv.assert_called_once()



# T28 - Test GARCH analysis outputs required metrics (not mathematical)
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

    mock_results.aic = 10
    mock_results.bic = 20
    mock_results.loglikelihood = 30

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
    figure, metrics = garch_analysis(
        "common trade index",
        1,
        1
    )

    # Check outputs exist
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
    assert metrics["aic"] == 10
    assert metrics["bic"] == 20
    assert metrics["log_likelihood"] == 30

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