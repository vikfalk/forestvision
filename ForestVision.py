import io
import base64
import requests
import numpy as np
import pydeck as pdk
from PIL import Image
import datetime as dt
import streamlit as st
from processing.frontend_processing import smooth_and_vectorize

CLOUD_URL = "https://forest-vision-ai-llzimbumzq-oe.a.run.app/get_satellite_images"
LOCAL_URL = "http://localhost:8080/get_satellite_images"

def base64_to_numpy(img_b64):
    img_bytes = io.BytesIO(base64.b64decode(img_b64))
    img_array = np.load(img_bytes)
    return img_array

def process_forest_loss_calculation(latitude, longitude, start_date, end_date, api_url):
    params = {
        'start_timeframe': start_date,
        'end_timeframe': end_date,
        'longitude': longitude,
        'latitude': latitude,
        'sample_number': 2,
        'send_orginal_images': 'True'
    }

    try:
        with st.session_state.input_spinner_placeholder, st.spinner('Requesting satellite images from Sentinel-2 L2A API...'):
            response = requests.get(
                url=api_url,
                params=params,
                timeout=60)

        # Process start images
        with st.session_state.input_spinner_placeholder, st.spinner('Processing images and calculating metrics...'):
            # Dates
            date_list_loaded = response.json().get("date_list_loaded")

            # Segmented Images
            segmented_images_b64 = response.json().get("segmented_img_list")
            segmented_image_arrays = [base64_to_numpy(img_b64) for img_b64 in segmented_images_b64]
            segmented_images = [Image.fromarray(image) for image in segmented_image_arrays]

            # Original Satellite Images
            original_images_b64 = response.json().get("original_img_list")
            original_image_arrays = [base64_to_numpy(img_b64) for img_b64 in original_images_b64]
            original_images = [Image.fromarray(image).convert('RGBA') for image in original_image_arrays]

            # Assign the session states and variables for first image
            st.session_state.start_mask = segmented_image_arrays[0]
            start_mask_image = segmented_images[0]

            st.session_state.start_sat = original_image_arrays[0]
            start_sat_image = original_images[0]

            start_mask_vector = smooth_and_vectorize(segmented_image_arrays[0], 9, '#00B272', 0.5).convert('RGBA')
            st.session_state.start_vector_overlay = start_mask_vector

            start_overlay = Image.alpha_composite(start_sat_image, start_mask_vector)
            st.session_state.start_overlay = start_overlay

            start_forest_cover_percent = round(((np.count_nonzero(segmented_image_arrays[0] != 0) / segmented_image_arrays[0].size) * 100), 1)
            st.session_state.start_forest_cover_percent = start_forest_cover_percent
            st.session_state.start_forest_cover_percent_int = int(start_forest_cover_percent)

            # Assign the session states and variables for last image
            st.session_state.end_mask = segmented_image_arrays[-1]
            end_mask_image = segmented_images[-1]

            st.session_state.end_sat = original_image_arrays[-1]
            end_sat_image = original_images[-1]

            end_mask_vector = smooth_and_vectorize(segmented_image_arrays[-1], 9, '#00B272', 0.5).convert('RGBA')
            st.session_state.end_vector_overlay = end_mask_vector

            end_overlay = Image.alpha_composite(end_sat_image, end_mask_vector)
            st.session_state.end_overlay = end_overlay

            end_forest_cover_percent = round(((np.count_nonzero(segmented_image_arrays[-1] != 0) / segmented_image_arrays[-1].size) * 100), 1)
            st.session_state.end_forest_cover_percent = end_forest_cover_percent
            st.session_state.end_forest_cover_percent_int = int(end_forest_cover_percent)

            # Image info
            start_info = date_list_loaded[0]
            end_info = date_list_loaded[-1]
            st.session_state.info_intro = 'The closest cloud-free images to your desired start and end dates are from:'
            st.session_state.start_info = start_info
            st.session_state.end_info = end_info

            # Calculated overlay
            total_overlay_calculated_array = segmented_image_arrays[0] - segmented_image_arrays[-1]
            total_overlay_calculated_array = smooth_and_vectorize(total_overlay_calculated_array, 9, '#994636', 0.5)  # color of deforested forest
            total_overlay_calculated = total_overlay_calculated_array.convert('RGBA')
            total_calculated_overlay = Image.alpha_composite(end_overlay, total_overlay_calculated)
            st.session_state.total_calculated_overlay = total_calculated_overlay

            # Total metrics
            total_deforestation = round((100 - (end_forest_cover_percent / start_forest_cover_percent) * 100), 1)
            st.session_state.total_deforestation = total_deforestation

            # Start metrics
            # Forest cover and forest loss in percent
            start_forest_cover_percent = round(((np.count_nonzero(segmented_image_arrays[0] != 0) / segmented_image_arrays[0].size) * 100), 1)
            st.session_state.start_forest_cover_percent = start_forest_cover_percent
            st.session_state.start_forest_cover_percent_int = int(start_forest_cover_percent)

            # Forest cover in hectares
            start_forest_cover_ha = (start_forest_cover_percent / 100) * 2621.44
            st.session_state.start_forest_cover_ha = start_forest_cover_ha

            # Annual CO2 absorption in tons
            start_annual_co2 = start_forest_cover_ha * 11
            st.session_state.start_annual_co2 = start_annual_co2

            # End metrics
            # Forest cover and forest loss in percent
            end_forest_cover_percent = round(((np.count_nonzero(segmented_image_arrays[-1] != 0) / segmented_image_arrays[-1].size) * 100), 1)
            st.session_state.end_forest_cover_percent = end_forest_cover_percent
            st.session_state.end_forest_cover_percent_int = int(end_forest_cover_percent)

            # Forest cover in hectares
            end_forest_cover_ha = (end_forest_cover_percent / 100) * 2621.44
            st.session_state.end_forest_cover_ha = end_forest_cover_ha

            # Annual CO2 absorption in tons
            end_annual_co2 = end_forest_cover_ha * 11
            st.session_state.end_annual_co2 = end_annual_co2

            # Total metrics
            # Forest loss in hectares
            total_deforestation_ha = round((start_forest_cover_ha - end_forest_cover_ha), 1)
            st.session_state.total_deforestation_ha = total_deforestation_ha

            # Equivalent of hectare loss in terms of Le Wagon loft space (187 m²)
            loft_loss = total_deforestation_ha * 10000 / 187
            st.session_state.loft_loss = loft_loss

            # Equivalent of hectare loss in terms of Berghains
            berg_loss = total_deforestation_ha * 10000 / 2838
            st.session_state.berg_loss = berg_loss

            # Environmental impact (CO2 loss), assumption: 11 tons per hectare
            annual_co2_loss = start_annual_co2 - end_annual_co2
            st.session_state.annual_co2_loss = annual_co2_loss

            # Equivalent of CO2 loss in terms of annual per capita CO2 emission, assumption: 5 tons per capita
            human_co2_cons_equ = annual_co2_loss / 4.7
            st.session_state.human_co2_cons_equ = human_co2_cons_equ

            # Equivalent of CO2 loss in kg of beef, assumption: 0.1 tons per kg
            beef_equ = annual_co2_loss / 0.1
            st.session_state.beef_equ = beef_equ

            # Set session states for UI updates
            st.session_state.expander_open = True
            st.session_state.output = True
            st.session_state.zoom = 12.5

    except (requests.RequestException, ValueError):
        with st.session_state.input_spinner_placeholder:
            st.markdown('No suitable image found near your start date. Please try another.')

