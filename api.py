from fastapi import FastAPI
import datetime as dt

api_app = FastAPI()

@api_app.get('/')
def index():
    return {'okay': True}


@api_app.get('/calculate_change')
def predict(start_timeframe, end_timeframe, longitude, latitude, sample_number):
    # add connection to actual model and processing
    return {'change': -12.34}

# enter "uvicorn api:api_app --reload" in the command line and go to the specified localhost to test it out.
