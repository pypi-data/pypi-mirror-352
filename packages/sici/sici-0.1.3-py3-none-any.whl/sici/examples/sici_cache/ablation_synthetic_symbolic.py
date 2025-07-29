# sici/examples/sici_cache/ablation_synthetic_symbolic.py

import time
import sympy as sp

from sici.canonical import canonicalize_ast
from sici.tree      import ExpressionTree
from sici.dag       import fold_and_rewrite
from sici.metrics   import count_ast_nodes

# Construct an expression with more obvious repeated subexpressions:
#    sub = (a + b) * (c + d)
#    expr = sub + sub + sub
# This way sub appears 3 times, and the difference before and after folding will be obvious.
a, b, c, d = sp.symbols('a b c d')
sub = (a + b) * (c + d)
expr_full = sub + sub + sub

def measure(name, do_canon, do_fold, do_rewrite):
    # 1) Canonicalize?
    expr = canonicalize_ast(expr_full) if do_canon else expr_full

    # 2) Count AST nodes
    ast_n = count_ast_nodes(expr)

    # 3) Pass both flags into fold_and_rewrite:
    #    skip_folding = not do_fold
    #    skip_rewrite = not do_rewrite
    tree = ExpressionTree(expr)
    t0 = time.perf_counter()
    dag_root = fold_and_rewrite(
        tree,
        skip_folding=not do_fold,
        skip_rewrite=not do_rewrite
    )
    fold_ms = (time.perf_counter() - t0) * 1000

    # 4) DAG node count
    dag_n = dag_root.size()
    return ast_n, dag_n, fold_ms

if __name__ == "__main__":
    configs = [
        ("full",                True,  True,  True),
        ("no_canonicalization", False, True,  True),
        ("no_dag_folding",      True,  False, True),
        ("no_rewriting",        True,  True,  False),
    ]

    print("Config ｜ AST‐nodes ｜ DAG‐nodes ｜ Fold Time (ms)  midrule")
    for name, canon, fold, rewrite in configs:
        ast_n, dag_n, ms = measure(name, canon, fold, rewrite)
        print(f"{name} ｜ {ast_n} ｜ {dag_n} ｜ {ms:.1f} ")