st.set_page_config(
    page_title="ForestVision",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if 'zoom' not in st.session_state:
    st.session_state.longitude_input = -55.26000
    st.session_state.longitude_input = -8.49000
    st.session_state.end_timeframe = dt.datetime(2024, 1, 1)
    st.session_state.start_timeframe = dt.datetime(2021, 1, 1)
    st.session_state.zoom = 1
    st.session_state.input_spinner_placeholder = None

col1, title_col, col3 = st.columns([2, 9.5, 2])

with title_col:
    st.markdown("<h1 style='text-align: center; font-family: FreeMono, monospace;font-size: 110px; color: #FFFFFF;'>ForestVision.AI</h1>", unsafe_allow_html=True)

    # Add custom CSS for the horizontal line
    st.markdown("""
        <style>
        .custom-divider {
            border-top: 1.5px solid #994636; /* Change the color code to your desired color */
            margin: 0px 0; /* Adjust the spacing around the line if needed */
        }
        </style>
        """, unsafe_allow_html=True)

    # Use the custom class in a markdown divider
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    st.markdown("<p style='text-align: center; alphafont-size: 16px; opacity: 1; color: #FFFFFF;'>Track forest area change of an area using real-time satellite data by inputting coordinates on the left or choosing an example on the right.</h1>", unsafe_allow_html=True)

col1, col2,col3 = st.columns([5, 5, 5])
with col2:
    st.session_state.input_spinner_placeholder = st.empty()

input_col1, map_col, example_col = st.columns([4, 20, 4])
with input_col1:
    st.markdown("<p style='text-align: center; font-family: FreeMono, monospace; font-size: 15px;'><b>Inputs</b></p>", unsafe_allow_html=True)
    with st.container(border=True, height = 470):

        st.session_state.latitude_input = st.text_input('Latitude', '-8.49000',
                                                        help = "Enter the longitude coordinates of your desired area of interest. Press enter to view on map.")
        st.session_state.longitude_input = st.text_input('Longitude', '-55.26000')


        start_timeframe = st.date_input('Start date', dt.datetime(2017, 6, 30),
                                        min_value=dt.datetime(2017, 1, 1),
                                        max_value= dt.datetime(2024, 12, 31),
                                        help= "Select the start and end date of your desired timeframe.")
        end_timeframe = st.date_input('End date',
                                    min_value=dt.datetime(2017, 1, 1),
                                    max_value= dt.datetime(2024, 12, 31))

        factors = [1, 2, 3, 4, 5, 10, 25, 50, 100]
        square_size_options = [5.12 * factor for factor in factors]
        labels = {val: f"{val:.2f}" for val in square_size_options}
        default_value = square_size_options[0]
        square_size = 5.12
        sample_number = 1

        params= {
            'start_timeframe': start_timeframe,
            'end_timeframe': end_timeframe,
            'longitude': st.session_state.longitude_input,
            'latitude': st.session_state.latitude_input,
            'sample_number': sample_number,
            'square_size': square_size
        }
        if st.button('View on map', use_container_width=True):
            st.session_state.latitude_input = st.session_state.latitude_input
            st.session_state.longitude_input = st.session_state.longitude_input
            st.session_state.zoom = 12.5

        if st.button("**Calculate forest loss**", use_container_width=True, type='primary', help= 'Click me to calculate deforestation.'):
            latitude = st.session_state.latitude_input
            longitude = st.session_state.longitude_input
            start_date = start_timeframe
            end_date = end_timeframe
            process_forest_loss_calculation(latitude, longitude, start_date, end_date, CLOUD_URL)

with example_col:
    st.markdown("<p style='text-align: center; font-family: FreeMono, monospace;font-size: 15px;'><b>Examples</b></p>", unsafe_allow_html=True)
    with st.container(border=True, height = 228):
        st.image('https://vikfalk.github.io/deforestation_frontend/images/brazil.png')
        if st.button('View on map   ', use_container_width=True):
            st.session_state.latitude_input = -12.11463
            st.session_state.longitude_input = -60.83938
            st.session_state.zoom = 12.5
        if st.button('Calculate ', use_container_width=True, type='primary'):
            st.session_state.latitude_input = -12.11463
            st.session_state.longitude_input = -60.83938
            st.session_state.zoom = 12.5
            st.session_state.start_timeframe = "2017-08-24"
            st.session_state.end_timeframe = "2024-04-24"

            process_forest_loss_calculation(st.session_state.latitude_input, st.session_state.longitude_input,
                                            st.session_state.start_timeframe, st.session_state.end_timeframe, CLOUD_URL)


    with st.container(border=True, height = 228):
        st.image('https://vikfalk.github.io/deforestation_frontend/images/bolivia.png')
        if st.button('View on map    ', use_container_width=True):
            st.session_state.latitude_input = -18.39
            st.session_state.longitude_input = -59.72
            st.session_state.zoom = 12.5
        if st.button('Calculate      ', use_container_width=True, type='primary'):
            st.session_state.latitude_input = -18.39
            st.session_state.longitude_input = -59.72
            st.session_state.zoom = 12.5
            st.session_state.start_timeframe = "2017-08-24"
            st.session_state.end_timeframe = "2024-04-24"

            process_forest_loss_calculation(st.session_state.latitude_input, st.session_state.longitude_input,
                                            st.session_state.start_timeframe, st.session_state.end_timeframe, CLOUD_URL)

# Map
view_state = pdk.ViewState(
    longitude=float(st.session_state.longitude_input),
    latitude=float(st.session_state.latitude_input),
    zoom=st.session_state.zoom
)

half_side_length = float(square_size) / 2 / 110.574

square_coords = [
    [float(st.session_state.longitude_input) - half_side_length, float(st.session_state.latitude_input) - half_side_length],
    [float(st.session_state.longitude_input) + half_side_length, float(st.session_state.latitude_input) - half_side_length],
    [float(st.session_state.longitude_input) + half_side_length, float(st.session_state.latitude_input) + half_side_length],
    [float(st.session_state.longitude_input) - half_side_length, float(st.session_state.latitude_input) + half_side_length],
    [float(st.session_state.longitude_input) - half_side_length, float(st.session_state.latitude_input) - half_side_length]
]

polygon_data = [{
    "polygon": square_coords,
    "name": "Deforestation Area"
}]


polygon_layer = pdk.Layer(
    'PolygonLayer',
    data=polygon_data,
    get_polygon='polygon',
    get_fill_color=[153, 70, 54, 40],
    get_line_color=[153, 70, 54, 100],
    get_line_width=10,
    pickable=True,
    extruded=False
)

# BOUNDS = square_coords

with map_col:
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/satellite-v9',
        initial_view_state=view_state,
        layers=[polygon_layer],
        tooltip=False
    ))

