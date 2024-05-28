from fastapi import FastAPI
from PIL import Image
import numpy as np
from model.coverage_comparer import compare_coverage

api_app = FastAPI()

# Enter "uvicorn api:api_app --reload" in the command line and go to "http://localhost:8000/docs" to test it out.

@api_app.get('/')
def index():
    return {'api status': "running"}



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
