import io
import base64
import datetime as dt
import numpy as np
import pandas as pd
import cv2
from typing import List
from PIL import Image, ImageFilter

HECTAR_PER_IMAGE = 2621.44

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

def convert_to_ha(percentage: float) -> float:
    ha = percentage / 100 * HECTAR_PER_IMAGE
    return ha

def calculate_metrics(
        dates: List[str],
        segmented_images: List[np.ndarray]
    ) -> pd.DataFrame:
    coverage_list = [np.count_nonzero(arr == 0) / arr.size * 100 for arr in segmented_images]
    coverage_list_inverted = [100 - cov for cov in coverage_list]
    pd.set_option('future.no_silent_downcasting', True)
    dataframe = (
        pd.DataFrame({
            "date": dates,
            "coverage": coverage_list_inverted
        })
        .assign(prev_coverage=lambda df_: df_.coverage.shift(1))
        .assign(prev_date=lambda df_: df_.date.shift(1))
        .assign(cover_diff_rel=lambda df_: (
            df_.coverage - df_.prev_coverage) / df_.prev_coverage * 100
        )
        .assign(cover_diff_pp=lambda df_: df_.coverage - df_.prev_coverage)
        .assign(cover_diff_pp_cum=lambda df_: df_.cover_diff_pp.cumsum())
        .assign(cover_diff_ha=lambda df_: (
            df_.coverage - df_.prev_coverage) / 100 * HECTAR_PER_IMAGE
        )
        .assign(cover_diff_ha_cum=lambda df_: df_.cover_diff_ha.cumsum())
        .assign(days_since_prev=lambda df_: df_.apply(day_difference_calculator, axis=1))
        .assign(months_since_prev=lambda df_: df_.days_since_prev / 30.437)
        .assign(loss_per_months_ha=lambda df_: df_.cover_diff_ha / df_.months_since_prev)
        .drop(columns=["prev_coverage", "prev_date"])
        .assign(date=lambda df_: df_.apply(date_reformatter, axis=1))
        .fillna(0)
        .infer_objects()
        .set_index("date")
    )
    return dataframe

def label(df: pd.DataFrame) -> pd.DataFrame:
    labelled_df = (df
    .drop(columns=["months_since_prev"])
    .rename(columns={
        'date': 'Dates',
        'coverage': 'Coverage (%)',
        'days_since_prev': 'Time Passed Since Previous Cloud-Free Image (Days)',
        'cover_diff_rel': 'Relative Change in Coverage (Previous Period, %)',
        'cover_diff_pp': 'Difference in Coverage (Previous Period, pp)',
        'cover_diff_pp_cum': 'Difference in Coverage (Cumulative, pp)',
        'cover_diff_ha': 'Forest Area Change (Previous Period, ha)',
        'cover_diff_ha_cum': 'Forest Area Change (Cumulative, ha)',
        'loss_per_months_ha': 'Forest Area Change Rate (Previous Period, Monthly)'
        })
    .astype('float32')
    .round(2)
    )
    return labelled_df

def smooth_and_vectorize(array, hex_code, smoothing=9, opacity=0.5):
    '''
    Takes the model output array, smooths, colours, defines opacity,
    and makes background transparent.
    smoothing = odd int e.g. 1, 3, 5, 7
    hex_code = str hexcode of colour e.g. #FF0000 (red)
    opacity = float between 0 - 1
    '''
    array_resized = cv2.resize(array, (512, 512))

    # Convert numpy array to PIL Image
    array_rgba = np.zeros((512, 512, 4), dtype=np.uint8)
    array_rgba[:, :, 0] = array_resized  # Copy the grayscale values to all RGB channels
    array_rgba[:, :, 1] = array_resized
    array_rgba[:, :, 2] = array_resized
    array_rgba[:, :, 3] = np.where(array_resized == 255, 0, 255)  # Set alpha channel based on white pixels

    image = Image.fromarray(array_rgba)

    # Apply Median Filter
    med_img = image.filter(ImageFilter.MedianFilter(size=smoothing))

    # Convert the smoothed image to grayscale
    smoothed_image = med_img.convert("L")

    # Convert to numpy array
    smoothed_array = np.array(smoothed_image)

    # Binarize the smoothed image (invert the binary image)
    _, binary_image = cv2.threshold(smoothed_array, 127, 255, cv2.THRESH_BINARY)

    # Create a mask from the binary image
    mask = Image.fromarray(binary_image).convert("L")

    # Create an RGBA image with the specified color

    #Convert hex into RGB
    hex_code = hex_code.lstrip('#')

    # Convert the hex code to RGB components
    r = int(hex_code[0:2], 16)
    g = int(hex_code[2:4], 16)
    b = int(hex_code[4:6], 16)

    opacity = int(opacity * 255)
    rgba = (r, g, b, opacity)

    color_img = Image.new("RGBA", image.size, rgba)

    # Composite the color image with the mask
    smooth_coloured_vector = Image.composite(
        color_img,
        Image.new("RGBA", image.size, (0, 0, 0, 0)),
        mask
    )
    smooth_coloured_vector_rgba = smooth_coloured_vector.convert("RGBA")
    return smooth_coloured_vector_rgba


def overlay_vector_on_mask(vector, mask):
    mask_rgba= mask.convert("RGBA")
    return Image.alpha_composite(mask_rgba, vector)
