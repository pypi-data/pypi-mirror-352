# sici/tests/test_compile.py

import sympy as sp
import pytest
from sici.models import SCM, Query
from sici.compiler import compile
from sici.tree import ExpressionTree
from sici.dag import DAGNode

def test_compile_backdoor_expression():
    # Define SCM: Z → X → Y
    scm = SCM(
        graph={"Z": [], "X": ["Z"], "Y": ["X", "Z"]},
        conditionals={ 
            "P(Z)": sp.symbols("P_Z"),
            "P(X|Z)": sp.symbols("P_X_given_Z"),
            "P(Y|X,Z)": sp.symbols("P_Y_given_X_Z")
        }
    )

    query = Query(outcome="Y", intervention="X")

    # Call compiler
    tree = compile(scm, query)
    

    # --- Assertions ---
    assert isinstance(tree, DAGNode)
    assert isinstance(tree, ExpressionTree), "Should return ExpressionTree"
    expr = tree.to_sympy()
    assert isinstance(expr, sp.Integral), "Top-level node should be Integral"
    assert expr.variables[0] in [sp.Symbol("X"), sp.Symbol("Z")], f"Integration should be over X or Z, got {expr.variables[0]}"
    expected_names = {"P(Y|X,Z)", "P_Y_given_X_Z"}
    assert any(str(s) in expected_names for s in expr.free_symbols), \
        f"Missing expected symbol P(Y|X,Z) or P_Y_given_X_Z, got {[str(s) for s in expr.free_symbols]}"
    print("test_compile_backdoor_expression passed.")

def test_compile_wrong_types():
    with pytest.raises(TypeError):
        compile({"Z": []}, Query("Y", "X"))  # Invalid SCM type

    with pytest.raises(TypeError):
        compile(SCM({}, {}), "P(Y | do(X))")  # Invalid Query type

    print("test_compile_wrong_types passed.")

if __name__ == "__main__":
    test_compile_backdoor_expression()
    test_compile_wrong_types()
