#!/bin/bash 
set -e 
# Copy udev rules 
cp /app/config/99-usb-stick.rules /etc/udev/rules.d/ 
# Copy systemd service files 
cp /app/config/camera_script.service /etc/systemd/system/ 
# Reload udev rules 
udevadm control --reload-rules 
udevadm trigger 
# Enable and start systemd services 
systemctl daemon-reload 
systemctl enable camera_script.service 
systemctl start camera_script.service 
echo "Configuration setup complete."
