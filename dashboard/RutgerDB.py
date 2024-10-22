import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# Create a SQLAlchemy engine to connect to the PostgreSQL database
engine = create_engine("postgresql://team13:team13@esg-stocks-db:5432/esg-stocks-database")

# Set up Streamlit title and description
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

st.subheader("Select industries to display")

# Create a multi-select dropdown for industry selection
industries = quarterly_avg_df['industry'].unique()
selected_industries = st.multiselect(
    '----------------------------------------------------------------------------------',
    options=industries,
    default=industries  # Pre-select all industries by default
)

st.write('----------------------------------------------------------------------------------')

# Filter the data based on the selected industries
if selected_industries:
    filtered_df = quarterly_avg_df[quarterly_avg_df['industry'].isin(selected_industries)]
else:
    # Show an empty DataFrame if no industries are selected
    filtered_df = pd.DataFrame(columns=quarterly_avg_df.columns)

# Create the Plotly figure
if not filtered_df.empty:
    fig = px.line(
        filtered_df,
        x='year_quarter',
        y='margin',
        color='industry',
        title='Quarterly Average Margin by Industry',
        labels={'year_quarter': 'Quarter', 'margin': 'Average Margin (%)'},
        markers=True,
    )

    # Customize x-axis ticks
    fig.update_xaxes(
        tickvals=filtered_df['year_quarter'],
        ticktext=[f'Q{q.quarter} {q.year}' for q in filtered_df['year_quarter']]
    )
    
    # Show the plot in Streamlit
    st.plotly_chart(fig)
else:
    st.write("No industries selected. Please select at least one industry to view the graph.")

# Run this in your terminal to start the Streamlit app
# streamlit run app.py



















