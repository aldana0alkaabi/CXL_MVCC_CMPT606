import time 
import statistics
import csv
import os
import sys
sys.path.append("src")
from transaction import Transaction
from validator import MVCCValidator

def run_test(number_of_transactions):
    start_time = time.perf_counter()

    validator = MVCCValidator()
    other_transactions = []
    validation_latencies = []


    for i in range(number_of_transactions):
        transaction = Transaction(i)
        transaction.write(f"key_{i}")

        start_validation_time = time.perf_counter()
        is_valid = validator.validate(transaction, other_transactions)

        validation_latency = time.perf_counter() - start_validation_time
        validation_latencies.append(validation_latency)

        if is_valid:
            transaction.commit()
        else:
            transaction.abort() 
        other_transactions.append(transaction)
   

    elapsed_time = time.perf_counter() - start_time

    throughput = number_of_transactions / elapsed_time

    return {
        "transaction": number_of_transactions,
        "elapsed_time": elapsed_time,
        "throughput": throughput,
        "p50_latency": statistics.median(validation_latencies),
        "p90_latency": statistics.quantiles(validation_latencies, n=10)[8],
        "p99_latency": statistics.quantiles(validation_latencies, n=100)[98]
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
            fieldnames=["transaction", "elapsed_time", "throughput", "p50_latency", "p90_latency", "p99_latency"]
        )
        writer.writeheader()

        for size in test_sizes:
            results = run_test(size)
            writer.writerow(results)

        print(
            f"Transactions: {results['transaction']},"
            f"Time: {results['elapsed_time']:.6f} seconds,"
            f"Throughput: {results['throughput']:.2f} transactions/second,"
            f"P50 Latency: {results['p50_latency']:.8f} seconds,"
            f"P90 Latency: {results['p90_latency']:.8f} seconds,"
            f"P99 Latency: {results['p99_latency']:.8f} seconds"
        )

if __name__ == "__main__":
    main()