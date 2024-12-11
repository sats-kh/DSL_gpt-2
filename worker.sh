for i in {0..2}; do
  echo $((i+1))
  docker run -dit --rm --network training_network \
    --name worker-$i \
    --hostname worker-$i \
    --gpus '"device='$i'"' \
    -v "$(pwd)":/workspace \
    -w /workspace \
    -e RANK=$i \
    pytorch/pytorch:latest
done

#for i in {0..3}; do
#  docker exec -it worker-$i python worker.py RANK=$((i + 1))
#done

