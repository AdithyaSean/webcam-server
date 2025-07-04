
# hikvision_utils.py
# Utilities for connecting to Hikvision cameras via ONVIF, retrieving RTSP stream, and motion-based frame capture.

from onvif import ONVIFCamera
import cv2
import numpy as np
import time

def get_rtsp_url(host, port, username, password, wsdl_dir='/etc/onvif/wsdl'):
    """
    Connect to a Hikvision camera using ONVIF and retrieve the RTSP stream URL.
    """
    cam = ONVIFCamera(host, port, username, password, wsdl_dir)
    media_service = cam.create_media_service()
    profiles = media_service.GetProfiles()
    # Use the first profile by default
    token = profiles[0].token
    stream_setup = {
        'StreamSetup': {
            'Stream': 'RTP-Unicast',
            'Transport': {'Protocol': 'RTSP'}
        },
        'ProfileToken': token
    }
    uri = media_service.GetStreamUri(**stream_setup)
    return uri.Uri

def detect_motion_and_capture(rtsp_url, min_area=5000, capture_callback=None, cooldown=2.0):
    """
    Connect to RTSP stream, detect motion by comparing consecutive frames, and capture frames on motion.
    When motion is detected, the frame is passed to capture_callback(frame).
    cooldown: seconds to wait after a capture before detecting again (to avoid duplicate captures).
    """
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open RTSP stream: {rtsp_url}")

    prev_gray = None
    last_capture_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.5)
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if prev_gray is None:
            prev_gray = gray
            continue

        # Compute absolute difference between current frame and previous frame
        frame_delta = cv2.absdiff(prev_gray, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        motion_detected = False
        for contour in contours:
            if cv2.contourArea(contour) < min_area:
                continue
            motion_detected = True
            break

        if motion_detected and (time.time() - last_capture_time > cooldown):
            last_capture_time = time.time()
            if capture_callback:
                capture_callback(frame)

        prev_gray = gray

    cap.release()

# Example capture_callback for face recognition pipeline
def process_frame_for_face_recognition(frame):
    """
    Placeholder: Integrate with your face recognition pipeline here.
    For example, detect faces, identify, and log attendance.
    """
    # ... your face recognition logic ...
    pass

# Example usage:
# rtsp_url = get_rtsp_url('192.168.1.64', 80, 'admin', 'password')
# detect_motion_and_capture(rtsp_url, capture_callback=process_frame_for_face_recognition)
