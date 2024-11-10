import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import finnhub
import dotenv
import plotly.express as px
import plotly.graph_objs as go
import numpy as np

def truncate_text(text, max_sentences=3):
    sentences = text.split('. ')
    if len(sentences) <= max_sentences:
        return text
    truncated_sentences = '. '.join(sentences[:max_sentences]) + "."
    return truncated_sentences
dotenv.load_dotenv()

engine = create_engine("postgresql://team13:team13@esg-stocks-db:5432/esg-stocks-database")

# Join all 3 tables and select certain columns
query = """
SELECT 
st.ticker_symbol, 
st.logo,
st.description,
st.name 
FROM stock AS st
"""

# Use pandas to read the data
df = pd.read_sql_query(query, engine)
selected_stock_name = st.selectbox('Stock:', df['name'])
selected_ticker_symbol = df[df['name'] == selected_stock_name]['ticker_symbol'].values[0]

# Display the selected ticker symbol for debugging purposes
logo_url = df[df['name'] == selected_stock_name]['logo'].values[0]
st.markdown(
    f"""
    <div style='display: flex; align-items: center;'>
        <img src='{logo_url}' style='height: 50px; margin-right: 10px;'>
        <h1 style='margin: 0; padding:0'>{selected_stock_name}</h1>
    </div>
    """,
    unsafe_allow_html=True
)
st.caption(truncate_text(df[df['name'] == selected_stock_name]['description'].values[0]))

finnhub_client = finnhub.Client('csbu6j9r01qgt32ev61gcsbu6j9r01qgt32ev620')
recommendation_response = finnhub_client.recommendation_trends(selected_ticker_symbol)

df = pd.DataFrame(recommendation_response)
df['period'] = pd.to_datetime(df['period'])
df['month'] = df['period'].dt.strftime('%B')
df = df.sort_values(by='period')  

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df['month'],
    y=df['strongSell'],
    name='Strong Sell',
    marker_color='red'
))
fig.add_trace(go.Bar(
    x=df['month'],
    y=df['sell'],
    name='Sell',
    marker_color='lightcoral'
))
fig.add_trace(go.Bar(
    x=df['month'],
    y=df['hold'],
    name='Hold',
    marker_color='#d1d1d1'
))
fig.add_trace(go.Bar(
    x=df['month'],
    y=df['buy'],
    name='Buy',
    marker_color='#60b360'
))
fig.add_trace(go.Bar(
    x=df['month'],
    y=df['strongBuy'],
    name='Strong Buy',
    marker_color='green'
))

# Customize layout
fig.update_layout(
    title="Analyst Recommendations",
    xaxis_title="Month",
    yaxis_title="Number of Recommendations",
    xaxis=dict(categoryorder='category ascending'),
    barmode='stack',
)
st.plotly_chart(fig)

