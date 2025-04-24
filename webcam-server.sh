#!/bin/bash

# Webcam Server control script - Simplified for HTTP streaming

WEBCAM_SERVER_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
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
            cd "$WEBCAM_SERVER_DIR" && uvicorn app:app --host 0.0.0.0 --port 3000 &
            echo "http://localhost:3000/video1, http://localhost:3000/video2, http://localhost:3000/video3, http://localhost:3000/video4"
            echo "Press Ctrl+C to stop the server"
            echo "To stop the server, run: webcam-server stop"
            echo "To check the server status, run: webcam-server status"
            ;;
            
        stop)
            echo "Stopping HTTP Video Server..."
            pkill -f "uvicorn app:app"
            echo "Server stopped"
            ;;
            
        status)
            if pgrep -f "uvicorn app:app" > /dev/null; then
                echo "HTTP Video server is running"
                echo "Available video streams:"
                echo "  Video endpoints:"
                echo "Available video streams:"
                for i in {1..4}; do
                    if [ -f "${WEBCAM_SERVER_DIR}/videos/video${i}.mp4" ]; then
                        echo "  - video${i}: http://localhost:3000/video${i}"
                    fi
                done
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
