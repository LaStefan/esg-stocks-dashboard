import streamlit as st

# Define the pages
pg = st.navigation([
    st.Page("home.py", title="Home", icon="🏡"), 
    st.Page("esg.py", title="ESG Scores", icon="📊"),
    st.Page("pricing.py", title="Stocks Analysis", icon="💹"),
    st.Page("RutgerDB.py", title="RutgerDB", icon="📊")
    ])

# Set the page configuration (this should be the first Streamlit command)
st.set_page_config(page_title="ESG Dashboard", page_icon=":bar_chart:", layout='wide', initial_sidebar_state='expanded')

# Run the page navigation
pg.run()