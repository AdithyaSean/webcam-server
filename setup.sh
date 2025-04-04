#!/bin/bash
# Setup script for webcam-server - Vision Computing Test Environment
# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Webcam Server - Vision Computing Test Environment${NC}"
echo -e "Setting up your environment..."

# Change to the script directory to ensure proper paths
cd "$SCRIPT_DIR"

# Virtual environment directory
VENV_DIR=".venv"

# Check for required dependencies
echo -e "\n${YELLOW}Checking system dependencies...${NC}"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    echo -e "Please install Python 3.8 or higher:${NC}"
    echo -e "    sudo apt update && sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if (( $(echo "$PYTHON_VERSION < 3.8" | bc -l) )); then
    echo -e "${RED}Error: Python 3.8 or higher is required. Found: Python $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}Python $PYTHON_VERSION detected.${NC}"

# Check for FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}Warning: FFmpeg is not installed.${NC}"
    echo -e "FFmpeg is required for video streaming. Install with:${NC}"
    echo -e "    sudo apt update && sudo apt install ffmpeg"
    
    # Ask if the user wants to install FFmpeg
    read -p "Do you want to install FFmpeg now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Installing FFmpeg...${NC}"
        sudo apt update && sudo apt install ffmpeg -y
        
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to install FFmpeg. Please install it manually.${NC}"
            exit 1
        fi
        echo -e "${GREEN}FFmpeg installed successfully.${NC}"
    else
        echo -e "${YELLOW}Continuing without FFmpeg. Streaming functionality will be limited.${NC}"
    fi
else
    echo -e "${GREEN}FFmpeg detected.${NC}"
fi

# Check for MediaMTX
if [ ! -f "$SCRIPT_DIR/mediamtx" ]; then
    echo -e "${YELLOW}MediaMTX not found in the project directory.${NC}"
    
    # Check if MediaMTX tarball exists, extract if it does
    if [ -f "$SCRIPT_DIR/mediamtx.tar.gz" ]; then
        echo -e "${YELLOW}Extracting MediaMTX from archive...${NC}"
        tar -xzf "$SCRIPT_DIR/mediamtx.tar.gz"
        
        if [ ! -f "$SCRIPT_DIR/mediamtx" ]; then
            echo -e "${RED}Failed to extract MediaMTX.${NC}"
            exit 1
        fi
        echo -e "${GREEN}MediaMTX extracted successfully.${NC}"
    else
        echo -e "${YELLOW}Downloading MediaMTX...${NC}"
        # Determine system architecture
        ARCH=$(uname -m)
        if [ "$ARCH" = "x86_64" ]; then
            echo -e "${YELLOW}Detected x86_64 architecture.${NC}"
            wget https://github.com/bluenviron/mediamtx/releases/download/v1.5.0/mediamtx_v1.5.0_linux_amd64.tar.gz -O mediamtx.tar.gz
        elif [ "$ARCH" = "aarch64" ]; then
            echo -e "${YELLOW}Detected ARM64 architecture.${NC}"
            wget https://github.com/bluenviron/mediamtx/releases/download/v1.5.0/mediamtx_v1.5.0_linux_arm64.tar.gz -O mediamtx.tar.gz
        else
            echo -e "${RED}Unsupported architecture: $ARCH${NC}"
            echo -e "${RED}Please download MediaMTX manually from: https://github.com/bluenviron/mediamtx/releases${NC}"
            exit 1
        fi
        
        # Extract the tarball
        tar -xzf mediamtx.tar.gz
        
        if [ ! -f "$SCRIPT_DIR/mediamtx" ]; then
            echo -e "${RED}Failed to download or extract MediaMTX.${NC}"
            exit 1
        fi
        echo -e "${GREEN}MediaMTX downloaded and extracted successfully.${NC}"
    fi
    
    # Make MediaMTX executable
    chmod +x "$SCRIPT_DIR/mediamtx"
else
    echo -e "${GREEN}MediaMTX detected.${NC}"
fi

# Create directories if they don't exist
echo -e "\n${YELLOW}Creating required directories...${NC}"
mkdir -p videos

