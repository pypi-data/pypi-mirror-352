import numpy as np
from scipy.stats import norm

from sici.models   import SCM, Query
from sici.compiler import compile  

def test_mixed_discrete_continuous_numeric():
    # Discrete confounder Z ∈ {0,1}
    p_z = {0: 0.6, 1: 0.4}

    # Continuous X | Z
    def p_x_given_z(x, z):
        return norm.pdf(x, loc=0.5*z, scale=1)

    # Continuous Y | X,Z
    def p_y_given_xz(y, x, z):
        return norm.pdf(y, loc=(x + z), scale=1)

    scm = SCM(
        graph={
            "Z": [],
            "X": ["Z"],
            "Y": ["X", "Z"]
        },
        conditionals={
            "P(Z)"    : p_z,             # discrete PMF
            "P(X|Z)"  : p_x_given_z,     # continuous density
            "P(Y|X,Z)": p_y_given_xz,    # continuous density
        }
    )

    query = Query(outcome="Y", intervention="X")

    # Now numeric mode will work
    result = compile(scm, query, mode="numeric")
    value  = result.value if hasattr(result, "value") else result

    print(f"E[Y | do(X=0)] = {value:.4f}")

if __name__ == "__main__":
    test_mixed_discrete_continuous_numeric()
