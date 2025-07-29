# sici/visual.py

from graphviz import Digraph
from sympy import Basic as SymPyExpr
from .trace import TraceGraph, TraceNode
from .tree import ExpressionTree
import sympy as sp


def visualize_trace_graph(trace: TraceGraph,
                          filename: str = "trace_graph",
                          view: bool = False):
    dot = Digraph(name=filename)
    dot.attr(rankdir='TB', nodesep="0.25", ranksep="0.4")

    # pretty label helper ------------------------------------------------
    def _clean(lbl: str) -> str:
        return lbl.replace("P(", "P(").replace(",", ", ")  # ←可按需做 LaTeX

    # --------------------------------------------------------------------
    for n in trace.nodes:
        if n.node_type == "distribution":
            dot.node(n.label, label=_clean(n.label), shape="ellipse")
        elif n.node_type == "operator":
            dot.node(n.label, label="×", shape="rectangle")
        elif n.node_type == "integral":
            scope = n.scope or ""
            dot.node(n.label, label=f"∫ {scope}", shape="diamond")

    for src, dst in trace.edges:
        dot.edge(src, dst)

    dot.render(filename=filename, format="png", cleanup=True, view=view)
    return dot


def visualize_expression_tree(tree: ExpressionTree,
                              filename: str = "expression_tree",
                              view: bool = False):
    dot = Digraph(name=filename)
    dot.attr(rankdir='TB', nodesep="0.25", ranksep="0.35")
    def add(expr, parent_id=None, idx=[0]):
        node_id = f"n{idx[0]}"; idx[0] += 1

        # ------------------ pretty label -------------------
        if isinstance(expr, sp.Integral):
            vars_ = ", ".join([str(v) for v in expr.variables])
            lbl = f"∫ {vars_}"
            shape = "diamond"
        elif isinstance(expr, sp.Mul):
            lbl, shape = "×", "rectangle"
        elif isinstance(expr, sp.Symbol):
            lbl, shape = str(expr), "ellipse"
        else:       # e.g. sympy Tuple
            lbl, shape = str(expr.func), "ellipse"

        dot.node(node_id, label=lbl, shape=shape)
        if parent_id:
            dot.edge(parent_id, node_id)

        # --------------- recurse on children ---------------
        if isinstance(expr, sp.Integral):
            add(expr.function, node_id)
        elif isinstance(expr, sp.Mul):
            for arg in expr.args:
                add(arg, node_id)
        elif isinstance(expr, (sp.Tuple,)):
            for arg in expr:
                add(arg, node_id)

    add(tree.to_sympy())
    dot.render(filename=filename, format="png", cleanup=True, view=view)
    return dot