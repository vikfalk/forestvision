import datetime as dt
import requests
import pydeck as pdk
import streamlit as st

PREDICTION_URL = 'https://taxifare.lewagon.ai/predict'
PREDICTION_URL = 'http://127.0.0.1:8000/calculate_change'

# TODO: Put the pointer yourself
# TODO: Make the marker to scale
# TODO: Make it a dropdown with multiples of 512 * 10m

st.markdown('''
# Deforestation Tracker
Enter the the coordinates below and see how
''')

col1, col2, col3 = st.columns(3)
latitude_input = float(col1.text_input('Latitude', '-3.04361'))
longitude_input = float(col2.text_input('Longitude', '-60.01282'))
square_size = float(col3.text_input('Side Length of the Square in km', '10'))

# location_input = st.text_input('Location', 'Optionally search by Location Name').lower()
# if location_input:
#     location_coordinates = get_coordinates(location_input)
#     print("hello")

col3, col4, col5 = st.columns(3)
start_timeframe = col3.date_input('Start of Timeframe', dt.datetime(2021, 1, 1))
end_timeframe = col4.date_input('End of Timeframe')
sample_number = col5.number_input('Number of Samples', 1)

# Map Functionality
view_state = pdk.ViewState(
    longitude=longitude_input,
    latitude=latitude_input,
    zoom=3
)

data = [
    {"position": [longitude_input, latitude_input], "name": "Location of Interest"},
]

point_layer = pdk.Layer(
    'ScatterplotLayer',
    data=data,
    get_position='position',
    radius_scale=10000,
    radius_min_pixels=10,
    get_fill_color=[255, 219, 88],
    pickable=True
)

st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/satellite-v9',
        initial_view_state=view_state,
        layers=[point_layer],
        tooltip={"text": "{name}"}
    ))

params = {
        'start_timeframe': start_timeframe,
        'end_timeframe': end_timeframe,
        'longitude': longitude_input,
        'latitude': latitude_input,
        'sample_number': sample_number
    }

st.markdown("""
    Here are the parameters that are going to get fed to our model API:
""")
st.json(params)

# Prediction Functionality
if st.button('Calculate Change') and all(params.values()):
    response = requests.get(url=PREDICTION_URL, params=params, timeout=5)
    url = PREDICTION_URL
    response = requests.get(url, params=params, timeout=5)
    prediction_json = response.json()
    prediction = round(prediction_json["change"], 2)
    prediction_string = format(prediction, '.2f')
    st.markdown(f"""
                In the specified plot of land,
                the rainforest area was reduced by {prediction_string} %
                between {start_timeframe} and {end_timeframe}.
                """)
else:
    st.markdown("""
                Please press the button.
                """)

# enter "streamlit run deforestation_app.py" in the terminal to run it locally.
