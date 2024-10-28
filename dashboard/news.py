import requests
import pandas as pd
import streamlit as st

@st.cache_data
def fetch_news_data():
    url = "https://finnhub.io/api/v1/news?category=general&token=cscc8hpr01qgt32f7ju0cscc8hpr01qgt32f7jug"
    response = requests.get(url)
    json_data = response.json()
    df = pd.DataFrame(json_data)
    df['datetime'] = pd.to_datetime(df['datetime'], unit='s')
    return df

def render_news_sidebar():
    if 'news_data' not in st.session_state:
        st.session_state['news_data'] = fetch_news_data()
        
    df = st.session_state['news_data']
    df = df[df['category'].isin(['business', 'top news'])]
    
    st.sidebar.header(":newspaper: Latest Market News")
    
    for index, row in df.iterrows():
        st.sidebar.subheader(row["headline"])
        st.sidebar.markdown(f"Published on: {row['datetime'].strftime('%B %d, %Y %I:%M %p')}")
        st.sidebar.image(row["image"], use_column_width=True)
        st.sidebar.markdown(f"{row['summary']}")
        st.sidebar.markdown(f"[🔗 Read more]({row['url']})")
        st.sidebar.markdown("---")