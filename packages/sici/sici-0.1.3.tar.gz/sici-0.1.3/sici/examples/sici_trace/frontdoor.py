# examples/sici_trace/frontdoor.py

from sici.models import SCM, Query
from sici.compiler import compile

import sympy as sp

scm = SCM(
    graph={
        "X": [],      
        "M": ["X"],   
        "Y": ["M"],   
    },
    conditionals={
        "P(X)"   : sp.Symbol("P_X"),
        "P(M|X)" : sp.Symbol("P_M_given_X"),
        "P(Y|M)" : sp.Symbol("P_Y_given_M"),  # 改成只带 M
    }
)

query = Query(outcome="Y", intervention="X")

compiled = compile(scm, query)
compiled.visualize()
print(compiled.to_sympy())
