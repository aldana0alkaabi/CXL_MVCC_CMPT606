import time 
import statistics

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

    print("Basic Benchmark Results")
    print("-" * 40)

    for size in test_sizes:
        results = run_test(size)

        print(
            f"Transactions: {results['transaction']},"
            f"Time: {results['elapsed_time']:.6f} seconds,"
            f"Throughput: {results['throughput']:.2f} transactions/second"
            )

if __name__ == "__main__":
    main()