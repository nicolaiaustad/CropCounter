#!/bin/bash 
set -e 

# Install GDAL dependencies
apt-get update 
apt-get install -y gdal-bin libgdal-dev

# Install necessary system packages
apt-get install -y python3-pillow python3-numpy python3-pandas python3-pyproj python3-geopandas python3-matplotlib python3-seaborn python3-inotify python3-opencv python3-shapely python3-fiona

# Install Python dependencies from requirements.txt
pip install -r /app/config/requirements.txt
