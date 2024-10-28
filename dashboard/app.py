import streamlit as st

from news import render_news_sidebar

# Define the pages
pg = st.navigation([
    st.Page("home.py", title="Home", icon="🏡"), 
    st.Page("esg.py", title="ESG and Market Performance", icon="📊"),
    st.Page("pricing.py", title="Stocks Analysis", icon="💹"),
    st.Page("pelle.py", title="ESG Scores vs Market Performance", icon="📈"),
    st.Page("jort.py", title="Jort", icon="📈"),

])

# Set the page configuration (this should be the first Streamlit command)
st.set_page_config(page_title="ESG Dashboard", page_icon=":bar_chart:", layout='wide', initial_sidebar_state='expanded')

# Run the page navigation
pg.run()

# render news sidebar 
render_news_sidebar()