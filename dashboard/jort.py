import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sqlalchemy import create_engine

# Streamlit title and description
st.subheader("Risk-Adjusted Returns vs ESG Scores", divider=True)
st.write("""
This chart shows the relationship between ESG scores and Sharpe Ratios for companies, highlighting whether higher ESG scores are associated with better risk-adjusted returns.
         
The **Sharpe Ratio** displayed here is calculated based on daily returns, which are then annualized to provide a theoretical estimate of the annual risk-adjusted return. This approach assumes 252 trading days in a year. 
So, while the underlying data might cover multiple years or different time spans depending on the stock, the resulting Sharpe Ratio is meant to give an **annual perspective** on risk-adjusted returns.
""")

# Create a SQLAlchemy engine to connect to the PostgreSQL database
engine = create_engine("postgresql://team13:team13@esg-stocks-db:5432/esg-stocks-database")

# SQL Query to get closing prices and ESG scores
query = """
SELECT 
    st.ticker_symbol, 
    st.name, 
    CAST(esg.total_score AS numeric) AS total_esg_score,
    ph.date, 
    ph.close
FROM stock AS st
INNER JOIN esg_history AS esg ON st.ticker_symbol = esg.ticker_symbol
INNER JOIN pricing_history AS ph ON ph.ticker_symbol = st.ticker_symbol
"""

# Use pandas to execute the SQL query and load the data into a dataframe
df = pd.read_sql_query(query, engine)

# Convert 'date' to datetime for return calculations
df['date'] = pd.to_datetime(df['date'])

# Ensure 'close' prices are numeric
df['close'] = pd.to_numeric(df['close'], errors='coerce')

# Sort data by ticker symbol and date to ensure proper return calculations
df = df.sort_values(by=['ticker_symbol', 'date'])

# Calculate daily log returns for each company
df['log_return'] = df.groupby('ticker_symbol')['close'].transform(lambda x: np.log(x / x.shift(1)))

# Group by company to calculate mean and standard deviation of daily log returns
company_stats = df.groupby('ticker_symbol').agg({
    'log_return': ['mean', 'std'],  # Mean and standard deviation of log returns
    'total_esg_score': 'mean'       # Average total ESG score for the company
}).reset_index()

# Flatten multi-index columns
company_stats.columns = ['ticker_symbol', 'mean_log_return', 'std_log_return', 'total_esg_score']

# Annualize the mean and standard deviation of log returns
company_stats['annualized_mean_return'] = company_stats['mean_log_return'] * 252
company_stats['annualized_std_return'] = company_stats['std_log_return'] * np.sqrt(252)

# Set a fixed annual risk-free rate of 2%
annual_risk_free_rate = 0.02

# Calculate the annualized Sharpe Ratio for each company
company_stats['sharpe_ratio'] = (company_stats['annualized_mean_return'] - annual_risk_free_rate) / company_stats['annualized_std_return']

# Drop rows with missing or invalid data
company_stats = company_stats.dropna(subset=['sharpe_ratio', 'total_esg_score'])

# Load stock names to map ticker symbols to stock names
query_stock = """
SELECT 
    ticker_symbol, 
    name 
FROM stock
"""
df_stock = pd.read_sql_query(query_stock, engine)
company_stats = company_stats.merge(df_stock, on='ticker_symbol', how='left')

# Filter out specific outlier companies by their ticker symbols, e.g., 'ACAC'
company_stats = company_stats[company_stats['ticker_symbol'] != 'ACAC']

# Create an interactive scatter plot using Plotly with stock names in hover data
fig = px.scatter(
    company_stats,
    x='total_esg_score',
    y='sharpe_ratio',
    hover_data={'ticker_symbol': False, 'name': True},  # Hide ticker, show stock name in hover
    labels={'total_esg_score': 'Total ESG Score', 'sharpe_ratio': 'Sharpe Ratio (Risk-Adjusted Return)', 'name': 'Stock Name'},
    title='Risk-Adjusted Returns (Sharpe Ratio) vs ESG Score (Fixed Risk-Free Rate: 2%)',
    size_max=15  # Maximum bubble size for better visibility
)

# Render the Plotly chart in Streamlit
st.plotly_chart(fig, use_container_width=True)

# Sort the DataFrame by Sharpe Ratio in descending order and select the top 10
top_10_stocks = company_stats.sort_values(by='sharpe_ratio', ascending=False).head(10)

# Add a ranking column from 1 to 10
top_10_stocks = top_10_stocks.reset_index(drop=True)
top_10_stocks.index += 1  # Start index from 1 for ranking

# Rename columns for readability
top_10_stocks_display = top_10_stocks[['name', 'sharpe_ratio', 'total_esg_score', 'annualized_mean_return']]
top_10_stocks_display = top_10_stocks_display.rename(columns={
    'name': 'Stock Name',
    'sharpe_ratio': 'Sharpe Ratio',
    'total_esg_score': 'Total ESG Score',
    'annualized_mean_return': 'Annualized Mean Return'
})

# Format the Annualized Mean Return as a percentage with one decimal and add % symbol
top_10_stocks_display['Annualized Mean Return'] = top_10_stocks_display['Annualized Mean Return'].round(1).astype(str) + '%'

# Display the top 10 stocks in a table format
st.subheader("Top 10 Stocks by Sharpe Ratio")
st.write("Here are the top 10 stocks with the highest risk-adjusted returns (Sharpe Ratio):")
st.table(top_10_stocks_display)

# Explanation of the Sharpe Ratio and Risk-Free Rate
st.write("""
### Understanding Sharpe Ratio:
The **Sharpe Ratio** measures the risk-adjusted return of an investment, helping you understand if the returns are worth the risks taken. It is calculated as the difference between an investment's returns and the risk-free rate, divided by the standard deviation of returns.

- **A Sharpe Ratio greater than 1** is generally considered good, indicating that the investment’s returns are well compensated for the risk.
- **A ratio above 2** is seen as very good, while **above 3** is considered excellent.
- **A ratio below 1** suggests that the returns may not justify the risk, and a **negative ratio** means the returns are lower than the risk-free rate.

### What is the Risk-Free Rate?
The **risk-free rate** represents the return on a risk-free investment, typically government bonds like U.S. Treasury bonds. Here, we use a fixed risk-free rate of 2%, serving as a benchmark to assess other investments.
""")
