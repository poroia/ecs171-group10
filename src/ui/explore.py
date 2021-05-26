import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import os
from datetime import datetime

from ui import utils

# correctly establishes base path if you run app.py
# or this script for debugging purposes 
ROOT_RELATIVE_PATH = "./"

# Heat Map and Bar Chart Visualization

# Resource: https://towardsdatascience.com/how-to-build-interactive-dashboards-in-python-using-streamlit-1198d4f7061b

# In this Visualization we display the VAERS patient data at a state level over time. We show the total sum of vaccine counts at each date and at which state of the Dataset. We also incorperate the option to view deaths from vaccines over time. 

# We observe the values as cumulative sums over the time range of 2021-01-01 00:00:00 to 2021-03-19 00:00:00

def main(state):

    st.title("Explore")

    st.write("Let's take a look at some general data:")

    #Import the dataset 
    @st.cache(allow_output_mutation=True)

    def load_data():
        data = pd.read_csv(os.path.join(ROOT_RELATIVE_PATH, './prototype/data/df_state.csv'))
        #data['date'] = pd.to_datetime(data['date'],format='%m/%d/%Y' ).dt.strftime('%Y-%m-%d')
        return data.dropna()

    df = load_data()
    # st.write(df)

    ########## pick counts or deaths

    option = st.selectbox(
        'Choose a metric to observe',
        ('number of vaccines', 'number of deaths after the vaccine'))

    ######### 

    subset_data = df

    # Toggle of different States
    state_name_input = st.multiselect(
    'State',
    df.groupby('state').count().reset_index()['state'].tolist(), default=["CA"]) #Creates list of all the names, sets default to CA

    # by country name
    if len(state_name_input) > 0:
        subset_data = df[df['state'].isin(state_name_input)]
    
    ###### BAR CHART

    temp = df.set_index("date")
    temp = temp[temp['state'].isin(state_name_input)].groupby('date').sum()

    states_list = state_name_input[0:len(state_name_input)]
    st.markdown(f"{', '.join(states_list)} daily vaccine doses from 1st Jan 2021")
    st.bar_chart(temp[[encode_option(option)]])


    ######

    # Set viewport for the deckgl map
    view = pdk.ViewState(latitude=34.0902, longitude=-95.500000, zoom=3)

    # Create the scatter plot layer
    covidLayer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        pickable=False,
        opacity=0.1,
        stroked=True,
        filled=True,
        radius_scale=200,
        radius_min_pixels=9,
        radius_max_pixels=20,
        line_width_min_pixels=1,
        get_position=["longitude", "latitude"],
        get_radius=option,
        get_fill_color=[252, 136, 3],
        get_line_color=[255, 0, 0],
        tooltip=option,
    )


    # Create the deck.gl map
    r = pdk.Deck(
        layers=[covidLayer],
        initial_view_state=view,
        map_style="mapbox://styles/mapbox/light-v10"
    )

    # Create a subheading to display current date
    st.subheader(f"{option} on:")

    date = st.slider("",
        value=datetime(2021, 1, 1), 
        min_value=datetime(2021, 1, 1), 
        max_value=datetime(2021, 3, 19))
    
    # Render the deck.gl map in the Streamlit app as a Pydeck chart 
    map = st.pydeck_chart(r)
    
    # Update data in map layers
    covidLayer.data = df[df['date'] == date.strftime('%Y-%m-%d')]

    # Update the deck.gl map
    r.update()

    # Render the map
    map.pydeck_chart(r)
    

def encode_option(option):
    return 'counts' if option == 'number of vaccines' else 'died'


# Only used if this file is ran directly
# Useful for developing with hot reloading
if __name__ == "__main__":
    ROOT_RELATIVE_PATH = "./"
    from session import _get_state
    state = _get_state()
    state.navigation = 'Explore'

    main(state)

    utils.main_debug_helper(state)
