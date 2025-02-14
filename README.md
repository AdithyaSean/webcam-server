# Webcam Server

A simple Python application that streams webcam output over HTTP within your local network using Flask and OpenCV.

## Requirements

- Python 3.x
- Webcam access
- macOS/Linux/Windows

## Installation

1. Clone this repository:
```bash
git clone https://github.com/AdithyaSean/webcam-server
cd webcam-server
```

2. Run the setup script:
```bash
./run.sh
```

The script will:
- Create a Python virtual environment
- Install required dependencies
- Start the webcam server

## Usage

1. After running the setup script, the server will start at:
   - Local access: http://localhost:5000
   - Network access: http://<your-ip-address>:5000

2. Open the URL in a web browser to view the webcam stream.

## Files

- `app.py`: Main application code for webcam capture and streaming
- `requirements.txt`: Python package dependencies
- `run.sh`: Setup and execution script

## Troubleshooting

1. **Camera Access Permission**
   - On macOS: Allow camera access in System Preferences > Security & Privacy > Camera
   - On Windows: Allow camera access in Settings > Privacy > Camera

2. **Package Installation Issues**
   - The script will automatically create a fresh virtual environment and install dependencies
   - If you encounter NumPy/OpenCV compatibility issues, the script handles this by using compatible versions

## Notes

- The stream is accessible to any device on your local network
- For security, the server only binds to your local network
- Close the terminal window to stop the server

## Security Warning

This is a basic implementation meant for local network use. Do not expose this server to the public internet without implementing proper security measures.
