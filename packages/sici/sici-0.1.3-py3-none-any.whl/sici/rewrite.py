# sici/rewrite.py
"""
Local, semantics-preserving rewriting passes on expression DAGs.

* pull_out_independent_integrals
* merge_sequential_independents
* reorder_products

Run `apply_rewrites(dag_root)` once after DAG folding; the routine
performs a depth-first traversal and applies in-place replacements of
`DAGNode.expr` where applicable, while preserving shared cache nodes.
"""

from __future__ import annotations
import sympy as sp
from typing import List
from .dag import DAGNode


# ----------------------------------------------------------------------
# entry point -----------------------------------------------------------
# ----------------------------------------------------------------------
def apply_rewrites(root: DAGNode) -> DAGNode:
    """
    Perform in-place DAG rewrites and return the root.
    """
    changed = True
    max_round = 3
    while changed and max_round:
        changed = _rewrite_pass(root, set())
        max_round -= 1
    return root


# ----------------------------------------------------------------------
# single traversal pass -------------------------------------------------
# ----------------------------------------------------------------------
def _rewrite_pass(node: DAGNode, visited: set) -> bool:
    """Return True if any modification happened under this node."""
    # 用 id(node) 而不是 node 自身来跟踪
    if id(node) in visited:
        return False
    visited.add(id(node))

    modified = False
    # 遍历 children 而不是 args
    for child in node.children:
        modified |= _rewrite_pass(child, visited)

    # bottom-up 依次尝试三条规则
    if _pull_out(node):
        return True
    if _merge_nested(node):
        return True
    if _reorder_mul(node):
        return True
    return modified


# ----------------------------------------------------------------------
# Rule 1: pull out independent integrals -------------------------------
# ----------------------------------------------------------------------
def _pull_out(node: DAGNode) -> bool:
    """
    Pattern: Integral(f(x)*g, (x,)) where g 不含 x  →  g * Integral(f(x),(x,))
    """
    expr = node.expr
    if not isinstance(expr, sp.Integral):
        return False

    var = expr.variables[0]
    body = expr.function
    if not isinstance(body, sp.Mul):
        return False

    indep, dep = [], []
    for f in body.args:
        (indep if var not in f.free_symbols else dep).append(f)

    if not indep or not dep:
        return False

    new_inner = sp.Integral(sp.Mul(*dep), (var,))
    new_expr  = sp.Mul(sp.Mul(*indep), new_inner)

    node.expr     = new_expr
    # 清空 children
    node.children = []
    return True


# ----------------------------------------------------------------------
# Rule 2: merge sequential integrals over independent variables --------
# ----------------------------------------------------------------------

def _merge_nested(node: DAGNode) -> bool:
    """
    Pattern: ∫ (∫ g(x) dx) dy  →  ∫ g(x) dx dy
    只要内层被积函数不含外层变量，就合并成双重积分。
    """
    expr = node.expr
    if not isinstance(expr, sp.Integral):
        return False
    inner = expr.function
    if not isinstance(inner, sp.Integral):
        return False

    var_outer = expr.variables[0]
    var_inner = inner.variables[0]
    base      = inner.function

    # 只要 base 不含外层变量，就可以扁平化
    if var_outer in base.free_symbols:
        return False

    # debug 用：确认规则被触发
    print("[REWRITE] merge_nested triggered")

    # 合并成一个双重积分
    # 取出原来两个 Integral 的 limits
    limits_inner = inner.limits   if hasattr(inner, 'limits') else ((var_inner,),)
    limits_outer = expr.limits     if hasattr(expr, 'limits')   else ((var_outer,),)
    # 合并成双重积分，并且保留每层的 limits
    merged = sp.Integral(base, *limits_inner, *limits_outer)
    node.expr     = merged
    node.children = []
    return True


# ----------------------------------------------------------------------
# Rule 3: reorder product (commutative) --------------------------------
# ----------------------------------------------------------------------
def _reorder_mul(node: DAGNode) -> bool:
    """
    Pattern: 重排 Mul 中的 args
    """
    expr = node.expr
    if not isinstance(expr, sp.Mul):
        return False

    sorted_args = tuple(sorted(expr.args, key=lambda a: sp.srepr(a)))
    if sorted_args == expr.args:
        return False

    node.expr     = sp.Mul(*sorted_args)
    node.children = []
    return True
