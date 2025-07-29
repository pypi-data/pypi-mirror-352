# sici/tests/test_rewrite_3rules.py

import sympy as sp
import pytest

from sici.tree import ExpressionTree
from sici.dag import fold_and_rewrite
from sici.metrics import count_ast_nodes
from sici.canonical import canonicalize_ast


def test_integral_pull_out_rule():
    # ∫ P(z) * (∫ f(x) dx) dz should trigger pull-out, 
    # becoming Mul(Integral(f), Integral(P))
    x, z = sp.symbols('x z')
    Pz = sp.Function('P')(z)
    fx = sp.Function('f')(x)

    inner = sp.Integral(fx, (x, -sp.oo, sp.oo))
    expr = sp.Integral(Pz * inner, (z, -sp.oo, sp.oo))
    tree = ExpressionTree(expr)

    # fold only
    dag_fold = fold_and_rewrite(tree, skip_rewrite=True)
    expr_fold = dag_fold.expr
    # fold + rewrite
    dag_full = fold_and_rewrite(tree, skip_rewrite=False)
    expr_full = dag_full.expr

    # After fold + rewrite, the top-level should be Mul, with two Integrals
    assert isinstance(expr_full, sp.Mul), f"Expected Mul after pull-out, got {expr_full}"
    ints = [a for a in expr_full.args if isinstance(a, sp.Integral)]
    assert len(ints) == 2, f"Expected 2 Integrals after pull-out, got {ints}"
    funcs = {str(iv.function) for iv in ints}
    assert funcs == {'f(x)', 'P(z)'}, f"Expected functions f(x), P(z), got {funcs}"


def test_nested_integral_flatten_rule():
    # Pure nesting: ∫ (∫ h(x) dx) dy should trigger nested-flatten, 
    # becoming ∫ h(x) dx dy (two variables in one Integral node)
    x, y = sp.symbols('x y')
    h = sp.Function('h')(x)

    inner = sp.Integral(h, (x, -sp.oo, sp.oo))
    expr = sp.Integral(inner, (y, -sp.oo, sp.oo))
    tree = ExpressionTree(expr)

    # fold + rewrite
    dag_full = fold_and_rewrite(tree, skip_rewrite=False)
    expr_full = dag_full.expr

    # Result should be a single Integral over both x and y
    assert isinstance(expr_full, sp.Integral), f"Expected a single Integral, got {expr_full}"
    # The integrand should still be h(x)
    assert expr_full.function == h, f"Expected integrand h(x), got {expr_full.function}"
    # Variable list should include both x and y
    var_names = {v.name for v in expr_full.variables}
    assert var_names == {'x', 'y'}, f"Expected variables (x,y), got {expr_full.variables}"


def test_product_reordering_rule():
    # Product expressions with different factor orders should canonicalize to the same form
    a, b, c = sp.symbols('a b c')
    m1 = sp.Mul(a, b, c, evaluate=False)
    m2 = sp.Mul(c, b, a, evaluate=False)

    c1 = canonicalize_ast(m1)
    c2 = canonicalize_ast(m2)

    assert sp.srepr(c1) == sp.srepr(c2), f"Expected same after reorder: {c1} vs {c2}"


if __name__ == "__main__":
    pytest.main([__file__])
