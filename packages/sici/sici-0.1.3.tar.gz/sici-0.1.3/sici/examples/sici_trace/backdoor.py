# examples/backdoor.py

from sici.models import SCM, Query
from sici.compiler import compile

import sympy as sp

# Simple backdoor graph: Z -> X -> Y
scm = SCM(
    graph={
        "Z": [],
        "X": ["Z"],
        "Y": ["X", "Z"]
    },
    conditionals={
        "P(Z)": sp.Symbol("P_Z"),
        "P(X|Z)": sp.Symbol("P_X_given_Z"),
        "P(Y|X,Z)": sp.Symbol("P_Y_given_X_Z")
    }
)

query = Query(outcome="Y", intervention="X")

compiled = compile(scm, query)
compiled.visualize()
print(compiled.to_sympy())
