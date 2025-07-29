# sici/dag.py

import hashlib
from typing import Any, List, Dict
import sympy as sp

class DAGNode:
    """
    Represents a node in an expression DAG. Now each node also carries:
      - expr: the SymPy sub-expression this node represents
      - args: alias for children, so rewrite.py can iterate over node.args
    """
    def __init__(self, op: Any, children: List["DAGNode"] = None, expr: sp.Expr = None):
        self.op = op
        self.children = children or []
        self.expr = expr
        # for rewrite.py compatibility
        self.args = self.children
        self.structural_hash = self._compute_hash()
        self._size = None

    def _compute_hash(self) -> str:
        h = hashlib.sha256()
        h.update(str(self.op).encode())
        for child in self.children:
            h.update(child.structural_hash.encode())
        return h.hexdigest()

    def size(self) -> int:
        """Compute the total number of unique nodes in the DAG."""
        if self._size is None:
            seen = set()
            stack = [self]
            count = 0
            while stack:
                node = stack.pop()
                if id(node) in seen:
                    continue
                seen.add(id(node))
                count += 1
                stack.extend(node.children)
            self._size = count
        return self._size


def fold_and_rewrite(
    expr_tree: Any,
    *,
    skip_folding: bool = False,
    skip_rewrite: bool = False,
) -> DAGNode:
    """
    Convert an ExpressionTree into a DAGNode, do folding and then rewriting.
    """

    # 1) Build initial DAG with expr attached to each node
    def expr_to_dag(expr: sp.Expr) -> DAGNode:
        node_map: Dict[int, DAGNode] = {}
        stack = [(expr, False)]
        while stack:
            e, done = stack.pop()
            if done:
                # children already processed
                if isinstance(e, sp.Integral):
                    body = node_map[id(e.function)]
                    var_tuple = tuple(sorted(e.variables, key=lambda x: x.name))
                    node = DAGNode(('int', var_tuple), [body], expr=e)
                elif isinstance(e, sp.Mul):
                    children = [node_map[id(arg)] for arg in e.args]
                    node = DAGNode('mul', children, expr=e)
                else:
                    node = DAGNode(e, [], expr=e)
                node_map[id(e)] = node
            else:
                # push back after children
                stack.append((e, True))
                for arg in e.args:
                    stack.append((arg, False))
        return node_map[id(expr)]

    root = expr_to_dag(expr_tree.root)

    # 2) Fold identical subtrees
    if not skip_folding:
        cache: Dict[str, DAGNode] = {}
        def _fold(node: DAGNode) -> DAGNode:
            if node.structural_hash in cache:
                return cache[node.structural_hash]
            # first fold children
            folded_children = [ _fold(c) for c in node.children ]
            # create a new node with same op, folded children, AND same expr
            new_node = DAGNode(node.op, folded_children, expr=node.expr)
            cache[new_node.structural_hash] = new_node
            return new_node
        root = _fold(root)

    # 3) Rewrite in place
    if not skip_rewrite:
        from sici.rewrite import apply_rewrites
        root = apply_rewrites(root)

    return root
