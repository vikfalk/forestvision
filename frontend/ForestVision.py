import io
import base64
import numpy as np
import pandas as pd
import datetime as dt
import requests
import pydeck as pdk
from PIL import Image
import streamlit as st
from processing.frontend_processing import smooth_and_vectorize


CLOUD_URL = "https://forestvision-llzimbumzq-oe.a.run.app/get_satellite_images"
LOCAL_URL = "http://localhost:8080/get_satellite_images"
API_URL = CLOUD_URL
SQUARE_SIZE = 5.12

def base64_to_numpy(img_b64):
    """
    Takes a base64 encoded image array, decodes it and returns a (numpy) image array.
    """
    img_bytes = io.BytesIO(base64.b64decode(img_b64))
    img_array = np.load(img_bytes)
    return img_array

def day_difference_calculator(row):
    try:
        date_obj_1 = dt.datetime.strptime(row.date, '%Y-%m-%d').date()
        date_obj_2 = dt.datetime.strptime(row.prev_date, '%Y-%m-%d').date()
        difference = date_obj_1 - date_obj_2
        return difference.days
    except TypeError:
        return pd.NA

def date_reformatter(row):
    try:
        return dt.datetime.strptime(row.date, '%Y-%m-%d').date().strftime("%Y/%m")
    except TypeError:
        return pd.NA

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
        with st.session_state.input_spinner_placeholder, st.spinner(
            'Requesting satellite images from Sentinel-2 L2A API...'
        ):
            response = requests.get(
                url=api_url,
                params=params,
                timeout=60
            )
        # Process start images
        with st.session_state.input_spinner_placeholder, st.spinner(
            'Processing images and calculating metrics...'
        ):
            # Obtaining Dates
            date_list_loaded = response.json().get("date_list_loaded")

            # Obtaining and Decoding Segmented Images (Black and White)
            segmented_images_b64 = response.json().get("segmented_img_list")
            segmented_image_arrays = [base64_to_numpy(img_b64) for img_b64 in segmented_images_b64]
            segmented_images = [Image.fromarray(image) for image in segmented_image_arrays]

            # Obtaining and Decoding Original Satellite Images (R, G, B)
            original_images_b64 = response.json().get("original_img_list")
            original_image_arrays = [base64_to_numpy(img_b64) for img_b64 in original_images_b64]
            original_images = [Image.fromarray(image).convert('RGBA') for image in original_image_arrays]

            # Assign the Session States and Variables for First Image
            st.session_state.start_mask = segmented_image_arrays[0]
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
            total_overlay_calculated_array = smooth_and_vectorize(
                array=total_overlay_calculated_array,
                smoothing=9,
                hex_code='#994636',
                opacity=0.5
            )
            total_overlay_calculated = total_overlay_calculated_array.convert('RGBA')
            total_calculated_overlay = Image.alpha_composite(end_overlay, total_overlay_calculated)
            st.session_state.total_calculated_overlay = total_calculated_overlay

            # Total metrics
            total_deforestation = -round((100 - (end_forest_cover_percent / start_forest_cover_percent) * 100), 1)
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
            # Forest Loss in Hectares
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
        st.markdown('''No suitable image found near your start date.
                    Please try a different location or timeframe.''')

st.set_page_config(
    page_title="ForestVision",
    page_icon="🌳",
    layout="wide"
)


logo_url = 'https://vikfalk.github.io/deforestation_frontend/images/logo.png'
st.sidebar.image(logo_url, use_column_width=True)

