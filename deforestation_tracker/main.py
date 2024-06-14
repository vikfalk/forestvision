import os
import io
import base64
import numpy as np
import datetime as dt
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from tensorflow.keras.models import load_model
from deforestation_tracker.custom_layer import RepeatElements
from deforestation_tracker.segmenter import segment, segment_self
from deforestation_tracker.image_array_loaders import load_img_array_from_satellite, load_multiple_imgs_from_sat

def numpy_to_base64(img_array):
    img_bytes = io.BytesIO()
    np.save(img_bytes, img_array)
    img_bytes.seek(0)
    img_b64 = base64.b64encode(img_bytes.read()).decode('utf-8')
    return img_b64

app = FastAPI()

@app.get('/')
def index():
    return {'api status': "running"}

@app.get("/get_image_from_satellite_with_params")
def get_image_from_satellite_with_params(
    start_timeframe: str,
    end_timeframe: str,
    longitude: str,
    latitude: str,
    sample_number: str,
    square_size: str):

    model = load_model('./deforestation_tracker/model_ressources/unet-attention-3d.hdf5')
    image_array, request_info_date = load_img_array_from_satellite(
        lat_deg=float(latitude),
        lon_deg=float(longitude),
        end_timeframe=str(end_timeframe),
    )

    original_image_list = image_array.flatten().tolist()

    image_array = segment(image_array, model)
    image_list = image_array.tolist()
    return JSONResponse(content={"original_image_list": original_image_list,
                                 "segmented_image_list": image_list,
                                 "request_info_date": request_info_date})

@app.get("/do_everything")
def do_everything(
    start_timeframe: str,
    end_timeframe: str,
    longitude: str,
    latitude: str
    ):

    model = load_model('./deforestation_tracker/model_ressources/unet-attention-3d.hdf5')

    #End sat pull
    # TODO: Change this to "get_multiple_images_from_satellite"
    end_sat_image_array, end_date_info = load_img_array_from_satellite(
        lat_deg=float(latitude),
        lon_deg=float(longitude),
        end_timeframe=str(end_timeframe)
    )

    start_sat_image_array, start_date_info = load_img_array_from_satellite(
        lat_deg=float(latitude),
        lon_deg=float(longitude),
        end_timeframe=str(start_timeframe)
    )

    #End sat present
    end_sat_image_list = end_sat_image_array.tolist()

    #End mask present
    end_mask_image_array = segment(end_sat_image_list, model)
    end_mask_image_list = end_mask_image_array.tolist()

    #Start sat present
    start_sat_image_list = start_sat_image_array.tolist()

    #Start mask present
    start_mask_image_array = segment(start_sat_image_list, model)
    start_mask_image_list = start_mask_image_array.tolist()

    return JSONResponse(content={"end_mask_image_list": end_mask_image_list,
                                 "end_sat_image_list": end_sat_image_list,
                                 "start_mask_image_list": start_mask_image_list,
                                 "start_sat_image_list": start_sat_image_list,
                                 'start_date_info':start_date_info,
                                 'end_date_info': end_date_info,
                                 })

# Selfmade Model Endpoints
@app.get("/get_image_from_satellite_self")
def get_image_from_satellite_self():
    model = load_model('./deforestation_tracker/model_ressources/att_unet_4b.hdf5', custom_objects={'RepeatElements': RepeatElements})

    # Retrieve two separate satellite images for RGB and fourth band, respectively
    original_image_array, request_info_date = load_img_array_from_satellite(request_type='TrueColor')
    four_b_array, date = load_img_array_from_satellite(request_type='4-band')

    # Extract fourth band from 4-band request and normalize to values between 0 and 1
    band_4 = four_b_array[:,:,3]
    max_value = np.max(band_4)
    band_4 = band_4 / max_value

    # Stack normalized RGB image and normalized fourth band together
    image_array = np.dstack((original_image_array, band_4))

    # Turn the original satellite image into a list
    original_image_list = original_image_array.flatten().tolist()

    # Segment the 4-band version of the satellite image
    image_array = segment_self(image_array, model)
    image_list = image_array.flatten().tolist()

    return JSONResponse(content={"original_image_list": original_image_list,
                                "segmented_image_list": image_list,
                                "request_info_date": request_info_date})