st.write('---') # PRICING HISTORY OVER YEARS

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
        # selected_ticker = st.selectbox("Select a stock", stock_names)

        # Moving average days setting
        avenr_raw = st.slider("Select days for moving average (averaging period before and after each date)", 
                          min_value=3, max_value=200, value=50)
        avenr = int((avenr_raw-1) / 2)

        # Filter data for selected ticker
        hist_pri = pricing_history[pricing_history['name'] == selected_stock_name]
        close = hist_pri['close'].values
        high = hist_pri['high'].values
        low = hist_pri['low'].values
        date = hist_pri['date'].values
        name = hist_pri['name'].unique()[0]

        # Calculate moving average for 'close' price
        aveclose = [np.mean(close[max(0, j - avenr):min(len(close), j + avenr)]) for j in range(len(close))]

        # Create Plotly figure
        fig_price_hist = go.Figure()

        # Add traces for high and low prices
        fig_price_hist.add_trace(go.Scatter(x=date, y=high, mode='lines', name='High Price', line=dict(color='cyan')))
        fig_price_hist.add_trace(go.Scatter(x=date, y=low, mode='lines', name='Low Price', line=dict(color='cyan')))

        # Add trace for closing price
        fig_price_hist.add_trace(go.Scatter(x=date, y=close, mode='lines', name='Closing Price', line=dict(color='blue')))

        # Add trace for moving average
        fig_price_hist.add_trace(go.Scatter(x=date, y=aveclose, mode='lines', name=f'Moving Average ({avenr * 2 + 1} days)', line=dict(color='red')))

        # Update layout with titles and axis labels
        fig_price_hist.update_layout(title=f"Historic Closing Prices of {name}",
            xaxis=dict(
                title='Date',
                tickformat='%Y-%m-%d',
                showgrid=True,               # Enable vertical gridlines
                gridcolor='lightgray',       # Set gridline color
                gridwidth=1                  # Set gridline width
            ),
            yaxis=dict(
                title='Price ($)',
                showgrid=True,               # Enable horizontal gridlines if desired
                gridcolor='lightgray',
                gridwidth=0.5
            ),
            xaxis_rangeslider_visible=True
        )

        # Display plot in Streamlit
        st.plotly_chart(fig_price_hist)

    else:
        st.error(f"The file must contain the following columns: {', '.join(required_columns)}")

except FileNotFoundError:
    st.error(f"The file at {file_path} was not found.")




# Quarterly Averages
st.title('Quarterly Average Margin by Industry')
st.write('This dashboard shows the quarterly average margins for each industry.')
st.write('----------------------------------------------------------------------------------')

# SQL query to join the pricing_history and stock tables
query = """
SELECT ph.ticker_symbol, ph.date, ph.open, ph.close, s.industry 
FROM pricing_history ph
JOIN stock s ON ph.ticker_symbol = s.ticker_symbol
"""

# Use pandas to read the data
df = pd.read_sql_query(query, engine)

# Ensure numeric and date conversions
df['open'] = pd.to_numeric(df['open'])
df['close'] = pd.to_numeric(df['close'])
df['date'] = pd.to_datetime(df['date'])

# Calculate the margin
df['margin'] = ((df['close'] - df['open']) / df['open']) * 100

# Create a 'year_quarter' column to represent the year and quarter
df['year_quarter'] = df['date'].dt.to_period('Q')

# Group by 'industry' and 'year_quarter', then calculate the mean margin
quarterly_avg_df = df.groupby(['industry', 'year_quarter'])['margin'].mean().reset_index()

# Convert 'year_quarter' back to a timestamp for easier plotting
quarterly_avg_df['year_quarter'] = quarterly_avg_df['year_quarter'].dt.to_timestamp()

st.subheader("Select graph settings")

# Calculate metrics for filtering options
industry_margin_df = quarterly_avg_df.groupby('industry')['margin'].mean().reset_index()
top_5_industries = industry_margin_df.nlargest(5, 'margin')['industry'].tolist()
volatility_df = quarterly_avg_df.groupby('industry')['margin'].std().reset_index()
top_5_volatile_industries = volatility_df.nlargest(5, 'margin')['industry'].tolist()

# Display filter option and chart type side by side
col1, col2 = st.columns([3, 1])
with col1:
    # Filter options
    filter_option = st.radio(
        "Filter industries by:",
        ('Select Manually', 'Top 5 by Margin', 'Top 5 by Volatility')
    )

with col2:
    # Chart type selection
    chart_type = st.radio(
        "Choose chart type:",
        ('Line Chart', 'Bar Chart')
    )

# Based on the filter option, set the default industries
if filter_option == 'Top 5 by Margin':
    selected_industries = top_5_industries
elif filter_option == 'Top 5 by Volatility':
    selected_industries = top_5_volatile_industries
else:
    # Limit to maximum 10 selectable industries for "Manual Selection"
    all_industries = quarterly_avg_df['industry'].unique()
    selected_industries = st.multiselect(
        'Select up to 10 industries',
        options=all_industries,
        default=all_industries[:10]  # Pre-select the first 10
    )

    # Display a warning if more than 10 industries are selected
    if len(selected_industries) > 10:
        st.warning("Please select 10 or fewer industries.")
        selected_industries = selected_industries[:10]

