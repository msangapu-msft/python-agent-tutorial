#!/bin/bash

echo "Custom startup script starting..."

# Check if /html directory exists, create if not
if [ ! -d "/html" ]; then
    echo "/html directory does not exist. Creating it..."
    mkdir /html
else
    echo "/html directory already exists."
fi

# Check if /html/50x.html already exists
if [ -f "/html/50x.html" ]; then
    echo "/html/50x.html already exists. Skipping copy."
else
    # Check if source file exists before copying
    if [ -f "/home/site/wwwroot/50x.html" ]; then
        echo "Copying 50x.html to /html/"
        cp /home/site/wwwroot/50x.html /html/50x.html
    else
        echo "50x.html not found in /home/site/wwwroot/"
    fi
fi
