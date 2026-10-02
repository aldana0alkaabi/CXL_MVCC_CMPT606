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

    for i in range(number_of_transactions):
        transaction = Transaction(i)
        transaction.write(f"key_{i}")

        start_validation_time = time.perf_counter()
        is_valid = validator.validate(transaction, other_transactions)
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