import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# Page Title and Description
st.title("ESG Scores and Market Performance Analysis")
st.markdown("""
Welcome to the ESG and Market Performance Dashboard. This tool allows you to analyze and compare companies' **Environmental, Social, and Governance (ESG) scores** against their **market performance metrics**, such as market cap and annual returns. 
Select an industry and specific companies to visualize their performance and ESG scores.
""")

# Create a SQLAlchemy engine to connect to the PostgreSQL database
engine = create_engine("postgresql://team13:team13@esg-stocks-db:5432/esg-stocks-database")

# Function to format large numbers (in billions, millions, thousands)
def format_large_number(num):
    if abs(num) >= 1e9:
        return f'{num / 1e9:.2f}B'
    elif abs(num) >= 1e6:
        return f'{num / 1e6:.2f}M'
    elif abs(num) >= 1e3:
        return f'{num / 1e3:.2f}K'
    return str(num)

# Function to calculate annual total returns
def calculate_annual_returns(df):
    df['year'] = df['date'].dt.year
    df = df.sort_values(by=['ticker_symbol', 'date'])
    annual_returns = df.groupby(['ticker_symbol', 'year']).apply(
        lambda x: (x['close'].iloc[-1] - x['close'].iloc[0]) / x['close'].iloc[0] * 100
    ).reset_index(name='annual_total_return_percentage')
    return df.merge(annual_returns, on=['ticker_symbol', 'year'], how='left')

# Function to create a Plotly scatter plot with custom formatted tick labels
def create_plotly_scatter(df, x_col, y_col, x_label, y_label, title, description):
    st.subheader(title)
    st.markdown(description)
    
    # Create the scatter plot
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color="name",
        title=title,
        labels={x_col: x_label, y_col: y_label},
    )

    # Generate custom tick values and labels for the x-axis
    tick_values = np.linspace(df[x_col].min(), df[x_col].max(), num=6)  # Creates 6 evenly spaced tick values
    tick_labels = [format_large_number(value) for value in tick_values]  # Use the format_large_number to label the ticks

    # Update layout for the figure
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
        title=title,
        legend_title="Companies",
        legend=dict(x=1.05, y=1, bordercolor="Black", borderwidth=1),
        # Set custom tick labels for the x-axis
        xaxis=dict(
            tickvals=tick_values,
            ticktext=tick_labels
        )
    )

    # Customize marker size and opacity for clarity
    fig.update_traces(marker=dict(size=8, opacity=0.7))
    
    # Display the figure
    st.plotly_chart(fig)

# Helper function to format and display metric information
def display_metric(label, value, col):
    with col:
        st.metric(label=label, value=value)

# Helper function to display details of a company metric
def display_company_info(label, company, metric_label, metric_value, col):
    with col:
        st.markdown(f"#### {label}")
        st.write(f"**Company:** {company}")
        st.write(f"**{metric_label}:** {metric_value}")

# Database connection and data loading
query = """
SELECT st.name, st.ticker_symbol, esg.total_score, st.industry, st.market_cap AS market_cap, 
       pr.date, pr.close
FROM stock AS st
INNER JOIN esg_history AS esg ON st.ticker_symbol = esg.ticker_symbol
INNER JOIN pricing_history AS pr ON st.ticker_symbol = pr.ticker_symbol
"""
df_market = pd.read_sql_query(query, engine)

# Data preprocessing
df_market['total_score'] = pd.to_numeric(df_market['total_score'], errors='coerce')
df_market['market_cap'] = pd.to_numeric(df_market['market_cap'], errors='coerce') * 1e6  # Adjusting to full market cap values
df_market['close'] = pd.to_numeric(df_market['close'], errors='coerce')
df_market['date'] = pd.to_datetime(df_market['date'])
df_market = df_market.dropna(subset=['market_cap', 'close', 'total_score'])  # Drop rows with NaN in key columns
df_market = calculate_annual_returns(df_market)  # Calculate annual returns

