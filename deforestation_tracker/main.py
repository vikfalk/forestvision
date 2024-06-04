from tensorflow.keras.models import load_model
import os
import numpy as np
from PIL import Image
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from deforestation_tracker.segmenter import segment, segment_self
from deforestation_tracker.image_array_loaders import load_img_array_from_satellite, load_img_array_locally

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
        end_timeframe=str(end_timeframe)  # assuming format "2023-02-03"
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
def get_image_from_satellite():
    model = load_model('./deforestation_tracker/model_ressources/att_unet4d_selfmade.hdf5')
    image_array = load_img_array_from_satellite(request_type='4-band')
    # Scale image array to have the same scale as training images that have been
    # preprocessed with rasterio
    max_values = np.max(image_array, axis=(0, 1))
    image_array = image_array / max_values
    image_array = segment_self(image_array, model)
    image_list = image_array.tolist()
    return JSONResponse(content={"image_list": image_list})

@app.get("/get_image_from_satellite_with_params_self")
def get_image_from_satellite_with_params_self(
    start_timeframe: str,  # TODO: Pay attention to unused inputs.
    end_timeframe: str,
    longitude: str,
    latitude: str,
    sample_number: str,  # TODO: Pay attention to unused inputs.
    square_size: str):  # TODO: Pay attention to unused inputs.

    model = load_model('./deforestation_tracker/model_ressources/att_unet4d_selfmade.hdf5')
    image_array = load_img_array_from_satellite(
        lat_deg=float(latitude),
        lon_deg=float(longitude),
        end_timeframe=str(end_timeframe),  # assuming format "2023-02-03"
        request_type='4-band'
    )
    # Scale image array to have the same scale as training images that have been
    # preprocessed with rasterio
    max_values = np.max(image_array, axis=(0, 1))
    image_array = image_array / max_values
    image_array = segment_self(image_array, model)
    image_list = image_array.tolist()
    return JSONResponse(content={"image_list": image_list})


# Selfmade model endpoints

@api_app.get("/get_image_from_satellite_self")
def get_image_from_satellite():
    model = load_model('./deforestation_tracker/model_ressources/att_unet4d_selfmade.hdf5')
    image_array = load_img_array_from_satellite()
    image_array = segment_self(image_array, model)
    image_list = image_array.tolist()
    return JSONResponse(content={"image_list": image_list})

@api_app.get("/get_image_from_satellite_with_params_self")
def get_image_from_satellite_with_params(
    start_timeframe: str,  # TODO: Pay attention to unused inputs.
    end_timeframe: str,
    longitude: str,
    latitude: str,
    sample_number: str,  # TODO: Pay attention to unused inputs.
    square_size: str):  # TODO: Pay attention to unused inputs.
    image_list = float(latitude), float(longitude), end_timeframe
    model = load_model('./deforestation_tracker/model_ressources/att_unet4d_selfmade.hdf5')
    image_array = load_img_array_from_satellite(
        lat_deg=float(latitude),
        lon_deg=float(longitude),
        end_timeframe=str(end_timeframe)  # assuming format "2023-02-03"
    )
    image_array = segment_self(image_array, model)
    image_list = image_array.tolist()
    return JSONResponse(content={"image_list": image_list})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ["PORT"]))
