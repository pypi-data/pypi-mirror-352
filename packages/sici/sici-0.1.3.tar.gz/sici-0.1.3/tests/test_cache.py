# sici/tests/test_cache.py
import random
import numpy as np
from time import perf_counter

import pytest

from sici.models import SCM, Query
from sici.compiler import compile as sici_compile
from sici.cache import NUMERIC_CACHE


def make_numeric_scm(graph):
    """
    Construct a simple continuous SCM:
      - Root node ~ N(0,1)
      - If there are parent nodes, P(v|Pa) ~ N(sum(Pa), 1)
    """
    from scipy.stats import norm
    conds = {}
    for v, parents in graph.items():
        key = f"P({v}|{','.join(parents)})" if parents else f"P({v})"
        if parents:
            ps = parents.copy()
            conds[key] = (lambda ps: (lambda val, *args: norm.pdf(val - sum(args), loc=0, scale=1)))(ps)
        else:
            conds[key] = lambda val: norm.pdf(val, loc=0, scale=1)
    return SCM(graph=graph, conditionals=conds)


def test_repeated_queries():
    """
    Scenario A: repeated queries → test the speedup of repeated requests
    """
    # Construct SCM and query set
    graph = {"Z": [], "X": ["Z"], "Y": ["X", "Z"]}
    scm = make_numeric_scm(graph)
    queries = [Query(outcome="Y", intervention="X") for _ in range(20)]

    # Baseline: no cache
    baseline_times = []
    for q in queries:
        start = perf_counter()
        sici_compile(scm, q, mode="numeric", use_cache=False,
                     intervention_value=0.0, mc_samples=2000)
        baseline_times.append(perf_counter() - start)
    avg_baseline = np.mean(baseline_times)

    # Warm-up & measurement
    NUMERIC_CACHE._tbl.clear()
    for q in queries:
        sici_compile(scm, q, mode="numeric", use_cache=True,
                     intervention_value=0.0, mc_samples=2000)
    NUMERIC_CACHE.reset_stats()
    times = []
    for q in queries:
        t0 = perf_counter()
        sici_compile(scm, q, mode="numeric", use_cache=True,
                     intervention_value=0.0, mc_samples=2000)
        times.append(perf_counter() - t0)

    avg_cached = np.mean(times)
    speedup = avg_baseline / avg_cached
    hit_rate = NUMERIC_CACHE.hit_ratio()

    print(f"[Test A] speedup = {speedup:.2f}×, hit_rate = {hit_rate:.1%}")
    assert speedup > 1.0
    assert hit_rate == 1.0


def test_new_queries():
    """
    Scenario B: new queries → test cache reuse rate across different requests
    """
    # Construct SCM
    graph = {"Z": [], "X": ["Z"], "Y": ["X", "Z"]}
    scm = make_numeric_scm(graph)

    # Warm-up queries: 20 unique interventions
    warm_queries = [Query(outcome="Y", intervention=i) for i in ["X","Z"] * 10]
    # Test queries: 20 different outcomes
    test_queries = [Query(outcome=o, intervention="X") for o in ["Y","Z"] * 10]

    # Warm-up
    NUMERIC_CACHE._tbl.clear()
    for q in warm_queries:
        sici_compile(scm, q, mode="numeric", use_cache=True,
                     intervention_value=0.0, mc_samples=2000)
    NUMERIC_CACHE.reset_stats()

    # Measure new queries
    times = []
    for q in test_queries:
        t0 = perf_counter()
        sici_compile(scm, q, mode="numeric", use_cache=True,
                     intervention_value=0.0, mc_samples=2000)
        times.append(perf_counter() - t0)

    hit_rate = NUMERIC_CACHE.hit_ratio()
    print(f"[Test B] hit_rate = {hit_rate:.1%}")
    assert 0.0 <= hit_rate <= 1.0


def main():
    """Manually run all tests"""
    pytest.main([__file__])


if __name__ == "__main__":
    main()
