# sici/examples/sici_trace/hepar2_experiment.py

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
BIF_PATH = os.path.join(DATA_DIR, "hepar2.bif")


def tree_depth(expr) -> int:
    if not getattr(expr, "args", None):
        return 1
    return 1 + max(tree_depth(arg) for arg in expr.args)


def load_hepar2_graph_and_tables(bif_path: str):
    """
    Read Hepar2 from a BIF, return (graph, tables, state_names).
    - graph: Dict[node, List[parent]]
    - tables: Dict["P(X|...)" or "P(X)", PMF dict]
    - state_names: Dict[node, List[int]] for numeric enumeration
    """
    reader = BIFReader(bif_path)
    model  = reader.get_model()

    graph = {v: list(model.get_parents(v)) for v in model.nodes()}

    # build state mapping
    state_map   = {}
    state_names = {}
    for cpd in model.get_cpds():
        var       = cpd.variable
        raw_states = cpd.state_names[var]
        mapping   = {s: i for i, s in enumerate(raw_states)}
        state_map[var]   = mapping
        state_names[var] = list(mapping.values())
    # now build the CPT tables
    tables = {}
    for cpd in model.get_cpds():
        var     = cpd.variable
        parents = list(cpd.get_evidence() or [])
        arr     = np.array(cpd.values, dtype=float)
        if parents:
            # reshape & normalize columns
            arr = arr.reshape((len(state_names[var]), -1))
            arr /= arr.sum(axis=0, keepdims=True)
            parent_states = [state_names[p] for p in parents]
            table = {}
            for col_idx, combo in enumerate(itertools.product(*parent_states)):
                for i, sv in enumerate(state_names[var]):
                    key = (sv,) + combo
                    table[key] = float(arr[i, col_idx])
            label = f"P({var}|{','.join(parents)})"
        else:
            # root node
            arr = arr.flatten()
            arr /= arr.sum()
            table = {sv: float(arr[i]) for i, sv in enumerate(state_names[var])}
            label = f"P({var})"
        tables[label] = table

    return graph, tables, state_names


def main():
    print(f"Loading Hepar2 BIF from {BIF_PATH!r}")
    graph, tables, state_names = load_hepar2_graph_and_tables(BIF_PATH)

    # pick any root→leaf
    roots = [v for v, ps in graph.items() if not ps]
    children = {v: [] for v in graph}
    for v, ps in graph.items():
        for p in ps:
            children[p].append(v)
    leaves = [v for v, cs in children.items() if not cs]

    x = roots[0]
    y = leaves[0]
    print(f"\n=== Hepar2 experiment: do({x}) → {y} ===")

    # 1) Symbolic compile over auto-generated Sympy symbols
    sym_scm = SCM(graph=graph, conditionals=None)
    query_sym = Query(outcome=y, intervention=x)

    t0 = time.perf_counter()
    tree = compile(sym_scm, query_sym, mode="symbolic")
    t1 = time.perf_counter()

    expr  = tree.to_sympy()
    ast_n = count_ast_nodes(expr)
    dag_n = GLOBAL_METRICS.dag_nodes
    depth = tree_depth(expr)
    formula = str(expr)

    print("Symbolic compile results:")
    print(f"  time        = {t1-t0:.4f}s")
    print(f"  AST nodes   = {ast_n}")
    print(f"  DAG nodes   = {dag_n}")
    print(f"  max depth   = {depth}")
    print(f"  formula len = {len(formula)} chars")

    # 2) Numeric compile & evaluation
    #    use the real CPT tables and state_names
    num_scm = SCM(
        graph=graph,
        conditionals=tables,
        state_names=state_names
    )
    # choose the first state for intervention and target
    inter_val  = state_names[x][0]
    target_val = state_names[y][0]
    query_num  = Query(outcome=y, intervention=x, context={y: target_val})

    print("\nNumeric evaluation (with Monte Carlo / nquad):")
    num = compile(
        num_scm,
        query_num,
        mode="numeric",
        intervention_value=inter_val,
        mc_samples=5000
    )
    print(f"P({y}={target_val} | do({x}={inter_val})) = {num:.4f}")


if __name__ == "__main__":
    main()
