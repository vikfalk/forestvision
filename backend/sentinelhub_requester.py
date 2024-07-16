# sentinelhub package that manages the authentication and requests to sentinelhub
import os
import numpy as np
import datetime as dt
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

def box_from_point(lat_deg, lon_deg, image_size_px = 512, resolution_m_per_px = 10):
    """
    creates a coordinate bounding box (square) around a point of interest defined by latitude and longitude.
    image_size_px and resolution_m_per_px (in meters) define the square length
    """
    a = 6378137
    e_2 = 0.00669437999014
    square_length_m = ((image_size_px - 1) * resolution_m_per_px)
    delta_meter_per_deg_lat = (np.pi * a* (1-e_2))/(180 * (1- (e_2 * (np.sin(np.deg2rad(lat_deg))**2)))**1.5)
    delta_meter_per_deg_lon = (np.pi * a * np.cos(np.deg2rad(lat_deg)))/(180 * np.sqrt((1- (e_2 * np.sin(np.deg2rad(lat_deg)**2)))))
    north_lat = round(lat_deg + (square_length_m/2 / delta_meter_per_deg_lat), ndigits=5)
    south_lat = round(lat_deg - (square_length_m/2 / delta_meter_per_deg_lat), ndigits=5)
    east_lon = round(lon_deg - (square_length_m/2 / delta_meter_per_deg_lon), ndigits=5)
    west_lon = round(lon_deg + (square_length_m/2 / delta_meter_per_deg_lon), ndigits=5)
    return BBox((east_lon, south_lat, west_lon, north_lat), crs=CRS.WGS84)

# Authorize
def sentinelhub_authorization():
    """
    creates an access token with sentinelhub to be used for one hour.
    returns the configuration to be used for requests
    """
    config = SHConfig()
    config.sh_client_id = os.getenv('SENTINEL_CLIENT_ID')
    config.sh_client_secret = os.getenv('SENTINEL_CLIENT_SECRET')
    if not config.sh_client_id or not config.sh_client_secret:
        print("Warning! To use Process API, please provide the credentials (OAuth client ID and client secret).")
    catalog = SentinelHubCatalog(config=config)
    return config,catalog



def search_available_L2A_tiles(catalog, bbox:'bounding box', date_request, range_days=91, maxCloudCoverage=10)->(dict|None):
    """
    searches for available images from the desired area with less than 10% cloud coverage
    then chooses the image which minimizes penalty = 10 * cloud_coverage + timedelta
    RETURNS a dict with the best tile, or None if no images are available. Example:
    {'id': 'S2B_MSIL2A_20200615T140059_N0214_R067_T21LXL_20200615T180658', 'date': '2020-06-15', 'cloud_cover': 0.03, 'penalty': 37.3}
    """
    time_interval = timeframe_constructor(date_request, temporal_padding=range_days)
    # search the sentinel2 data
    results = list(
        catalog.search(
                    DataCollection.SENTINEL2_L2A,
                    bbox=bbox,
                    time=time_interval,
                    filter=f"eo:cloud_cover < {maxCloudCoverage}",
                    fields={"include": ["id", "properties.datetime", "properties.eo:cloud_cover"], "exclude": []},
                )
            )
    if results:
        properties = []
        for tile in results:
            # get time offset to requested date, get cloud cover
            timedelta_tile = (dt.datetime.strptime(
                                date_request, '%Y-%m-%d') - dt.datetime.strptime(
                                                    tile.get('properties').get('datetime'), '%Y-%m-%dT%H:%M:%SZ'
                                )
                             ).days
            cloud_cover_tile = tile.get('properties').get('eo:cloud_cover')
            # penalty formula to weigh CC and time difference to desired date
            penalty = 10 * cloud_cover_tile + np.abs(timedelta_tile)
            tile_properties = [penalty, {'id': tile.get('id'),
                                    'date': dt.datetime.strftime(
                                        dt.datetime.strptime(
                                            tile.get('properties').get('datetime'), '%Y-%m-%dT%H:%M:%SZ'
                                        ).date(),
                                    '%Y-%m-%d'),
                                    'cloud_cover': cloud_cover_tile
                                    }
                        ]
            properties.append(tile_properties)
        optimal_tile = sorted(properties, key=lambda x: x[0])[0][1]
        optimal_tile['penalty'] = sorted(properties, key=lambda x: x[0])[0][0]
        return optimal_tile
    else:
        return None

# Evalscript for true color
def request_image(box, image_size_px, resolution_m_per_px, time_interval, config, request_type):
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
    return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02];
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
            return [sample.B02,
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
                other_args={"dataFilter": {"maxCloudCoverage": 50, "mosaickingOrder": "leastCC"}}
            ),
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

def sentinel_build_request(config, box, request_type, request_date, image_size_px=512):
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
    return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02];
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
            return [sample.B02,
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
                other_args={"dataFilter": {"maxCloudCoverage": 50, "mosaickingOrder": "leastCC"}}
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


if __name__ == '__main__':
    pass
    # Defining request parameters
    # lat_deg = -8.48638
    # lon_deg = -55.26209
    # time_interval = ('2024-04-28', '2024-05-28')
    # date_requested = '2020-05-10'

    # config, catalog = sentinelhub_authorization()

    # box = box_from_point(lat_deg=lat_deg, lon_deg=lon_deg, image_size_px=512, resolution_m_per_px=10)
    # optimal_tile = search_available_L2A_tiles(catalog=catalog, bbox=box, date_request=date_requested, range_days=92, maxCloudCoverage=10)
    # if optimal_tile:
    #     optimal_date = optimal_tile.get('date')
    #     print(request_image(
    #                         box=box,
    #                         image_size_px=512,
    #                         resolution_m_per_px=10,
    #                         config=config,
    #                         time_interval=(optimal_date, optimal_date),
    #                         request_type='TrueColor'
    #                         ).flatten().mean()
    #         )
