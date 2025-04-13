from pathlib import Path
from contextlib import asynccontextmanager
import os
import time
import subprocess
from fastapi import FastAPI

# --- Configuration ---
VIDEO_DIR = Path("videos")  # Directory containing the video files
VIDEO_FILES = [
    VIDEO_DIR / "video1.mp4",
    VIDEO_DIR / "video2.mp4",
    VIDEO_DIR / "video3.mp4",
    VIDEO_DIR / "video4.mp4"
]
RTSP_PORT = int(os.environ.get("RTSP_PORT", 8554))

# Global variables
FFMPEG_PROCESSES = []  # Will hold FFmpeg process instances

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start RTSP streams
    start_streams()
    yield
    # Stop streams on shutdown
    stop_streams()

app = FastAPI(lifespan=lifespan)

def start_streams():
    """Start FFmpeg processes to stream videos to RTSP"""
    global FFMPEG_PROCESSES
    
    # Create RTSP stream for each video file
    for idx, video_file in enumerate(VIDEO_FILES, 1):
        if video_file.is_file():
            stream_path = f"video{idx}"
            rtsp_url = f"rtsp://127.0.0.1:{RTSP_PORT}/{stream_path}"
            
            cmd = [
                "ffmpeg",
                "-re",                  # Read input at native frame rate
                "-stream_loop", "-1",   # Loop forever
                "-i", str(video_file),  # Input file
                "-c:v", "copy",         # Copy video codec
                "-c:a", "copy",         # Copy audio codec
                "-f", "rtsp",           # Output format: RTSP
                "-rtsp_transport", "tcp", # Use TCP for RTSP
                rtsp_url                # Output URL
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            FFMPEG_PROCESSES.append(process)
            time.sleep(0.5)  # Brief pause between starting streams

def stop_streams():
    """Stop all FFmpeg processes"""
    global FFMPEG_PROCESSES
    for process in FFMPEG_PROCESSES:
        try:
            process.terminate()
        except:
            pass
    FFMPEG_PROCESSES = []

@app.get("/")
async def root():
    """Returns information about available RTSP streams."""
    server_ip = os.environ.get("SERVER_IP", "localhost")
    streams = {}
    for idx in range(1, 5):
        stream_name = f"video{idx}"
        streams[stream_name] = f"rtsp://{server_ip}:{RTSP_PORT}/{stream_name}"
    
    return {"streams": streams}

# To run:
# 1. Make sure MediaMTX is running: ./mediamtx
# 2. Start this app: uvicorn app:app --host 0.0.0.0 --port 3000
