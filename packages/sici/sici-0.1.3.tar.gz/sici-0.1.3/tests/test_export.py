# sici/tests/test_export.py
import sympy as sp
from sici.tree import ExpressionTree
from sici.export import export_sympy, export_latex, export_json_tree

def test_export_sympy_latex_json():
    expr = sp.Integral(sp.Symbol("P_Y_given_X_Z"), (sp.Symbol("X"),))
    tree = ExpressionTree(expr)

    assert export_sympy(tree) == expr

    latex = export_latex(tree)
    assert isinstance(latex, str)
    assert "\\int" in latex
    assert "P_{Y given X Z}" in latex 

    json_tree = export_json_tree(tree)
    assert isinstance(json_tree, dict)
    assert "op" in json_tree

if __name__ == "__main__":
    test_export_sympy_latex_json()
    print("✅ test_export passed.")
