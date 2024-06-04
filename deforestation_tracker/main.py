import os
import tensorflow as tf
from tensorflow.keras.models import load_model
import os
import numpy as np
import datetime as dt
from PIL import Image
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from deforestation_tracker.segmenter import segment, segment_self
from deforestation_tracker.image_array_loaders import load_img_array_from_satellite, load_img_array_locally, load_multiple_imgs_from_sat
from deforestation_tracker.custom_layer import RepeatElements

# INSTRUCTION:
# Run this file, triggering the __main__ function.
# Go to "http://localhost:8080/docs" to test it out.

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
        end_timeframe=str(end_timeframe),  # assuming format "2023-02-03"
    )

    original_image_list = image_array.flatten().tolist()

    image_array = segment(image_array, model)
    image_list = image_array.tolist()
    return JSONResponse(content={"original_image_list": original_image_list,
                                 "segmented_image_list": image_list,
                                 "request_info_date": request_info_date})

@app.get("/do_everything")
def do_everything(
    start_timeframe: str,  # TODO: Pay attention to unused inputs.
    end_timeframe: str,
    longitude: str,
    latitude: str,
    sample_number: str,  # TODO: Pay attention to unused inputs.
    square_size: str):  # TODO: Pay attention to unused inputs.

    model = load_model('./deforestation_tracker/model_ressources/unet-attention-3d.hdf5')

    #End sat pull
    end_sat_image_array, end_date_info = load_img_array_from_satellite(
        lat_deg=float(latitude),
        lon_deg=float(longitude),
        end_timeframe=str(end_timeframe)  # assuming format "2023-02-03"
    )

    start_sat_image_array, start_date_info = load_img_array_from_satellite(
        lat_deg=float(latitude),
        lon_deg=float(longitude),
        end_timeframe=str(start_timeframe)  # assuming format "2023-02-03"
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

# Selfmade model endpoints

@app.get("/get_image_from_satellite_self")
def get_image_from_satellite_self():
    model = load_model('./deforestation_tracker/model_ressources/att_unet_4b.hdf5', custom_objects={'RepeatElements': RepeatElements})
    image_array, request_info_date = load_img_array_from_satellite(request_type='4-band')
    # Scale image array to have the same scale as training images that have been
    # preprocessed with rasterio
    max_values = np.max(image_array, axis=(0, 1))
    image_array = image_array / max_values
    # Retain the original satellite image and convert it to 3-band
    original_image_array = image_array
    original_image_array = original_image_array[:,:,:3]
    original_image_list = original_image_array.flatten().tolist()
    # Segment the 4-band version of the satellite image
    image_array = segment_self(image_array, model)
    image_list = image_array.flatten().tolist()
    return JSONResponse(content={"original_image_list": original_image_list,
                                "segmented_image_list": image_list,
                                "request_info_date": request_info_date})

@app.get("/get_image_from_satellite_with_params_self")
def get_image_from_satellite_with_params_self(
    start_timeframe: str,  # TODO: Pay attention to unused inputs.
    end_timeframe: str,
    longitude: str,
    latitude: str,
    sample_number: str,  # TODO: Pay attention to unused inputs.
    square_size: str):  # TODO: Pay attention to unused inputs.
    image_list = float(latitude), float(longitude), end_timeframe
    model = load_model('./deforestation_tracker/model_ressources/att_unet_4b.hdf5', custom_objects={'RepeatElements': RepeatElements})
    image_array, request_info_date = load_img_array_from_satellite(
        lat_deg=float(latitude),
        lon_deg=float(longitude),
        end_timeframe=str(end_timeframe),  # assuming format "2023-02-03"
        request_type='4-band'
    )

    # Scale image array to have the same scale as training images that have been
    # preprocessed with rasterio
    max_values = np.max(image_array, axis=(0, 1))
    image_array = image_array / max_values
    # Retain the original satellite image and convert it to 3-band
    original_image_array = image_array
    original_image_array = original_image_array[:,:,:3]
    original_image_list = original_image_array.flatten().tolist()
    # Segment the 4-band version of the satellite image
    image_array = segment_self(image_array, model)
    image_list = image_array.flatten().tolist()
    return JSONResponse(content={"original_image_list": original_image_list,
                                "segmented_image_list": image_list,
                                "request_info_date": request_info_date})

@app.get("/get_multiple_images_from_satellite")
def get_multiple_images_from_satellite(
    start_timeframe: str,  # TODO: Pay attention to unused inputs.
    end_timeframe: str,
    longitude: str,
    latitude: str,
    sample_number: str):  # TODO: Pay attention to unused inputs.
    # construct list with request dates
    start_dt, end_dt = dt.datetime.strptime(start_timeframe, "%Y-%m-%d"), dt.datetime.strptime(end_timeframe, "%Y-%m-%d")
    date_step_size = (end_dt - start_dt)/(sample_number - 1)
    date_list = [dt.date.strftime(start_dt + i * date_step_size, "%Y-%m-%d") for i in range(sample_number)]
    date_list_loaded, img_list = load_multiple_imgs_from_sat(lat_deg=latitude, lon_deg=longitude, date_list=date_list, request_type='TrueColor')
    test_img = img_list[0]
    test_img_list = image_array.flatten().tolist()
    return JSONResponse(content={"test_img_list": test_img_list
                                })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ["PORT"]))
