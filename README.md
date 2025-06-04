# Webcam Server

A simple FastAPI application that serves video files as continuous looping streams directly via HTTP.

## Features

- Dynamic video discovery - automatically detects all video files in the videos directory
- Direct HTTP video streaming with continuous looping
- Support for multiple video formats (MP4, AVI, MOV, MKV, WebM, FLV)
- REST API endpoint to discover available videos
- Configurable via environment variables
- No web interface - pure API endpoints for easy integration

## Requirements

- Python 3.7+
- FastAPI
- Uvicorn

## Setup

1. Clone the repository:
  ```bash
  git clone https://github.com/AdithyaSean/webcam-server.git
  cd webcam-server
  ```

2. Run the setup script:
  ```bash
  ./setup.sh
  ```

3. Add video files to the `videos` directory:
  - Any video files with supported extensions (mp4, avi, mov, mkv, webm, flv)
  - Files will be automatically discovered and made available for streaming
  - Example: video1.mp4, mycamera.avi, recording.mov

## Configuration

The application can be configured using environment variables:
- `SERVER_IP`: The host:port to advertise for streams (default: "localhost:3000")

## Usage

1. Start the webcam server:
  ```bash
  webcam-server start
  ```
  
  Or manually with:
  ```bash
  uvicorn app:app --host 0.0.0.0 --port 3000
  ```

2. Videos can be accessed directly via their streaming endpoints.

3. List all available videos:
  ```bash
  curl http://localhost:3000/
  ```

## API

- `GET /`: Lists all available video streams with their endpoints and file information.
  
- `GET /{video_name}`: Streams the specified video directly via HTTP.
  This endpoint will stream the video in an endless loop.

  Examples:
  ```bash
  # List all available videos
  curl http://localhost:3000/
  
  # Stream a specific video
  ffplay http://localhost:3000/video1
  ffplay http://localhost:3000/mycamera
  ```

The video name is derived from the filename without the extension. For example:
- `video1.mp4` → accessible at `/video1`
- `mycamera.avi` → accessible at `/mycamera`
- `recording.mov` → accessible at `/recording`
