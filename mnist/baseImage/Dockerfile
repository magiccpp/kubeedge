# Use a Python base image
FROM arm32v7/python:3.8-slim-bullseye

# Set the working directory in the container
WORKDIR /app
RUN apt-get update && apt-get install -y 

RUN apt-get update && apt-get install -y build-essential zlib1g-dev libjpeg-dev libtiff5-dev libfreetype6-dev liblcms2-dev libwebp-dev libopenjp2-7-dev libraqm-dev

# Copy the Python requirements file
COPY requirements.txt /app/requirements.txt

# Install the necessary packages
RUN pip install --no-cache-dir -r requirements.txt

