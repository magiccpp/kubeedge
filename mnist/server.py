import aiohttp
import numpy as np
from PIL import Image
from io import BytesIO
from aiohttp import web
from tflite_runtime.interpreter import Interpreter
import os
import time
import paho.mqtt.client as mqtt
from prometheus_client import Counter, generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
from prometheus_client import Histogram
from prometheus_client import multiprocess

PROMETHEUS_CONTENT_TYPE = 'text/plain; version=0.0.4'

# Define callback functions for MQTT events
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

def on_publish(client, userdata, mid):
    print("Message published")

# Read the STORAGE_PATH environment variable
storage_path = os.getenv('STORAGE_PATH', '/app/disk')
print(f'Using storage path: {storage_path}')

mqtt_enabled = os.getenv('MQTT_ENABLE', 'FALSE')
if mqtt_enabled == 'FALSE':
    mqtt_enabled = False
else:
    mqtt_enabled = True

if mqtt_enabled:
    mqtt_ip = os.getenv('MQTT_IP', '172.17.0.2')
    print(f'Using mqtt ip: {mqtt_ip}')

    mqtt_topic = os.getenv('MQTT_TOPIC', 'image_classification')
    print(f'Using mqtt topic: {mqtt_topic}')

    client = mqtt.Client()
    # Set callback functions
    client.on_connect = on_connect
    client.on_publish = on_publish

    # Connect to the broker
    client.connect(mqtt_ip, 1883)
    client.loop_start()

# Load the TensorFlow Lite model
model_path = 'mnist_model.tflite'
interpreter = Interpreter(model_path=model_path)
interpreter.allocate_tensors()

# Get input and output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Define Prometheus metrics
REQUEST_COUNT = Counter('images_processed_total', 'Total number of images processed')
REQUEST_LATENCY = Histogram('image_processing_latency_seconds', 'Latency of image processing in seconds')

# Optionally, you can add more metrics like failures
FAILURE_COUNT = Counter('image_processing_failures_total', 'Total number of failed image processing attempts')

# Define the function to preprocess the image
def preprocess_image(image, storage_path):
    image = image.convert('L')  # Convert the image to grayscale
    image = image.resize((28, 28))  # Resize the image to match the model input shape
    image = np.expand_dims(np.array(image), axis=0)
    image = np.expand_dims(image, axis=3)
    image = image.astype('float32') / 255.0  # Normalize the pixel values

    timestamp = str(int(time.time()))
    filename = os.path.join(storage_path, 'grayscale-' + timestamp + '.png')

    # Save the preprocessed image to the specified path in PNG format
    preprocessed_image = Image.fromarray(np.squeeze(image * 255).astype(np.uint8))
    preprocessed_image.save(filename, format='PNG')
    return image

# Define the function to perform inference
def run_inference(image):
    input_data = preprocess_image(image, storage_path)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    predicted_class = int(np.argmax(output_data))
    return predicted_class

# Define the request handler for the predict API
async def predict(request):
    with REQUEST_LATENCY.time():
        try:
            # Read the image from the request payload
            reader = await request.multipart()
            field = await reader.next()
            image_data = await field.read()

            # Process the image and perform inference
            image = Image.open(BytesIO(image_data))
            predicted_class = run_inference(image)
            message = str(predicted_class)
            if mqtt_enabled:
                client.publish(mqtt_topic, message)
            
            # Increment the request count
            REQUEST_COUNT.inc()
            
            # Send the predicted class back to the client
            return web.json_response({'class': predicted_class})
        except Exception as e:
            # Increment the failure count
            FAILURE_COUNT.inc()
            return web.Response(status=500, text=str(e))

# Define the request handler for Prometheus metrics
async def metrics(request):
    # Generate the latest metrics
    metrics_data = generate_latest()
    
    # Create a response without embedding charset in content_type
    resp = web.Response(
        body=metrics_data,
        content_type=PROMETHEUS_CONTENT_TYPE,
        charset='utf-8'  # Set charset separately if required
    )
    return resp

async def version(request):
    version_info = {"version": "2.0.3"}  # Update with your actual version
    return web.json_response(version_info)

# Create the aiohttp web application and add the routes
app = web.Application()
app.router.add_post('/predict', predict)
app.router.add_get('/metrics', metrics)  # Add the /metrics endpoint
app.router.add_get('/version', version)  # Add the /version endpoint


# Start the web service
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8080)
