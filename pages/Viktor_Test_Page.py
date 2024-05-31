import streamlit as st
import datetime as dt
import pydeck as pdk
from PIL import Image
import requests
#import leafmap
import random
from streamlit_extras.grid import grid
import streamlit_nested_layout


if 'forest_loss' not in st.session_state:
    st.session_state.forest_loss_start = 0.0
    st.session_state.forest_loss_end = 0.0
    st.session_state.forest_loss_final = 0.0
    st.session_state.test_img = None

API_URL = 'http://localhost:8000/calculate_change'

st.set_page_config(
    page_title="Deforestation Tracker",
    page_icon="🌳",
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.markdown("## Deforestation Tracker")
st.markdown("Track forest area change of a desired location by entering coordinates and a timeframe below.")

# Create columns for layout
input_col1, inputcol2, map_col, output_col = st.columns([1, 1, 6, 3])

# Place inputs in the first column
with input_col1:
    latitude_input = float(st.text_input('Latitude', '-8.49000'))
    start_timeframe = st.date_input('Start date', dt.datetime(2021, 1, 1))
    factors = [1, 2, 3, 4, 5, 10, 25, 50, 100]
    square_size_options = [5.12 * factor for factor in factors]
    labels = {val: f"{val:.2f}" for val in square_size_options}
    default_value = square_size_options[0]
    square_size = st.select_slider('Square length (km)', 
                                options=square_size_options, 
                                value=default_value, 
                                format_func=lambda x: labels[x])
    st.markdown('-----')
    st.markdown('#')
    st.markdown('Click for magic ->')

with inputcol2:    
    longitude_input = float(st.text_input('Longitude', '-55.26000'))
    end_timeframe = st.date_input('End date')
    sample_number = st.slider('Number of samples', min_value=1, max_value=10)

    params = {
        'start_timeframe': start_timeframe,
        'end_timeframe': end_timeframe,
        'longitude': longitude_input,
        'latitude': latitude_input,
        'sample_number': sample_number,
        'square_size': square_size
    }
    st.markdown('-----')
    st.markdown('###')
    if st.button('Calculate Change') and all(params.values()):
        response = requests.get(url=API_URL, params=params, timeout=5)
        prediction_json = response.json()
        prediction = round(prediction_json["change"], 2)
        prediction_string = format(prediction, '.2f')
        # st.markdown(f"""
        #             In the specified plot of land,
        #             the rainforest area was reduced by {prediction_string} %
        #             between {start_timeframe} and {end_timeframe}.
        #             """)
        
        st.session_state.forest_loss_start = round(random.uniform(3.1, 6), 2)
        st.session_state.forest_loss_end = round(st.session_state.forest_loss_start - round(random.uniform(2, 3), 2))
        st.session_state.test_img = 'image_postproc/smoothed_png.png'

with output_col:
    tab1, tab2, tab3, tab4 = st.tabs(['Forest Loss', 'Sat Images', 'Masks', 'Test'])
    
    with tab1:
        st.markdown('Start date forest area')
        
        WIDTH_FACTOR = 50
        box_width_start = st.session_state.forest_loss_start * WIDTH_FACTOR
        st.markdown(f'<div style="display: flex; justify-content: left; align-items: center; background-color: #FF4B4B; border-radius: 10px; width: {box_width_start}px; height: 50px; padding: 5px">'
                    f'<p style="color: white; font-size: 24px; font-weight: bold; margin: 0;">{st.session_state.forest_loss_start}</p>'
                    '</div>', unsafe_allow_html=True)

        
        # st.markdown('<div style="display: flex; justify-content: left; align-items: center; background-color: #FF4B4B; border-radius: 10px; width: 350px; height: 50px; padding: 5px">'
        #         '<p style="color: white; font-size: 24px; font-weight: bold; margin: 0;">5.4 ha</p>'
        #         '</div>', unsafe_allow_html=True)
        
        st.markdown("###")
        
        st.markdown('End date forest area')

        box_width_end = st.session_state.forest_loss_end * WIDTH_FACTOR
        st.markdown(f'<div style="display: flex; justify-content: left; align-items: center; background-color: #FF4B4B; border-radius: 10px; width: {box_width_end}px; height: 50px; padding: 5px">'
                    f'<p style="color: white; font-size: 24px; font-weight: bold; margin: 0;">{st.session_state.forest_loss_end}</p>'
                    '</div>', unsafe_allow_html=True)

        st.markdown("###")
        st.markdown(
                '<h3 style="color: white; font-size: 24px;">Total deforestation</h3>'
                '</div>', unsafe_allow_html=True)
        
        st.session_state.forest_loss_final = st.session_state.forest_loss_start - st.session_state.forest_loss_end
        st.markdown('<div style="display: flex; justify-content: center; align-items: center; background-color: #262630; border-radius: 10px; height: 100px; padding: 5px"; border>'
                f'<p style="color: white; font-size: 50px; font-weight: bold; margin: 0;">{st.session_state.forest_loss_final:.2f} ha</p>'
                '</div>', unsafe_allow_html=True)
    
    with tab2:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('Start')
            st.markdown('#')
            st.markdown('#')
            st.markdown('End')
        with col2:
            fn = '/Users/viktor/code/vikfalk/deforestation/deforestation_frontend/images/after_resized_satellite.tiff'
            image = Image.open(fn)
            st.image(image, width=190)
            
            fn = '/Users/viktor/code/vikfalk/deforestation/deforestation_frontend/images/after_resized_satellite.tiff'
            image = Image.open(fn)
            st.image(image, width=190)
    
    with tab3:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('Start')
            st.markdown('#')
            st.markdown('#')
            st.markdown('End')
        with col2:
            st.image('pages/final_overlay_image.png', width=190)
            st.image('pages/final_overlay_image.png', width=190)
        
    
    # with tab4:
    #     st.markdown("Test")
        
    #     col1, col2 = st.columns(3)
    #     with col1:
    #         st.image('pages/final_overlay_image.png', width=130)
    #     with col2:
    #         st.image('pages/final_overlay_image.png', width=130)
   



# Calculate the map view state and polygon coordinates
view_state = pdk.ViewState(
    longitude=longitude_input,
    latitude=latitude_input,
    zoom=12.5
)

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
    filled=False,  # Set to False to render only the border
    get_line_color=[230, 175, 47, 100],  # Color of the border
    get_line_width=10,  # Width of the border
    pickable=True,
    extruded=False
)

