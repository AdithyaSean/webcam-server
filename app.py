from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import os
import asyncio

# --- Configuration ---
VIDEO_DIR = Path("videos")  # Directory containing the video files
VIDEO_FILES = {
    f"video{idx}": VIDEO_DIR / f"video{idx}.mp4" 
    for idx in range(1, 5)
}

app = FastAPI()

async def generate_video_stream(video_path):
    """Generate a continuous video stream by looping the file"""
    while True:
        with open(video_path, "rb") as video_file:
            while chunk := video_file.read(1024 * 1024):  # Read 1MB chunks
                yield chunk
                await asyncio.sleep(0.01)  # Small delay to control streaming rate

@app.get("/{video_name}")
async def stream_video(video_name: str):
    """Stream a video file in a continuous loop"""
    if video_name not in VIDEO_FILES:
        raise HTTPException(status_code=404, detail=f"Video {video_name} not found")
    
    video_path = VIDEO_FILES[video_name]
    if not video_path.is_file():
        raise HTTPException(status_code=404, detail=f"Video file {video_name} does not exist")
    
    return StreamingResponse(
        generate_video_stream(video_path),
        media_type="video/mp4"
    )

@app.get("/videos")
async def list_videos():
    """Returns a JSON list of available videos"""
    available_videos = {}
    for name, path in VIDEO_FILES.items():
        if path.is_file():
            server_host = os.environ.get("SERVER_IP", "localhost:3000")
            available_videos[name] = f"http://{server_host}/{name}"
    
    return {"videos": available_videos}

# To run:
# uvicorn app:app --host 0.0.0.0 --port 3000
