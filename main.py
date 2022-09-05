#%%
import pandas as pd
import glob
import os
import warnings
import datetime
from datetime import time
import streamlit as st
# warnings.filterwarnings("ignore")

#%%

st.set_page_config(page_title="Polar data extraction", layout ='centered')

st.title("Strength data summary")
st.text("")
# st.header("**Instruction**")


def flatten_xlsx(path):

    data = pd.read_excel(path, header=None)

    metadata=data.head(6)
    tests=data[7::]
    metadata[[0,1]] = metadata[[0,1]].astype("string")
    tests[[1,2]] = tests[[1,2]].astype("float")

    date = metadata[metadata[0]=='Date'][1][0]
    device = metadata[metadata[0]=='Device'][1][1]
    team = metadata[metadata[0]=='Team'][1][2]

    name = metadata[metadata[0]=='Name'][1][3]
    name = name.replace(" - nordic", "") #remove those occurences from the names
    name = name.replace("1","") #sometimes it states " - nordic1", that line removes the issue

    comment = metadata[metadata[0]=='Comment'][1][4]
    left_max = tests[1].max()
    right_max = tests[2].max()

    x = [date,device,team,name,comment,left_max,right_max]

    return x

def preprocess(uploaded_files, start_date, end_date):

    # file_names = glob.glob(os.path.join(dir_path, "*.xlsx"))

    players_data = []
    for file in uploaded_files:
        one_player = flatten_xlsx(file)
        players_data.append(one_player)
        #line to add another column or so 

    
    df = pd.DataFrame(players_data, columns=['Date','Device','Team','Name','Comment',"Max left", "Max right"])
    df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y %H:%M:%S')
    df[["Max left","Max right"]] = df[["Max left","Max right"]].astype(float)
    # df = df.loc[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    df['time_difference'] = (df['Date']-start_date).astype('timedelta64[m]')
    df['time_difference'] = df['time_difference'].astype(int)
    within_interval_df = df[(df['time_difference'] >= -t_interval) & (df['time_difference'] <= t_interval)]
    within_interval_df_meta = within_interval_df.copy()
    within_interval_df = within_interval_df.groupby(['Name', 'Device'])[["Max left", "Max right"]].max()
    
    within_interval_df_meta = within_interval_df_meta.drop(['Max left', 'Max right'], axis = 1)
    merge_within_interval = pd.merge(within_interval_df, within_interval_df_meta, on=["Name","Device"])


    not_in_interval = df[~((df['time_difference'] >= -t_interval) & (df['time_difference'] <= t_interval))]

    final_df = pd.concat([merge_within_interval, not_in_interval])

    final_df = final_df.drop_duplicates(subset=['Name', 'Device', "Max left", "Max right"])
    final_df = final_df.sort_values(by=['Name'])
    final_df['Max left'] = final_df['Max left'].round(decimals=1)
    final_df['Max right'] = final_df['Max right'].round(decimals=1)
    # final_df = final_df.drop(["time_difference"], axis=1)
    final_df = final_df.reset_index(drop=True)
   
    return final_df

def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')


min_date = "2022-01-01"
min_date = datetime.datetime.strptime(min_date, '%Y-%m-%d')
max_date = "2023-01-01"
max_date = datetime.datetime.strptime(max_date, '%Y-%m-%d')

uploaded_files = st.file_uploader("Upload xlsx files below", type="xlsx", accept_multiple_files=True)


try:

    if uploaded_files:
        x = []
        for file in uploaded_files:
            file.seek(0)
                
        uploaded_data_read = [pd.read_excel(file, header=None) for file in uploaded_files]
        raw_data = pd.concat(uploaded_data_read)
        raw_data = raw_data[raw_data[0]=="Date"]
        raw_data[1] = pd.to_datetime(raw_data[1], format='%d.%m.%Y %H:%M:%S')
        min_date = raw_data[1].min()
        max_date = raw_data[1].max()



    with st.form(key='my_form'):

        c1, c2 = st.columns(2)
        # with c1:
        #     date1 = st.date_input(
        #         "Choose a start date",
        #         min_date.date())
        #     t1 = st.time_input('Choose a start time', datetime.time(0, 00))
        # with c2: 
        #     date2 = st.date_input(
        #         "Choose an end date",
        #         max_date.date())
        #     t2 = st.time_input('Choose an end time', datetime.time(23, 45))

        date1 = st.date_input(
                "Choose a testing date",
                min_date.date())
        t1 = st.time_input("Choose the time of the testing", datetime.time(12,30))
        t_interval = st.slider("Select the time interval [min]", 0, 720, 30)

        output_name = st.text_input("Enter the output file name", "output")
        st.form_submit_button()






    # path = input("Enter the directory path where the Excel files are stored: ")
    # path2 = input("Enter the directory path where the CSV output is saved: ")
    # date1 = input("Enter the starting date and time (format - 2022-03-04 12:00:00): ")
    # date2 = input("Enter the end date (format - 2022-03-04 12:00:00): ")
    # name = input("Enter the output file name: ")

    #start_datetime = datetime.strptime('2022-03-04 12:00:00', '%Y-%m-%d %H:%M:%S')

    # start_date = date1 + t1
    # end_date = date2 + t2

    # start_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    # end_datetime = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

        start_date = datetime.datetime.combine(date1,t1)
        # end_date = datetime.datetime.combine(date2,t2)
        end_date = '2025-08-08 12:00:00'
        df = preprocess(uploaded_files=uploaded_files, start_date=start_date, end_date=end_date)
        st.dataframe(df)
        
        csv = convert_df(df)

        st.download_button(
        "Press to Download",
        csv,
        output_name + ".csv",
        "text/csv",
        key='download-csv'
        )
except:
    pass