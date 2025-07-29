# sici/tests/test_identity_checker.py

import pytest
from sici.identity_checker import analyze_paths

def test_backdoor_case():
    graph = {
        "Z": [],
        "X": ["Z"],
        "Y": ["X", "Z"]
    }
    outcome = "Y"
    intervention = "X"
    result = analyze_paths(graph, outcome, intervention)
    assert result == "backdoor"
    print("✅ Backdoor case passed.")

def test_frontdoor_case():
    graph = {
        "X": [],
        "Z": ["X"],
        "Y": ["Z"]
    }
    outcome = "Y"
    intervention = "X"
    result = analyze_paths(graph, outcome, intervention)
    assert result == "frontdoor"
    print("✅ Frontdoor case passed.")

def test_confounded_case():
    graph = {
        "U": [],
        "X": ["U"],
        "Y": ["U"]
    }
    outcome = "Y"
    intervention = "X"
    latent = {"U"}
    result = analyze_paths(graph, outcome, intervention, latent_nodes=latent)
    assert result == "unobserved_confounding"
    print("✅ Unobserved confounding case passed.")

def test_unknown_case():
    graph = {
        "X": [],
        "Y": []
    }
    outcome = "Y"
    intervention = "X"
    result = analyze_paths(graph, outcome, intervention)
    assert result == "unknown"
    print("✅ Unknown case passed.")

if __name__ == "__main__":
    pytest.main(["-s", __file__])
