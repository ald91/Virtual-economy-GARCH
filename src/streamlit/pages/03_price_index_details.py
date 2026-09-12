""" X """

import streamlit as st
import pandas as pd

from src.config import SUPPORTED_INDEX_LIST, ECONOMY_MASTER_DATA, EVENTS_MASTER_DATA, RETURNS_DATA, SQ_RETURNS_DATA, VOL30_DATA, VOL7_DATA, LM_DATA, ADF_DATA
from src.streamlit.steamlit_helpers import filter_dataframe
from src.streamlit.ui.graph_box import graph_box



#------------------------
# Page Config
#------------------------

SUPPORTED_INDEX_LIST = list(SUPPORTED_INDEX_LIST)

#from previous page
INDEX_NAME = str(st.query_params.get("index"))

if INDEX_NAME is None or INDEX_NAME not in SUPPORTED_INDEX_LIST:
    st.warning(f"No index selected or your submitted index is invalid ({INDEX_NAME}). Please select an index.")

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


#------------------------
# Load Data
#------------------------
ECONOMIC_DATA = pd.read_csv(ECONOMY_MASTER_DATA)
ECONOMIC_DATA["date"] = pd.to_datetime(ECONOMIC_DATA["date"],errors="coerce")

EVENTS_DATA = pd.read_csv(EVENTS_MASTER_DATA)
EVENTS_DATA["date"] = pd.to_datetime(EVENTS_DATA["date"],errors="coerce")

RETURNS_DATA = pd.read_csv(RETURNS_DATA)
RETURNS_DATA["date"] = pd.to_datetime(RETURNS_DATA["date"], errors="coerce")

SQ_DATA = pd.read_csv(SQ_RETURNS_DATA)
SQ_DATA["date"] = pd.to_datetime(SQ_DATA["date"], errors="coerce")

V7_DATA = pd.read_csv(VOL7_DATA)
V7_DATA["date"] = pd.to_datetime(V7_DATA["date"], errors="coerce")

V30_DATA = pd.read_csv(VOL30_DATA)
V30_DATA["date"] = pd.to_datetime(V30_DATA["date"], errors="coerce")

ADF_DATA = pd.read_csv(ADF_DATA)
LM_DATA = pd.read_csv(LM_DATA)

#------------------------
# Title
#------------------------

st.title(f"{INDEX_NAME.title()} — Detailed Statistics")
if INDEX_NAME is not None:
    st.write(
        f"""
            Detailed economic statistics for {INDEX_NAME} showing a
            range of metrics and where applicable GARCH analysis if
            data fits the GARCH hypothesis.
        """
    )



# -----------------------
# GARCH Eligibility
# -----------------------

lm_result = LM_DATA.loc[LM_DATA["index"] == INDEX_NAME]
lm_result_value = bool(lm_result["arch_effects"].iloc[0])
lm_p_value = lm_result["p_value"].iloc[0]

adf_result = ADF_DATA.loc[ADF_DATA["index"] == INDEX_NAME]
adf_result_value = bool(adf_result["stationary"].iloc[0])
adf_p_value = adf_result["adf_p_value"].iloc[0]

garch_eligibility = lm_result_value and adf_result_value

st.divider()

st.subheader("GARCH Model Suitability")

st.write(
    "The ADF and ARCH-LM tests provide preliminary statistical evidence "
    "for whether GARCH modelling is appropriate for this market index."
)

col1, col2 = st.columns(2)

with col1:

    st.markdown("### ADF — Stationarity")

    st.caption(
        "The Augmented Dickey-Fuller (ADF) test examines whether the "
        "return series is stationary. Stationary returns are generally "
        "required for modelling volatility with GARCH."
    )

    
    st.metric(
        "ADF p-value",
        f"{adf_p_value:.4g}"
    )

    if adf_result_value:
        st.success(
            "Stationary returns detected"
        )
    else:
        st.warning(
            "Stationarity not supported"
        )

    if adf_p_value < 0.05:
        st.info(
            "The p-value is below 0.05, providing evidence against the "
            "presence of a unit root and supporting stationarity."
        )
    else:
        st.info(
            "The p-value is at or above 0.05, so there is insufficient "
            "evidence to reject the hypothesis."
        )

    with st.expander("View full ADF test results"):
        st.dataframe(adf_result)



