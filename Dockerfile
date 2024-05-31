FROM python:3.10.6-buster

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY deforestation_tracker deforestation_tracker
COPY setup.py setup.py
RUN pip install .

CMD uvicorn deforestation_tracker.main:api_app --host 0.0.0.0 --port $API_PORT
