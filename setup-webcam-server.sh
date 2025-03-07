#!/bin/bash

# Get the absolute path of the webcam-server directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WEBCAM_SCRIPT="$SCRIPT_DIR/webcam-server.sh"

# Ensure script is executable
chmod +x "$WEBCAM_SCRIPT"

# Create ~/.local/bin if it doesn't exist
mkdir -p ~/.local/bin

# Create symbolic link in ~/.local/bin
LINK_PATH="$HOME/.local/bin/webcam-server"
ln -sf "$WEBCAM_SCRIPT" "$LINK_PATH"

# Check if ~/.local/bin is in PATH, if not, add it
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo "Added ~/.local/bin to your PATH in ~/.bashrc"
    echo "Please run 'source ~/.bashrc' or restart your terminal for this to take effect."
fi

# Remove the old scripts if they exist
if [ -f "$SCRIPT_DIR/run.sh" ]; then
    rm "$SCRIPT_DIR/run.sh"
    echo "Removed old run.sh script."
fi

if [ -f "$SCRIPT_DIR/stop-webcam-server.sh" ]; then
    rm "$SCRIPT_DIR/stop-webcam-server.sh"
    echo "Removed old stop-webcam-server.sh script."
fi

# Remove the old symbolic link if it exists
if [ -L "$HOME/.local/bin/webcam-server-stop" ]; then
    rm "$HOME/.local/bin/webcam-server-stop"
    echo "Removed old webcam-server-stop link."
fi

echo "Setup complete!"
echo "You can now run the webcam server from anywhere using the following commands:"
echo "  webcam-server start [N]  - Start with N streams (default: 1)"
echo "  webcam-server stop       - Stop all running servers"
echo "  webcam-server restart [N]- Restart with N streams"
echo "  webcam-server [N]        - Start with N streams"
echo "  webcam-server help       - Show help"
