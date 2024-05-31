import datetime as dt
import requests
import pydeck as pdk
import streamlit as st
from PIL import Image
import io

API_URL = 'http://localhost:8000/calculate_change'

# Enter "streamlit run Deforestation_Calculator.py" in the terminal to run it locally.
# TODO: Functionality to allow the user to select the area on the map.

st.set_page_config(
    page_title="Deforestation Tracker",
    page_icon="🌳",
)

st.sidebar.markdown("""
    # Sidebar Placeholder
    """)


st.markdown('''
# Deforestation Tracker
Enter the the coordinates below and see how the forest coverage has changed in the area of interest.
''')

col1, col2, col3 = st.columns(3)
latitude_input = float(col1.text_input('Latitude', '-3.04361'))
longitude_input = float(col2.text_input('Longitude', '-60.01282'))
factors = [100, 50, 25, 10, 5, 4, 3, 2, 1]
square_size_options = [5.12 * factor for factor in factors]
square_size = col3.selectbox('Side Length of the Square in km', square_size_options)

col3, col4, col5 = st.columns(3)
start_timeframe = col3.date_input('Start of Timeframe', dt.datetime(2021, 1, 1))
end_timeframe = col4.date_input('End of Timeframe')
sample_number = col5.number_input('Number of Samples', 1)

view_state = pdk.ViewState(
    longitude=longitude_input,
    latitude=latitude_input,
    zoom=3.5
)

data = [
    {"position": [longitude_input, latitude_input], "name": "Location of Interest"},
]

half_side_length = float(square_size) / 2 / 110.574

square_coords = [
    [longitude_input - half_side_length, latitude_input - half_side_length],
    [longitude_input + half_side_length, latitude_input - half_side_length],
    [longitude_input + half_side_length, latitude_input + half_side_length],
    [longitude_input - half_side_length, latitude_input + half_side_length],
    [longitude_input - half_side_length, latitude_input - half_side_length]
]

polygon_data = [{
    "polygon": square_coords,
    "name": "Deforestation Area"
}]

polygon_layer = pdk.Layer(
    'PolygonLayer',
    data=polygon_data,
    get_polygon='polygon',
    get_fill_color='[230, 184, 109, 140]',
    # get_line_color='[255, 255, 255]',
    pickable=True,
    extruded=False
)

st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/satellite-v9',
        initial_view_state=view_state,
        layers=[polygon_layer], #  point_layer,
        tooltip={"text": "{name}"}
    ))

params = {
        'start_timeframe': start_timeframe,
        'end_timeframe': end_timeframe,
        'longitude': longitude_input,
        'latitude': latitude_input,
        'sample_number': sample_number,
        'square_size' : square_size
    }

st.markdown("""
    Here are the parameters that are going to get fed to our model API:
""")
st.json(params)

if st.button('Calculate Change') and all(params.values()):
    response = requests.get(url=API_URL, params=params, timeout=5)
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

col1, col2 = st.columns(2)
with col1:
    st.image("./images/before_resized.png", caption="Before")
with col2:
    st.image("./images/after_resized.png", caption="After")
