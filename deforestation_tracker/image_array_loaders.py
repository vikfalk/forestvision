from deforestation_tracker.sentinelhub_requester import request_image, sentinelhub_authorization
from deforestation_tracker.utils import path_constructor, timeframe_constructor
from PIL import Image
import numpy as np

def load_img_array_from_satellite(
        lat_deg: float = -8.48638,
        lon_deg: float = -55.26209,
        # end_timeframe: str = "datetime.date(2024, 5, 30)", # let's try with "2024-05-30"
        end_timeframe: str = "2024-05-30",
        ) -> np.array:
    """Loads a satellite image array from sentinel hub, scales it and returns it."""
    time_interval_=timeframe_constructor(end_timeframe)
    config = sentinelhub_authorization()
    img_array = request_image(
        lat_deg=lat_deg, lon_deg=lon_deg, time_interval=time_interval_,
        config=config, pixel_size=512, resolution=10,  request_type='TrueColor'
    )
    # img_array = np.array(img_array) / 255.0  # seems like it is already scaled
    return img_array

def load_img_array_locally(image_name_without_ending="after_resized"):
    input_path, output_path = path_constructor(image_name_without_ending)
    img = Image.open(input_path)
    img_array = np.array(img) / 255.0
    return img_array
