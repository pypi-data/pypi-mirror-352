# SICI: Symbolic Integration for Causal Inference

**SICI** is a fast and modular compiler for structural causal queries:

- Outputs **symbolic integrals** (SymPy)
- Or **numeric estimates** (MC integration / SciPy nquad)
- **Optimizes** and **caches** complex expressions across queries
- Scales to large DAGs (n > 5000)

---

## 🚀 Why SICI?

Automatic causal identification (backdoor, frontdoor, IV, counterfactuals, unobserved confounding)  
**Symbolic compiler** → clean SymPy integrals  
**Numeric compiler** → fast MC evaluation  
**SICI-Cache** → cross-query caching & deep DAG folding  
Outperforms existing tools: SymPy CSE, Whittemore, Causaleffect  
Scales to thousands of variables — robust against symbolic blowup

---
## ⚡ Tutorial
python sici/examples/sici_tutorial.ipynb

## ⚡ Quickstart

```python
from sici.models import SCM, Query
from sici.compiler import compile

# Simple SCM: Z → X → Y, Z → Y
scm = SCM(
    graph={"Z": [], "X": ["Z"], "Y": ["X", "Z"]},
    conditionals={
        "P(Z)": "P_Z",
        "P(X|Z)": "P_X|Z",
        "P(Y|X,Z)": "P_Y|X,Z"
    }
)

# Symbolic query: P(Y | do(X))
q = Query(outcome="Y", intervention="X")
tree = compile(scm, q, mode="symbolic")
print(tree.to_sympy())

# Numeric query with MC integration
from scipy.stats import norm

scm = SCM(
    graph={"Z": [], "X": ["Z"], "Y": ["X", "Z"]},
    conditionals={
        "P(Z)":     lambda z: norm.pdf(z, 0, 1),
        "P(X|Z)":   lambda x, z: norm.pdf(x - z, 0, 1),
        "P(Y|X,Z)": lambda y, x, z: norm.pdf(y - (x+z), 0, 1)
    }
)

q = Query(outcome="Y", intervention="X")
value = compile(scm, q, mode="numeric", intervention_value=0.0, mc_samples=5000)
print("E[Y|do(X=0)] ≈", value)
```
## 🔍 Running Benchmarks
### Compare with SymPy CSE / Whittemore:
python sici/examples/sici_cache/failure_existing.py
### Scalability on large synthetic DAGs:
python sici/examples/sici_cache/large_scale.py
### Real data + cross-query caching:
python sici/examples/real_data_cross_query.py
### MC convergence:
python sici/examples/sici_cache/mc_convergence.py

## 💎 Key Results

| Experiment                       | Result                                    |
|---------------------------------|-------------------------------------------|
| Cross-query caching              | 10×–100× speedup                          |
| DAG folding                      | up to 90% symbolic complexity reduction   |
| Large DAGs                       | scales to n = 10,000                      |
| Compared to SymPy CSE            | merges more subexpressions                |
| Compared to Whittemore/Causaleffect | generates flatter, reusable expressions  |

---

## 📦 Installation

```bash
pip install sici
```
Requires: Python 3.9+
Dependencies: sympy, scipy, graphviz, numpy, pandas, pytest, pgmpy

Note: The current open-sourced SICI version does not bundle Ananke fallback by default. 
Fallback to Ananke (https://gitlab.com/causal/ananke) can be enabled manually if desired.
 


## 🖥️ Compute Resources

### All benchmarks were run on:

Machine: MacBook Air (M1, 2020), 8 GB RAM

Python: Python 3.9.7

Libraries: SciPy 1.10.1, SymPy 1.10.1

### Typical runtimes:

Backdoor compile: ~0.003 s

Large DAG (n=500, p=0.02): ~11 s

Asia network symbolic compile: ~0.02 s

Alarm network numeric evaluation: ~0.30 s

## 🗂️ Project Structure

```bash
sici/
├── compiler.py          # Unified symbolic & numeric compiler
├── dag.py               # DAG folding
├── canonical.py         # AST canonicalization
├── cache.py             # Global caching
├── metrics.py           # Logging & benchmark metrics
├── trace.py             # Trace graph construction
├── tree.py              # ExpressionTree (SymPy wrapper)
├── models.py            # SCM & Query classes
├── rewrite.py           # Symbolic rewrite rules
├── visual.py            # Graphviz renderers
├── examples/
│   ├── sici_cache/      # experiments of SICI-Cache
│   ├── sici_trace/      # experiments of SICI-Trace
│   └── real_data_cross_query.py
└── tests/               # Unit tests
```

## 💼 License
MIT License.

## 🧭 Related Work
Whittemore

Causaleffect (R package)

SymPy CSE

CausalGraphs.jl


### ✨ SICI bridges symbolic causal reasoning with scalable compilation and efficient caching.
