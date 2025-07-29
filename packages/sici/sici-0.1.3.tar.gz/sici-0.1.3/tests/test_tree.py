# tests/test_tree.py

import sympy as sp
from sici.models import SCM, Query
from sici.trace import build_trace_graph
from sici.tree import build_expression_tree, ExpressionTree

def test_expression_tree_construction():
    # Define SCM: Z → X → Y
    scm = SCM(
        graph={
            "Z": [],
            "X": ["Z"],
            "Y": ["X", "Z"]
        },
        conditionals={
            "P(Z)": sp.symbols("P_Z", commutative=False),
            "P(X|Z)": sp.symbols("P_X_given_Z", commutative=False),
            "P(Y|X,Z)": sp.symbols("P_Y_given_X_Z", commutative=False)
        }
    )

    query = Query(outcome="Y", intervention="X")

    # Step 1: Build trace graph
    trace = build_trace_graph(scm, query)

    # Step 2: Build expression tree
    tree = build_expression_tree(scm, query, trace)

    assert isinstance(tree, ExpressionTree), "Should return an ExpressionTree object"

    expr = tree.to_sympy()

    # Check that expression includes known symbols (string matching for robustness)
    expected_names = {"P(Y|X,Z)", "P_Y_given_X_Z"}
    found_names = set(str(s) for s in expr.free_symbols)
    assert any(n in found_names for n in expected_names), \
        f"Missing P(Y|X,Z) or P_Y_given_X_Z, got {found_names}"

    # Also check P(X|Z) and P(Z) are present
    assert any("P(X|Z)" == str(s) or "P_X_given_Z" == str(s) for s in expr.free_symbols), \
        f"Missing P(X|Z) or P_X_given_Z, got {found_names}"
    assert any("P(Z)" == str(s) or "P_Z" == str(s) for s in expr.free_symbols), \
        f"Missing P(Z) or P_Z, got {found_names}"

    # Check the structure: integral over some variable
    assert isinstance(expr, sp.Integral)
    assert len(expr.variables) >= 1
    assert any(str(v) in ["X", "Z"] for v in expr.variables), \
        f"Integration should be over X or Z, got {[str(v) for v in expr.variables]}"
