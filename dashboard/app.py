import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# Set the page configuration
st.set_page_config(page_title="ESG Dashboard", page_icon=":bar_chart:", layout='wide', initial_sidebar_state='expanded')

# Define the pages
pg = st.navigation([
    st.Page("app.py", title="Home", icon="🏡"), 
    st.Page("esg.py", title="ESG Scores", icon="📊")
])

# Streamlit Title
st.title("Sustainable Investing With ESG")

# Run the page navigation
# pg.run()

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
"""

# Use pandas to read the data
df = pd.read_sql_query(query, engine)

# Sort the DataFrame
df_sorted = df.sort_values(by='max_esg_score', ascending=False)

# Display data table
# st.dataframe(df_sorted)

# Create a bar chart using Plotly
fig = go.Figure()

fig.add_trace(go.Bar(
    x=df['name'],
    y=df['max_env_score'],
    name='Environment',
    marker_color='lightblue'
))

fig.add_trace(go.Bar(
    x=df['name'],
    y=df['max_social_score'],
    name='Social',
    marker_color='lightgreen'
))

fig.add_trace(go.Bar(
    x=df['name'],
    y=df['max_governance_score'],
    name='Governance',
    marker_color='lightpink'
))

# Update layout
fig.update_layout(
    barmode='group',
    xaxis_tickangle=-45,
    xaxis_title='Stocks',
    yaxis_title='ESG Scores',
    title='ESG Scores by Category',
    legend_title_text='Categories',
    width=1200,  # Set width
    height=700,  # Set height
    legend=dict(yanchor="top", y=1.15, xanchor="left", x=1.05)
)

# Render the chart in Streamlit
st.plotly_chart(fig)

# Use pandas to read the data
df = pd.read_sql_query(query, engine)
print(df)

df_sorted = df.sort_values(by='max_esg_score', ascending=False)

# Plot the data using a bar chart
plt.figure(figsize=(10, 6))
plt.bar(df_sorted['name'], df_sorted['max_esg_score'], color='skyblue')
plt.xlabel('Stocks')
plt.ylabel('ESG Score')
plt.title('Biggest Total ESG Score per Stock')
plt.xticks(rotation=45)  # Rotate x-ticks if necessary

plt.tight_layout()  # Adjust layout to prevent clipping of tick-labels
plt.show()