# Sidebar filters
st.sidebar.header("Filters")
industries = sorted(df_market['industry'].dropna().unique())
selected_industry = st.sidebar.selectbox("Select an industry", industries)
companies_in_industry = df_market[df_market['industry'] == selected_industry]['name'].unique()
selected_companies = st.sidebar.multiselect("Select companies", companies_in_industry, default=companies_in_industry)
df_filtered = df_market[(df_market['industry'] == selected_industry) & (df_market['name'].isin(selected_companies))]

   # Summary Statistics Section
if not df_filtered.empty:
        st.markdown(f"## 📊 Summary Statistics for {selected_industry}")
        st.markdown("""
        Below are key statistics for the selected companies in the chosen industry, providing insights into their average ESG scores, total market cap, and notable highs and lows.
        """)

        # Ensuring unique companies for correct market cap aggregation
        df_unique = df_filtered.groupby('name').agg({
            'market_cap': 'first',  # Take the first market cap value for each company
            'total_score': 'first'   # Take the first ESG score for each company
        }).reset_index()

        # Calculating summary statistics
        num_companies = df_unique['name'].nunique()
        total_market_cap = format_large_number(df_unique['market_cap'].sum())
        avg_market_cap = format_large_number(df_unique['market_cap'].mean())
        avg_esg_score = df_unique['total_score'].mean()

        # Getting the highest and lowest metrics
        max_market_cap = df_unique.loc[df_unique['market_cap'].idxmax()]
        min_market_cap = df_unique.loc[df_unique['market_cap'].idxmin()]
        max_esg = df_unique.loc[df_unique['total_score'].idxmax()]
        min_esg = df_unique.loc[df_unique['total_score'].idxmin()]

        # First Row - High-level Summary Metrics
        st.markdown("### Key Industry Metrics")
        col1, col2, col3 = st.columns(3)
        display_metric("Number of Companies", num_companies, col1)
        display_metric("Total Market Cap", total_market_cap, col2)
        display_metric("Average ESG Score", f"{avg_esg_score:.2f}", col3)

        # Market Cap Insights
        st.markdown("---")
        st.markdown("### Market Cap Insights")
        col4, col5 = st.columns(2)
        display_company_info("🏆 Highest Market Cap", max_market_cap['name'], "Market Cap", format_large_number(max_market_cap['market_cap']), col4)
        display_company_info("📉 Lowest Market Cap", min_market_cap['name'], "Market Cap", format_large_number(min_market_cap['market_cap']), col5)

        # ESG Score Insights
        st.markdown("---")
        st.markdown("### ESG Score Insights")
        col6, col7 = st.columns(2)
        display_company_info("🌍 Highest ESG Score", max_esg['name'], "ESG Score", max_esg['total_score'], col6)
        display_company_info("⚠️ Lowest ESG Score", min_esg['name'], "ESG Score", min_esg['total_score'], col7)
        st.divider()


# Check if df_filtered is empty after filtering
if df_filtered.empty:
    st.warning("No companies found in the selected industry or market cap range. Please select other filters.")
