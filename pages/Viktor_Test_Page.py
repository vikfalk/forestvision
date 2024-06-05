import streamlit as st
import datetime as dt
import pydeck as pdk
from PIL import Image
import requests
import numpy as np
from processing.frontend_processing import smooth_and_vectorize, overlay_vector_on_mask


placeholder_image = Image.new("RGB", (512, 512), (15, 17, 22))

if 'forest_loss' not in st.session_state:
    st.session_state.forest_loss_start = 0.0
    st.session_state.forest_loss_end = 0.0
    st.session_state.forest_loss_final = 0.0
    st.session_state.test_img = None
    st.session_state.end_vector_overlay = None
    st.session_state.end_mask = placeholder_image
    st.session_state.end_forest_cover_percent = 0.0
    st.session_state.end_sat = placeholder_image
    st.session_state.end_overlay = placeholder_image
    st.session_state.end_forest_cover_percent_int = 20
    st.session_state.start_vector_overlay = None
    st.session_state.start_mask = placeholder_image
    st.session_state.start_forest_cover_percent = 0.0
    st.session_state.start_sat = placeholder_image
    st.session_state.start_overlay = placeholder_image
    st.session_state.start_forest_cover_percent_int = 20
    st.session_state.total_overlay = placeholder_image
    st.session_state.total_deforestation = 0
    st.session_state.start_forest_cover_ha = 0
    st.session_state.end_forest_cover_ha = 0


