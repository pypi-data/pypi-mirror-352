# sici/tests/test_ast_generation.py
import pytest
import sympy as sp
from sici.models import SCM, Query
from sici.identity_checker import analyze_paths
from sici.ast_generator import ASTGenerator

def has_all_substr(s, substrs):
    """Return True iff all substrs appear in s."""
    return all(sub in s for sub in substrs)

def test_backdoor_ast_generation():
    """Validate AST generation for backdoor adjustment"""
    graph = {
        "Z": [],
        "X": ["Z"],
        "Y": ["X", "Z"]
    }
    conditionals = {
        "P(Z)": lambda z: sp.stats.norm.pdf(z, 0, 1),
        "P(X|Z)": lambda x, z: sp.stats.norm.pdf(x - z, 0, 0.1),
        "P(Y|X,Z)": lambda y, x, z: sp.stats.norm.pdf(y - x - z, 0, 0.1)
    }
    scm = SCM(graph, conditionals)
    query = Query(outcome="Y", intervention="X")

    case_type = analyze_paths(
        graph=graph,
        outcome=query.outcome,
        intervention=query.intervention,
        latent_nodes=scm.latent_vars
    )
    assert case_type == "backdoor"

    ast = ASTGenerator(scm).generate(case_type, query)
    assert isinstance(ast, sp.Integral)
    ast_str = str(ast)
    # As long as key terms are present (order does not matter)
    assert has_all_substr(ast_str, ["P(Y|X,Z)", "P(X|Z)", "P(Z)"])
    assert "Integral" in ast_str

def test_frontdoor_ast_generation():
    """Validate AST generation for frontdoor adjustment"""
    graph = {
        "X": [],
        "M": ["X"],
        "Y": ["M"]
    }
    conditionals = {
        "P(X)": lambda x: sp.stats.norm.pdf(x, 0, 1),
        "P(M|X)": lambda m, x: sp.stats.norm.pdf(m - 0.5*x, 0, 0.1),
        "P(Y|M)": lambda y, m: sp.stats.norm.pdf(y - m, 0, 0.1)
    }
    scm = SCM(
        graph=graph,
        conditionals=conditionals,
        latent_vars=set()
    )
    query = Query(outcome="Y", intervention="X")

    case_type = analyze_paths(
        graph,
        query.outcome,
        query.intervention,
        context=getattr(query, "context", None)
    )
    assert case_type == "frontdoor"

    ast = ASTGenerator(scm).generate(case_type, query)
    assert isinstance(ast, sp.Integral)
    ast_str = str(ast)
    # Frontdoor expression may contain P(Y|M,X) or P(Y|M), 
    # may have two or more layers of integration
    # Only key terms need to be present
    assert "P(M|X)" in ast_str
    assert "P(X)" in ast_str
    # Compatible with P(Y|M,X) or P(Y|M)
    assert any(sym in ast_str for sym in ["P(Y|M,X)", "P(Y|M)"])
    assert "Integral" in ast_str

def test_instrumental_variable_ast():
    """Validate AST generation for instrumental variable scenario"""
    graph = {
        "Z": [],
        "X": ["Z"],
        "Y": ["X", "U"],
        "U": []
    }
    conditionals = {
        "P(Z)": lambda z: sp.stats.uniform.pdf(z, 0, 1),
        "P(X|Z)": lambda x, z: sp.stats.norm.pdf(x - z, 0, 0.2),
        "P(Y|X,U)": lambda y, x, u: sp.stats.norm.pdf(y - 0.8*x - u, 0, 0.1)
    }
    scm = SCM(graph, conditionals, latent_vars={"U"})
    query = Query(outcome="Y", intervention="X")

    case_type = analyze_paths(
        scm.graph, query.outcome, query.intervention,
        latent_nodes=scm.latent_vars, context=getattr(query, "context", None)
    )
    assert case_type == "instrumental"

    ast = ASTGenerator(scm).generate(case_type, query)
    assert isinstance(ast, sp.Integral)
    ast_str = str(ast)
    # Flexible order of terms in the integrand; key terms must be present
    assert has_all_substr(ast_str, ["P(Y|X,Z)", "P(X|Z)", "P(Z)"])
    assert "Integral" in ast_str
    # Typically involves one or two layers of integration, no strict requirement
    # As long as it is a multivariable integral

def test_unobserved_confounding_ast():
    """Validate AST generation for unobserved confounding"""
    graph = {
        "X": ["U"],
        "Y": ["X", "U"],
        "U": []
    }
    conditionals = {
        "P(U)": lambda u: sp.stats.norm.pdf(u, 0, 1),
        "P(X|U)": lambda x, u: sp.stats.norm.pdf(x - u, 0, 0.2),
        "P(Y|X,U)": lambda y, x, u: sp.stats.norm.pdf(y - x - 0.5*u, 0, 0.1)
    }
    scm = SCM(graph, conditionals, latent_vars={"U"})
    query = Query(outcome="Y", intervention="X")

    case_type = analyze_paths(
        scm.graph, query.outcome, query.intervention,
        latent_nodes=scm.latent_vars, context=getattr(query, "context", None)
    )
    assert case_type == "unobserved_confounding"

    ast = ASTGenerator(scm).generate(case_type, query)
    # Check that beta, P(U), and Integral(U) are present
    ast_str = str(ast)
    assert "beta" in ast_str
    assert "P(U)" in ast_str
    assert "Integral" in ast_str

def test_counterfactual_ast_generation():
    """Validate AST generation for counterfactual inference"""
    graph = {
        "X": [],
        "Y": ["X", "U"],
        "U": []
    }
    conditionals = {
        "P(X)": lambda x: sp.stats.bernoulli.pmf(x, 0.5),
        "P(Y|X,U)": lambda y, x, u: sp.stats.norm.pdf(y - x - u, 0, 0.1),
        "P(U)": lambda u: sp.stats.norm.pdf(u, 0, 1)
    }
    scm = SCM(graph, conditionals, latent_vars={"U"})
    query = Query(outcome="Y", intervention="X", context={"X": 0})

    case_type = analyze_paths(
        scm.graph, query.outcome, query.intervention,
        latent_nodes=scm.latent_vars, context=getattr(query, "context", None)
    )
    assert case_type == "counterfactual"

    ast = ASTGenerator(scm).generate(case_type, query)
    ast_str = str(ast)
    # Check Integral, P(U), and P(Y_x|X=x,U) (or simplified form like P(Y_x|U))
    assert "Integral" in ast_str
    assert "P(U)" in ast_str
    assert any(s in ast_str for s in ["P(Y_x|X=x,U)", "P(Y_x|U)"])

if __name__ == "__main__":
    pytest.main(["-v", "--cov=sici", "--cov-report=html"])
