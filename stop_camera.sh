#!/bin/bash
echo "Stopping camera script..." >> /home/nicolaiaustad/Desktop/stop_camera.log

if systemctl is-active --quiet camera_script.service; then
    systemctl stop camera_script.service
    echo "Camera script service stopped." >> /home/nicolaiaustad/Desktop/stop_camera.log
else
    echo "No running program found to stop." >> /home/nicolaiaustad/Desktop/stop_camera.log
fi
