# sici/examples/sici_cache/mc_convergence.py

import time
import numpy as np
import random
from scipy.stats import norm

from sici.models   import SCM, Query
from sici.compiler import compile as sici_compile

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

def make_numeric_scm(graph):
    """
    Construct a simple continuous SCM:
      - Root nodes ~ N(0,1)
      - If the node has parents, P(v|Pa) ~ N(sum(Pa), 1)
    """
    conds = {}
    for v, parents in graph.items():
        if parents:
            # capture parents for lambda closure
            ps = parents.copy()
            def mk_fn(ps):
                return lambda val, *args: norm.pdf(val - sum(args), loc=0, scale=1)
            conds[f"P({v}|{','.join(ps)})"] = mk_fn(ps)
        else:
            conds[f"P({v})"] = lambda val: norm.pdf(val, loc=0, scale=1)
    return SCM(graph=graph, conditionals=conds)

def run_mc_convergence(graph, intervention, outcome,
                       x_val=0.0,
                       sample_sizes=(100, 500, 1000, 2000, 5000, 10000),
                       repeats=10):
    """
    For the given SCM and query P(outcome | do(intervention)=x_val),
    run with different mc_samples, repeat multiple times, record mean absolute error and std.
    """
    scm = make_numeric_scm(graph)
    q   = Query(outcome=outcome, intervention=intervention)
    # Ground truth: For this linear model, E[Y|do(X=x)] = x
    true_val = x_val

    results = []
    for m in sample_sizes:
        errors = []
        for _ in range(repeats):
            start = time.perf_counter()
            est = sici_compile(
                scm, q,
                mode="numeric",
                use_cache=False,
                intervention_value=x_val,
                mc_samples=m
            )
            elapsed = time.perf_counter() - start
            errors.append(abs(est - true_val))
        mean_err = float(np.mean(errors))
        std_err  = float(np.std(errors))
        results.append({
            "mc_samples": m,
            "mean_abs_error": mean_err,
            "std_error": std_err,
            "avg_time_s": elapsed / repeats
        })
    return results

def main():
    # Backdoor scenario: Z->X->Y, Z->Y
    graph = {
        "Z": [],
        "X": ["Z"],
        "Y": ["X", "Z"],
    }
    intervention = "X"
    outcome      = "Y"

    sample_sizes = [100, 500, 1000, 2000, 5000, 10000]
    repeats = 20

    print(f"{'mc_samples':>10} | {'mean_err':>10} | {'std_err':>10} | {'time(s)':>8}")
    print("-" * 50)
    results = run_mc_convergence(
        graph, intervention, outcome,
        x_val=0.0,
        sample_sizes=sample_sizes,
        repeats=repeats
    )
    for r in results:
        print(f"{r['mc_samples']:10d} | "
              f"{r['mean_abs_error']:10.4f} | "
              f"{r['std_error']:10.4f} | "
              f"{r['avg_time_s']:8.4f}")

if __name__ == "__main__":
    main()
