import os
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from deforestation_tracker.segmenter import segment, segment_self
from deforestation_tracker.image_array_loaders import load_img_array_from_satellite, load_img_array_locally

# INSTRUCTION:
# Run this file, triggering the __main__ function.
# Go to "http://localhost:8000/docs" to test it out.

api_app = FastAPI()

@api_app.get('/')
def index():
    return {'api status': "running"}

@api_app.get("/get_image")
def get_image():
    image_array = np.random.randint(0, 256, (3, 3, 3), dtype=np.uint8)
    image_list = image_array.tolist()
    return JSONResponse(content={"image_list": image_list})

@api_app.get("/get_complex_image")  # bad name, but it will disappear soon.
def get_complex_image():
    image = Image.open('./segmented_output_files/after_resized.png')
    image_array = np.array(image)
    image_list = image_array.tolist()
    return JSONResponse(content={"image_list": image_list})

@api_app.get("/get_image_from_model")
def get_image_from_model():
    model = load_model('./deforestation_tracker/model_ressources/unet-attention-3d.hdf5')
    image_array = load_img_array_locally()
    image_array = segment(image_array, model)
    image_list = image_array.tolist()
    return JSONResponse(content={"image_list": image_list})

@api_app.get("/get_image_from_satellite")
def get_image_from_satellite():
    model = load_model('./deforestation_tracker/model_ressources/unet-attention-3d.hdf5')
    image_array = load_img_array_from_satellite()
    image_array = segment(image_array, model)
    image_list = image_array.tolist()
    return JSONResponse(content={"image_list": image_list})

@api_app.get("/get_image_from_satellite_with_params")
def get_image_from_satellite_with_params(
    start_timeframe: str,  # TODO: Pay attention to unused inputs.
    end_timeframe: str,
    longitude: str,
    latitude: str,
    sample_number: str,  # TODO: Pay attention to unused inputs.
    square_size: str):  # TODO: Pay attention to unused inputs.
    image_list = float(latitude), float(longitude), end_timeframe
    model = load_model('./deforestation_tracker/model_ressources/unet-attention-3d.hdf5')
    image_array = load_img_array_from_satellite(
        lat_deg=float(latitude),
        lon_deg=float(longitude),
        end_timeframe=str(end_timeframe)  # assuming format "2023-02-03"
    )
    image_array = segment(image_array, model)
    image_list = image_array.tolist()
    return JSONResponse(content={"image_list": image_list})

@api_app.get("/generic_param_api")
def generic_param_api(
    start_timeframe,
    end_timeframe,
    longitude,
    latitude,
    sample_number,
    square_size):
    """To test the transmissions of UI parameters to the backend."""

    param_list = {
        "start_timeframe": start_timeframe,
        "end_timeframe": end_timeframe,
        "longitude": longitude,
        "latitude": latitude,
        "sample_number": sample_number,
        "square_size": square_size
    }

    return JSONResponse(content={"param_list": param_list})

# Selfmade model endpoints

@api_app.get("/get_image_from_satellite_self")
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api_app, host="0.0.0.0", port=int(os.environ["API_PORT"]))
