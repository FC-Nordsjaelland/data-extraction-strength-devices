#%%
import pandas as pd
import io
import matplotlib.pyplot as plt
import datetime
from datetime import time
import streamlit as st
from st_aggrid import AgGrid
import numpy as np
import seaborn as sns
import math

#%%
st.set_page_config(page_title="Trial tests comparison", layout="wide")
st.sidebar.markdown("## Trial tests comparison")

st.title("Trial tests comparison")


def percentage_difference(col1, col2):
    return abs(col1 - col2) / ((col1 + col2) / 2) * 100


def convert_df(df):
    return df.to_csv(index=False, date_format="%m.%d.%Y").encode("utf-8")


def flatten_xlsx(path):
    data = pd.read_excel(path, header=None)
    data.reset_index()
    metadata = data[[0, 1]]

    test = metadata[metadata[0] == "Exercise"][1].values[0]
    if test == "Isometric":
        test = "Hamstring"

    name = metadata[metadata[0] == "Name"][1].values[0]

    if "_" in name:
        name = " ".join(name.split("_"))

    tests = data[[1, 2]][7::]
    tests.columns = ["Left", "Right"]
    tests = tests.astype("float")

    results_left = {}
    for i, j in enumerate(tests["Left"]):
        results_left[i] = j

    results_right = {}
    for i, j in enumerate(tests["Right"]):
        results_right[i] = j

    x = []
    for leg in ["Left", "Right"]:
        for i in range(len(tests)):
            if leg == "Left":
                x.append([name, test, leg, i + 1, results_left[i]])
            if leg == "Right":
                x.append([name, test, leg, i + 1, results_right[i]])
    return x


#%%
def preprocess(uploaded_files):
    players_data = []
    for file in uploaded_files:
        one_player = flatten_xlsx(file)
        players_data.append(one_player)

    flattened_data = [item for sublist in players_data for item in sublist]

    df = pd.DataFrame(
        flattened_data, columns=["Name", "Test", "Leg", "Trial no.", "Strength"]
    )

    return df


#%%
# uploaded_files = [
#     "/Users/franekl/Desktop/Adamo_Nagalo_060323-10_50_49 (1).xlsx",
#     "/Users/franekl/Desktop/Andreas_Hansen_060323-10_35_33.xlsx",
#     "/Users/franekl/Desktop/Villads_Nielsen_200223-15_43_33.xlsx",
# ]
# df = preprocess(uploaded_files)

# %%
uploaded_files = st.file_uploader(
    "Upload xlsx files below", type="xlsx", accept_multiple_files=True
)

if uploaded_files is not None:
    try:
        df = preprocess(uploaded_files=uploaded_files)
        AgGrid(df, fit_columns_on_grid_load=True)

        csv = convert_df(df)
        st.download_button(
            "Press to Download",
            csv,
            "output.csv",
            "text/csv",
            key="download-csv",
        )

        st.write("")
        st.write("")

        # with st.form(key="my_form2"):
        #     test = st.radio(
        #         "Choose a test to compare", ("Nordic", "Hamstring", "Isometric")
        #     )

        #     if test == "Nordic":
        #         df = df[df["Test"] == "Nordic"]
        #         title = "Nordic"

        #     elif test == "Hamstring":
        #         df = df[df["Test"] == "Hamstring"]
        #         title = "Hamstring"

        #     elif test == "Isometric":
        #         df = df[df["Test"] == "Isometric"]
        #         title = "Isometric"

        #     st.write(df)
        #     submitted = st.form_submit_button(label="Visualize")

        #     if submitted:
        #         st.write(df)
        #         df = df.dropna(subset=["Strength"])
        #         sns.set_style("whitegrid")

        #         # Create a nested bar plot for the trial number
        #         trial_plot = sns.catplot(
        #             x="Name",
        #             y="Strength",
        #             hue="Trial no.",
        #             col="Leg",
        #             col_order=["Left"],
        #             data=df,
        #             kind="bar",
        #             alpha=0.9,
        #             edgecolor="black",
        #             height=6,
        #             aspect=1.2,
        #         )
        #         plt.xlabel("")
        #         plt.title("Left leg")
        #         st.pyplot(fig=plt)

        #         trial_plot = sns.catplot(
        #             x="Name",
        #             y="Strength",
        #             hue="Trial no.",
        #             col="Leg",
        #             col_order=["Right"],
        #             data=df,
        #             kind="bar",
        #             alpha=0.9,
        #             edgecolor="black",
        #             height=6,
        #             aspect=1.2,
        #         )
        #         plt.xlabel("")
        #         plt.title("Right leg")
        #         st.pyplot(fig=plt)

    except:
        pass

    # %%
