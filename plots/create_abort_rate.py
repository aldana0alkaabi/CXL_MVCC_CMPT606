
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
        groups[key].append(float(row["abort_rate"]))

models = ["Baseline", "CXL_Simulation"]
key_counts = [10, 100, 1000]
transaction_counts = [100, 500, 1000]

fig, axes = plt.subplots(
    1, 3, figsize=(12, 3.6), sharey=True
)

for ax, number_of_keys in zip(axes, key_counts):
    for model in models:
        means = []

        for n in transaction_counts:
            values = groups[(model, number_of_keys, n)]
            means.append(sum(values) / len(values))

        ax.plot(
            transaction_counts,
            means,
            marker="o",
            label=model
        )

    ax.set_title(f"{number_of_keys} keys")
    ax.set_xlabel("Number of transactions")
    ax.set_ylim(-5, 105)
    ax.grid(alpha=0.25)

axes[0].set_ylabel("Abort rate (%)")
axes[-1].legend(fontsize=8)

fig.suptitle("Abort Rate under Prepared Workloads")
fig.tight_layout()
fig.savefig(
    "plots/abort_rate_prepared_workload.pdf",
    bbox_inches="tight"
)
plt.close(fig)

print("Saved: plots/abort_rate_prepared_workload.pdf")

