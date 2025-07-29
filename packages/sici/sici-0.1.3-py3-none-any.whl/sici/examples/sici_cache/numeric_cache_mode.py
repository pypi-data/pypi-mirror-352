#!/usr/bin/env python3
# sici/examples/sici_cache/numeric_cache_mode.py

import os
import random
import time
import numpy as np
from time import perf_counter
from pgmpy.utils import get_example_model
from pgmpy.readwrite import BIFReader

from sici.models   import SCM, Query
from sici.compiler import compile as sici_compile
from sici.cache    import NUMERIC_CACHE

SEED = 42
random.seed(SEED)
np.random.seed(SEED)


def load_discrete_network(name):
    if name == "asia":
        model = get_example_model("asia")
    else:
        here     = os.path.dirname(__file__)
        data_dir = os.path.abspath(os.path.join(here, os.pardir, "data"))
        path     = os.path.join(data_dir, f"{name}.bif")
        reader   = BIFReader(path)
        model    = reader.get_model()
    graph = {v: list(model.get_parents(v)) for v in model.nodes()}
    cpds  = {cpd.variable: cpd for cpd in model.get_cpds()}
    return graph, cpds


def make_numeric_scm(graph, cpds):
    """
    Convert pgmpy discrete CPDs to a dictionary mapping for SCM:
      - key: (value, *parent_values)
      - value: probability
    """
    conds = {}
    state_names = {}
    for var, cpd in cpds.items():
        parents       = list(cpd.get_evidence())
        var_states    = list(cpd.state_names[var])
        parent_states = [ list(cpd.state_names[p]) for p in parents ]
        values        = cpd.get_values()
        # reshape so axis0=var, axis1..=parents
        dims = [len(var_states)] + [len(ps) for ps in parent_states]
        table = values.reshape(dims, order="C")

        label = f"P({var}|{','.join(parents)})" if parents else f"P({var})"
        mapping = {}
        if parents:
            for idxs in np.ndindex(*dims):
                vi = idxs[0]
                pi = idxs[1:]
                state_val   = var_states[vi]
                parent_vals = tuple(parent_states[i][pi[i]] for i in range(len(parents)))
                mapping[(state_val, *parent_vals)] = float(table[idxs])
        else:
            for i, sv in enumerate(var_states):
                mapping[sv] = float(table[i])
        conds[label] = mapping
        state_names[var] = var_states

    return SCM(graph=graph, conditionals=conds, state_names=state_names)


def numeric_cache_test(name: str, n_queries: int = 20, mc_samples: int = 2000):
    print(f"\n→ Numeric-mode cache test on {name}")

    # 1) Load network and construct SCM
    graph, cpds = load_discrete_network(name)
    scm = make_numeric_scm(graph, cpds)

    # Randomly select a batch of (x, y) pairs
    vars_ = list(graph.keys())
    pairs = random.sample(
        [(x, y) for x in vars_ for y in vars_ if x != y],
        k=n_queries
    )

    # 2) Baseline (no cache)
    NUMERIC_CACHE._tbl.clear()
    times_no = []
    for x, y in pairs:
        t0 = perf_counter()
        sici_compile(
            scm,
            Query(outcome=y, intervention=x),
            mode="numeric",
            use_cache=False,
            intervention_value=0.0,
            mc_samples=mc_samples
        )
        times_no.append(perf_counter() - t0)
    avg_no = sum(times_no) / len(times_no)
    print(f"   baseline (no cache) avg. time = {avg_no:.4f} s")

    # 3) Warm-up (populate cache with all future query keys)
    NUMERIC_CACHE._tbl.clear()
    for x, y in pairs:
        sici_compile(
            scm,
            Query(outcome=y, intervention=x),
            mode="numeric",
            use_cache=True,
            intervention_value=0.0,
            mc_samples=mc_samples
        )
    print(f"   [debug] cache size after warm-up = {len(NUMERIC_CACHE._tbl)} (should be {n_queries})")

    # 4) Measure performance with cache hits
    NUMERIC_CACHE.reset_stats()
    times_yes = []
    for x, y in pairs:
        t0 = perf_counter()
        sici_compile(
            scm,
            Query(outcome=y, intervention=x),
            mode="numeric",
            use_cache=True,
            intervention_value=0.0,
            mc_samples=mc_samples
        )
        times_yes.append(perf_counter() - t0)
    avg_yes  = sum(times_yes) / len(times_yes)
    speedup  = avg_no / avg_yes if avg_yes > 0 else float("inf")
    hit_rate = NUMERIC_CACHE.hit_ratio()  # after reset_stats(), this is the hit rate during measurement phase

    print(f"   cached   avg. time = {avg_yes:.4f} s")
    print(f"   speedup       = {speedup:.2f}×")
    print(f"   cache hit     = {hit_rate:.1%}")


if __name__ == "__main__":
    for net in ("asia", "alarm", "hepar2"):
        numeric_cache_test(net, n_queries=20, mc_samples=2000)