@app.get("/get_image_from_satellite_with_params_self")
def get_image_from_satellite_with_params_self(
    end_timeframe: str,
    longitude: str,
    latitude: str
    ):
    image_list = float(latitude), float(longitude), end_timeframe
    model = load_model('./deforestation_tracker/model_ressources/att_unet_4b.hdf5', custom_objects={'RepeatElements': RepeatElements})

    # Retrieve two separate satellite images for RGB and fourth band, respectively
    original_image_array, request_info_date = load_img_array_from_satellite(
        lat_deg=float(latitude),
        lon_deg=float(longitude),
        end_timeframe=str(end_timeframe),
        request_type='TrueColor'
    )
    four_b_array, date = load_img_array_from_satellite(
        lat_deg=float(latitude),
        lon_deg=float(longitude),
        end_timeframe=str(end_timeframe),
        request_type='4-band'
    )

    # Extract fourth band from 4-band request and normalize to values between 0 and 1
    band_4 = four_b_array[:,:,3]
    max_value = np.max(band_4)
    band_4 = band_4 / max_value

    # Stack normalized RGB image and normalized fourth band together
    image_array = np.dstack((original_image_array, band_4))

    # Turn the original satellite image into a list
    original_image_list = original_image_array.flatten().tolist()

    # Segment the 4-band version of the satellite image
    image_array = segment_self(image_array, model)
    image_list = image_array.flatten().tolist()

    return JSONResponse(content={"original_image_list": original_image_list,
                                 "segmented_image_list": image_list,
                                 "request_info_date": request_info_date})

@app.get("/do_everything_self")
def do_everything_self(
    start_timeframe: str,
    end_timeframe: str,
    longitude: str,
    latitude: str):

    model = load_model('./deforestation_tracker/model_ressources/att_unet_4b.hdf5', custom_objects={'RepeatElements': RepeatElements})

    # TODO: Change this to "get_multiple_images_from_satellite"
    #End sat pull
    end_sat_image_array, end_date_info = load_img_array_from_satellite(
        lat_deg=float(latitude),
        lon_deg=float(longitude),
        end_timeframe=str(end_timeframe),
        request_type='TrueColor'
    )

    # Start sat pull
    start_sat_image_array, start_date_info = load_img_array_from_satellite(
        lat_deg=float(latitude),
        lon_deg=float(longitude),
        end_timeframe=str(start_timeframe),
        request_type='TrueColor'
    )

    # End 4-band pull
    four_b_array_end, date = load_img_array_from_satellite(
        lat_deg=float(latitude),
        lon_deg=float(longitude),
        end_timeframe=str(end_timeframe),
        request_type='4-band'
    )

    # Start 4-band pull
    four_b_array_start, date = load_img_array_from_satellite(
        lat_deg=float(latitude),
        lon_deg=float(longitude),
        end_timeframe=str(start_timeframe),
        request_type='4-band'
    )

    ## Extract fourth band from 4-band request and normalize to values between 0 and 1
    band_4_end = four_b_array_end[:,:,3]
    max_value = np.max(band_4_end)
    band_4_end = band_4_end / max_value

    band_4_start = four_b_array_start[:,:,3]
    max_value = np.max(band_4_start)
    band_4_start = band_4_start / max_value

    # Stack normalized RGB image and normalized fourth band together
    image_array_end = np.dstack((end_sat_image_array, band_4_end))
    image_array_start = np.dstack((start_sat_image_array, band_4_start))

    # Create segmentation masks
    end_mask_image_array = segment(image_array_end, model)
    end_mask_image_list = end_mask_image_array.tolist()

    start_mask_image_array = segment(image_array_start, model)
    start_mask_image_list = start_mask_image_array.tolist()

    # Convert satellite images to lists
    end_sat_image_list = end_sat_image_array.flatten().tolist()
    start_sat_image_list = start_sat_image_array.flatten().tolist()

    return JSONResponse(content={"end_mask_image_list": end_mask_image_list,
                                 "end_sat_image_list": end_sat_image_list,
                                 "start_mask_image_list": start_mask_image_list,
                                 "start_sat_image_list": start_sat_image_list,
                                 'start_date_info':start_date_info,
                                 'end_date_info': end_date_info,
                                 })

