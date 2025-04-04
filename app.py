from pathlib import Path
from typing import List, Dict, Optional, Any
from contextlib import asynccontextmanager
import os
import threading
import time
import subprocess
import socket
import logging
import signal
import sys
import json
from datetime import datetime

from fastapi import FastAPI, HTTPException, status, Body, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# --- Configuration ---
VIDEO_DIR = Path("videos")  # Directory containing the video files
VIDEO_FILE_1 = VIDEO_DIR / "video1.mp4"
VIDEO_FILE_2 = VIDEO_DIR / "video2.mp4"
VIDEO_FILE_3 = VIDEO_DIR / "video3.mp4"
VIDEO_FILE_4 = VIDEO_DIR / "video4.mp4"
VIDEO_FILES = [VIDEO_FILE_1, VIDEO_FILE_2, VIDEO_FILE_3, VIDEO_FILE_4]

# Get RTSP port from environment variable or use default 8554
RTSP_PORT = int(os.environ.get("RTSP_PORT", 8554))
# Get enabled streams from environment variable or enable all
ENABLED_STREAMS = os.environ.get("ENABLED_STREAMS", "1,2,3,4")

# Global variables
FFMPEG_PROCESSES = []  # Will hold FFmpeg process instances
MEDIAMTX_PROCESS = None  # Will hold the MediaMTX process
ACTIVE_TEST = None  # Will store information about the active test
TEST_RESULTS = {}  # Will store test results
CONFIG = {
    "rtsp_port": RTSP_PORT,
    "enabled_streams": ENABLED_STREAMS,
    "test_mode": "standard",
    "camera_setup": "dual",
    "recognition_threshold": 0.8,
    "performance_test_duration": 60,
    "attendance_mode": "auto"
}
# --- ---

# --- Data Models ---
class TestConfig(BaseModel):
    duration: int = 60
    camera_setup: str = "dual"
    streams: str = "1,2,3,4"

class ConfigUpdateRequest(BaseModel):
    key: str
    value: str

class Person(BaseModel):
    id: str
    name: str
    department: str
    attendance_status: Optional[str] = None
    recognition_confidence: Optional[float] = None
    last_seen: Optional[str] = None

# --- Lifespan Events ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup events
    if not VIDEO_DIR.is_dir():
        print(f"Warning: Video directory '{VIDEO_DIR}' not found. Creating it.")
        VIDEO_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Please place video files inside the '{VIDEO_DIR}' directory.")

    for video_file in VIDEO_FILES:
        if not video_file.is_file():
            print(f"Warning: Video file '{video_file}' not found in '{VIDEO_DIR}'.")
    
    # Parse enabled streams
    streams = [s.strip() for s in ENABLED_STREAMS.split(",") if s.strip()]
    print(f"Enabled streams: {', '.join(streams)}")
    
    # Start RTSP server
    start_rtsp_server()
    
    yield
    
    # Shutdown events - Stop RTSP server
    stop_rtsp_server()

app = FastAPI(lifespan=lifespan)

