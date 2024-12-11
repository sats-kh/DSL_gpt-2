import csv
import time
import psutil
from pynvml import *
import subprocess

# GPU 사용량 측정 함수
def get_gpu_usage():
    nvmlInit()
    gpu_usage = []
    for i in range(nvmlDeviceGetCount()):
        handle = nvmlDeviceGetHandleByIndex(i)
        mem_info = nvmlDeviceGetMemoryInfo(handle)
        util = nvmlDeviceGetUtilizationRates(handle)
        gpu_usage.append({
            'gpu': i,
            'memory_used_MB': mem_info.used / 1024 / 1024,
            'memory_total_MB': mem_info.total / 1024 / 1024,
            'utilization_percent': util.gpu
        })
    nvmlShutdown()
    return gpu_usage

# CPU 및 메모리 사용량 측정 함수
def get_system_usage():
    return {
        'cpu_percent': psutil.cpu_percent(interval=0.5),
        'memory_percent': psutil.virtual_memory().percent,
        'memory_used_MB': psutil.virtual_memory().used / 1024 / 1024,
        'memory_total_MB': psutil.virtual_memory().total / 1024 / 1024
    }

# 네트워크 송신 및 수신 throughput 측정 함수
def get_network_usage():
    counters = psutil.net_io_counters()
    return {
        'bytes_sent_MB': counters.bytes_sent / 1024 / 1024,
        'bytes_recv_MB': counters.bytes_recv / 1024 / 1024
    }

# 네트워크 latency 측정 함수
def get_network_latency(host="8.8.8.8"):
    try:
        # Ping 명령 실행
        result = subprocess.run(
            ["ping", "-c", "1", host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Ping 결과에서 시간 추출
        for line in result.stdout.split("\n"):
            if "time=" in line:
                latency = float(line.split("time=")[1].split(" ")[0])
                return latency
        return None  # 실패 시 None 반환
    except Exception:
        return None

# 메인 함수
def monitor_resource_usage(output_file="resource_usage.csv", ping_host="8.8.8.8"):
    # CSV 파일 초기화
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            'timestamp', 'cpu_percent', 'memory_percent',
            'memory_used_MB', 'memory_total_MB',
            'gpu_id', 'gpu_utilization_percent', 'gpu_memory_used_MB', 'gpu_memory_total_MB',
            'bytes_sent_MB', 'bytes_recv_MB', 'latency_ms'
        ])
    
    try:
        prev_net_usage = get_network_usage()
        while True:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            system_usage = get_system_usage()
            gpu_usage = get_gpu_usage()
            net_usage = get_network_usage()
            latency = get_network_latency(host=ping_host)

            # Throughput 계산
            bytes_sent = net_usage['bytes_sent_MB'] - prev_net_usage['bytes_sent_MB']
            bytes_recv = net_usage['bytes_recv_MB'] - prev_net_usage['bytes_recv_MB']
            prev_net_usage = net_usage

            # GPU별로 데이터를 기록
            with open(output_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                for gpu in gpu_usage:
                    writer.writerow([
                        timestamp, system_usage['cpu_percent'], system_usage['memory_percent'],
                        system_usage['memory_used_MB'], system_usage['memory_total_MB'],
                        gpu['gpu'], gpu['utilization_percent'], gpu['memory_used_MB'], gpu['memory_total_MB'],
                        bytes_sent, bytes_recv, latency
                    ])
            
            time.sleep(1)  # 1초마다 측정
    except KeyboardInterrupt:
        print("Monitoring stopped.")

if __name__ == '__main__':
    monitor_resource_usage()
