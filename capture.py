
from datetime import datetime
from picamera2 import Picamera2
import time
import io
import os

def capture_image(picam2, counter, capture_images):
    #Add logic to extract gps coordinates for images taken
    latitude, longitude = 0,0
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not capture_images:
        image_stream = io.BytesIO()
        picam2.capture_file(image_stream, format='png')
        print("Captured image but not saving it.")
    else:
        directory = "/home/nicolaiaustad/Desktop/CropCounter/images/Folder_A"
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = f"{directory}/image_{timestamp}__lat{latitude}_lon{longitude}.png"
        picam2.capture_file(filename)
        print(f"Captured {filename}")
        
    #return latitude, longitude

