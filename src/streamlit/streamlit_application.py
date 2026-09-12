import streamlit as st
import sys
from pathlib import Path

from ui.sidebar import render_sidebar

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

page_dict = {
    "home": {
        "path": "pages/home.py",
        "title": "Home",
        "icon": "🏠",
    },
    "events": {
        "path": "pages/01_events.py",
        "title": "Events Overview",
        "icon": "📰",
    },
    "price_indices": {
        "path": "pages/02_price_indices_overview.py",
        "title": "Price Indices",
        "icon": "📊",
    },
    "price_index_details": {
        "path": "pages/03_price_index_details.py",
        "title": "Price Index Details",
        "icon": "📈",
    },
    "GARCH_analysis": {
        "path" : "pages/04_garch_analysis.py",
        "title" : "GARCH Analysis",
        "icon" : "📈"
    }
}


main_pages = [
    st.Page(
        page_dict["home"]["path"],
        title=page_dict["home"]["title"],
        icon=page_dict["home"]["icon"],
    ),
    st.Page(
        page_dict["events"]["path"],
        title=page_dict["events"]["title"],
        icon=page_dict["events"]["icon"],
    ),
    st.Page(
        page_dict["price_indices"]["path"],
        title=page_dict["price_indices"]["title"],
        icon=page_dict["price_indices"]["icon"],
    ),
]

detail_pages = [
    st.Page(
        page_dict["price_index_details"]["path"],
        title=page_dict["price_index_details"]["title"],
        icon=page_dict["price_index_details"]["icon"],
    ),
    st.Page(
        page_dict["GARCH_analysis"]["path"],
        title=page_dict["GARCH_analysis"]["title"],
        icon=page_dict["GARCH_analysis"]["icon"],
    ),
]

pages = {
    "Main": main_pages,
    "Advanced": detail_pages,
}

pg = st.navigation(pages, position="sidebar")

pg = st.navigation(pages)

render_sidebar()

pg.run()