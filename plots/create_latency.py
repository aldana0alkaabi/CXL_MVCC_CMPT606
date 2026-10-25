
import csv
from collections import defaultdict
import matplotlib.pyplot as plt

source = "results/fair_benchmark/benchmark_results_prepared_workload.csv"
groups = defaultdict(list)

with open(source, newline="") as file:
    for row in csv.DictReader(file):
        key = (
            row["model"],
            int(row["number_of_keys"]),
            int(row["transactions"])
        )
        groups[key].append(row)

models = ["Baseline", "CXL_Simulation"]
key_counts = [10, 100, 1000]
transaction_counts = [100, 500, 1000]
metrics = [
    ("p50_latency", "p50"),
    ("p99_latency", "p99")
]

fig, axes = plt.subplots(
    2, 3, figsize=(12, 6.5), sharex=True
)

for row_index, (metric, label) in enumerate(metrics):
    for col_index, number_of_keys in enumerate(key_counts):
        ax = axes[row_index, col_index]

        for model in models:
            means = []
            for n in transaction_counts:
                records = groups[(model, number_of_keys, n)]
                values = [
                    float(record[metric]) * 1000
                    for record in records
                ]
                means.append(sum(values) / len(values))

            ax.plot(
                transaction_counts,
                means,
                marker="o",
                label=model
            )

        if row_index == 0:
            ax.set_title(f"{number_of_keys} keys")

        if col_index == 0:
            ax.set_ylabel(f"{label} latency (ms)")

        if row_index == 1:
            ax.set_xlabel("Number of transactions")

        ax.grid(alpha=0.25)

axes[0, 2].legend(fontsize=8)
fig.suptitle("Commit Latency under Prepared Workloads")
fig.tight_layout()
fig.savefig(
    "plots/latency_prepared_workload.pdf",
    bbox_inches="tight"
)
plt.close(fig)

print("Saved: plots/latency_prepared_workload.pdf")

