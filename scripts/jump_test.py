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
import glob
import os
from tqdm import tqdm
import re

#%%
def extract_date_from_filename(filename):
    pattern = r"\d{6}(?:-)?"
    match = re.search(pattern, filename)
    date = match.group()
    date = date.replace("-","")
    # Manipulate the extracted date format if needed
    return date

#%%
path = ''
data = pd.read_excel(path, header=None)


if data[0][0] == "Date" or data[0][0] == "col1":
    pass
else:
    data = data.drop([0])

data.reset_index(inplace=True)


if "index" in data.columns:
    data.drop(["index"], axis=1, inplace=True)

# extract metadata
metadata = data[[0, 1, 2, 3, 4, 5, 6]].copy()

# date = metadata[metadata[0] == "Date"][1][0].split()[0]
# dateid = metadata[metadata[0] == "Date"][1][0]



measure = "Newtons"

name = metadata[metadata[0] == "Name"][1].values[0]

# handling names separated by _
if "_" in name:
    name = " ".join(name.split("_"))

#capitalize every word in string name
name = name.title()



# internal_id
id = metadata[metadata[3] == "ID"][4].values[0]


# date_key
dateid = extract_date_from_filename(path)
date = datetime.datetime.strptime(dateid, "%d%m%y").strftime("%d.%m.%y") #format 14.03.2023
# year = date.split(".")[-1]

# team_id
team_to_id = {
    "Superliga": "fcn_men_superliga",
    "U10": "fcn_men_u10",
    "U11": "fcn_men_u11",
    "U12": "fcn_men_u12",
    "U13": "fcn_men_u13",
    "U14": "fcn_men_u14",
    "U15": "fcn_men_u15",
    "U17": "fcn_men_u17",
    "U19": "fcn_men_u19",
    "Womens Senior": "fcn_women_senior",
    "Womens U14": "fcn_women_u14",
    "Womens U16": "fcn_women_u16",
    "Womens U18": "fcn_women_u18",
    "U11 Egypt": "rtd_egypt_men_u11",
    "U13 Egypt": "rtd_egypt_men_u13",
    "U15 Egypt": "rtd_egypt_men_u15",
    "Advanced": "rtd_ghana_men_advanced",
    "Development": "rtd_ghana_men_development",
    "Foundation": "rtd_ghana_men_foundation",
    "International Academy": "rtd_ghana_men_ia",
    "Juniors": "rtd_ghana_men_juniors",
    "Transition": "rtd_ghana_men_transition",
}

team = metadata[metadata[0] == "Team"][1].values[0]
team_id = team_to_id[team]
# height
height = metadata[metadata[3] == "Height"][4].values[0]

# position 
position = metadata[metadata[3] == "Position"][4].values[0]

# body_mass
body_mass = metadata[metadata[3] == "Weight"][4].values[0]

# rsi

# contact_time

# flight_time

# flight_height

# test
test = metadata[metadata[0] == "Exercise"][1].values[0]
if test == "Isometric":
    test = "Hamstring"

# type_measure
type_measure = metadata[metadata[5] == "Season Period"][6].values[0]

# forcemate_version
forcemate_version = metadata[metadata[0] == "ForceMate v."][1].values[0]

# firmware_version
firmware_version = float(metadata[metadata[0] == "Firmware v."][1].values[0])

# hz
test = metadata[metadata[0] == "Hz"][1].values[0]


#%%



#%%


# # extract test results
# test_results = data[[1, 2]][7::].copy()

# #%%
# test_results.columns = ["Left", "Right"]
# # check if any value in the dataframe is called "Left"
# if "Left" in test_results.values:
#     test_results = data[[1, 2]][8::].copy()
# test_results.columns = ["Left", "Right"]
# tests = test_results.astype("float")
# left_max = tests["Left"].max()
# right_max = tests["Right"].max()

# # extract player and test information
# try:
#     right_col_data = data[[4, 5, 6, 7, 8]].copy()
# except:
#     pass