#Sidebar styling
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width:30% !important;
             border: 2px solid #333;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
        .main.st-emotion-cache-bm2z3a.ea3mdgi8 {
            background-color: #0E1117;
        }
        .st-emotion-cache-dsgfvv.ezrtsby2 {
            background-color: #0E1117;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
        #view-default-view {
            position: absolute;
            left: 100px;
            top: -200px; /* Adjust the top value to move it upwards */
            width: 438px;
            height: 500px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if 'latitude_input' not in st.session_state:
    st.session_state.latitude_input = '-8.49'
    st.session_state.longitude_input = '-55.26'

with st.sidebar:
    st.markdown(' ')
    st.markdown('''Track forest area change of any area on Earth using real-time \
        satellite data and AI by inputting coordinates or choosing an example below.''')
    st.title('Choose your own location')
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.latitude_input = st.text_input('Latitude ', st.session_state.latitude_input,
                                                        help = "Enter the longitude coordinates of your desired area of interest. Press enter to view on map.")
        st.session_state.start_timeframe = st.date_input('Start date ', dt.datetime(2017, 6, 30),
                                        min_value=dt.datetime(2017, 1, 1),
                                        max_value= dt.datetime(2024, 12, 31),
                                        help= "Select the start and end date of your desired timeframe.")

        if st.button('View on map', use_container_width=True):
                    st.session_state.latitude_input = st.session_state.latitude_input
                    st.session_state.longitude_input = st.session_state.longitude_input
                    st.session_state.zoom = 12.5


    with col2:
        st.session_state.longitude_input = st.text_input('Longitude', st.session_state.longitude_input,)
        st.session_state.end_timeframe = st.date_input(
            'End date ',
            min_value=dt.datetime(2017, 1, 1),
            max_value= dt.datetime(2024, 12, 31)
        )
        if st.button(
            "**Calculate forest loss**",
            use_container_width=True,
            type='primary',
            help= 'Click me to calculate deforestation.'
        ):
            process_forest_loss_calculation(
                latitude=st.session_state.latitude_input,
                longitude=st.session_state.longitude_input,
                start_date=st.session_state.start_timeframe,
                end_date=st.session_state.end_timeframe,
                api_url=API_URL
            )
    # st.divider()

    st.title('View an example')
    # with st.expander('Examples'):
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True, height = 228):
            st.image('https://vikfalk.github.io/deforestation_frontend/images/bolivia_example.png')
            if st.button('View on map        ', use_container_width=True):
                st.session_state.latitude_input = -18.39
                st.session_state.longitude_input = -59.72
                st.session_state.zoom = 12.5
            if st.button('Calculate      ', use_container_width=True, type='primary'):
                st.session_state.latitude_input = -18.39
                st.session_state.longitude_input = -59.72
                st.session_state.zoom = 12.5
                st.session_state.start_timeframe = "2017-08-24"
                st.session_state.end_timeframe = "2024-04-24"

                process_forest_loss_calculation(
                    latitude=st.session_state.latitude_input,
                    longitude=st.session_state.longitude_input,
                    start_date=st.session_state.start_timeframe,
                    end_date=st.session_state.end_timeframe,
                    api_url=API_URL
                )
    with col2:
        with st.container(border=True, height = 228):
            st.image('https://vikfalk.github.io/deforestation_frontend/images/brazil_example.png')
            if st.button('View on map       ', use_container_width=True):
                st.session_state.latitude_input = -12.11463
                st.session_state.longitude_input = -60.83938
                st.session_state.zoom = 12.5
            if st.button('Calculate ', use_container_width=True, type='primary'):
                st.session_state.latitude_input = -12.11463
                st.session_state.longitude_input = -60.83938
                st.session_state.zoom = 12.5
                st.session_state.start_timeframe = "2017-08-24"
                st.session_state.end_timeframe = "2024-04-24"

                process_forest_loss_calculation(
                    latitude=st.session_state.latitude_input,
                    longitude=st.session_state.longitude_input,
                    start_date=st.session_state.start_timeframe,
                    end_date=st.session_state.end_timeframe,
                    api_url=API_URL
                )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('''# Detailed Analysis\nScrutinize incremental change between the start and end date by choosing the number of intermediary intervals and pressing the "Calculate" button.''')
    with col2:
        st.markdown("#")
        sample_number = st.slider('', min_value=2, max_value=8)
        send_orginal_images = 'False'
        if st.checkbox('Also send raw images'):
            send_orginal_images = 'True'
        params = {
                'start_timeframe': st.session_state.start_timeframe,
                'end_timeframe': st.session_state.end_timeframe,
                'longitude': st.session_state.longitude_input,
                'latitude': st.session_state.latitude_input,
                'sample_number': sample_number,
                'send_orginal_images': send_orginal_images
        }
        if st.button("Calculate", use_container_width=True, type='primary'):
            st.session_state.show_intervall_analytics = True

    # with st.expander('View more time intervals and data visualizations.'):