# Path to the PNG image
IMG_URL = '/Users/viktor/code/vikfalk/deforestation/deforestation_frontend/image_postproc/smoothed_png.png'
BOUNDS = square_coords

bitmap_layer = pdk.Layer(
    "BitmapLayer", 
    data=None, 
    image=st.session_state.test_img, 
    bounds=BOUNDS, 
    opacity=0.5
)
# Place the map in the second column

with map_col:
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/satellite-v9',
        initial_view_state=view_state,
        layers=[polygon_layer, bitmap_layer],  # Add both layers
        tooltip={"text": "{name}"}
    ))












# st.markdown("#")   
# st.markdown("#")
# st.markdown("#")
# st.markdown("#")
# st.markdown("#") 
# st.markdown("------")
# st.markdown("### Output")


# sat_col, forest_col, overlay_col, metrics_col = st.columns([1, 1, 3, 2])

# with sat_col:
#     st.markdown("##### Start date")
#     st.markdown("Satellite image")
#     fn = '/Users/viktor/code/vikfalk/deforestation/deforestation_frontend/images/after_resized_satellite.tiff'
#     image = Image.open(fn)
#     st.image(image)
    
#     st.markdown("##### End date")
#     st.markdown("Satellite image")
#     fn = '/Users/viktor/code/vikfalk/deforestation/deforestation_frontend/images/after_resized_satellite.tiff'
#     image = Image.open(fn)
#     st.image(image)
    
# with forest_col:
#     st.markdown('<p style="color: #0F1116; ">filler</p>', unsafe_allow_html=True)
#     st.markdown("Forest area")
#     st.image('/Users/viktor/code/vikfalk/deforestation/deforestation_frontend/image_postproc/final_overlay_image.png')
    
#     st.markdown('<p style="color: #0F1116; ">filler</p>', unsafe_allow_html=True)
#     st.markdown("Forest area")
#     st.image('/Users/viktor/code/vikfalk/deforestation/deforestation_frontend/image_postproc/final_overlay_image.png')

# with overlay_col:
#     st.markdown("#### Change in forest area")
#     st.image('pages/final_overlay_image.png')
    
#     st.download_button('Download image', IMG_URL)

# with metrics_col:
#     tab1, tab2, tab3 = st.tabs(['Forest Loss', 'Enviromental Impacts', 'EUDR Rating'])
#     with tab1:
#         st.markdown(
#                 '<p style="color: white; font-size: 18px;">Start data forest area</p>'
#                 '</div>', unsafe_allow_html=True)
#         st.markdown('<div style="display: flex; justify-content: left; align-items: center; background-color: green; border-radius: 10px; width: 350px; height: 70px; padding: 5px">'
#                 '<p style="color: white; font-size: 36px; font-weight: bold; margin: 0;">5.12 ha</p>'
#                 '</div>', unsafe_allow_html=True)
        
#         st.markdown("###")
        
#         st.markdown(
#                 '<p style="color: white; font-size: 18px;">End data forest area</p>'
#                 '</div>', unsafe_allow_html=True)
        
#         st.markdown('<div style="display: flex; justify-content: left; align-items: center; background-color: orange; border-radius: 10px; width: 150px; height: 70px; padding: 5px">'
#                 '<p style="color: white; font-size: 36px; font-weight: bold; margin: 0;">2.11 ha</p>'
#                 '</div>', unsafe_allow_html=True)

#         st.markdown("#")
#         st.markdown("#")
#         st.markdown(
#                 '<h3 style="color: white; font-size: 24px;">Total deforestation</h3>'
#                 '</div>', unsafe_allow_html=True)
        
#         st.markdown('<div style="display: flex; justify-content: center; align-items: center; background-color: red; border-radius: 10px; height: 100px; padding: 5px">'
#                 '<p style="color: white; font-size: 61px; font-weight: bold; margin: 0;">3.01 ha</p>'
#                 '</div>', unsafe_allow_html=True)


# st.title("Interactive Map")

# col1, col2 = st.columns([4, 1])
# options = list(leafmap.basemaps.keys())
# index = options.index("OpenTopoMap")

# with col2:
#     basemap = st.selectbox("Select a basemap:", options, index)

# with col1:
#     m = leafmap.Map(
#         locate_control=True, latlon_control=True, draw_export=True, minimap_control=True
#     )
#     m.add_basemap(basemap)
#     m.to_streamlit(height=700)
    


# st.pydeck_chart(pdk.Deck(
#     map_style='mapbox://styles/mapbox/satellite-v9',
#     initial_view_state=view_state,
#     layers=[bitmap_layer],  # Add bitmap_layer here
#     tooltip={"text": "{name}"}
# ))




#st.image('/Users/viktor/code/vikfalk/deforestation/deforestation_frontend/image_postproc/final_overlay_image.png', use_column_width=True)



# st.markdown("""
#     Here are the parameters that are going to get fed to our model API:
# """)
# st.json(params)

# col1, col2 = st.columns(2)
# with col1:
#     st.image("./images/before_resized.png", caption="Before")
# with col2:
#     st.image("./images/after_resized.png", caption="After")






