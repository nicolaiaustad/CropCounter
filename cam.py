from datetime import datetime
from picamera2 import Picamera2
import time
import os
import logging
import matplotlib.pyplot as plt


save_directory = "/home/dataplicity/remote"
if not os.path.exists(save_directory):
    os.makedirs(save_directory)
    
# Create and save the heatmap
plt.figure(figsize=(12, 10))


plt.title('Heatmap of Values')
plt.xlabel('UTM X Coordinate')
plt.ylabel('UTM Y Coordinate')

#plt.savefig("/home/nicolaiaustad/Desktop/heatmap_1sigma.png")
    
plt.savefig(f"{save_directory}/wormhole_heatmap_new04.png")
plt.close()

#print(f"Heatmap saved to {heatmap_output_path}")