else:
    # Market Cap Slider Configuration
    min_market_cap, max_market_cap = df_filtered['market_cap'].min(), df_filtered['market_cap'].max()
    if min_market_cap == max_market_cap:
        st.info(f"There is only **one company** in the selected industry with a market cap of **{format_large_number(min_market_cap)}**.")
    else:
        market_cap_units = 1e3 if min_market_cap < 1e6 else 1e6
        slider_label = 'Select Market Cap Range (Thousands)' if market_cap_units == 1e3 else 'Select Market Cap Range (Millions)'
        min_value, max_value = min_market_cap / market_cap_units, max_market_cap / market_cap_units
        market_cap_min, market_cap_max = st.slider(slider_label, min_value=float(min_value), max_value=float(max_value),
                                                   value=(float(min_value), float(max_value)))
        df_filtered = df_filtered[(df_filtered['market_cap'] >= market_cap_min * market_cap_units) &
                                  (df_filtered['market_cap'] <= market_cap_max * market_cap_units)]
        if df_filtered.empty:
            st.warning("No companies found in the selected market cap range.")

    # ESG vs Market Cap Plotly Scatter Plot
    if not df_filtered.empty:
        create_plotly_scatter(
            df_filtered,
            x_col="market_cap",
            y_col="total_score",
            x_label="Market Cap",
            y_label="Total ESG Score",
            title=f"ESG Score vs Market Cap for {selected_industry} Industry",
            description="This scatter plot visualizes the relationship between a company's market capitalization and its ESG score. Higher ESG scores may indicate better adherence to environmental, social, and governance standards, while larger market caps often indicate more established companies."
        )

    # Annual Total Return vs ESG Score Plotly Scatter Plot with Explanation
    if not df_filtered.empty:
        create_plotly_scatter(
            df_filtered,
            x_col="annual_total_return_percentage",
            y_col="total_score",
            x_label="Annual Total Return (%)",
            y_label="Total ESG Score",
            title=f"Annual Total Return vs ESG Score for {selected_industry} Industry",
            description="""
                This scatter plot illustrates the relationship between a company's **annual total return** and its **ESG score**. 
                This allows you to explore if there is any correlation between a company's financial performance and its ESG practices.
                
                #### How is Annual Total Return Calculated?
                The **Annual Total Return** is calculated as the percentage change in a company's stock price from the start to the end of each year. 
                This is determined by comparing the closing price on the first trading day of the year with the closing price on the last trading day.
            """
        )


st.subheader("Environment, Social, Governance Scores Analysis (ESG)", divider=True)
# Join all 3 tables and select certain columns
query = """
SELECT 
st.ticker_symbol, 
st.name, 
CAST(MAX(esg.total_score) AS numeric) AS max_esg_score,
CAST(MAX(esg.environment_score) AS numeric) AS max_env_score,
CAST(MAX(esg.social_score) AS numeric) AS max_social_score,
CAST(MAX(esg.governance_score) AS numeric) AS max_governance_score
FROM stock AS st
INNER JOIN esg_history AS esg ON st.ticker_symbol = esg.ticker_symbol
INNER JOIN pricing_history AS ph ON ph.ticker_symbol = st.ticker_symbol
GROUP BY st.ticker_symbol, st.name
"""

# Use pandas to read the data
df_esg = pd.read_sql_query(query, engine)

# Sort the DataFrame
df_sorted = df_esg.sort_values(by='max_esg_score', ascending=False)
# Determine the maximum ESG score across all stocks
max_esg_score = df_sorted[['max_env_score', 'max_social_score', 'max_governance_score']].max().max()


# Let users select a stock
stock_names = df_sorted['name'].unique()
selected_stock = st.selectbox("Select a Stock", stock_names)

# Filter the dataframe for the selected stock
selected_df = df_sorted[df_sorted['name'] == selected_stock]

# Create a bar chart using Plotly
fig_esg = go.Figure()

fig_esg.add_trace(go.Bar(
    x=selected_df['name'],
    y=selected_df['max_env_score'],
    name='Environment',
    marker_color='lightblue'
))

fig_esg.add_trace(go.Bar(
    x=selected_df['name'],
    y=selected_df['max_social_score'],
    name='Social',
    marker_color='lightgreen'
))

fig_esg.add_trace(go.Bar(
    x=selected_df['name'],
    y=selected_df['max_governance_score'],
    name='Governance',
    marker_color='lightpink'
))

# Update layout
fig_esg.update_layout(
    barmode='group',
    xaxis_title='Stocks',
    yaxis_title='ESG Scores',
    yaxis=dict(
        title='ESG Scores',
        range=[0, max_esg_score + 100]  # Fixed y-axis range
    ),
    title=f'ESG Scores for {selected_stock}',
    legend_title_text='Categories',
    width=800,  # Adjust width
    height=600,  # Adjust height
    legend=dict(yanchor="top", y=1.15, xanchor="left", x=1.05)
)

# Render the chart in Streamlit
st.plotly_chart(fig_esg)


