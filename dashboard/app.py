import streamlit as st
import json
import requests
import pandas as pd

# Streamlit Title
st.title("Stock Prices & ESG Score Analysis")

# Load the API key from the config file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Fetch API key
api_key = config.get('ALPHAVANTAGE_API_KEY')

# Define URL for API request
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey={api_key}'

# Make the API request
r = requests.get(url)
data = r.json()

# Access the time series data
time_series = data.get('Time Series (5min)', {})

# Convert to DataFrame
df = pd.DataFrame.from_dict(time_series, orient='index')

# Convert index to datetime
df.index = pd.to_datetime(df.index)

# Optionally, sort the index
df.sort_index(inplace=True)

# Add the symbol as a column
df['Company'] = 'IBM'

# Reorder columns if needed, placing 'Company' at the front
cols = ['Company'] + [col for col in df.columns if col != 'Company']
df = df[cols]

# Display the DataFrame in Streamlit
st.header("IBM Stock Prices")
st.dataframe(df)
