
import csv
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, "src")

from cxl_shared_memory import CXLSharedMemory
from logical_clock import LogicalClock
from transaction import Transaction


def run_multihost(number_of_hosts, number_of_transactions=500,
                  number_of_keys=100, max_workers=10):

    clock = LogicalClock()
    memory = CXLSharedMemory()

    transactions = []

    for i in range(number_of_transactions):
        tx = Transaction(transaction_id=i, clock=clock)
        tx.write(f"key_{i % number_of_keys}")
        transactions.append(tx)

    def worker(tx):
        host_id = tx.transaction_id % number_of_hosts
        key = f"key_{tx.transaction_id % number_of_keys}"

        start = time.perf_counter()

        success = memory.commit_transaction(
            tx,
            {key: tx.transaction_id},
            host_id=host_id
        )

        latency = time.perf_counter() - start
        return success, latency

    start_time = time.perf_counter()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(worker, transactions))

    elapsed = time.perf_counter() - start_time

    commits = sum(1 for success, _ in results if success)
    aborts = len(results) - commits

    latencies = sorted(latency for _, latency in results)
    p99 = latencies[int(0.99 * (len(latencies) - 1))]

    return {
        "hosts": number_of_hosts,
        "transactions": number_of_transactions,
        "threads": max_workers,
        "successful_commits": commits,
        "aborted_transactions": aborts,
        "throughput": commits / elapsed,
        "abort_rate": aborts / len(results) * 100,
        "p99_latency": p99
    }


def main():
    host_counts = [1, 2, 4, 8]
    repetitions = 5
    results = []

    for hosts in host_counts:
        for run in range(1, repetitions + 1):

            result = run_multihost(hosts)
            result["repetition"] = run
            results.append(result)

            print(
                f"Hosts: {hosts} | Run: {run} | "
                f"Throughput: {result['throughput']:.2f} tx/s | "
                f"Abort: {result['abort_rate']:.2f}% | "
                f"P99: {result['p99_latency']:.6f}s"
            )

    os.makedirs("results/multihost", exist_ok=True)

    output = "results/multihost/multihost_results.csv"

    with open(output, "w", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to {output}")


if __name__ == "__main__":
    main()
