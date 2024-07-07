# # Use the official Python image from the Docker Hub
# FROM python:3.11-slim

# # Set environment variables to noninteractive for apt-get
# ENV DEBIAN_FRONTEND=noninteractive

# # Set the working directory in the container
# WORKDIR /app

# # Copy the setup scripts and configuration files into the container
# COPY config/setup.sh /app/setup.sh
# COPY config/setup_config.sh /app/setup_config.sh
# COPY config/99-usb-stick.rules /app/config/99-usb-stick.rules
# COPY config/camera_script.service /app/config/camera_script.service
# COPY config/requirements.txt /app/config/requirements.txt

# # Make the setup scripts executable
# RUN chmod +x /app/setup.sh /app/setup_config.sh

# # Install necessary system packages
# RUN apt-get update && \
#     apt-get install -y \
#     systemd \
#     udev \
#     gdal-bin \
#     libgdal-dev \
#     build-essential \
#     python3-dev \
#     && apt-get clean

# # Set the GDAL environment variables
# ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
# ENV C_INCLUDE_PATH=/usr/include/gdal

# # Run the setup script to install system and Python dependencies
# RUN /app/setup.sh

# # Copy the rest of the application code to the working directory
# COPY . /app

# # Ensure the scripts have the right permissions
# RUN chmod +x /app/start_camera.sh /app/stop_camera.sh /app/start_camera_relay.sh

# # Expose any necessary ports (if applicable)
# # EXPOSE 8000

# # Set the default command to run the application
# CMD ["python3", "run.py"]


# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Copy configuration and setup scripts
COPY config/setup.sh /app/setup.sh
COPY config/setup_config.sh /app/setup_config.sh
COPY config/99-usb-stick.rules /app/config/99-usb-stick.rules
COPY config/camera_script.service /app/config/camera_script.service
COPY config/requirements.txt /app/config/requirements.txt

# Make the setup scripts executable
RUN chmod +x /app/setup.sh /app/setup_config.sh

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
    systemd \
    udev \
    gdal-bin \
    libgdal-dev \
    build-essential && \
    apt-get clean

# Run the setup script to install system and Python dependencies
RUN /app/setup.sh

# Ensure the scripts have the right permissions
RUN chmod +x /app/start_camera.sh /app/stop_camera.sh /app/start_camera_relay.sh