st.set_page_config(
    page_title="Deforestation Tracker",
    page_icon="🌳",
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.markdown("## Deforestation Tracker :palm_tree:")
st.markdown("Track forest area change of a desired location by entering coordinates and a timeframe on the left. Or choose some examples on the right. ")

input_col1, map_col, example_col = st.columns([4, 19, 4])
with input_col1:
    # latitude_input = float(st.text_input('Latitude', '-8.49000',
    #                                     help= "Enter the longitude coordinates of your desired area of interest. Press enter to view on map."))
    # longitude_input = float(st.text_input('Longitude', '-55.26000',
    #                                     help= "Enter the longitude coordinates of your desired area of interest. Press enter to view on map."))
    
    latitude_input = float(st.text_input('Latitude', '-8.49000'))
    longitude_input = float(st.text_input('Longitude', '-55.26000'))
    
    start_timeframe = st.date_input('Start date', dt.datetime(2021, 1, 1), 
                                    min_value=dt.datetime(2017, 1, 1),
                                    max_value= dt.datetime(2024, 12, 31))
    end_timeframe = st.date_input('End date',
                                  min_value=dt.datetime(2017, 1, 1),
                                  max_value= dt.datetime(2024, 12, 31))
    
    factors = [1, 2, 3, 4, 5, 10, 25, 50, 100]
    square_size_options = [5.12 * factor for factor in factors]
    labels = {val: f"{val:.2f}" for val in square_size_options}
    default_value = square_size_options[0]
    square_size = 5.12
    # square_size = st.select_slider('Square length (km)', 
    #                              options=square_size_options, 
    #                              value=default_value, 
    #                              format_func=lambda x: labels[x])

    #     #sample_number = st.slider('Number of samples', min_value=1, max_value=10)
    sample_number = 1
    
    params= {
        'start_timeframe': start_timeframe,
        'end_timeframe': end_timeframe,
        'longitude': longitude_input,
        'latitude': latitude_input,
        'sample_number': sample_number,
        'square_size': square_size
    }

    everything_api = "http://localhost:8080/do_everything_self"
    if st.button("✨ Click for magic ✨"):   
        with st.spinner('Beep boop, contacting satellite :satellite_antenna:'):
            response = requests.get(url=everything_api, params=params, timeout=60)
            
            #start Mask
            start_mask_image_list = response.json().get("start_mask_image_list")
            start_mask_image_array = np.array(start_mask_image_list, dtype=np.uint8)
            start_mask_image = Image.fromarray(start_mask_image_array)
            st.session_state.start_mask = start_mask_image_array
            
            #start Sat
            start_sat_image_list = response.json().get("start_sat_image_list")
            start_sat_image_array = np.array(start_sat_image_list, dtype=np.float32).reshape((512, 512, 3))
            start_sat_image = Image.fromarray((start_sat_image_array * 255).astype(np.uint8)).convert('RGBA')
            st.session_state.start_sat = start_sat_image_array
        
            #REPONSE WITH INFORMATION

            #start vector
            start_mask_vector = smooth_and_vectorize(start_mask_image_array, 9, '#307251', 0.4)
            start_mask_vector = start_mask_vector.convert('RGBA')
            st.session_state.start_vector_overlay = start_mask_vector
            
            #start overlay
            start_mask_image_rgba = start_mask_image.convert('RGBA')
            start_overlay = Image.alpha_composite(start_sat_image, start_mask_vector)
            st.session_state.start_overlay = start_overlay
            

            # start metrics
            start_forest_cover_percent = round(((np.count_nonzero(start_mask_image_array == 0) / start_mask_image_array.size) * 100), 1)
            st.session_state.start_forest_cover_percent = start_forest_cover_percent
            st.session_state.start_forest_cover_percent_int = int(start_forest_cover_percent)
            
            start_forest_cover_ha = ((start_forest_cover_percent/100)*26214400)/1000
            st.session_state.start_forest_cover_ha = start_forest_cover_ha

            
            #End Mask
            end_mask_image_list = response.json().get("end_mask_image_list")
            end_mask_image_array = np.array(end_mask_image_list, dtype=np.uint8)
            end_mask_image = Image.fromarray(end_mask_image_array)
            st.session_state.end_mask = end_mask_image_array
            
            #End Sat
            end_sat_image_list = response.json().get("end_sat_image_list")
            end_sat_image_array = np.array(end_sat_image_list, dtype=np.float32).reshape((512, 512, 3))
            end_sat_image = Image.fromarray((end_sat_image_array * 255).astype(np.uint8)).convert('RGBA')
            st.session_state.end_sat = end_sat_image_array
        
            # #rREPONSE WITH INFORMATION

            #End vector
            end_mask_vector = smooth_and_vectorize(end_mask_image_array, 9, '#FF0000', 0.4)
            end_mask_vector = end_mask_vector.convert('RGBA')
            st.session_state.end_vector_overlay = end_mask_vector
            
            #End overlay
            end_mask_image_rgba = end_mask_image.convert('RGBA')
            end_overlay = Image.alpha_composite(end_sat_image, end_mask_vector)
            st.session_state.end_overlay = end_overlay
        
            # End metrics
            end_forest_cover_percent = round(((np.count_nonzero(end_mask_image_array == 0) / end_mask_image_array.size) * 100), 1)
            st.session_state.end_forest_cover_percent = end_forest_cover_percent
            st.session_state.end_forest_cover_percent_int = int(end_forest_cover_percent)
            
            end_forest_cover_ha = ((end_forest_cover_percent/100)* 26214400)/1000
            st.session_state.end_forest_cover_ha = end_forest_cover_ha
            
            
            #Total overlay
            total_overlay = Image.alpha_composite(end_overlay, start_mask_vector)
            st.session_state.total_overlay = total_overlay
            
            #Total metrics
            total_deforestation = round(((end_forest_cover_percent/start_forest_cover_percent)*100),1)
            st.session_state.total_deforestation = total_deforestation
            
            
            #st.balloons()

# with example_col:
#     with st.container():
#         img = image_select(
#             "Choose an example",
#             images=[
#                 "https://vikfalk.github.io/deforestation_frontend/example_images/brazil.png",
#                 "https://vikfalk.github.io/deforestation_frontend/example_images/brazil.png"
#             ],
#             captions=["Brazilian Soy Farm", "Brazilian Soy Farm"],
#             return_value= 'index', 
#             index = 0
#         )
    
#         if img == 0:
#             pass
            
#         if img == 1:
#             pass
#             # st.session_state.longitude_input = -55.26000
#             # st.session_state.latitude_input = -8.49000
#             # st.session_state.zoom = 12.5


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

# Convert end_mask_vector to pydeck polygon layer
end_mask_polygon_layer = pdk.Layer(
    "PolygonLayer", 
    data=None, 
    get_polygon=st.session_state.end_vector_overlay,
    get_line_color=[255, 0, 0, 255],  # Red color with full opacity for the border
    get_line_width=1,  # Width of the border
)

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
BOUNDS = square_coords

# Retrieve the vectorized mask image from the session state
end_mask_vector = st.session_state.end_vector_overlay

# # Convert the vectorized mask image to PNG format
# if end_mask_vector:
#     buffer = BytesIO()
#     end_mask_vector.save(buffer, format="PNG")
#     st.session_state.end_mask_png = buffer.getvalue()


# Create a BitmapLayer to overlay the PNG image on the map
bitmap_layer = pdk.Layer(
    "BitmapLayer", 
    data=None, 
    image=st.session_state.end_mask_png, 
    bounds=BOUNDS, 
    opacity=0.5  # Adjust opacity as needed
)

# Place the BitmapLayer in the list of layers when creating the pydeck Deck object
with map_col:
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/satellite-v9',
        initial_view_state=view_state,
        layers=[polygon_layer],  # Add the BitmapLayer here
        tooltip={"text": "{name}"}
    ))

