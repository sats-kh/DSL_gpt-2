#!/bin/bash

# Monitoring
python3 monitor_containers.py &

# Check if param-server is running
if ! docker ps --format "{{.Names}}" | grep -q "param-server"; then
  echo "Error: param-server container not running!"
  exit 1
fi

# Execute param-server script
echo "Starting param-server..."
docker exec -dit param-server python3 /workspace/param_server.py || {
  echo "Failed to start param-server.py"
  exit 1
}

sleep 20
# Define the number of workers
WORKER_COUNT=3

# Execute worker scripts
for ((i=0; i<$WORKER_COUNT; i++)); do
  CONTAINER_NAME="worker-$i"
  echo $CONTAINER_NAME
  # Check if worker container exists and is running
  if ! docker ps --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
    echo "Error: $CONTAINER_NAME container not running!"
    exit 1
  fi

  echo "Executing $CONTAINER_NAME..."
  docker exec -dit "$CONTAINER_NAME" python3 /workspace/worker.py || {
    echo "Failed to start worker-$i.py"
    exit 1
  }
done

echo "All workers executed successfully!"
