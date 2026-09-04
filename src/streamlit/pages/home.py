
import streamlit as st

#------------------------
# Page Config
#------------------------

st.set_page_config(
    page_title="Virtual Economies GARCH Project",
    page_icon="📈",
    layout="wide"
)

#------------------------
# Title
#------------------------

st.title("📈 Volatility in Virtual Economies a GARCH study on Old School Runescape")
st.write(
    """
    This application allows the user to explore the economic stability and 
    volatility of virtual economies. \n
    This particular application is focused on the massively multiplayer online role Playing Game (MMORPG) Old School Runescape (OSRS)
    by Jagex: The Runescape Company. \n
    All data is obtained from the official OSRS Wiki using the Grand Exchange Market Watch API (GEMW) and the Wiki API.
    """
)


#-------------------------
# Page contents
#-------------------------