# try:
#     # different possible NRS names (fx. NRS (R), NRS Right, NRS Right (Pain during Test))
#     nrs_vals = []
#     for val in right_col_data[7].values:
#         if type(val) == str and val.startswith("NRS"):
#             nrs_vals.append(right_col_data[right_col_data[7] == val][8].values[0])

#     if len(nrs_vals) == 2:
#         nrs_right = nrs_vals[0]
#         nrs_left = nrs_vals[1]
#         nrs_prev_right = np.nan
#         nrs_prev_left = np.nan
#     elif len(nrs_vals) == 4:
#         nrs_right = nrs_vals[0]
#         nrs_left = nrs_vals[1]
#         nrs_prev_right = nrs_vals[2]
#         nrs_prev_left = nrs_vals[3]

#     season_data = right_col_data[right_col_data[7] == "Season Period"][8]
#     try:
#         season_split = season_data.values[0].split()
#     except:
#         season_split = [np.nan, np.nan]

#     term = season_split[1]
#     season_period = season_split[0]
#     test_type = right_col_data[right_col_data[7] == "Test Type"][8].values[0]
# except:
#     nrs_right = np.nan
#     nrs_left = np.nan
#     nrs_prev_right = np.nan
#     nrs_prev_left = np.nan
#     term = np.nan
#     season_period = np.nan
#     test_type = np.nan

# # right_col_data[4] = [
# #     None,  # player attributes
# #     "Date of birth (dd/mm/yyyy)",
# #     "Gender",
# #     "Height",
# #     "Weight",
# #     "Position",
# #     "ID",
# #     "Hip-Knee Lever",
# #     "Hip-Ankle Lever",
# # ] + [None] * (len(data) - 9)

# try:
#     # st.write(right_col_data)
#     dob = right_col_data[right_col_data[4] == "Date of birth (dd/mm/yyyy)"][
#         5
#     ].values[0]
#     gender = right_col_data[right_col_data[4] == "Gender"][5].values[0]
#     height = right_col_data[right_col_data[4] == "Height"][5].values[0]
#     weight = right_col_data[right_col_data[4] == "Weight"][5].values[0]

#     # if there's a value for weight under custom fields, it should replace the other one
#     if (
#         "Weight" in right_col_data[7].values
#         and float(right_col_data[right_col_data[7] == "Weight"][8].values[0]) > 0
#     ):
#         weight = right_col_data[right_col_data[7] == "Weight"][8].values[0]

#     # in case the weight field is called bodymass
#     if (
#         "Bodymass" in right_col_data[7].values
#         and float(right_col_data[right_col_data[7] == "Bodymass"][8].values[0]) > 0
#     ):
#         weight = right_col_data[right_col_data[7] == "Bodymass"][8].values[0]

#     position = right_col_data[right_col_data[4] == "Position"][5].values[0]

#     lever_knee = right_col_data[right_col_data[4] == "Hip-Knee Lever"][5].values[0]
#     lever_groin = right_col_data[right_col_data[4] == "Hip-Ankle Lever"][5].values[
#         0
#     ]
#     height = round(float(height), 1)
#     weight = round(float(weight), 1)
# except:
#     dob = np.nan
#     gender = np.nan
#     height = np.nan
#     weight = np.nan
#     position = np.nan
#     # id = np.nan
#     lever_knee = np.nan
#     lever_groin = np.nan

# try:
#     id = right_col_data[right_col_data[4] == "ID"][5].values[0]
# except:
#     id = np.nan

# # extracting software specs
# try:
#     software_specs = data[[11, 12]]
#     forcemate_version = software_specs[software_specs[11] == "ForceMate version"][
#         12
#     ].values[0]
#     firmware_version = software_specs[software_specs[11] == "Firmware version"][
#         12
#     ].values[0]
#     hz = software_specs[software_specs[11] == "Hz"][12].values[0]
#     measure = software_specs[software_specs[11] == "Unit"][12].values[0]
#     if measure == "N":
#         measure = "Newtons"
# except:
#     forcemate_version = np.nan
#     firmware_version = np.nan
#     hz = np.nan
#     measure = "Newtons"

