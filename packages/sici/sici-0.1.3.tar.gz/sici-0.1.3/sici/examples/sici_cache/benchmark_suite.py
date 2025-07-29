#!sici/examples/benchmark_suite.py
"""
SICI-Cache Benchmark Suite (Enhanced Version, Print AST and DAG Node Counts)

1. Symbolic mode: Test AST compression ratio and subexpression cache hit rate, and print node counts.
2. Numeric mode: Test end-to-end speedup brought by symbolic cache.
3. For Random DAG(15), run with multiple random seeds, report mean and standard deviation.
"""

import numpy as np
from time import perf_counter
from collections import namedtuple
from scipy.stats import norm
import random
from sici.models import SCM, Query
from sici.compiler import compile
from sici.metrics import GLOBAL_METRICS, count_ast_nodes
from sici.cache import SYMBOLIC_CACHE, NUMERIC_CACHE

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ---------------------------- Benchmark Configuration ------------------------------
Bench = namedtuple("Bench", "name graph sym_scm num_scm q_sym q_num")

def make_numeric_scm(graph):
    conds = {}
    for v, parents in graph.items():
        key = f"P({v}|{','.join(parents)})" if parents else f"P({v})"
        if parents:
            def cpd_factory(ps):
                return lambda x, *args: norm.pdf(x - sum(args), 0, 1)
            conds[key] = cpd_factory(parents)
        else:
            conds[key] = lambda x: norm.pdf(x, 0, 1)
    return SCM(graph.copy(), conds)

def generate_random_dag(n, max_parents=3, seed=None):
    rng = np.random.default_rng(seed)
    vars_ = [f"V{i}" for i in range(n)]
    graph = {}
    for i, v in enumerate(vars_):
        if i == 0:
            graph[v] = []
        else:
            choices = vars_[:i]
            k = int(rng.integers(0, min(len(choices), max_parents) + 1))
            graph[v] = rng.choice(choices, size=k, replace=False).tolist() if k > 0 else []
    return graph

def load_benchmarks():
    data = [
        ("Backdoor (3 conf.)",
         {"Z1": [], "Z2": [], "Z3": [], "X": ["Z1", "Z2", "Z3"], "Y": ["X", "Z1", "Z2", "Z3"]},
         "Y", "X"),
        ("Frontdoor (1 med.)",
         {"X": [], "M": ["X"], "Y": ["M"]},
         "Y", "X"),
        ("Layered DAG",
         {"U": [], "Z": ["U"], "X": ["Z"], "Y": ["X", "Z", "U"]},
         "Y", "X"),
        ("Random DAG (15)",
         None,  # Generated in run_main
         "V14", "V0"),
        ("Instrumental",
         {"Z": [], "X": ["Z"], "Y": ["X"]},
         "Y", "X"),
        ("UnobsConfound",
         {"U": [], "X": ["U"], "Y": ["U"]},
         "Y", "X")
    ]
    benches = []
    for name, graph, y, x in data:
        if graph is not None:
            sym_scm = SCM(graph.copy())
            num_scm = make_numeric_scm(graph)
            ctx_id = np.random.randint(1000, 9999)
            q_sym = Query(y, x, context={"test_id": ctx_id})
            q_num = Query(y, x, context={"test_id": ctx_id})
            benches.append(Bench(name, graph, sym_scm, num_scm, q_sym, q_num))
        else:
            benches.append(Bench(name, None, None, None, y, x))
    return benches

# ---------------------------- Print Format ------------------------------
def print_header():
    print("-" * 100)
    print(f"{'Benchmark':<22} | {'AST nodes':>9} | {'DAG nodes':>9} | {'Reduction':>9} | {'Cache Hit':>9} | {'Num.Speed(×)':>12}")
    print("-" * 100)

def print_row(name, ast_n, dag_n, red, hit, speed, red_std=None, hit_std=None, speed_std=None):
    if red_std is None:
        print(f"{name:<22} | {ast_n:>9d} | {dag_n:>9d} | {red:>8.1%} | {hit:>8.1%} | {speed:>12.2f}")
    else:
        # for Random DAG with std
        print(f"{name:<22} | {ast_n:>9s} | {dag_n:>9s} | "
              f"{red:>6.1%}±{red_std:.1%} | {hit:>6.1%}±{hit_std:.1%} | {speed:>6.2f}±{speed_std:.2f}")

