# sici/tests/test_trace.py

import sympy as sp
from sici.models import SCM, Query
from sici.trace import build_trace_graph, TraceNode, TraceGraph

def test_basic_backdoor_trace_graph():
    # SCM: Z → X → Y
    scm = SCM(
        graph={
            "Z": [],
            "X": ["Z"],
            "Y": ["X", "Z"]
        },
        conditionals={
            "P(Z)": sp.symbols("P_Z"),
            "P(X|Z)": sp.symbols("P_X_given_Z"),
            "P(Y|X,Z)": sp.symbols("P_Y_given_X_Z")
        }
    )

    query = Query(outcome="Y", intervention="X")
    trace = build_trace_graph(scm, query)

    # --- Structural Assertions ---
    dist_labels = [n.label for n in trace.nodes if n.node_type == "distribution"]
    assert any("P(Y|X,Z)" in d for d in dist_labels), "P(Y|X,Z) missing"
    assert any("P(Z)" in d for d in dist_labels), "P(Z) missing"
    
    operator_labels = [n.label for n in trace.nodes if n.node_type == "operator"]
    assert "×" in operator_labels, "Missing multiplication node"

    integral_nodes = [n for n in trace.nodes if n.node_type == "integral"]
    assert len(integral_nodes) == 1, "Should have 1 integration node"
    assert integral_nodes[0].scope == "X", "Integration should be over do variable X"

    # --- Edge Assertions ---
    edge_labels = trace.edges
    assert any(edge == ("P(Y|X,Z)", "×") for edge in edge_labels), "Missing edge P(Y|X,Z) → ×"
    assert any(edge == ("P(Z)", "×") for edge in edge_labels), "Missing edge P(Z) → ×"
    assert any(edge == ("×", "∫ X") for edge in edge_labels), "Missing edge × → ∫ X"


    print("✅ test_basic_backdoor_trace_graph passed.")

if __name__ == "__main__":
    test_basic_backdoor_trace_graph()
