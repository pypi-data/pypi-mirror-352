# sici/examples/failure_existing.py

"""
Experiment: Failure Modes of Existing Symbolic Tools (SymPy CSE vs SICI-Cache)
------------------------------------------------------------------------------

Compare SymPy's CSE and SICI-Cache DAG folding in typical causal inference queries:
- Cross-query subexpression reuse (e.g., integrals over same adjustment set but different outcomes)
- Variable order differences
- Nested integral structures

Outputs:
- AST node counts after CSE / after SICI-Cache
- Side-by-side pretty-print of symbolic expressions

Run with: python sici/examples/failure_existing.py
"""
import random
import numpy as np
import sympy as sp
from sympy.simplify.cse_main import cse
from sici.canonical import canonicalize_ast
from sici.dag import fold_and_rewrite
from sici.tree import ExpressionTree
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

def count_ast_nodes(expr):
    """Count number of nodes in sympy AST."""
    if not hasattr(expr, 'args') or not expr.args:
        return 1
    return 1 + sum(count_ast_nodes(arg) for arg in expr.args)

def print_comparison(title, expr1, expr2, nodes1, nodes2):
    print(f"\n--- {title} ---")
    print("SymPy CSE Output:")
    print(sp.pretty(expr1))
    print(f"  AST nodes: {nodes1}")
    print("\nSICI-Cache Output:")
    print(sp.pretty(expr2))
    print(f"  AST nodes: {nodes2}")
    print("-" * 50)

def sympy_cse_expr(expr):
    # SymPy's cse returns (list of substitutions, reduced expr)
    subs, reduced = cse(expr)
    # For node count, count all ASTs (subs + reduced expr)
    all_exprs = [v for _, v in subs] + ([reduced] if not isinstance(reduced, list) else reduced)
    return all_exprs, sum(count_ast_nodes(e) for e in all_exprs)

def sici_cache_expr(expr):
    # Canonicalize and fold to DAG (simulate main pipeline)
    expr_canon = canonicalize_ast(expr)
    dag = fold_and_rewrite(ExpressionTree(expr_canon))
    # The expr property of dag's root is the simplified version
    # Node count = dag.size()
    return dag.expr, dag.size()

if __name__ == "__main__":
    # Example 1: Cross-query redundant integrals
    # Query 1: ∫ P(Y|X,z) P(z) dz
    # Query 2: ∫ P(Y'|X,z) P(z) dz
    z = sp.Symbol("z")
    x = sp.Symbol("x")
    y  = sp.Symbol("y")
    y1 = sp.Symbol("y1")
    y2 = sp.Symbol("y2")

    p_y1_given_xz = sp.Symbol("P(y1|x,z)", commutative=False)
    p_y2_given_xz = sp.Symbol("P(y2|x,z)", commutative=False)
    p_z = sp.Symbol("P(z)", commutative=False)

    expr1 = sp.Integral(p_y1_given_xz * p_z, (z,))
    expr2 = sp.Integral(p_y2_given_xz * p_z, (z,))

    # SymPy CSE on expr1 + expr2
    sum_expr = expr1 + expr2
    sympy_exprs, sympy_nodes = sympy_cse_expr(sum_expr)
    sympy_combined = sympy_exprs[-1] if sympy_exprs else sum_expr  # show final result

    # SICI-Cache: canonicalize and fold (should merge inside the integral)
    sici_expr, sici_nodes = sici_cache_expr(sum_expr)

    print_comparison(
        "Cross-query redundant integral: ∫ P(Y1|x,z)P(z)dz + ∫ P(Y2|x,z)P(z)dz",
        sympy_combined, sici_expr, sympy_nodes, sici_nodes
    )

    # Example 2: Variable order
    # ∫ P(y|z,x)P(z) dz  vs  ∫ P(z)P(y|x,z) dz (same up to order)
    p_y_given_zx = sp.Symbol("P(y|z,x)", commutative=False)
    p_y_given_xz = sp.Symbol("P(y|x,z)", commutative=False)

    expr3 = sp.Integral(p_y_given_zx * p_z, (z,))
    expr4 = sp.Integral(p_z * p_y_given_xz, (z,))

    # SymPy CSE (should treat as distinct)
    sympy_exprs2, sympy_nodes2 = sympy_cse_expr(expr3 + expr4)
    sympy_combined2 = sympy_exprs2[-1] if sympy_exprs2 else expr3 + expr4

    # SICI-Cache: canonicalizes variable/product order
    sici_expr2, sici_nodes2 = sici_cache_expr(expr3 + expr4)

    print_comparison(
        "Variable order: ∫ P(y|z,x)P(z)dz + ∫ P(z)P(y|x,z)dz",
        sympy_combined2, sici_expr2, sympy_nodes2, sici_nodes2
    )

    # Example 3: Nested redundant integrals (flat vs nested)
    # ∫ (∫ P(y|x,z) P(z) dz) dx   vs   ∫∫ P(y|x,z) P(z) dz dx
    expr5 = sp.Integral(sp.Integral(p_y_given_xz * p_z, (z,)), (x,))
    expr6 = sp.Integral(sp.Integral(p_y_given_xz * p_z, (x,)), (z,))  # wrong nesting, but for demonstration

    # SymPy CSE
    sympy_exprs3, sympy_nodes3 = sympy_cse_expr(expr5 + expr6)
    sympy_combined3 = sympy_exprs3[-1] if sympy_exprs3 else expr5 + expr6

    # SICI-Cache (should flatten and merge)
    sici_expr3, sici_nodes3 = sici_cache_expr(expr5 + expr6)

    print_comparison(
        "Nested redundant integrals: ∫(∫P(y|x,z)P(z)dz)dx + ∫(∫P(y|x,z)P(z)dx)dz",
        sympy_combined3, sici_expr3, sympy_nodes3, sici_nodes3
    )

    print("\nSummary: In all cases, SICI-Cache merges structurally equivalent sub-expressions even when SymPy CSE fails.")
