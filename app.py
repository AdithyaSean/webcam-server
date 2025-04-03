import os
import re
from pathlib import Path
from typing import Generator, Optional

from fastapi import FastAPI, Request, Response, Header, HTTPException, status
from fastapi.responses import StreamingResponse, HTMLResponse

# --- Configuration ---
CHUNK_SIZE = 1024 * 1024  # 1MB chunk size for reading
VIDEO_DIR = Path("videos") # Directory containing the video files
VIDEO_FILE_1 = VIDEO_DIR / "video1.mp4"
VIDEO_FILE_2 = VIDEO_DIR / "video2.mp4"
# --- ---

app = FastAPI()

# --- Helper Function for Range Requests ---
def parse_range_header(range_header: str | None, file_size: int) -> tuple[int, int | None]:
    """Parses the Range header and returns start and end byte positions."""
    if range_header is None:
        return 0, file_size - 1 # If no range requested, send the whole file

    match = re.match(r'bytes=(\d+)-(\d*)', range_header)
    if not match:
        raise HTTPException(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                            detail="Invalid Range header format.")

    start_byte = int(match.group(1))
    end_byte_str = match.group(2)

    if start_byte >= file_size:
        raise HTTPException(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                            detail="Range start position is beyond file size.")

    if end_byte_str:
        end_byte = int(end_byte_str)
        if end_byte < start_byte or end_byte >= file_size:
            # If end byte is invalid, often browsers just want the rest
             end_byte = file_size - 1
            # Alternatively, raise error:
            # raise HTTPException(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            #                     detail="Invalid end byte value.")
    else:
        # No end byte specified, read until the end of the file
        end_byte = file_size - 1

    return start_byte, end_byte

async def range_requests_handler(
    file_path: Path, range_header: str | None
) -> tuple[Generator[bytes, None, None], int, int, dict[str, str]]:
    """
    Handles range requests for a given file path.

    Returns:
        - A generator yielding chunks of the file.
        - The final status code (200 or 206).
        - The calculated Content-Length.
        - A dictionary of response headers.
    """
    if not file_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video file not found.")

    file_size = file_path.stat().st_size
    start_byte, end_byte = parse_range_header(range_header, file_size)

    content_length = (end_byte - start_byte) + 1
    status_code = status.HTTP_206_PARTIAL_CONTENT if range_header else status.HTTP_200_OK

    headers = {
        "Content-Length": str(content_length),
        "Accept-Ranges": "bytes",
        "Content-Range": f"bytes {start_byte}-{end_byte}/{file_size}",
         # Guess MIME type (adjust if needed for specific formats)
        "Content-Type": "video/mp4", # Hardcoding for simplicity, could use mimetypes library
        "Connection": "keep-alive",
    }

    # If it's a full request, remove Content-Range
    if status_code == status.HTTP_200_OK:
        del headers["Content-Range"]

    async def file_iterator(start: int, chunk_size: int, length_to_read: int):
        """Asynchronous generator to read file chunks."""
        bytes_read = 0
        try:
            with open(file_path, mode="rb") as file:
                file.seek(start)
                while bytes_read < length_to_read:
                    read_size = min(chunk_size, length_to_read - bytes_read)
                    chunk = file.read(read_size)
                    if not chunk:
                        break  # End of file reached unexpectedly
                    yield chunk
                    bytes_read += len(chunk)
        except Exception as e:
            print(f"Error reading file chunk: {e}")
            # Handle error appropriately, maybe stop streaming
        finally:
            # print(f"Finished streaming {bytes_read} bytes for range {start}-{start+bytes_read-1}")
            pass  # File is closed by 'with' statement

    return file_iterator(start_byte, CHUNK_SIZE, content_length), status_code, content_length, headers
# --- ---

# --- API Endpoints ---
@app.get("/video1", tags=["Video Streaming"])
async def stream_video1(request: Request, range: Optional[str] = Header(None)):
    """Streams video file 1, supporting range requests."""
    generator, status_code, content_length, headers = await range_requests_handler(VIDEO_FILE_1, range)
    return StreamingResponse(
        generator,
        status_code=status_code,
        headers=headers,
        media_type="video/mp4" # Set media_type here too for clarity
    )

@app.get("/video2", tags=["Video Streaming"])
async def stream_video2(request: Request, range: Optional[str] = Header(None)):
    """Streams video file 2, supporting range requests."""
    generator, status_code, content_length, headers = await range_requests_handler(VIDEO_FILE_2, range)
    return StreamingResponse(
        generator,
        status_code=status_code,
        headers=headers,
        media_type="video/mp4"
    )

@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
async def get_frontend():
    """Serves a simple HTML page with two video players."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FastAPI Video Streaming</title>
        <style>
            body { font-family: sans-serif; display: flex; justify-content: space-around; padding: 20px; }
            video { max-width: 45%; border: 1px solid #ccc; }
            h2 { text-align: center; width: 100%; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div>
            <h2>Video 1</h2>
            <video controls width="640">
                <source src="/video1" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
        <div>
            <h2>Video 2</h2>
            <video controls width="640">
                <source src="/video2" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# --- ---

# Optional: Add check for video directory and files on startup
@app.on_event("startup")
async def startup_event():
    if not VIDEO_DIR.is_dir():
        print(f"Warning: Video directory '{VIDEO_DIR}' not found. Creating it.")
        VIDEO_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Please place '{VIDEO_FILE_1.name}' and '{VIDEO_FILE_2.name}' inside the '{VIDEO_DIR}' directory.")

    if not VIDEO_FILE_1.is_file():
         print(f"Warning: Video file '{VIDEO_FILE_1}' not found in '{VIDEO_DIR}'. Endpoint /video1 will fail.")
    if not VIDEO_FILE_2.is_file():
         print(f"Warning: Video file '{VIDEO_FILE_2}' not found in '{VIDEO_DIR}'. Endpoint /video2 will fail.")

# --- How to Run (in terminal) ---
# uvicorn main:app --host 0.0.0.0 --port 3000 --reload
# --- ---