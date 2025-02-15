#!/bin/bash

# Exit on error
set -e

echo "Setting up webcam server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    # Create virtual environment if it doesn't exist
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    # Install requirements
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    # Just activate existing virtual environment
    echo "Activating existing virtual environment..."
    source venv/bin/activate
fi

# Run the application
echo "Starting webcam server..."
echo "To access from other devices in the network, use your computer's IP address instead of localhost"
python app.py

# Cleanup on exit
deactivate