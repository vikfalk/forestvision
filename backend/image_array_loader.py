from typing import List
from sentinelhub import SentinelHubDownloadClient
from backend.sentinelhub_requester import (
    search_available_l2a_tiles,
    sentinelhub_authorization,
    box_from_point,
    sentinel_build_request
)


def load_multiple_imgs_from_sat(
        lat_deg: float,
        lon_deg: float,
        date_list: List[str]
    ):
    """Loads available image arrays from sentinel hub at multiple times."""

    box = box_from_point(
        lat_deg=lat_deg,
        lon_deg=lon_deg,
        image_size_px=512,
        resolution_m_per_px=10
    )

    # Authorize session
    config, catalog_ = sentinelhub_authorization()
    date_list_available = []
    # search for available dates
    for date_i in date_list:
        # Search for tiles
        optimal_tile = search_available_l2a_tiles(
            catalog=catalog_,
            bbox=box,
            date_request=date_i,
            range_days=91,
            max_cloud_coverage=10
        )
        if optimal_tile:
           date_list_available.append(optimal_tile.get('date'))
    list_of_requests_vis= [
        sentinel_build_request(
            config=config,
            box=box,
            request_type='TrueColor',
            request_date=(date_i, date_i)
        )
        for date_i in date_list_available
    ]
    list_of_requests_fourband= [
        sentinel_build_request(
            config=config,
            box=box,
            request_type='4-band',
            request_date=(date_i, date_i)
        )
        for date_i in date_list_available
    ]
    list_of_requests = list_of_requests_vis + list_of_requests_fourband
    list_of_requests = [
        request.download_list[0]
        for request in list_of_requests
    ]
    img_arrays = SentinelHubDownloadClient(config=config).download(
        list_of_requests,
        max_threads=5
    )
    return date_list_available, img_arrays
