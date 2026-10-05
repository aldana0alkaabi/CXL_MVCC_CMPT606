import csv
import os
import matplotlib.pyplot as plt

# Read the execution trace sample
csv_file = "logs/execution_trace_sample.csv"
latencies = []

with open(csv_file, "r", newline="") as file:
    reader = csv.DictReader(file)
    
    for row in reader:
        latency = float(row['validation_latency'])
        latencies.append(latency * 1000)  # Convert to milliseconds

    if not latencies:
        raise ValueError("No latency data found in the sample.")

# Sort latencies and calculate cumulative percntages
latencies.sort()
cdf = [(i + 1) / len(latencies) * 100
       for i in range(len(latencies))]

# Save the CDF plot:
os.makedirs("plots", exist_ok=True)

plt.figure(figsize=(8, 5))
plt.plot(latencies, cdf, label="CXL MVCC (Sample)")
plt.xlabel("Validation Latency (ms)")
plt.ylabel("Cumulative Percentage (%)")
plt.title("CXL MVCC Validation Latency CDF")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("plots/latency_cdf.png", dpi=300)
plt.close()

print(f"Latency CDF saved. Sample size: {len(latencies)}")
print("Output: plots/latency_cdf.png")