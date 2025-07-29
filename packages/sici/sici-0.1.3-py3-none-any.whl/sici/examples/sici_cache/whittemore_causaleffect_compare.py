# sici/examples/sici_cache/whittemore_causaleffect_compare.py

import sympy as sp
from sici.canonical import canonicalize_ast
from sici.metrics import count_ast_nodes

# Flat formula (mimic causaleffect/whittemore)
z = sp.Symbol('z')
P_y_xz  = sp.Symbol('P(y|x,z)')
P_y2_xz = sp.Symbol("P(y'|x,z)")
P_z = sp.Symbol('P(z)')

# Typical output: 2 independent integrals (flat)
flat_formula = sp.Integral(P_y_xz * P_z, (z,)) + sp.Integral(P_y2_xz * P_z, (z,))
print("Flat formula (Causaleffect/Whittemore):")
print(flat_formula)
print("AST nodes:", count_ast_nodes(flat_formula))

# SICI-Cache: merge integrals
merged = sp.Integral((P_y_xz + P_y2_xz) * P_z, (z,))
merged_canon = canonicalize_ast(merged)
print("\nSICI-Cache merged:")
print(merged_canon)
print("AST nodes:", count_ast_nodes(merged_canon))