st.markdown(' ')

if 'output' not in st.session_state:
    st.session_state.output = False

if st.session_state.output:
    with st.container():
        col1, col2, col3 = st.columns([11, 3, 11])
        with col1:
            st.markdown('---')
        with col2:
            st.markdown("<p style='text-align: center; font-family: FreeMono, monospace; font-size: 30px;'><b>Output</b></p>", unsafe_allow_html=True)
        with col3:
            st.markdown('---')

    with st.container(border = True):
            st.markdown(f"**Summary:** {st.session_state.info_intro} {st.session_state.start_info} and {st.session_state.end_info}. This area witnessed a {round(st.session_state.total_deforestation)}% decrease in forest cover over this timeframe.")

    with st.container(border = False):
        sat_col, forest_col, overlay_col, metrics_col = st.columns([3.2, 3.2, 7, 6])

        with sat_col:
            st.markdown("<p style='text-align: left; font-family: FreeMono, monospace; font-size: 18px;'><b>Start date</b></p>", unsafe_allow_html=True)
            st.image(st.session_state.start_sat, use_column_width=True, caption='Satellite image')

            st.markdown("<p style='text-align: left; font-family: FreeMono, monospace; font-size: 18px;'><b>End date</b></p>", unsafe_allow_html=True)
            st.image(st.session_state.end_sat, use_column_width=True, caption='Satellite image')

        with forest_col:
            st.markdown("<p style='text-align: left; font-family: FreeMono, monospace; color: #0E1117; font-size: 18px;'><b>Start date</b></p>", unsafe_allow_html=True)
            st.image(st.session_state.start_overlay, use_column_width=True, caption='Predicted forest area')

            st.markdown("<p style='text-align: left; font-family: FreeMono, monospace; color: #0E1117; font-size: 18px;'><b>End date</b></p>", unsafe_allow_html=True)
            st.image(st.session_state.end_overlay, use_column_width=True, caption='Predicted forest area' )

        with overlay_col:
            with st.container(border=True, height = 620):
                st.markdown("<p style='text-align: center; font-family: FreeMono, monospace; font-size: 22px;'><b>Total Forest Change</b></p>", unsafe_allow_html=True)
                st.image(st.session_state.total_calculated_overlay)
                st.image('https://vikfalk.github.io/deforestation_frontend/images/legend.png')

        with metrics_col:
            with st.container(border=True, height = 620):
                st.markdown("<p style='text-align: center; font-family: FreeMono, monospace; font-size: 22px;'><b>Metrics</b></p>", unsafe_allow_html=True)

                forest_loss_percent_tab, forest_loss_ha_tab, env_tab = st.tabs(['Forest Loss (%)', 'Forest Loss (ha)', 'Enviromental Impact'])
                with forest_loss_percent_tab:
                    st.markdown('Start date forest cover')
                    st.markdown(f'<div style="display: flex; justify-content: left; align-items: center; background-color: #262730; border-radius: 10px; width: {st.session_state.start_forest_cover_percent_int}%; height: 50px; padding: 5px">'
                                f'<p style="color: white; font-size: 24px; font-weight: bold; margin: 0; width: 80%;">{st.session_state.start_forest_cover_percent:.0f}%</p>'
                                '</div>', unsafe_allow_html=True)
                    st.markdown(' ')

                    st.markdown('End date forest cover')

                    st.markdown(f'<div style="display: flex; justify-content: left; align-items: center; background-color: #262730; border-radius: 10px; width: {st.session_state.end_forest_cover_percent_int}%; height: 50px; padding: 5px">'
                                f'<p style="color: white; font-size: 24px; font-weight: bold; margin: 0; width: 80%;">{st.session_state.end_forest_cover_percent:.0f}%</p>'
                                '</div>', unsafe_allow_html=True)

                    st.markdown("###")
                    st.markdown(
                            '<h3 style="color: white; font-size: 24px;">Total change in forest cover</h3>'
                            '</div>', unsafe_allow_html=True)

                    st.markdown('<div style="display: flex; justify-content: center; align-items: center; background-color: #994636; border-radius: 10px; height: 150px; padding: 5px"; border>'
                            f'<p style="color: white; font-size: 80px; font-weight: bold; margin: 0;">- {st.session_state.total_deforestation:.0f}%</p>'
                            '</div>', unsafe_allow_html=True)

                with forest_loss_ha_tab:
                    st.markdown('Start date forest area (hectares)')
                    st.markdown(f'<div style="display: flex; justify-content: left; align-items: center; background-color: #262730; border-radius: 10px; width: {st.session_state.start_forest_cover_percent_int}%; height: 50px; padding: 5px">'
                                f'<p style="color: white; font-size: 24px; font-weight: bold; margin: 0; width: 80%;">{st.session_state.start_forest_cover_ha:.0f} ha</p>'
                                '</div>', unsafe_allow_html=True)
                    st.markdown(' ')

                    st.markdown('End date forest area (hectares)')

                    st.markdown(f'<div style="display: flex; justify-content: left; align-items: center; background-color: #262730; border-radius: 10px; width: {st.session_state.end_forest_cover_percent_int}%; height: 50px; padding: 5px">'
                                f'<p style="color: white; font-size: 24px; font-weight: bold; margin: 0; width: 80%;">{st.session_state.end_forest_cover_ha:.0f} ha</p>'
                                '</div>', unsafe_allow_html=True)

                    st.markdown("###")
                    st.markdown(
                            '<h3 style="color: white; font-size: 24px;">Total change in forest area</h3>'
                            '</div>', unsafe_allow_html=True)

                    st.markdown('<div style="display: flex; justify-content: center; align-items: center; background-color: #994636; border-radius: 10px; height: 150px; padding: 5px"; border>'
                            f'<p style="color: white; font-size: 80px; font-weight: bold; margin: 0;">- {st.session_state.total_deforestation_ha:.0f} ha</p>'
                            '</div>', unsafe_allow_html=True)
                with env_tab:
                    st.markdown('This loss of forest is equivalent to...')
                    st.markdown('')
                    st.markdown('##### Area (ha)')
                    sub1, sub2 = env_tab.columns([2,2])
                    st.markdown(
                                    """
                                <style>
                                [data-testid="stMetricValue"] {
                                    font-size: 50px;
                                }
                                </style>
                                """,
                                    unsafe_allow_html=True,
                        )
                    with sub1:
                        st.metric(value = round(st.session_state.loft_loss), label = '🚗 LeWagon Berlin Lofts', help = 'Equivalent to 187m2')
                    with sub2:
                        st.metric(value = round(st.session_state.berg_loss), label = ' 🏢 Berghains', help = "Equivalent to 2838 m2. But it's just a guess, none of us have gotten in...")
                    st.markdown('####')
                    st.markdown('##### CO2 (tons)')
                    sub1, sub2 = env_tab.columns([2,2])
                    st.markdown(
                                    """
                                <style>
                                [data-testid="stMetricValue"] {
                                    font-size: 50px;
                                }
                                </style>
                                """,
                                    unsafe_allow_html=True,
                        )
                    with sub1:
                        st.metric(value = round(st.session_state.human_co2_cons_equ), label = '✈️ Annual per capita emissions', help = 'Assumption: 4.7 tonnes CO2 emitted annually per capita.')

                    with sub2:
                        st.metric(value = round(st.session_state.beef_equ), label = '🐮 Kilograms of beef', help = 'Based on the production of this amount of beef. Assumption: 0.1 tons CO2 per kg')
