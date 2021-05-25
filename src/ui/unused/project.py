import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import datetime
import time

#Heat Map and Bar Chart Visualization

#Resource: https://towardsdatascience.com/how-to-build-interactive-dashboards-in-python-using-streamlit-1198d4f7061b

#In this Visualization we display the VARES patient data at a state level over time. We show the total sum of vaccine counts at each date and at which state of the Dataset. We also incorperate the option to view deaths from vaccines over time. 

#We observe the values as cumulative sums over the time range of 2021-01-01 00:00:00 to 2021-03-19 00:00:00



#Import the dataset 
st.title('COVID-19 VARES Vaccine Visualizations \n ECS 171 Final Project')

path = ('df_state.csv')
@st.cache(allow_output_mutation=True)

def load_data():
    data = pd.read_csv(path)
    #data['date'] = pd.to_datetime(data['date'],format='%m/%d/%Y' ).dt.strftime('%Y-%m-%d')
    return data

df = load_data()
st.write(df)

########## pick counts or deaths

option = st.selectbox(
     'Metric to Observe',
     ('counts', 'died'))

st.write('You selected:', option)

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

st.markdown( str(state_name_input[0:len(state_name_input)]) + " daily vaccine doses from 1st Jan 2021")
st.bar_chart(temp[[option]])


######
# Start date
date = datetime.date(2021,1,1)


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
        get_line_color=[255,0,0],
        tooltip=option,
    )


# Create the deck.gl map
r = pdk.Deck(
    layers=[covidLayer],
    initial_view_state=view,
    map_style="mapbox://styles/mapbox/light-v10"
)

# Create a subheading to display current date
subheading = st.subheader("")


# Render the deck.gl map in the Streamlit app as a Pydeck chart 
map = st.pydeck_chart(r)

#iterate for the 77 days 
for i in range(0, 77, 1):
    # Increment day by 1
     
    date += datetime.timedelta(days=1)

    # Update data in map layers
        
    covidLayer.data = df[df['date'] == date.isoformat()]

    # Update the deck.gl map
    r.update()

    # Render the map
    map.pydeck_chart(r)

    # Update the heading with current date
    subheading.subheader("%s on : %s" % (option, date.strftime("%B %d, %Y")))
    
    # wait 0.1 second before go onto next day
    time.sleep(0.3)


