FROM python:3.10.6-slim-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY deforestation_tracker deforestation_tracker
COPY setup.py setup.py
RUN pip install .

CMD uvicorn deforestation_tracker.main:app --host 0.0.0.0 --port $PORT
