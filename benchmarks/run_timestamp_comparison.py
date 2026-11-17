"""Compare prepared snapshots against worker-start timestamps without overwriting original results."""
import csv
import os
from run_fair_benchmark import run_benchmark, BaselineSharedMemory
from cxl_shared_memory import CXLSharedMemory

def main():
    rows = []
    for mode in ("prepared", "execution_start"):
        for name, cls in (("Baseline", BaselineSharedMemory), ("CXL_Simulation", CXLSharedMemory)):
            for threads in (1, 4, 10):
                for repeat in range(1, 6):
                    result = run_benchmark(cls, 500, 100, max_workers=threads, timestamp_mode=mode)
                    rows.append({"model": name, "threads": threads, "repetition": repeat, **result})
    os.makedirs("results/timestamp_comparison", exist_ok=True)
    path = "results/timestamp_comparison/timestamp_comparison.csv"
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} rows to {path}")

if __name__ == "__main__":
    main()
