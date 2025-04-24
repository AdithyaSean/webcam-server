#!/bin/bash

# Webcam Server control script - Simplified for HTTP streaming

WEBCAM_SERVER_DIR="/home/adithya/dev/personal/webcam-server"
VENV_PATH="${WEBCAM_SERVER_DIR}/.venv"

webcam-server() {
    case "$1" in
        start)
            echo "Starting HTTP Video Server..."
            # Check if virtual environment exists and create if needed
            if [ ! -d "$VENV_PATH" ]; then
                echo "Creating Python virtual environment..."
                cd "$WEBCAM_SERVER_DIR"
                python3 -m venv .venv
                source "$VENV_PATH/bin/activate"
                pip install --upgrade pip
                pip install fastapi uvicorn
            else
                source "$VENV_PATH/bin/activate"
            fi
            
            # Start the FastAPI app
            cd "$WEBCAM_SERVER_DIR" && uvicorn app:app --host 0.0.0.0 --port 3000
            ;;
            
        stop)
            echo "Stopping HTTP Video Server..."
            pkill -f "uvicorn app:app"
            echo "Server stopped"
            ;;
            
        status)
            if pgrep -f "uvicorn app:app" > /dev/null; then
                echo "HTTP Video server is running"
            else
                echo "HTTP Video server is not running"
            fi
            ;;
            
        *)
            echo "Usage: webcam-server {start|stop|status}"
            echo "  start  - Start the HTTP video server"
            echo "  stop   - Stop the HTTP video server"
            echo "  status - Check if the server is running"
            ;;
    esac
}

# Export the function with all arguments passed to the script
webcam-server "$@"