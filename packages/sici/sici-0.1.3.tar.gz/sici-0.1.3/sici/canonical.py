# sici/canonical.py
"""
Canonicalization utilities for symbolic integration trees produced by SICI-Trace
or any SymPy‐based causal-integration compiler.

• Variable order & integration order normalization  
• Unified ordering of product nodes  
• Conditional distribution strings (P(Y|X,Z)) → unify parent variable dictionary order  
The output is a new SymPy expression structurally normalised, enabling
structural hashing & DAG folding downstream.

"""

from __future__ import annotations
from functools import lru_cache
import sympy as sp


# ----------------------------------------------------------------------
# -- public api ---------------------------------------------------------
# ----------------------------------------------------------------------
def canonicalize_ast(expr: sp.Expr) -> sp.Expr:
    """
    Recursively normalise a SymPy expression that may contain Integrals,
    Mul (product) nodes and Symbol leaves representing conditional
    distributions.

    Parameters
    ----------
    expr : sp.Expr
        The raw expression emitted by build_expression_tree.

    Returns
    -------
    sp.Expr
        A new, canonicalised SymPy expression.
    """
    return _canon(expr)


# ----------------------------------------------------------------------
# -- implementation helpers --------------------------------------------
# ----------------------------------------------------------------------
@lru_cache(maxsize=None)
def _canon(expr: sp.Expr) -> sp.Expr:
    """Internal recursive canonicalisation with memoisation."""
    # (1) Symbol representing distribution: normalise parent order
    if isinstance(expr, sp.Symbol):
        name = str(expr)
        if name.startswith("P(") and "|" in name:
            lhs, rhs = name[2:-1].split("|", 1)  # 处理多级条件
            lhs = lhs.strip()
            parents = [p.strip() for p in rhs.split(",")]
            parents_sorted = sorted(parents, key=lambda x: x)
            new_name = f"P({lhs}|{','.join(parents_sorted)})"
            return sp.Symbol(new_name)
        return expr
    # (2) Product/Mul: canonicalise children then sort by structural key
    if isinstance(expr, sp.Mul):
        args_canon = [_canon(a) for a in expr.args]
        args_sorted = sorted(args_canon, key=lambda x: sp.srepr(x))
        return sp.Mul(*args_sorted)
    # (3) Integral: canonicalise body & sort limits (preserve lower/upper)
    if isinstance(expr, sp.Integral):
        # expr.limits 是类似 ((var1, lo1, hi1), (var2, lo2, hi2), …)
        limits_sorted = sorted(expr.limits, key=lambda lim: lim[0].name)
        return sp.Integral(_canon(expr.function), *limits_sorted)

    # (4) Other SymPy node: canonicalise children generically
    if expr.args:
        new_args = tuple(_canon(a) for a in expr.args)
        return expr.func(*new_args)

    return expr  # leaf (number, etc.)


def _structural_key(node: sp.Expr) -> tuple:
    """
    Generate a sortable key for SymPy nodes to enable deterministic
    ordering inside commutative operations (Mul).

    We use (op-name, hash-of-string) for simplicity; more elaborate keys
    aren’t necessary for structural hashing later.
    """
    return (node.func.__name__, sp.srepr(node))
