import streamlit as st

def render_sidebar():

    st.sidebar.title("OSRS Economy Tool")

    page = st.sidebar.radio(
        "Navigation",
        [
            "Home",
            "Market Overview",
            "Event Analysis",
            "Statistical Analysis",
            "GARCH Analysis",
            "About"
        ]
    )

    return page