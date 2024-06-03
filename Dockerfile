# Use an official Python runtime as a parent image
FROM python:3.10.6-buster

# Set the working directory in the container
WORKDIR /app

# Copy and install the requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY deforestation_tracker deforestation_tracker
COPY setup.py .

# Install the package
RUN pip install .

# Expose the API port
EXPOSE 8080

# Command to run the API
CMD uvicorn deforestation_tracker.main:app --host 0.0.0.0 --port 8080
