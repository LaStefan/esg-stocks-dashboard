import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.graph_objects as go

st.subheader("Environment, Social, Governance Scores Analysis (ESG)", divider=True)

# Create a SQLAlchemy engine to connect to the PostgreSQL database
engine = create_engine("postgresql://team13:team13@esg-stocks-db:5432/esg-stocks-database")

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
LIMIT 50
"""

# Use pandas to read the data
df = pd.read_sql_query(query, engine)

# Sort the DataFrame
df_sorted = df.sort_values(by='max_esg_score', ascending=False)
# Determine the maximum ESG score across all stocks
max_esg_score = df_sorted[['max_env_score', 'max_social_score', 'max_governance_score']].max().max()

# Add CSS to reduce the width of the selectbox
st.markdown(
    """
    <style>
    .stSelectbox [data-baseweb="select"] {
        width: 20rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# Let users select a stock
stock_names = df_sorted['name'].unique()
selected_stock = st.selectbox("Select a Stock", stock_names)

# Filter the dataframe for the selected stock
selected_df = df_sorted[df_sorted['name'] == selected_stock]

# Create a bar chart using Plotly
fig = go.Figure()

fig.add_trace(go.Bar(
    x=selected_df['name'],
    y=selected_df['max_env_score'],
    name='Environment',
    marker_color='lightblue'
))

fig.add_trace(go.Bar(
    x=selected_df['name'],
    y=selected_df['max_social_score'],
    name='Social',
    marker_color='lightgreen'
))

fig.add_trace(go.Bar(
    x=selected_df['name'],
    y=selected_df['max_governance_score'],
    name='Governance',
    marker_color='lightpink'
))

# Update layout
fig.update_layout(
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
st.plotly_chart(fig)


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
LIMIT 10
"""

# Use pandas to read the data
industry_esg = pd.read_sql_query(query, engine)

# Sort the DataFrame
industry_esg_sorted = industry_esg.sort_values(by='max_esg_score', ascending=False)
max_esg_per_industry = industry_esg_sorted[['max_env_score', 'max_social_score', 'max_governance_score']].max().max()

# Create a bar chart using Plotly
industry_fig = go.Figure()

industry_fig.add_trace(go.Bar(
    x=industry_esg_sorted['industry'],
    y=industry_esg_sorted['max_env_score'],
    name='Environment',
    marker_color='lightblue'
))

industry_fig.add_trace(go.Bar(
    x=industry_esg_sorted['industry'],
    y=industry_esg_sorted['max_social_score'],
    name='Social',
    marker_color='lightgreen'
))

industry_fig.add_trace(go.Bar(
    x=industry_esg_sorted['industry'],
    y=industry_esg_sorted['max_governance_score'],
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