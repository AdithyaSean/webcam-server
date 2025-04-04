#!/bin/bash

# Script to manage the webcam-server application

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Application name
APP_NAME="webcam-server"

# Default port for FastAPI (REST API)
DEFAULT_PORT=3000

# Default RTSP port
DEFAULT_RTSP_PORT=8554

# Default test mode
DEFAULT_TEST_MODE="standard"

# Default streams to enable
DEFAULT_STREAMS="1,2,3,4"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Usage function
usage() {
    echo -e "${BLUE}${APP_NAME}${NC} - Vision Computing Test Server"
    echo
    echo -e "${YELLOW}USAGE:${NC}"
    echo "  $APP_NAME COMMAND [OPTIONS]"
    echo
    echo -e "${YELLOW}COMMANDS:${NC}"
    echo "  start         Start the webcam server"
    echo "  stop          Stop the webcam server"
    echo "  restart       Restart the webcam server"
    echo "  status        Check server status"
    echo "  test          Run a specific test scenario (see test options below)"
    echo "  stream        Stream a specific video"
    echo "  list          List available videos and test scenarios"
    echo "  log           View server logs"
    echo "  config        View or edit configuration"
    echo
    echo -e "${YELLOW}GENERAL OPTIONS:${NC}"
    echo "  -p <port>       Specify the REST API port number (default: $DEFAULT_PORT)"
    echo "  -r <rtsp_port>  Specify the RTSP port number (default: $DEFAULT_RTSP_PORT)"
    echo "  -s <streams>    Enable specific video streams (comma-separated, e.g., 1,3) (default: $DEFAULT_STREAMS)"
    echo "  -h              Show this help message"
    echo
    echo -e "${YELLOW}TEST OPTIONS:${NC}"
    echo "  -m <mode>       Test mode: standard, attendance, recognition, performance (default: $DEFAULT_TEST_MODE)"
    echo "  -d <duration>   Test duration in seconds (for performance tests)"
    echo "  -c <cameras>    Specify camera setup: single, dual (default: dual)"
    echo "  -g              Generate test report"
    echo
    echo -e "${YELLOW}EXAMPLES:${NC}"
    echo "  $APP_NAME start"
    echo "  $APP_NAME start -p 8080 -r 5554 -s 1,2"
    echo "  $APP_NAME test -m attendance -c dual -s 3,4"
    echo "  $APP_NAME stream -s 3 -p 8080"
    echo "  $APP_NAME log"
    echo
    echo -e "${YELLOW}NOTES:${NC}"
    echo "  - Videos 1,2: Random people walking"
    echo "  - Videos 3,4: Known people for attendance testing"
    exit 1
}

# Function to start the server
start() {
    local port=$DEFAULT_PORT
    local rtsp_port=$DEFAULT_RTSP_PORT
    local streams=$DEFAULT_STREAMS
    
    # Parse options
    while getopts "p:r:s:h" opt; do
        case $opt in
            p)  port="$OPTARG" ;;
            r)  rtsp_port="$OPTARG" ;;
            s)  streams="$OPTARG" ;;
            h)  usage ;;
            \?) echo -e "${RED}Invalid option: -$OPTARG${NC}" >&2; usage ;;
        esac
    done
    shift $((OPTIND-1))
    
    # Check if the virtual environment is set up
    if [ ! -d "$SCRIPT_DIR/.venv" ]; then
        echo -e "${RED}Error: Virtual environment not found. Please run setup.sh first.${NC}"
        exit 1
    fi
    
    # Activate the virtual environment
    source "$SCRIPT_DIR/.venv/bin/activate"
    
    # Check if the server is already running
    if is_running; then
        echo -e "${YELLOW}Server is already running.${NC}"
        exit 0
    fi
    
    # Change to the script directory before starting server
    cd "$SCRIPT_DIR"
    
    # Set environment variables for the app
    export RTSP_PORT="$rtsp_port"
    export ENABLED_STREAMS="$streams"
    
    # Start the server in the background
    echo -e "${GREEN}Starting REST API server on port $port...${NC}"
    echo -e "${GREEN}RTSP streaming will be available on port $rtsp_port...${NC}"
    echo -e "${GREEN}Enabled streams: $streams${NC}"
    
    uvicorn app:app --host 0.0.0.0 --port "$port" --reload &
    
    # Store the process ID
    echo $! > "$SCRIPT_DIR/$APP_NAME.pid"
    
    echo -e "${GREEN}Server started in the background.${NC}"
    echo -e "Use the following command to check status: ${BLUE}$APP_NAME status${NC}"
    echo ""
    echo -e "Access the REST API at: ${BLUE}http://SERVER_IP:$port${NC}"
    echo -e "Access RTSP streams at: ${BLUE}rtsp://SERVER_IP:$rtsp_port/videoN${NC} (where N is in: $streams)"
}

