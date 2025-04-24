# Webcam Server

A simple FastAPI application that serves video files directly via HTTP.

## Features

- Direct HTTP video streaming without additional dependencies
- Built-in HTML interface with embedded video players
- Simple REST API endpoint to discover available videos
- Configurable via environment variables

## Requirements

- Python 3.7+
- FastAPI
- Uvicorn

## Setup

1. Clone the repository:
  ```bash
  git clone https://github.com/yourusername/webcam-server.git
  cd webcam-server
  ```

2. Run the setup script:
  ```bash
  ./setup.sh
  ```

3. Add video files to the `videos` directory:
  - video1.mp4
  - video2.mp4
  - video3.mp4
  - video4.mp4

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

2. Access the web interface at `http://localhost:3000` to view and play all available videos.

3. Videos can be streamed directly in any browser using the URLs provided.

## API

- `GET /`: Returns an HTML page with embedded video players for all available videos.

- `GET /videos`: Returns a JSON object containing information about all available video streams.
  
  Example response:
  ```json
  {
   "videos": {
    "video1": "http://localhost:3000/stream/video1",
    "video2": "http://localhost:3000/stream/video2",
    "video3": "http://localhost:3000/stream/video3",
    "video4": "http://localhost:3000/stream/video4"
   }
  }
  ```

- `GET /stream/{video_name}`: Streams the specified video directly via HTTP.