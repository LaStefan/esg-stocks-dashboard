# streamlit_app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Set title and description
st.title("Stock Price History and Moving Average Visualization")
st.write("""
This app visualizes historical stock prices with an adjustable moving average. 
Upload a CSV file containing stock data, choose a ticker, and customize the averaging window.
""")

# File uploader for CSV
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

if uploaded_file is not None:
    # Load the data
    pricing_history = pd.read_csv(uploaded_file)

    # Check that required columns are present
    required_columns = {'ticker_symbol', 'date', 'close', 'high', 'low'}
    if required_columns.issubset(pricing_history.columns):
        
        # Convert date column to datetime format
        pricing_history['date'] = pd.to_datetime(pricing_history['date'])

        # Ticker selection
        ticker_symbols = pricing_history['ticker_symbol'].unique()
        selected_ticker = st.selectbox("Select a Ticker Symbol", ticker_symbols)

        # Moving average days setting
        avenr = st.slider("Select days for moving average (averaging period before and after each date)", 
                          min_value=1, max_value=100, value=50)

        # Filter data for selected ticker
        hist_pri = pricing_history[pricing_history['ticker_symbol'] == selected_ticker]
        close = hist_pri['close'].values
        high = hist_pri['high'].values
        low = hist_pri['low'].values
        date = hist_pri['date'].values

        # Calculate moving average for 'close' price
        aveclose = [np.mean(close[max(0, j-avenr):min(len(close), j+avenr)]) for j in range(len(close))]

        # Plotting
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot high and low prices
        ax.plot(date, high, color='c', label='High Price')
        ax.plot(date, low, color='c', label='Low Price')

        # Plot closing price and moving average
        ax.plot(date, close, color='b', label='Closing Price')
        ax.plot(date, aveclose, color='r', label=f'Moving Average ({avenr * 2 + 1} days)')

        # Format date and labels
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=-45)
        plt.xlabel('Date')
        plt.ylabel('Price ($)')
        plt.title(f"Historic Closing Prices of {selected_ticker}")
        plt.legend()
        plt.grid(True)

        # Display plot in Streamlit
        st.pyplot(fig)

    else:
        st.error(f"The uploaded file must contain the following columns: {', '.join(required_columns)}")
else:
    st.info("Please upload a CSV file.")
