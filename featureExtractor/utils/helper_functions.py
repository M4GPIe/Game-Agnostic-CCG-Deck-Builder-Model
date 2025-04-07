
import psutil
import GPUtil
import time


def is_numeric(value: str) -> bool:
    """
    Verifies if a value is numeric
    """
    try:
        int(value)  
        return True
    except ValueError:
        return False  


def print_cpu_gpu_usage():
    print('CPU ------------------------------------------------------------------------------')
    cpu_usage = psutil.cpu_percent(interval=1)
    print(f"Uso de CPU: {cpu_usage}%")

    print('GPU ------------------------------------------------------------------------------')
    gpus = GPUtil.getGPUs()
    for gpu in gpus:
        print(f"GPU {gpu.id}:")
        print(f"  Uso: {gpu.load*100:.1f}%")
        print(f"  Memoria usada: {gpu.memoryUtil*100:.1f}%")
    print('----------------------------------------------------------------------------------')

def print_current_time(initialTime):
    print(f"Passed time {time.time() - initialTime}")