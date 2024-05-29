from input_api import request_image, box_from_point, sentinelhub_authorization
import numpy as np

# call request_image function here with values from Output_API
# hardcoded for now
lat_deg = -8.48638
lon_deg = -55.26209
pixel_size = 512
resolution_m = 10
time_interval = ('2024-04-28', '2024-05-28')
request_type = 'TrueColor'

if __name__ == '__main__':
    config = sentinelhub_authorization()
    image = request_image(
            lat_deg=lat_deg,
            lon_deg=lon_deg,
            pixel_size=pixel_size,
            resolution=resolution_m,
            time_interval=time_interval,
            config=config,
            request_type=request_type
            )
    print(image.flatten().mean())
    # dummy model call: segment_func(image)
