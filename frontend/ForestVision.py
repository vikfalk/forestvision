import datetime as dt
from typing import List, Tuple
import pydeck as pdk
from PIL import Image
import streamlit as st
import requests
import numpy as np
from processing.frontend_processing import (
    smooth_and_vectorize,
    calculate_metrics,
    base64_to_numpy,
    label,
    convert_to_ha
)


DARK_BLUE = "#262730"
LIGHT_RED = "#994636"
LIGHT_GREEN = "#00B272"
SQUARE_SIZE = 5.12
HECTAR_PER_IMAGE = 2621.44
CO2_TONS_PER_HA_PER_YEAR = 11
LOGO_URL = 'https://vikfalk.github.io/deforestation_frontend/images/logo.png'
LEGEND_URL = 'https://vikfalk.github.io/deforestation_frontend/images/legend.png'
BRAZIL_ICON_URL = 'https://vikfalk.github.io/deforestation_frontend/images/brazil_example.png'
BOLIVIA_ICON_URL = 'https://vikfalk.github.io/deforestation_frontend/images/bolivia_example.png'
CLOUD_URL = "https://forestvision-llzimbumzq-oe.a.run.app/get_satellite_images"
LOCAL_URL = "http://localhost:8080/get_satellite_images"
API_URL = LOCAL_URL  # CLOUD_URL | LOCAL_URL


def create_polygon_layer():
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
    return polygon_layer


def inject_map():
    view_state = pdk.ViewState(
        longitude=float(st.session_state.longitude_input),
        latitude=float(st.session_state.latitude_input),
        zoom=st.session_state.zoom
    )
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/satellite-streets-v12',
        initial_view_state=view_state,
        layers=[create_polygon_layer()],
        tooltip=False
    ))


def set_metrics_session_states(
        image_dates: List[str],
        segmented_images: List[np.ndarray]
    ) -> None:
    st.session_state.metrics = calculate_metrics(
        image_dates,
        segmented_images
    ).reset_index()
    st.session_state.date_start = image_dates[0]
    st.session_state.date_end = image_dates[-1]
    st.session_state.cover_start = st.session_state.metrics.at[0, "coverage"]
    st.session_state.cover_end = st.session_state.metrics.at[1, "coverage"]
    st.session_state.cover_start_ha = convert_to_ha(st.session_state.cover_start)
    st.session_state.cover_end_ha = convert_to_ha(st.session_state.cover_end)
    st.session_state.cover_diff_pp = (
        st.session_state.cover_end
        - st.session_state.cover_start
    )
    st.session_state.cover_diff_rel = (
        st.session_state.cover_diff_pp
        / st.session_state.cover_start
        * 100
    )
    st.session_state.cover_diff_ha = convert_to_ha(st.session_state.cover_diff_pp)
    st.session_state.output = True


def set_overlay_session_states(raw_images, segmented_images):
    st.session_state.start_sat = raw_images[0]
    st.session_state.end_sat = raw_images[-1]

    st.session_state.start_vector_overlay = smooth_and_vectorize(
        array=segmented_images[0],
        hex_code=LIGHT_GREEN
    )
    st.session_state.start_overlay = Image.alpha_composite(
        im1=Image.fromarray(raw_images[0]).convert('RGBA'),
        im2=st.session_state.start_vector_overlay
    )
    # END
    st.session_state.end_vector_overlay = smooth_and_vectorize(
        array=segmented_images[-1],
        hex_code=LIGHT_GREEN
    )
    st.session_state.end_overlay = Image.alpha_composite(
        im1=Image.fromarray(raw_images[-1]).convert('RGBA'),
        im2=st.session_state.end_vector_overlay
    )
    total_overlay_calculated = smooth_and_vectorize(
        array=segmented_images[0] - segmented_images[-1],
        hex_code=LIGHT_RED
    )
    st.session_state.total_calculated_overlay = Image.alpha_composite(
        st.session_state.end_overlay,
        total_overlay_calculated
    )


def inject_bold_centered(text: str, font_em: float=1):
    st.markdown(
        f"""<p style='text-align: center; font-weight: bold; font-size: {font_em}em'> {text}</p>""",
        unsafe_allow_html=True
    )


