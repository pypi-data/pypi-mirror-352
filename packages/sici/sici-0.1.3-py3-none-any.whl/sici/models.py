# sici/models.py

import sympy as sp
import numpy as np
from scipy.integrate import nquad
from itertools import product
from typing import Dict, List, Optional, Set, Callable, Union


class SCM:
    """
    Structural Causal Model:
      - graph: adjacency list (node -> list of parents)
      - conditionals: mapping "P(X|Pa…)" or "P(X)" -> either
          • a SymPy Expr (symbolic mode),
          • a dict (discrete PMF),
          • or a callable (continuous density)
      - latent_vars: set of unobserved (latent) variable names
      - state_names: mapping node -> list of its discrete support values
    """
    def __init__(
        self,
        graph: Dict[str, List[str]],
        conditionals: Optional[Dict[str, Union[sp.Expr, Callable, dict]]] = None,
        latent_vars: Optional[Set[str]] = None,
        state_names: Optional[Dict[str, List[Union[int, float]]]] = None
    ):
        self.graph = graph
        # use provided conditionals or auto-generate symbolic ones
        self.conditionals = (
            conditionals
            if conditionals is not None
            else self._auto_generate_conditionals()
        )
        self.latent_vars = latent_vars or set()

        # determine discrete support (state_names)
        if state_names:
            self.state_names = state_names
        else:
            self.state_names: Dict[str, List[Union[int, float]]] = {}
            for label, cond in self.conditionals.items():
                if isinstance(cond, dict):
                    # parse var name from "P(var|…)" or "P(var)"
                    var = label.split("(", 1)[1].split("|", 1)[0].rstrip(")")
                    vals = set()
                    for key in cond.keys():
                        # key might be like (value, …) or a single value
                        if isinstance(key, tuple):
                            vals.add(key[0])
                        else:
                            vals.add(key)
                    try:
                        self.state_names[var] = sorted(vals)
                    except TypeError:
                        # mixed types: fall back to string sorting
                        self.state_names[var] = sorted(vals, key=lambda x: str(x))

    def _auto_generate_conditionals(self) -> Dict[str, sp.Expr]:
        """
        When no conditionals are provided, create fresh SymPy symbols:
        P(V) or P(V|Pa1,Pa2,…).
        """
        conds: Dict[str, sp.Expr] = {}
        for v, parents in self.graph.items():
            if parents:
                label = f"P({v}|{','.join(parents)})"
                sym   = sp.Symbol(f"P_{v}_given_{'_'.join(parents)}",
                                  commutative=False)
            else:
                label = f"P({v})"
                sym   = sp.Symbol(f"P_{v}", commutative=False)
            conds[label] = sym
        return conds

    def variables(self) -> List[str]:
        """All nodes in the graph."""
        return list(self.graph.keys())

    def parents_of(self, v: str) -> List[str]:
        """Return the immediate parents of node `v`."""
        return self.graph.get(v, [])

    def get_conditional(
        self,
        v: str,
        parents: List[str] = None
    ) -> Union[sp.Expr, Callable, dict]:
        """
        Look up the conditional distribution for v.
        If `parents` is given, match "P(v|pa1,…)" exactly.
        Otherwise return the first label starting with "P(v".
        """
        if parents is not None:
            label = f"P({v}|{','.join(parents)})"
            return self.conditionals[label]
        for label, val in self.conditionals.items():
            if label.startswith(f"P({v}") or label == f"P({v})":
                return val
        raise ValueError(f"No conditional found for variable '{v}'")


class Query:
    """
    Causal query object: P(Y | do(X)), with optional counterfactual context.
    """
    def __init__(
        self,
        outcome: str,
        intervention: str,
        context: Optional[Dict[str, Union[int, float]]] = None
    ):
        self.outcome = outcome
        self.intervention = intervention
        self.context = context or {}

    def __repr__(self):
        return f"P({self.outcome} | do({self.intervention}))"
