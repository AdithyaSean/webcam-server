from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
import os

# --- Configuration ---
VIDEO_DIR = Path("videos")  # Directory containing the video files
VIDEO_FILES = {
    f"video{idx}": VIDEO_DIR / f"video{idx}.mp4" 
    for idx in range(1, 5)
}

app = FastAPI()

@app.get("/")
async def root():
    """Returns an HTML page with video players for all videos"""
    server_host = os.environ.get("SERVER_IP", "localhost:3000")
    
    video_links = ""
    for video_name in VIDEO_FILES.keys():
        if (VIDEO_DIR / f"{video_name}.mp4").is_file():
            video_links += f"""
            <div class="video-container">
                <h3>{video_name}</h3>
                <video width="640" height="480" controls>
                    <source src="/stream/{video_name}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
            """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Video Server</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            .video-container {{
                margin-bottom: 40px;
            }}
            h1 {{
                color: #333;
            }}
        </style>
    </head>
    <body>
        <h1>Video Server</h1>
        <p>The following videos are available for streaming:</p>
        {video_links}
        <h2>Direct URLs</h2>
        <ul>
            {"".join([f'<li><a href="/stream/{name}">{name}</a></li>' for name in VIDEO_FILES.keys() if (VIDEO_DIR / f"{name}.mp4").is_file()])}
        </ul>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/stream/{video_name}")
async def stream_video(video_name: str):
    """Stream a video file directly via HTTP"""
    if video_name not in VIDEO_FILES:
        raise HTTPException(status_code=404, detail=f"Video {video_name} not found")
    
    video_path = VIDEO_FILES[video_name]
    if not video_path.is_file():
        raise HTTPException(status_code=404, detail=f"Video file {video_name} does not exist")
    
    return FileResponse(path=video_path, media_type="video/mp4")

@app.get("/videos")
async def list_videos():
    """Returns a JSON list of available videos"""
    available_videos = {}
    for name, path in VIDEO_FILES.items():
        if path.is_file():
            server_host = os.environ.get("SERVER_IP", "localhost:3000")
            available_videos[name] = f"http://{server_host}/stream/{name}"
    
    return {"videos": available_videos}

# To run:
# uvicorn app:app --host 0.0.0.0 --port 3000
