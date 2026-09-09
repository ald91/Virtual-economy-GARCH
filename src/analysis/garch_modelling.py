""" explores data using plotly library"""


import plotly.graph_objects as go
import pandas as pd

from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.diagnostic import het_arch
from arch import arch_model

from src.config import ANALYSIS_DATA_DIR, SUPPORTED_INDEX_LIST
from src.data_helper import load_csv, save_csv

#=====================
#GARCH FUNCTIONS
#=====================

def arch_lm_test() -> pd.DataFrame:
    """Test return series for ARCH effects.

    The ARCH-LM test checks whether conditional variance depends
    on previous squared returns, providing evidence of volatility
    clustering.

    H0: No ARCH effects / conditional homoskedasticity.
    H1: ARCH effects are present.

    A p-value below 0.05 provides evidence of ARCH effects and
    supports further ARCH/GARCH modelling.
    """

    returns = load_csv("returns",ANALYSIS_DATA_DIR).set_index("date")
    results = []

    for index in SUPPORTED_INDEX_LIST:
        column_name = index.lower()
        returns_data = returns[column_name].dropna()

        lm_statistic, p_value, f_statistic, f_p_value = het_arch(
            returns_data,
            nlags=30
        )

        results.append({
            "index": column_name,
            "lm_statistic": lm_statistic,
            "p_value": p_value,
            "f_statistic": f_statistic,
            "f_p_value": f_p_value,
            "arch_effects": p_value < 0.05
        })

    results = pd.DataFrame(results)
    save_csv("lm_data",results,ANALYSIS_DATA_DIR)
    return results
    
def adf_test () -> pd.DataFrame:
    """ inspects a returns time series to deduce if a returns series
    is stationary or non-stationary. GARCH models require stationary
    returns series."""

    returns = load_csv("returns",ANALYSIS_DATA_DIR).set_index("date")
    results = []

    for index in SUPPORTED_INDEX_LIST:
        column_name = index.lower()
        returns_data = returns[column_name].dropna()
        adf_statistic, p_value, used_lags, nobs, critical_values, icbest = adfuller(returns_data)

        results.append({
            "index": column_name,
            "adf statistic": adf_statistic,
            "adf_p_value": p_value,
            "stationary": p_value < 0.05
        })
    results = pd.DataFrame(results)
    save_csv("adf_data",results,ANALYSIS_DATA_DIR)
    return results

def garch_analysis(index_name: str, p: int, q: int, category_filter: list | None = None, scope_filter: list | None = None) -> tuple:
    """Fit a GARCH model and plot conditional volatility with
    filtered exogenous events.

    The function also calculates diagnostics,
    including an ARCH-LM test on residuals and autocorrelation.
    These are used to assess whether the GARCH model has 
    captured the volatility dynamics of the series.

    Args:
        index_name (str): Name of the market index to analyse.
        p (int): Number of lagged (days) conditional variance terms.
        q (int): Number of lagged (days) squared return terms.
        category_filter (list | None): Categories of events to display.
            Use ["all"] or None to display all categories.
        scope_filter (list | None): Scopes of events to display.
            Use ["all"] or None to display all scopes.

    Returns:
        tuple: A Plotly figure showing GARCH conditional volatility
            with filtered exogenous events, and a dictionary
            containing GARCH model metrics.
    """

    # Load data
    events_dataframe = load_csv("events index", ANALYSIS_DATA_DIR)

    returns_dataframe = load_csv("returns", ANALYSIS_DATA_DIR).set_index("date")

    # Start with all events
    filtered_events = events_dataframe.copy()

    # Apply category filter
    if category_filter and "all" not in category_filter:
        filtered_events = filtered_events[filtered_events["category"].isin(category_filter)]

    # Apply scope filter
    if scope_filter and "all" not in scope_filter:
        filtered_events = filtered_events[filtered_events["scope"].isin(scope_filter)]

    # Convert decimal returns to percentage returns for GARCH
    returns = returns_dataframe[index_name].dropna() * 100

    # Create GARCH model
    model = arch_model(
        returns,
        mean="Constant",
        vol="GARCH",
        p=p,
        q=q,
        dist="t"
    )

    # Fit model
    results = model.fit(disp="off")

    # -------------------------
    # Post-estimation diagnostics
    # -------------------------

    standardized_residuals = results.std_resid.dropna()

    # tests to confirm if residuals stil show ARCH effects after GARCH
    residual_arch_lm, residual_arch_p, residual_arch_f, residual_arch_f_p = het_arch(standardized_residuals,nlags=30)

    # Autocorrelation (do past results impact the current result)
    residual_autocorrelation = standardized_residuals.autocorr()

    # Autocorrelation in squared residuals
    squared_residuals = standardized_residuals ** 2
    squared_residual_autocorrelation = squared_residuals.autocorr()

    #result values for clarity
    alpha = results.params.get("alpha[1]")
    beta = results.params.get("beta[1]")
    omega = results.params.get("omega")
    nu = results.params.get("nu")
    mu = results.params.get("mu")

    #p values for statistical significance
    alpha_p = results.pvalues.get("alpha[1]")
    beta_p = results.pvalues.get("beta[1]")
    omega_p = results.pvalues.get("omega")
    nu_p = results.pvalues.get("nu")
    mu_p = results.pvalues.get("mu")

    persistence = alpha + beta

    aic = results.aic
    bic = results.bic
    log_likelihood = results.loglikelihood

    # =========================
    # metrics dict for Garch Page
    # =========================

    metrics = {
        "alpha": alpha,
        "beta": beta,
        "persistence": persistence,
        "omega": omega,
        "nu": nu,
        "mu": mu,
        "aic": aic,
        "bic": bic,
        "log_likelihood": log_likelihood,
        "alpha_p": alpha_p,
        "beta_p": beta_p,
        "omega_p": omega_p,
        "nu_p": nu_p,
        "mu_p": mu_p,

        "residual_arch_lm": residual_arch_lm,
        "residual_arch_p": residual_arch_p,
        "residual_arch_f": residual_arch_f,
        "residual_arch_f_p": residual_arch_f_p,
        "residual_autocorrelation": residual_autocorrelation,
        "squared_residual_autocorrelation": squared_residual_autocorrelation,
    }
    
    print(results.summary())

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=returns.index,
            y=results.conditional_volatility,
            mode="lines",
            name="GARCH Conditional Volatility",
            line=dict(width=2),
            hovertemplate=(
                "Date: %{x|%d %b %Y}<br>"
                "Conditional volatility: %{y:.4f}"
                "<extra></extra>"
            )
        )
    )

    # -------------------------
    # Event markers filter
    # -------------------------

    if not filtered_events.empty:

        # Find a sensible position near the top of the volatility graph
        event_y = results.conditional_volatility.max()

        figure.add_trace(
            go.Scatter(
                x=filtered_events["date"],
                y=[event_y] * len(filtered_events),
                mode="markers",
                name="Exogenous Events",
                marker=dict(
                    size=9,
                    symbol="circle"
                ),
                customdata=filtered_events[
                    ["title", "category", "scope"]
                ].to_numpy(),
                hovertemplate=(
                    "Date: %{x|%d %b %Y}<br>"
                    "Event: %{customdata[0]}<br>"
                    "Category: %{customdata[1]}<br>"
                    "Scope: %{customdata[2]}"
                    "<extra></extra>"
                )
            )
        )

    # -------------------------
    # Layout
    # -------------------------

    figure.update_layout(
        title=(
            f"{index_name.title()} GARCH({p},{q}) "
            "Conditional Volatility"
        ),
        xaxis_title="Date",
        yaxis_title="Conditional Volatility",
        height=600,
        hovermode="closest"
    )

    return (figure, metrics)

