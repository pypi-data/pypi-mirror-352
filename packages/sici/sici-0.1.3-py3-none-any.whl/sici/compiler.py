# sici/compiler.py

from __future__ import annotations
from typing import Any, Optional, Dict, List  # Critical fix
from time import perf_counter
from concurrent.futures import ThreadPoolExecutor
import sympy as sp
import numpy as np
import hashlib
import json
from scipy.integrate import nquad
from itertools import product

from sici.models import SCM, Query
from sici.trace import build_trace_graph
from sici.tree import build_expression_tree, ExpressionTree
from sici.dag import fold_and_rewrite, DAGNode
from sici.canonical import canonicalize_ast
from sici.cache import SYMBOLIC_CACHE, NUMERIC_CACHE
from sici.metrics import compute_metrics
from sici.utils import induced_ancestral_graph

# --------------------------------------------------------------------
# Helper class combining DAG and Expression Tree
# --------------------------------------------------------------------
class DAGExpressionTree(DAGNode, ExpressionTree):
    """Hybrid node combining DAG folding and expression tree."""
    def __init__(self, dag: DAGNode, expr: sp.Expr):
        super().__init__(dag.op, dag.children)
        ExpressionTree.__init__(self, expr)

# --------------------------------------------------------------------
# Stable hashing for complex objects
# --------------------------------------------------------------------
def stable_hash(obj: Any) -> str:
    """Generate stable hash for dictionaries and nested structures."""
    def _serialize(o):
        if isinstance(o, dict):
            return sorted( (k, _serialize(v)) for k, v in o.items() )
        elif isinstance(o, list):
            return [_serialize(e) for e in o]
        else:
            return str(o)
    return hashlib.sha256(json.dumps(_serialize(obj)).encode()).hexdigest()

