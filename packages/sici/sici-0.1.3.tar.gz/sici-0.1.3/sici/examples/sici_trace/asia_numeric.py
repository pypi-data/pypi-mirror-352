# examples/sici_trace/asia_numeric.py

import itertools
import numpy as np
import time
from typing import List, Tuple
from pgmpy.utils import get_example_model
from sici.models import SCM, Query
from sici.compiler import compile

def parent_combo_from_index(parent_states: List[List[float]], index: int) -> Tuple[float, ...]:
    """Convert column index to parent value combination (with integer casting)."""
    combo = []
    strides = [
        int(np.prod([len(p) for p in parent_states[i+1:]]))
        for i in range(len(parent_states))
    ]
    for i in range(len(parent_states)):
        stride = strides[i] if i < len(strides) else 1
        idx = int((index // stride) % len(parent_states[i]))
        combo.append(parent_states[i][idx])
    return tuple(combo)

def build_asia_numeric_scm():
    """Load Asia network and convert to numeric SCM with normalized CPDs."""
    model = get_example_model("asia")
    
    graph = {v: list(model.get_parents(v)) for v in model.nodes()}
    conds = {}
    state_names = {}
    value_map = {"yes": 1.0, "no": 0.0}

    for cpd in model.get_cpds():
        var = cpd.variable
        parents = list(cpd.variables[1:])
        
        str_states = cpd.state_names[var]
        num_states = [value_map[s] for s in str_states]
        state_names[var] = num_states
        
        arr = np.array(cpd.values, dtype=float)
        if parents:
            arr = arr.reshape((len(num_states), -1))
            arr /= arr.sum(axis=0, keepdims=True)
        else:
            arr = arr.flatten()
            arr /= arr.sum()
        
        table = {}
        if parents:
            parent_states = [
                [value_map[s] for s in cpd.state_names[p]]
                for p in parents
            ]
            for col_idx, _ in enumerate(itertools.product(*parent_states)):
                for row_idx, child_val in enumerate(num_states):
                    key = (child_val,) + tuple(parent_combo_from_index(parent_states, col_idx))
                    table[key] = float(arr[row_idx, col_idx])
        else:
            for row_idx, child_val in enumerate(num_states):
                table[child_val] = float(arr[row_idx])

        label = f"P({var}|{','.join(parents)})" if parents else f"P({var})"
        conds[label] = table

    return SCM(graph=graph, conditionals=conds, state_names=state_names)

def main():
    scm = build_asia_numeric_scm()
    
    interventions = {"no": 0.0, "yes": 1.0}
    for label, value in interventions.items():
        # 计时开始
        t0 = time.perf_counter()
        result = compile(
            scm,
            Query(outcome="tub", intervention="asia", context={"tub": 1.0}),
            mode="numeric",
            intervention_value=value,
            mc_samples=10_000
        )
        t1 = time.perf_counter()
        elapsed = t1 - t0

        print(f"P(tub=1.0 | do(asia={label})) = {result:.4f} (time = {elapsed:.4f}s)")

if __name__ == "__main__":
    main()
