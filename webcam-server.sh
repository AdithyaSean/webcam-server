#!/bin/bash

# Webcam Server control script

WEBCAM_SERVER_DIR="/home/adithya/dev/personal/webcam-server"
MEDIAMTX_PATH="${WEBCAM_SERVER_DIR}/mediamtx"
VENV_PATH="${WEBCAM_SERVER_DIR}/.venv"

webcam-server() {
    case "$1" in
        start)
            echo "Starting Webcam Server..."
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
            
            # Check if MediaMTX is running
            if ! pgrep -f mediamtx > /dev/null; then
                echo "Starting MediaMTX..."
                cd "$WEBCAM_SERVER_DIR" && $MEDIAMTX_PATH &
                sleep 2
            else
                echo "MediaMTX is already running"
            fi
            
            # Start the FastAPI app
            cd "$WEBCAM_SERVER_DIR" && uvicorn app:app --host 0.0.0.0 --port 3000
            ;;
            
        stop)
            echo "Stopping Webcam Server..."
            pkill -f "uvicorn app:app"
            pkill -f mediamtx
            echo "Server stopped"
            ;;
            
        status)
            if pgrep -f "uvicorn app:app" > /dev/null; then
                echo "Webcam server is running"
            else
                echo "Webcam server is not running"
            fi
            
            if pgrep -f mediamtx > /dev/null; then
                echo "MediaMTX is running"
            else
                echo "MediaMTX is not running"
            fi
            ;;
            
        *)
            echo "Usage: webcam-server {start|stop|status}"
            echo "  start  - Start the webcam server"
            echo "  stop   - Stop the webcam server"
            echo "  status - Check if the server is running"
            ;;
    esac
}

# Export the function with all arguments passed to the script
webcam-server "$@"