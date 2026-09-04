""" X """

import streamlit as st
from src.config import SUPPORTED_INDEX_LIST

#------------------------
# Page Config
#------------------------

SUPPORTED_INDEX_LIST = list(SUPPORTED_INDEX_LIST)

#from previous page
index_name = st.query_params.get("index")

if index_name is None or index_name not in SUPPORTED_INDEX_LIST:
    st.warning(f"No index selected or your submitted index is invalid ({index_name}). Please select an index.")

    selected_index = st.selectbox(
        "Select Index",
        options= [None] + SUPPORTED_INDEX_LIST,
        key="index_selector",
        index=0
    )

    if selected_index in SUPPORTED_INDEX_LIST:
        st.query_params["index"] = selected_index
        st.rerun()

st.title(f"{index_name.title()} — Detailed Statistics")

#------------------------
# Title
#------------------------

st.title("📈 X")
st.write(
    """
        TEST
    """
)
