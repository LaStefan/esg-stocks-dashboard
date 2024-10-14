import streamlit as st

# Set the page configuration
st.set_page_config(page_title="ESG Dashboard", page_icon=":bar_chart:", layout='wide', initial_sidebar_state='expanded')

# Define the pages
pg = st.navigation([
    st.Page("app.py", title="Home", icon="🏡"), 
    st.Page("esg.py", title="ESG Scores", icon="📊")
])

# Streamlit Title
st.title("Sustainable Investing With ESG")

# Run the page navigation
pg.run()