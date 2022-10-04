import streamlit as st
import pandas as pd


st.set_page_config(page_title="Strength data visualization", page_icon="☀️", layout="wide")
st.sidebar.markdown("## Strength data visualization")

uploaded_file = st.file_uploader("Choose a file to upload")
if uploaded_file is not None:
    df1=pd.read_csv(uploaded_file)
    st.dataframe(df1)