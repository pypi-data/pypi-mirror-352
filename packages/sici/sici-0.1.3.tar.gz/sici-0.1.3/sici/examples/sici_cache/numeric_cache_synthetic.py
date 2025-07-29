# sici/examples/sici_cache/numeric_cache_synthetic.py

import random
import numpy as np
from time import perf_counter
from scipy.stats import norm

from sici.models    import SCM, Query
from sici.compiler  import compile
from sici.cache     import NUMERIC_CACHE
from sici.metrics   import GLOBAL_METRICS

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

def make_numeric_scm(graph, n_states=3):
    conds = {}
    for v, parents in graph.items():
        key = f"P({v}|{','.join(parents)})" if parents else f"P({v})"
        def make_cpd_fn(n_states):
            def fn(x, *pvals):
                # uniform over n_states
                return 1.0 / n_states
            return fn
        conds[key] = make_cpd_fn(n_states)

    scm = SCM(
        graph=graph,
        conditionals=conds,  
        state_names={v: list(range(n_states)) for v in graph}
    )
    return scm

def numeric_cache_benefit(graph, n_queries=30, mc_samples=2000):
    scm = make_numeric_scm(graph)
    vars_ = list(graph.keys())
    pairs = random.sample(
        [(x, y) for x in vars_ for y in vars_ if x != y],
        k=n_queries
    )

    # Warm‐up: fill the cache (all misses)
    NUMERIC_CACHE._tbl.clear()
    for x, y in pairs:
        compile(
            scm,
            Query(outcome=y, intervention=x),
            mode="numeric",
            use_cache=True,
            intervention_value=0.0,
            mc_samples=mc_samples
        )

    # Reset only the hit/miss counters (but keep entries around)
    NUMERIC_CACHE.reset_stats()

    # Second run: measure hit‐rate & timing
    times = []
    hits  = []
    for x, y in pairs:
        t0 = perf_counter()
        compile(
            scm,
            Query(outcome=y, intervention=x),
            mode="numeric",
            use_cache=True,
            intervention_value=0.0,
            mc_samples=mc_samples
        )
        times.append(perf_counter() - t0)
        hits.append(NUMERIC_CACHE.hit_ratio())

    avg_t = sum(times) / len(times)
    avg_h = sum(hits)  / len(hits)
    print(f"Nodes={len(graph):>3}  avg_time={avg_t:.4f}s  cache_hit={avg_h:.1%}")

if __name__ == "__main__":
    for nodes in (20, 40, 60, 80, 100):
        rng = np.random.default_rng(SEED)
        vars_n = [f"V{i}" for i in range(nodes)]
        graph  = {}
        for i, v in enumerate(vars_n):
            pop = vars_n[:i]
            k   = int(rng.integers(0, min(len(pop), 2) + 1))
            parents = rng.choice(pop, size=k, replace=False).tolist() if k > 0 else []
            graph[v] = parents

        numeric_cache_benefit(graph, n_queries=20, mc_samples=2000)