# Join all 3 tables and select certain columns
query = """
SELECT 
st.industry, 
CAST(MAX(esg.total_score) AS numeric) AS max_esg_score,
CAST(MAX(esg.environment_score) AS numeric) AS max_env_score,
CAST(MAX(esg.social_score) AS numeric) AS max_social_score,
CAST(MAX(esg.governance_score) AS numeric) AS max_governance_score
FROM stock AS st
INNER JOIN esg_history AS esg ON st.ticker_symbol = esg.ticker_symbol
GROUP BY st.industry
"""

# Use pandas to read the data
industry_esg = pd.read_sql_query(query, engine)

# Sort the DataFrame
industry_esg_sorted = industry_esg.sort_values(by='max_esg_score', ascending=False)
max_esg_per_industry = industry_esg_sorted[['max_env_score', 'max_social_score', 'max_governance_score']].max().max()


# Select top 7 industries by default
default_selected_industries = industry_esg_sorted['industry'].head(10).tolist()

# Create checkboxes for industry selection
selected_industries = st.multiselect(
    'Select Industries to Display:',
    industry_esg_sorted['industry'],
    default=default_selected_industries
)

# Filter the sorted dataframe based on selected industries
filtered_esg_sorted = industry_esg_sorted[industry_esg_sorted['industry'].isin(selected_industries)]

# Create a bar chart using Plotly
industry_fig = go.Figure()

industry_fig.add_trace(go.Bar(
    x=filtered_esg_sorted['industry'],
    y=filtered_esg_sorted['max_env_score'],
    name='Environment',
    marker_color='lightblue'
))

industry_fig.add_trace(go.Bar(
    x=filtered_esg_sorted['industry'],
    y=filtered_esg_sorted['max_social_score'],
    name='Social',
    marker_color='lightgreen'
))

industry_fig.add_trace(go.Bar(
    x=filtered_esg_sorted['industry'],
    y=filtered_esg_sorted['max_governance_score'],
    name='Governance',
    marker_color='lightpink'
))

# Update layout
industry_fig.update_layout(
    barmode='group',
    xaxis_title='Industry',
    yaxis_title='ESG Scores',
    yaxis=dict(
        title='ESG Scores',
        range=[0, max_esg_per_industry + 100]  # Fixed y-axis range
    ),
    title='ESG Scores per Industry',
    legend_title_text='Categories',
    width=1200,  # Adjust width
    height=800,  # Adjust height
    legend=dict(yanchor="top", y=1.15, xanchor="left", x=1.05)
)

# Render the chart in Streamlit
st.plotly_chart(industry_fig)

# Streamlit title and description
st.subheader("Risk-Adjusted Returns vs ESG Scores", divider=True)
st.write("""
This chart shows the relationship between ESG scores and Sharpe Ratios for companies, highlighting whether higher ESG scores are associated with better risk-adjusted returns.
         
The **Sharpe Ratio** displayed here is calculated based on daily returns, which are then annualized to provide a theoretical estimate of the annual risk-adjusted return. This approach assumes 252 trading days in a year. 
So, while the underlying data might cover multiple years or different time spans depending on the stock, the resulting Sharpe Ratio is meant to give an **annual perspective** on risk-adjusted returns.
""")

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
df_risk = pd.read_sql_query(query, engine)

# Convert 'date' to datetime for return calculations
df_risk['date'] = pd.to_datetime(df_risk['date'])

# Ensure 'close' prices are numeric
df_risk['close'] = pd.to_numeric(df_risk['close'], errors='coerce')

# Sort data by ticker symbol and date to ensure proper return calculations
df_risk = df_risk.sort_values(by=['ticker_symbol', 'date'])

# Calculate daily log returns for each company
df_risk['log_return'] = df_risk.groupby('ticker_symbol')['close'].transform(lambda x: np.log(x / x.shift(1)))

# Group by company to calculate mean and standard deviation of daily log returns
company_stats = df_risk.groupby('ticker_symbol').agg({
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
