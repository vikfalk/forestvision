from PIL import Image
import numpy as np
import datetime as dt
import requests
import pydeck as pdk
import streamlit as st

# INSTRUCTION:
# Enter "# Enter "streamlit run Deforestation_Calculator.py" in the terminal to run it locally." in the terminal to run it locally.

st.set_page_config(
    page_title="Deforestation Tracker",
    page_icon="🌳",
)

st.sidebar.markdown("""
    # Sidebar Placeholder
    """)

st.markdown('''
# Deforestation Tracker
''')

col1, col2, col3 = st.columns(3)
latitude_input = float(col1.text_input('Latitude', '-8.48638'))
longitude_input = float(col2.text_input('Longitude', '-55.26209'))
factors = [100, 50, 25, 10, 5, 4, 3, 2, 1]
square_size_options = [5.12 * factor for factor in factors]
square_size = col3.selectbox('Side Length of the Square in km', square_size_options)

col3, col4, col5 = st.columns(3)
start_timeframe = col3.date_input('Start of Timeframe', dt.datetime(2021, 1, 1))
end_timeframe = col4.date_input('End of Timeframe')
sample_number = col5.number_input('Number of Samples', 1)

#  Map Stuff
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
    pickable=True,
    extruded=False
)

st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/satellite-v9',
        initial_view_state=view_state,
        layers=[polygon_layer], #  point_layer,
        tooltip={"text": "{name}"}
    ))

# API Stuff
st.title("Fetch Image from Satellite Using User Inputs")
params = {
        'start_timeframe': start_timeframe,
        'end_timeframe': end_timeframe,
        'longitude': longitude_input,
        'latitude': latitude_input,
        'sample_number': sample_number,
        'square_size' : square_size
}
param_api = "http://localhost:8000/get_image_from_satellite_with_params"
if st.button("Test Input Sensitive API"):
    response = requests.get(url=param_api, params=params, timeout=10)
    image_list = response.json().get("image_list")
    image_array = np.array(image_list, dtype=np.uint8)
    image =  Image.fromarray(image_array)
    if image:
            st.image(image, caption="Fetched Image")

st.markdown("""
    # Testing Section
    ## User Input Parameters
    Here are the parameters that are going to get fed to our model API… NOT.

    Actually the date format will come out as as a string with the particular
    format "YYYY-MM-DD".
""")
st.write(params)

st.markdown("""
    ## Image Fetcher From API Without User Inputs
""")
api_options = [
    "http://localhost:8000/get_image",
    "http://localhost:8000/get_complex_image",
    "http://localhost:8000/get_image_from_model",
    "http://localhost:8000/get_image_from_satellite"
]
api_url = st.selectbox('API Selection', api_options)

if st.button("Test API"):
    response = requests.get(api_url, timeout=10)
    image_list = response.json().get("image_list")
    image_array = np.array(image_list, dtype=np.uint8)
    image =  Image.fromarray(image_array)
    if image:
            st.image(image, caption="Fetched Image")

# Image Depiction Stuff
st.markdown("""
    ## Image Segmentation Example (File Saved Locally in Frontend Repo)
""")
col1, col2 = st.columns(2)
col1.image("./images/before_resized.png", caption="Before")
col2.image("./images/after_resized.png", caption="After")
