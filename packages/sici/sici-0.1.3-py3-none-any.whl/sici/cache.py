#sici/cache.py
"""
Global expression-cache utility for SICI-Cache.
Separate caches for symbolic and numeric compilation paths.
"""

from __future__ import annotations
from collections import OrderedDict
from threading import Lock
from typing import Dict, Optional

# DAGNode is the compiled DAG for a subexpression
from sici.dag import DAGNode

class ExpressionCache:
    """
    Lightweight LRU cache for expression nodes.
    
    Attributes:
        capacity: Max entries before eviction (None = unlimited)
        _tbl: OrderedDict storing cached nodes
        _lock: Thread safety lock
        _lookup_count: Total cache queries
        _hits: Successful lookups
        _misses: Failed lookups
    """
    def __init__(self, capacity: Optional[int] = None) -> None:
        self.capacity = capacity
        self._tbl: Dict[str, DAGNode] = OrderedDict()
        self._lock = Lock()
        self._lookup_count = 0
        self._hits = 0
        self._misses = 0

    def lookup(self, h: str) -> Optional[DAGNode]:
        """Try to retrieve a cached DAGNode by hash."""
        with self._lock:
            self._lookup_count += 1
            node = self._tbl.get(h)
            if node:
                self._hits += 1
                self._tbl.move_to_end(h)  # Mark as recently used
                return node
            self._misses += 1
            return None

    def insert(self, h: str, node: DAGNode) -> None:
        """Insert a new node, evicting LRU if over capacity."""
        with self._lock:
            if self.capacity and len(self._tbl) >= self.capacity:
                self._tbl.popitem(last=False)  # Remove least recently used
            self._tbl[h] = node

    def hit_ratio(self) -> float:
        """Calculate cache hit rate."""
        return self._hits / self._lookup_count if self._lookup_count else 0.0

    def reset_stats(self) -> None:
        """Reset performance counters."""
        with self._lock:
            self._lookup_count = 0
            self._hits = 0
            self._misses = 0

    def __len__(self) -> int:
        """Current number of cached entries."""
        return len(self._tbl)

    def __repr__(self) -> str:
        status = f"<ExpressionCache size={len(self)}"
        if self.capacity:
            status += f"/{self.capacity}"
        status += f", hits={self._hits}, misses={self._misses}>"
        return status

# -------------------------------------------------------------------
# Initialized cache instances (exported)
# -------------------------------------------------------------------
SYMBOLIC_CACHE = ExpressionCache(capacity=1000)  # 符号编译专用缓存
NUMERIC_CACHE = ExpressionCache(capacity=500)    # 数值计算专用缓存

# Explicit exports
__all__ = ['ExpressionCache', 'SYMBOLIC_CACHE', 'NUMERIC_CACHE']