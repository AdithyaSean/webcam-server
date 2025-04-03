#!/bin/bash

# filepath: /home/adithya/Dev/Python/webcam-server/webcam-server.sh
function start_server() {
    # Default host and port
    HOST="0.0.0.0"
    PORT="3000"

    # Virtual environment directory
    VENV_DIR=".venv"

    # Get the directory where this script is located
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    
    # Change to the script directory to ensure proper paths for virtual env
    cd "$SCRIPT_DIR"

    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment..."
        python3 -m venv $VENV_DIR
        
        # Activate virtual environment and install requirements
        source "$VENV_DIR/bin/activate"
        echo "Installing requirements..."
        pip install -r requirements.txt
    else
        # Just activate the virtual environment
        source "$VENV_DIR/bin/activate"
    fi

    # Run the FastAPI app using uvicorn
    echo "Starting server on host $HOST and port $PORT..."
    uvicorn app:app --host "$HOST" --port "$PORT" --reload
}

function stop_server() {
    # Find all uvicorn processes running the app
    PIDS=$(pgrep -f "uvicorn app:app")

    if [ -z "$PIDS" ]; then
        echo "No webcam server instances found running."
        return 0
    fi

    # Kill all found processes
    for PID in $PIDS; do
        echo "Stopping webcam server process (PID: $PID)..."
        kill $PID
    done

    echo "Webcam server stopped successfully."
}

function show_help() {
    echo "Usage: webcam-server [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start          Start the webcam server"
    echo "  stop           Stop all running webcam server instances"
    echo "  restart        Restart the webcam server"
    echo "  help           Show this help message"
    echo ""
    echo "If no command is provided, the server will start by default."
}

# Handle command line arguments
case "$1" in
    "start")
        start_server
        ;;
    "stop")
        stop_server
        ;;
    "restart")
        stop_server
        sleep 1
        start_server
        ;;
    "help")
        show_help
        ;;
    "")
        # Default to starting the server if no arguments
        start_server
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac