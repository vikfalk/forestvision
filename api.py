from fastapi import FastAPI

api_app = FastAPI()

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
    return {'change': -12.34}

# enter "uvicorn api:api_app --reload" in the command line and go to the specified localhost to test it out.