# #%%

# def extract_date_from_filename(filename):
#     pattern = r"\d{6}(?:-)?"
#     match = re.search(pattern, filename)
#     date = match.group()
#     date = date.replace("-","")
#     # Manipulate the extracted date format if needed
#     return date


# def flatten_xlsx(path):
#     # print(path)

#     data = pd.read_excel(path, header=None)

#     if data[0][0] == "Date" or data[0][0] == "col1":
#         pass
#     else:
#         data = data.drop([0])

#     data.reset_index(inplace=True)


#     if "index" in data.columns:
#         data.drop(["index"], axis=1, inplace=True)

#     # extract metadata
#     metadata = data[[0, 1]].copy()

#     dateid = extract_date_from_filename(path)
#     #convert to datetime of format 14.03.2023
#     date = datetime.datetime.strptime(dateid, "%d%m%y").strftime("%d.%m.%y")
#     # date = metadata[metadata[0] == "Date"][1][0].split()[0]
#     # dateid = metadata[metadata[0] == "Date"][1][0]
#     year = date.split(".")[-1]
#     test = metadata[metadata[0] == "Exercise"][1].values[0]
#     if test == "Isometric":
#         test = "Hamstring"

#     measure = "Newtons"
#     team = metadata[metadata[0] == "Team"][1].values[0]
#     name = metadata[metadata[0] == "Name"][1].values[0]

#     # handling names separated by _
#     if "_" in name:
#         name = " ".join(name.split("_"))

#     #capitalize every word in string name
#     name = name.title()

#     # extract test results
#     test_results = data[[1, 2]][7::].copy()
#     test_results.columns = ["Left", "Right"]
#     # check if any value in the dataframe is called "Left"
#     if "Left" in test_results.values:
#         test_results = data[[1, 2]][8::].copy()
#     test_results.columns = ["Left", "Right"]
#     tests = test_results.astype("float")
#     left_max = tests["Left"].max()
#     right_max = tests["Right"].max()

#     # extract player and test information
#     try:
#         right_col_data = data[[4, 5, 6, 7, 8]].copy()
#     except:
#         pass

#     try:
#         # different possible NRS names (fx. NRS (R), NRS Right, NRS Right (Pain during Test))
#         nrs_vals = []
#         for val in right_col_data[7].values:
#             if type(val) == str and val.startswith("NRS"):
#                 nrs_vals.append(right_col_data[right_col_data[7] == val][8].values[0])

#         if len(nrs_vals) == 2:
#             nrs_right = nrs_vals[0]
#             nrs_left = nrs_vals[1]
#             nrs_prev_right = np.nan
#             nrs_prev_left = np.nan
#         elif len(nrs_vals) == 4:
#             nrs_right = nrs_vals[0]
#             nrs_left = nrs_vals[1]
#             nrs_prev_right = nrs_vals[2]
#             nrs_prev_left = nrs_vals[3]

#         season_data = right_col_data[right_col_data[7] == "Season Period"][8]
#         try:
#             season_split = season_data.values[0].split()
#         except:
#             season_split = [np.nan, np.nan]

#         term = season_split[1]
#         season_period = season_split[0]
#         test_type = right_col_data[right_col_data[7] == "Test Type"][8].values[0]
#     except:
#         nrs_right = np.nan
#         nrs_left = np.nan
#         nrs_prev_right = np.nan
#         nrs_prev_left = np.nan
#         term = np.nan
#         season_period = np.nan
#         test_type = np.nan

#     # right_col_data[4] = [
#     #     None,  # player attributes
#     #     "Date of birth (dd/mm/yyyy)",
#     #     "Gender",
#     #     "Height",
#     #     "Weight",
#     #     "Position",
#     #     "ID",
#     #     "Hip-Knee Lever",
#     #     "Hip-Ankle Lever",
#     # ] + [None] * (len(data) - 9)