# Map
if 'zoom' not in st.session_state:
    st.session_state.longitude_input = -55.26000
    st.session_state.latitude_input = -8.49000
    st.session_state.end_timeframe = dt.datetime(2024, 1, 1)
    st.session_state.start_timeframe = dt.datetime(2021, 1, 1)
    st.session_state.zoom = 0.9
    st.session_state.input_spinner_placeholder = None

view_state = pdk.ViewState(
    longitude=float(st.session_state.longitude_input),
    latitude=float(st.session_state.latitude_input),
    zoom=st.session_state.zoom
)

half_side_length = float(SQUARE_SIZE) / 2 / 110.574

square_coords = [
    [float(st.session_state.longitude_input) - half_side_length,
     float(st.session_state.latitude_input) - half_side_length],
    [float(st.session_state.longitude_input) + half_side_length,
    float(st.session_state.latitude_input) - half_side_length],
    [float(st.session_state.longitude_input) + half_side_length,
    float(st.session_state.latitude_input) + half_side_length],
    [float(st.session_state.longitude_input) - half_side_length,
    float(st.session_state.latitude_input) + half_side_length],
    [float(st.session_state.longitude_input) - half_side_length,
    float(st.session_state.latitude_input) - half_side_length]
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

# with map_col:
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/satellite-streets-v12',
    initial_view_state=view_state,
    layers=[polygon_layer],
    tooltip=False
))

st.session_state.input_spinner_placeholder = st.empty()

if 'output' not in st.session_state:
    st.session_state.output = False

