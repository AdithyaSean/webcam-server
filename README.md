# Webcam Server

A Flask-based webcam streaming server that supports multiple stream views of a single camera feed.

## Features

- Multiple stream views of the same camera feed
- Responsive grid layout that adapts to screen size
- Automatic virtual environment setup and dependency management
- Easy to run with different numbers of streams
- Cross-device accessible through network

## Requirements

- Python 3.x
- Webcam/Camera device
- Required packages (automatically installed):
  - Flask
  - OpenCV-Python
  - NumPy

## Installation & Setup

The project uses a virtual environment for dependency management. The setup is automated through the `run.sh` script.

1. Clone the repository:
```bash
git clone https://github.com/yourusername/webcam-server.git
cd webcam-server
```

2. Make the run script executable (if not already):
```bash
chmod +x run.sh
```

## Usage

Run the server using the provided shell script:

```bash
# Start with 1 stream (default)
./run.sh

# Start with 2 streams
./run.sh 2

# Start with 3 streams
./run.sh 3
```

The script will:
1. Create a virtual environment (if it doesn't exist)
2. Install required dependencies (on first run)
3. Start the Flask server with the specified number of streams

Access the streams through your web browser at:
```
http://localhost:3000
```

Or from other devices on the same network using:
```
http://<your-ip-address>:3000
```

## How It Works

- The server captures video from your default camera (usually the built-in webcam on laptops)
- Each stream view shows the same camera feed in real-time
- The web interface automatically adjusts the layout based on the number of streams
- All streams share a single camera instance for efficient resource usage

## Files

- `app.py`: Main Flask application with video streaming logic
- `run.sh`: Setup and run script with virtual environment management
- `requirements.txt`: Python package dependencies
