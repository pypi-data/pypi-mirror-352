# sici/ast_generator.py

import sympy as sp
from typing import Any
from sici.models import SCM, Query

class ASTGenerator:
    def __init__(self, scm: SCM):
        self.scm = scm
        self.children = {v: [] for v in scm.graph}
        for child, parents in scm.graph.items():
            for p in parents:
                self.children.setdefault(p, []).append(child)

    def generate(self, case_type: str, query: Query) -> sp.Expr:
        if case_type == "backdoor":
            return self._backdoor(query)
        elif case_type == "frontdoor":
            return self._frontdoor(query)
        elif case_type == "instrumental":
            return self._instrumental(query)
        elif case_type == "unobserved_confounding":
            return self._unobserved_confounding(query)
        elif case_type == "counterfactual":
            return self._counterfactual(query)
        else:
            raise ValueError(f"Unknown case type: {case_type}")

    def _backdoor(self, query: Query) -> sp.Expr:
        x, y = query.intervention, query.outcome
        Zs = list(self.scm.graph.get(x, []))
        if not Zs:
            return sp.Symbol(f"P({y}|{x})", commutative=False)
        cond_y = sp.Symbol(f"P({y}|{x},{','.join(Zs)})", commutative=False)
        cond_x = sp.Symbol(f"P({x}|{','.join(Zs)})", commutative=False)
        p_zs = [sp.Symbol(f"P({z})", commutative=False) for z in Zs]
        integrand = cond_y * cond_x
        for pz in p_zs:
            integrand *= pz
        expr = integrand
        for z in Zs:
            z_sym = sp.Symbol(z)
            expr = sp.Integral(expr, (z_sym, -sp.oo, sp.oo))
        return expr

    def _frontdoor(self, query: Query) -> sp.Expr:
        x, y = query.intervention, query.outcome
        # 所有符合条件的M
        Ms = [m for m in self.children.get(x, []) if m in self.scm.graph.get(y, [])]
        if not Ms:
            raise ValueError(f"No frontdoor mediator found between '{x}' and '{y}'")
        cond_y = sp.Symbol(f"P({y}|{','.join(Ms+[x])})", commutative=False)
        p_x = sp.Symbol(f"P({x})", commutative=False)
        p_m_given_x = [sp.Symbol(f"P({m}|{x})", commutative=False) for m in Ms]
        m_product = sp.Mul(*p_m_given_x) if p_m_given_x else 1
        inner = sp.Integral(cond_y * p_x, (sp.Symbol(x), -sp.oo, sp.oo))
        expr = m_product * inner
        for m in Ms:
            m_sym = sp.Symbol(m)
            expr = sp.Integral(expr, (m_sym, -sp.oo, sp.oo))
        return expr

    def _instrumental(self, query: Query) -> sp.Expr:
        x, y = query.intervention, query.outcome
        Zs = list(self.scm.graph.get(x, []))
        if not Zs:
            raise ValueError(f"No instrumental variable found for '{x}'")
        cond_y = sp.Symbol(f"P({y}|{x},{','.join(Zs)})", commutative=False)
        cond_x = sp.Symbol(f"P({x}|{','.join(Zs)})", commutative=False)
        p_zs = [sp.Symbol(f"P({z})", commutative=False) for z in Zs]
        integrand = cond_y * cond_x
        for pz in p_zs:
            integrand *= pz
        # limits: 先所有Z再X（和 textbook 一致）
        limits = [(sp.Symbol(z), -sp.oo, sp.oo) for z in Zs]
        limits.append((sp.Symbol(x), -sp.oo, sp.oo))
        expr = sp.Integral(integrand, *limits)
        return expr

    def _unobserved_confounding(self, query: Query) -> sp.Expr:
        if not self.scm.latent_vars:
            raise ValueError("SCM has no latent variables for unobserved confounding case.")
        u = next(iter(self.scm.latent_vars))
        pu = sp.Symbol(f"P({u})", commutative=False)
        return sp.Mul(
            sp.Symbol("beta", commutative=False),
            sp.Integral(pu, (sp.Symbol(u), -sp.oo, sp.oo)),
            evaluate=False
        )

    def _counterfactual(self, query: Query) -> sp.Expr:
        if not self.scm.latent_vars:
            raise ValueError("SCM has no latent variables for counterfactual case.")
        u = next(iter(self.scm.latent_vars))
        cf = sp.Symbol(
            f"P({query.outcome}_x|{query.intervention}=x,{u})",
            commutative=False
        )
        pu = sp.Symbol(f"P({u})", commutative=False)
        return sp.Integral(
            sp.Mul(cf, pu, evaluate=False),
            (sp.Symbol(u), -sp.oo, sp.oo)
        )