if st.session_state.output:
    with st.container():
        col1, col2, col3 = st.columns([11, 5, 11])
        with col1:
            st.markdown('---')
        with col2:
            st.markdown("<p style='text-align: center; font-family: Helvetica, sans serif; font-size: 30px;'><b>Output</b></p>", unsafe_allow_html=True)
        with col3:
            st.markdown('---')

    with st.container(border = True):
            st.markdown(f"**Summary:** {st.session_state.info_intro} {st.session_state.start_info} and {st.session_state.end_info}. This area witnessed a {round(st.session_state.total_deforestation)}% change in forest cover over this timeframe.")

    with st.container(border = False):
        sat_col, forest_col, overlay_col, metrics_col = st.columns([3.2, 3.2, 7, 6])

        with sat_col:
            st.markdown("<p style='text-align: left; font-size: 18px;'><b>Start date</b></p>", unsafe_allow_html=True)
            st.image(st.session_state.start_sat, use_column_width=True, caption='Satellite image')

            st.markdown("<p style='text-align: left; font-size: 18px;'><b>End date</b></p>", unsafe_allow_html=True)
            st.image(st.session_state.end_sat, use_column_width=True, caption='Satellite image')

        with forest_col:
            st.markdown("<p style='text-align: left; color: #0E1117; font-size: 18px;'><b>Start date</b></p>", unsafe_allow_html=True)
            st.image(st.session_state.start_overlay, use_column_width=True, caption='Predicted forest area')

            st.markdown("<p style='text-align: left; color: #0E1117; font-size: 18px;'><b>End date</b></p>", unsafe_allow_html=True)
            st.image(st.session_state.end_overlay, use_column_width=True, caption='Predicted forest area' )

        with overlay_col:
            with st.container(border=True, height = 620):
                st.markdown("<p style='text-align: center; font-size: 22px;'><b>Total Forest Change</b></p>", unsafe_allow_html=True)
                st.image(st.session_state.total_calculated_overlay)
                st.image('https://vikfalk.github.io/deforestation_frontend/images/legend.png')

        with metrics_col:
            with st.container(border=True, height = 620):
                st.markdown("<p style='text-align: center; font-size: 22px;'><b>Metrics</b></p>", unsafe_allow_html=True)

                forest_loss_percent_tab, forest_loss_ha_tab = st.tabs(['Forest Loss (%)', 'Forest Loss (ha)'])
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
                            f'<p style="color: white; font-size: 80px; font-weight: bold; margin: 0;"> {st.session_state.total_deforestation:.0f}%</p>'
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
                # with env_tab:
                #     st.markdown('This loss of forest is equivalent to...')
                #     st.markdown('')
                #     st.markdown('##### Area (ha)')
                #     sub1, sub2 = env_tab.columns([2,2])
                #     st.markdown(
                #                     """
                #                 <style>
                #                 [data-testid="stMetricValue"] {
                #                     font-size: 50px;
                #                 }
                #                 </style>
                #                 """,
                #                     unsafe_allow_html=True,
                #         )
                #     with sub1:
                #         st.metric(value = round(st.session_state.loft_loss), label = '🚗 LeWagon Berlin Lofts', help = 'Equivalent to 187m2')
                #     st.markdown('####')
                #     st.markdown('##### CO2 (tons)')
                #     sub1, sub2 = env_tab.columns([2,2])
                #     st.markdown(
                #                     """
                #                 <style>
                #                 [data-testid="stMetricValue"] {
                #                     font-size: 50px;
                #                 }
                #                 </style>
                #                 """,
                #                     unsafe_allow_html=True,
                #         )
                #     with sub1:
                #          st.metric(value = round(st.session_state.human_co2_cons_equ), label = '✈️ Annual per capita emissions', help = 'Assumption: 4.7 tonnes CO2 emitted annually per capita.')

                #     with sub2:
                #         st.metric(value = round(st.session_state.beef_equ), label = '🐮 Kilograms of beef', help = 'Based on the production of this amount of beef. Assumption: 0.1 tons CO2 per kg')


if 'show_intervall_analytics' not in st.session_state:
    st.session_state.show_intervall_analytics = False

