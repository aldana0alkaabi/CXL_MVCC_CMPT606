import time
import csv
import os
import sys
import statistics
from concurrent.futures import ThreadPoolExecutor

sys.path.append("src")

from transaction import Transaction
from logical_clock import LogicalClock
from cxl_shared_memory import CXLSharedMemory
from validator import MVCCValidator
from threading import Lock

class BaselineSharedMemory:
    def __init__(self):
        self._lock = Lock()
        self._memory = {}
        self._committed_transactions = []

    def write(self, key, value):
        with self._lock:
            self._memory[key] = value

    def read(self, key):
        with self._lock:
            return self._memory.get(key)

    def commit_transaction(self, transaction, writes):
        with self._lock:
            
            if transaction.status != "active":
                return False
            
            if set(writes) != transaction.write_set:
                raise ValueError("Writes do not match transaction write_set")
            
            validator = MVCCValidator()

            if not validator.validate(
                transaction, self._committed_transactions
            ):
                transaction.abort()
                return False

            transaction.commit()

            for key, value in writes.items():
                self._memory[key] = value

            self._committed_transactions.append(transaction)
            return True

def create_workload(number_of_transactions, clock, number_of_keys=10):
    transactions = []

    for i in range(number_of_transactions):
        tx = Transaction(i, clock)
        tx.write(f"key_{i % number_of_keys}")
        transactions.append(tx)
    return transactions

def run_benchmark(memory_class, number_of_transactions, number_of_keys=10):
    clock = LogicalClock()
    shared_memory = memory_class()
    transactions = create_workload(number_of_transactions, clock, number_of_keys)

    def commit_worker(tx):
        start = time.perf_counter()

        success = shared_memory.commit_transaction(
        tx, {f"key_{tx.transaction_id % number_of_keys}": tx.transaction_id}
        )

        latency = time.perf_counter() - start
        return success, latency

    start_time = time.perf_counter()

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(commit_worker, transactions))

    elapsed_time = time.perf_counter() - start_time

    successful_commit = sum(1 for success, _ in results if success)
    aborted_transactios = len(results) - successful_commit

    throughput = successful_commit / elapsed_time
    abort_rate = aborted_transactios / len(results) * 100
    latencies = sorted(latency for _, latency in results)

    p50_latency = latencies[int(0.50 * (len(latencies) - 1))]
    p90_latency = latencies[int(0.90 * (len(latencies) - 1))]
    p99_latency = latencies[int(0.99 * (len(latencies) - 1))] 

    return {
        "transactions": number_of_transactions,
        "successful_commits": successful_commit,
        "aborted_transactions": aborted_transactios,
        "elapsed_time": elapsed_time,
        "throughput": throughput,
        "abort_rate": abort_rate,
        "p50_latency": p50_latency,
        "p90_latency": p90_latency,
        "p99_latency": p99_latency,
    }

def main():
    test_sizes = [100, 500, 1000]
    key_counts = [10, 100, 1000]
    repetitions = 5
    memory_models = {
        "Baseline": BaselineSharedMemory,
        "CXL_Simulation": CXLSharedMemory,
    }

    output_dir = "results/fair_benchmark"
    os.makedirs(output_dir, exist_ok=True)

    csv_file = os.path.join(output_dir, "benchmark_results.csv")
    all_results = []

    for size in test_sizes:
        for number_of_keys in key_counts:
            for model_name, memory_class in memory_models.items():
                for repetition in range(repetitions):
                    results = run_benchmark(
                        memory_class, size, number_of_keys
                    )
                    
                    results["repetition"] = repetition + 1
                    results["number_of_keys"] = number_of_keys
                    results["model"] = model_name
                    all_results.append(results)

                    print(
                        f"{model_name} | "
                        f"Transactions: {size} | "
                        f"Throughput: {results['throughput']:.2f} tx/s | "
                        f"Abort Rate: {results['abort_rate']:.2f}%"
                    )

    grouped_results = {}

    for result in all_results:
        key = (
            result["model"],
            result["transactions"],
            result["number_of_keys"]
        )

        grouped_results.setdefault(key, []).append(result["throughput"])

    for key, throughputs in grouped_results.items():
        mean_throughput = statistics.mean(throughputs)
        std_throughput = statistics.stdev(throughputs)

        print(
            f"{key} | "
            f"Mean: {mean_throughput:.2f} tx/s | "
            f"Std Dev: {std_throughput:.2f}"
        )
    
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.DictWriter(
            file, 
            fieldnames=["model"] + [
                key for key in all_results[0] if key != "model"
            ]
        )

        writer.writeheader()
        writer.writerows(all_results)

if __name__ == "__main__":
    main()
