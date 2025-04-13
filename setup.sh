#!/bin/bash
# Simple setup script for webcam-server
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Setting up webcam-server environment..."
cd "$SCRIPT_DIR"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

# Check for FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}Warning: FFmpeg is not installed.${NC}"
    echo "FFmpeg is required for video streaming. Install with:"
    echo "    sudo apt update && sudo apt install ffmpeg"
    read -p "Install FFmpeg now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo apt update && sudo apt install ffmpeg -y
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to install FFmpeg.${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}Continuing without FFmpeg. Streaming won't work.${NC}"
    fi
fi

# Download MediaMTX if needed
if [ ! -f "$SCRIPT_DIR/mediamtx" ]; then
    echo -e "${YELLOW}Downloading MediaMTX...${NC}"
    ARCH=$(uname -m)
    if [ "$ARCH" = "x86_64" ]; then
        wget https://github.com/bluenviron/mediamtx/releases/download/v1.5.0/mediamtx_v1.5.0_linux_amd64.tar.gz -O mediamtx.tar.gz
    elif [ "$ARCH" = "aarch64" ]; then
        wget https://github.com/bluenviron/mediamtx/releases/download/v1.5.0/mediamtx_v1.5.0_linux_arm64.tar.gz -O mediamtx.tar.gz
    else
        echo -e "${RED}Unsupported architecture: $ARCH${NC}"
        exit 1
    fi
    
    tar -xzf mediamtx.tar.gz
    chmod +x "$SCRIPT_DIR/mediamtx"
    rm mediamtx.tar.gz
fi

# Create videos directory
mkdir -p videos

# Set up Python environment
echo "Setting up Python environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn

# Add webcam-server.sh to .bashrc if not already present
echo "Adding webcam-server.sh to .bashrc..."
BASHRC_FILE="$HOME/.bashrc"
WEBCAM_SERVER_PATH="$SCRIPT_DIR/webcam-server.sh"

# Create function in .bashrc instead of sourcing the script
if ! grep -q "webcam-server()" "$BASHRC_FILE"; then
    echo "" >> "$BASHRC_FILE"
    echo "# webcam-server command" >> "$BASHRC_FILE"
    echo "webcam-server() {" >> "$BASHRC_FILE"
    echo "    bash \"$WEBCAM_SERVER_PATH\" \"\$@\"" >> "$BASHRC_FILE"
    echo "}" >> "$BASHRC_FILE"
    echo -e "${GREEN}Added webcam-server() function to .bashrc${NC}"
    echo "You can now use 'webcam-server start|stop|status' from any terminal"
    echo "Please restart your terminal or run 'source ~/.bashrc' to apply changes"
else
    echo -e "${YELLOW}webcam-server() function is already in .bashrc${NC}"
fi

echo -e "${GREEN}Setup completed!${NC}"
echo -e "${YELLOW}To start the server:${NC}"
echo "1. Add video files to the videos/ directory"
echo "2. Start MediaMTX: ./mediamtx"
echo "3. Start the server: uvicorn app:app --host 0.0.0.0 --port 3000"
echo -e "${YELLOW}RTSP streams will be available at: rtsp://SERVER_IP:8554/video*${NC}"
