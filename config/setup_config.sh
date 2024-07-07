#!/bin/bash
set -e

# Copy udev rules
sudo cp config/99-usb-stick.rules /etc/udev/rules.d/

# Copy systemd service files
sudo cp config/camera_script.service /etc/systemd/system/

# Reload udev rules if the command exists
if command -v udevadm &> /dev/null; then
    sudo udevadm control --reload-rules
    sudo udevadm trigger
else
    echo "udevadm not found, skipping udev rule reload"
fi

# Enable and start systemd services if systemctl exists
if command -v systemctl &> /dev/null; then
    sudo systemctl daemon-reload
    sudo systemctl enable camera_script.service
    sudo systemctl start camera_script.service
else
    echo "systemctl not found, skipping systemd service setup"
fi

echo "Configuration setup complete."
