# Use an official Python runtime as a parent image
FROM python:3.10.6-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy and install the requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY deforestation_tracker deforestation_tracker
COPY setup.py .

# Command to run the API
CMD uvicorn deforestation_tracker.main_copy:app --host 0.0.0.0 --port $PORT
