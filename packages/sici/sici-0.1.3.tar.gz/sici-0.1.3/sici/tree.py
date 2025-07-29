# sici/tree.py

import sympy as sp
from typing import Union
from sici.trace import TraceGraph
from sici.models import SCM, Query
from sici.canonical import canonicalize_ast
from sici.ast_generator import ASTGenerator  # New

class ExpressionTree:
    def __init__(self, root_expr: Union[sp.Expr, sp.Integral]):
        self.root = root_expr

    def to_sympy(self) -> sp.Expr:
        return self.root

    def to_latex(self) -> str:
        return sp.latex(self.root)

    def visualize(self):
        print(sp.pretty(self.root))

    def to_json(self):
        # 递归转换SymPy AST为JSON
        def expr_to_json(expr):
            if isinstance(expr, sp.Symbol):
                return {"op": "Symbol", "name": str(expr)}
            elif isinstance(expr, sp.Number):
                return {"op": "Number", "value": float(expr)}
            elif isinstance(expr, sp.Integral):
                return {
                    "op": "Integral",
                    "integrand": expr_to_json(expr.function),
                    "limits": [
                        {
                            "var": str(v[0]) if isinstance(v, (tuple, list)) else str(v),
                            "lower": float(v[1]) if len(v) > 1 else None,
                            "upper": float(v[2]) if len(v) > 2 else None,
                        } if isinstance(v, (tuple, list)) else {
                            "var": str(v),
                            "lower": None,
                            "upper": None,
                        }
                        for v in expr.limits
                    ]
                }
            elif isinstance(expr, sp.Mul):
                return {
                    "op": "Mul",
                    "args": [expr_to_json(a) for a in expr.args]
                }
            elif isinstance(expr, sp.Add):
                return {
                    "op": "Add",
                    "args": [expr_to_json(a) for a in expr.args]
                }
            else:
                return {
                    "op": type(expr).__name__,
                    "args": [expr_to_json(a) for a in expr.args]
                }
        return expr_to_json(self.root)



def build_expression_tree(
    scm: SCM,
    query: Query,
    trace: TraceGraph,
    *,
    disable_canonicalization: bool = False,
) -> ExpressionTree:
    """
    Construct an expression tree. Prefer using ASTGenerator to generate
    “fast-path” ASTs for backdoor/frontdoor/instrumental paths, etc.;
    otherwise fall back to the general product+integral construction.
    """

    # 1) If it's one of the fast-paths, use ASTGenerator directly
    case = trace.identification_result
    gen = ASTGenerator(scm)
    if case in {"backdoor", "frontdoor", "instrumental",
                "unobserved_confounding", "counterfactual"}:
        expr = gen.generate(case, query)
    else:
        # 2) ID-fallback: original product + integral logic
        def wrap_if_needed(label: str, val):
            if isinstance(val, sp.Expr):
                return val
            symname = (
                label.replace(" ", "")
                     .replace("|", "_given_")
                     .replace(",", "_")
                     .replace("(", "_")
                     .replace(")", "")
            )
            return sp.Symbol(symname, commutative=False)

        # Distribution symbol mapping
        labels2sym = {}
        for node in trace.nodes:
            if node.node_type == "distribution":
                clean = node.label.replace(" ", "")
                raw  = scm.conditionals.get(clean)
                if raw is None:
                    raise KeyError(f"No conditional for {node.label!r}")
                labels2sym[clean] = wrap_if_needed(node.label, raw)

        # 2a) Multiply all distributions not of form P(X|…)
        kept = [
            v for k, v in labels2sym.items()
            if not k.startswith(f"P({query.intervention}|")
        ]
        expr = sp.Mul(*kept)

        # 2b) Integrate over intervention variable and adjustment set in order
        expr = sp.Integral(expr, (sp.Symbol(query.intervention),))
        for z in getattr(trace, "adjustment_set", []):
            expr = sp.Integral(expr, (sp.Symbol(z),))

    # 3) Optional AST canonicalization
    if not disable_canonicalization:
        expr = canonicalize_ast(expr)

    return ExpressionTree(expr)