#     try:
#         # st.write(right_col_data)
#         dob = right_col_data[right_col_data[4] == "Date of birth (dd/mm/yyyy)"][
#             5
#         ].values[0]
#         gender = right_col_data[right_col_data[4] == "Gender"][5].values[0]
#         height = right_col_data[right_col_data[4] == "Height"][5].values[0]
#         weight = right_col_data[right_col_data[4] == "Weight"][5].values[0]

#         # if there's a value for weight under custom fields, it should replace the other one
#         if (
#             "Weight" in right_col_data[7].values
#             and float(right_col_data[right_col_data[7] == "Weight"][8].values[0]) > 0
#         ):
#             weight = right_col_data[right_col_data[7] == "Weight"][8].values[0]

#         # in case the weight field is called bodymass
#         if (
#             "Bodymass" in right_col_data[7].values
#             and float(right_col_data[right_col_data[7] == "Bodymass"][8].values[0]) > 0
#         ):
#             weight = right_col_data[right_col_data[7] == "Bodymass"][8].values[0]

#         position = right_col_data[right_col_data[4] == "Position"][5].values[0]

#         lever_knee = right_col_data[right_col_data[4] == "Hip-Knee Lever"][5].values[0]
#         lever_groin = right_col_data[right_col_data[4] == "Hip-Ankle Lever"][5].values[
#             0
#         ]
#         height = round(float(height), 1)
#         weight = round(float(weight), 1)
#     except:
#         dob = np.nan
#         gender = np.nan
#         height = np.nan
#         weight = np.nan
#         position = np.nan
#         # id = np.nan
#         lever_knee = np.nan
#         lever_groin = np.nan

#     try:
#         id = right_col_data[right_col_data[4] == "ID"][5].values[0]
#     except:
#         id = np.nan

#     # extracting software specs
#     try:
#         software_specs = data[[11, 12]]
#         forcemate_version = software_specs[software_specs[11] == "ForceMate version"][
#             12
#         ].values[0]
#         firmware_version = software_specs[software_specs[11] == "Firmware version"][
#             12
#         ].values[0]
#         hz = software_specs[software_specs[11] == "Hz"][12].values[0]
#         measure = software_specs[software_specs[11] == "Unit"][12].values[0]
#         if measure == "N":
#             measure = "Newtons"
#     except:
#         forcemate_version = np.nan
#         firmware_version = np.nan
#         hz = np.nan
#         measure = "Newtons"

#     # try:
#     #     nrs_prev_left = right_col_data[right_col_data[7] == "NRS Previous wk (L)"][
#     #         8
#     #     ].values[0]
#     #     nrs_prev_right = right_col_data[right_col_data[7] == "NRS Previous wk (R)"][
#     #         8
#     #     ].values[0]
#     # except:
#     #     nrs_prev_left = np.nan
#     #     nrs_prev_right = np.nan

#     try:
#         test_id = (
#             id
#             + test
#             + (id + test + "".join(dateid.split("."))).replace(" ", "").replace(":", "")
#         )
#     except:
#         test_id = np.nan

#     x = [
#         [
#             name,
#             id,
#             gender,
#             dob,
#             np.nan,
#             height,
#             weight,
#             lever_knee,
#             lever_groin,
#             team,
#             position,
#             date,
#             year,
#             term,
#             season_period,
#             test_type,
#             test,
#             "Right",
#             measure,
#             right_max,
#             nrs_right,
#             nrs_prev_right,
#             test_id,
#             forcemate_version,
#             firmware_version,
#             hz,
#         ],
#         [
#             name,
#             id,
#             gender,
#             dob,
#             np.nan,
#             height,
#             weight,
#             lever_knee,
#             lever_groin,
#             team,
#             position,
#             date,
#             year,
#             term,
#             season_period,
#             test_type,
#             test,
#             "Left",
#             measure,
#             left_max,
#             nrs_left,
#             nrs_prev_left,
#             test_id,
#             forcemate_version,
#             firmware_version,
#             hz,
#         ],
#     ]

