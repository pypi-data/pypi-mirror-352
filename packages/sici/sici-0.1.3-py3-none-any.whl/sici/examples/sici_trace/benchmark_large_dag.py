# examples/sici_trace/benchmark_large_dag.py

import time
import random
import csv
import networkx as nx
import sympy as sp
import concurrent.futures

from sici.models import SCM, Query
from sici.compiler import compile
from sici.metrics import GLOBAL_METRICS, count_ast_nodes

def random_dag(n, p, seed=None):
    """
    Generate an n-node random DAG with edge probability p by
    first drawing a random permutation of the n nodes, then
    only adding edges from earlier→later in that permutation.
    """
    rng = random.Random(seed)
    nodes = list(range(n))
    rng.shuffle(nodes)  # this is our topological ordering
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    for i in range(n):
        for j in range(i+1, n):
            if rng.random() < p:
                u, v = nodes[i], nodes[j]
                G.add_edge(u, v)
    return G

def make_cpds(G: nx.DiGraph):
    """Create a dict of symbolic CPDs P(v|pa) or P(v) for each node."""
    cpds = {}
    for v in G.nodes:
        parents = list(G.predecessors(v))
        v_str = str(v)
        parents_str = [str(p) for p in parents]
        if parents_str:
            label = f"P({v_str}|{','.join(parents_str)})"
            sym   = sp.Symbol(f"P_{v_str}_given_{'_'.join(parents_str)}", commutative=False)
        else:
            label = f"P({v_str})"
            sym   = sp.Symbol(f"P_{v_str}", commutative=False)
        cpds[label] = sym
    return cpds

def tree_depth(expr) -> int:
    """Recursively compute the max depth of a SymPy expression tree."""
    if not getattr(expr, "args", None):
        return 1
    return 1 + max(tree_depth(arg) for arg in expr.args)

def safe_compile(scm, qry, timeout=5.0):
    """
    Run symbolic compile in a thread, bail out after `timeout` seconds.
    We disable cache here to match paper benchmark.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        fut = ex.submit(
            compile,
            scm,
            qry,
            mode="symbolic",
            use_cache=False      # 禁用缓存
        )
        try:
            return fut.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            return None

def run_benchmark(
    node_sizes   = [500],   # 仅 500 节点
    densities    = [0.02],  # 仅 p=0.02
    replicates   = 5,       # 重复 5 次
    timeout      = 5.0,
    out_csv      = "large_dag_benchmark.csv"
):
    print(f"=== Benchmark on random DAG (n={node_sizes[0]}, p={densities[0]}) ===")
    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "n_nodes","density","replicate",
            "compile_time_s","ast_nodes","dag_nodes","max_depth","formula_len"
        ])
        writer.writeheader()

        n = node_sizes[0]
        p = densities[0]
        for rep in range(1, replicates+1):
            # 1) Build random DAG
            G = random_dag(n, p, seed=rep*123)
            graph = {
                str(v): [str(u) for u in G.predecessors(v)]
                for v in G.nodes
            }

            # 2) Build symbolic SCM
            cpds = make_cpds(G)
            scm  = SCM(graph=graph, conditionals=cpds)

            # 3) Pick a random root → leaf causal pair
            roots  = [str(v) for v,d in G.in_degree()  if d==0]
            leaves = [str(v) for v,d in G.out_degree() if d==0]
            if not roots or not leaves:
                continue
            x = random.choice(roots)
            y = random.choice(leaves)
            qry = Query(outcome=y, intervention=x)

            # 4) Compile with timeout guard (cache disabled)
            t0 = time.perf_counter()
            tree = safe_compile(scm, qry, timeout=timeout)
            t1 = time.perf_counter()
            elapsed = t1 - t0

            if tree is None:
                print(f"[rep={rep}] TIMEOUT")
                writer.writerow({
                    "n_nodes":       n,
                    "density":       p,
                    "replicate":     rep,
                    "compile_time_s":"timeout",
                    "ast_nodes":     None,
                    "dag_nodes":     None,
                    "max_depth":     None,
                    "formula_len":   None
                })
                continue

            # 5) Gather metrics
            expr    = tree.to_sympy()
            ast_n   = count_ast_nodes(expr)
            dag_n   = GLOBAL_METRICS.dag_nodes
            depth   = tree_depth(expr)
            formula = str(expr)

            print(f"[rep={rep}] time={elapsed:.4f}s  AST={ast_n}  "
                  f"DAG={dag_n}  depth={depth}  len={len(formula)}")
            writer.writerow({
                "n_nodes":       n,
                "density":       p,
                "replicate":     rep,
                "compile_time_s":f"{elapsed:.6f}",
                "ast_nodes":     ast_n,
                "dag_nodes":     dag_n,
                "max_depth":     depth,
                "formula_len":   len(formula)
            })

    print(f"\nResults written to {out_csv}")

if __name__ == "__main__":
    run_benchmark()
