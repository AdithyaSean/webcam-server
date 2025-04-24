#!/bin/bash
# Simplified setup script for HTTP video server
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Setting up HTTP video server environment..."
cd "$SCRIPT_DIR"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    echo "Please install Python 3.7 or higher"
    exit 1
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
echo "1. Add your video files to the videos/ directory"
echo "2. Start the server with: webcam-server start"
echo "For individual video streams, use URLs like: http://localhost:3000/video1, http://localhost:3000/video2, http://localhost:3000/video3, http://localhost:3000/video4"
echo "To stop the server, use: webcam-server stop"
echo "To check the server status, use: webcam-server status"
echo -e "${YELLOW}Note:${NC} Ensure you have the necessary permissions to access the webcam and video files."
echo "For more information, refer to the documentation."
