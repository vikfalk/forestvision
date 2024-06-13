FROM python:3.10.6-slim-bullseye

WORKDIR /app

COPY deforestation_tracker deforestation_tracker
COPY requirements.txt .
COPY setup.py .
RUN pip install .

CMD uvicorn deforestation_tracker.main:app --host 0.0.0.0 --port $PORT
