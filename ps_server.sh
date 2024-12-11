#/bin/bash
docker run -dit --rm --network training_network \
  --name param-server \
  --hostname param-server \
  -v "$(pwd)":/workspace \
  -w /workspace \
  -e RANK=0 \
  pytorch/pytorch:latest

#docker exec -it param-server python param_server.py
