import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np 
from pathlib import Path

st.set_page_config(page_title="Strength data visualization", page_icon="☀️", layout="wide")
st.sidebar.markdown("## Strength data visualization")

uploaded_file = st.file_uploader("Choose a file to upload")
if uploaded_file is not None:
    df1=pd.read_csv(uploaded_file)
    st.dataframe(df1)


def return_max(lst):

    max_value = 0
    for num in lst:
        if (max_value is None or float(num) > float(max_value)):
            max_value = num
    return float(max_value)


def output_calculations(path, perc_margin=1, splits = 10, viz=False, zoom=False, output=False): 
    
    """
    args:
    path = file path where the csv file for extraction is located 
    perc_margin = +/- value for +/- 2.5%, fx. for perc_margin = 1, the threshold will be set from 2.4% to 2.6%
                - increase the margin if the onset/offset are further away from the curve of interest than they should be
    splits = intervals/milisecond splits, used for the output file, fx. splits=10 means that we will take only every 10th milisecond into consideration
    viz = set to True for visualization of the peaks, along with the onset/offset line (x axis = time[ms], y_axis = force_left/force_right[N])
    zoom = set to True to view the zoomed part of the graphs in order to assess the peak and onset/offset calculations
    output = set to True to save the files (will be saved in the same directory as the input file)
    """ 

    df = pd.read_csv(path, delimiter=';', skiprows=5)
    if len(df.columns) == 4:
         df.drop(df.columns[3], inplace=True, axis=1)
    # df = df.rename(columns={"Time: 08.07.2022 13:57:23":"SampleTime[s]", "Unnamed: 1": "Force_left[N]", "Unnamed: 2":"Force_right[N]"})
    dct_replace = {df.columns[0]:"SampleTime[s]", df.columns[1]:"Force_left[N]", df.columns[2]: "Force_right[N]"}
    df = df.rename(columns=dct_replace)
    df['Force_left[N]'] = df['Force_left[N]'].astype(float)
    df['Force_right[N]'] = df['Force_right[N]'].astype(float)
    df.reset_index(inplace = True)
    df.drop("index", inplace=True, axis=1)

    left = list(df['Force_left[N]'])
    right = list(df['Force_right[N]'])
    max_left = return_max(left)
    max_right = return_max(right)
    index_max_left = df[df['Force_left[N]'] == float(max_left)].index[0]
    index_max_right = df[df['Force_right[N]'] == float(max_right)].index[0]

    perc = 2.5
    p = perc * 0.01
    perc_margin = perc_margin * 0.001
    p_lower = round(p-perc_margin,3)
    p_upper = round(p+perc_margin,3)

    left_24 = p_lower * float(max_left)
    left_26 = p_upper * float(max_left)
    left_24 = float("{:.2f}".format(left_24))
    left_26 = float("{:.2f}".format(left_26))

    right_24 = p_lower * float(max_right)
    right_26 = p_upper * float(max_right)
    right_24 = float("{:.2f}".format(right_24))
    right_26 = float("{:.2f}".format(right_26))

    acceptable_onset_value_lst_left = list(np.arange(left_24, left_26, 0.01))
    acceptable_onset_value_lst_left = [float('%.2f' % elem) for elem in acceptable_onset_value_lst_left]

    acceptable_onset_value_lst_right = list(np.arange(right_24, right_26, 0.01))
    acceptable_onset_value_lst_right = [float('%.2f' % elem) for elem in acceptable_onset_value_lst_right]

    possible_onsets_left = df[df['Force_left[N]'].isin(acceptable_onset_value_lst_left)]
    possible_onsets_right = df[df['Force_right[N]'].isin(acceptable_onset_value_lst_right)]

    onset_left = max([x for x in list(possible_onsets_left.index) if x <= index_max_left])
    offset_left = min([x for x in list(possible_onsets_left.index) if x >= index_max_left])

    onset_right = max([x for x in list(possible_onsets_right.index) if x <= index_max_right])
    offset_right = min([x for x in list(possible_onsets_right.index) if x >= index_max_right])

    df_left = df[['SampleTime[s]', 'Force_left[N]']]
    df_left = df_left.iloc[onset_left:offset_left]

    df_right = df[['SampleTime[s]', 'Force_right[N]']]
    df_right = df_right.iloc[onset_right:offset_right]

    df_left = df_left.iloc[::splits, :]
    df_right = df_right.iloc[::splits, :]

    df_left["Peak"] = max_left
    df_right["Peak"] = max_right
    df_left['Peak_difference[Peak-Force_left]'] = max_left - df_left['Force_left[N]']
    df_right['Peak_difference[Peak-Force_right]'] = max_right - df_right['Force_right[N]']

    if viz == True:

        fig, (ax1, ax2) = plt.subplots(2,1)
        sns.lineplot(data=df, x=df.index, y='Force_left[N]', ax=ax1)
        ax1.axvline(x=onset_left, color='green', linestyle='--', lw=1)
        ax1.axvline(x=offset_left, color='green', linestyle='--', lw=1)

        sns.lineplot(data=df, x=df.index, y='Force_right[N]', ax=ax2)
        ax2.axvline(x=onset_right, color='green', linestyle='--', lw=1)
        ax2.axvline(x=offset_right, color='green', linestyle='--', lw=1)

        if zoom==True:
            ax1.set_xlim(onset_left-150, offset_left+150)
            ax2.set_xlim(onset_right-150, offset_right+150)

    if output == True:

        directory_path = str(Path(path).parent)
        df_left.to_excel(directory_path + "/output_left.xlsx")
        df_right.to_excel(directory_path + "/output_right.xlsx")


    return df_left, df_right


# path = " "
# output_calculations(path, viz=True, output=True)
