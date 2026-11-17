
# CXL-Aware MVCC Validation for Multi-Writer Cloud Databases

## Overview

This project implements and evaluates a software simulation of CXL-aware MVCC validation for multi-writer cloud databases.

The implementation includes concurrent transaction processing, conflict detection, atomic commits, logical timestamps, shared metadata management, and checkpoint recovery.

## Requirements

- Python 3.9+
- Dependencies in `requirements.txt`

## Installation

Run from the project root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Testing

Run all unit tests:

```bash
python -m pytest -q
```

The latest verified test run completed with 25 passing tests.

## Experiments

Run all four experimental suites:

```bash
python run_all_experiments.py
```

Or run them individually:

```bash
python benchmarks/run_fair_benchmark.py
python benchmarks/run_ablation_benchmark.py
python benchmarks/run_scalability_benchmark.py
python benchmarks/run_multihost_benchmark.py
```

Running benchmarks may overwrite existing CSV result files.

## Experimental Evaluation

1. Baseline vs simulated CXL performance
2. Ablation study of metadata validation reads
3. Thread scalability
4. Simulated logical multi-host configurations

## Results

Experimental outputs are located in:

- `results/fair_benchmark/`
- `results/ablation/`
- `results/scalability/`
- `results/multihost/`

Figures and plotting scripts are located in `plots/`.

## Limitations

- This project uses software simulation rather than physical CXL hardware.
- Logical hosts operate within one Python process.
- The multi-host experiment does not establish physical scale-out.
- Benchmark performance can vary between runs and machines.
- Some prepared workloads intentionally produce high contention.
- The ablation disables metadata reads during validation, not metadata writes or all conflict checks.
```

## Optional simulated metadata-access delay (revision)

`CXLSharedMemory(cxl_access_delay_us=50)` charges a **software sleep** per CXL metadata `get`, `put`, or `append` operation; default is zero. This is a configurable sensitivity parameter, **not a calibrated model of CXL latency or bandwidth**. The local baseline remains unchanged. The delay is charged outside the metadata-store lock, but transaction commit still uses a single RLock. OS sleep scheduling and Python overhead can dominate small delay values.

Run `python benchmarks/run_cxl_delay_sensitivity.py` to generate a separate CSV without overwriting the original paper results. The illustrative delay settings (0, 50, 200 microseconds) are not hardware measurements. The benchmark uses execution-start timestamps, 100 transactions, 20 keys, 4 threads, and 5 repetitions.
