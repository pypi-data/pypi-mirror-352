# sici/tests/test_compile_numeric.py

import numpy as np
from scipy.stats import norm
from sici.models    import SCM, Query
from sici.compiler  import compile  # unified entry point

def test_compile_v2_gaussian_backdoor():
    # Define the SCM:
    # Z ~ N(0, 1)
    # X = Z + noise_X (noise_X ~ N(0, 1))
    # Y = X + Z + noise_Y (noise_Y ~ N(0, 1))

    # Conditional probability functions
    def p_z(z):
        return norm.pdf(z, loc=0, scale=1)

    def p_x_given_z(x, z):
        return norm.pdf(x - z, loc=0, scale=1)

    def p_y_given_xz(y, x, z):
        return norm.pdf(y - (x + z), loc=0, scale=1)

    scm = SCM(
        graph={
            "Z": [],
            "X": ["Z"],
            "Y": ["X", "Z"]
        },
        conditionals={
            "P(Z)": p_z,
            "P(X|Z)": p_x_given_z,
            "P(Y|X,Z)": p_y_given_xz
        }
    )

    query = Query(outcome="Y", intervention="X")

    # Run the compile_v2
    result = compile(scm, query, mode="numeric")

    # --- Assertions ---
    assert isinstance(result, float)
    assert np.isfinite(result)
    print(f"test_compile_v2_gaussian_backdoor passed. Result: {result:.4f}")

if __name__ == "__main__":
    test_compile_v2_gaussian_backdoor()
