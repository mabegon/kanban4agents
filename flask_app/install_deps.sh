#!/bin/bash

echo "Installing dependencies for Flask application..."

# Try to install pip if not available
if ! command -v pip3 &> /dev/null; then
    echo "Installing pip..."
    sudo apt update
    sudo apt install -y python3-pip
fi

# Install required packages
pip3 install flask flask-cors pyjwt bcrypt

echo "Dependencies installed successfully!"