#     return x



# #%%
# # flatten_xlsx("/Users/franekl/Desktop/RTD Tables/Bishop_Addai_050623-14_47_27.xlsx")
# #%%
# def preprocess(uploaded_files):

#     # file_names = glob.glob(os.path.join(dir_path, "*.xlsx"))

#     players_data = []
#     for file in tqdm(uploaded_files):
#         one_player = flatten_xlsx(file)
#         one_player_right = one_player[0]
#         one_player_left = one_player[1]
#         players_data.append(one_player_right)
#         players_data.append(one_player_left)

#     df = pd.DataFrame(
#         players_data,
#         columns=[
#             "Name",
#             "id",
#             "Gender",
#             "DoB",
#             "age",
#             "height",
#             "body_mass",
#             "lever_knee",
#             "lever_groin",
#             "team",
#             "position",
#             "date",
#             "year",
#             "term",
#             "season_period",
#             "type",
#             "test",
#             "leg",
#             "measure",
#             "strength",
#             "NRS",
#             "NRS previous",
#             "test_id",
#             "forcemate_version",
#             "firmware_version",
#             "hz",
#         ],
#     )

#     df = df.dropna(subset=["strength"])
#     print(df['date'])
#     # df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y", errors="coerce").fillna(
#     #     np.nan
#     # )
    
#     # df["DoB"] = pd.to_datetime(df["DoB"], format="%Y-%m-%d", errors="coerce").fillna(
#     #     np.nan
#     # )
#     # print(df['DoB'])
#     # mask = pd.notnull(df["DoB"])
#     # df.loc[mask, "age"] = (
#     #     (df.loc[mask, "date"] - df.loc[mask, "DoB"]) / pd.Timedelta(days=365)
#     # ).astype(int)
#     df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y", errors="coerce")
#     df["DoB"] = pd.to_datetime(df["DoB"], format="%Y-%m-%d", errors="coerce")

#     df['age'] = (df["date"] - df["DoB"]) / pd.Timedelta(days=365) 
#     df.loc[df['age'].notna(), 'age'] = df.loc[df['age'].notna(), 'age'].astype(int)

#     df["age"] = pd.to_numeric(df["age"], errors="coerce")
#     df["date"] = df["date"].dt.strftime("%m-%d-%y")
#     df["DoB"] = df["DoB"].dt.strftime("%Y-%m-%d")

#     final_df = df.sort_values(by=["Name"])
#     final_df["strength"] = final_df["strength"].round(decimals=1)
#     final_df = final_df.reset_index(drop=True)

#     final_df = final_df[
#         [
#             "Name",
#             "id",
#             "Gender",
#             "DoB",
#             "age",
#             "height",
#             "body_mass",
#             "lever_knee",
#             "lever_groin",
#             "team",
#             "position",
#             "date",
#             "year",
#             "term",
#             "season_period",
#             "type",
#             "test",
#             "leg",
#             "measure",
#             "strength",
#             "NRS",
#             "NRS previous",
#             "test_id",
#             "forcemate_version",
#             "firmware_version",
#             "hz",
#         ]
#     ]
#     return final_df


# def convert_df(df):
#     return df.to_csv(index=False, date_format="%m.%d.%Y").encode("utf-8")


# #%%
# # list all the files in the folder /Users/franekl/Desktop/Chris old data
# dir_path = "/Users/franekl/Desktop/RTD Tables"
# file_names = glob.glob(os.path.join(dir_path, "*.xlsx"))
# results = preprocess(file_names)
# results = results[results['test'] != 'Eccentric']
# results.reset_index(inplace=True)
# results.drop('index', axis=1, inplace=True)
# results.to_csv("results.csv", index=False)
# # %%

# # %%