# ---------------------------- Test Execution ------------------------------
def run_main(benches, random_repeats=10, random_seed_base=42):
    print_header()
    for b in benches:
        if b.name == "Random DAG (15)":
            reds, hits, speeds = [], [], []
            ast_ns, dag_ns = [], []
            for i in range(random_repeats):
                # Reset cache and metrics
                GLOBAL_METRICS.reset()
                SYMBOLIC_CACHE._tbl.clear()
                NUMERIC_CACHE._tbl.clear()
                SYMBOLIC_CACHE.reset_stats()
                NUMERIC_CACHE.reset_stats()

                graph = generate_random_dag(15, max_parents=3, seed=random_seed_base + i)
                sym_scm = SCM(graph.copy())
                num_scm = make_numeric_scm(graph)
                y_label, x_label = b.q_sym, b.q_num

                # Symbolic mode: compile twice
                compile(sym_scm, Query(y_label, x_label), mode="symbolic", use_cache=True)
                compile(sym_scm, Query(y_label, x_label), mode="symbolic", use_cache=True)
                ast_ns.append(GLOBAL_METRICS.ast_nodes)
                dag_ns.append(GLOBAL_METRICS.dag_nodes)
                reds.append(GLOBAL_METRICS.reduction)
                hits.append(SYMBOLIC_CACHE.hit_ratio())

                # Numeric mode
                rng = np.random.default_rng(random_seed_base + i)
                ivalue = rng.uniform(-1.0, 1.0)
                samples = rng.integers(1000, 5000)

                # --- baseline: full pipeline without cache
                t0 = perf_counter()
                compile(sym_scm, Query(y_label, x_label),    mode="symbolic", use_cache=False)
                compile(num_scm, Query(y_label, x_label,
                        context={"intervention_value": ivalue}),
                    mode="numeric", use_cache=False,
                    intervention_value=ivalue, mc_samples=samples)
                t_base = perf_counter() - t0

                # --- optimized: reuse symbolic cache, numeric integral still runs
                t0 = perf_counter()
                compile(sym_scm, Query(y_label, x_label),    mode="symbolic", use_cache=True)
                compile(num_scm, Query(y_label, x_label,
                        context={"intervention_value": ivalue}),
                    mode="numeric", use_cache=False,
                    intervention_value=ivalue, mc_samples=samples)
                t_opt = perf_counter() - t0

                speeds.append(t_base / t_opt if t_opt > 0 else float("inf"))

            # Compute mean and std
            avg_r, std_r = np.mean(reds), np.std(reds)
            avg_h, std_h = np.mean(hits), np.std(hits)
            avg_s, std_s = np.mean(speeds), np.std(speeds)
            avg_ast, std_ast = np.mean(ast_ns), np.std(ast_ns)
            avg_dag, std_dag = np.mean(dag_ns), np.std(dag_ns)
            ast_str = f"{avg_ast:.1f}±{std_ast:.1f}"
            dag_str = f"{avg_dag:.1f}±{std_dag:.1f}"

            print_row(
                b.name,
                ast_str, dag_str,
                avg_r, avg_h, avg_s,
                std_r, std_h, std_s
            )

        else:
            # Single scenario
            GLOBAL_METRICS.reset()
            SYMBOLIC_CACHE._tbl.clear()
            NUMERIC_CACHE._tbl.clear()
            SYMBOLIC_CACHE.reset_stats()
            NUMERIC_CACHE.reset_stats()

            # Symbolic mode: compile twice
            compile(b.sym_scm, b.q_sym, mode="symbolic", use_cache=True)
            compile(b.sym_scm, b.q_sym, mode="symbolic", use_cache=True)
            ast_n = GLOBAL_METRICS.ast_nodes
            dag_n = GLOBAL_METRICS.dag_nodes
            red = GLOBAL_METRICS.reduction
            hit = SYMBOLIC_CACHE.hit_ratio()

            # Numeric mode
            rng = np.random.default_rng()
            ivalue = rng.uniform(-1.0, 1.0)
            samples = rng.integers(1000, 5000)

            # baseline
            t0 = perf_counter()
            compile(b.sym_scm, b.q_sym, mode="symbolic", use_cache=False)
            compile(b.num_scm,
                    Query(b.q_num.outcome, b.q_num.intervention,
                          context={"intervention_value": ivalue}),
                    mode="numeric", use_cache=False,
                    intervention_value=ivalue, mc_samples=samples)
            t_base = perf_counter() - t0

            # optimized
            t0 = perf_counter()
            compile(b.sym_scm, b.q_sym, mode="symbolic", use_cache=True)
            compile(b.num_scm,
                    Query(b.q_num.outcome, b.q_num.intervention,
                          context={"intervention_value": ivalue}),
                    mode="numeric", use_cache=False,
                    intervention_value=ivalue, mc_samples=samples)
            t_opt = perf_counter() - t0

            speed = t_base / t_opt if t_opt > 0 else float("inf")
            print_row(b.name, ast_n, dag_n, red, hit, speed)

if __name__ == "__main__":
    benches = load_benchmarks()
    run_main(benches)