# Check if there are any videos in the videos directory
VIDEO_COUNT=$(ls -1 "$SCRIPT_DIR/videos"/*.mp4 2>/dev/null | wc -l)
if [ "$VIDEO_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}No video files found in videos/ directory.${NC}"
    echo -e "${YELLOW}You need to add your own video files:${NC}"
    echo -e "  - video1.mp4, video2.mp4: Random people walking (for general testing)"
    echo -e "  - video3.mp4, video4.mp4: Known people (for attendance testing)"
else
    echo -e "${GREEN}Found $VIDEO_COUNT video files in videos/ directory.${NC}"
fi

# Create virtual environment if it doesn't exist
echo -e "\n${YELLOW}Setting up Python environment...${NC}"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv $VENV_DIR
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment.${NC}"
        exit 1
    fi
    
    # Activate virtual environment and install requirements
    source "$VENV_DIR/bin/activate"
    echo -e "${YELLOW}Installing requirements...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install requirements.${NC}"
        exit 1
    fi
    echo -e "${GREEN}Requirements installed successfully.${NC}"
else
    # Just activate the virtual environment for potential updates
    source "$VENV_DIR/bin/activate"
    echo -e "${YELLOW}Updating requirements...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to update requirements.${NC}"
        exit 1
    fi
    echo -e "${GREEN}Requirements updated successfully.${NC}"
fi

# Make webcam-server.sh executable
chmod +x "$SCRIPT_DIR/webcam-server.sh"

# Add as an app to .bashrc if not already present
echo -e "\n${YELLOW}Setting up command-line tools...${NC}"

# Check which method to use (function or alias)
SETUP_METHOD="function"  # Default to function

# Add as a function to .bashrc if not already present
if ! grep -q "webcam-server()" ~/.bashrc; then
    echo -e "${YELLOW}Adding webcam-server function to .bashrc...${NC}"
    echo "" >> ~/.bashrc
    echo "# Webcam Server - Vision Computing Test Environment" >> ~/.bashrc
    echo "webcam-server() {" >> ~/.bashrc
    echo "    $SCRIPT_DIR/webcam-server.sh \"\$@\"" >> ~/.bashrc
    echo "}" >> ~/.bashrc
    echo -e "${GREEN}Function added to .bashrc.${NC}"
else
    echo -e "${GREEN}Function already exists in .bashrc.${NC}"
fi

# Create a symbolic link to /usr/local/bin if the user has permission
if [ -w "/usr/local/bin" ]; then
    echo -e "${YELLOW}Creating symbolic link in /usr/local/bin...${NC}"
    sudo ln -sf "$SCRIPT_DIR/webcam-server.sh" /usr/local/bin/webcam-server
    echo -e "${GREEN}Link created. You can now use 'webcam-server' from anywhere.${NC}"
fi

# Test if the server can start and connect to MediaMTX
echo -e "\n${YELLOW}Testing server configuration...${NC}"

# Start MediaMTX in the background to test
"$SCRIPT_DIR/mediamtx" > /dev/null 2>&1 &
MEDIAMTX_PID=$!

# Give it a moment to start
sleep 2

# Check if MediaMTX is running
if kill -0 $MEDIAMTX_PID 2>/dev/null; then
    echo -e "${GREEN}MediaMTX server started successfully.${NC}"
    
    # Stop MediaMTX
    kill $MEDIAMTX_PID
    wait $MEDIAMTX_PID 2>/dev/null
else
    echo -e "${RED}Warning: MediaMTX server failed to start.${NC}"
    echo -e "${RED}You may need to check if port 8554 is already in use.${NC}"
fi

# Final Instructions
echo -e "\n${GREEN}Setup completed successfully!${NC}"
echo -e "${YELLOW}To use webcam-server:${NC}"
echo -e "  1. Restart your terminal or run: ${BLUE}source ~/.bashrc${NC}"
echo -e "  2. Start the server with: ${BLUE}webcam-server start${NC}"
echo -e "  3. Check status with: ${BLUE}webcam-server status${NC}"
echo -e ""
echo -e "${YELLOW}RTSP streaming will be available on port 8554${NC}"
echo -e "Example: ${BLUE}rtsp://YOUR_SERVER_IP:8554/video1${NC}"
echo -e ""
echo -e "${YELLOW}See README.md for complete documentation.${NC}"
