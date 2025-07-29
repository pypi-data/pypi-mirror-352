# sici/examples/sici_trace/alarm_numeric.py

import os
import time
import itertools
import numpy as np
from pgmpy.readwrite import BIFReader

from sici.models import SCM, Query
from sici.compiler import compile
from sici.metrics import GLOBAL_METRICS, count_ast_nodes

HERE     = os.path.dirname(__file__)
DATA_DIR = os.path.abspath(os.path.join(HERE, "..", "data"))
BIF_PATH = os.path.join(DATA_DIR, "alarm.bif")

def build_alarm_numeric_scm(bif_path: str) -> SCM:
    """
    Load the Alarm network from a BIF file and convert to a numeric SCM
    whose conditionals are Python dicts (PMFs).
    """
    reader = BIFReader(bif_path)
    model  = reader.get_model()

    # 1) Extract graph structure
    graph = {v: list(model.get_parents(v)) for v in model.nodes()}

    # 2) Build state‐to‐int mappings
    state_map = {}
    state_names = {}
    for cpd in model.get_cpds():
        var = cpd.variable
        raw_states = cpd.state_names[var]
        mapping = {s: i for i, s in enumerate(raw_states)}
        state_map[var] = mapping
        state_names[var] = list(mapping.values())
        # ensure parents also have mappings
        for p in cpd.get_evidence() or []:
            if p not in state_map:
                raw_p_states = cpd.state_names[p]
                mp = {s: i for i, s in enumerate(raw_p_states)}
                state_map[p] = mp
                state_names[p] = list(mp.values())

    # 3) Build CPD tables as dicts
    conds = {}
    for cpd in model.get_cpds():
        var     = cpd.variable
        parents = list(cpd.get_evidence() or [])
        num_states = state_names[var]

        arr = np.array(cpd.values, dtype=float)
        if parents:
            arr = arr.reshape((len(num_states), -1))
            arr /= arr.sum(axis=0, keepdims=True)
            table = {}
            parent_states = [state_names[p] for p in parents]
            for col_idx, combo in enumerate(itertools.product(*parent_states)):
                for i, sv in enumerate(num_states):
                    key = (sv,) + combo
                    table[key] = float(arr[i, col_idx])
            label = f"P({var}|{','.join(parents)})"
        else:
            arr = arr.flatten()
            arr /= arr.sum()
            table = {sv: float(arr[i]) for i, sv in enumerate(num_states)}
            label = f"P({var})"

        conds[label] = table

    return SCM(graph=graph, conditionals=conds, state_names=state_names)

def tree_depth(expr) -> int:
    """Compute max depth of a Sympy Expr."""
    if not getattr(expr, "args", None):
        return 1
    return 1 + max(tree_depth(arg) for arg in expr.args)

def main():
    print(f"Loading Alarm BIF from {BIF_PATH!r}")
    scm = build_alarm_numeric_scm(BIF_PATH)

    # pick a root→leaf query
    roots    = [v for v, ps in scm.graph.items() if not ps]
    children = {v: [] for v in scm.graph}
    for v, ps in scm.graph.items():
        for p in ps:
            children[p].append(v)
    leaves = [v for v, cs in children.items() if not cs]

    x = roots[0]
    y = leaves[0]
    print(f"=== Alarm network experiment: do({x}) → {y} ===")

    # choose an intervention value (first state) and target state
    inter_val  = scm.state_names[x][0]
    target_val = scm.state_names[y][0]

    # --- Symbolic compile & metrics ---
    query_sym = Query(outcome=y, intervention=x)
    t0 = time.perf_counter()
    sym_tree = compile(scm, query_sym, mode="symbolic")
    t1 = time.perf_counter()

    expr  = sym_tree.to_sympy()
    ast_n = count_ast_nodes(expr)
    dag_n = GLOBAL_METRICS.dag_nodes
    depth = tree_depth(expr)
    formula = str(expr)

    print("\nSymbolic compilation:")
    print(f"  time        = {t1-t0:.4f}s")
    print(f"  AST nodes   = {ast_n}")
    print(f"  DAG nodes   = {dag_n}")
    print(f"  max depth   = {depth}")
    print(f"  formula len = {len(formula)} chars")

    # --- Numeric compile & eval ---
    query_num = Query(outcome=y, intervention=x, context={y: target_val})
    t0 = time.perf_counter()
    num_res = compile(
        scm,
        query_num,
        mode="numeric",
        intervention_value=inter_val,
        mc_samples=2000000
    )
    t1 = time.perf_counter()

    print("\nNumeric compilation + evaluation:")
    print(f"  time        = {t1-t0:.4f}s")
    print(f"P({y}={target_val} | do({x}={inter_val})) = {num_res:.4f}")

if __name__ == "__main__":
    main()
