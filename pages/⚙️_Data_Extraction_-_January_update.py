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

#%%
st.set_page_config(page_title="Strength data summary", layout="wide")
st.sidebar.markdown("## Strength data summary")

st.title("Strength data summary (01/23 update)")


def percentage_difference(col1, col2):
    return abs(col1 - col2) / ((col1 + col2) / 2) * 100


def flatten_xlsx(path):
    data = pd.read_excel(path, header=None)
    try:
        data.reset_index()
        metadata = data[[0, 1]]
        date = metadata[metadata[0] == "Date"][1][0].split()[0]
        dateid = metadata[metadata[0] == "Date"][1][0]
        year = metadata[metadata[0] == "Date"][1][0].split()[0].split(".")[-1]
        test = metadata[metadata[0] == "Exercise"][1].values[0]
        if test == "Isometric":
            test = "Hamstring"
        measure = "Newtons"
        team = metadata[metadata[0] == "Team"][1].values[0]
        name = metadata[metadata[0] == "Name"][1].values[0]

        right_col_data = data[[4, 5, 6, 7, 8]]

        nrs = right_col_data[right_col_data[7] == "NRS (Pain during Test)"][8].values[0]
        season_split = (
            right_col_data[right_col_data[7] == "Season Period"][8].values[0].split()
        )
        term = season_split[1]
        season_period = season_split[0]
        test_type = right_col_data[right_col_data[7] == "Test Type"][8].values[0]

        dob = right_col_data[right_col_data[4] == "Date of birth (dd/mm/yyyy)"][
            5
        ].values[0]
        gender = right_col_data[right_col_data[4] == "Gender"][5].values[0]
        height = right_col_data[right_col_data[4] == "Height"][5].values[0]
        weight = right_col_data[right_col_data[4] == "Weight"][5].values[0]
        position = right_col_data[right_col_data[4] == "Position"][5].values[0]
        id = right_col_data[right_col_data[4] == "ID"][5].values[0]

        try:
            lever_knee = right_col_data[right_col_data[4] == "Hip-Knee Lever"][
                5
            ].values[0]
            lever_groin = right_col_data[right_col_data[4] == "Hip-Ankle Lever"][
                5
            ].values[0]
        except:
            lever_knee = np.nan
            lever_groin = np.nan

        try:
            tests = data[[1, 2]][7::]
            tests.columns = ["Left", "Right"]
            tests = tests.astype("float")
            left_max = tests["Left"].max()
            right_max = tests["Right"].max()
        except:
            left_max = np.nan
            right_max = np.nan

        x = [
            [
                name,
                id,
                gender,
                dob,
                np.nan,
                height,
                weight,
                lever_knee,
                lever_groin,
                team,
                position,
                date,
                year,
                term,
                season_period,
                test_type,
                test,
                "Right",
                measure,
                right_max,
                nrs,
                id
                + test
                + (id + test + "".join(dateid.split(".")))
                .replace(" ", "")
                .replace(":", ""),
            ],
            [
                name,
                id,
                gender,
                dob,
                np.nan,
                height,
                weight,
                lever_knee,
                lever_groin,
                team,
                position,
                date,
                year,
                term,
                season_period,
                test_type,
                test,
                "Left",
                measure,
                left_max,
                nrs,
                id
                + test
                + (id + test + "".join(dateid.split(".")))
                .replace(" ", "")
                .replace(":", ""),
            ],
        ]
    except:
        x = [
            [
                name,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                team,
                np.nan,
                date,
                year,
                term,
                season_period,
                test_type,
                test,
                "Right",
                measure,
                np.nan,
                nrs,
                np.nan,
            ],
            [
                name,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                team,
                np.nan,
                date,
                year,
                term,
                season_period,
                test_type,
                test,
                "Left",
                measure,
                np.nan,
                nrs,
                np.nan,
            ],
        ]

    return x


def preprocess(uploaded_files):

    # file_names = glob.glob(os.path.join(dir_path, "*.xlsx"))

    players_data = []
    for file in uploaded_files:
        one_player = flatten_xlsx(file)
        one_player_right = one_player[0]
        one_player_left = one_player[1]
        players_data.append(one_player_right)
        players_data.append(one_player_left)

    df = pd.DataFrame(
        players_data,
        columns=[
            "Name",
            "id",
            "Gender",
            "DoB",
            "age",
            "height",
            "body_mass",
            "lever_knee",
            "lever_groin",
            "team",
            "position",
            "date",
            "year",
            "term",
            "season_period",
            "type",
            "test",
            "leg",
            "measure",
            "strength",
            "NRS",
            "test_id",
        ],
    )
    df = df.dropna(subset=["strength"])
    df = df.dropna(subset=["id"])
    df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y", errors="coerce").fillna(
        np.nan
    )
    df["DoB"] = pd.to_datetime(df["DoB"], format="%Y.%m.%d", errors="coerce").fillna(
        np.nan
    )
    mask = pd.notnull(df["DoB"])
    df.loc[mask, "age"] = (
        (df.loc[mask, "date"] - df.loc[mask, "DoB"]) / pd.Timedelta(days=365)
    ).astype(int)
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["date"] = df["date"].dt.strftime("%m-%d-%y")
    df["DoB"] = df["DoB"].dt.strftime("%Y-%m-%d")

    final_df = df.sort_values(by=["Name"])
    final_df["strength"] = final_df["strength"].round(decimals=1)
    final_df = final_df.reset_index(drop=True)

    final_df = final_df[
        [
            "Name",
            "id",
            "Gender",
            "DoB",
            "age",
            "height",
            "body_mass",
            "lever_knee",
            "lever_groin",
            "team",
            "position",
            "date",
            "year",
            "term",
            "season_period",
            "type",
            "test",
            "leg",
            "measure",
            "strength",
            "NRS",
            "test_id",
        ]
    ]
    return final_df


