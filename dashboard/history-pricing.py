import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import numpy as np

# File path to known CSV
file_path = "../data/transformed/pricing_history.csv"

# Check if the file exists and load data
try:
    history = pd.read_csv(file_path)
    stock = pd.read_csv("../data/transformed/stock.csv")

    sub_stock = stock[['ticker_symbol', 'name']]

    pricing_history = pd.merge(history, sub_stock, on='ticker_symbol')
    
    # Check that required columns are present
    required_columns = {'ticker_symbol', 'date', 'close', 'high', 'low', 'name'}
    if required_columns.issubset(pricing_history.columns):
        
        # Convert date column to datetime format
        pricing_history['date'] = pd.to_datetime(pricing_history['date'])

        # Ticker selection
        ticker_symbols = pricing_history['ticker_symbol'].unique()
        stock_names = pricing_history['name'].unique()
        selected_ticker = st.selectbox("Select a stock", stock_names)

        # Moving average days setting
        avenr_raw = st.slider("Select days for moving average (averaging period before and after each date)", 
                          min_value=3, max_value=200, value=50)
        avenr = int((avenr_raw-1) / 2)

        # Filter data for selected ticker
        hist_pri = pricing_history[pricing_history['name'] == selected_ticker]
        close = hist_pri['close'].values
        high = hist_pri['high'].values
        low = hist_pri['low'].values
        date = hist_pri['date'].values
        name = hist_pri['name'].unique()[0]

        # Calculate moving average for 'close' price
        aveclose = [np.mean(close[max(0, j - avenr):min(len(close), j + avenr)]) for j in range(len(close))]

        # Create Plotly figure
        fig = go.Figure()

        # Add traces for high and low prices
        fig.add_trace(go.Scatter(x=date, y=high, mode='lines', name='High Price', line=dict(color='cyan')))
        fig.add_trace(go.Scatter(x=date, y=low, mode='lines', name='Low Price', line=dict(color='cyan')))

        # Add trace for closing price
        fig.add_trace(go.Scatter(x=date, y=close, mode='lines', name='Closing Price', line=dict(color='blue')))

        # Add trace for moving average
        fig.add_trace(go.Scatter(x=date, y=aveclose, mode='lines', name=f'Moving Average ({avenr * 2 + 1} days)', line=dict(color='red')))

        # Update layout with titles and axis labels
        fig.update_layout(title=f"Historic Closing Prices of {name}",
                          xaxis_title='Date',
                          yaxis_title='Price ($)',
                          xaxis_tickformat='%Y-%m-%d',
                          xaxis_rangeslider_visible=True)

        # Display plot in Streamlit
        st.plotly_chart(fig)

    else:
        st.error(f"The file must contain the following columns: {', '.join(required_columns)}")

except FileNotFoundError:
    st.error(f"The file at {file_path} was not found.")
