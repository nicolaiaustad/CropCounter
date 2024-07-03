
from datetime import datetime
from picamera2 import Picamera2
import time

def capture_image(picam2, counter, capture_images):
    latitude, longitude = 0,0
    #latitude, longitude = generate_synthetic_gps(counter)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # if latitude is not None and longitude is not None:
    #     filename = f"/home/nicolaiaustad/Desktop/image_{timestamp}_lat{latitude}_lon{longitude}.jpg"
    # else:
    #     filename = f"/home/nicolaiaustad/Desktop/image_{timestamp}_nogps.jpg"
    if not capture_images:
        image_stream = io.BytesIO()
        picam2.capture_file(image_stream, format='png')
        print("Captured image but not saving it.")
    else:
        filename = f"/home/nicolaiaustad/Desktop/images/Folder_A/image_{timestamp}__lat{latitude}_lon{longitude}.png"
        picam2.capture_file(filename)
        print(f"Captured {filename}")
    #return latitude, longitude