@app.get("/get_multiple_images_from_satellite")
def get_multiple_images_from_satellite(
    start_timeframe: str = "2020-05-13",
    end_timeframe: str = "2024-05-30",
    longitude: str = "-55.26209",
    latitude: str = "-8.48638",
    sample_number: str = "2"):

    model = load_model('./deforestation_tracker/model_ressources/att_unet_4b.hdf5', custom_objects={'RepeatElements': RepeatElements})

    # construct list with request dates
    start_dt, end_dt = dt.datetime.strptime(start_timeframe, "%Y-%m-%d"), dt.datetime.strptime(end_timeframe, "%Y-%m-%d")
    date_step_size = (end_dt - start_dt)/(int(sample_number) - 1)
    date_list = [dt.date.strftime(start_dt + i * date_step_size, "%Y-%m-%d") for i in range(int(sample_number))]

    # load both 3 band and 4 band images
    date_list_loaded, img_list = load_multiple_imgs_from_sat(lat_deg=float(latitude), lon_deg=float(longitude), date_list=date_list, request_type='TrueColor')

    # Join 3-band with 4-band
    number_of_dates = len(date_list_loaded)
    combined_img_arrays = []
    for date in range(number_of_dates):
        band_4_at_date = img_list[(date + number_of_dates)][:,:,3]
        vis_at_date = img_list[date]

        # Normalize 4-band channel to values between 0 and 1
        max_value = np.max(band_4_at_date)
        band_4_at_date = band_4_at_date / max_value
        combined_img_arrays.append(np.dstack((vis_at_date, band_4_at_date)))

    # Segment
    segmented_arrays = [segment(img_at_date, model) for img_at_date in combined_img_arrays]
    print(f'Shape of segmented arrays: {segmented_arrays[0].shape}')

    # Flatten image arrays
    original_img_list = [img.flatten().tolist() for img in combined_img_arrays]
    segmented_img_list = [mask.flatten().tolist() for mask in segmented_arrays]

    # Delete instances where arrays are not correct shape (512x512)
    for i, list_ in enumerate(segmented_img_list):
        if len(list_) != 262144:
            date_list_loaded.pop(i)
            original_img_list.pop(i)
            segmented_img_list.pop(i)

    return JSONResponse(content = {
        "date_list_loaded": date_list_loaded,
        "segmented_img_list": segmented_img_list})



