"""Plots revised results with standard-error error bars across five repetitions."""
import csv, math, statistics
from collections import defaultdict
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parents[1]
source=root/'results/revised_benchmark/execution_start_results.csv'
groups=defaultdict(list)
with source.open(newline='') as f:
    for row in csv.DictReader(f):
        groups[(row['model'],int(row['number_of_keys']),int(row['transactions']))].append(row)
for metric, ylabel, scale in [('throughput','Successful commits / second',1),('abort_rate','Abort rate (%)',1),('p99_latency','P99 attempt latency (ms)',1000)]:
    fig, axes=plt.subplots(1,3,figsize=(12,3.7),sharey=False)
    for ax,keys in zip(axes,(10,100,1000)):
        for model in ('Baseline','CXL_Simulation'):
            xs=[100,500,1000]; means=[]; ses=[]
            for n in xs:
                vals=[float(r[metric])*scale for r in groups[(model,keys,n)]]
                means.append(statistics.mean(vals))
                ses.append(statistics.stdev(vals)/math.sqrt(len(vals)))
            ax.errorbar(xs,means,yerr=ses,marker='o',capsize=3,label=model)
        ax.set_title(f'{keys} keys');ax.set_xlabel('Transactions');ax.grid(alpha=.2)
    axes[0].set_ylabel(ylabel);axes[-1].legend(fontsize=8)
    fig.suptitle('Execution-start timestamps — mean ± SE (5 repetitions)')
    fig.tight_layout()
    output=root/f'plots/revised_{metric}.pdf'
    fig.savefig(output,bbox_inches='tight');plt.close(fig)
    print('Saved',output)
