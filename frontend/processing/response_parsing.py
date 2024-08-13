import io
import base64
import numpy as np
from typing import List, Tuple
import requests
from PIL import Image


def base64_to_numpy(img_b64):
    """
    Takes a base64 encoded image array, decodes it and returns a (numpy) image array.
    """
    img_bytes = io.BytesIO(base64.b64decode(img_b64))
    img_array = np.load(img_bytes)
    return img_array


def request_satellite_images(url, latitude, longitude, start_date, end_date, sample_number=2):
    response = requests.get(
        url=url,
        params={
            'start_timeframe': start_date,
            'end_timeframe': end_date,
            'longitude': longitude,
            'latitude': latitude,
            'sample_number': sample_number,
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
