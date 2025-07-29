# sici/examples/real_data_cross_query.py

import os
import random
from time import perf_counter
import numpy as np
from pgmpy.readwrite import BIFReader
from pgmpy.utils import get_example_model
from sici.models     import SCM, Query
from sici.compiler   import compile as sici_compile
from sici.metrics    import GLOBAL_METRICS
from sici.cache      import SYMBOLIC_CACHE
import sympy as sp
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
def load_bif_network(bif_path):
    """
    Load a BIF file using pgmpy and return:
      - graph: dict var → list of parent vars
      - state_names: dict var → list of possible values
    """
    reader = BIFReader(bif_path)
    model  = reader.get_model()
    graph = {var: list(model.get_parents(var)) for var in model.nodes()}
    state_names = {}
    for cpd in model.get_cpds():
        var = cpd.variable
        state_names[var] = list(cpd.state_names[var])
    return graph, state_names

def load_asia():
    """Load Asia network from pgmpy built-in example."""
    model = get_example_model('asia')
    graph = {var: list(model.get_parents(var)) for var in model.nodes()}
    state_names = {}
    for cpd in model.get_cpds():
        var = cpd.variable
        state_names[var] = list(cpd.state_names[var])
    return graph, state_names

def sici_batch_benchmark(name, graph, state_names, n_queries=10):
    scm = SCM(graph=graph, state_names=state_names)
    vars_ = list(graph.keys())

    # Sample random (X,Y) pairs
    queries = []
    while len(queries) < n_queries:
        x, y = random.choice(vars_), random.choice(vars_)
        if x != y:
            queries.append((x, y))

    # Reset cache
    SYMBOLIC_CACHE._tbl.clear()
    SYMBOLIC_CACHE.reset_stats()

    metrics = []
    total_time = 0.0

    # First run, no cache
    for x, y in queries:
        GLOBAL_METRICS.reset()
        t0 = perf_counter()
        sici_compile(scm, Query(y, x), mode="symbolic", use_cache=True)
        t1 = perf_counter()
        total_time += (t1 - t0)
        m = GLOBAL_METRICS
        metrics.append({
            "intervention": x,
            "outcome":      y,
            "reduction":    m.reduction,
            "cache_hit":    SYMBOLIC_CACHE.hit_ratio(),
            "opt_time":     m.opt_time
        })

    # Second run, all cache hits
    hit_count = 0
    for x, y in queries:
        t0 = perf_counter()
        sici_compile(scm, Query(y, x), mode="symbolic", use_cache=True)
        t1 = perf_counter()
        if SYMBOLIC_CACHE.hit_ratio() > 0:
            hit_count += 1

    avg_reduction = sum(m["reduction"] for m in metrics) / n_queries
    avg_hit       = sum(m["cache_hit"] for m in metrics) / n_queries
    avg_time      = sum(m["opt_time"]  for m in metrics) / n_queries

    print(f"\n[{name}] SICI-Cache:")
    print(f"  avg. reduction  = {avg_reduction:.2%}")
    print(f"  avg. cache hit  = {avg_hit:.2%}")
    print(f"  avg. opt time   = {avg_time:.4f} s")
    print(f"  cache hits (2nd run): {hit_count}/{n_queries}")
    return metrics, avg_time

def sympy_batch_benchmark(name, graph, state_names, n_queries=10):
    """Baseline: For each query, build new symbolic integral, no cache, no reuse."""
    scm = SCM(graph=graph, state_names=state_names)
    vars_ = list(graph.keys())

    queries = []
    while len(queries) < n_queries:
        x, y = random.choice(vars_), random.choice(vars_)
        if x != y:
            queries.append((x, y))

    total_time = 0.0
    for x, y in queries:
        # Each time, always cold start
        q = Query(y, x)
        t0 = perf_counter()
        tree = sici_compile(scm, q, mode="symbolic", use_cache=False)
        expr = tree.to_sympy()
        t1 = perf_counter()
        total_time += (t1 - t0)
    avg_time = total_time / n_queries

    print(f"[{name}] SymPy baseline:")
    print(f"  cache hit: always 0")
    print(f"  avg. compile time: {avg_time:.4f} s")
    return avg_time

if __name__ == "__main__":
    # The data lives in sici/examples/data, one level up from this script
    script_dir = os.path.dirname(__file__)
    data_dir = os.path.abspath(os.path.join(script_dir, os.pardir, "data"))

    # Asia: use built-in
    asia_graph, asia_state_names = load_asia()
    sici_metrics, sici_time = sici_batch_benchmark(
        name="Asia", graph=asia_graph, state_names=asia_state_names, n_queries=10)
    sympy_time = sympy_batch_benchmark(
        name="Asia", graph=asia_graph, state_names=asia_state_names, n_queries=10)
    print(f"[Asia] Speedup (SymPy/SICI): {sympy_time/sici_time:.2f}x\n")

    # Alarm & Hepar2: load from BIF
    for bif_file in ("alarm.bif", "hepar2.bif"):
        path = os.path.join(data_dir, bif_file)
        if not os.path.exists(path):
            print(f"Warning: {bif_file} not found in {data_dir}")
            continue
        graph, state_names = load_bif_network(path)
        sici_metrics, sici_time = sici_batch_benchmark(
            name=bif_file, graph=graph, state_names=state_names, n_queries=10)
        sympy_time = sympy_batch_benchmark(
            name=bif_file, graph=graph, state_names=state_names, n_queries=10)
        print(f"[{bif_file}] Speedup (SymPy/SICI): {sympy_time/sici_time:.2f}x\n")
