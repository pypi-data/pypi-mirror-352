#sici/precompiled.py

from sympy import Integral, Symbol, Mul

TEMPLATES = {
    "instrumental": Integral(
        Integral(
            Mul(
                Symbol('P(Y|X,Z)'), 
                Symbol('P(Z)')
            ),
            (Symbol('Z'),)
        ),
        (Symbol('X'),)
    ),
    "unobserved_confounding": Mul(
        Symbol('beta'),
        Integral(
            Symbol('P(U)'),
            (Symbol('U'),)
        )
    ),
    "counterfactual": Integral(
        Mul(
            Symbol('P(Y_x|X=x,U)'),
            Symbol('P(U)')
        ),
        (Symbol('U'),)
    )
}