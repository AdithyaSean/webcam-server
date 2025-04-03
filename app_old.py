import cv2
from flask import Flask, Response, render_template_string
import sys

app = Flask(__name__)
camera = None
num_streams = 1  # Default to 1 stream if not specified

def init_camera():
    global camera
    try:
        # Initialize single camera that will be shared across streams
        camera = cv2.VideoCapture(0)  # Use default camera
        if not camera.isOpened():
            raise Exception("Could not open webcam")
    except Exception as e:
        print(f"Error initializing camera: {e}")
        sys.exit(1)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    # Generate HTML dynamically based on number of streams
    camera_divs = ''
    for i in range(1, num_streams + 1):
        camera_divs += f'''
            <div>
                <h2>Camera Feed {i}</h2>
                <img src="/video_feed_{i}" width="720" height="480" />
            </div>
        '''
    
    html = f'''
    <html>
        <head>
            <title>Webcam Streams</title>
            <style>
                .camera-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(720px, 1fr));
                    gap: 20px;
                    padding: 20px;
                }}
                .camera-feed {{
                    text-align: center;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                }}
            </style>
        </head>
        <body>
            <h1 style="text-align: center;">Webcam Streams</h1>
            <div class="camera-grid">
                {camera_divs}
            </div>
        </body>
    </html>
    '''
    return html

@app.route('/video_feed_<int:stream_id>')
def video_feed(stream_id):
    if stream_id < 1 or stream_id > num_streams:
        return "Invalid stream ID", 404
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Get number of streams from command line argument
    if len(sys.argv) > 1:
        try:
            num_streams = int(sys.argv[1])
            if num_streams < 1:
                raise ValueError("Number of streams must be at least 1")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    print(f"Initializing camera with {num_streams} stream view(s)...")
    init_camera()
    try:
        # Start Flask app, accessible from any device in the network
        app.run(host='0.0.0.0', port=3000, debug=False)
    finally:
        if camera is not None:
            camera.release()
