# Webcam Server

A simple FastAPI application that creates RTSP streams from video files using FFmpeg.

## Features

- Automatically streams video files via RTSP
- Loops videos continuously
- Simple REST API endpoint to discover available streams
- Configurable via environment variables

## Requirements

- Python 3.7+
- FastAPI
- Uvicorn
- FFmpeg
- [MediaMTX](https://github.com/bluenviron/mediamtx) RTSP server

## Setup

1. Clone the repository:
  ```bash
  git clone https://github.com/yourusername/webcam-server.git
  cd webcam-server
  ```

2. Install dependencies:
  ```bash
  pip install fastapi uvicorn
  ```

3. Ensure FFmpeg is installed:
  ```bash
  sudo apt install ffmpeg  # For Ubuntu/Debian
  ```

4. Download and set up MediaMTX following their documentation

5. Add video files to the `videos` directory:
  - video1.mp4
  - video2.mp4
  - video3.mp4
  - video4.mp4

## Configuration

The application can be configured using environment variables:
- `RTSP_PORT`: The port for RTSP streaming (default: 8554)
- `SERVER_IP`: The IP address to advertise for streams (default: "localhost")

## Usage

1. Start the MediaMTX server:
  ```bash
  ./mediamtx
  ```

2. Start the webcam server:
  ```bash
  uvicorn app:app --host 0.0.0.0 --port 3000
  ```

3. Access the API at `http://localhost:3000` to get a list of available RTSP streams.

4. Connect to the streams using any RTSP client (e.g., VLC Media Player) with the URLs provided by the API.

## API

- `GET /`: Returns a JSON object containing information about all available RTSP streams.
  
  Example response:
  ```json
  {
   "streams": {
    "video1": "rtsp://localhost:8554/video1",
    "video2": "rtsp://localhost:8554/video2",
    "video3": "rtsp://localhost:8554/video3",
    "video4": "rtsp://localhost:8554/video4"
   }
  }
  ```