# Filter the data based on the selected industries
filtered_df = quarterly_avg_df[quarterly_avg_df['industry'].isin(selected_industries)]

st.write('---')

st.subheader('Quarterly Average Margin by Industry', divider=True)



# Create the Plotly figure based on the chart type
if not filtered_df.empty:
    if chart_type == 'Line Chart':
        fig = px.line(
            filtered_df,
            x='year_quarter',
            y='margin',
            color='industry',
            labels={'year_quarter': 'Quarter', 'margin': 'Average Margin (%)'},
            markers=True,
        )
    else:
        fig = px.bar(
            filtered_df,
            x='year_quarter',
            y='margin',
            color='industry',
            labels={'year_quarter': 'Quarter', 'margin': 'Average Margin (%)'},
        )

    # Customize x-axis ticks to show quarter and year (e.g., Q1 2023)
    fig.update_xaxes(
        tickvals=filtered_df['year_quarter'],
        ticktext=[f'Q{q.quarter} {q.year}' for q in filtered_df['year_quarter']]
    )

    # Show the plot in Streamlit
    st.plotly_chart(fig)





# Display key metrics below the graph
st.subheader("Key Insights")


# Calculate key insights
if not filtered_df.empty:
    # Highest and lowest margin industries
    highest_margin_row = filtered_df.loc[filtered_df['margin'].idxmax()]
    highest_margin_value = highest_margin_row['margin']
    highest_margin_industry = highest_margin_row['industry']

    lowest_margin_row = filtered_df.loc[filtered_df['margin'].idxmin()]
    lowest_margin_value = lowest_margin_row['margin']
    lowest_margin_industry = lowest_margin_row['industry']

    overall_avg_margin = filtered_df['margin'].mean()

    # Calculate industry with the greatest margin increase
    industry_margin_change = filtered_df.groupby('industry')['margin'].agg(lambda x: x.iloc[-1] - x.iloc[0])
    max_growth_industry = industry_margin_change.idxmax()
    max_growth_value = industry_margin_change.max()

    # Industry with largest margin decline
    min_growth_industry = industry_margin_change.idxmin()
    min_growth_value = industry_margin_change.min()

    # Calculate volatility (standard deviation of margins)
    volatility_df = filtered_df.groupby('industry')['margin'].std().reset_index()
    most_volatile_industry = volatility_df.loc[volatility_df['margin'].idxmax()]['industry']
    least_volatile_industry = volatility_df.loc[volatility_df['margin'].idxmin()]['industry']

    st.write("----------------------------------------------------------------------------------")

    # Create metric columns
    col1, col2, col3 = st.columns(3)

    # Highest and Lowest Margins
    with col1:
        st.metric(label="Highest Margin (%)", value=f"{highest_margin_value:.2f}%", delta=f"Industry: {highest_margin_industry}")
    
    with col2:
        st.metric(label="Lowest Margin (%)", value=f"{lowest_margin_value:.2f}%", delta=f"Industry: {lowest_margin_industry}", delta_color="inverse")  # Red arrow for lowest margin
    
    with col3:
        st.metric(label="Overall Average Margin (%)", value=f"{overall_avg_margin:.2f}%")
        

    st.write("----------------------------------------------------------------------------------")
    

    # Additional insights
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.metric(label="Greatest Margin Increase (%)", value=f"{max_growth_value:.2f}%", delta=f"Industry: {max_growth_industry}")
    
    with col5:
        st.metric(label="Greatest Margin Decline (%)", value=f"{min_growth_value:.2f}%", delta=f"Industry: {min_growth_industry}", delta_color="inverse") # Red arrow for lowest margin
    
    with col6:
        st.metric(label="Most Volatile Industry", value=f"{most_volatile_industry}")