# sici/examples/sici_trace/two_confounders_numeric.py

import numpy as np
from scipy.stats import norm

from sici.models   import SCM, Query
from sici.compiler import compile   # unified compiler

def test_two_confounders_numeric():
    # Two binary confounders Z1, Z2 and continuous X, Y
    p_z1 = {0: 0.6, 1: 0.4}
    p_z2 = {0: 0.5, 1: 0.5}

    def p_x_given_z12(x, z1, z2):
        mu = z1 - z2
        return norm.pdf(x, loc=mu, scale=1)

    def p_y_given_xz12(y, x, z1, z2):
        mu = x + z1 + 2*z2
        return norm.pdf(y, loc=mu, scale=1)

    scm = SCM(
        graph={
            "Z1": [], "Z2": [],
            "X":  ["Z1", "Z2"],
            "Y":  ["X", "Z1", "Z2"],
        },
        conditionals={
            "P(Z1)"       : p_z1,
            "P(Z2)"       : p_z2,
            "P(X|Z1,Z2)"  : p_x_given_z12,
            "P(Y|X,Z1,Z2)": p_y_given_xz12,
        }
    )

    query = Query(outcome="Y", intervention="X")

    # Run the unified compiler in numeric mode
    result = compile(scm, query, mode="numeric")

    # Extract the float
    value = result.value if hasattr(result, "value") else result

    print(f"Causal effect E[Y | do(X=0)] = {value:.4f}")

if __name__ == "__main__":
    test_two_confounders_numeric()
