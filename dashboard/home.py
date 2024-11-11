import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Streamlit Title
st.title("Sustainable Investing With ESG")

engine = create_engine("postgresql://team13:team13@esg-stocks-db:5432/esg-stocks-database")

# Join all 3 tables and select certain columns
query = """
SELECT 
CAST(esg.total_score AS numeric) AS max_esg_score,
CAST(esg.environment_score AS numeric) AS max_env_score,
CAST(esg.social_score AS numeric) AS max_social_score,
CAST(esg.governance_score AS numeric) AS max_governance_score
FROM esg_history AS esg
GROUP BY max_esg_score, max_env_score, max_social_score, max_governance_score
"""

# Use pandas to read the data
df = pd.read_sql_query(query, engine)

# Sort the DataFrame
df_sorted = df.sort_values(by='max_esg_score', ascending=False)
# Determine the maximum ESG score across all stocks
avg_env_score = df_sorted['max_env_score'].mean()
avg_soc_score = df_sorted['max_social_score'].mean()
avg_gov_score = df_sorted['max_governance_score'].mean()
env_score = df_sorted['max_env_score'].max()
soc_score = df_sorted['max_social_score'].max()
gov_score = df_sorted['max_governance_score'].max()

st.subheader("""
         _ESG_ stands for _environmental_, _social_, and _governance_. An ESG rating is a measure of a company’s performance along the criteria explained below.
         """)

st.write('----------------------------------------------------------------------------------')


col1, col2, col3 = st.columns(3, gap='medium', vertical_alignment='top')
with col1:
    st.subheader(":earth_africa: Environment (E)")
    st.markdown(f"""
        <div style="background: linear-gradient(to right, #e3ffe7, #d9e7ff);padding:10px;border-radius:8px;">
        <h5>Average Score out of the Highest Score</h5>
        <h3 style="text-align:center;color:#2e7d32;">{round(avg_env_score, 2)} / {round(env_score, 2)}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("""
             This aspect emphasizes a company's commitment to environmental stewardship, assessing how it utilizes natural resources and its impact on the environment. It primarily addresses issues related to climate change.""")
 
    st.image("assets/environment.jpg", use_container_width='auto')

with col2:
    st.subheader(":people_holding_hands: Social (S)")
    st.markdown(f"""
        <div style="background: linear-gradient(to right, #e3ffe7, #d9e7ff);padding:10px;border-radius:8px;">
        <h5>Average Score out of the Highest Score</h5>
        <h3 style="text-align:center;color:#2e7d32;">{round(avg_soc_score, 2)} / {round(soc_score, 2)}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("""
            This criteria centers on a company’s social responsibility, evaluating how it manages relationships with its employees and the community. It focuses on the social implications of business activities.""")
    
    st.image("assets/society.jpg", use_container_width='auto')

with col3:
    st.subheader(":classical_building: Governance (G)")    
    st.markdown(f"""
        <div style="background: linear-gradient(to right, #e3ffe7, #d9e7ff);padding:10px;border-radius:8px;">
        <h5>Average Score out of the Highest Score</h5>
        <h3 style="text-align:center;color:#2e7d32;">{round(avg_gov_score, 2)} / {round(gov_score, 2)}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("""
             Governance deals with the integrity of a company’s management structure, examining if leadership operates ethically and responsibly. It is mainly concerned with accountability within leadership.
             """)

    st.image("assets/governance.jpg", use_container_width='auto')



st.write('----------------------------------------------------------------------------------')

# Add sustainable investing section with colorful background
st.markdown("""
    <div style="background: linear-gradient(to right, #e3ffe7, #d9e7ff); padding: 15px; border-radius: 10px; margin-top: 20px;">
        <h4 style="color:#2c3e50;">💡 Sustainable Investing</h4>
        <p style="color:#34495e;">
            Sustainable investing, also known as responsible investing or ESG investing, involves selecting investments based on environmental, social, and governance criteria alongside traditional financial analysis. The aim is to achieve positive financial returns while encouraging companies to act responsibly and champion sustainable development.
        </p>
    </div>
""", unsafe_allow_html=True)