from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
import os

# Video files configuration
VIDEO_DIR = Path("videos")
VIDEO_FILES = {
    f"video{idx}": VIDEO_DIR / f"video{idx}.mp4" 
    for idx in range(1, 5)
}

app = FastAPI()

@app.get("/{video_name}")
async def stream_video(video_name: str):
    """Stream video with a simple file response"""
    if video_name not in VIDEO_FILES:
        raise HTTPException(status_code=404, detail=f"Video {video_name} not found")
    
    video_path = VIDEO_FILES[video_name]
    if not video_path.is_file():
        raise HTTPException(status_code=404, detail=f"Video file {video_name} does not exist")
    
    return FileResponse(path=video_path, media_type="video/mp4")

# To run:
# uvicorn app:app --host 0.0.0.0 --port 3000
