#%%
import pandas as pd
import streamlit as st
from plottable import ColumnDefinition, Table
from plottable.cmap import normed_cmap
from matplotlib.colors import LinearSegmentedColormap
import matplotlib
import matplotlib.colors as mcolors
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import io

#%%

st.set_page_config(page_title="Sprint app data extraction", layout="wide")

st.title("Sprint test data extraction")


#%%
def preprocess(uploaded_file):
    data = pd.read_excel(uploaded_file, sheet_name="Result (All)")
    final_results = []
    for name in list(data["Name"].unique()):
        name_data = data[data["Name"] == name]
        min_time = name_data["Time (s)"].min()
        best_sprint = name_data[name_data["Time (s)"] == min_time]
        if len(best_sprint.columns) > 1:
            best_sprint = best_sprint[
                best_sprint["25-30m (s)"] == min(best_sprint["25-30m (s)"])
            ]
        zero_five = float(best_sprint["0-5m (s)"])
        five_tfive = float(best_sprint["5-25m (s)"])
        tfive_thirty = float(best_sprint["25-30m (s)"])
        max_vel = round(5 / tfive_thirty * 3.6, 2)
        speed_at_5m = round(5 / zero_five * 3.6, 2)
        results = [
            name,
            min_time,
            zero_five,
            five_tfive,
            tfive_thirty,
            max_vel,
            speed_at_5m,
        ]
        final_results.append(results)

    column_names = [
        "Name",
        "Time (s)",
        "0-5m (s)",
        "5-25m (s)",
        "25-30m (s)",
        "Max Velocity (km/h)",
        "Speed @ 5m (km/h)",
    ]
    df = pd.DataFrame(final_results, columns=column_names)
    df = df.sort_values(by=["Time (s)", "Name"])
    average_row = df.mean()
    average_row["Name"] = "Average"
    df.loc["Average"] = average_row

    for col in df.columns:
        if col != "Name":
            df[col] = df[col].round(decimals=2)

    df = df.reset_index(drop=True)

    return df


def plot_table(df):
    fig, ax = plt.subplots(figsize=(20, 15))
    col_defs = [
        ColumnDefinition(
            name="Name",
            textprops={
                "ha": "center",
                "weight": "bold",
                # "bbox": {"boxstyle": "circle", "pad": 0.65, 'color':'gray'},
            },
            width=3,
            border="right",
        ),
        ColumnDefinition(
            name="Time (s)",
            textprops={"ha": "center"},
            width=1.25,
            border="right",
            cmap=normed_cmap(
                df["Time (s)"], cmap=matplotlib.cm.RdYlGn.reversed(), num_stds=2
            ),
        ),
        ColumnDefinition(
            name="0-5m (s)",
            textprops={"ha": "center"},
            width=1.25,
            border="right",
        ),
        ColumnDefinition(
            name="5-25m (s)", textprops={"ha": "center"}, width=1.25, border="right"
        ),
        ColumnDefinition(
            name="25-30m (s)", textprops={"ha": "center"}, width=1, border="right"
        ),
        ColumnDefinition(
            name="Max Velocity (km/h)",
            textprops={"ha": "center"},
            width=2,
            border="right",
        ),
        ColumnDefinition(
            name="Speed @ 5m (km/h)",
            textprops={"ha": "center"},
            width=2,
            border="right",
        ),
    ]

    table = Table(
        df,
        column_definitions=col_defs,
        ax=ax,
        textprops={"fontsize": 16, "fontname": "Roboto"},
    )

    table.rows[df.shape[0] - 1].set_facecolor("lightgrey")
    if team_name != "":
        plt.title(f"Sprint test results - {team_name}, {date}", fontsize=30)
    else:
        plt.title(f"Sprint test results - {date}", fontsize=30)


def convert_df(df):
    return df.to_csv(index=False, date_format="%m.%d.%Y").encode("utf-8")


# %%

team_name = st.text_input("Enter team name:")
date = st.date_input("Select date:")
# sb = st.selectbox(
#     "Select the name:",
#     ["Mounir Jamal Secka", "Hektor Højbjerg Thomsen", "Marcelo Cunha Randolf"],
# )

uploaded_files = st.file_uploader(
    "Upload sprint test data file below", type="xlsx", accept_multiple_files=False
)


if uploaded_files is not None:
    df = preprocess(uploaded_file=uploaded_files)
    csv = convert_df(df)
    df = df.set_index("Name")
    # plot_table(df)

    with PdfPages("Sprint testing Results.pdf") as pdf:
        plot_table(df)
        st.pyplot(fig=plt)
        pdf.savefig(bbox_inches="tight")

    with open("Sprint testing Results.pdf", "rb") as results:
        st.download_button(
            "Download the data",
            results,
            f'Sprint_Test_Results_{team_name}_{"".join(str(date).split("-"))}.pdf',
        )

    st.download_button(
        "Download the csv file",
        csv,
        f'Sprint_Test_Results_{team_name}_{"".join(str(date).split("-"))}.csv',
        "text/csv",
        key="download-csv",
    )
