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
}


pages = [
    st.Page(
        page["path"],
        title=page["title"],
        icon=page["icon"],
    )
    for page in page_dict.values()
]


pg = st.navigation(pages)

render_sidebar()

pg.run()