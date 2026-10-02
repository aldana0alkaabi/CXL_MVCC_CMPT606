import csv
import os
import matplotlib.pyplot as plt

# Read benchmark results
csv_file = "results/raw/benchmark_results.csv"

transactions = []
throughput = []
p50 = []
p90 = []
p99 = []

with open(csv_file, "r" , newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        transactions.append(int(row['transaction']))
        throughput.append(float(row['throughput']))
        p50.append(float(row['p50_latency']) * 1000)
        p90.append(float(row['p90_latency']) * 1000)
        p99.append(float(row['p99_latency']) * 1000)

os.makedirs("plots", exist_ok=True)

# Plot 1: Throughput
plt.figure()
plt.plot(transactions, throughput, marker='o')
plt.xlabel("Number of Transactions")
plt.ylabel("Throughput (transactions/second)")
plt.title("Throughput vs Number of Transactions")
plt.grid(True)
plt.tight_layout ()
plt.savefig("plots/throughput_vs_transactions.png")
plt.close()

# Plot 2: Validation Latency percentiles
plt.figure()
plt.plot(transactions, p50, marker='o', label='P50 Latency')
plt.plot(transactions, p90, marker='o', label='P90 Latency')
plt.plot(transactions, p99, marker='o', label='P99 Latency')
plt.xlabel("Number of Transactions")
plt.ylabel("Validation Latency (ms)")
plt.title("Validation Latency Percentiles")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("plots/_latency_percentiles.png")
plt.close()

print("Plots saved successfully.")
print("plots/throughput_vs_transactions.png'.")
print("plots/latency_percentiles.png'.")
