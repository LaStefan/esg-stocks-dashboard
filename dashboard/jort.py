import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sqlalchemy import create_engine

# Streamlit title and description
st.subheader("Risk-Adjusted Returns vs ESG Scores", divider=True)
st.write("This chart shows the relationship between ESG scores and Sharpe Ratios for companies, highlighting whether higher ESG scores are associated with better risk-adjusted returns.")

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

# Calculate daily returns for each company
df['return'] = df.groupby('ticker_symbol')['close'].pct_change()

# Group by company to calculate the Sharpe Ratio
company_stats = df.groupby('ticker_symbol').agg({
    'return': ['mean', 'std'],  # Mean and standard deviation of returns
    'total_esg_score': 'mean'  # Average total ESG score for the company
}).reset_index()

# Flatten multi-index columns
company_stats.columns = ['ticker_symbol', 'mean_return', 'std_return', 'total_esg_score']

# Convert returns and standard deviations to numeric types (if necessary)
company_stats['mean_return'] = pd.to_numeric(company_stats['mean_return'], errors='coerce')
company_stats['std_return'] = pd.to_numeric(company_stats['std_return'], errors='coerce')

# Add a slider for the user to adjust the risk-free rate
risk_free_rate = st.slider(
    'Select Risk-Free Rate (%)',
    min_value=0.0,
    max_value=10.0,
    value=2.0,
    step=0.1
) / 100  # Convert to a decimal

# Calculate the Sharpe Ratio for each company based on the selected risk-free rate
company_stats['sharpe_ratio'] = (company_stats['mean_return'] - risk_free_rate) / company_stats['std_return']

# Drop rows with missing or invalid data
company_stats = company_stats.dropna(subset=['sharpe_ratio', 'total_esg_score'])

company_stats = company_stats[company_stats['ticker_symbol'] != 'ACAC']

# Create an interactive scatter plot using Plotly
fig = px.scatter(
    company_stats,
    x='total_esg_score',
    y='sharpe_ratio',
    hover_data=['ticker_symbol'],
    labels={'total_esg_score': 'Total ESG Score', 'sharpe_ratio': 'Sharpe Ratio (Risk-Adjusted Return)'},
    title=f'Risk-Adjusted Returns (Sharpe Ratio) vs ESG Score (Risk-Free Rate: {risk_free_rate * 100:.1f}%)',
    size_max=15,  # Maximum bubble size for better visibility
)

# Render the Plotly chart in Streamlit
st.plotly_chart(fig, use_container_width=True)

# Explanation of the Sharpe Ratio and Risk-Free Rate
st.write("""
### Understanding the Sharpe Ratio:
The **Sharpe Ratio** measures the risk-adjusted return of an investment, helping you understand if the returns are worth the risks taken. It is calculated as the difference between an investment's returns and the risk-free rate, divided by the standard deviation of returns.

- **A Sharpe Ratio greater than 1** is generally considered good, indicating that the investment’s returns are well compensated for the risk.
- **A ratio above 2** is seen as very good, while **above 3** is considered excellent.
- **A ratio below 1** suggests that the returns may not justify the risk, and a **negative ratio** means the returns are lower than the risk-free rate.

### What is the Risk-Free Rate?
The **risk-free rate** represents the return on a risk-free investment, typically government bonds like U.S. Treasury bonds. It is used as a benchmark to measure other investments. In this chart, you can adjust the risk-free rate using the slider, allowing you to see how changes affect the Sharpe Ratios of different companies. A higher risk-free rate makes it harder for investments to show a high Sharpe Ratio, as they need to outperform a higher baseline.
""")
