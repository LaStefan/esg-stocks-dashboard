import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Streamlit Title
st.title("Sustainable Investing With ESG")

engine = create_engine("postgresql://team13:team13@esg-stocks-db:5432/esg-stocks-database")

# Join all 3 tables and select certain columns
query = """
SELECT 
st.ticker_symbol, 
st.name, 
MAX(CAST(esg.total_score AS numeric)) AS max_esg_score,
MAX(CAST(esg.environment_score AS numeric)) AS max_env_score,
MAX(CAST(esg.social_score AS numeric)) AS max_social_score,
MAX(CAST(esg.governance_score AS numeric)) AS max_governance_score
FROM stock AS st
INNER JOIN esg_history AS esg ON st.ticker_symbol = esg.ticker_symbol
GROUP BY st.ticker_symbol, st.name
"""

# Use pandas to read the data
df = pd.read_sql_query(query, engine)

# Sort the DataFrame
df_sorted = df.sort_values(by='max_esg_score', ascending=False)
# Determine the maximum ESG score across all stocks
avg_env_score = df_sorted['max_env_score'].mean()
avg_soc_score = df_sorted['max_social_score'].mean()
avg_gov_score = df_sorted['max_governance_score'].mean()

st.subheader("""
         _ESG_ stands for _environmental_, _social_, and _governance_. An ESG rating is a measure of a company’s performance along the criteria explained below.
         """)

st.write('----------------------------------------------------------------------------------')


col1, col2, col3 = st.columns(3, gap='medium', vertical_alignment='top')
with col1:
    st.subheader(":earth_africa: Environment (E)")
    st.write("""
             This aspect emphasizes a company's commitment to environmental stewardship, assessing how it utilizes natural resources and its impact on the environment. It primarily addresses issues related to climate change.""")
 
    st.image("assets/environment.jpg", use_column_width='auto')
    st.subheader(f"Average Score: {round(avg_env_score, 4)}")

with col2:
    st.subheader(":people_holding_hands: Social (S)")
    st.write("""
            This criteria centers on a company’s social responsibility, evaluating how it manages relationships with its employees and the community. It focuses on the social implications of business activities.""")
    
    st.image("assets/society.jpg", use_column_width='auto')
    st.subheader(f"Average Score: {round(avg_soc_score, 4)}")

with col3:
    st.subheader(":classical_building: Governance (G)")
    st.write("""
             Governance deals with the integrity of a company’s management structure, examining if leadership operates ethically and responsibly. It is mainly concerned with accountability within leadership.
             """)
    
    st.image("assets/governance.jpg", use_column_width='auto')

    st.subheader(f"Average Score: {round(avg_gov_score, 4)}")


st.write('----------------------------------------------------------------------------------')

st.subheader("""
         Here goes the text about Sustainable Investing
         """)