with st.container():
    sat_col, forest_col, filler, overlay_col, metrics_col = st.columns([2, 2, 1, 6, 5])

    with sat_col:
        st.markdown("##### Start date")
        st.image(st.session_state.start_sat, caption= "Satellite Image")
            
        st.markdown("##### End date")
        st.image(st.session_state.end_sat, caption= "Satellite Image")
        
    with forest_col:
        st.markdown('<p style="color: #0F1116; ">filler</p>', unsafe_allow_html=True)
        st.image(st.session_state.start_overlay, caption= "Forest Area")
        
        st.markdown('<p style="color: #0F1116; ">filler</p>', unsafe_allow_html=True)
        st.image(st.session_state.end_overlay, caption= "Forest Area")
    
    with overlay_col:
        st.markdown('#### Total Forest Change')
        st.image(st.session_state.total_overlay)
    
    with metrics_col:
        st.markdown('#### Metrics')

        tab1, tab2, tab3, tab4 = st.tabs(['Forest Loss (%)', 'Forest Loss (ha)', 'Enviromental Impact', 'EUDR Classification'])
        with tab1:
            st.markdown('##### Start date forest area')
            st.markdown(f'<div style="display: flex; justify-content: left; align-items: center; background-color: #FF4B4B; border-radius: 10px; width: {st.session_state.start_forest_cover_percent_int}%; height: 50px; padding: 5px">'
                        f'<p style="color: white; font-size: 24px; font-weight: bold; margin: 0; width: 80%;">{st.session_state.start_forest_cover_percent:.1f}%</p>'
                        '</div>', unsafe_allow_html=True)
            st.markdown(' ')
            
            st.markdown('##### End date forest area')
            
            st.markdown(f'<div style="display: flex; justify-content: left; align-items: center; background-color: #FF4B4B; border-radius: 10px; width: {st.session_state.end_forest_cover_percent_int}%; height: 50px; padding: 5px">'
                        f'<p style="color: white; font-size: 24px; font-weight: bold; margin: 0; width: 80%;">{st.session_state.end_forest_cover_percent:.1f}%</p>'
                        '</div>', unsafe_allow_html=True)

            st.markdown("###")
            st.markdown(
                    '<h3 style="color: white; font-size: 24px;">Total deforestation change</h3>'
                    '</div>', unsafe_allow_html=True)
            
            st.markdown('<div style="display: flex; justify-content: center; align-items: center; background-color: #262630; border-radius: 10px; height: 100px; padding: 5px"; border>'
                    f'<p style="color: white; font-size: 50px; font-weight: bold; margin: 0;">- {st.session_state.total_deforestation}%</p>'
                    '</div>', unsafe_allow_html=True)
        with tab2:
            st.markdown('##### Start date forest area (thousand hectares)')
            st.markdown(f'<div style="display: flex; justify-content: left; align-items: center; background-color: #FF4B4B; border-radius: 10px; width: {st.session_state.start_forest_cover_percent_int}%; height: 50px; padding: 5px">'
                        f'<p style="color: white; font-size: 24px; font-weight: bold; margin: 0; width: 80%;">{st.session_state.start_forest_cover_ha:.0f}</p>'
                        '</div>', unsafe_allow_html=True)
            st.markdown(' ')
            
            st.markdown('##### End date forest area (thousand hectares)')
            
            st.markdown(f'<div style="display: flex; justify-content: left; align-items: center; background-color: #FF4B4B; border-radius: 10px; width: {st.session_state.end_forest_cover_percent_int}%; height: 50px; padding: 5px">'
                        f'<p style="color: white; font-size: 24px; font-weight: bold; margin: 0; width: 80%;">{st.session_state.end_forest_cover_ha:.0f}</p>'
                        '</div>', unsafe_allow_html=True)

            st.markdown("###")
            st.markdown(
                    '<h3 style="color: white; font-size: 24px;">Total deforestation</h3>'
                    '</div>', unsafe_allow_html=True)
            
            st.markdown('<div style="display: flex; justify-content: center; align-items: center; background-color: #262630; border-radius: 10px; height: 100px; padding: 5px"; border>'
                    f'<p style="color: white; font-size: 50px; font-weight: bold; margin: 0;">-{st.session_state.total_deforestation:.0f}k hectares</p>'
                    '</div>', unsafe_allow_html=True)


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

# api = "http://localhost:8080/"
# if st.button("Test"):   
#     with st.spinner('Beep boop, contacting satellite :satellite_antenna:'):
#         response = requests.get(url=api, timeout=60)
#         response = response.json().get("api status")
#         st.markdown(response)




