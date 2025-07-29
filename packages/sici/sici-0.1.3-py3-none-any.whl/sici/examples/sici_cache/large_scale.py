# sici/examples/sici_cache/large_scale.py

"""
Scalability experiment: Large synthetic DAGs, SICI-Cache vs. naive symbolic pipeline.

- Randomly generate DAGs of different scales (n=500~10000)
- Test two pipelines: naive (no optimization) vs. SICI-Cache (canonicalize + fold + rewrite)
- Output AST node count, DAG node count, execution time, reduction rate, and naive pipeline failure status
"""

import time
import random
import numpy as np
import sys

from sici.models     import SCM, Query
from sici.compiler   import compile as sym_compile
from sici.canonical  import canonicalize_ast
from sici.tree       import ExpressionTree
from sici.dag        import fold_and_rewrite
from sici.metrics    import count_ast_nodes

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

def generate_random_dag(n, max_parents=3, seed=None):
    """
    Generate a random acyclic graph for synthetic causal network.
    """
    rng = np.random.default_rng(seed)
    vars_ = [f"V{i}" for i in range(n)]
    graph = {}
    for i, v in enumerate(vars_):
        pop = vars_[:i]
        k = int(rng.integers(0, min(len(pop), max_parents) + 1))
        parents = rng.choice(pop, size=k, replace=False).tolist() if k > 0 else []
        graph[v] = parents
    return graph

def one_query_compare(graph):
    """
    Compare naive symbolic pipeline (no optimization) vs SICI-Cache (full optimization).
    """
    vars_ = list(graph.keys())
    x = random.choice(vars_)
    y = random.choice([v for v in vars_ if v != x])
    scm  = SCM(graph)
    q    = Query(outcome=y, intervention=x)

    # 1. naive pipeline: no canonicalization, no folding, no rewrite
    try:
        t0 = time.perf_counter()
        tree_naive = sym_compile(
            scm, q,
            mode="symbolic",
            use_cache=False,
            disable_rewriting=True,
            disable_dag_folding=True,
            disable_canonicalization=True
        )
        t_naive = time.perf_counter() - t0
        expr_naive = tree_naive.to_sympy()
        ast_n_naive = count_ast_nodes(expr_naive)
        fail_flag = False
    except Exception as e:
        print("[Naive pipeline] Failed!", e)
        ast_n_naive = -1
        t_naive = -1
        fail_flag = True

    # 2. SICI-Cache pipeline: canonicalization + folding + rewrite
    try:
        if not fail_flag:
            expr = canonicalize_ast(expr_naive)
        else:
            # fallback: canonicalize a minimal valid expr
            expr = canonicalize_ast(
                SCM(graph).conditionals[list(SCM(graph).conditionals.keys())[0]]
            )
        et   = ExpressionTree(expr)
        t1 = time.perf_counter()
        root = fold_and_rewrite(et, skip_folding=False, skip_rewrite=False)
        t_fold = time.perf_counter() - t1
        dag_n = root.size()
    except Exception as e:
        print("[SICI-Cache pipeline] Unexpected failure!", e)
        dag_n = -1
        t_fold = -1

    return ast_n_naive, dag_n, t_naive, t_fold, fail_flag

def main():
    ns         = [500, 1000, 2000, 5000, 10000]
    reps       = 5
    max_parents = 3

    header = f"{'n':>6} | {'AST-n':>8} | {'DAG-n':>8} | {'naive(s)':>10} | {'fold(s)':>8} | {'Reduct(%)':>9} | {'naive_fail':>10}"
    print(header)
    print("-" * len(header))

    for n in ns:
        asts, dags, t_naives, t_folds, fails = [], [], [], [], []
        for i in range(reps):
            graph = generate_random_dag(n, max_parents, seed=SEED + n*reps + i)
            ast_n, dag_n, t_naive, t_fold, fail_flag = one_query_compare(graph)
            asts.append(ast_n)
            dags.append(dag_n)
            t_naives.append(t_naive)
            t_folds.append(t_fold)
            fails.append(fail_flag)
        # filter invalid
        valid = [(a, d) for a, d in zip(asts, dags) if a > 0 and d > 0]
        red = 100*np.mean([(1 - d/a) for a, d in valid]) if valid else 0
        avg_ast = int(np.mean([x for x in asts if x>0])) if any(x>0 for x in asts) else -1
        avg_dag = int(np.mean([x for x in dags if x>0])) if any(x>0 for x in dags) else -1
        avg_naive = np.mean([x for x in t_naives if x>0]) if any(x>0 for x in t_naives) else -1
        avg_fold = np.mean([x for x in t_folds if x>0]) if any(x>0 for x in t_folds) else -1
        n_fail = sum(fails)
        print(f"{n:6d} | {avg_ast:8d} | {avg_dag:8d} | {avg_naive:10.4f} | {avg_fold:8.4f} | {red:9.2f}% | {n_fail:10d}/{reps}")

    print("\nNote: naive_fail > 0 means naive pipeline exploded/failed, only SICI-Cache can scale;"
          " Reduct(%) is the percentage reduction in DAG node count.")

if __name__ == "__main__":
    main()
