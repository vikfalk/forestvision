# sentinelhub package that manages the authentication and requests to sentinelhub
import os
import numpy as np
from sentinelhub import (
    SHConfig,
    CRS,
    BBox,
    DataCollection,
    DownloadRequest,
    MimeType,
    MosaickingOrder,
    SentinelHubDownloadClient,
    SentinelHubRequest,
    bbox_to_dimensions,
)


def box_from_point(lat_deg, lon_deg, pixel_size, resolution_m):
    """
    creates a coordinate bounding box (square) around a point of interest defined by latitude and longitude.
    pixel_size and resolution_m (in meters) define the square length
    """
    a = 6378137
    e_2 = 0.00669437999014
    square_length_m = ((pixel_size - 1) * resolution_m)
    delta_meter_per_deg_lat = (np.pi * a* (1-e_2))/(180 * (1- (e_2 * (np.sin(np.deg2rad(lat_deg))**2)))**1.5)
    delta_meter_per_deg_long = (np.pi * a * np.cos(np.deg2rad(lat_deg)))/(180 * np.sqrt((1- (e_2 * np.sin(np.deg2rad(lat_deg)**2)))))
    north_lat = round(lat_deg + (square_length_m/2 / delta_meter_per_deg_lat), ndigits=5)
    south_lat = round(lat_deg - (square_length_m/2 / delta_meter_per_deg_lat), ndigits=5)
    east_long = round(lon_deg - (square_length_m/2 / delta_meter_per_deg_long), ndigits=5)
    west_long = round(lon_deg + (square_length_m/2 / delta_meter_per_deg_long), ndigits=5)
    return (east_long, south_lat, west_long, north_lat)

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
    return config

# Defining request parameters
lat_deg = -8.48638
lon_deg = -55.26209
pixel_size = 512
resolution_m = 10
time_interval = ('2024-04-28', '2024-05-28')

# Evalscript for true color
def request_image(lat_deg, lon_deg, pixel_size, resolution, time_interval, config, request_type):
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
                other_args={"dataFilter": {"maxCloudCoverage": 1, "mosaickingOrder": "leastCC"}}
            ),
        ],
        responses=[
            SentinelHubRequest.output_response('default', MimeType.TIFF),
        ],
        bbox=BBox(bbox=box_from_point(lat_deg, lon_deg, pixel_size, resolution), crs=CRS.WGS84),
        size=[pixel_size, pixel_size],
        config=config
    )
    return request.get_data()[0]


if __name__ == '__main__':
    config = sentinelhub_authorization()
    print(request_image(
                    lat_deg=lat_deg,
                    lon_deg=lon_deg,
                    pixel_size=pixel_size,
                    resolution=resolution_m,
                    config=config,
                    time_interval=time_interval,
                    request_type='TrueColor'
                    ).flatten().mean()
    )
