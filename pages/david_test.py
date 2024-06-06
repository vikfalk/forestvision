from PIL import Image
import numpy as np
import datetime as dt
import requests
import streamlit as st
from PIL import Image
import pandas as pd
import datetime as dt

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

# def list_nester(input_list, sub_list_length):
#     list_length = len(input_list)
#     nested_list_length = int(list_length / sub_list_length)
#     nested_list = []
#     for i in range(nested_list_length):
#         start_index = i * sub_list_length
#         end_index = start_index + sub_list_length
#         sub_list = (input_list[start_index:end_index])
#         nested_list.append(sub_list)
#     return nested_list

# INSTRUCTION:
# Enter "# Enter "streamlit run Deforestation_Calculator.py" in the terminal to run it locally."
# Go to http://localhost:8501/david_test


col1, col2, col3 = st.columns(3)
latitude_input = float(col1.text_input('Latitude', '-8.48638'))
longitude_input = float(col2.text_input('Longitude', '-55.26209'))
col3, col4, col5 = st.columns(3)
start_timeframe = col3.date_input('Start of Timeframe', dt.datetime(2018, 6, 15))
end_timeframe = col4.date_input('End of Timeframe', dt.datetime(2024, 5, 30))
sample_number = col5.number_input('Number of Samples', 2)

params = {
        'start_timeframe': start_timeframe,
        'end_timeframe': end_timeframe,
        'longitude': longitude_input,
        'latitude': latitude_input,
        'sample_number': sample_number,
}

# REQUEST

# cloud_base_url = "https://defotra-llzimbumzq-oe.a.run.app"
# cloud_base_url = "https://tree-tracker-llzimbumzq-oe.a.run.app"
# cloud_base_url = "https://tree-tracker-llzimbumzq-oe.a.run.app"
# cloud_base_url = "https://tree-tracker-two-llzimbumzq-oe.a.run.app"
local_base_url = "http://localhost:8080"
response = requests.get(url=f"{local_base_url}/get_multiple_images_from_satellite",
                        params=params,
                        timeout=100)

# DATES
date_list_loaded = response.json().get("date_list_loaded")

# SEGEMENTED IMAGES
segmented_image_array_lists = response.json().get("segmented_img_list")
segmented_image_arrays = [np.array(list_, dtype=np.uint8).reshape((512, 512)) for list_ in segmented_image_array_lists]
segmented_image_list = [Image.fromarray(image) for image in segmented_image_arrays]

# METRICS
coverage_list = [round(((np.count_nonzero(arr == 0) / arr.size) * 100), 1) for arr in segmented_image_arrays]
coverage_list_inverted = [100 - cov for cov in coverage_list]
HECTAR_PER_IMAGE = 2621.44

# DATA
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
    st.markdown(f"<p style='text-align: center; font-family: FreeMono, monospace; font-size: 25px;'><b>Deforestation Over Time</b></p>", unsafe_allow_html=True)
    with st.container(border=True):
        cols = st.columns(len(date_list_loaded))
        for col, request_info_date, segmented_image in zip(cols, date_list_loaded, segmented_image_list):
            col.markdown(f"<p style='text-align: center; font-family: FreeMono, monospace; font-size: 14px;'><b>{request_info_date}</b></p>", unsafe_allow_html=True)
            col.image(segmented_image, use_column_width=True)
    with st.container(border=True):
        col_a, col_b = st.columns(2)
        with col_a.container(border=False):
                st.markdown(f"<p style='text-align: center; font-family: FreeMono, monospace; font-size: 15px;'><b>Coverage Lost Since Start</b></p>", unsafe_allow_html=True)
                st.bar_chart(df_perc_cumu, x="Dates", y="Coverage Loss in %")

        with col_b.container(border=False):
                st.markdown(f"<p style='text-align: center; font-family: FreeMono, monospace; font-size: 15px;'><b>Monthly Loss Rate</b></p>", unsafe_allow_html=True)
                st.bar_chart(df_ha_monthly, x="Dates", y="Monthy Loss in Hectar")

# DATA SUPPLY
renamed_df = (df
 .drop(columns=["months_since_prev"])
 .rename(columns={
    'coverage': 'Coverage in Percent',
    'days_since_prev': 'Days Passed Since Previous Cloud-Free Image',
    'cover_difference_perc': 'Forest Coverage Change in Previous Period (%)',
    'cover_difference_perc_cumu': 'Cum. Difference in Coverage in Previous Period (%)',
    'cover_difference_ha': 'Forest Area Change in Previous Period (Hectar)',
    'cover_difference_ha_cumu': 'Cum. Forest Area Change in Previous Period (Hectar)',
    'ha_per_months': 'Montly Area Loss Rate in Previous Period'
     })
 .astype('float32')
 .round(2)
)
with st.container(border=False):
    st.write(renamed_df.T)
    # Other Options:
    # st.table(renamed_df)
    # st.table(renamed_df.T)
    # st.write(renamed_df)
