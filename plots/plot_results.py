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
cxl_transactions = []
cxl_p50 = []
cxl_p90 = []
cxl_p99 = []

with open(csv_file, "r" , newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        transactions.append(int(row['transaction']))
        throughput.append(float(row['throughput']))
        p50.append(float(row['p50_latency']) * 1000)
        p90.append(float(row['p90_latency']) * 1000)
        p99.append(float(row['p99_latency']) * 1000)

os.makedirs("plots", exist_ok=True)


# Read CXL Benchmark results
cxl_file = "results/raw/benchmark_results_cxl.csv"

with open(cxl_file, "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        cxl_transactions.append(float(row['transaction']))
        cxl_p50.append(float(row['cxl_p50_latency']) * 1000)
        cxl_p90.append(float(row['cxl_p90_latency']) * 1000)
        cxl_p99.append(float(row['cxl_p99_latency']) * 1000)

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

# Plot 2: Baseline vs CXL Latency Percentiles
plt.figure()

plt.plot(transactions, p50, marker='o', label='Baseline P50')
plt.plot(transactions, p90, marker='o', label='Baseline P90')
plt.plot(transactions, p99, marker='o', label='Baseline P99')

plt.plot(cxl_transactions, cxl_p50, marker='s', linestyle='--', label='CXL P50')
plt.plot(cxl_transactions, cxl_p90, marker='s', linestyle='--', label='CXL P90')
plt.plot(cxl_transactions, cxl_p99, marker='s', linestyle='--', label='CXL P99')

plt.xlabel("Number of Transactions")
plt.ylabel("Latency (ms)")
plt.yscale("log")
plt.title("Baseline vs CXL Latency Percentiles")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("plots/_latency_percentiles.png")
plt.close()

print("Plots saved successfully.")
print("plots/throughput_vs_transactions.png'.")
print("plots/latency_percentiles.png'.")
