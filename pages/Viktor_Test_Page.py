import streamlit as st
import datetime as dt
import pydeck as pdk
from PIL import Image
import requests
import numpy as np
from processing.frontend_processing import smooth_and_vectorize
import streamlit_lottie
import io
import pandas as pd
import streamlit as st
import pandas as pd

# Creating the data
data = {
    '2020-06-15': [86.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    '2020-12-02': [79.8, -6.2, -162.5, -6.2, -162.5, 170.0, 5.6, -29.1],
    '2021-08-04': [73.1, -6.7, -175.6, -12.9, -338.2, 245.0, 8.0, -21.8],
    '2022-04-26': [91.1, 18.0, 471.9, 5.1, 133.7, 265.0, 8.7, 54.2],
    '2022-09-03': [19.2, -71.9, -1884.8, -66.8, -1751.1, 130.0, 4.3, -441.3],
}

# Creating the DataFrame
columns = ['coverage', 'cover_difference_perc', 'cover_difference_ha', 'cover_difference_perc_cumu', 
           'cover_difference_ha_cumu', 'days_since_prev', 'months_since_prev', 'ha_per_months']

df = pd.DataFrame(data, index=columns)

# Transposing the DataFrame to get the dates as rows
df = df.T
st.table(df)

sat_col, forest_col, filler, overlay_col, metrics_col = st.columns([2, 2, 1, 6, 5])

with metrics_col:
    forest_loss_percent_tab, forest_loss_ha_tab, tab3, tab4 = st.tabs(['Forest Loss (%)', 'Forest Loss (ha)', 'Environmental Impact', 'EUDR Classification'])
    with forest_loss_percent_tab:
        st.markdown("##### Forest loss over timeframe")
        df_perc = df[['coverage']][0:2]
        st.line_chart(df_perc, color='#00B272',
                      height=260)
        
        st.markdown("##### Forest loss over timeframe")
        df_perc = df[['coverage']][0:2]
        st.bar_chart(df_perc, color= '#FF4C4B', height=260)
        
        st.markdown("##### Forest loss over timeframe")
        df_perc = df[['cover_difference_perc']]
        st.line_chart(df_perc, color='#FF4C4B',
                      height=260)
        
        st.markdown("##### Forest loss over timeframe")
        df_perc = df[['cover_difference_perc']]
        st.bar_chart(df_perc, color= '#00B272', height=260)
