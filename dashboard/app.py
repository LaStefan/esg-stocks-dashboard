import streamlit as st
import json
import requests
import pandas as pd
import numpy as np

# Set the page configuration
st.set_page_config(page_title="ESG Stocks Dashboard", page_icon="📈")

# Streamlit Title
st.title("Stock Prices & ESG Score Analysis")

# Load the API key from the config file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Fetch API key
api_key = config.get('ALPHAVANTAGE_API_KEY')

# Define URL for API request
url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&apikey={api_key}'

# Make the API request
r = requests.get(url)
data = r.json()

# Access the time series data
daily_data = data.get('Time Series (Daily)', {})

# Convert to DataFrame
df = pd.DataFrame.from_dict(daily_data, orient='index')

# Convert index to datetime
df.index = pd.to_datetime(df.index)

# Optionally, sort the index
df.sort_index(inplace=True)

# Add the symbol as a column at the beginning
df.insert(0,'Company', 'IBM')

# Display the DataFrame in Streamlit
st.header("IBM Stock Prices")
if st.checkbox('Show stocks table'):
    st.dataframe(df)

if st.checkbox('Show chart'):
# Line chart plot
    chart_data = pd.DataFrame(
     np.random.randn(20, 3),
     columns=['a', 'b', 'c'])
    st.line_chart(chart_data)

# Map plot
map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.map(map_data)

#  Slider could be cool to use when filtering values
x = st.slider('x')  # 👈 this is a widget
st.write(x, 'squared is', x * x)