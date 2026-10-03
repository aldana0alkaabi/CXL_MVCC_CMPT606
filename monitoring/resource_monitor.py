import csv
import os
import time
import psutil
from datetime import datetime


def record_resource_usage(output_file="results/processed/resource_trace.csv", duration=10, interval=1):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, mode="w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["timestamp", "cpu_percent", "memory_percent", "memory_used_mb"]
        )
        writer.writeheader()

        for _ in range(duration):
            writer.writerow({
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": psutil.cpu_percent(interval=None),
                "memory_percent": psutil.virtual_memory().percent,
                "memory_used_mb": round(
                    psutil.virtual_memory().used / (1024 * 1024), 2)
            })
            file.flush()
            time.sleep(interval)

if __name__ == "__main__":
    record_resource_usage()
    print("Resource trace saved to results/processed/resource_trace.csv")