#sici/examples/sici_trace/large_scale_identifibility_benckmark.py

import time
import random
from typing import Tuple, List

import networkx as nx
from sici.identity_checker import analyze_paths
from sici.utils import induced_ancestral_graph

def random_dag(n: int, p: float, seed: int = None) -> nx.DiGraph:
    rng = random.Random(seed)
    nodes = list(range(n))
    rng.shuffle(nodes)
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    for i in range(n):
        for j in range(i+1, n):
            if rng.random() < p:
                G.add_edge(nodes[i], nodes[j])
    return G

def benchmark_once(
    graph: dict,
    treatment: str,
    outcome: str
) -> Tuple[float, str]:
    """
    Returns:
      (t_sici, res_sici)
    """
    # 1) Ancestral pruning
    pruned = induced_ancestral_graph(graph, treatment, outcome)

    # --- SICI-Trace identify_paths ---
    t0 = time.perf_counter()
    res_sici = analyze_paths(pruned, outcome=outcome, intervention=treatment)
    t1 = time.perf_counter()
    t_sici = t1 - t0

    return t_sici, res_sici

def run_benchmark(n: int = 500, p: float = 0.02, reps: int = 5):
    print(f"=== Benchmark on random DAG (n={n}, p={p}) ===")
    for rep in range(1, reps+1):
        G = random_dag(n, p, seed=rep*123)
        graph = { str(v): [str(u) for u in G.predecessors(v)] for v in G.nodes }
        roots  = [str(v) for v,d in G.in_degree()  if d==0]
        leaves = [str(v) for v,d in G.out_degree() if d==0]
        if not roots or not leaves:
            continue
        x = random.choice(roots)
        y = random.choice(leaves)
        t_sici, res_sici = benchmark_once(graph, x, y)
        print(f"[rep={rep:2d}] Query do({x})→{y}  SICI-Trace: {res_sici:<12} {t_sici:.4f}s")

if __name__ == "__main__":
    run_benchmark(n=500, p=0.02, reps=5)
