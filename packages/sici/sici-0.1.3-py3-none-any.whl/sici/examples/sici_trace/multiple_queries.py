# examples/multiple_queries.py

from sici.models import SCM, Query
from sici.compiler import compile

import sympy as sp

# SCM with two outputs
scm = SCM(
    graph={
        "Z": [],
        "X": ["Z"],
        "Y": ["X"],
        "W": ["X"]
    },
    conditionals={
        "P(Z)": sp.Symbol("P_Z"),
        "P(X|Z)": sp.Symbol("P_X_given_Z"),
        "P(Y|X)": sp.Symbol("P_Y_given_X"),
        "P(W|X)": sp.Symbol("P_W_given_X")
    }
)

query_y = Query(outcome="Y", intervention="X")
query_w = Query(outcome="W", intervention="X")

compiled_y = compile(scm, query_y)
compiled_w = compile(scm, query_w)

compiled_y.visualize()
compiled_w.visualize()

print(compiled_y.to_sympy())
print(compiled_w.to_sympy())
