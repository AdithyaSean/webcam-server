# Hikvision Camera Integration Documentation

## Overview
This document describes the integration of a Hikvision camera into the project using the ONVIF protocol. The integration enables programmatic connection, authentication, and retrieval of the RTSP stream URL, as well as efficient motion-based frame capture for downstream face recognition and attendance logging.

## Features Implemented

### 1. ONVIF Camera Connection & RTSP URL Retrieval
- Utilizes the ONVIF protocol to connect to a Hikvision camera.
- Authenticates using provided credentials.
- Programmatically retrieves the correct RTSP stream URL (no manual configuration required).
- Implemented in the function: `get_rtsp_url(host, port, username, password, wsdl_dir)`.

### 2. Motion Detection & Frame Capture
- Connects to the camera's RTSP stream using OpenCV.
- Compares consecutive frames to detect significant changes (motion detection).
- Only captures and processes frames when motion is detected, reducing computational overhead.
- Cooldown logic prevents duplicate captures within a short time window.
- Implemented in the function: `detect_motion_and_capture(rtsp_url, min_area, capture_callback, cooldown)`.

### 3. Face Recognition Pipeline Integration (Pluggable)
- When motion is detected, the captured frame is passed to a callback function for further processing.
- A placeholder function `process_frame_for_face_recognition(frame)` is provided for integration with the face recognition and attendance logging pipeline.

## Example Usage
```python
rtsp_url = get_rtsp_url('192.168.1.64', 80, 'admin', 'password')
detect_motion_and_capture(rtsp_url, capture_callback=process_frame_for_face_recognition)
```

## File: hikvision_utils.py
- Contains all the above logic and is ready for integration with the rest of the application.

## Next Steps
- Implement the actual face recognition logic in `process_frame_for_face_recognition`.
- Integrate with the attendance logging system as needed.

---
This document summarizes the work completed for the Hikvision camera integration phase as per project requirements.
