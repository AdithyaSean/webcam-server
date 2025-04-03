#!/bin/bash

# filepath: /home/adithya/Dev/Python/webcam-server/webcam-server.sh

# Script to manage the webcam-server application

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Application name
APP_NAME="webcam-server"

# Default port
DEFAULT_PORT=3000

# Usage function
usage() {
    echo "Usage: $APP_NAME {start|stop|restart|status} [options]"
    echo "Options:"
    echo "  -p <port>   Specify the port number (default: $DEFAULT_PORT)"
    echo "  -h          Show this help message"
    exit 1
}

# Function to start the server
start() {
    local port=$DEFAULT_PORT
    
    # Parse options
    while getopts "p:h" opt; do
        case $opt in
            p)  port="$OPTARG" ;;
            h)  usage ;;
            \?) echo "Invalid option: -$OPTARG" >&2; usage ;;
        esac
    done
    shift $((OPTIND-1))

    # Check if the virtual environment is set up
    if [ ! -d "$SCRIPT_DIR/.venv" ]; then
        echo "Error: Virtual environment not found. Please run setup.sh first."
        exit 1
    fi

    # Activate the virtual environment
    source "$SCRIPT_DIR/.venv/bin/activate"

    # Check if the server is already running
    if is_running; then
        echo "Server is already running."
        exit 0
    fi

    # Change to the script directory before starting server
    cd "$SCRIPT_DIR"
    
    # Start the server in the background
    echo "Starting server on port $port..."
    uvicorn app:app --host 0.0.0.0 --port "$port" --reload &
    
    # Store the process ID
    echo $! > "$SCRIPT_DIR/$APP_NAME.pid"

    echo "Server started in the background."
}

# Function to stop the server
stop() {
    if ! is_running; then
        echo "Server is not running."
        exit 0
    fi

    # Get the process ID
    local pid=$(get_pid)

    # Stop the server
    echo "Stopping server (PID: $pid)..."
    kill "$pid"
    wait "$pid" 2>/dev/null # Wait for the process to terminate, discard errors
    
    # Remove the PID file
    rm -f "$SCRIPT_DIR/$APP_NAME.pid"

    echo "Server stopped."
}

# Function to restart the server
restart() {
    stop
    sleep 1 # Give it a second to fully stop
    start "$@" # Pass any options to the start function
}

# Function to check the server status
status() {
    if is_running; then
        echo "Server is running (PID: $(get_pid))."
    else
        echo "Server is not running."
    fi
}

# Helper function to get the process ID
get_pid() {
    if [ -f "$SCRIPT_DIR/$APP_NAME.pid" ]; then
        cat "$SCRIPT_DIR/$APP_NAME.pid"
    else
        echo ""
    fi
}

# Helper function to check if the server is running
is_running() {
    local pid=$(get_pid)
    if [ -n "$pid" ] && ps -p "$pid" > /dev/null; then
        return 0 # Running
    else
        return 1 # Not running
    fi
}

# Main script logic
case "$1" in
    start)
        start "${@:2}" # Pass along arguments after the command
        ;;
    stop)
        stop
        ;;
    restart)
        restart "${@:2}" # Pass along arguments after the command
        ;;
    status)
        status
        ;;
    *)
        usage
        ;;
esac

exit 0