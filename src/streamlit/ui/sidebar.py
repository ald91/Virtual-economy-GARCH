import streamlit as st


def render_sidebar():

    with st.sidebar:
        st.title("Virtual Economy GARCH")
        st.divider()

        st.caption(
            "MSc project investigating volatility "
            "and adjustment in MMORPG virtual markets."
        )