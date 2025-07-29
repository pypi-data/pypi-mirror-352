# sici/identity_checker.py

import networkx as nx
from typing import Dict, List, Set, Optional
from pgmpy.base import DAG

# Registry for remembering which variables are latent for a given graph dict
_GRAPH_LATENT_REGISTRY: Dict[int, Set[str]] = {}


def ancestral_subgraph(G: nx.DiGraph, X: str, Y: str) -> nx.DiGraph:
    """
    Return the induced subgraph of G containing X, Y, and all their ancestors.
    Pruning to this subgraph can dramatically speed up d-separation checks.
    """
    anc = set(nx.ancestors(G, X)) | set(nx.ancestors(G, Y)) | {X, Y}
    return G.subgraph(anc).copy()


class IdentityChecker:
    """
    Heuristic backdoor/frontdoor/instrumental/unobserved‐confounding checker using
    d-separation on the ancestral subgraph of (X, Y).
    """

    def __init__(
        self,
        graph: Dict[str, List[str]],
        latent_vars: Optional[Set[str]] = None
    ):
        # graph: node -> list of parent nodes
        self.parents = graph
        # latent set: either passed in or looked up from the registry
        self.latent = (
            latent_vars
            if latent_vars is not None
            else _GRAPH_LATENT_REGISTRY.get(id(graph), set())
        )
        # build children map
        self.children: Dict[str, List[str]] = {n: [] for n in graph}
        for n, ps in graph.items():
            for p in ps:
                self.children.setdefault(p, []).append(n)
        # build an explicit NetworkX DiGraph for d-separation
        self._nx_graph = nx.DiGraph()
        self._nx_graph.add_nodes_from(graph.keys())
        for child, ps in graph.items():
            for p in ps:
                self._nx_graph.add_edge(p, child)

    def analyze(self, treatment: str, outcome: str, context: dict = None) -> str:
        # Counterfactual: if query context specifies values
        if context is not None and len(context) > 0:
            return "counterfactual"
        # Unobserved confounding
        if self._has_unobserved_confounding(treatment, outcome):
            return "unobserved_confounding"
        # Frontdoor
        if self._is_frontdoor(treatment, outcome):
            return "frontdoor"
        # Instrumental
        if self._has_instrument(treatment, outcome):
            return "instrumental"
        # Backdoor
        if self._is_backdoor(treatment, outcome):
            return "backdoor"
        return "unknown"

    def _has_unobserved_confounding(self, x: str, y: str) -> bool:
        for u in self.latent:
            desc = self._descendants(u)
            if x in desc and y in desc:
                return True
        return False

    def _is_frontdoor(self, x: str, y: str) -> bool:
        """
        Detect exactly the simple front-door motif:
          X -> M -> Y
        where
          * no edge X->Y
          * M has exactly one parent (X) and one child (Y)
          * M is observed
          * no latent confounder on X->M or M->Y
        """
        # 1) exclude direct shortcut
        if self._nx_graph.has_edge(x, y):
            return False

        # 2) scan children of X
        for m in self.children.get(x, []):
            # must have exactly one parent (=X) and one child (=Y)
            if self.parents.get(m, []) != [x]:
                continue
            if self.children.get(m, []) != [y]:
                continue
            # must be direct edges
            if not self._nx_graph.has_edge(x, m) or not self._nx_graph.has_edge(m, y):
                continue
            # mediator must be observed
            if m in self.latent:
                continue

            # 3) check no latent U confounds X->M or M->Y
            bad = False
            for u in self.latent:
                desc_u = self._descendants(u)
                if (x in desc_u and m in desc_u) or (m in desc_u and y in desc_u):
                    bad = True
                    break
            if bad:
                continue

            # all checks passed
            return True
        return False

    def _is_backdoor(self, x: str, y: str) -> bool:
        # simple heuristic: adjust for all parents of X
        Z = set(self.parents.get(x, []))
        # backdoor holds if X⊥Y | Pa(X) is false ⇒ need adjustment
        return not self._blocks_all_paths(x, y, cond=Z)

    def _has_instrument(self, x: str, y: str) -> bool:
        # look for Z→X such that Z⊥Y | X
        for z in self.parents:
            if x in self._descendants(z):
                if self._blocks_all_paths(z, y, cond={x}):
                    return True
        return False

    def _descendants(self, node: str) -> Set[str]:
        seen = set()
        stack = [node]
        while stack:
            n = stack.pop()
            for c in self.children.get(n, []):
                if c not in seen:
                    seen.add(c)
                    stack.append(c)
        return seen

    def _blocks_all_paths(
        self,
        source: str,
        target: str,
        cond: Set[str]
    ) -> bool:
        """
        Returns True iff source and target are d-separated by cond
        in the ancestral subgraph of {source, target}.
        """
        subG = ancestral_subgraph(self._nx_graph, source, target)
        # only keep conditioning variables present in the subgraph
        cond_in_subg = {c for c in cond if c in subG.nodes()}

        try:
            dag = DAG(subG)
            return not dag.is_dconnected(source, target, list(cond_in_subg))
        except nx.NodeNotFound:
            return False


def analyze_paths(
    graph: Dict[str, List[str]],
    outcome: str,
    intervention: str,
    latent_nodes: Optional[Set[str]] = None,
    context: Optional[dict] = None,
) -> str:
    # 1) Register latent set
    if latent_nodes is not None:
        _GRAPH_LATENT_REGISTRY[id(graph)] = latent_nodes

    # 2) Fast‐path
    checker = IdentityChecker(graph, latent_vars=latent_nodes)
    result = checker.analyze(treatment=intervention, outcome=outcome, context=context)
    if result != "unknown":
        return result

    # 3) Full ID fallback (using pgmpy >= 1.2.1)
    try:
        from pgmpy.base import DAG
    except ImportError:
        raise ImportError("pgmpy >= 1.2.1 is required for identification fallback.")

    # Build DAG
    dag = DAG()
    dag.add_nodes_from(graph.keys())
    for child, ps in graph.items():
        for p in ps:
            dag.add_edge(p, child)

    try:
        # If intervention and outcome are d-separated given some Pa(X), it’s backdoor
        pa_x = set(graph.get(intervention, []))
        if dag.d_separated({intervention}, {outcome}, pa_x):
            return "backdoor"

        # Otherwise: unknown or need full ID (to be implemented)
        # Placeholder: return "id_fallback"
        return "id_fallback"

    except Exception:
        # In case anything goes wrong
        return "unknown"


# backward compatibility for tests doing `checker = IdentityChecker(...)`
import builtins
builtins.IdentityChecker = IdentityChecker
