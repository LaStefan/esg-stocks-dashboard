import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import numpy as np

# Constants
DB_CONNECTION_STRING = "postgresql://team13:team13@esg-stocks-db:5432/esg-stocks-database"

# Page Title and Description
st.title("ESG Scores and Market Performance Analysis")
st.markdown("""
Welcome to the ESG and Market Performance Dashboard. This tool allows you to analyze and compare companies' **Environmental, Social, and Governance (ESG) scores** against their **market performance metrics**, such as market cap and annual returns. 
Select an industry and specific companies to visualize their performance and ESG scores.
""")

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
engine = create_engine(DB_CONNECTION_STRING)
query = """
SELECT st.name, st.ticker_symbol, esg.total_score, st.industry, st.market_cap AS market_cap, 
       pr.date, pr.close
FROM stock AS st
INNER JOIN esg_history AS esg ON st.ticker_symbol = esg.ticker_symbol
INNER JOIN pricing_history AS pr ON st.ticker_symbol = pr.ticker_symbol
"""
df = pd.read_sql_query(query, engine)

# Data preprocessing
df['total_score'] = pd.to_numeric(df['total_score'], errors='coerce')
df['market_cap'] = pd.to_numeric(df['market_cap'], errors='coerce') * 1e6  # Adjusting to full market cap values
df['close'] = pd.to_numeric(df['close'], errors='coerce')
df['date'] = pd.to_datetime(df['date'])
df = df.dropna(subset=['market_cap', 'close', 'total_score'])  # Drop rows with NaN in key columns
df = calculate_annual_returns(df)  # Calculate annual returns

# Sidebar filters
st.sidebar.header("Filters")
industries = sorted(df['industry'].dropna().unique())
selected_industry = st.sidebar.selectbox("Select an industry", industries)
companies_in_industry = df[df['industry'] == selected_industry]['name'].unique()
selected_companies = st.sidebar.multiselect("Select companies", companies_in_industry, default=companies_in_industry)
df_filtered = df[(df['industry'] == selected_industry) & (df['name'].isin(selected_companies))]

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

    # Summary Statistics Section
    if not df_filtered.empty:
        st.markdown("## 📊 Summary Statistics for Selected Industry")
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
