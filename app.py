""" Initializes the app and communicated with streamlit what to display on user display"""

import streamlit as lit

#------------------------
# Page Config
#------------------------

lit.set_page_config(
    page_title="Virtual Economies GARCH Project",
    page_icon="📈",
    layout="wide"
)


#------------------------
# Title
#------------------------

lit.title("📈 OSRS Consumer Price Index")
lit.write(
    """
    Analysis of Grand Exchange sector indices, inflation,
    and volatility behaviour in the Old School Runescape economy. 
    Data taken from the Grand Exchange Market watch, based on official Runescape data.
    """
)
