import csv
import os
import matplotlib.pyplot as plt

# Read resource utilization data
resource_file = "results/processed/resource_trace.csv"

cpu_percent = []
memory_percent = []

with open(resource_file, "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        cpu_percent.append(float(row["cpu_percent"]))
        memory_percent.append(float(row["memory_percent"]))

# Create plots directory
os.makedirs("plots", exist_ok=True)

# Plot Resource Utilization
plt.figure(figsize=(8, 5))

plt.plot(cpu_percent, marker='o', label="CPU Utilization")
plt.plot(memory_percent, marker='o', label="Memory Utilization")

plt.xlabel("Sample")
plt.ylabel("Utilization (%)")
plt.title("Resource Utilization Over Time")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig("plots/resource_utilization.png", dpi=300)
plt.close()

print("Resource utilization plot saved.")
print("Output: plots/resource_utilization.png")