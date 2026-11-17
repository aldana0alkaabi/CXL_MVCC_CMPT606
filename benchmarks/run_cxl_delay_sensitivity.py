"""Isolated software-delay sensitivity study; does not emulate real CXL hardware."""
import csv
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_fair_benchmark import run_benchmark
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cxl_shared_memory import CXLSharedMemory


def main():
    output = Path("results/cxl_delay_sensitivity/delay_results.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for delay_us in (0, 50, 200):
        for repetition in range(1, 6):
            result = run_benchmark(CXLSharedMemory, 100, number_of_keys=20,
                                   max_workers=4, timestamp_mode="execution_start",
                                   memory_kwargs={"cxl_access_delay_us": delay_us})
            rows.append({"delay_us": delay_us, "repetition": repetition, **result})
    with output.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print("Wrote", output)


if __name__ == "__main__":
    main()
