
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
import load_settings
import logging
from inotify.adapters import Inotify
import signal

#Logging to check performance through script
logging.basicConfig(
    filename='/home/nicolaiaustad/Desktop/CropCounter/run.log',
    level=logging.DEBUG,  # Adjust as needed
    format='%(asctime)s %(levelname)s %(message)s'
)

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

#Raises a signal when /tmp/usb_inserted does not exist anymore
def signal_handler(sig, frame):
    logging.info("Signal received, exiting...")
    raise KeyboardInterrupt

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main(capture_images=False):
    
    logging.info('run.py script started')
    mount_point = '/mnt/usb_settings'
    device = '/dev/sda1'  # Adjust this as needed
    mount_point = load_settings.mount_usb(mount_point, device) # Ensure the USB is mounted
    settings_dest = '/tmp/settings.txt' # Destinations defined on the USB stick
    shapefiles_dest = '/tmp/shapefiles'
    load_settings.copy_settings_and_shapefiles(mount_point, settings_dest, shapefiles_dest) # Copy settings and shapefiles from USB
    settings = load_settings.read_settings_file(settings_dest)  # Read settings
    
    # This is not being used now, but can be used to write the settings to a file in the directory
    with open('/tmp/usb_settings.env', 'w') as file:
        for key, value in settings.items():
            file.write(f'{key}={value}\n')
           
    job_name = str(settings['JOB_NAME'])
    grid_size = int(settings['GRID_SIZE'])
    float_number = float(settings['FLOAT'])
    print(job_name, grid_size, float_number)
    
    # Find the shapefile with an arbitrary name
    shapefile_path = load_settings.find_shapefile(shapefiles_dest)
    #shapefile_path = load_settings.find_shapefile('/home/nicolaiaustad/Desktop/CropCounter/trygve')  #Can use this shapefile when usb_settings stick not inserted
    if not shapefile_path:
        print("No shapefile found in", shapefiles_dest)
        return
    print("Using shapefile:", shapefile_path)
    
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
    grid_utm, grid_gps, df_utm, df_gps = maps.shp_to_grid(shapefile_path, grid_size) #returns grid in utm and df in wgs84 (degrees)
    init_lon = grid_gps[0,0]
    init_lat = grid_gps[0,1]
    zone_number, hemisphere = maps.get_utm_zone(init_lon, init_lat)
    utm_crs = maps.create_utm_proj(zone_number, hemisphere)
    
    try:
        counter = 0
        logging.info('Now the While loop starts...')
        while True:
            ### Comment out the three next lines when running the script manually
            # if not os.path.exists('/tmp/usb_inserted'):
            #     logging.info('USB stick removed, breaking the loop.')
            #     raise KeyboardInterrupt
            
            capture.capture_image(picam2, counter, capture_images)  #Enable this when actually capturing images
            value = calculations.AI_calculation("/home/nicolaiaustad/Desktop/CropCounter/dummy.png")+(counter % 10) #Extract value from captured image
            
            #Add logic that deletes image to save storage here, but save maybe every 100 image for backtracking
            
            #Use these to find gps coordinates when no gps module is attached
            random_index = np.random.choice(grid_gps.shape[0]) 
            random_gps_coords = grid_gps[random_index]
            longitude, latitude = random_gps_coords[0], random_gps_coords[1]
            
            utm_x, utm_y = maps.transform_to_utm(longitude, latitude, utm_crs)  #Transform wgs84 coordinates from gps to UTM coordinates to map to utm_grid
            df_row = maps.find_grid_cell(utm_x, utm_y, grid_size, df_utm)
            if df_row is not None:
                if df_utm.at[df_row, "measured"]== False: 
                    df_utm.at[df_row, "measured"] = True
                    df_utm.at[df_row, "values"] = value
                else:
                    #Add logic that throws away value if a value has been stores for that grid square
                    continue #Throw away value calculated or make an average
            
            counter += 1
            logging.info('Still calculating values from gps...')
            
            time.sleep(2)  #Adjust this to decide how often to capture images.
            #Consider adding logic to capture two consecutive images to calibrate for black holes and shadows
            
    except KeyboardInterrupt:
        print("Program interrupted")
        logging.info("Program interrupted")
    finally:
        logging.info("Cleaning up resources...")
        try:
            picam2.stop()
        except Exception as e:
            logging.error(f"Error stopping camera: {e}")

        try:
            # Save the generated files to the USB stick
            maps.make_heatmap_and_save(df_utm, grid_size, f'/tmp/{job_name}.png', f'/tmp/{job_name}', utm_crs)
            heatmap_folder = os.path.join(mount_point, 'generated_heatmaps')
            generated_shapefiles_folder = os.path.join(mount_point, 'generated_shapefiles')
            os.makedirs(heatmap_folder, exist_ok=True)
            os.makedirs(generated_shapefiles_folder, exist_ok=True)
            load_settings.copy_files(f'/tmp/{job_name}.png', heatmap_folder)
            load_settings.copy_files(f'/tmp/{job_name}', generated_shapefiles_folder)
            
            # Unmount the USB stick
            time.sleep(4)
            load_settings.unmount_usb(mount_point)
            logging.info('Now generated files should be saved...')
        except Exception as e:
            logging.error(f"Error during final file handling: {e}")
            
if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Re-running the script with sudo...")
        logging.info("Re-running the script with sudo...")
        try:
            load_settings.subprocess.run(['sudo', 'python3'] + load_settings.sys.argv)
        except KeyboardInterrupt:
            pass
    else:
        main(capture_images=False)



### Use this script to verify that run.py actually runs when needed

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























#TO NICOLAI. I think the problem is that the mount point connects to the swithc usb as it just looks for any usb. Must ensure that it mounts the other usb.