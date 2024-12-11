import torch
import torch.distributed as dist
import torch.nn as nn

try:
    # 초기화 시작 메시지
    print("Initializing Parameter Server...")
    dist.init_process_group(
        backend="nccl", init_method="tcp://127.0.0.1:1234", world_size=4, rank=0
    )

    # 모델 정의
    model = nn.Linear(128, 2).cuda()

    # 파라미터 초기화 및 동기화
    print("Broadcasting Parameters...")
    for param in model.parameters():
        dist.broadcast(param.data, src=0)

    print("Parameter Server Ready...")

except Exception as e:
    print(f"Error: {e}")