# --------------------------------------------------------------------
# Main compile() function
# --------------------------------------------------------------------
def compile(
    scm: SCM,
    query: Query,
    *,
    mode: str = "symbolic",
    disable_canonicalization: bool = False,
    disable_dag_folding: bool = False,
    disable_rewriting: bool = False,
    use_cache: bool = True,
    intervention_value: float = 0.0,
    mc_samples: int = 2000
):
    # -------- Common pre-processing ---------------------------------
    if not isinstance(scm, SCM):
        raise TypeError("Invalid SCM instance")
    if not isinstance(query, Query):
        raise TypeError("Invalid Query instance")

    # 1) Prune to ancestral graph (preserve original for hashing)
    original_graph = scm.graph.copy()
    pruned = induced_ancestral_graph(scm.graph, query.intervention, query.outcome)
    pruned_scm = SCM(
        graph=pruned,
        conditionals=scm.conditionals,
        latent_vars=scm.latent_vars,
        state_names=scm.state_names
    )

    # ----------------------------------------------------------------
    # SYMBOLIC mode (structural cache)
    # ----------------------------------------------------------------
    if mode == "symbolic":
        # 1) Build trace graph and raw expression
        trace = build_trace_graph(pruned_scm, query)
        raw_tree = build_expression_tree(
            pruned_scm, query, trace,
            disable_canonicalization=disable_canonicalization
        )
        raw_expr = raw_tree.to_sympy()

        # 2) Apply canonicalization if enabled
        expr = canonicalize_ast(raw_expr) if not disable_canonicalization else raw_expr
        
        # 3) Generate unique cache key with full SCM signature
        scm_signature = stable_hash({
            "graph": original_graph,
            "latent": pruned_scm.latent_vars,
            "query": (query.intervention, query.outcome)
        })
        key_data = f"{scm_signature}:{expr}"
        h = hashlib.sha256(key_data.encode()).hexdigest()
        print(f"[DEBUG] Symbolic Key: {h[:8]}")  # Debug output

        if use_cache:
            cached = SYMBOLIC_CACHE.lookup(h)
            if cached is not None:
                print(f"[CACHE] Symbolic hit: {h[:8]}")
                compute_metrics(expr, cached)
                return cached

        # 4) Build optimized DAG
        t0 = perf_counter()
        dag = fold_and_rewrite(
            raw_tree,
            skip_folding=disable_dag_folding,
            skip_rewrite=disable_rewriting
        )
        tree = DAGExpressionTree(dag, expr)

        if use_cache:
            SYMBOLIC_CACHE.insert(h, tree)
            print(f"[CACHE] Symbolic insert: {h[:8]} size={len(SYMBOLIC_CACHE)}")

        compute_metrics(expr, tree, t0)
        return tree

    # ----------------------------------------------------------------
    # NUMERIC mode (result cache)
    # ----------------------------------------------------------------

    elif mode == "numeric":
        # 1) Collect all variables and their domains
        variables = sorted(pruned_scm.variables())
        cont_vars, disc_vars, domains = [], [], {}
        for v in variables:
            cond = pruned_scm.get_conditional(v)
            if callable(cond):
                cont_vars.append(v)
                # Important: set continuous variable domain to (-∞, ∞)
                domains[v] = (-np.inf, np.inf)
            elif isinstance(cond, dict):
                disc_vars.append(v)
                domains[v] = pruned_scm.state_names.get(v, [])
            else:
                raise TypeError(f"Unsupported CPD type for {v}: {type(cond)}")

        # 2) Exclude do-intervention variable
        iv = query.intervention
        cont_vars = [v for v in cont_vars if v != iv]
        disc_vars = [v for v in disc_vars if v != iv]
        if iv in domains:
            domains.pop(iv)

        # 3) Build cache key (unchanged)
        key_data = stable_hash({
            "graph": original_graph,
            "intervention": iv,
            "outcome": query.outcome,
            "value": intervention_value,
            "samples": mc_samples,
            "domains": domains,
            "context": query.context
        })
        key = hashlib.sha256(key_data.encode()).hexdigest()
        print(f"[DEBUG] Numeric Key: {key[:8]} params="
              f"value={intervention_value:.2f}, samples={mc_samples}")

        if use_cache:
            cached = NUMERIC_CACHE.lookup(key)
            if cached is not None:
                print(f"[CACHE] Numeric hit: {key[:8]}")
                return cached

        # 4) Define integrand (unchanged)
        target = query.context.get(query.outcome) if query.context else None
        is_outcome_discrete = query.outcome in disc_vars

        def integrand_full(assign):
            a = dict(assign)
            a[iv] = intervention_value
            joint = 1.0
            for v in variables:
                if v == iv:
                    continue
                cond = pruned_scm.get_conditional(v)
                parents = pruned_scm.parents_of(v)
                if callable(cond):
                    args = [a[p] for p in parents]
                    joint *= cond(a[v], *args)
                else:
                    keyp = (a[v],) + tuple(a[p] for p in parents) if parents else a[v]
                    joint *= cond.get(keyp, 0.0)
            if target is not None:
                return joint if a[query.outcome] == target else 0.0
            elif is_outcome_discrete:
                return joint
            else:
                return float(a[query.outcome]) * joint

        # 5) Integration strategy: use nquad for 1D continuous over (-∞, ∞)
        result = 0.0
        if len(cont_vars) > 1:
            total = 0.0
            for _ in range(mc_samples):
                sample = {v: np.random.randn() for v in cont_vars}
                sample.update({v: np.random.choice(domains[v]) for v in disc_vars})
                total += integrand_full(sample)
            result = total / mc_samples
        elif len(cont_vars) == 1:
            var = cont_vars[0]
            total = 0.0
            for combo in product(*(domains[v] for v in disc_vars)):
                assign = dict(zip(disc_vars, combo))
                fn = lambda x: integrand_full({**assign, var: x})
                # Important: set integration limits to (-∞, ∞)
                res, _ = nquad(fn, [( -np.inf, np.inf )])
                total += res
            result = total
        else:
            # Pure discrete part (unchanged)
            if len(disc_vars) > 8:
                total = sum(integrand_full(
                    {v: np.random.choice(domains[v]) for v in disc_vars}
                ) for _ in range(mc_samples))
                result = total / mc_samples
            else:
                total = 0.0
                for combo in product(*(domains[v] for v in disc_vars)):
                    total += integrand_full(dict(zip(disc_vars, combo)))
                result = total

        # 6) Cache and return
        if use_cache:
            NUMERIC_CACHE.insert(key, float(result))
            print(f"[CACHE] Numeric insert: {key[:8]} value={result:.4f}")
        return float(result)

    else:
        raise ValueError(f"Invalid mode: {mode}")

# --------------------------------------------------------------------
# Batch compilation
# --------------------------------------------------------------------
def batch_compile(queries, **kwargs):
    """Batch compile queries with ThreadPool."""
    with ThreadPoolExecutor() as ex:
        return [ex.submit(compile, **q, **kwargs).result() for q in queries]