# Function to stop the server
stop() {
    if ! is_running; then
        echo -e "${YELLOW}Server is not running.${NC}"
        exit 0
    fi
    
    # Get the process ID
    local pid=$(get_pid)
    
    # Stop the server
    echo -e "${YELLOW}Stopping server (PID: $pid)...${NC}"
    kill "$pid"
    wait "$pid" 2>/dev/null # Wait for the process to terminate, discard errors
    
    # Try to kill any hanging ffmpeg processes
    pkill -f "ffmpeg.*rtsp://127.0.0.1" 2>/dev/null
    
    # Remove the PID file
    rm -f "$SCRIPT_DIR/$APP_NAME.pid"
    echo -e "${GREEN}Server stopped.${NC}"
}

# Function to restart the server
restart() {
    stop
    sleep 1 # Give it a second to fully stop
    start "$@" # Pass any options to the start function
}

# Function to check the server status
status() {
    if is_running; then
        local pid=$(get_pid)
        echo -e "${GREEN}Server is running (PID: $pid).${NC}"
        
        # Get the list of enabled streams
        local streams
        if [ -f "$SCRIPT_DIR/.venv/bin/python" ]; then
            streams=$(curl -s http://localhost:$DEFAULT_PORT/status | grep -o '"available_streams":\[[^]]*\]' | cut -d'[' -f2 | tr -d ']"')
        else
            streams="Unknown (server is running but can't query API)"
        fi
        
        echo -e "REST API available at ${BLUE}http://SERVER_IP:$DEFAULT_PORT${NC}"
        echo -e "RTSP streaming available at ${BLUE}rtsp://SERVER_IP:$DEFAULT_RTSP_PORT/videoN${NC}"
        echo -e "Current active streams: ${BLUE}$streams${NC}"
        echo -e "Check API for more details: ${BLUE}http://SERVER_IP:$DEFAULT_PORT/status${NC}"
        
        # Show running ffmpeg processes
        local ffmpeg_count=$(pgrep -c ffmpeg 2>/dev/null || echo 0)
        echo -e "FFmpeg processes: ${BLUE}$ffmpeg_count running${NC}"
    else
        echo -e "${YELLOW}Server is not running.${NC}"
    fi
}

# Function to test various scenarios
test_scenarios() {
    local mode=$DEFAULT_TEST_MODE
    local duration=60
    local camera_setup="dual"
    local streams=$DEFAULT_STREAMS
    local generate_report=false
    
    # Parse options
    while getopts "m:d:c:s:gh" opt; do
        case $opt in
            m)  mode="$OPTARG" ;;
            d)  duration="$OPTARG" ;;
            c)  camera_setup="$OPTARG" ;;
            s)  streams="$OPTARG" ;;
            g)  generate_report=true ;;
            h)  usage ;;
            \?) echo -e "${RED}Invalid option: -$OPTARG${NC}" >&2; usage ;;
        esac
    done
    
    # Validate mode
    case $mode in
        standard|attendance|recognition|performance)
            # Valid modes
            ;;
        *)
            echo -e "${RED}Invalid test mode: $mode${NC}"
            echo -e "Valid modes: standard, attendance, recognition, performance"
            exit 1
            ;;
    esac
    
    # Validate camera setup
    case $camera_setup in
        single|dual)
            # Valid camera setups
            ;;
        *)
            echo -e "${RED}Invalid camera setup: $camera_setup${NC}"
            echo -e "Valid camera setups: single, dual"
            exit 1
            ;;
    esac
    
    # Start server with specific options if not running
    if ! is_running; then
        start -s "$streams"
        sleep 2  # Wait for server to fully start
    fi
    
    # Set up environment for the test
    echo -e "${BLUE}Running test scenario: $mode${NC}"
    echo -e "${BLUE}Camera setup: $camera_setup${NC}"
    echo -e "${BLUE}Using streams: $streams${NC}"
    
    # Call the appropriate API endpoint based on the test mode
    local port=$DEFAULT_PORT
    local test_url="http://localhost:$port/test/$mode"
    local test_data="{\"duration\": $duration, \"camera_setup\": \"$camera_setup\", \"streams\": \"$streams\"}"
    
    echo -e "${YELLOW}Starting test...${NC}"
    curl -s -X POST -H "Content-Type: application/json" -d "$test_data" "$test_url"
    echo
    
    # If generating a report, wait for test to complete and fetch report
    if [ "$generate_report" = true ]; then
        echo -e "${YELLOW}Test running for $duration seconds. Waiting for completion...${NC}"
        sleep $duration
        sleep 5  # Additional buffer
        
        echo -e "${GREEN}Generating test report...${NC}"
        local timestamp=$(date +"%Y%m%d_%H%M%S")
        local report_file="test_report_${mode}_${timestamp}.txt"
        
        curl -s "http://localhost:$port/test/report" > "$report_file"
        echo -e "${GREEN}Test report saved to: ${BLUE}$report_file${NC}"
    else
        echo -e "${YELLOW}Test started. No report will be generated.${NC}"
        echo -e "Use ${BLUE}$APP_NAME test -g${NC} to generate a report"
    fi
}

