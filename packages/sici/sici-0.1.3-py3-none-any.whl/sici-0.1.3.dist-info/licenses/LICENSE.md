# SICI: Symbolic Integration for Causal Inference

**SICI** is a symbolic compiler for structural causal queries.
It transforms a fully specified SCM and causal query into a structured symbolic expression tree (AST) via annotated trace graphs.

- 📘 Based on our NeurIPS 2025 submission: "Symbolic Integration for Causal Inference"
- ⚙️ Supports graph-guided query execution planning
- 🧠 Interpretable, reusable symbolic outputs
- 🔗 Integrates with SymPy, Pyro, causal discovery libraries
- Export compiled expressions to LaTeX, SymPy, or JSON with one line

## Install

```bash
pip install -e .

🚧 This repo currently includes:
- `sici.trace` – Annotated trace graph construction
- `sici.tree` – Symbolic expression tree synthesis

Coming soon:
- `sici.rewriter` – Symbolic expression rewriting engine
- `sici.strategy` – Strategy planner for query path optimization

📚 Read the paper: [link to PDF / arXiv]

symbolic_integration_causal/       ← ✅ 项目根目录（推荐用小写+下划线）
├── pyproject.toml                 ← ✅ 管理依赖与打包配置
├── README.md                      ← ✅ 项目说明
# ├── LICENSE                        ← ✅ 开源协议（如 MIT） （待添加）
# ├── .gitignore                     ← ✅ 忽略缓存/虚拟环境等（待添加）
│
├── sici/                          ← ✅ 真正的 Python 包
│   ├── __init__.py
│   ├── compiler.py
│   ├── models.py
│   ├── tree.py
│   ├── trace.py
│   ├── visual.py
│   ├── export.py
│   ├── utils.py
│   └── examples/
│       ├── backdoor.py
│       ├── frontdoor.py
│       ├── multiple_queries.py
│       └── notebooks/
│           ├── intro_walkthrough.ipynb
│           └── visualize_expression.ipynb
│
├── tests/                         ← ✅ 测试目录
│   ├── test_compile.py
│   ├── test_tree.py
│   └── test_trace.py
│
└── docs/                          ← 📄（可选）项目文档
    ├── index.md
    └── api_reference.md