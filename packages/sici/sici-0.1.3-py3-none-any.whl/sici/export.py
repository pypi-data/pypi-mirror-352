# sici/export.py

import sympy as sp
import json
from .tree import ExpressionTree
from .trace import TraceGraph

def export_sympy(tree: ExpressionTree) -> sp.Expr:
    """
    Return a raw SymPy expression from an ExpressionTree.
    :param tree: ExpressionTree
    :return: sympy.Expr
    """
    return tree.to_sympy()

def export_latex(tree: ExpressionTree) -> str:
    """
    Return LaTeX string of the symbolic expression.
    :param tree: ExpressionTree
    :return: str (LaTeX formatted)
    """
    return sp.latex(tree.to_sympy())

def export_json_tree(tree: ExpressionTree, filepath: str = None) -> dict:
    """
    Export the symbolic expression tree as a JSON structure.
    :param tree: ExpressionTree
    :param filepath: If provided, saves to this path
    :return: dictionary representing the tree
    """
    obj = tree.to_json()
    if filepath:
        with open(filepath, 'w') as f:
            json.dump(obj, f, indent=2)
    return obj

def export_json_trace(trace: TraceGraph, filepath: str = None) -> dict:
    """
    Export trace graph (nodes + edges) to JSON.
    :param trace: TraceGraph
    :param filepath: Optional path to save
    :return: dict with 'nodes' and 'edges'
    """
    obj = {
        "nodes": [n.__dict__ for n in trace.nodes],
        "edges": trace.edges
    }
    if filepath:
        with open(filepath, 'w') as f:
            json.dump(obj, f, indent=2)
    return obj
