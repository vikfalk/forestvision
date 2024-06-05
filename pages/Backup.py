import streamlit as st
import datetime as dt
import pydeck as pdk
from PIL import Image
import requests
import numpy as np
from processing.frontend_processing import smooth_and_vectorize, overlay_vector_on_mask

placeholder_image = Image.new("RGB", (512, 512), (15, 17, 22))

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