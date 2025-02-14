#!/bin/bash

# Exit on error
set -e

echo "Setting up webcam server..."

# Remove existing virtual environment if it exists
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the application
echo "Starting webcam server..."
echo "To access from other devices in the network, use your computer's IP address instead of localhost"
python app.py

# Cleanup on exit
deactivate
