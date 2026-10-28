import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Project paths
project_dir = Path(__file__).resolve().parent.parent

results_file = (
    project_dir / "results" / "multihost" /
    "multihost_results.csv"
)

output_file = Path(__file__).resolve().parent / "figure6.pdf"

# Load experimental results
df = pd.read_csv(results_file)

# Calculate mean throughput across repetitions
summary = (
    df.groupby("hosts", as_index=False)["throughput"]
    .mean()
    .sort_values("hosts")
)

# Create publication-ready figure
fig, ax = plt.subplots(figsize=(6, 3.5))

ax.plot(
    summary["hosts"],
    summary["throughput"],
    marker="o",
    color="black",
    linewidth=1.8,
    markersize=6
)

ax.set_xlabel("Number of Logical Hosts")
ax.set_ylabel("Throughput (transactions/sec)")
ax.set_xticks(summary["hosts"])
ax.grid(True, linestyle="--", alpha=0.35)

fig.tight_layout()

# Save as vector PDF
fig.savefig(output_file, format="pdf", bbox_inches="tight")
plt.close(fig)

print("Figure saved to:", output_file)
print(summary.to_string(index=False))