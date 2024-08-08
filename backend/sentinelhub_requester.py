import os
import datetime as dt
from typing import Tuple
import numpy as np
from sentinelhub import (
    SHConfig,
    CRS,
    BBox,
    DataCollection,
    MimeType,
    SentinelHubRequest,
    SentinelHubCatalog
)
from backend.utils import timeframe_constructor


def box_from_point(lat_deg, lon_deg, image_size_px=512, resolution_m_per_px=10) -> BBox:
    """
    Creates a coordinate bounding box (square) around a point of interest
    defined by latitude and longitude. image_size_px and resolution_m_per_px
    (in meters) define the square length.
    """
    a = 6378137
    e_2 = 0.00669437999014
    sq_length_m = (image_size_px - 1) * resolution_m_per_px
    delta_meter_per_deg_lat = (
        (np.pi * a * (1 - e_2))
        / (180 * (1 - (e_2 * (np.sin(np.deg2rad(lat_deg)) ** 2))) ** 1.5)
    )
    delta_meter_per_deg_lon = (
        (np.pi * a * np.cos(np.deg2rad(lat_deg)))
        / (180 * np.sqrt((1 - (e_2 * np.sin(np.deg2rad(lat_deg) ** 2)))))
    )
    north_lat = round(lat_deg + (sq_length_m / 2 / delta_meter_per_deg_lat), 5)
    south_lat = round(lat_deg - (sq_length_m / 2 / delta_meter_per_deg_lat), 5)
    east_lon = round(lon_deg - (sq_length_m / 2 / delta_meter_per_deg_lon), 5)
    west_lon = round(lon_deg + (sq_length_m / 2 / delta_meter_per_deg_lon), 5)
    return BBox((east_lon, south_lat, west_lon, north_lat), crs=CRS.WGS84)

def sentinelhub_authorization() -> Tuple[SHConfig, SentinelHubCatalog]:
    """
    creates an access token with sentinelhub to be used for one hour.
    returns the configuration to be used for requests
    """
    config = SHConfig()
    config.sh_client_id = os.getenv('SENTINEL_CLIENT_ID')
    config.sh_client_secret = os.getenv('SENTINEL_CLIENT_SECRET')
    if not config.sh_client_id or not config.sh_client_secret:
        print(
            "Warning! To use Process API, please provide the credentials",
            "(OAuth client ID and client secret)."
        )
    catalog = SentinelHubCatalog(config=config)
    return config, catalog


def search_available_l2a_tiles(
        catalog: SentinelHubCatalog,
        bbox: BBox,
        date_request: str,
        range_days: int=91,
        max_cloud_coverage: int=10
    ) -> (dict | None):
    """
    Searches for available images from the desired area with less than 10%
    cloud coverage then chooses the image which minimizes a definied penalty.
    Returns a dict with the best tile, or None if no images are available.
    """
    time_interval = timeframe_constructor(
        date_request,
        temporal_padding=range_days
    )
    results = list(catalog.search(
        DataCollection.SENTINEL2_L2A,
        bbox=bbox,
        time=time_interval,
        filter=f"eo:cloud_cover < {max_cloud_coverage}",
        fields={
            "include": [
                "id",
                "properties.datetime",
                "properties.eo:cloud_cover"
            ],
            "exclude": []
        },
    ))
    if not results:
        return None
    properties = []
    for tile in results:
        # get time offset to requested date, get cloud cover
        timedelta_tile = (
            dt.datetime.strptime(date_request, '%Y-%m-%d')\
            - dt.datetime.strptime(
                tile.get('properties').get('datetime'),
                '%Y-%m-%dT%H:%M:%SZ'
            )
        ).days
        cloud_cover_tile = tile.get('properties').get('eo:cloud_cover')
        # penalty formula to weigh CC and time difference to desired date
        penalty = 10 * cloud_cover_tile + np.abs(timedelta_tile)
        tile_properties = [
            penalty,
            {
                'id': tile.get('id'),
                'date': dt.datetime.strftime(
                    dt.datetime.strptime(
                        tile.get('properties').get('datetime'),
                        '%Y-%m-%dT%H:%M:%SZ'
                    ).date(),
                    '%Y-%m-%d'
                ),
                'cloud_cover': cloud_cover_tile
            }
                    ]
        properties.append(tile_properties)
    optimal_tile = sorted(properties, key=lambda x: x[0])[0][1]
    optimal_tile['penalty'] = sorted(properties, key=lambda x: x[0])[0][0]
    return optimal_tile


def request_image(box, image_size_px, time_interval, config, request_type):
    evalscript_true_color = """
        //VERSION=3
        function setup() {
            return {
                input: ["B02", "B03", "B04"],
                output: {
                    bands: 3,
                    sampleType: "FLOAT32"
                }
            };
        }
        function evaluatePixel(sample) {
            return [
                2.5 * sample.B04,
                2.5 * sample.B03,
                2.5 * sample.B02
            ];
        }
    """
    evalscript_four_bands = """
        //VERSION=3
        function setup() {
            return {
                input: [{
                    bands: ["B02","B03","B04","B08"],
                    units: "DN"
                }],
                output: {
                    bands: 4,
                    sampleType: "FLOAT32"
                }
            };
        }
        function evaluatePixel(sample) {
            return [
                sample.B02,
                sample.B03,
                sample.B04,
                sample.B08,
            ];
        }
    """
    if request_type == 'TrueColor':
        evalscript = evalscript_true_color
    elif request_type == '4-band':
        evalscript = evalscript_four_bands
    request = SentinelHubRequest(
        data_folder="sentinel_imgs",
        evalscript=evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=time_interval,
                other_args={
                    "dataFilter": {
                        "maxCloudCoverage": 50,
                        "mosaickingOrder": "leastCC"
                    }
                }
            )
        ],
        responses=[
            SentinelHubRequest.output_response('default', MimeType.TIFF),
        ],
        bbox=box,
        size=[image_size_px, image_size_px],
        config=config
    )
    img = request.get_data()[0]

    if request_type == 'TrueColor':
        return np.clip(img, 0, 1)
    elif request_type == '4-band':
        return img


def sentinel_build_request(
        config, box, request_type, request_date, image_size_px=512
    ):
    evalscript_true_color = """
        //VERSION=3

        function setup() {
        return {
            input: ["B02", "B03", "B04"],
            output: {
                bands: 3,
                sampleType: "FLOAT32"
            }
        };
        }

        function evaluatePixel(sample) {
            return [
                2.5 * sample.B04,
                2.5 * sample.B03,
                2.5 * sample.B02
            ];
        }
    """
    evalscript_four_bands = """
        //VERSION=3
        function setup() {
            return {
                input: [{
                    bands: ["B02","B03","B04","B08"],
                    units: "DN"
                }],
                output: {
                    bands: 4,
                    sampleType: "FLOAT32"
                }
            };
        }
        function evaluatePixel(sample) {
            return [
                sample.B02,
                sample.B03,
                sample.B04,
                sample.B08,
            ];
        }
    """
    if request_type == 'TrueColor':
        evalscript = evalscript_true_color
    elif request_type == '4-band':
        evalscript = evalscript_four_bands
    request = SentinelHubRequest(
        data_folder="sentinel_imgs",
        evalscript=evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=request_date,
                other_args={
                    "dataFilter": {
                        "maxCloudCoverage": 50,
                        "mosaickingOrder": "leastCC"
                    }
                }
            ),
        ],
        responses=[
            SentinelHubRequest.output_response('default', MimeType.TIFF),
        ],
        bbox=box,
        size=[image_size_px, image_size_px],
        config=config
    )
    return request
