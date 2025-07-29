from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from .models import SCM, Query
from .identity_checker import analyze_paths  

@dataclass
class TraceNode:
    label: str
    node_type: str  # "distribution", "operator", "integral"
    scope: Optional[str] = None

@dataclass
class TraceGraph:
    nodes: List[TraceNode] = field(default_factory=list)
    edges: List[Tuple[str, str]] = field(default_factory=list)
    identification_result: Optional[str] = None  # ✅ 可以是 backdoor / frontdoor / unknown

    def add_node(self, node: TraceNode):
        self.nodes.append(node)

    def add_edge(self, src_label: str, dst_label: str):
        self.edges.append((src_label, dst_label))

    def get_distribution_labels(self) -> List[str]:
        return [n.label for n in self.nodes if n.node_type == "distribution"]

# --------------------------------------------------------------
def build_trace_graph(scm: SCM, query: Query, check_identity: bool = True) -> TraceGraph:
    """
    Constructs an annotated trace graph from an SCM and causal query.
    """
    graph = scm.graph
    outcome = query.outcome
    intervention = query.intervention

    trace = TraceGraph()
    visited = set()

    # --- Step 1: Quick DFS to select relevant distributions ---
    def dfs(node):
        if node in visited:
            return
        visited.add(node)

        # # sort parents so that P(node|…) labels always come out in a canonical order
        # raw_parents = graph.get(node, [])
        # try:
        #     # if your node names are integer‐strings, sort by int for natural order
        #     parents = sorted(raw_parents, key=lambda x: int(x))
        # except ValueError:
        #     # otherwise sort lexicographically
        #     parents = sorted(raw_parents)
        # preserve the user‐provided parent ordering so labels line up with SCM.conditionals
        parents = graph.get(node, [])

        if parents:
            label = f"P({node}|{','.join(parents)})"
        else:
            label = f"P({node})"
        trace.add_node(TraceNode(label=label, node_type="distribution"))

        for parent in parents:
            dfs(parent)

    dfs(outcome)

    # --- Step 2: Build symbolic operation structure ---
    multiply_node = TraceNode(label="×", node_type="operator")
    trace.add_node(multiply_node)
    for node_label in trace.get_distribution_labels():
        trace.add_edge(node_label, multiply_node.label)

     # --- Step 2b: integrate over the do‐variable ---
    int_label = f"∫ {intervention}"
    int_node  = TraceNode(label=int_label, node_type="integral", scope=intervention)
    trace.add_node(int_node)
    trace.add_edge(multiply_node.label, int_label)

    # --- Step 3: Identification checking ---
    if check_identity:
        trace.identification_result = analyze_paths(
            graph, outcome, intervention,
            latent_nodes=getattr(scm, "latent_nodes", set())
        )
    else:
        trace.identification_result = "unknown"
        
    trace.adjustment_set = graph.get(intervention, [])

    return trace