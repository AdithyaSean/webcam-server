#!/bin/bash

# Setup script for webcam-server

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    
# Change to the script directory to ensure proper paths
cd "$SCRIPT_DIR"

# Virtual environment directory
VENV_DIR=".venv"

# Create directories if they don't exist
echo "Creating required directories..."
mkdir -p templates
mkdir -p videos

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv $VENV_DIR
    
    # Activate virtual environment and install requirements
    source "$VENV_DIR/bin/activate"
    echo "Installing requirements..."
    pip install -r requirements.txt
else
    # Just activate the virtual environment for potential updates
    source "$VENV_DIR/bin/activate"
    echo "Updating requirements..."
    pip install -r requirements.txt
fi

# Create a sample index.html if it doesn't exist
if [ ! -f "templates/index.html" ]; then
    echo "Creating sample index.html template..."
    cat > templates/index.html << 'TEMPLATE'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Webcam Server</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        select, input {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #45a049;
        }
        .camera-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .camera-grid div {
            text-align: center;
        }
        .camera-grid img, .camera-grid video {
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Webcam Server</h1>
        
        <form method="post" action="/">
            <div class="form-group">
                <label for="source">Select Source:</label>
                <select id="source" name="source">
                    <option value="webcam">Webcam</option>
                    <option value="video">Video File</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="num_streams">Number of Streams (for webcam):</label>
                <input type="number" id="num_streams" name="num_streams" min="1" max="4" value="1">
            </div>
            
            <button type="submit">Start Streaming</button>
        </form>
        
        {% if video_content %}
        <div class="stream-container">
            {{ video_content|safe }}
        </div>
        {% endif %}
    </div>
</body>
</html>
TEMPLATE
fi

# Make webcam-server.sh executable
chmod +x "$SCRIPT_DIR/webcam-server.sh"

# Add as an app to .bashrc if not already present
if ! grep -q "webcam-server()" ~/.bashrc; then
    echo "Adding webcam-server function to .bashrc..."
    echo "webcam-server() {" >> ~/.bashrc
    echo "    $SCRIPT_DIR/webcam-server.sh \"\$@\"" >> ~/.bashrc
    echo "}" >> ~/.bashrc
    source ~/.bashrc
    echo "Function added. Please restart your terminal or run 'source ~/.bashrc' to use it."
else
    echo "Function already exists in .bashrc."
fi
if ! grep -q "alias webcam-server" ~/.bashrc; then
    echo "Adding alias to .bashrc..."
    echo "alias webcam-server='$SCRIPT_DIR/webcam-server.sh'" >> ~/.bashrc
    echo "Alias added. Please restart your terminal or run 'source ~/.bashrc' to use it."
else
    echo "Alias already exists in .bashrc."
fi

echo "Setup completed successfully!"
echo "Run 'webcam-server start' to start the server."
