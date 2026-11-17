import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'benchmarks'))
from run_fair_benchmark import BaselineSharedMemory, run_benchmark

def test_prepared_snapshots_reproduce_fixed_abort_rate():
    result = run_benchmark(BaselineSharedMemory, 50, 10, max_workers=1, timestamp_mode='prepared')
    assert result['successful_commits'] == 10
    assert result['abort_rate'] == 80.0

def test_execution_start_sequential_transactions_can_commit():
    result = run_benchmark(BaselineSharedMemory, 50, 10, max_workers=1, timestamp_mode='execution_start')
    assert result['successful_commits'] == 50
    assert result['abort_rate'] == 0.0

def test_invalid_timestamp_mode_is_rejected():
    with pytest.raises(ValueError):
        run_benchmark(BaselineSharedMemory, 5, timestamp_mode='unknown')
