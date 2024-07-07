# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables to noninteractive for apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory in the container
WORKDIR /app

# Copy the setup scripts and configuration files into the container
COPY config/setup.sh /app/setup.sh
COPY config/setup_config.sh /app/setup_config.sh
COPY config/99-usb-stick.rules /app/config/99-usb-stick.rules
COPY config/camera_script.service /app/config/camera_script.service
COPY config/requirements.txt /app/config/requirements.txt

# Make the setup scripts executable
RUN chmod +x /app/setup.sh /app/setup_config.sh

# Install necessary system packages
RUN apt-get update && \
    apt-get install -y systemd udev && \
    apt-get clean

# Run the setup script to install system and Python dependencies
RUN /app/setup.sh

# Copy the rest of the application code to the working directory
COPY . /app

# Run the configuration setup script
RUN /app/setup_config.sh

# Ensure the scripts have the right permissions
RUN chmod +x /app/start_camera.sh /app/stop_camera.sh /app/start_camera_relay.sh

# Set up systemd in the container
STOPSIGNAL SIGRTMIN+3
CMD ["/lib/systemd/systemd"]

# Expose any necessary ports (if applicable)
# EXPOSE 8000
