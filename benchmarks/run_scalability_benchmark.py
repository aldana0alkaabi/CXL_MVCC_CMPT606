
import csv
import os
from run_fair_benchmark import run_benchmark
from cxl_shared_memory import CXLSharedMemory

def main():
    thread_counts = [1, 2, 4, 8, 16]
    repetitions = 5
    results = []

    for threads in thread_counts:
        for run in range(1, repetitions + 1):
            result = run_benchmark(
                CXLSharedMemory,
                number_of_transactions=500,
                number_of_keys=100,
                max_workers=threads
            )

            result["threads"] = threads
            result["repetition"] = run
            results.append(result)

            print(
                f"Threads: {threads} | Run: {run} | "
                f"Throughput: {result['throughput']:.2f} tx/s | "
                f"Abort: {result['abort_rate']:.2f}%"
            )

    os.makedirs("results/scalability", exist_ok=True)

    output = "results/scalability/scalability_results.csv"

    with open(output, "w", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to {output}")

if __name__ == "__main__":
    main()
