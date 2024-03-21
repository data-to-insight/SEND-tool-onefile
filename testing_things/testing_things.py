import plotly.express as px
import streamlit as st
import pandas as pd

uploaded_files = st.file_uploader('pls', accept_multiple_files=True)


if uploaded_files:

    loaded_files = {uploaded_file.name: pd.read_csv(uploaded_file) for uploaded_file in uploaded_files}

    #st.write(loaded_files.keys())

    ass_outcomes = loaded_files['Module 3.csv'].groupby(['Assessment Outcome To Issue EHCP'])['Assessment Outcome To Issue EHCP'].count().reset_index(name='count')

    assessment_outcome_plot =  px.pie(ass_outcomes, values='count', names='Assessment Outcome To Issue EHCP') 

    st.plotly_chart(assessment_outcome_plot) 