# --- MediaMTX Server Functions ---
def start_mediamtx_server():
    """Start the MediaMTX RTSP server if not already running"""
    global MEDIAMTX_PROCESS
    
    # Check if MediaMTX process is running
    try:
        # Look for mediamtx processes
        result = subprocess.run(
            ["pgrep", "-f", "mediamtx"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0:
            # MediaMTX is already running
            print("MediaMTX RTSP server is already running.")
            return True
        
        # Start MediaMTX
        mediamtx_path = Path("./mediamtx")
        if not mediamtx_path.exists():
            print("Error: MediaMTX executable not found. Please ensure it's in the current directory.")
            return False
        
        print(f"Starting MediaMTX RTSP server on port {RTSP_PORT}")
        
        # Start MediaMTX in the background
        MEDIAMTX_PROCESS = subprocess.Popen(
            ["./mediamtx"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Give it a moment to start
        time.sleep(1)
        
        if MEDIAMTX_PROCESS.poll() is None:
            print(f"MediaMTX RTSP server started successfully on port {RTSP_PORT}")
            return True
        else:
            print("Error: Failed to start MediaMTX RTSP server.")
            return False
    except Exception as e:
        print(f"Error starting MediaMTX: {e}")
        return False

# --- RTSP Server Functions ---
def start_rtsp_server():
    """Start the RTSP streaming using MediaMTX and FFmpeg"""
    global FFMPEG_PROCESSES
    
    if FFMPEG_PROCESSES:
        print("RTSP streaming processes are already running.")
        return
    
    # Check if ffmpeg is installed
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error: FFmpeg is not installed or not found in PATH. Please install FFmpeg.")
        return

    # First, ensure MediaMTX is running
    if not start_mediamtx_server():
        print("Failed to start RTSP server. Cannot proceed with streaming.")
        return
    
    print(f"Starting RTSP server on port {RTSP_PORT}")
    
    # Parse enabled streams
    enabled_streams = [int(s.strip()) for s in ENABLED_STREAMS.split(",") if s.strip().isdigit()]
    
    # Create an RTSP stream for each enabled video file
    for idx, video_file in enumerate(VIDEO_FILES, 1):
        if idx not in enabled_streams:
            print(f"Skipping video{idx} as it's not in enabled streams: {ENABLED_STREAMS}")
            continue
            
        if video_file.is_file():
            # Start FFmpeg process for streaming this video
            stream_path = f"video{idx}"
            rtsp_url = f"rtsp://127.0.0.1:{RTSP_PORT}/{stream_path}"
            
            print(f"Setting up stream for {video_file} at {rtsp_url}")
            
            # FFmpeg command to loop video and publish to MediaMTX RTSP server
            cmd = [
                "ffmpeg",
                "-re",                  # Read input at native frame rate
                "-stream_loop", "-1",   # Loop forever
                "-i", str(video_file),  # Input file
                "-c:v", "copy",         # Copy video codec (no re-encoding)
                "-c:a", "copy",         # Copy audio codec (no re-encoding)
                "-f", "rtsp",           # Output format: RTSP
                "-rtsp_transport", "tcp", # Use TCP for RTSP
                rtsp_url                # Output URL
            ]
            
            try:
                # Start the FFmpeg process
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                FFMPEG_PROCESSES.append(process)
                
                # Give it a moment to connect
                time.sleep(0.5)
                
                # Check if process is still running
                if process.poll() is None:
                    print(f"Started streaming {video_file.name} to RTSP at rtsp://SERVER_IP:{RTSP_PORT}/{stream_path}")
                else:
                    stdout, stderr = process.communicate()
                    print(f"Error starting FFmpeg for {video_file.name}. Process exited with code {process.returncode}")
                    print(f"Error: {stderr}")
            except subprocess.SubprocessError as e:
                print(f"Error starting FFmpeg for {video_file.name}: {e}")
    
    if FFMPEG_PROCESSES:
        print(f"RTSP server started on port {RTSP_PORT} with {len(FFMPEG_PROCESSES)} streams")
    else:
        print("No RTSP streams were started. Check if video files exist.")

def stop_rtsp_server():
    """Stop the RTSP server by terminating FFmpeg processes and MediaMTX"""
    global FFMPEG_PROCESSES, MEDIAMTX_PROCESS
    
    # Stop FFmpeg processes
    if FFMPEG_PROCESSES:
        print("Stopping RTSP streaming processes...")
        for process in FFMPEG_PROCESSES:
            try:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
            except:
                pass  # Process might already be gone
        
        FFMPEG_PROCESSES = []
        print("All RTSP streaming processes stopped.")
    
    # Don't stop MediaMTX automatically - it might be used by other services
    # If you want to stop it, uncomment below:
    """
    if MEDIAMTX_PROCESS and MEDIAMTX_PROCESS.poll() is None:
        print("Stopping MediaMTX RTSP server...")
        MEDIAMTX_PROCESS.terminate()
        try:
            MEDIAMTX_PROCESS.wait(timeout=5)
        except subprocess.TimeoutExpired:
            MEDIAMTX_PROCESS.kill()
        MEDIAMTX_PROCESS = None
        print("MediaMTX RTSP server stopped.")
    """

# --- Test Runner Functions ---
def run_test_in_background(mode: str, duration: int, camera_setup: str, streams: str):
    """Run a specific test scenario in the background"""
    global ACTIVE_TEST, TEST_RESULTS
    
    # Setup test environment
    test_id = f"{mode}_{int(time.time())}"
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    ACTIVE_TEST = {
        "id": test_id,
        "mode": mode,
        "camera_setup": camera_setup,
        "streams": streams,
        "duration": duration,
        "start_time": start_time,
        "status": "running"
    }
    
    print(f"Starting test: {mode} (ID: {test_id})")
    print(f"Camera setup: {camera_setup}, Streams: {streams}, Duration: {duration}s")
    
    # Mock test data - in a real implementation, this would handle different test types
    TEST_RESULTS[test_id] = {
        "id": test_id,
        "mode": mode,
        "start_time": start_time,
        "end_time": None,
        "duration": duration,
        "camera_setup": camera_setup,
        "streams": streams,
        "status": "running",
        "metrics": {},
        "details": []
    }
    
    # Different test types have different behaviors
    if mode == "attendance":
        run_attendance_test(test_id, duration, camera_setup, streams)
    elif mode == "recognition":
        run_recognition_test(test_id, duration, camera_setup, streams)
    elif mode == "performance":
        run_performance_test(test_id, duration, camera_setup, streams)
    else:  # standard test
        run_standard_test(test_id, duration, camera_setup, streams)
    
    # After test completes
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if test_id in TEST_RESULTS:
        TEST_RESULTS[test_id]["status"] = "completed"
        TEST_RESULTS[test_id]["end_time"] = end_time
    
    ACTIVE_TEST["status"] = "completed"
    print(f"Test {test_id} completed at {end_time}")

def run_standard_test(test_id: str, duration: int, camera_setup: str, streams: str):
    """Run a standard test to verify basic video streaming functionality"""
    test_result = TEST_RESULTS[test_id]
    
    # Simulate test execution
    time.sleep(duration)
    
    # Generate test metrics
    test_result["metrics"] = {
        "stream_status": "operational",
        "video_quality": "good",
        "frame_rate": 30,
        "resolution": "1280x720"
    }
    
    # Add some details
    test_result["details"] = [
        {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "message": "Basic video streaming test completed successfully"},
        {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "message": f"All streams ({streams}) verified"}
    ]

def run_attendance_test(test_id: str, duration: int, camera_setup: str, streams: str):
    """Run an attendance test to verify attendance marking functionality"""
    test_result = TEST_RESULTS[test_id]
    
    # In a real application, this would connect to your actual attendance marking system
    # For this example, we'll simulate the process
    attendance_records = []
    
    # Stimulate people recognized over time
    for i in range(5):
        time.sleep(duration / 5)  # Divide test into 5 phases
        
        # Add some simulated attendance records
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if i == 0:
            attendance_records.append({
                "id": "P001",
                "name": "John Smith",
                "department": "Engineering",
                "attendance_status": "Present",
                "recognition_confidence": 0.92,
                "timestamp": timestamp
            })
        elif i == 1:
            attendance_records.append({
                "id": "P002",
                "name": "Jane Doe",
                "department": "HR",
                "attendance_status": "Present",
                "recognition_confidence": 0.88,
                "timestamp": timestamp
            })
        elif i == 2:
            attendance_records.append({
                "id": "P003",
                "name": "Robert Johnson",
                "department": "Marketing",
                "attendance_status": "Present",
                "recognition_confidence": 0.75,
                "timestamp": timestamp
            })
        elif i == 3:
            # Update an existing record to show detection from another camera
            attendance_records[0]["recognition_confidence"] = 0.95
            attendance_records[0]["timestamp"] = timestamp
            attendance_records[0]["camera"] = "Camera 2"
        
        # Add details to the test results
        test_result["details"].append({
            "timestamp": timestamp,
            "message": f"Updated attendance records. Total records: {len(attendance_records)}"
        })
    
    # Generate test metrics
    test_result["metrics"] = {
        "total_recognized": len(attendance_records),
        "recognition_rate": len(attendance_records) / (3 if camera_setup == "single" else 4),
        "average_confidence": sum(record["recognition_confidence"] for record in attendance_records) / len(attendance_records),
        "dual_camera_matches": 1 if camera_setup == "dual" else 0
    }
    
    # Store the attendance records
    test_result["attendance_records"] = attendance_records

def run_recognition_test(test_id: str, duration: int, camera_setup: str, streams: str):
    """Run a recognition test to verify face recognition accuracy"""
    test_result = TEST_RESULTS[test_id]
    
    # In a real application, this would test your actual recognition system
    # For this example, we'll simulate the process
    recognition_events = []
    
    # Simulate recognition events over time
    for i in range(duration):
        if i % 10 == 0:  # Every 10 seconds
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Simulate a recognition event
            confidence = 0.7 + (i / duration) * 0.2  # Confidence improves over time
            
            event = {
                "timestamp": timestamp,
                "person_id": f"P00{(i//10)+1}",
                "confidence": confidence,
                "camera": f"Camera {(i%2)+1}" if camera_setup == "dual" else "Camera 1"
            }
            
            recognition_events.append(event)
            
            # Add details to the test results
            test_result["details"].append({
                "timestamp": timestamp,
                "message": f"Recognition event: Person {event['person_id']} detected with {confidence:.2f} confidence on {event['camera']}"
            })
        
        time.sleep(1)
    
    # Calculate metrics
    true_positives = sum(1 for e in recognition_events if e["confidence"] > 0.8)
    false_positives = len(recognition_events) - true_positives
    
    # Generate test metrics
    test_result["metrics"] = {
        "total_events": len(recognition_events),
        "true_positives": true_positives,
        "false_positives": false_positives,
        "accuracy": true_positives / len(recognition_events) if recognition_events else 0,
        "average_confidence": sum(e["confidence"] for e in recognition_events) / len(recognition_events) if recognition_events else 0
    }
    
    # Store the recognition events
    test_result["recognition_events"] = recognition_events

def run_performance_test(test_id: str, duration: int, camera_setup: str, streams: str):
    """Run a performance test to benchmark system performance"""
    test_result = TEST_RESULTS[test_id]
    
    # In a real application, this would benchmark your actual system
    # For this example, we'll simulate the process
    performance_samples = []
    
    # Simulate performance sampling over time
    for i in range(duration):
        if i % 5 == 0:  # Every 5 seconds
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Simulate performance metrics
            cpu_usage = 20 + (i / duration) * 30  # CPU usage increases over time
            memory_usage = 200 + (i / duration) * 100  # Memory usage increases over time
            processing_time = 50 - (i / duration) * 20  # Processing time improves over time
            
            sample = {
                "timestamp": timestamp,
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "processing_time": processing_time,
                "fps": 15 + (i / duration) * 10
            }
            
            performance_samples.append(sample)
            
            # Add details to the test results
            test_result["details"].append({
                "timestamp": timestamp,
                "message": f"Performance sample: CPU {cpu_usage:.1f}%, Memory {memory_usage:.1f}MB, Processing {processing_time:.1f}ms/frame"
            })
        
        time.sleep(1)
    
    # Generate test metrics
    test_result["metrics"] = {
        "average_cpu": sum(s["cpu_usage"] for s in performance_samples) / len(performance_samples),
        "average_memory": sum(s["memory_usage"] for s in performance_samples) / len(performance_samples),
        "average_processing_time": sum(s["processing_time"] for s in performance_samples) / len(performance_samples),
        "average_fps": sum(s["fps"] for s in performance_samples) / len(performance_samples),
        "peak_cpu": max(s["cpu_usage"] for s in performance_samples),
        "peak_memory": max(s["memory_usage"] for s in performance_samples)
    }
    
    # Store the performance samples
    test_result["performance_samples"] = performance_samples

# --- API Endpoints ---
@app.get("/", tags=["API Information"])
async def root():
    """Returns information about available RTSP streams and API endpoints."""
    server_ip = os.environ.get("SERVER_IP", "YOUR_SERVER_IP")
    
    streams = {}
    for idx, video_file in enumerate(VIDEO_FILES, 1):
        if str(idx) in ENABLED_STREAMS.split(",") and video_file.is_file():
            stream_name = f"video{idx}"
            stream_type = "random people" if idx <= 2 else "known people"
            streams[stream_name] = {
                "url": f"rtsp://{server_ip}:{RTSP_PORT}/{stream_name}",
                "type": stream_type
            }
    
    return {
        "message": "Webcam Server - Vision Computing Test Environment",
        "rtsp_port": RTSP_PORT,
        "streams": streams,
        "endpoints": {
            "status": "/status",
            "test": "/test/{mode}",
            "report": "/test/report",
            "config": "/config",
            "restart_rtsp": "/restart-rtsp"
        },
        "usage": "Connect to these streams using an RTSP client like VLC, ffplay, or GStreamer"
    }

@app.get("/restart-rtsp", tags=["RTSP Server Management"])
async def restart_rtsp():
    """Restart the RTSP server."""
    stop_rtsp_server()
    time.sleep(1)  # Give it time to fully stop
    start_rtsp_server()
    return {"message": "RTSP server restarted successfully"}

@app.get("/status", tags=["RTSP Server Management"])
async def server_status():
    """Get the status of the RTSP server and any active tests."""
    # Check if MediaMTX is running
    mediamtx_running = False
    try:
        result = subprocess.run(
            ["pgrep", "-f", "mediamtx"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        mediamtx_running = result.returncode == 0
    except:
        pass
    
    # Check active FFmpeg processes
    active_processes = []
    active_streams = []
    for process in FFMPEG_PROCESSES[:]:
        if process.poll() is None:  # Process is still running
            active_processes.append(process)
    
    # Determine active streams
    for idx, video_file in enumerate(VIDEO_FILES, 1):
        if str(idx) in ENABLED_STREAMS.split(",") and video_file.is_file():
            active_streams.append(f"video{idx}")
    
    # Create status response
    status_response = {
        "rtsp_server": "running" if mediamtx_running else "stopped",
        "ffmpeg_processes": len(active_processes),
        "rtsp_port": RTSP_PORT,
        "enabled_streams": ENABLED_STREAMS,
        "available_streams": active_streams,
        "active_test": ACTIVE_TEST
    }
    
    return status_response

@app.post("/test/{mode}", tags=["Testing"])
async def run_test(
    mode: str,
    test_config: TestConfig = Body(...),
    background_tasks: BackgroundTasks = None
):
    """Start a specific test scenario."""
    # Validate test mode
    valid_modes = ["standard", "attendance", "recognition", "performance"]
    if mode not in valid_modes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid test mode. Must be one of: {', '.join(valid_modes)}"
        )
    
    # Update enabled streams if needed
    global ENABLED_STREAMS
    if test_config.streams != ENABLED_STREAMS:
        ENABLED_STREAMS = test_config.streams
        # Restart RTSP server to apply new stream configuration
        stop_rtsp_server()
        time.sleep(1)
        start_rtsp_server()
    
    # Start the test in the background
    if background_tasks:
        background_tasks.add_task(
            run_test_in_background, 
            mode, 
            test_config.duration, 
            test_config.camera_setup, 
            test_config.streams
        )
    else:
        # Start in a separate thread if background_tasks not available
        thread = threading.Thread(
            target=run_test_in_background,
            args=(mode, test_config.duration, test_config.camera_setup, test_config.streams)
        )
        thread.daemon = True
        thread.start()
    
    return {
        "message": f"Started {mode} test",
        "config": {
            "duration": test_config.duration,
            "camera_setup": test_config.camera_setup,
            "streams": test_config.streams
        }
    }

@app.get("/test/report", tags=["Testing"])
async def get_test_report():
    """Get the report for the most recent test."""
    if not TEST_RESULTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No test results available"
        )
    
    # Get the most recent test result
    latest_test_id = sorted(TEST_RESULTS.keys())[-1]
    result = TEST_RESULTS[latest_test_id]
    
    return result

@app.get("/test/list", tags=["Testing"])
async def list_tests():
    """List all completed tests."""
    test_list = []
    for test_id, result in TEST_RESULTS.items():
        test_list.append({
            "id": test_id,
            "mode": result["mode"],
            "start_time": result["start_time"],
            "end_time": result["end_time"],
            "status": result["status"]
        })
    
    return {"tests": test_list}

@app.get("/config", tags=["Configuration"])
async def get_config():
    """Get the current configuration."""
    return CONFIG

@app.post("/config", tags=["Configuration"])
async def update_config(request: ConfigUpdateRequest):
    """Update a configuration value."""
    if request.key not in CONFIG:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown configuration key: {request.key}"
        )
    
    # Update the configuration
    old_value = CONFIG[request.key]
    CONFIG[request.key] = request.value
    
    # Special handling for some config values
    if request.key == "enabled_streams":
        global ENABLED_STREAMS
        ENABLED_STREAMS = request.value
    elif request.key == "rtsp_port":
        # Changing RTSP port requires restart
        return {
            "message": f"Configuration updated: {request.key} = {request.value}. RTSP server restart required.",
            "old_value": old_value,
            "new_value": request.value,
            "restart_required": True
        }
    
    return {
        "message": f"Configuration updated: {request.key} = {request.value}",
        "old_value": old_value,
        "new_value": request.value
    }

@app.get("/attendance", tags=["Attendance"])
async def get_attendance():
    """Get the current attendance records from the latest attendance test."""
    attendance_records = []
    
    # Find the most recent attendance test
    attendance_tests = [
        test_id for test_id, result in TEST_RESULTS.items()
        if result["mode"] == "attendance" and result["status"] == "completed"
    ]
    
    if attendance_tests:
        latest_test = sorted(attendance_tests)[-1]
        if "attendance_records" in TEST_RESULTS[latest_test]:
            attendance_records = TEST_RESULTS[latest_test]["attendance_records"]
    
    return {"records": attendance_records}

@app.post("/attendance/mark", tags=["Attendance"])
async def mark_attendance(person: Person):
    """Manually mark a person as present (for testing)."""
    # Find or create an attendance test
    attendance_tests = [
        test_id for test_id, result in TEST_RESULTS.items()
        if result["mode"] == "attendance"
    ]
    
    if not attendance_tests:
        # Create a new attendance test
        test_id = f"attendance_{int(time.time())}"
        TEST_RESULTS[test_id] = {
            "id": test_id,
            "mode": "attendance",
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": None,
            "duration": 3600,  # 1 hour
            "camera_setup": "dual",
            "streams": "1,2,3,4",
            "status": "running",
            "metrics": {},
            "details": [],
            "attendance_records": []
        }
        attendance_tests = [test_id]
    
    latest_test = sorted(attendance_tests)[-1]
    
    # Make sure attendance_records exists
    if "attendance_records" not in TEST_RESULTS[latest_test]:
        TEST_RESULTS[latest_test]["attendance_records"] = []
    
    # Check if person already exists
    existing_person = next(
        (p for p in TEST_RESULTS[latest_test]["attendance_records"] if p["id"] == person.id),
        None
    )
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if existing_person:
        # Update existing person
        existing_person["attendance_status"] = person.attendance_status or "Present"
        existing_person["recognition_confidence"] = person.recognition_confidence or 0.9
        existing_person["timestamp"] = timestamp
        message = f"Updated attendance for {person.name} (ID: {person.id})"
    else:
        # Add new person
        new_record = {
            "id": person.id,
            "name": person.name,
            "department": person.department,
            "attendance_status": person.attendance_status or "Present",
            "recognition_confidence": person.recognition_confidence or 0.9,
            "timestamp": timestamp
        }
        TEST_RESULTS[latest_test]["attendance_records"].append(new_record)
        message = f"Marked attendance for {person.name} (ID: {person.id})"
    
    # Add detail to test result
    TEST_RESULTS[latest_test]["details"].append({
        "timestamp": timestamp,
        "message": message
    })
    
    # Update metrics
    TEST_RESULTS[latest_test]["metrics"] = {
        "total_recognized": len(TEST_RESULTS[latest_test]["attendance_records"]),
        "last_update": timestamp
    }
    
    return {
        "message": message,
        "timestamp": timestamp,
        "attendance_status": person.attendance_status or "Present"
    }

# --- How to Run (in terminal) ---
# 1. Start MediaMTX: ./mediamtx
# 2. Run the FastAPI server: uvicorn app:app --host 0.0.0.0 --port 3000 --reload
# 3. RTSP server will start automatically on port 8554
# 4. Access streams via: rtsp://SERVER_IP:8554/videoN
# 
# Example clients:
# - VLC: vlc rtsp://SERVER_IP:8554/video1
# - FFplay: ffplay rtsp://SERVER_IP:8554/video1
# - GStreamer: gst-launch-1.0 playbin uri=rtsp://SERVER_IP:8554/video1
# --- ---