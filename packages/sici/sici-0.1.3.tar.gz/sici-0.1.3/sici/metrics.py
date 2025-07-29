# sici/metrics.py

"""
Metric helpers for SICI-Cache experiments.
"""

from __future__ import annotations
from dataclasses import dataclass
import sympy as sp
from typing import Any
from time import perf_counter

# Modify import statement: remove GLOBAL_CACHE, use SYMBOLIC_CACHE instead
from sici.cache import SYMBOLIC_CACHE  # New
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SICI")

# ----------------------------------------------------------------------
# AST size --------------------------------------------------------------
# ----------------------------------------------------------------------
def count_ast_nodes(expr: sp.Expr) -> int:
    """DFS to count number of nodes in the expression AST"""
    if not expr.args:
        return 1
    return 1 + sum(count_ast_nodes(a) for a in expr.args)

# ----------------------------------------------------------------------
# Metric container ------------------------------------------------------
# ----------------------------------------------------------------------
@dataclass
class Metrics:
    ast_nodes: int      = 0
    dag_nodes: int      = 0
    reduction: float    = 0.0
    cache_hit_ratio: float = 0.0  # Hit ratio using symbolic cache
    opt_time: float     = 0.0
    
    def reset(self) -> None:
        self.ast_nodes = 0
        self.dag_nodes = 0
        self.reduction = 0.0
        self.cache_hit_ratio = 0.0
        self.opt_time = 0.0

    def __str__(self) -> str:
        return (f"[Metrics] nodes↓ {self.reduction:.2%} "
                f"(AST {self.ast_nodes} → DAG {self.dag_nodes}), "
                f"cache hit {self.cache_hit_ratio:.2%}, "
                f"opt_time {self.opt_time:.4f}s")

GLOBAL_METRICS = Metrics()  # Global metrics using symbolic cache

# ----------------------------------------------------------------------
# Main logic ------------------------------------------------------------
# ----------------------------------------------------------------------
def compute_metrics(
    orig_expr: sp.Expr,
    dag_root: Any,
    start_time: float = None
) -> Metrics:
    global GLOBAL_METRICS
    GLOBAL_METRICS.ast_nodes = count_ast_nodes(orig_expr)
    GLOBAL_METRICS.dag_nodes = getattr(dag_root, "size", lambda: 0)()
    GLOBAL_METRICS.reduction = 1 - GLOBAL_METRICS.dag_nodes / GLOBAL_METRICS.ast_nodes
    # Hit ratio using symbolic cache
    GLOBAL_METRICS.cache_hit_ratio = SYMBOLIC_CACHE.hit_ratio()  # Modified
    if start_time is not None:
        GLOBAL_METRICS.opt_time = perf_counter() - start_time
    logger.debug(str(GLOBAL_METRICS))
    return GLOBAL_METRICS