def inject_metric_bar(text: str, metric: float, unit: str = '%'):
    st.markdown(
        f"""
        {text}
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: {DARK_BLUE};
            border-radius: 10px;
            padding: 5px;
            height: 3em;
            width: {metric}%;
            position: relative;">
            <p style="
                font-weight: bold;
                font-size: 1.25em;
                margin: 0;
                width: 100%;
            ">
                {metric if unit == '%' else convert_to_ha(metric):.0f}{unit}
            </p>
        </div>""",
        unsafe_allow_html=True
    )


def inject_total_change(metric: float, unit: str):
    st.markdown(
        f"""
        Total Change
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: {LIGHT_RED};
            border-radius: 10px;
            padding: 5px;
            height: 6em;
        ">
            <p style="
                font-weight: bold;
                font-size: 2.5em;
                margin: 0;
            ">
                {metric:.0f}{unit}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown('')


def request_satellite_images(latitude, longitude, start_date, end_date):
    response = requests.get(
        url=API_URL,
        params={
            'start_timeframe': start_date,
            'end_timeframe': end_date,
            'longitude': longitude,
            'latitude': latitude,
            'sample_number': 2,
            'send_orginal_images': 'True'
        },
        timeout=60
    )
    return response


def parse_response(
    response: requests.Response
    ) -> Tuple[List[str], List[np.ndarray], List[Image.Image]]:
    image_dates = response.json().get("date_list_loaded")
    segmented_images_b64 = response.json().get("segmented_img_list")
    segmented_images = [base64_to_numpy(img_b64) for img_b64 in segmented_images_b64]
    raw_images_b64 = response.json().get("original_img_list")
    raw_images = [base64_to_numpy(img_b64) for img_b64 in raw_images_b64]
    parsed_response = (image_dates, segmented_images, raw_images)
    return parsed_response


def process_forest_loss_calculation(latitude, longitude, start_date, end_date):
    try:
        with st.session_state.input_spinner_placeholder, st.spinner(
            'Requesting satellite images from Sentinel-2 L2A API...'
        ):
            st.session_state.response = request_satellite_images(latitude, longitude, start_date, end_date)

        with st.session_state.input_spinner_placeholder, st.spinner(
            'Processing images and calculating metrics...'
        ):
            image_dates, segmented_images, raw_images = parse_response(
                st.session_state.response
            )

            set_metrics_session_states(image_dates, segmented_images)
            set_overlay_session_states(raw_images, segmented_images)
            st.session_state.zoom = 12.5

    except (requests.RequestException, ValueError):
        st.markdown(
            "No suitable image found near your start date. "
            "Please try a different location or timeframe."
        )


def fill_sidebar_top_col1():
    st.session_state.latitude_input = st.text_input(
        label='Latitude',
        value=-8.49,
        help=(
            "Enter the coordinates of your desired area of interest. "
            "Press enter to view on map."
        )
    )
    st.session_state.start_timeframe = st.date_input(
        'Start date', dt.datetime(2017, 6, 30),
        min_value=dt.datetime(2017, 1, 1),
        max_value=dt.datetime(2024, 12, 31),
        help="Select the start and end date of your desired timeframe."
    )
    if st.button('View on map', use_container_width=True):
        st.session_state.latitude_input = st.session_state.latitude_input
        st.session_state.longitude_input = st.session_state.longitude_input
        st.session_state.zoom = 12.5


def fill_sidebar_top_col2():
    st.session_state.longitude_input = st.text_input(
        label='Longitude',
        value=-55.26
    )
    st.session_state.end_timeframe = st.date_input(
        label='End date',
        min_value=dt.datetime(2017, 1, 1),
        max_value= dt.datetime(2024, 12, 31)
    )
    if st.button(
        label="**Calculate forest loss**",
        use_container_width=True,
        type='primary',
        help='Click me to calculate deforestation.'
    ):
        process_forest_loss_calculation(
            latitude=st.session_state.latitude_input,
            longitude=st.session_state.longitude_input,
            start_date=st.session_state.start_timeframe,
            end_date=st.session_state.end_timeframe
        )


def fill_sidebar_bot_col1():
    with st.container(border=True):
        st.image(BOLIVIA_ICON_URL)
        if st.button('View on map   ', use_container_width=True):
            st.session_state.latitude_input = -18.39
            st.session_state.longitude_input = -59.72
            st.session_state.zoom = 12.5
        if st.button('Calculate   ', use_container_width=True, type='primary'):
            st.session_state.latitude_input = -18.39
            st.session_state.longitude_input = -59.72
            st.session_state.zoom = 12.5
            st.session_state.start_timeframe = "2017-08-24"
            st.session_state.end_timeframe = "2024-04-24"

            process_forest_loss_calculation(
                latitude=st.session_state.latitude_input,
                longitude=st.session_state.longitude_input,
                start_date=st.session_state.start_timeframe,
                end_date=st.session_state.end_timeframe
            )


def fill_sidebar_bot_col2():
    with st.container(border=True):
        st.image(BRAZIL_ICON_URL)
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
                end_date=st.session_state.end_timeframe
            )


def fill_detailed_analysis_col_2():
    st.markdown("#                 ")
    sample_number = st.slider(
        label='Select a sample number',
        min_value=2,
        max_value=8,
        label_visibility="hidden"
    )
    send_orginal_images = 'False'
    if st.checkbox('Also send raw images'):
        send_orginal_images = 'True'
    if st.button("Calculate", use_container_width=True, type='primary'):
        st.session_state.show_intervall_analytics = True
    return sample_number, send_orginal_images


st.set_page_config(
    page_title="ForestVision",
    page_icon="🌳",
    layout="wide"
)
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 30% !important;
            border: 2px solid #333;
        }
        .main.st-emotion-cache-bm2z3a.ea3mdgi8 {
            background-color: #0E1117;
        }
        .st-emotion-cache-dsgfvv.ezrtsby2 {
            background-color: #0E1117;
        }
        #view-default-view {
            position: absolute;
            left: 100px;
            top: -200px;
            width: 438px;
            height: 500px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
st.sidebar.image(LOGO_URL, use_column_width=True)
st.session_state.setdefault('latitude_input', '-8.49')
st.session_state.setdefault('longitude_input', '-55.26')

with st.sidebar:
    st.markdown(' ')
    st.markdown(
        "Track forest area change of any area on Earth using real-time satellite "
        "data and AI by inputting coordinates or choosing an example below."
    )
    st.title('Choose your own location')
    col1, col2 = st.columns(2)
    with col1:
        fill_sidebar_top_col1()

    with col2:
        fill_sidebar_top_col2()

    st.title('View an example')
    col1, col2 = st.columns(2)
    with col1:
        fill_sidebar_bot_col1()
    with col2:
        fill_sidebar_bot_col2()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            '''# Detailed Analysis\nScrutinize incremental change between the
            start and end date by choosing the number of intermediary intervals
            and pressing the "Calculate" button.
            '''
        )
    with col2:
        sample_number, send_orginal_images = fill_detailed_analysis_col_2()

if 'zoom' not in st.session_state:
    st.session_state.longitude_input = -55.26000
    st.session_state.latitude_input = -8.49000
    st.session_state.end_timeframe = dt.datetime(2024, 1, 1)
    st.session_state.start_timeframe = dt.datetime(2021, 1, 1)
    st.session_state.zoom = 0.9
    st.session_state.input_spinner_placeholder = None

inject_map()

st.session_state.input_spinner_placeholder = st.empty()

if st.session_state.get('output', False):
    with st.container():
        col1, col2, col3 = st.columns([11, 5, 11])
        with col1:
            st.markdown('---')
        with col2:
            inject_bold_centered('Output', font_em=2)
        with col3:
            st.markdown('---')
    with st.container(border=True):
        st.markdown(
            f"""
            **Summary:** The closest cloud-free images to your desired start
            and end dates are from: {st.session_state.date_start} and
            {st.session_state.date_end}. This area witnessed a
            {st.session_state.cover_diff_rel:.0f}% change in forest cover
            over this timeframe.
            """
        )
    with st.container(border=False):
        component_col, overlay_col, metrics_col = st.columns(3)
        with component_col:
            with st.container(border=True):
                inject_bold_centered('Start Date')
                sat_col, forest_col = st.columns(2)
                with sat_col:
                    st.image(
                        st.session_state.start_sat,
                        use_column_width=True,
                        caption='Satellite image'
                    )
                with forest_col:
                    st.image(
                        st.session_state.start_overlay,
                        use_column_width=True,
                        caption='Forest segments'
                    )
                inject_bold_centered('End Date')
                sat_col, forest_col = st.columns(2)
                with sat_col:
                    st.image(
                        st.session_state.end_sat,
                        use_column_width=True,
                        caption='Satellite image'
                    )
                with forest_col:
                    st.image(
                        st.session_state.end_overlay,
                        use_column_width=True,
                        caption='Forest segments'
                    )

        with overlay_col:
            with st.container(border=True):
                inject_bold_centered('Total Forest Change')
                st.image(st.session_state.total_calculated_overlay)
                st.image(LEGEND_URL)
        with metrics_col:
            with st.container(border=True):
                inject_bold_centered('Metrics')
                percent_tab, hectar_tab = st.tabs(['Change in %', 'Change in ha'])
                with percent_tab:
                    inject_metric_bar(
                        text='Start Date Forest Cover',
                        metric=st.session_state.cover_start,
                        unit='%'
                    )
                    st.markdown('')
                    inject_metric_bar(
                        text='End Date Forest Cover',
                        metric=st.session_state.cover_end,
                        unit='%'
                    )
                    st.markdown('')
                    inject_total_change(st.session_state.cover_diff_rel, '%')
                with hectar_tab:
                    inject_metric_bar(
                        text='Start Date Forest Cover',
                        metric=st.session_state.cover_start,
                        unit=' ha'
                    )
                    st.markdown('')
                    inject_metric_bar(
                        text='End Date Forest Cover',
                        metric=st.session_state.cover_end,
                        unit=' ha'
                    )
                    st.markdown('')
                    inject_total_change(st.session_state.cover_diff_ha, ' ha')

if st.session_state.get("show_intervall_analytics", False):
    intervall_response = requests.get(
        url=API_URL,
        params={
            'start_timeframe': st.session_state.start_timeframe,
            'end_timeframe': st.session_state.end_timeframe,
            'longitude': st.session_state.longitude_input,
            'latitude': st.session_state.latitude_input,
            'sample_number': sample_number,
            'send_orginal_images': send_orginal_images
        },
        timeout=20
    )
    date_list_loaded = intervall_response.json().get("date_list_loaded")
    img_b64_list = intervall_response.json().get("segmented_img_list")
    segmented_image_arrays = [base64_to_numpy(img_b64) for img_b64 in img_b64_list]
    segmented_image_list = [Image.fromarray(image) for image in segmented_image_arrays]
    if send_orginal_images == 'True':
        img_b64_list = intervall_response.json().get("original_img_list")
        original_image_arrays = [base64_to_numpy(img_b64) for img_b64 in img_b64_list]
        original_image_list = [Image.fromarray(image) for image in original_image_arrays]
    df = calculate_metrics(date_list_loaded, segmented_image_arrays)
    df_perc_cumu = df[["cover_diff_pp_cum"]].round(1).reset_index().rename(columns={
        "date": "Dates",
        "cover_diff_pp_cum": "Coverage Loss in %"}
    )
    df_ha_monthly = df[["loss_per_months_ha"]].round(1).reset_index().rename(columns={
        "date": "Dates",
        "loss_per_months_ha": "Monthy Loss in Hectar"}
    )
    with st.container(border=False):
        inject_bold_centered('Deforestation Over Time', font_em=2)
        with st.container(border=True):
            cols = st.columns(len(date_list_loaded))
            if send_orginal_images == 'False':
                for col, request_info_date, segmented_image in zip(cols, date_list_loaded, segmented_image_arrays):
                    with col:
                        inject_bold_centered(request_info_date)
                    col.image(segmented_image, use_column_width=True)
            if send_orginal_images == 'True':
                for col, request_info_date, original_image, segmented_image in zip(cols, date_list_loaded, original_image_arrays, segmented_image_arrays):
                    with col:
                        inject_bold_centered(request_info_date)
                    col.image(segmented_image, use_column_width=True)
                    col.image(original_image, use_column_width=True)
        with st.container(border=True):
            col_a, col_b = st.columns(2)
            with col_a.container(border=False):
                inject_bold_centered('Coverage Lost Since Start')
                st.bar_chart(
                    df_perc_cumu,
                    x="Dates",
                    y="Coverage Loss in %",
                    color=LIGHT_RED
                )
            with col_b.container(border=False):
                inject_bold_centered('Monthly Loss Rate')
                st.bar_chart(
                    df_ha_monthly,
                    x="Dates",
                    y="Monthy Loss in Hectar",
                    color=LIGHT_RED
                )
    with st.container(border=False):
        st.write(label(df).T)

requests.get(url="https://forestvision-llzimbumzq-oe.a.run.app", timeout=10)
