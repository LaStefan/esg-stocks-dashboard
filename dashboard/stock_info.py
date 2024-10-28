import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import finnhub
import os
import matplotlib.pyplot as plt
import dotenv
import plotly.express as px

def truncate_text(text, max_sentences=3):
    sentences = text.split('. ')
    if len(sentences) <= max_sentences:
        return text
    truncated_sentences = '. '.join(sentences[:max_sentences]) + "."
    return truncated_sentences
dotenv.load_dotenv()
# Streamlit Title

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



# Necessary to be able to import helper functions from dashboard folder
# project_root = os.path.abspath(os.path.join(os.getcwd(), ".."))
# if project_root not in sys.path:
#     sys.path.append(project_root)
# Load .env file from dashboard folder
# dotenv.load_dotenv(os.path.join(project_root, 'dashboard', '.env'))
finnhub_client = finnhub.Client(os.getenv('FINNHUB_API_KEY_RESERVED'))
recommendation_response = finnhub_client.recommendation_trends(selected_ticker_symbol)
# st.write(recommendation_response)
data = recommendation_response[0]
labels = ['Strong Sell', 'Sell', 'Hold', 'Buy', 'Strong Buy']
values = [data['strongSell'], data['sell'], data['hold'], data['buy'], data['strongBuy']]
colors = ['#8B0000', '#FF4500', '#FFD700', '#9ACD32', '#006400'] 
# Create the pie chart
fig = px.pie(
    names=labels,
    values=values,
    color=labels,
    color_discrete_map={
        'Strong Sell': '#8B0000',
        'Sell': '#FF4500',
        'Hold': '#FFD700',
        'Buy': '#9ACD32',
        'Strong Buy': '#006400'
    },
    title=f"Analyst recommendations"
)

# Display the pie chart in the Streamlit app
st.plotly_chart(fig)