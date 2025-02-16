#!/bin/bash

# Get number of streams from command line argument, default to 1 if not provided
num_streams=${1:-1}

# Virtual environment directory
VENV_DIR=".venv"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv $VENV_DIR
    
    # Activate virtual environment and install requirements
    source $VENV_DIR/bin/activate
    echo "Installing requirements..."
    pip install -r requirements.txt
else
    # Just activate the virtual environment
    source $VENV_DIR/bin/activate
fi

# Run the Flask app with the specified number of streams
echo "Starting server with $num_streams stream(s)..."
python3 app.py $num_streams
