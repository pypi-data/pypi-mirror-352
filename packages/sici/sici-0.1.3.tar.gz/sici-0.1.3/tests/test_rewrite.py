# sici/tests/test_rewrite.py

import sympy as sp
import pytest
from sici.tree import ExpressionTree
from sici.dag import fold_and_rewrite
from sici.metrics import count_ast_nodes

def test_pull_out_and_merge_nested():
    x, z = sp.symbols('x z')
    # Construct P(z) using Function to ensure free_symbols includes z
    P = sp.Function('P')
    Pz = P(z)
    fx = sp.Function('f')(x)

    # Construct ∫ P(z) * (∫ f(x) dx) dz
    inner = sp.Integral(fx, (x, -sp.oo, sp.oo))
    outer = sp.Integral(Pz * inner, (z, -sp.oo, sp.oo))

    # Original AST node count
    ast_nodes = count_ast_nodes(outer)

    # Fold + rewrite
    tree = ExpressionTree(outer)
    dag_root = fold_and_rewrite(tree)

    # Node count after folding should be smaller
    dag_nodes = dag_root.size()
    assert dag_nodes < ast_nodes, f"DAG ({dag_nodes}) should be smaller than AST ({ast_nodes})"

    # Get the final SymPy expression
    expr_after = dag_root.expr

    # The top-level should be Mul(inner_integral, outer_integral)
    assert isinstance(expr_after, sp.Mul), "The inner integral should be pulled out, top-level should be Mul"

    # Find the two integrals: one is ∫f(x)dx, the other is ∫P(z)dz
    integrals = [arg for arg in expr_after.args if isinstance(arg, sp.Integral)]
    assert len(integrals) == 2, f"Expected 2 Integrals, but found {len(integrals)}: {integrals}"

    # Verify that their integrands are f(x) and P(z)
    funcs = {str(iv.function) for iv in integrals}
    assert funcs == {'f(x)', 'P(z)'}, f"Expected integrands f(x) and P(z), but got {funcs}"

    # Verify that the unique integration variable of ∫P(z)dz is z
    pz_int = next(iv for iv in integrals if str(iv.function) == 'P(z)')
    vars_list = list(pz_int.variables)
    assert len(vars_list) == 1 and vars_list[0] == z, (
        f"Expected variable list of ∫P(z) to be [z], but got {vars_list}"
    )

if __name__ == "__main__":
    pytest.main([__file__])
