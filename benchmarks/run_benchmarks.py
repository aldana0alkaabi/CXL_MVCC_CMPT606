import time 
import statistics
import csv
import os

def run_test(number_of_transactions):
    start_time = time.perf_counter()

    for i in range(number_of_transactions):
        transaction_id = i

    elapsed_time = time.perf_counter() - start_time

    throughput = number_of_transactions / elapsed_time

    return {
        "transaction": number_of_transactions,
        "elapsed_time": elapsed_time,
        "throughput": throughput
    }

def main():
    test_sizes = [1000, 5000, 10000]

    output_dir = "results/raw"
    os.makedirs(output_dir, exist_ok=True)

    csv_file = os.path.join(output_dir, "benchmark_results.csv")

    print("Basic Benchmark Results")
    print("-" * 40)

    with open(csv_file, mode='w', newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["transaction", "elapsed_time", "throughput"]
        )
        writer.writeheader()

        for size in test_sizes:
            results = run_test(size)
            writer.writerow(results)

        print(
            f"Transactions: {results['transaction']},"
            f"Time: {results['elapsed_time']:.6f} seconds,"
            f"Throughput: {results['throughput']:.2f} transactions/second"
            )

if __name__ == "__main__":
    main()