"""Revised execution-start timing experiment; preserves original prepared workload CSV."""
import csv
import os
import statistics
from run_fair_benchmark import run_benchmark, BaselineSharedMemory, CXLSharedMemory


def main():
    out = 'results/revised_benchmark'
    os.makedirs(out, exist_ok=True)
    rows = []
    for n in (100, 500, 1000):
        for keys in (10, 100, 1000):
            for name, cls in (('Baseline', BaselineSharedMemory), ('CXL_Simulation', CXLSharedMemory)):
                for rep in range(1, 6):
                    result = run_benchmark(cls, n, keys, max_workers=10, timestamp_mode='execution_start')
                    rows.append({'model':name,'number_of_keys':keys,'repetition':rep, **result})
                    print(name,n,keys,rep,round(result['throughput'],1),round(result['abort_rate'],2),flush=True)
    path = os.path.join(out,'execution_start_results.csv')
    with open(path,'w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    print('Saved',path, 'rows',len(rows))

if __name__ == '__main__': main()
