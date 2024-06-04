from PIL import Image
import numpy as np
import datetime as dt
import requests
import pydeck as pdk
import streamlit as st
from PIL import Image
import io

# INSTRUCTION:
# Enter "# Enter "streamlit run Deforestation_Calculator.py" in the terminal to run it locally." in the terminal to run it locally.

st.set_page_config(
    page_title="Deforestation Tracker",
    page_icon="🌳",
)

# st.sidebar.markdown("""
#     # Sidebar Placeholder
#     """)

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
start_timeframe = col3.date_input('Start of Timeframe', dt.datetime(2020, 6, 15))
end_timeframe = col4.date_input('End of Timeframe', dt.datetime(2024, 5, 30))
sample_number = col5.number_input('Number of Samples', 1)

# Assembled User Input Parameters
params = {
        'start_timeframe': start_timeframe,
        'end_timeframe': end_timeframe,
        'longitude': longitude_input,
        'latitude': latitude_input,
        'sample_number': sample_number,
        'square_size' : square_size
}

#  Map Stuff
# view_state = pdk.ViewState(
#     longitude=longitude_input,
#     latitude=latitude_input,
#     zoom=3.5
# )

# data = [
#     {"position": [longitude_input, latitude_input], "name": "Location of Interest"},
# ]

# half_side_length = float(square_size) / 2 / 110.574

# square_coords = [
#     [longitude_input - half_side_length, latitude_input - half_side_length],
#     [longitude_input + half_side_length, latitude_input - half_side_length],
#     [longitude_input + half_side_length, latitude_input + half_side_length],
#     [longitude_input - half_side_length, latitude_input + half_side_length],
#     [longitude_input - half_side_length, latitude_input - half_side_length]
# ]

# polygon_data = [{
#     "polygon": square_coords,
#     "name": "Deforestation Area"
# }]

# polygon_layer = pdk.Layer(
#     'PolygonLayer',
#     data=polygon_data,
#     get_polygon='polygon',
#     get_fill_color='[230, 184, 109, 140]',
#     pickable=True,
#     extruded=False
# )

# st.pydeck_chart(pdk.Deck(
#         map_style='mapbox://styles/mapbox/satellite-v9',
#         initial_view_state=view_state,
#         layers=[polygon_layer], #  point_layer,
#         tooltip={"text": "{name}"}
#     ))

# API Stuff
st.title("Fetch Image from Satellite Using User Inputs")

# cloud_base_url = "https://deforestation-tracker-llzimbumzq-oe.a.run.app"  # buster image
cloud_base_url = "https://defotra-llzimbumzq-oe.a.run.app" # slim image
local_base_url = "http://localhost:8080"
param_api_options = [
    f"{local_base_url}/get_image_from_satellite_with_params",
    f"{cloud_base_url}/get_image_from_satellite_with_params",
]
param_api_url = st.selectbox('API Selection', param_api_options)

if st.button("Test Input Sensitive API"):
    response = requests.get(url=param_api_url, params=params, timeout=60)

    segmented_image_list = response.json().get("segmented_image_list")
    image_array = np.array(segmented_image_list, dtype=np.uint8)

    original_image_array_list = response.json().get("original_image_list")
    original_image_array = np.array(original_image_array_list, dtype=np.float32).reshape((512, 512, 3))

    st.image(image_array, caption="Segmented Image")
    st.image(original_image_array, caption="Original Image")

# st.markdown("""
#     ## User Input Parameters
#     Here are the parameters that are going to get fed to our model API… NOT.

#     Actually the date format will come out as as a string with the particular
#     format "YYYY-MM-DD".
# """)
# st.write(params)
