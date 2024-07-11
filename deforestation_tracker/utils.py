import re
import numpy as np
from PIL import Image
import datetime as dt

def timeframe_constructor(datetime_string="2021-01-01", temporal_padding=14):
    """Takes the '2021-01-01' string from the UI and returns a
    tuple of date strings in the format YY-MM-DD."""
    date_tuple = (int(datetime_string[0:4]), int(datetime_string[5:7]), int(datetime_string[8:10]))
    dt_object = dt.datetime(year=date_tuple[0], month=date_tuple[1], day=date_tuple[2])
    timeframe_start = dt_object - dt.timedelta(days=temporal_padding)
    timeframe_end = dt_object + dt.timedelta(days=temporal_padding)
    time_interval = (timeframe_start.strftime("%Y-%m-%d"), timeframe_end.strftime("%Y-%m-%d"))
    return time_interval

def calculate_black_coverage(image_array):
    total_pixels = image_array.size
    black_pixels = np.sum(image_array == 0)
    return black_pixels / total_pixels * 100

def compare_black_coverage_of_img_arrays(array_1, array_2):
    forest_coverage_1 = calculate_black_coverage(array_1)
    forest_coverage_2 = calculate_black_coverage(array_2)
    change_phrase = "an increase" if forest_coverage_1 < forest_coverage_2 else "a decrease"
    change_percentage = round(((forest_coverage_2 - forest_coverage_1) / forest_coverage_1) * 100, 2)

    result_string = (f"""
    The forest coverage on the first image is {round(forest_coverage_1, 2)} %,
    the forest coverage on the second image is {round(forest_coverage_2, 2)} %.
    That is {change_phrase} of {change_percentage} %.
    """)
    return result_string

def compare_black_coverage_of_png_files(
    image_1_path="./segmented_output_files/generic_test.png",
    image_2_path="./segmented_output_files/without_clouds.png",
    ):

    image_1 = Image.open(image_1_path)
    image_2 = Image.open(image_2_path)

    array_1 = np.array(image_1)
    array_2 = np.array(image_2)

    forest_coverage_1 = calculate_black_coverage(array_1)
    forest_coverage_2 = calculate_black_coverage(array_2)
    change_phrase = "an increase" if forest_coverage_1 < forest_coverage_2 else "a decrease"
    change_percentage = round(((forest_coverage_2 - forest_coverage_1) / forest_coverage_1) * 100, 2)

    result_string = (f"""
    The forest coverage on the first image is {round(forest_coverage_1, 2)} %,
    the forest coverage on the second image is {round(forest_coverage_2, 2)} %.
    That is {change_phrase} of {change_percentage} %.
    """)
    return result_string

def scale_image(img, clip=False):
    """
    Not used anymore as of May 30th.
    After realizing that clipping does not increase unet-attention-3D
    model performance, this may only be used for visualization."""
    img_array = np.array(img) / 255.0
    if clip:
        img_array_ = img_array * 3.5
        img_array_ = np.clip(a=img_array_, a_min=0, a_max=1)
    return img_array_

def timeframe_constructor_pseudo_dt(datetime_string="datetime.date(2021, 1, 1)", temporal_padding=14):
    """
    Not used anymore as of May 30th.
    Takes the 'datetime.date(2021, 1, 1)' string from the UI and returns a
    tuple of date strings in the format YY-MM-DD."""
    date_tuple = date_extractor(datetime_string)
    dt_object = dt.datetime(year=date_tuple[0], month=date_tuple[1], day=date_tuple[2])
    timeframe_start = dt_object - dt.timedelta(days=temporal_padding)
    timeframe_end = dt_object + dt.timedelta(days=temporal_padding)
    time_interval = (timeframe_start.strftime("%Y-%m-%d"), timeframe_end.strftime("%Y-%m-%d"))
    return time_interval

def date_extractor(datetime_string):
    """
    Not used anymore as of May 30th.
    Takes the 'datetime.date(2021, 1, 1)' string from the UI and returns an
    integer tuple resembling year, month and day.
    Used by the function timeframe_constructor_pseudo_dt()."""
    pattern = r"\((\d+),\s*(\d+),\s*(\d+)\)"
    match = re.search(pattern, datetime_string)
    year, month, day = match.groups()
    return (int(year), int(month), int(day))
