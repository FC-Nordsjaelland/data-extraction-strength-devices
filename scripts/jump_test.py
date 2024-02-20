#%%
import pandas as pd
import datetime
from datetime import time
import numpy as np
import glob
import os
from tqdm import tqdm
import re

def extract_date_from_filename(filename):
    pattern = r"\d{6}(?:-)?"
    match = re.search(pattern, filename)
    date = match.group()
    date = date.replace("-","")
    return date


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

    # Initialize a dictionary to store 'rsi modified' values
    rsi_modified_values = {}

    # Iterate over name and value columns to find 'rsi modified' values
    for name_col, value_col in zip(name_cols, value_cols):
        if name_col in jump_test_results and value_col in jump_test_results:
            mask = jump_test_results[name_col].astype(str) == 'rsi modified'
            if mask.any():
                # Extract the first 'rsi modified' value found and round it to 3 decimal places
                rsi_value = round(jump_test_results.loc[mask, value_col].values[0], 3)
                rsi_modified_values[name_col] = rsi_value

    # Determine the test with the highest 'rsi modified' value
    if rsi_modified_values:
        best_test_col = max(rsi_modified_values, key=rsi_modified_values.get)
        best_test_value_col = best_test_col + 1

        # Define required parameters to extract
        required_parameters = ['contact time', 'flight time', 'jump height ft', 'rsi modified']
        results = {}
        for param in required_parameters:
            mask = jump_test_results[best_test_col].astype(str) == param
            if mask.any():
                # Round extracted values to 3 decimal places as needed
                if param in ['contact time', 'flight time', 'jump height ft']:
                    results[param] = jump_test_results.loc[mask, best_test_value_col].values[0]
                else:
                    # For 'rsi modified', no multiplication by 100 is needed
                    results[param] = jump_test_results.loc[mask, best_test_value_col].values[0]
    else:
        # Initialize results with NaN if no 'rsi modified' values were found
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
    rsi = results.get('rsi modified', np.nan)

    # contact_time
    contact_time = results.get('contact time', np.nan)

    # flight_time
    flight_time = results.get('flight time', np.nan)

    # flight_height * 100
    flight_height = results.get('jump height ft', np.nan)

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


def preprocess(dir_path):

    file_names = glob.glob(os.path.join(dir_path, "*.xlsx"))

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
            'jump_height',
            'test',
            'type_measure',
            'forcemate_version',
            'firmware_version',
            'hz'
        ],
    )


    df['date_key'] = pd.to_datetime(df['date_key'])
    df['date_key'] = df['date_key'].dt.strftime('%Y-%d-%m')

    df = df.dropna(subset=["jump_height"])

    return df

dir_path = '../data/jump_test'

df = preprocess(dir_path=dir_path)

df

df.to_csv("jump_test_results.csv")
# %%
df
# %%



#if statement if dj