# Function to stream a specific video
stream_specific() {
    local stream_id="1"
    local port=$DEFAULT_PORT
    
    # Parse options
    while getopts "s:p:h" opt; do
        case $opt in
            s)  stream_id="$OPTARG" ;;
            p)  port="$OPTARG" ;;
            h)  usage ;;
            \?) echo -e "${RED}Invalid option: -$OPTARG${NC}" >&2; usage ;;
        esac
    done
    
    # Validate stream ID
    if [[ ! $stream_id =~ ^[1-4]$ ]]; then
        echo -e "${RED}Invalid stream ID: $stream_id${NC}"
        echo -e "Valid stream IDs: 1, 2, 3, 4"
        exit 1
    fi
    
    # Check if server is running, if not start it
    if ! is_running; then
        start -p "$port"
        sleep 2  # Wait for server to fully start
    fi
    
    # Play the stream using ffplay if available
    if command -v ffplay &>/dev/null; then
        echo -e "${GREEN}Opening stream: video${stream_id}${NC}"
        xterm -e "ffplay -rtsp_transport tcp -i rtsp://localhost:$RTSP_PORT/video${stream_id}" &
    else
        echo -e "${YELLOW}FFplay not found. Use a media player to open:${NC}"
        echo -e "${BLUE}rtsp://localhost:$RTSP_PORT/video${stream_id}${NC}"
    fi
}

# Function to list available videos and test scenarios
list_resources() {
    echo -e "${BLUE}Available Resources${NC}"
    echo -e "${YELLOW}Videos:${NC}"
    echo -e "  1. video1.mp4 - Random people walking"
    echo -e "  2. video2.mp4 - Random people walking"
    echo -e "  3. video3.mp4 - Known people (for attendance testing)"
    echo -e "  4. video4.mp4 - Known people (for attendance testing)"
    
    echo -e "${YELLOW}Test Scenarios:${NC}"
    echo -e "  1. standard    - Basic video streaming test"
    echo -e "  2. attendance  - Test attendance marking functionality"
    echo -e "  3. recognition - Test face recognition accuracy"
    echo -e "  4. performance - Benchmark system performance"
    
    # Also list actual video files in the directory
    echo -e "${YELLOW}Actual Video Files in Directory:${NC}"
    ls -la "$SCRIPT_DIR/videos/" | grep -E '\.mp4$|\.avi$|\.mkv$'
}

