import streamlit as st

# Streamlit Title
st.title("Sustainable Investing With ESG")
st.subheader("""
         ESG stands for environmental, social, and governance. An ESG rating is a measure of a company’s performance along the criteria explained below.
         """)

st.write('----------------------------------------------------------------------------------')


col1, col2, col3 = st.columns(3, gap='medium', vertical_alignment='top')
with col1:
    st.subheader("Environment (E)")
    st.write("""
             Environmental criteria focuses on a company’s environmental stewardship. 
             The environmental segment of ESG examines how a company uses natural resources and impacts the environment. 
             Environmental factors are primarily concerned with climate change issues.""")
 
    st.image("assets/environment.jpg", use_column_width='auto')

with col2:
    st.subheader("Social (S)")
    st.write("""
             Social criteria focuses on a company's social responsibility. 
             The social segment of ESG examines how a company manages its relationships with its workforce and other stakeholders in its community.
             Social factors are primarily concerned with social consequences of business decisions.""")
    
    st.image("assets/society.jpg", use_column_width='auto')

with col3:
    st.subheader("Governance (G)")
    st.write("""
             Governance criteria focuses on the integrity of a company’s governance structure. 
             The governance segment of ESG examines whether a company’s leadership is operating within an ethical and responsible framework. 
             Governance factors are primarily concerned with leadership accountability.
             """)
    
    st.image("assets/governance.jpg", use_column_width='auto')
