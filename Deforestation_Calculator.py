import streamlit as st
import datetime as dt
import pydeck as pdk
from PIL import Image
import requests
import numpy as np
from processing.frontend_processing import smooth_and_vectorize
import streamlit_lottie
import io

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
    st.session_state.total_calculated_overlay = placeholder_image
    st.session_state.total_calculated_overlay_map = None
    st.session_state.longitude_input = -55.26000
    st.session_state.longitude_input = -8.49000
    st.session_state.end_timeframe = dt.datetime(2024, 1, 1)
    st.session_state.start_timeframe = dt.datetime(2021, 1, 1)
    
    st.session_state.expander_open = False
    st.session_state.info_intro = ' '
    st.session_state.start_info = ' '
    st.session_state.end_info = ' '
    
    st.session_state.zoom = 1
    
    # st.session_state.forest_color = '#0C8346'
    # st.session_state.deforestation_color = '#FF4C4B'

st.set_page_config(
    page_title="AI-Driven Deforestation Tracker",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

filler_col, animation_col, intro_col, info_col = st.columns([2, 5, 23, 5])
with animation_col:
        st.lottie("https://lottie.host/9bc48342-5206-4456-8ea4-cce828f5fe15/fQVJJlzp4j.json", height = 180)
    
with intro_col:
    st.markdown("<h1 style='text-align: left; font-family: FreeMono, monospace;font-size: 75px; color: #FFFFFF;'>TreeTracker AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: left; alphafont-size: 16px; opacity: 0.5; color: #FFFFFF;'>Track forest area change of an area using real-time satellite data by inputting coordinates on the left or choosing an example on the right.</h1>", unsafe_allow_html=True)

input_col1, map_col, example_col = st.columns([5, 20, 4])
with input_col1:    
    st.markdown("<p style='text-align: center; font-family: FreeMono, monospace; font-size: 15px;'><b>Inputs</b></p>", unsafe_allow_html=True)

    with st.container(border=True, height= 470):

        st.session_state.latitude_input = st.text_input('Latitude', '-8.49000', 
                                                        help = "Enter the longitude coordinates of your desired area of interest. Press enter to view on map.")
        st.session_state.longitude_input = st.text_input('Longitude', '-55.26000')
        
        
        start_timeframe = st.date_input('Start date', dt.datetime(2021, 1, 1), 
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
        # square_size = st.select_slider('Square length (km)', 
        #                              options=square_size_options, 
        #                              value=default_value, 
        #                              format_func=lambda x: labels[x])

        #     #sample_number = st.slider('Number of samples', min_value=1, max_value=10)
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

        everything_api = "http://localhost:8080/do_everything_self"
        #everything_api = "https://south-american-forest-llzimbumzq-oe.a.run.app/do_everything_self"
        if st.button("**Calculate deforestation**", use_container_width=True, type='primary', help= 'Click me to calculate deforestation.'):   
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
            
                #start vector
                start_mask_vector = smooth_and_vectorize(start_mask_image_array, 9, '#00B272', 0.5) #color of initial forest
                start_mask_vector = start_mask_vector.convert('RGBA')
                st.session_state.start_vector_overlay = start_mask_vector
                
                #start overlay
                start_mask_image_rgba = start_mask_image.convert('RGBA')
                start_overlay = Image.alpha_composite(start_sat_image, start_mask_vector)
                st.session_state.start_overlay = start_overlay
                
                # start metrics
                start_forest_cover_percent = round(((np.count_nonzero(start_mask_image_array != 0) / start_mask_image_array.size) * 100), 1)
                st.session_state.start_forest_cover_percent = start_forest_cover_percent
                st.session_state.start_forest_cover_percent_int = int(start_forest_cover_percent)
                
                start_forest_cover_ha = ((start_forest_cover_percent/100)*26214400)/10000
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
                
                #End vector
                end_mask_vector = smooth_and_vectorize(end_mask_image_array, 9, '#0C8346', 0.5) #colour of remaining forest
                end_mask_vector = end_mask_vector.convert('RGBA')
                st.session_state.end_vector_overlay = end_mask_vector
                
                #End overlay
                end_mask_image_rgba = end_mask_image.convert('RGBA')
                end_overlay = Image.alpha_composite(end_sat_image, end_mask_vector)
                st.session_state.end_overlay = end_overlay
            
                # End metrics
                end_forest_cover_percent = round(((np.count_nonzero(end_mask_image_array != 0) / end_mask_image_array.size) * 100), 1)
                st.session_state.end_forest_cover_percent = end_forest_cover_percent
                st.session_state.end_forest_cover_percent_int = int(end_forest_cover_percent)
                
                end_forest_cover_ha = ((end_forest_cover_percent/100)* 26214400)/10000
                st.session_state.end_forest_cover_ha = end_forest_cover_ha
                
                # image info
                start_info = response.json().get("start_date_info")
                end_info = response.json().get("end_date_info")
                st.session_state.info_intro = f'The closest cloud-free images to your desired start and end dates are from:'
                st.session_state.start_info = start_info
                st.session_state.end_info = end_info
                
                #Calculated overlay
                total_overlay_calculated_array  = start_mask_image_array - end_mask_image_array 
                total_overlay_calculated_array = smooth_and_vectorize(total_overlay_calculated_array, 9, '#FF4C4B', 0.5) #color of deforested forest
                total_overlay_calculated = total_overlay_calculated_array.convert('RGBA')
                total_calculated_overlay = Image.alpha_composite(end_overlay, total_overlay_calculated)
                st.session_state.total_calculated_overlay = total_calculated_overlay
                
                #Total overlay
                total_overlay = Image.alpha_composite(end_overlay, start_mask_vector)
                st.session_state.total_overlay = total_overlay
                
                #Total metrics
                total_deforestation = round(((end_forest_cover_percent/start_forest_cover_percent)*100),1)
                st.session_state.total_deforestation = total_deforestation
                
                st.session_state.expander_open = True
                st.session_state.show_expander = True
                st.session_state.zoom = 12.5
                
                #st.balloons()
        
with example_col:
    st.markdown("<p style='text-align: center; font-family: FreeMono, monospace;font-size: 15px;'><b>Examples</b></p>", unsafe_allow_html=True)
    with st.container(border=True, height = 228):
        st.image('brazil.png') #3000 x 1690 px
        #st.image('https://vikfalk.github.io/deforestation_frontend/example_images/brazil.png')
        if st.button('View on map   ', use_container_width=True):
            st.session_state.latitude_input = -5.49000
            st.session_state.longitude_input = -58.26000
            st.session_state.zoom = 12.5
        if st.button('Calculate ', use_container_width=True, type='primary'):
            with st.spinner('Beep boop, contacting satellite :satellite_antenna:'):
                st.session_state.latitude_input = -5.49000
                st.session_state.longitude_input = -58.26000
                st.session_state.start_timeframe = "2020-10-10" 
                st.session_state.end_timeframe = "2020-10-10"
                st.session_state.zoom = 12
                
                params= {
                        'start_timeframe': st.session_state.start_timeframe,
                        'end_timeframe': st.session_state.end_timeframe,
                        'longitude': st.session_state.longitude_input,
                        'latitude': st.session_state.latitude_input,
                        'sample_number': sample_number,
                        'square_size': square_size
                    }
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
                
                st.session_state.total_calculated_overlay_map = start_mask_vector
                

                # start metrics
                start_forest_cover_percent = round(((np.count_nonzero(start_mask_image_array != 0) / start_mask_image_array.size) * 100), 1)
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
                end_mask_vector = smooth_and_vectorize(end_mask_image_array, 9, '#307251', 0.4)
                end_mask_vector = end_mask_vector.convert('RGBA')
                st.session_state.end_vector_overlay = end_mask_vector
                
                #End overlay
                end_mask_image_rgba = end_mask_image.convert('RGBA')
                end_overlay = Image.alpha_composite(end_sat_image, end_mask_vector)
                st.session_state.end_overlay = end_overlay
            
                # End metrics
                end_forest_cover_percent = round(((np.count_nonzero(end_mask_image_array != 0) / end_mask_image_array.size) * 100), 1)
                st.session_state.end_forest_cover_percent = end_forest_cover_percent
                st.session_state.end_forest_cover_percent_int = int(end_forest_cover_percent)
                
                end_forest_cover_ha = ((end_forest_cover_percent/100)* 26214400)/1000
                st.session_state.end_forest_cover_ha = end_forest_cover_ha
                
                #Calculated overlay
                total_overlay_calculated_array  = start_mask_image_array - end_mask_image_array 
                total_overlay_calculated_array = smooth_and_vectorize(total_overlay_calculated_array, 9, '#FF0000', 0.4)
                total_overlay_calculated = total_overlay_calculated_array.convert('RGBA')
                total_calculated_overlay = Image.alpha_composite(end_overlay, total_overlay_calculated)
                
                #Total overlay
                total_overlay = Image.alpha_composite(end_overlay, start_mask_vector)
                st.session_state.total_overlay = total_overlay
                
                #Total metrics
                total_deforestation = round(((end_forest_cover_percent/start_forest_cover_percent)*100),1)
                st.session_state.total_deforestation = total_deforestation   
   
    with st.container(border=True, height = 228):
        st.image('peru.png') #3000 x 1690 px
        if st.button('View on map ', use_container_width=True):
            st.session_state.latitude_input = -5.49000
            st.session_state.longitude_input = -58.26000
        if st.button('Calculate', use_container_width=True, type='primary'):
            with st.spinner('Beep boop, contacting satellite :satellite_antenna:'):
                st.session_state.latitude_input = -5.49000
                st.session_state.longitude_input = -58.26000
                st.session_state.start_timeframe = "2020-10-10" 
                st.session_state.end_timeframe = "2020-10-10" 
                
                params= {
                        'start_timeframe': st.session_state.start_timeframe,
                        'end_timeframe': st.session_state.end_timeframe,
                        'longitude': st.session_state.longitude_input,
                        'latitude': st.session_state.latitude_input,
                        'sample_number': sample_number,
                        'square_size': square_size
                    }
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
                
                st.session_state.total_calculated_overlay_map = start_mask_vector
                

                # start metrics
                start_forest_cover_percent = round(((np.count_nonzero(start_mask_image_array != 0) / start_mask_image_array.size) * 100), 1)
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
                end_mask_vector = smooth_and_vectorize(end_mask_image_array, 9, '#307251', 0.4)
                end_mask_vector = end_mask_vector.convert('RGBA')
                st.session_state.end_vector_overlay = end_mask_vector
                
                #End overlay
                end_mask_image_rgba = end_mask_image.convert('RGBA')
                end_overlay = Image.alpha_composite(end_sat_image, end_mask_vector)
                st.session_state.end_overlay = end_overlay
            
                # End metrics
                end_forest_cover_percent = round(((np.count_nonzero(end_mask_image_array != 0) / end_mask_image_array.size) * 100), 1)
                st.session_state.end_forest_cover_percent = end_forest_cover_percent
                st.session_state.end_forest_cover_percent_int = int(end_forest_cover_percent)
                
                end_forest_cover_ha = ((end_forest_cover_percent/100)* 26214400)/1000
                st.session_state.end_forest_cover_ha = end_forest_cover_ha
                
                #Calculated overlay
                total_overlay_calculated_array  = start_mask_image_array - end_mask_image_array 
                total_overlay_calculated_array = smooth_and_vectorize(total_overlay_calculated_array, 9, '#994636', 0.4)
                total_overlay_calculated = total_overlay_calculated_array.convert('RGBA')
                total_calculated_overlay = Image.alpha_composite(end_overlay, total_overlay_calculated)
                
                #Total overlay
                total_overlay = Image.alpha_composite(end_overlay, start_mask_vector)
                st.session_state.total_overlay = total_overlay
                
                #Total metrics
                total_deforestation = round(((end_forest_cover_percent/start_forest_cover_percent)*100),1)
                st.session_state.total_deforestation = total_deforestation   

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

# Convert end_mask_vector to pydeck polygon layer
end_mask_polygon_layer = pdk.Layer(
    "PolygonLayer", 
    data=None, 
    get_polygon=st.session_state.total_calculated_overlay_map,
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

BOUNDS = square_coords

with map_col:
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/satellite-v9',
        initial_view_state=view_state,
        layers=[polygon_layer], # Add the BitmapLayer here
        tooltip=True
    ))

if 'show_expander' not in st.session_state:
    st.session_state.show_expander = False

if st.session_state.show_expander:
    with st.expander(label='Output', expanded=st.session_state.expander_open):
        st.markdown(f'{st.session_state.info_intro} {st.session_state.start_info} and {st.session_state.end_info}')
        
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
            st.image(st.session_state.total_calculated_overlay)
            st.markdown('🟩 Remaining forest 🟥 Deforestation ')
                    
            buffer = io.BytesIO()
            st.session_state.total_calculated_overlay.save(buffer, format="PNG")
            buffer.seek(0)
            
            # forest_color = st.color_picker('Pick the colour of the forest overlay')
            # deforestation_color = st.color_picker('Pick the colour of the deforestation overlay ')
            
        
        with metrics_col:
            st.markdown('#### Metrics')

            forest_loss_percent_tab, forest_loss_ha_tab, tab3, tab4 = st.tabs(['Forest Loss (%)', 'Forest Loss (ha)', 'Enviromental Impact', 'EUDR Classification'])
            with forest_loss_percent_tab:
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
                
                st.markdown(' ')
                st.download_button(
                label="Download image 💾 ",
                data=buffer,
                file_name=f"deforestatation{st.session_state.start_info}/{st.session_state.end_info}.png",
                mime="image/png"
        )
                
            with forest_loss_ha_tab:
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