# Function to view server logs
view_logs() {
    if ! is_running; then
        echo -e "${YELLOW}Server is not running.${NC}"
        exit 0
    fi
    
    local pid=$(get_pid)
    
    # Check for any log files or use journalctl if available
    if [ -f "$SCRIPT_DIR/$APP_NAME.log" ]; then
        tail -f "$SCRIPT_DIR/$APP_NAME.log"
    else
        # If no log file, try to follow the uvicorn output
        echo -e "${YELLOW}No dedicated log file found. Following process output...${NC}"
        tail -f /proc/$pid/fd/1 2>/dev/null || echo -e "${RED}Cannot access process output.${NC}"
    fi
}

# Function to view or edit configuration
config_manager() {
    local action="view"
    local key=""
    local value=""
    
    # Parse options
    while getopts "a:k:v:h" opt; do
        case $opt in
            a)  action="$OPTARG" ;;
            k)  key="$OPTARG" ;;
            v)  value="$OPTARG" ;;
            h)  usage ;;
            \?) echo -e "${RED}Invalid option: -$OPTARG${NC}" >&2; usage ;;
        esac
    done
    
    # Handle different actions
    case $action in
        view)
            echo -e "${BLUE}Current Configuration:${NC}"
            echo -e "${YELLOW}FastAPI port:${NC} $DEFAULT_PORT"
            echo -e "${YELLOW}RTSP port:${NC} $DEFAULT_RTSP_PORT"
            echo -e "${YELLOW}Default streams:${NC} $DEFAULT_STREAMS"
            echo -e "${YELLOW}Default test mode:${NC} $DEFAULT_TEST_MODE"
            
            # If server is running, also show current settings
            if is_running; then
                echo
                echo -e "${BLUE}Runtime Configuration:${NC}"
                curl -s "http://localhost:$DEFAULT_PORT/config" | python3 -m json.tool
            fi
            ;;
        edit)
            if [ -z "$key" ]; then
                echo -e "${RED}Error: Key not specified.${NC}"
                echo -e "Usage: $APP_NAME config -a edit -k <key> -v <value>"
                exit 1
            fi
            
            if [ -z "$value" ]; then
                echo -e "${RED}Error: Value not specified.${NC}"
                echo -e "Usage: $APP_NAME config -a edit -k <key> -v <value>"
                exit 1
            fi
            
            # Update config via API if server is running
            if is_running; then
                echo -e "${YELLOW}Updating configuration: $key = $value${NC}"
                curl -s -X POST -H "Content-Type: application/json" \
                     -d "{\"key\": \"$key\", \"value\": \"$value\"}" \
                     "http://localhost:$DEFAULT_PORT/config"
                echo
            else
                echo -e "${RED}Server is not running. Cannot update configuration.${NC}"
                exit 1
            fi
            ;;
        *)
            echo -e "${RED}Invalid action: $action${NC}"
            echo -e "Valid actions: view, edit"
            exit 1
            ;;
    esac
}

# Helper function to get the process ID
get_pid() {
    if [ -f "$SCRIPT_DIR/$APP_NAME.pid" ]; then
        cat "$SCRIPT_DIR/$APP_NAME.pid"
    else
        echo ""
    fi
}

# Helper function to check if the server is running
is_running() {
    local pid=$(get_pid)
    if [ -n "$pid" ] && ps -p "$pid" > /dev/null; then
        return 0 # Running
    else
        return 1 # Not running
    fi
}

# Main script logic
case "$1" in
    start)
        start "${@:2}" # Pass along arguments after the command
        ;;
    stop)
        stop
        ;;
    restart)
        restart "${@:2}" # Pass along arguments after the command
        ;;
    status)
        status
        ;;
    test)
        test_scenarios "${@:2}" # Pass along arguments after the command
        ;;
    stream)
        stream_specific "${@:2}" # Pass along arguments after the command
        ;;
    list)
        list_resources
        ;;
    log)
        view_logs
        ;;
    config)
        config_manager "${@:2}" # Pass along arguments after the command
        ;;
    *)
        usage
        ;;
esac

exit 0