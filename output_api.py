from fastapi import FastAPI
import numpy as np
from model.segmenter import image_segmenter
from fastapi.responses import JSONResponse
from PIL import Image

api_app = FastAPI()

# Enter "uvicorn output_api:api_app --reload" in the command line and go to "http://localhost:8000/docs" to test it out.


@api_app.get('/')
def index():
    return {'api status': "running"}


@api_app.get("/get_image")
def get_image():
    image_array = np.random.randint(0, 256, (3, 3, 3), dtype=np.uint8)
    image_list = image_array.tolist()
    return JSONResponse(content={"image_list": image_list})

@api_app.get("/get_complex_image")
def get_complex_image():
    image = Image.open('./segmented_output_files/after_resized.png')
    image_array = np.array(image)
    image_list = image_array.tolist()
    return JSONResponse(content={"image_list": image_list})

@api_app.get("/get_image_from_model")
def get_image_from_model():
    image_array = image_segmenter()
    image_list = image_array.tolist()
    return JSONResponse(content={"image_list": image_list})

@api_app.get('/calculate_change')
def calculate_change(
    # TODO: Needs to be adjusted a lot depending on the state of the project, especially user inputs.
    start_timeframe,
    end_timeframe,
    longitude,
    latitude,
    sample_number):
    # result_string = compare_coverage(
    #     "./segmented_output_files/before_resized.png",
    #     "./segmented_output_files/after_resized.png"
    # )
    # return result_string
    return {'change': -12.34}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api_app, host="0.0.0.0", port=8000)
