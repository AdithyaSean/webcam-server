from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
import cv2
import asyncio
import glob
import os
import time

# Video files configuration
VIDEO_DIR = Path("videos")

def get_available_videos():
    """Dynamically discover all video files in the videos directory"""
    video_files = {}
    if VIDEO_DIR.exists():
        # Support common video file extensions
        video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.webm', '*.flv']
        
        for extension in video_extensions:
            for video_path in VIDEO_DIR.glob(extension):
                # Use filename without extension as the key
                video_name = video_path.stem
                video_files[video_name] = video_path
    
    return video_files

# Get all available video files
VIDEO_FILES = get_available_videos()

app = FastAPI()

@app.get("/")
async def list_videos():
    """List all available video streams"""
    # Refresh the video list to catch any newly added files
    current_videos = get_available_videos()
    
    if not current_videos:
        return {"message": "No video files found in the videos directory", "videos": []}
    
    video_list = []
    for video_name, video_path in current_videos.items():
        video_info = {
            "name": video_name,
            "url": f"/{video_name}",
            "file": str(video_path),
            "exists": video_path.exists()
        }
        video_list.append(video_info)
    
    return {
        "message": f"Found {len(current_videos)} video(s)",
        "videos": video_list
    }

@app.get("/{video_name}")
async def stream_video(video_name: str):
    """Stream video continuously by looping the video file"""
    # Refresh the video list to catch any newly added files
    current_videos = get_available_videos()
    
    if video_name not in current_videos:
        available_videos = list(current_videos.keys())
        raise HTTPException(
            status_code=404, 
            detail=f"Video '{video_name}' not found. Available videos: {available_videos}"
        )
    
    video_path = current_videos[video_name]
    if not video_path.is_file():
        raise HTTPException(status_code=404, detail=f"Video file '{video_name}' does not exist")
    
    def generate_video_stream():
        """Generate continuous video stream by looping the video file"""
        while True:
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                break
                
            try:
                # Get video properties
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_delay = 1.0 / fps if fps > 0 else 1.0 / 30  # Default to 30 FPS if unknown
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break  # End of video, will loop
                    
                    # Encode frame as JPEG
                    _, buffer = cv2.imencode('.jpg', frame)
                    frame_bytes = buffer.tobytes()
                    
                    # Yield frame in MJPEG format
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    
                    # Control frame rate
                    time.sleep(frame_delay)
                    
            finally:
                cap.release()
                
            # Small delay before restarting the video
            time.sleep(0.1)
    
    return StreamingResponse(
        generate_video_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/{video_name}/download")
async def download_video(video_name: str):
    """Download video file directly (fallback for direct file access)"""
    # Refresh the video list to catch any newly added files
    current_videos = get_available_videos()
    
    if video_name not in current_videos:
        available_videos = list(current_videos.keys())
        raise HTTPException(
            status_code=404, 
            detail=f"Video '{video_name}' not found. Available videos: {available_videos}"
        )
    
    video_path = current_videos[video_name]
    if not video_path.is_file():
        raise HTTPException(status_code=404, detail=f"Video file '{video_name}' does not exist")
    
    return FileResponse(path=video_path, media_type="video/mp4")

# To run:
# uvicorn app:app --host 0.0.0.0 --port 3000
