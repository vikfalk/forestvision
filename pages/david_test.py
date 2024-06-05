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
        difference.days
        return difference.days
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
start_timeframe = col3.date_input('Start of Timeframe', dt.datetime(2020, 6, 15))
end_timeframe = col4.date_input('End of Timeframe', dt.datetime(2024, 5, 30))
sample_number = col5.number_input('Number of Samples', 2)

# Assembled User Input Parameters
params = {
        'start_timeframe': start_timeframe,
        'end_timeframe': end_timeframe,
        'longitude': longitude_input,
        'latitude': latitude_input,
        'sample_number': sample_number,
}

# start_timeframe: str = "2020-05-13",
# end_timeframe: str = "2024-05-30",
# longitude: str = "-55.26209",
# latitude: str = "-8.48638",
# sample_number: str = "2"):

# API Stuff
st.title("Fetch Image from Satellite Using User Inputs")

# cloud_base_url = "https://defotra-llzimbumzq-oe.a.run.app"
# cloud_base_url = "https://tree-tracker-llzimbumzq-oe.a.run.app"
# cloud_base_url = "https://tree-tracker-llzimbumzq-oe.a.run.app"
# cloud_base_url = "https://tree-tracker-two-llzimbumzq-oe.a.run.app"
local_base_url = "http://localhost:8080"

if st.button("Test get_multiple_images_from_satellite"):
    statement = """
    Assumption:
    JSONResponse objects has three keys:
    1) date_list_loaded: a list of strings in the format "YYYY-MM-DD"
    2) original_image_list: a list of flattened (to list) arrays
    3) segmented_image_list: a list of flattened (to list) arrays
    """

    response = requests.get(url=f"{local_base_url}/get_multiple_images_from_satellite",
                            params=params,
                            timeout=100)

    date_list_loaded = response.json().get("date_list_loaded")

    original_image_array_lists = response.json().get("original_img_list")
    original_image_array = [np.array(list_, dtype=np.float32).reshape((512, 512, 4)) for list_ in original_image_array_lists]
    original_image_list = [Image.fromarray((array * 255).astype(np.uint8)).convert('RGBA') for array in original_image_array]

    segmented_image_array_lists = response.json().get("segmented_img_list")
    segmented_image_arrays = [np.array(list_, dtype=np.uint8).reshape((512, 512)) for list_ in segmented_image_array_lists]
    segmented_image_list = [Image.fromarray(image) for image in segmented_image_arrays]

    # METRICS
    coverage_list = [round(((np.count_nonzero(arr == 0) / arr.size) * 100), 1) for arr in segmented_image_arrays]
    coverage_list_inverted = [100 - cov for cov in coverage_list]
    HECTAR_PER_IMAGE = 2621.44

    df = (pd.DataFrame({
            "date": date_list_loaded,
            "coverage": coverage_list_inverted})
        .assign(coverage_prev_year=lambda df_: df_.coverage.shift(1))
        .assign(prev_date=lambda df_: df_.date.shift(1))
        .assign(cover_difference_perc=lambda df_: df_.coverage - df_.coverage_prev_year)
        .assign(cover_difference_ha=lambda df_: (df_.coverage - df_.coverage_prev_year) / 100 * HECTAR_PER_IMAGE)
        .assign(cover_difference_perc_cumu=lambda df_: df_.cover_difference_perc.cumsum())
        .assign(cover_difference_ha_cumu=lambda df_: df_.cover_difference_ha.cumsum())
        .assign(days_since_prev=lambda df_: df_.apply(day_difference_calculator, axis=1))
        .assign(months_since_prev=lambda df_: df_.days_since_prev / 30.437)
        .assign(ha_per_months=lambda df_: df_.cover_difference_ha / df_.months_since_prev)
        .drop(columns=["coverage_prev_year", "prev_date"])
        .fillna(0)
        .set_index("date")
        .round(1)
    )

    df_perc = df[["cover_difference_perc", "cover_difference_perc_cumu"]]
    st.line_chart(df_perc)

    df_ha = df[["cover_difference_ha", "cover_difference_ha_cumu", "ha_per_months"]]
    st.line_chart(df_ha)

    st.table(df.T)

    cols = st.columns(len(original_image_list))
    for col, request_info_date, original_image, segmented_image in zip(cols, date_list_loaded, original_image_list, segmented_image_list):
        col.header(request_info_date)
        col.image(original_image, use_column_width=True)
        col.image(segmented_image, use_column_width=True)


# tab1, tab2, tab3, tab4 = st.tabs(['Forest Loss (%)', 'Forest Loss (ha)', 'Enviromental Impact', 'EUDR Classification'])
# with tab1:
#     st.markdown('##### Start date forest area')

# with tab2:
#     st.markdown('##### Start date forest area (thousand hectares)')
