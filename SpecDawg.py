import tkinter as tk
import psutil
import GPUtil
import shutil
import platform
import threading
import time
from PIL import Image, ImageTk  # Make sure pillow installed!

# Try to import pynvml for NVIDIA support
try:
    from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetTemperature, nvmlDeviceGetMemoryInfo
    nvmlInit()
    NVML_AVAILABLE = True
except:
    NVML_AVAILABLE = False

def get_system_info():
    cpu_usage = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    ram_usage = ram.percent
    total, used, free = shutil.disk_usage("/")
    storage_total = total // (2**30)
    storage_used = used // (2**30)
    storage_percent = (used / total) * 100

    gpus = GPUtil.getGPUs()
    gpu_info_list = []

    if gpus:
        for idx, gpu in enumerate(gpus):
            gpu_name = gpu.name
            gpu_load = gpu.load * 100
            gpu_temp = "N/A"
            gpu_memory_used = "N/A"
            gpu_memory_total = "N/A"

            if "NVIDIA" in gpu_name.upper() and NVML_AVAILABLE:
                try:
                    handle = nvmlDeviceGetHandleByIndex(idx)
                    gpu_temp = nvmlDeviceGetTemperature(handle, 0)
                    gpu_memory = nvmlDeviceGetMemoryInfo(handle)
                    gpu_memory_used = gpu_memory.used // (1024**2)
                    gpu_memory_total = gpu_memory.total // (1024**2)
                except:
                    pass
            elif "AMD" in gpu_name.upper():
                gpu_temp = "Use HWMonitor"
                gpu_memory_used = "Use HWMonitor"
                gpu_memory_total = "Use HWMonitor"
            elif "INTEL" in gpu_name.upper():
                gpu_temp = "N/A (Intel iGPU)"
                gpu_memory_used = "Shared Memory"
                gpu_memory_total = "Shared Memory"

            gpu_info_list.append({
                "name": gpu_name,
                "load": gpu_load,
                "temp": gpu_temp,
                "memory_used": gpu_memory_used,
                "memory_total": gpu_memory_total
            })
    else:
        gpu_info_list.append({
            "name": "No GPU Found",
            "load": 0,
            "temp": "N/A",
            "memory_used": "N/A",
            "memory_total": "N/A"
        })

    cpu_temp = 0
    try:
        if platform.system() == "Windows":
            import wmi
            w = wmi.WMI(namespace="root\\wmi")
            temperature_info = w.MSAcpi_ThermalZoneTemperature()[0]
            cpu_temp = (temperature_info.CurrentTemperature / 10) - 273.15
    except:
        pass

    return {
        "cpu_usage": cpu_usage,
        "ram_usage": ram_usage,
        "cpu_temp": cpu_temp,
        "gpu_info_list": gpu_info_list,
        "storage_total": storage_total,
        "storage_used": storage_used,
        "storage_percent": storage_percent
    }

def update_info():
    info = get_system_info()
    gpu_details = ""
    for gpu in info['gpu_info_list']:
        gpu_details += f"""
    GPU: {gpu['name']}
    GPU Load: {gpu['load']:.1f}%
    GPU Temp: {gpu['temp']}
    GPU Memory: {gpu['memory_used']} / {gpu['memory_total']}
        """

    output = f"""
    CPU Usage: {info['cpu_usage']}%
    CPU Temp: {info['cpu_temp']:.1f}°C
    RAM Usage: {info['ram_usage']}%

    {gpu_details}

    Storage Used: {info['storage_used']}GB / {info['storage_total']}GB
    Storage Usage: {info['storage_percent']:.1f}%

    ---------------------------
    Version: v1.1.0
    Created by Joseph Morrison
    License: CC BY-NC-ND 4.0
    """
    label.config(text=output)
    root.after(3000, update_info)  # Refresh every 3 seconds

# GUI setup
root = tk.Tk()
root.title("SpecDawg Monitor")
root.geometry("380x550")
root.configure(bg="black")

label = tk.Label(root, text="", font=("Consolas", 10), fg="lime", bg="black", justify="left")
label.pack(padx=10, pady=10)

# Load your SpecDawg logo
try:
    logo_image = Image.open(r"C:\Users\Morrison\OneDrive\Python Files\SpecDawgLogo.png")  # <<<<< PUT YOUR PATH HERE
    logo_image = logo_image.resize((150, 150))  # Resize if needed
    logo_photo = ImageTk.PhotoImage(logo_image)

    logo_label = tk.Label(root, image=logo_photo, bg="black")
    logo_label.pack(pady=5)
except Exception as e:
    print(f"Failed to load logo: {e}")

update_info()

root.mainloop()

