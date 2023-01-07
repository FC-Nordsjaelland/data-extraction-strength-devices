#%%
import pandas as pd
import io
import matplotlib.pyplot as plt
import datetime
from datetime import time
import streamlit as st
from st_aggrid import AgGrid
# warnings.filterwarnings("ignore")
import numpy as np

#%%

st.set_page_config(page_title="Strength data summary", layout ='wide')
st.sidebar.markdown("## Strength data summary")

# st.sidebar.header("**Functionality**")
# st.sidebar.markdown("- The app accepts multiple excel files and produces one output that aggregates all the data into one file")
# st.sidebar.markdown("- The aggregated data columns are as follows: (Name, Device, Team, Date, Max left, Max right, Comment)")
# st.sidebar.markdown("- After the user uploads the files, a table is shown below with the preview of the output, a user can then decide to modify the time interval in order to capture the entire testing session")
# st.sidebar.markdown("- The time interval functionality's goal is to capture the data for one player within multiple files but also to get rid of the files produced by mistake during testing")
# st.sidebar.markdown("- The user can download the output as seen in the preview data table")

st.title("Strength data summary (01/23 update)")

# st.header("**Instruction**")
# st.markdown("1) Upload the excel files to preprocess")
# st.markdown("2) Choose a testing date (by default set to the earliest one found in the excel files)")
# st.markdown("3) Choose the time of testing and the interval of acceptance - **multiple files for one player will be aggregated within the specified time interval**")
# st.markdown("4) Select the output name of the downloaded file (default: output.csv)")  
# st.markdown("")


def percentage_difference(col1, col2):
    return (abs(col1 - col2)/((col1 + col2)/2) * 100)

def flatten_xlsx(path):

    data = pd.read_excel(path, header=None)
    try:
        data.reset_index()
        metadata = data[[0,1]]
        date = metadata[metadata[0]=='Date'][1][0].split()[0]
        year = metadata[metadata[0]=='Date'][1][0].split()[0].split(".")[-1]
        test = metadata[metadata[0]=='Exercise'][1].values[0]
        measure = 'Newtons'
        team = metadata[metadata[0]=='Team'][1].values[0]
        name = metadata[metadata[0]=='Name'][1].values[0]

       
        
        right_col_data = data[[4,5,6,7,8]]

        nrs = right_col_data[right_col_data[7]=='NRS (Pain during Test)'][8].values[0]
        season_split = right_col_data[right_col_data[7]=='Season Period'][8].values[0].split()
        term = season_split[1]
        season_period = season_split[0]
        test_type = right_col_data[right_col_data[7]=='Test Type'][8].values[0]


        dob = right_col_data[right_col_data[4]=='Date of birth (dd/mm/yyyy)'][5].values[0]
        gender = right_col_data[right_col_data[4]=='Gender'][5].values[0]
        height = right_col_data[right_col_data[4]=='Height'][5].values[0]
        weight = right_col_data[right_col_data[4]=='Weight'][5].values[0]
        position = right_col_data[right_col_data[4]=='Position'][5].values[0]
        id = right_col_data[right_col_data[4]=='ID'][5].values[0]
            
        try:
            lever_knee = right_col_data[right_col_data[4]=='Hip-Knee Lever'][5].values[0]
            lever_groin = right_col_data[right_col_data[4]=='Hip-Ankle Lever'][5].values[0]
        except:
            lever_knee = np.nan
            lever_groin = np.nan
        
        try:
            tests = data[[1,2]][7::]
            tests.columns = ['Left', 'Right']
            tests = tests.astype("float")
            left_max = tests['Left'].max()
            right_max = tests["Right"].max()
        except:
            left_max = np.nan
            right_max = np.nan
    

        x = [[name, id, gender, dob, np.nan, height, weight, lever_knee, lever_groin, team, position, date, year, term, season_period, test_type, test, "Right", measure, right_max, nrs, id + test + "".join(date.split("."))],
            [name, id, gender, dob, np.nan, height, weight, lever_knee, lever_groin, team, position, date, year, term, season_period, test_type, test, "Left", measure, left_max, nrs, id + test + "".join(date.split("."))]]
    except:
        x = [[name, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, team, np.nan, date, year, term, season_period, test_type, test, "Right", measure, right_max, nrs, np.nan],
            [name, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, team, np.nan, date, year, term, season_period, test_type, test, "Left", measure, left_max, nrs, np.nan]]

    return x

