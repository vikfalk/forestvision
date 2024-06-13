FROM python:3.10.6-slim-bullseye

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY deforestation_tracker deforestation_tracker
COPY setup.py .

CMD uvicorn deforestation_tracker.main_copy:app --host 0.0.0.0 --port $PORT