@app.get("/get_satellite_images")
def get_satellite_images(
    start_timeframe: str = "2020-05-13",
    end_timeframe: str = "2024-05-30",
    longitude: str = "-55.26209",
    latitude: str = "-8.48638",
    sample_number: str = "2",
    send_orginal_images = 'False'
    ):
    """Takes start and end date and coordinates and returns
    a JSON response object including dates, segmented images and optionally,
    original images.If sample_number equals two, only data belonging to the
    closest point in time to the start and the end date respectively will be
    returned, higher sample_numbers will return data from points in time between
    the start and the end date, as evenly spaced as possible.
    """

    # Construct list with request dates.
    start_dt, end_dt = dt.datetime.strptime(start_timeframe, "%Y-%m-%d"), dt.datetime.strptime(end_timeframe, "%Y-%m-%d")
    date_step_size = (end_dt - start_dt)/(int(sample_number) - 1)
    date_list = [dt.date.strftime(start_dt + i * date_step_size, "%Y-%m-%d") for i in range(int(sample_number))]

    # Load both 3 band and 4 band images.
    date_list_loaded, img_list = load_multiple_imgs_from_sat(lat_deg=float(latitude), lon_deg=float(longitude), date_list=date_list)

    # Join 3-band with 4-band and normalize 4-band channel to values between 0 and 1.
    number_of_dates = len(date_list_loaded)
    original_img_arrays = []
    combined_img_arrays = []
    for date in range(number_of_dates):
        band_4_at_date = img_list[(date + number_of_dates)][:,:,3]
        vis_at_date = img_list[date]
        rescaled_vis_at_date = (vis_at_date * 255).astype(np.uint8)
        original_img_arrays.append(rescaled_vis_at_date)
        max_value = np.max(band_4_at_date)
        band_4_at_date = band_4_at_date / max_value
        combined_img_arrays.append(np.dstack((vis_at_date, band_4_at_date)))
    print(f'Shape of combined image arrays: {combined_img_arrays[0].shape}')

    # Segment
    model = load_model('./deforestation_tracker/model_ressources/att_unet_4b.hdf5', custom_objects={'RepeatElements': RepeatElements})
    segmented_arrays = [segment(img_at_date, model) for img_at_date in combined_img_arrays]
    print(f'Shape of segmented arrays: {segmented_arrays[0].shape}')

    # TODO: Make this a shape check rather than a length check.
    # delete instances where arrays are not correct shape (512x512)
    # for i, list_ in enumerate(segmented_img_list):
    #     if len(list_) != 262144:
    #         date_list_loaded.pop(i)
    #         original_img_list.pop(i)
    #         segmented_img_list.pop(i)

    # Encode
    segmented_img_b64_list = [numpy_to_base64(img) for img in segmented_arrays]
    original_img_b64_list = [numpy_to_base64(img) for img in original_img_arrays]

    # Transmitting
    if send_orginal_images == 'False':
        print("Not sending original satellite images.")
        json_response_content = {
                "date_list_loaded": date_list_loaded,
                "segmented_img_list": segmented_img_b64_list}
    elif send_orginal_images == 'True':
        print("Sending original satellite images, too under the key 'original_img_list'.")
        json_response_content = {
                "date_list_loaded": date_list_loaded,
                "segmented_img_list": segmented_img_b64_list,
                "original_img_list": original_img_b64_list}
    # return json_response_content
    return JSONResponse(content=json_response_content)

# def base64_to_numpy(img_b64):
#     img_bytes = io.BytesIO(base64.b64decode(img_b64))
#     img_array = np.load(img_bytes)
#     return img_array

# from PIL import Image
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ["PORT"]))
    # json_response_content = get_satellite_images(send_orginal_images='True')

    # print(json_response_content.keys())

    # print(json_response_content.get("date_list_loaded"))
    # print(len(json_response_content.get("segmented_img_list")))
    # one_b64_string = json_response_content.get("segmented_img_list")[0]
    # print(one_b64_string)
    # img_array = base64_to_numpy(one_b64_string)
    # print(img_array.shape)
    # print(img_array)
    # image = Image.fromarray(img_array)
    # print(type(image))
    # #  would be nice to have all of them come out as 255 to
    # print(len(json_response_content.get("original_img_list")))
    # original_image_b64_string = json_response_content.get("original_img_list")[0]
    # print(original_image_b64_string)
    # img_array = base64_to_numpy(original_image_b64_string)
    # print(img_array.shape)
    # print(type(img_array[0, 0, 0]))
    # # rescaled_img_array = (img_array * 255).astype(np.uint8)
    # # print(rescaled_img_array.shape)
    # # print(type(rescaled_img_array[0, 0, 0]))
    # # image = Image.fromarray(rescaled_img_array).convert("RGBA")
    # # print(type(image))
