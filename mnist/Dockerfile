# Use a Python base image
FROM magiccpp1/arm32v7-base:01

# Set the working directory in the container
WORKDIR /app

# Copy the Python requirements file
COPY requirements.txt /app/requirements.txt

# Install the necessary packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the TensorFlow Lite model to the container
COPY mnist_model.tflite /app/mnist_model.tflite


# Copy the web service code to the container
COPY server.py /app/server.py

# Expose the port on which the web service will run
EXPOSE 8080

# Start the web service when the container launches
CMD ["python", "server.py"]
