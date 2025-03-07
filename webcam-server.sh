#!/bin/bash

function start_server() {
    # Get number of streams from command line argument, default to 1 if not provided
    num_streams=${1:-1}

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
}

function stop_server() {
    # Find all Python processes running the webcam server app.py
    PIDS=$(pgrep -f "python3 app.py")

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
    echo "Usage: webcam-server [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start [N]    Start the webcam server with N streams (default: 1)"
    echo "  stop         Stop all running webcam server instances"
    echo "  restart [N]  Restart the webcam server with N streams (default: 1)"
    echo "  help         Show this help message"
    echo ""
    echo "If no command is provided, the server will start with 1 stream by default."
}

# Handle command line arguments
case "$1" in
    "start")
        start_server "$2"
        ;;
    "stop")
        stop_server
        ;;
    "restart")
        stop_server
        sleep 1
        start_server "$2"
        ;;
    "help")
        show_help
        ;;
    "")
        # Default to starting with 1 stream if no arguments
        start_server 1
        ;;
    *)
        if [[ "$1" =~ ^[0-9]+$ ]]; then
            # If first arg is a number, treat it as number of streams
            start_server "$1"
        else
            echo "Unknown command: $1"
            show_help
            exit 1
        fi
        ;;
esac
