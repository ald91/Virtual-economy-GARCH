import streamlit as st

import pandas as pd

from src.config import SUPPORTED_INDEX_LIST, EVENTS_MASTER_DATA

from src.analysis.garch_modelling import garch_analysis


#------------------------
# Page Config
#------------------------

SUPPORTED_INDEX_LIST = list(SUPPORTED_INDEX_LIST)

#from previous page
INDEX_NAME = st.query_params.get("index")

if INDEX_NAME is None or INDEX_NAME not in SUPPORTED_INDEX_LIST:

    selected_index = st.selectbox(
        "Select Index",
        options= [None] + SUPPORTED_INDEX_LIST,
        key="index_selector",
        index=0
    )

    if selected_index in SUPPORTED_INDEX_LIST:
        st.query_params["index"] = selected_index
        st.rerun()

st.set_page_config(
    page_title=f"{INDEX_NAME.title()} — Detailed Statistics",
    page_icon="📈",
    layout="wide"
)
#------------
# data
#------------
EVENTS_DATA = pd.read_csv(EVENTS_MASTER_DATA)
EVENTS_DATA["date"] = pd.to_datetime(EVENTS_DATA["date"],errors="coerce")

#------------------------
# Title
#------------------------

st.title(f"{INDEX_NAME.title()} — GARCH Analysis Statistics")
if INDEX_NAME is not None:
    st.write(
        f"""
            GARCH analysis outcomes for {INDEX_NAME} showing a
            range of relavent metrics and their significance
        """
    )

    st.info(
    "Visual proximity between an exogenous event and a period of high "
    "volatility does not establish a causal relationship. However, such "
    "patterns may identify periods that warrant further investigation."
    )


# -----------------------
# Event Filters
# -----------------------


categories = sorted(EVENTS_DATA["category"].dropna().unique())

st.write("Event Categories")

selected_categories = []

for start in range(0, len(categories), 5):

    row_categories = categories[start:start + 5]
    category_cols = st.columns(5)

    for i, category in enumerate(row_categories):
        with category_cols[i]:
            if st.checkbox(category, value=True):
                selected_categories.append(category)
                  
filtered_events = EVENTS_DATA[EVENTS_DATA["category"].isin(selected_categories)]



# -----------------------
# Event Statistics
# -----------------------

TOTAL_EVENTS = len(filtered_events)

col1, col2, col3 = st.columns(3)

if filtered_events.empty:

    col1.metric("Total Events", 0)
    col2.metric("Earliest Event", "No Events")
    col3.metric("Latest Event", "No Events")

else:

    OLDEST_EVENT = filtered_events["date"].min()
    NEWEST_EVENT = filtered_events["date"].max()

    col1.metric("Total Events", TOTAL_EVENTS)
    col2.metric("Earliest Event",OLDEST_EVENT.strftime("%d %b %Y"))
    col3.metric("Latest Event",NEWEST_EVENT.strftime("%d %b %Y"))


# -----------------------
# GARCH Analysis
# -----------------------

figure, metrics = garch_analysis(
    INDEX_NAME,
    1,
    1,
    selected_categories
)

selected_points = st.plotly_chart(
    figure,
    use_container_width=True
)

residual_arch_p = metrics["residual_arch_p"]
persistence = metrics["persistence"]

#-------------------------
#events identification
#-------------------------

st.subheader("Exogenous Events")
st.write("A full table of exogenous events stored in the application database.")

st.dataframe(
filtered_events,
width='stretch',
hide_index=True
)

# -----------------------
# GARCH Metrics
# -----------------------

st.subheader("Volatility Dynamics")

col1, col2 = st.columns(2)

with col1:

    st.markdown("**Alpha (α)**")
    st.markdown(f"### {metrics['alpha']:.4f}")
    st.caption(
        "Response of volatility to new market shocks."
    )

    if metrics["alpha_p"] < 0.05:
        st.success(
            "Statistically significant at the 5% level."
        )
    else:
        st.caption(
            "Not statistically significant at the 5% level."
        )

    st.markdown("**Beta (β)**")
    st.markdown(f"### {metrics['beta']:.4f}")
    st.caption(
        "Persistence of previous volatility into the current period."
    )

    if metrics["beta_p"] < 0.05:
        st.success(
            "Statistically significant at the 5% level."
        )
    else:
        st.caption(
            "Not statistically significant at the 5% level."
        )


with col2:

    st.markdown("**Persistence (α + β)**")
    st.markdown(f"### {metrics['persistence']:.4f}")
    st.caption(
        "Overall persistence of volatility. Values closer to 1 "
        "indicate slower adjustment after shocks."
    )

    if persistence < 0.8:
        st.success(
            "Volatility shocks are estimated to decay relatively quickly."
        )

    elif persistence < 0.95:
        st.info(
            "Volatility is persistent, with shocks expected to decay "
            "over several periods."
        )

    elif persistence < 1:
        st.warning(
            "Volatility is highly persistent and shocks are expected "
            "to decay slowly."
        )

    else:
        st.warning(
            "Persistence is at or above 1. This is at or beyond the "
            "standard GARCH boundary and requires further investigation."
        )

    st.markdown("**Omega (ω)**")
    st.markdown(f"### {metrics['omega']:.4f}")
    st.caption(
        "Baseline component of the conditional variance."
    )

# -----------------------
# Model Diagnostics
# -----------------------

st.subheader("Post-Estimation Diagnostics")

st.write(
    "These diagnostics assess whether the fitted GARCH model has "
    "adequately accounted for volatility clustering in the return series."
)

# -----------------------
# Remaining ARCH effects
# -----------------------

st.markdown("### Remaining ARCH Effects")

if residual_arch_p >= 0.05:

    st.success(
        f"ARCH-LM test: p = {residual_arch_p:.4f}. "
        "There is insufficient evidence of remaining ARCH effects at "
        "the 5% significance level. This supports the fitted"
        "GARCH model in capturing volatility clustering."
    )

else:

    st.warning(
        f"ARCH-LM test: p = {residual_arch_p:.4f}. "
        "Significant remaining ARCH effects are present at the 5% level. "
        "This suggests that the fitted GARCH model may not fully capture "
        "the volatility dynamics."
    )

# -----------------------
# Residual dependence
# -----------------------

st.markdown("### Residual Dependence")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Standardised residual autocorrelation",
        f"{metrics['residual_autocorrelation']:.4f}"
    )

    st.caption(
        "Measures linear dependence between consecutive standardised residuals."
        "Values closer to zero indicate weaker linear dependence."
    )

with col2:

    st.metric(
        "Squared residual autocorrelation",
        f"{metrics['squared_residual_autocorrelation']:.4f}"
    )

    st.caption(
        "Measures dependence in the squared residuals."
        "an indication of remaining volatility clustering."
    )

# -----------------------
# Overall Diagnostic Assessment
# -----------------------

st.markdown("### Overall Assessment")

if residual_arch_p >= 0.05:

    st.success(
        "The post-estimation ARCH-LM test provides no significant evidence"
        "of remaining ARCH effects. This supports the use of the fitted "
        "GARCH model for investigating the volatility this index."
    )

else:

    st.warning(
        "The post-estimation ARCH-LM test identifies significant remaining "
        "ARCH effects. The fitted GARCH model may not fully capture the "
        "volatility of this index, so its results should be "
        "interpreted with caution."
    )