import csv
import os
from functools import partial

from run_fair_benchmark import run_benchmark
from cxl_shared_memory import CXLSharedMemory

def main():
    test_sizes = [100, 500, 1000]
    key_counts = [10, 100, 1000]
    reptitions = 5

    models = {
        "Full_Metadata": partial(
            CXLSharedMemory,
            enable_metadata_validation=True
        ),

        "Without_Metadata_Validation": partial(
            CXLSharedMemory,
            enable_metadata_validation=False
        ),
    }

    all_results = []
    for size in test_sizes:
        for keys in key_counts:
            for repetition in range(1, reptitions + 1):
                for model_name, factory in models.items():
                    result = run_benchmark(factory, size, keys)
                    result["model"] = model_name
                    result["repetition"] = repetition
                    result["number_of_keys"] = keys
                    all_results.append(result)

                    print(
                        f"{model_name} | "
                        f"Transaction: {size} | "
                        f"Keys: {keys} | "
                        f"Run: {repetition} | "
                        f"Throughput: {result['throughput']:.2f} tx/s | "
                        f"Abort: {result['abort_rate']:.2f}%"
                    )

    output_dir = "results/ablation"
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(
        output_dir, "ablation_results.csv"
    )

    with open(output_file, "w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(all_results[0].keys())
        )
        writer.writeheader()
        writer.writerows(all_results)

    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()

