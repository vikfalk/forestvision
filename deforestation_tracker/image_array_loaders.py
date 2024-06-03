from deforestation_tracker.sentinelhub_requester import search_available_L2A_tiles, request_image, sentinelhub_authorization, box_from_point
from deforestation_tracker.utils import path_constructor, timeframe_constructor
from PIL import Image
import numpy as np


def load_img_array_from_satellite(
        lat_deg: float = -8.48638,
        lon_deg: float = -55.26209,
        end_timeframe: str = "2024-05-30",
        request_type: str = "TrueColor"
        ) -> np.array:
    """Searches for available tiles at the requested date,
    then downloads the best image array. Returns array and date."""

    # time_interval_6m = timeframe_constructor(end_timeframe, temporal_padding=91)

    box_ = box_from_point(lat_deg=lat_deg, lon_deg=lon_deg, image_size_px=512, resolution_m_per_px=10)

    # Authorize session
    config_, catalog_ = sentinelhub_authorization()

    # Search for tiles
    #to_be_logged = (f"Searching for in {box_} on date: {end_timeframe}")
    optimal_tile = search_available_L2A_tiles(catalog=catalog_, bbox=box_, date_request=end_timeframe, range_days=91, maxCloudCoverage=10)
    if optimal_tile:
        # Request tile
        img_array = request_image(
            box=box_, time_interval=(optimal_tile.get('date'), optimal_tile.get('date')), config=config_,
            image_size_px=512, resolution_m_per_px=10,  request_type=request_type
        )
        #to_be_logged = (f"found optimal tile with penalty of {optimal_tile.get('penalty')}. Shape: {img_array.shape}, Mean: {img_array.flatten().mean()}")
        return img_array, optimal_tile.get('date')
    else:
        #to_be_logged = (f"no tiles found for {end_timeframe} plus/minus 3 months with less than 10% Clouds.")
        return None, None


def load_img_array_locally(image_name_without_ending="after_resized"):
    input_path, output_path = path_constructor(image_name_without_ending)
    img = Image.open(input_path)
    img_array = np.array(img) / 255.0
    return img_array


# img_array, request_info = load_img_array_from_satellite()
# print(request_info)