def convert_df(df):
    return df.to_csv(index=False, date_format="%m.%d.%Y").encode("utf-8")


def df_summary(df):
    cut_df = df[
        ["Name", "date", "term", "season_period", "test", "leg", "strength", "test_id"]
    ]
    df_left = cut_df[cut_df["leg"] == "Left"]
    df_right = cut_df[cut_df["leg"] == "Right"]
    joined_df = pd.merge(df_left, df_right, on=["Name", "test_id"])
    joined_df = joined_df.rename(
        columns={
            "date_x": "Date",
            "term_x": "Term",
            "season_period_x": "Season Period",
            "test_x": "Test",
            "strength_x": "Max left",
            "strength_y": "Max right",
        }
    )
    joined_df = joined_df.drop(
        ["date_y", "term_y", "season_period_y", "test_y", "leg_x", "leg_y"], axis=1
    )

    joined_df["Percentage difference"] = percentage_difference(
        joined_df["Max left"], joined_df["Max right"]
    )
    joined_df["Percentage difference"] = joined_df["Percentage difference"].round(
        decimals=1
    )
    joined_df["Mean strength"] = (joined_df["Max left"] + joined_df["Max right"]) / 2
    joined_df["Mean strength"] = joined_df["Mean strength"].round(decimals=1)

    joined_df = joined_df[
        [
            "Name",
            "Date",
            "Term",
            "Season Period",
            "Test",
            "Max left",
            "Max right",
            "Mean strength",
            "Percentage difference",
        ]
    ]
    return joined_df


uploaded_files = st.file_uploader(
    "Upload xlsx files below", type="xlsx", accept_multiple_files=True
)

if uploaded_files is not None:
    # try:
    df = preprocess(uploaded_files=uploaded_files)
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    joined_df = df_summary(df)
    AgGrid(joined_df, fit_columns_on_grid_load=True)
    # except:
    # pass

    # try:
    csv = convert_df(df)
    st.download_button(
        "Press to Download the full mastersheet version",
        csv,
        "output.csv",
        "text/csv",
        key="download-csv",
    )
    # except:
    # pass

    st.write("")
    st.write("")

    with st.form(key="my_form2"):
        test = st.radio(
            "Choose a test to visualize", ("Nordic", "Hamstring", "Isometric")
        )
        sorter = st.radio(
            "Sort the values by", ("Max right", "Max left", "Mean strength")
        )
        if sorter == "Max right":
            joined_df = joined_df.sort_values(by=["Max right"])
        elif sorter == "Max left":
            joined_df = joined_df.sort_values(by=["Max left"])
        elif sorter == "Mean strength":
            joined_df = joined_df.sort_values(by=["Mean strength"])
        submitted = st.form_submit_button(label="Visualize")

        if test == "Nordic":
            joined_df = joined_df[joined_df["Test"] == "Nordic"]
            title = "Nordic"

        elif test == "Hamstring":
            joined_df = joined_df[joined_df["Test"] == "Hamstring"]
            title = "Hamstring"

        elif test == "Isometric":
            joined_df = joined_df[joined_df["Test"] == "Isometric"]
            title = "Isometric"

        if len(df["team"].unique()) == 1:
            uniqueteam = df["team"].unique()[0]
        else:
            uniqueteam = ""

        if len(df["date"].unique()) == 1:
            uniquedate = df["date"].unique()[0]
        else:
            uniquedate = ""

    if submitted:
        ax = joined_df.plot(
            x="Name", y=["Max left", "Max right"], kind="bar", width=0.6
        )
        plt.xticks(rotation=75)
        plt.xlabel("")
        plt.ylabel("Strength (Newtons)")
        plt.rcParams.update({"font.size": 6})
        joined_df["Percentage difference"] = (
            joined_df["Percentage difference"].astype(str) + " %"
        )
        ax.bar_label(ax.containers[0], joined_df["Percentage difference"])

        plt.legend(fontsize=7)
        plt.title(title + " test " + uniqueteam + " " + uniquedate)

        st.pyplot(fig=plt)

        plt.subplots_adjust(bottom=0.30)
        fn = "scatter.png"
        plt.savefig(fn, dpi=1000)
        with open(fn, "rb") as img:
            btn = st.download_button(
                label="Press to Download", data=img, file_name=fn, mime="image/png"
            )


# %%
