import sympy as sp
from sici.models import SCM

def test_scm_auto_conditionals():
    # Define a causal graph with no explicit conditionals
    graph = {
        "Z": [],
        "X": ["Z"],
        "Y": ["X", "Z"]
    }

    # Instantiate SCM with only the graph
    scm = SCM(graph)

    # Expected keys in conditionals
    expected_keys = ["P(Z)", "P(X|Z)", "P(Y|X,Z)"]
    # As long as the auto-generated keys are present, we don't require specific Symbol types or exact instances
    for label in expected_keys:
        assert label in scm.conditionals, f"Missing {label} in generated conditionals"
        val = scm.conditionals[label]
        # It can be either a symbol or a string (depends on implementation)
        assert isinstance(val, (sp.Symbol, str)), f"Conditional {label} is not a symbol or str"
        # The variable names should be present in the symbol name
        for v in label.replace("P(", "").replace(")", "").replace("|", ",").split(","):
            v = v.strip()
            if v:
                assert v in str(val), f"{label} conditional symbol missing variable {v} (got {val})"
