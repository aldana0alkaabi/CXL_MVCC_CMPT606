import subprocess
import sys

experiments = [
    "benchmarks/run_fair_benchmark.py",
    "benchmarks/run_ablation_benchmark.py",
    "benchmarks/run_scalability_benchmark.py",
    "benchmarks/run_multihost_benchmark.py",
]

for experiment in experiments:
    print(f"\nRunning {experiment}", flush=True)

    subprocess.run(
        [sys.executable, experiment],
        check=True
    )

print("\nAll experiments completed successfully.")
