# sici/examples/sici_cache/cse_comparison.py

import time
import random
import numpy as np
import sympy as sp

from sici.models       import SCM, Query
from sici.compiler     import compile as sym_compile
from sici.canonical    import canonicalize_ast
from sici.tree         import ExpressionTree
from sici.dag          import fold_and_rewrite
from sici.metrics      import count_ast_nodes
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

def generate_random_dag(n, max_parents=2, seed=None):
    """Generate a random DAG with n nodes and at most max_parents parents per node."""
    rng = np.random.default_rng(seed)
    vars_ = [f"V{i}" for i in range(n)]
    graph = {}
    for i, v in enumerate(vars_):
        pop = vars_[:i]
        k   = int(rng.integers(0, min(len(pop), max_parents) + 1))
        parents = rng.choice(pop, size=k, replace=False).tolist() if k > 0 else []
        graph[v] = parents
    return graph

def build_canonical_ast(graph, x, y):
    """
    Compile canonicalized AST using SICI-Cache 
    (only canonicalization, no folding/rewrite), and return sympy.Expr.
    """
    scm = SCM(graph)
    q   = Query(outcome=y, intervention=x)
    tree = sym_compile(
        scm, q,
        mode="symbolic",
        use_cache=False,
        disable_dag_folding=True,
        disable_rewriting=True
    )
    expr = tree.to_sympy()
    # Canonicalize again to ensure consistency with internal representation
    return canonicalize_ast(expr)

def measure_combined(graph, x, y1, y2):
    # Build two ASTs
    expr1 = build_canonical_ast(graph, x, y1)
    expr2 = build_canonical_ast(graph, x, y2)
    combined = expr1 + expr2
    combined = canonicalize_ast(combined)

    # 1) Count combined AST nodes
    ast_n = count_ast_nodes(combined)

    # 2) SymPy CSE
    t0 = time.perf_counter()
    repls, reduced = sp.cse(combined)
    t_cse = time.perf_counter() - t0
    # CSE node count = sum of all repl expr nodes + all reduced expr nodes
    cse_n = sum(count_ast_nodes(r) for _, r in repls) \
          + sum(count_ast_nodes(r) for r in reduced)

    # 3) SICI-Cache DAG folding + rewrite
    tree_et = ExpressionTree(combined)
    t0 = time.perf_counter()
    dag_root = fold_and_rewrite(tree_et, skip_folding=False, skip_rewrite=False)
    t_fold = time.perf_counter() - t0
    dag_n = dag_root.size()

    return ast_n, len(repls), cse_n, t_cse, dag_n, t_fold

def main():
    print(f"{'n':>2} | {'AST-n':>6} | {'CSE-r':>5} | {'CSE-n':>6} | {'CSE(s)':>7} | "
          f"{'DAG-n':>6} | {'FOLD(s)':>7} | {'Reduct%':>7}")
    print("-" * 72)
    random.seed(0)
    for n in range(5, 11):            # Node count 5–10
        for rep in range(5):          # Run 5 times per size
            graph = generate_random_dag(n, max_parents=2, seed=1000 + n * 10 + rep)
            vars_ = list(graph.keys())
            x = random.choice(vars_)
            y1, y2 = random.sample([v for v in vars_ if v != x], 2)

            ast_n, cse_r, cse_n, t_cse, dag_n, t_fold = measure_combined(graph, x, y1, y2)
            reduct = 1 - dag_n / ast_n

            print(f"{n:2d} | {ast_n:6d} | {cse_r:5d} | {cse_n:6d} | {t_cse:7.4f} | "
                  f"{dag_n:6d} | {t_fold:7.4f} | {reduct * 100:7.2f}%")

if __name__ == "__main__":
    main()