if st.session_state.show_intervall_analytics:
    response = requests.get(
        url=API_URL,
        params=params,
        timeout=20
    )
    # Dates
    date_list_loaded = response.json().get("date_list_loaded")

    # Segmented Images
    img_b64_list = response.json().get("segmented_img_list")
    segmented_image_arrays = [base64_to_numpy(img_b64) for img_b64 in img_b64_list]
    segmented_image_list = [Image.fromarray(image) for image in segmented_image_arrays]

    # Original Images
    if send_orginal_images == 'True':
        img_b64_list = response.json().get("original_img_list")
        original_image_arrays = [base64_to_numpy(img_b64) for img_b64 in img_b64_list]
        original_image_list = [Image.fromarray(image) for image in original_image_arrays]

    # METRICS
    coverage_list = [round(((np.count_nonzero(arr == 0) / arr.size) * 100), 1) for arr in segmented_image_arrays]
    coverage_list_inverted = [100 - cov for cov in coverage_list]
    HECTAR_PER_IMAGE = 2621.44

    # DATAFRAME CALCULATIONS
    pd.set_option('future.no_silent_downcasting', True)
    df = (pd.DataFrame({
                "date": date_list_loaded,
                "coverage": coverage_list_inverted})
            .assign(coverage_prev_year=lambda df_: df_.coverage.shift(1))
            .assign(prev_date=lambda df_: df_.date.shift(1))
            .assign(cover_difference_perc=lambda df_: df_.coverage_prev_year - df_.coverage)
            .assign(cover_difference_ha=lambda df_: (df_.coverage_prev_year - df_.coverage) / 100 * HECTAR_PER_IMAGE)
            .assign(cover_difference_perc_cumu=lambda df_: df_.cover_difference_perc.cumsum())
            .assign(cover_difference_ha_cumu=lambda df_: df_.cover_difference_ha.cumsum())
            .assign(days_since_prev=lambda df_: df_.apply(day_difference_calculator, axis=1))
            .assign(months_since_prev=lambda df_: df_.days_since_prev / 30.437)
            .assign(ha_per_months=lambda df_: df_.cover_difference_ha / df_.months_since_prev)
            .drop(columns=["coverage_prev_year", "prev_date"])
            .assign(date=lambda df_: df_.apply(date_reformatter, axis=1))
            .fillna(0)
            .infer_objects()
            .set_index("date")
    )

    # DATA VISUALIZATION
    df_perc_cumu = df[["cover_difference_perc_cumu"]].round(1).reset_index().rename(columns={
        "date": "Dates",
        "cover_difference_perc_cumu": "Coverage Loss in %"})
    df_ha_monthly = df[["ha_per_months"]].round(1).reset_index().rename(columns={
        "date": "Dates",
        "ha_per_months": "Monthy Loss in Hectar"})

    with st.container(border=False):
        st.markdown("<p style='text-align: center; font-family: Helvetica, sans serif; font-size: 30px;'><b>Deforestation Over Time</b></p>", unsafe_allow_html=True)
        # st.markdown("## Deforestation Over Time:")
        with st.container(border=True):
            cols = st.columns(len(date_list_loaded))
            if send_orginal_images == 'False':
                for col, request_info_date, segmented_image in zip(cols, date_list_loaded, segmented_image_list):
                    col.markdown(f"<p style='text-align: center; font-size: 14px;'><b>{request_info_date}</b></p>", unsafe_allow_html=True)
                    # col.markdown(f"{request_info_date}")
                    col.image(segmented_image, use_column_width=True)
            if send_orginal_images == 'True':
                for col, request_info_date, original_image, segmented_image in zip(cols, date_list_loaded, original_image_list, segmented_image_list):
                    col.markdown(f"<p style='text-align: center; font-size: 14px;'><b>{request_info_date}</b></p>", unsafe_allow_html=True)
                    # col.markdown(f"{request_info_date}")
                    col.image(segmented_image, use_column_width=True)
                    col.image(original_image, use_column_width=True)
        with st.container(border=True):
            col_a, col_b = st.columns(2)
            with col_a.container(border=False):
                    st.markdown("<p style='text-align: center; font-size: 15px;'><b>Coverage Lost Since Start</b></p>", unsafe_allow_html=True)
                    # st.markdown("### Coverage Lost Since Start")
                    st.bar_chart(df_perc_cumu, x="Dates", y="Coverage Loss in %", color="#994636")

            with col_b.container(border=False):
                    st.markdown("<p style='text-align: center; font-size: 15px;'><b>Monthly Loss Rate</b></p>", unsafe_allow_html=True)
                    # st.markdown("### Monthly Loss Rate", unsafe_allow_html=True)
                    st.bar_chart(df_ha_monthly, x="Dates", y="Monthy Loss in Hectar", color="#994636")

    # Data Supply
    renamed_df = (df
    .drop(columns=["months_since_prev"])
    .rename(columns={
        'coverage': 'Coverage in Percent',
        'days_since_prev': 'Days Passed Since Previous Cloud-Free Image',
        'cover_difference_perc': 'Forest Coverage Change in Previous Period (%)',
        'cover_difference_perc_cumu': 'Cum. Difference in Coverage in Previous Period (%)',
        'cover_difference_ha': 'Forest Area Change in Previous Period (Hectar)',
        'cover_difference_ha_cumu': 'Cum. Forest Area Change in Previous Period (Hectar)',
        'ha_per_months': 'Monthly Area Loss Rate in Previous Period'
        })
    .astype('float32')
    .round(2)
    )
    with st.container(border=False):
        st.write(renamed_df.T)


requests.get(url="https://forestvision-llzimbumzq-oe.a.run.app", timeout=10)