with col2:

    st.markdown("### ARCH-LM — Volatility Clustering")
    st.caption(
        "The ARCH-LM test examines whether the variance of returns "
        "changes over time, providing evidence of volatility clustering."
        "this metric shows if GARCH investigation is advisable."
    )

    st.metric(
        "ARCH-LM p-value",
        f"{lm_p_value:.4g}"
    )

    if lm_result_value:
        st.success(
            "Evidence of ARCH effects detected"
        )
    else:
        st.warning(
            "ARCH effects not supported"
        )

    if lm_p_value < 0.05:
        st.info(
            "The p-value is below 0.05, providing evidence of "
            "conditional heteroskedasticity and supporting ARCH/GARCH "
            "volatility modelling."
        )
    else:
        st.info(
            "The p-value is at or above 0.05, so there is insufficient "
            "evidence of ARCH effects in this return series."
        )


    with st.expander("View full ARCH-LM test results"):
        st.dataframe(lm_result)

# -----------------------
# GARCH OUTPUT
# -----------------------

st.divider()

st.subheader("Overall GARCH Assessment")

if garch_eligibility:
    
    st.success(
        "GARCH modelling is supported by the preliminary tests. "
    )

    if st.button("View GARCH Analysis",type="primary"):
        st.switch_page("pages/04_garch_analysis.py", query_params={"index": INDEX_NAME})

    st.write(
        "The return series satisfies the stationarity condition tested "
        "by the ADF test and shows evidence of ARCH effects in the "
        "ARCH-LM test. These results provide statistical support for "
        "further GARCH modelling."
    )



else:

    st.warning(
        "GARCH modelling is not supported by both preliminary tests."
    )

    st.write(
        "At least one of the preliminary tests does not provide the "
        "required evidence for GARCH modelling. The results should "
        "therefore be interpreted cautiously and further investigation "
        "may be required."
    )
#------------------------
# filters
#------------------------

def reset_date_filter():
    st.session_state["date_filter"] = (ECONOMIC_DATA["date"].min().date(), ECONOMIC_DATA["date"].max().date())

min_date = ECONOMIC_DATA["date"].min().date()
max_date = ECONOMIC_DATA["date"].max().date()

if "date_filter" not in st.session_state:
    st.session_state["date_filter"] = (ECONOMIC_DATA["date"].min().date(), ECONOMIC_DATA["date"].max().date())

if INDEX_NAME is not None and INDEX_NAME in SUPPORTED_INDEX_LIST:

    col1, col2 = st.columns([5, 1])

    with col1:
        selected_dates = st.date_input(
            "Date Range",
            min_value=min_date,
            max_value=max_date,
            key="date_filter"
        )

    with col2:
        st.write("")
        st.write("")

        st.button(
            "Reset",
            use_container_width=True,
            on_click=reset_date_filter
        )

    filtered_economic_data = ECONOMIC_DATA
    filtered_returns_data = RETURNS_DATA
    filtered_v7_data = V7_DATA
    filtered_v30_data = V30_DATA
    filtered_sq_data = SQ_DATA

    if len(selected_dates) == 2:
        start_date, end_date = selected_dates

        filtered_economic_data = filter_dataframe(ECONOMIC_DATA,"date",start_date,end_date)
        filtered_returns_data = filter_dataframe(RETURNS_DATA,"date",start_date,end_date)
        filtered_sq_data = filter_dataframe(SQ_DATA,"date",start_date,end_date)
        filtered_v7_data = filter_dataframe(V7_DATA,"date",start_date,end_date)
        filtered_v30_data = filter_dataframe(V30_DATA,"date",start_date,end_date)

    min_date = filtered_economic_data["date"].min().date()
    max_date = filtered_economic_data["date"].max().date()


    #-------------------------
    # Normal CPI Graph
    #-------------------------

    min_value = min_date.strftime("%d %b %Y")
    max_value = max_date.strftime("%d %b %Y")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Price Index line graph" )
    with col2:
        st.subheader("")

    graph_box(filtered_economic_data,INDEX_NAME,3,"price")

    #-------------------------
    # returns Graph
    #-------------------------

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("returns analysis" )
    with col2:
        st.subheader("")

    graph_box(filtered_returns_data,INDEX_NAME,3,"returns")

    #-------------------------
    # returns SQ Graph
    #-------------------------

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("square returns analysis" )
    with col2:
        st.subheader("")

    graph_box(filtered_sq_data,INDEX_NAME,3,"sq")

    #-------------------------
    # Volatility Graph
    #-------------------------

    min_value = min_date.strftime("%d %b %Y")
    max_value = max_date.strftime("%d %b %Y")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Volatility analysis" )
    with col2:
        st.subheader("7 and 30 day rolling volatility information")

    graph_box(filtered_v7_data,INDEX_NAME,3,"vol7")
    graph_box(filtered_v30_data,INDEX_NAME,3,"vol30")

else:
    st.write("No suitable index selected.")