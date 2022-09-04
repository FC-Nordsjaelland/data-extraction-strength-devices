import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
st.set_page_config(layout="wide")


##### HEADER #####

st.title("Strength devices extraction app")
st.markdown("""
**_
""")
st.write("------------------------------------------")


sidebar_options = (
    "Upload the csv", 
    "Visualization",
    "Data extraction")

##### PAGE CODE ##########

hide_table_row_index = """
        <style>
        tbody th {display:none;}
        .blank {display:none;}
        .row_heading.level0 {display:none;}
        </style>
        """
# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)

# def start_page():
    
