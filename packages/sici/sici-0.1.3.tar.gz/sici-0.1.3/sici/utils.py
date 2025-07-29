# sici/utils.py

import re
from typing import Dict, List, Set

def clean_distribution_label(label: str) -> str:
    """
    Clean a distribution label string (e.g., 'P(Y | X, Z)') → 'P(Y|X,Z)'
    :param label: Original label with optional spaces
    :return: Cleaned label
    """
    return re.sub(r'\s+', '', label)

def extract_variables_from_label(label: str) -> List[str]:
    """
    Given a label like 'P(Y|X,Z)', return ['Y', 'X', 'Z']
    :param label: Symbolic label of a conditional distribution
    :return: List of variable names
    """
    match = re.match(r'P\((.*?)\)', label)
    if not match:
        return []
    inside = match.group(1)
    if '|' in inside:
        left, right = inside.split('|')
        return [x.strip() for x in [left] + right.split(',')]
    else:
        return [x.strip() for x in inside.split(',')]

def pretty_header(title: str):
    print(f"\n{'=' * (len(title) + 4)}")
    print(f"= {title} =")
    print(f"{'=' * (len(title) + 4)}")

def shorten_expr(expr_str: str, maxlen=60) -> str:
    """
    Truncate long SymPy expressions for CLI-friendly preview.
    """
    return expr_str if len(expr_str) <= maxlen else expr_str[:maxlen] + "..."

def bold(text: str) -> str:
    return f"\033[1m{text}\033[0m"

def color(text: str, c='blue') -> str:
    color_codes = {
        'red': '\033[91m', 'green': '\033[92m',
        'yellow': '\033[93m', 'blue': '\033[94m',
        'magenta': '\033[95m', 'cyan': '\033[96m',
    }
    return color_codes.get(c, '') + text + '\033[0m'

def induced_ancestral_graph(
    full_graph: Dict[str, List[str]],
    treatment: str,
    outcome: str
) -> Dict[str, List[str]]:
    """
    返回只包含 intervention/outcome 及其所有祖先节点的子图。
    Graph 格式：node -> list of parents
    """
    anc: Set[str] = {treatment, outcome}
    stack = [treatment, outcome]
    while stack:
        node = stack.pop()
        for p in full_graph.get(node, []):
            if p not in anc:
                anc.add(p)
                stack.append(p)
    # 过滤，只保留祖先子图
    return {
        n: [p for p in parents if p in anc]
        for n, parents in full_graph.items()
        if n in anc
    }