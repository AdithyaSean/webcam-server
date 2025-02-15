import cv2
from flask import Flask, Response
import sys

app = Flask(__name__)
camera = None

def init_camera():
    global camera
    try:
        camera = cv2.VideoCapture(0)  # Try to use the first available webcam
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
    return '''
    <html>
        <head>
            <title>Webcam Streams</title>
        </head>
        <body>
            <h1>Webcam Streams</h1>
            <div style="display: flex; gap: 20px;">
                <div>
                    <h2>Camera Feed 1</h2>
                    <img src="/video_feed_1" width="720" height="480" />
                </div>
                <div>
                    <h2>Camera Feed 2</h2>
                    <img src="/video_feed_2" width="720" height="480" />
                </div>
            </div>
        </body>
    </html>
    '''

@app.route('/video_feed_1')
def video_feed_1():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_2')
def video_feed_2():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    init_camera()
    try:
        # Start Flask app, accessible from any device in the network
        app.run(host='0.0.0.0', port=3000, debug=False)
    finally:
        if camera is not None:
            camera.release()
