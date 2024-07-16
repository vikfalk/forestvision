import numpy as np
from sentinelhub import SentinelHubDownloadClient
from backend.sentinelhub_requester import search_available_L2A_tiles, request_image, sentinelhub_authorization, box_from_point, sentinel_build_request


def load_img_array_from_satellite(
        lat_deg: float = -8.48638,
        lon_deg: float = -55.26209,
        end_timeframe: str = "2024-05-30",
        request_type: str = "TrueColor") -> np.array:
    """Loads a satellite image array from sentinel hub, scales it and returns it."""


    # time_interval_6m = timeframe_constructor(end_timeframe, temporal_padding=91)

    box_ = box_from_point(lat_deg=lat_deg, lon_deg=lon_deg, image_size_px=512, resolution_m_per_px=10)

    # Authorize session
    config_, catalog_ = sentinelhub_authorization()

    # Search for tiles
    #to_be_logged = (f"Searching for in {box_} on date: {end_timeframe}")
    optimal_tile = search_available_L2A_tiles(catalog=catalog_, bbox=box_, date_request=end_timeframe, range_days=91, maxCloudCoverage=10)
    if optimal_tile:
        # Request tile
        #print(optimal_tile)
        img_array = request_image(
            box=box_, time_interval=(optimal_tile.get('date'), optimal_tile.get('date')), config=config_,
            image_size_px=512, resolution_m_per_px=10,  request_type=request_type
        )
        #to_be_logged = (f"found optimal tile with penalty of {optimal_tile.get('penalty')}. Shape: {img_array.shape}, Mean: {img_array.flatten().mean()}")
        return img_array, optimal_tile.get('date')
    else:
        #to_be_logged print(f"no tiles found for {end_timeframe} plus/minus 3 months with less than 10% Clouds.")
        return None, None

def load_multiple_imgs_from_sat_vis(
        lat_deg: float = -8.48638,
        lon_deg: float = -55.26209,
        date_list: list = ["2020-05-30", "2024-05-30"],
        request_type: str = "TrueColor"):
    """Loads available satellite image arrays from sentinel hub at multiple times."""

    box = box_from_point(lat_deg=lat_deg, lon_deg=lon_deg, image_size_px=512, resolution_m_per_px=10)

    # Authorize session
    config, catalog_ = sentinelhub_authorization()
    date_list_available = []
    # search for available dates
    for date_i in date_list:
        # Search for tiles
        optimal_tile = search_available_L2A_tiles(catalog=catalog_, bbox=box, date_request=date_i, range_days=91, maxCloudCoverage=10)
        if optimal_tile:
           date_list_available.append(optimal_tile.get('date'))
    list_of_requests= [sentinel_build_request(config=config, box=box, request_type='TrueColor', request_date=(date_i, date_i)) for date_i in date_list_available]
    list_of_requests = [request.download_list[0] for request in list_of_requests]
    img_arrays = SentinelHubDownloadClient(config=config).download(list_of_requests, max_threads=5)
    return date_list_available, img_arrays

def load_multiple_imgs_from_sat(
        lat_deg: float = -8.48638,
        lon_deg: float = -55.26209,
        date_list: list = ["2020-05-30", "2024-05-30"]):
    """Loads available satellite image arrays from sentinel hub at multiple times."""

    box = box_from_point(lat_deg=lat_deg, lon_deg=lon_deg, image_size_px=512, resolution_m_per_px=10)

    # Authorize session
    config, catalog_ = sentinelhub_authorization()
    date_list_available = []
    # search for available dates
    for date_i in date_list:
        # Search for tiles
        optimal_tile = search_available_L2A_tiles(catalog=catalog_, bbox=box, date_request=date_i, range_days=91, maxCloudCoverage=10)
        if optimal_tile:
           date_list_available.append(optimal_tile.get('date'))
    list_of_requests_vis= [sentinel_build_request(config=config, box=box, request_type='TrueColor', request_date=(date_i, date_i)) for date_i in date_list_available]
    list_of_requests_fourband= [sentinel_build_request(config=config, box=box, request_type='4-band', request_date=(date_i, date_i)) for date_i in date_list_available]
    list_of_requests = list_of_requests_vis + list_of_requests_fourband
    list_of_requests = [request.download_list[0] for request in list_of_requests]
    img_arrays = SentinelHubDownloadClient(config=config).download(list_of_requests, max_threads=5)
    return date_list_available, img_arrays