#%%

def preprocess(uploaded_files):

    # file_names = glob.glob(os.path.join(dir_path, "*.xlsx"))

    players_data = []
    for file in uploaded_files:
        one_player = flatten_xlsx(file)
        one_player_right = one_player[0]
        one_player_left = one_player[1]
        players_data.append(one_player_right)
        players_data.append(one_player_left)

    
    df = pd.DataFrame(players_data, columns=['Name', 'id', 'Gender', 'DoB', 'age', 'height', 'body_mass', 'lever_knee', 'lever_groin', 'team', 'position', 'date', 'year', 'term', 'season_period', 'type', 'test', 'leg', 'measure', 'strength', 'NRS', 'test_id'])
    df = df.dropna(subset=['strength'])
    df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y', errors='coerce').fillna('0000-00-00')
    df['DoB'] = pd.to_datetime(df['DoB'], format='%Y.%m.%d', errors='coerce').fillna('0000-00-00')
    df['age'] = ((df['date'] - df['DoB']) / pd.Timedelta(days=365)).astype(int)
    df['age'] = df['age'].apply(lambda x: 0 if x > 50 else x)
    df['date'] = df['date'].dt.strftime('%m-%d-%y')
    df['DoB'] = df['DoB'].dt.strftime('%Y-%m-%d')
        
    final_df = df.sort_values(by=['Name'])
    final_df['strength'] = final_df['strength'].round(decimals=1)
    final_df = final_df.reset_index(drop=True)

    final_df = final_df[['Name', 'id', 'Gender', 'DoB', 'age', 'height', 'body_mass', 'lever_knee', 'lever_groin', 'team', 'position', 'date', 'year', 'term', 'season_period', 'type', 'test', 'leg', 'measure', 'strength', 'NRS', 'test_id']]
    return final_df

def convert_df(df):
    return df.to_csv(index=False, date_format='%m.%d.%Y').encode('utf-8')


    
uploaded_files = st.file_uploader("Upload xlsx files below", type="xlsx", accept_multiple_files=True)
    
if uploaded_files is not None:
    try:
        df = preprocess(uploaded_files=uploaded_files)
        st.write("")
        st.write("")
        st.write("")    
        st.write("")
        AgGrid(df, fit_columns_on_grid_load=True)
    except:
        pass

    try:
        csv = convert_df(df)
        st.download_button(
        "Press to Download",
        csv,
        "output.csv",
        "text/csv",
        key='download-csv'
        )
    except:
        pass

    #     st.write("")
    #     st.write("")
    #     with st.form(key='my_form2'):
    #         test = st.radio("Choose a test to visualize", ("NORDIC", "GROIN"))
    #         sorter = st.radio("Sort the values by", ("Max right", "Max left", "Mean strength"))
    #         if sorter == 'Max right':
    #             df = df.sort_values(by=['Max right'])
    #         elif sorter == 'Max left':
    #             df = df.sort_values(by=['Max left'])
    #         elif sorter == 'Mean strength':
    #             df = df.sort_values(by=['Mean strength'])
    #         st.form_submit_button(label='Visualize')

            
    #     if test == 'NORDIC':
    #         df = df[df['Device'].str.startswith("NORDIC")]

    #     elif test == 'GROIN':
    #         df = df[df['Device'].str.startswith("GROIN")]

    #     try:

    #         ax = df.plot(x='Name', y=['Max left', 'Max right'], kind='bar', width=0.6)

    #         plt.xticks(rotation=75)
    #         plt.xlabel("")
    #         plt.ylabel("Strength (Newtons)")
    #         plt.rcParams.update({'font.size': 6})
    #         ax.bar_label(ax.containers[0], df['Percentage difference'])
    #         if test == 'NORDIC':
    #             plt.title("Hamstring Strength")

    #         elif test == 'GROIN':
    #             plt.title("Adductor Strength")

    #         plt.legend(fontsize=7)

    #         st.pyplot(fig=plt)

    #         plt.subplots_adjust(bottom=0.30)
    #         fn = 'scatter.png'
    #         plt.savefig(fn, dpi=1000)
    #         with open(fn, "rb") as img:
    #             btn = st.download_button(
    #                 label="Press to Download",
    #                 data=img,
    #                 file_name=fn,
    #                 mime="image/png"
    #         )
    #     except:
    #         pass
    # except:
    #     pass

# %%
