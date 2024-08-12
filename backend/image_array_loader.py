from typing import List
from sentinelhub import SentinelHubDownloadClient
from backend.sentinelhub_requester import (
    search_optimal_l2a_tiles,
    create_sentinelhub_token,
    create_bounding_box,
    build_sentinel_request
)


def load_images_from_satellite(
        lat_deg: float,
        lon_deg: float,
        date_list: List[str]
    ):
    """Loads available image arrays from sentinel hub at multiple times."""
    box = create_bounding_box(
        lat_deg=lat_deg,
        lon_deg=lon_deg,
        image_size_px=512,
        resolution_m_per_px=10
    )
    config, catalog_ = create_sentinelhub_token()
    date_list_available = []
    for date_i in date_list:
        optimal_tile = search_optimal_l2a_tiles(
            catalog=catalog_,
            bbox=box,
            date_request=date_i,
            range_days=91,
            max_cloud_coverage=10
        )
        if optimal_tile:
           date_list_available.append(optimal_tile.get('date'))
    list_of_requests_vis= [
        build_sentinel_request(
            config=config,
            box=box,
            request_type='TrueColor',
            request_date=(date_i, date_i)
        )
        for date_i in date_list_available
    ]
    list_of_requests_fourband= [
        build_sentinel_request(
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
