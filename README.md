# Webcam Server - Vision Computing Test Environment

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful command-line tool to simulate webcam feeds and RTSP streams for testing computer vision applications. Particularly useful for testing real-time attendance marking and face recognition systems during development.

## Features

- 🎥 **Multiple RTSP Video Streams**: Stream video files as RTSP streams for testing
- 🖥️ **Dual Camera Testing**: Test applications that use multiple camera inputs
- 🧪 **Test Scenarios**: Pre-configured test modes for attendance, recognition, and performance testing
- 📊 **Test Reports**: Generate reports to track your application's performance
- 🔧 **Highly Customizable**: Configure ports, streams, and test parameters via CLI
- 🚀 **Streamlined Development**: Save time by skipping manual testing with real cameras

## Requirements

- Linux (Ubuntu/Debian recommended)
- Python 3.8+
- FFmpeg
- [MediaMTX](https://github.com/bluenviron/mediamtx) (included)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/AdithyaSean/webcam-server.git
cd webcam-server
```

2. Run the setup script:

```bash
chmod +x setup.sh
./setup.sh
```

This will create a Python virtual environment and install all required dependencies.

3. Place your test videos in the `videos/` directory:
   - `video1.mp4`, `video2.mp4`: Random people walking (for general testing)
   - `video3.mp4`, `video4.mp4`: Known people (for attendance testing)

## Quick Start

Start the server with default settings:

```bash
webcam-server start
```

Check server status:

```bash
webcam-server status
```

Access the RTSP streams in your application or media player:
- `rtsp://SERVER_IP:8554/video1` - Random people
- `rtsp://SERVER_IP:8554/video2` - Random people
- `rtsp://SERVER_IP:8554/video3` - Known people for attendance
- `rtsp://SERVER_IP:8554/video4` - Known people for attendance

Access the REST API at:
- `http://SERVER_IP:3000`

## Usage

The `webcam-server` CLI provides a comprehensive set of commands to help you test your computer vision applications:

```
USAGE:
  webcam-server COMMAND [OPTIONS]

COMMANDS:
  start         Start the webcam server
  stop          Stop the webcam server
  restart       Restart the webcam server
  status        Check server status
  test          Run a specific test scenario (see test options below)
  stream        Stream a specific video
  list          List available videos and test scenarios
  log           View server logs
  config        View or edit configuration

GENERAL OPTIONS:
  -p <port>       Specify the REST API port number (default: 3000)
  -r <rtsp_port>  Specify the RTSP port number (default: 8554)
  -s <streams>    Enable specific video streams (comma-separated, e.g., 1,3)
  -h              Show this help message

TEST OPTIONS:
  -m <mode>       Test mode: standard, attendance, recognition, performance
  -d <duration>   Test duration in seconds (for performance tests)
  -c <cameras>    Specify camera setup: single, dual (default: dual)
  -g              Generate test report
```

### Examples

Start the server with custom ports:
```bash
webcam-server start -p 8080 -r 5554
```

Start with only specific video streams:
```bash
webcam-server start -s 3,4
```

Run an attendance test with dual cameras:
```bash
webcam-server test -m attendance -c dual -s 3,4
```

Run a performance test and generate a report:
```bash
webcam-server test -m performance -d 120 -g
```

Stream a specific video and view it:
```bash
webcam-server stream -s 3
```

View and edit configuration:
```bash
webcam-server config
webcam-server config -a edit -k recognition_threshold -v 0.85
```

## Testing Computer Vision Applications

### Attendance System Testing

For testing a dual-camera attendance marking system:

1. Start the server with known people videos:
```bash
webcam-server start -s 3,4
```

2. Run an attendance test:
```bash
webcam-server test -m attendance -c dual -d 300
```

3. Check attendance records:
```bash
curl http://localhost:3000/attendance
```

### Face Recognition Testing

For testing face recognition accuracy:

1. Start the server:
```bash
webcam-server start
```

2. Run a recognition test:
```bash
webcam-server test -m recognition -d 180 -g
```

3. View the generated test report for recognition metrics.

## REST API Endpoints

The webcam-server exposes several API endpoints:

- `GET /`: Server information and available streams
- `GET /status`: Current server status
- `GET /restart-rtsp`: Restart the RTSP streaming server
- `POST /test/{mode}`: Start a test (mode: standard, attendance, recognition, performance)
- `GET /test/report`: Get the most recent test report
- `GET /test/list`: List all completed tests
- `GET /config`: Get current configuration
- `POST /config`: Update configuration
- `GET /attendance`: Get attendance records
- `POST /attendance/mark`: Manually mark attendance

## Integration with Computer Vision Projects

### Using in Python Projects

```python
import cv2
import requests

# Start a test
response = requests.post(
    "http://localhost:3000/test/attendance",
    json={"duration": 300, "camera_setup": "dual", "streams": "3,4"}
)

# Connect to RTSP streams
cap1 = cv2.VideoCapture("rtsp://localhost:8554/video3")
cap2 = cv2.VideoCapture("rtsp://localhost:8554/video4")

# Process frames...
while True:
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()
    
    if not ret1 or not ret2:
        break
        
    # Process frames with your computer vision algorithms
    # ...
    
    # Mark attendance when a person is recognized
    if person_recognized:
        requests.post(
            "http://localhost:3000/attendance/mark",
            json={
                "id": "P001",
                "name": "John Smith",
                "department": "Engineering",
                "recognition_confidence": 0.92
            }
        )
```

## Architecture

The webcam-server consists of several components:

1. **MediaMTX**: A lightweight RTSP server that hosts video streams
2. **FFmpeg**: Used to read video files and publish them to the RTSP server
3. **FastAPI Server**: Provides the REST API for controlling and monitoring the system
4. **CLI Interface**: A user-friendly command-line interface for controlling the system

## Troubleshooting

### Common Issues

- **"Connection refused" error**: Make sure the MediaMTX server is running. Try restarting with `webcam-server restart`.
- **No video in streams**: Check that your video files exist in the `videos/` directory.
- **FFmpeg processes becoming defunct**: This typically happens if the MediaMTX server isn't running properly. Check logs with `webcam-server log`.

### Checking Logs

View the server logs to diagnose issues:

```bash
webcam-server log
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

[Adithya Sean](https://github.com/AdithyaSean)

---

For more information, visit the [GitHub repository](https://github.com/AdithyaSean/webcam-server).