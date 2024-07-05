
from datetime import datetime
from picamera2 import Picamera2
import time
from PIL import Image
import io
import calculations
import random
import pyproj
import maps
import numpy as np
import pandas as pd
import capture
import os

# Initialize GPS
# session = gps.gps(mode=gps.WATCH_ENABLE)

# def get_gps_coordinates():
#     try:
#         report = session.next()
#         if report['class'] == 'TPV':
#             latitude = getattr(report, 'lat', 'Unknown')
#             longitude = getattr(report, 'lon', 'Unknown')
#             return latitude, longitude
#     except KeyError:
#         pass
#     except KeyboardInterrupt:
#         quit()
#     except StopIteration:
#         session = None
#         print("GPSD has terminated")
#     return None, None



def main(capture_images=False):
    
    BASE_DIR = '/home/nicolaiaustad/Desktop/CropCounter'
    shapefile_path = os.path.join(BASE_DIR, "trygve","trygve.shp")
    
    picam2 = Picamera2()
    # Configure the camera with high-resolution settings
    camera_config = picam2.create_still_configuration(
        main={
            "size": (4056, 3040),  # Maximum resolution for the camera
            "format": "RGB888"  # Use a high-quality format
        },
        controls={
            "ExposureTime": 10000,  # Adjust as needed for your lighting
            "AnalogueGain": 1.0,  # Set the gain to the lowest possible value to reduce noise
            "Brightness": 0.5,
            "Contrast": 1.0,
            "Saturation": 1.0,
            "Sharpness": 1.0
        }
    )

    # Apply the configuration
    picam2.configure(camera_config)
    picam2.set_controls({"ExposureTime": 4000, "AnalogueGain": 3.0})
    picam2.start()
    time.sleep(2)  # Allow the camera to warm up

    #Map settings
    proj_wgs84 = pyproj.CRS('EPSG:4326')  # WGS84  
 
    grid_size = 50
    grid_utm, grid_gps, df_utm, df_gps = maps.shp_to_grid(shapefile_path, grid_size) #returns grid in utm and df in wgs84 (degrees)
    init_lon = grid_gps[0,0]
    init_lat = grid_gps[0,1]
    value_map = [[]] #Store
    
    zone_number, hemisphere = maps.get_utm_zone(init_lon, init_lat)
    utm_crs = maps.create_utm_proj(zone_number, hemisphere)
    


    try:
        counter = 0
        while True:
            #capture.capture_image(picam2, counter, capture_images)
            random_index = np.random.choice(grid_gps.shape[0])
            random_gps_coords = grid_gps[random_index]
            
            longitude, latitude = random_gps_coords[0], random_gps_coords[1]
            utm_x, utm_y = maps.transform_to_utm(longitude, latitude, utm_crs)  #Here the mistake lies!
            
            df_row = maps.find_grid_cell(utm_x, utm_y, grid_size, df_utm)
            if df_row is not None:
                if df_utm.at[df_row, "measured"]== False: 
                    df_utm.at[df_row, "measured"] = True
                    df_utm.at[df_row, "values"] = random.randint(0,10)
                else:
                    continue #Throw away value calculated or make an average
                
            
            counter += 1
            value = calculations.AI_calculation("/home/nicolaiaustad/Desktop/CropCounter/dummy.png")+(counter % 10)
            
            time.sleep(2)  # Wait for 5 seconds before capturing the next image
    except KeyboardInterrupt:
        print("Program interrupted")
        
    finally:
        picam2.stop()
        maps.make_heatmap_and_save(df_utm, grid_size, 'heatmapNEW.png', '/home/nicolaiaustad/Desktop/CropCounter/generated_shape_files/SHAPE.shp', utm_crs )
    
if __name__ == "__main__":
    main(capture_images=False)





# import time
# import logging

# # Configure logging
# logging.basicConfig(
#     filename='/home/nicolaiaustad/Desktop/CropCounter/run.log',
#     level=logging.INFO,
#     format='%(asctime)s %(message)s'
# )

# def main():
#     logging.info('Program started.')
#     try:
#         while True:
#             logging.info('Program running...lol')
#             time.sleep(5)  # Log a message every 5 seconds
#     except Exception as e:
#         logging.error(f"Program encountered an error: {e}")
#     except KeyboardInterrupt:
#         logging.info('Program interrupted by user.')
#     finally:
#         logging.info('Program stopped.')

# if __name__ == "__main__":
#     main()


