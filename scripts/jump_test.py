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

def flatten_xlsx(path):
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
    try:
        jump_test_results = data.loc[:, 7:].copy()  
    except KeyError:
        return None

    name_cols = [col for col in [7, 10, 13] if col in jump_test_results.columns]
    value_cols = [col + 1 for col in name_cols]

    jump_height_ft_values = {}
    for name_col, value_col in zip(name_cols, value_cols):
        if name_col in jump_test_results and value_col in jump_test_results:
            mask = jump_test_results[name_col].astype(str) == 'jump height ft'
            if mask.any():
                jump_height_ft_values[name_col] = jump_test_results.loc[mask, value_col].values[0]

    if jump_height_ft_values:
        best_test_col = max(jump_height_ft_values, key=jump_height_ft_values.get)
        best_test_value_col = best_test_col + 1 

        required_parameters = ['contact time', 'flight time', 'jump height ft', 'rsi modified']
        results = {}
        for param in required_parameters:
            mask = jump_test_results[best_test_col].astype(str) == param
            if mask.any():
                results[param] = jump_test_results.loc[mask, best_test_value_col].values[0]
    else:
        results = {param: np.nan for param in required_parameters}


    # internal_id
    internal_id = metadata[metadata[3] == "ID"][4].values[0]


    # date_key
    dateid = extract_date_from_filename(path)
    date_key = datetime.datetime.strptime(dateid, "%d%m%y").strftime("%d.%m.%y") #format 14.03.2023
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
    rsi = results['rsi modified']

    # contact_time
    contact_time = results['contact time']

    # flight_time
    flight_time = results['flight time']

    # flight_height * 100
    flight_height = results['jump height ft'] * 100

    # test
    test = metadata[metadata[0] == "Exercise"][1].values[0]
    if test == "Isometric":
        test = "Hamstring"

    # type_measure
    type_measure = metadata[metadata[5] == "Test Type"][6].values[0]

    # forcemate_version
    forcemate_version = metadata[metadata[0] == "ForceMate v."][1].values[0]

    # firmware_version
    firmware_version = float(metadata[metadata[0] == "Firmware v."][1].values[0])

    # hz
    hz = metadata[metadata[0] == "Hz"][1].values[0]


    player_results = [
                internal_id,
                date_key,
                team_id,
                height,
                position,
                body_mass,
                rsi,
                contact_time,
                flight_time,
                flight_height,
                test,
                type_measure,
                forcemate_version,
                firmware_version,
                hz
            ]

    return player_results

#%%
dir_path = '../data/jump_test'
# def preprocess(uploaded_files):

file_names = glob.glob(os.path.join(dir_path, "*.xlsx"))


#%%
players_data = []
for file in tqdm(file_names):
    try:
        one_player = flatten_xlsx(file)
        if one_player is not None:
            players_data.append(one_player)
    except Exception as e:
        print(f"Error processing file {file}: {e}")  

df = pd.DataFrame(
    players_data,
    columns=[
         'internal_id',
        'date_key',
        'team_id',
        'height',
        'position',
        'body_mass',
        'rsi',
        'contact_time',
        'flight_time',
        'flight_height',
        'test',
        'type_measure',
        'forcemate_version',
        'firmware_version',
        'hz'
    ],
)

df = df.dropna(subset=["flight_height"])
# %%
