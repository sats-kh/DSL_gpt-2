import os 
import torch
import torch.distributed as dist
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

# PyTorch 초기화
dist.init_process_group(backend="nccl", init_method="tcp://172.18.0.2:1234", world_size=4, rank=int(os.getenv("RANK")))

# 모델과 데이터 설정
model = nn.Linear(128, 2).cuda()
optimizer = optim.SGD(model.parameters(), lr=0.01)
loss_fn = nn.CrossEntropyLoss()

# 데이터 로더 (예시 데이터)
train_loader = DataLoader(torch.randn(1000, 128), batch_size=16)

model.train()
for epoch in range(100):
    for batch in train_loader:
        optimizer.zero_grad()
        output = model(batch.cuda())
        loss = loss_fn(output, torch.randint(0, 2, (batch.size(0),)).cuda())
        loss.backward()
        
        # 매개변수 동기화
        for param in model.parameters():
            dist.reduce(param.grad.data, dst=0, op=dist.ReduceOp.SUM)
            if dist.get_rank() == 0:
                param.data -= 0.01 * param.grad.data
                dist.broadcast(param.data, src=0)
