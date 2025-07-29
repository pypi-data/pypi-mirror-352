# sici/tests/test_visual.py

import sympy as sp
from sici.trace import TraceGraph, TraceNode
from sici.tree import ExpressionTree
from sici.visual import visualize_trace_graph, visualize_expression_tree

def test_visualize_trace_graph_and_expression_tree():
    # Fake trace
    trace = TraceGraph(
        nodes=[
            TraceNode(label="P(Y|X,Z)", node_type="distribution"),
            TraceNode(label="P(Z)", node_type="distribution"),
            TraceNode(label="×", node_type="operator"),
            TraceNode(label="∫ X", node_type="integral", scope="X")
        ],
        edges=[
            ("P(Y|X,Z)", "×"),
            ("P(Z)", "×"),
            ("×", "∫ X")
        ]
    )

    # Fake expression tree
    expr = sp.Integral(sp.Symbol("P_Y_given_X_Z"), (sp.Symbol("X"),))
    tree = ExpressionTree(expr)

    g1 = visualize_trace_graph(trace, filename="test_trace_graph", view=False)
    g2 = visualize_expression_tree(tree, filename="test_expression_tree", view=False)

    assert g1 is not None
    assert g2 is not None

if __name__ == "__main__":
    test_visualize_trace_graph_and_expression_tree()
    print("✅ test_visual passed.")
