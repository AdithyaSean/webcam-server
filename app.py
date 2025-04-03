from pathlib import Path
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse

# --- Configuration ---
CHUNK_SIZE = 1024 * 1024  # 1MB chunk size for reading
VIDEO_DIR = Path("videos") # Directory containing the video files
VIDEO_FILE_1 = VIDEO_DIR / "video1.mp4"
VIDEO_FILE_2 = VIDEO_DIR / "video2.mp4"
VIDEO_FILE_3 = VIDEO_DIR / "video3.mp4"
VIDEO_FILE_4 = VIDEO_DIR / "video4.mp4"
# --- ---

# --- Lifespan Events ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup events
    if not VIDEO_DIR.is_dir():
        print(f"Warning: Video directory '{VIDEO_DIR}' not found. Creating it.")
        VIDEO_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Please place video files inside the '{VIDEO_DIR}' directory.")

    for video_file in [VIDEO_FILE_1, VIDEO_FILE_2, VIDEO_FILE_3, VIDEO_FILE_4]:
        if not video_file.is_file():
            print(f"Warning: Video file '{video_file}' not found in '{VIDEO_DIR}'.")
         
    yield
    # Shutdown events - can clean up resources here if needed

app = FastAPI(lifespan=lifespan)

# --- Helper Functions for Video Streaming ---
async def stream_video_in_loop(file_path: Path) -> AsyncGenerator[bytes, None]:
    """
    Stream a video file in a continuous loop.
    """
    if not file_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Video file {file_path.name} not found.")
    
    while True:  # Loop forever
        try:
            with open(file_path, mode="rb") as file:
                while True:
                    chunk = file.read(CHUNK_SIZE)
                    if not chunk:
                        break  # End of file reached, start over
                    yield chunk
        except Exception as e:
            print(f"Error streaming video file {file_path}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                              detail=f"Error streaming video: {str(e)}")

# --- API Endpoints ---
@app.get("/video1", tags=["Video Streaming"])
async def stream_video1():
    """Streams video1.mp4 in a continuous loop."""
    return StreamingResponse(
        stream_video_in_loop(VIDEO_FILE_1),
        media_type="video/mp4"
    )

@app.get("/video2", tags=["Video Streaming"])
async def stream_video2():
    """Streams video2.mp4 in a continuous loop."""
    return StreamingResponse(
        stream_video_in_loop(VIDEO_FILE_2),
        media_type="video/mp4"
    )

@app.get("/video3", tags=["Video Streaming"])
async def stream_video11():
    """Streams video3.mp4 in a continuous loop."""
    return StreamingResponse(
        stream_video_in_loop(VIDEO_FILE_3),
        media_type="video/mp4"
    )

@app.get("/video4", tags=["Video Streaming"])
async def stream_video21():
    """Streams video4.mp4 in a continuous loop."""
    return StreamingResponse(
        stream_video_in_loop(VIDEO_FILE_4),
        media_type="video/mp4"
    )

@app.get("/", tags=["API Information"])
async def root():
    """Returns information about available video endpoints."""
    return {
        "message": "Webcam Server Video Streaming API",
        "endpoints": {
            "/video1": "Streams video1.mp4 in a continuous loop",
            "/video2": "Streams video2.mp4 in a continuous loop",
            "/video3": "Streams video3.mp4 in a continuous loop",
            "/video4": "Streams video4.mp4 in a continuous loop"
        }
    }

# --- How to Run (in terminal) ---
# uvicorn app:app --host 0.0.0.0 --port 3000 --reload
# --- ---