#!/bin/bash

docker kill $(docker ps -aq)


SCRIPT_NAME="monitor_containers.py"

# Check if the Python script is running
if pgrep -f "$SCRIPT_NAME" > /dev/null; then
    echo "Terminating $SCRIPT_NAME..."
    pkill -f "$SCRIPT_NAME"
    echo "$SCRIPT_NAME terminated."
else
    echo "$SCRIPT_NAME is not running."
fi
