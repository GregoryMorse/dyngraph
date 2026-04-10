# dyngraph — Dynamic Graph Algorithms for Control Flow Graphs

Research implementation accompanying the PhD dissertation of Gregory Morse, covering fully dynamic algorithms on digraphs with applications to control flow graph (CFG) analysis under self-modifying code.

## Authors

- **Gregory Morse** — [gregory.morse@live.com](mailto:gregory.morse@live.com) — [GregoryMorse](https://github.com/GregoryMorse)
- **Tamás Kozsik** — co-author on the SCC/reachability work

## Research Context

This repository supports a PhD dissertation and three associated manuscripts:

| Status | Description |
|--------|-------------|
| In preparation | **Dynamic BFS and Lex-BFS on Digraphs** |
| In preparation | **Fully Dynamic Loop Nesting Forest for Reducible and Irreducible CFGs** |
| Submitted | **Fully Dynamic Strong Connectivity and Reachability in Digraphs** — Gregory Morse; Tamás Kozsik. *Submitted to Proceedings of the ICAI 2026.* |

The central application domain is static and dynamic program analysis of binaries, particularly control flow reconstruction when facing self-modifying or obfuscated code. Algorithms are designed to support efficient incremental and decremental edge/node updates without recomputing from scratch.

## Repository Structure

| File | Description |
|------|-------------|
| `graph.py` | Core data structures: `DisjointSet` (union-find with path compression and union by rank), `PartitionRefinement` (doubly-linked partition lists), `Tree`, and graph enumeration combinatorics |
| `dfs.py` | Depth-first search: interval/discovery timestamps, edge classification (tree/back/forward/cross), dynamic incremental/decremental DFS tree maintenance |
| `bfs.py` | Breadth-first search and Lex-BFS: dynamic incremental/decremental BFS tree, rank-dynamic and semi-dynamic variants, verification harness |
| `sccreach.py` | Strongly connected components and reachability: Tarjan's SCC, Nuutila's SCC with transitive closure, **fully dynamic online SCC and reachability** |
| `dominators.py` | Dominator trees, DJ-graphs, iterated dominance frontiers (IDF), and Tarjan offline LCA |
| `lnf.py` | Loop Nesting Forest: incremental reducible LNF (Tarjan-based), incremental/decremental reducible and irreducible LNF |
| `cfg.py` | `Digraph` class integrating all above: DFS tree, BFS trees, dominator trees, DJ-graphs, LNF, and SCC/reach; Graphviz DOT output; CFG test cases |
| `sat.py` | SATLIB benchmark downloader and parser (DIMACS CNF), unit propagation; used to generate random 3-SAT CFG instances |
| `irredloop.py` | Irreducible loop structure enumeration; Python and Java reference implementations for structuring irreducible loops without `goto` |
| `JSMC.java` | Java reference implementation of irreducible loop structuring |
| `findpyrecursive.py` | Static analysis utility: detects direct recursion in Python source via AST walking |
| `gengraphs.idc` | IDA Pro IDC script for extracting control flow graphs from binaries |
| `test.py` | Test and benchmarking harness: runs all paper algorithm experiments and timing benchmarks |
| `setup.py` | Cython build configuration |
| `CFGenum.ipynb` | Jupyter notebook: CFG enumeration and analysis |
| `confflow.ipynb` | Jupyter notebook: control-flow experiments |
| `cfgs/` | SATLIB benchmark instances (uf20-91 random 3-SAT, 1000 instances); auto-downloaded by `sat.py` |
| `results/` | Generated output: Graphviz DOT/SVG/TeX files, timing and paper experiment text outputs |

## Prerequisites

- Python 3.8+
- [Graphviz](https://graphviz.org/download/) installed and on `PATH` (for DOT rendering)
- Optional: Cython (for `setup.py` compilation)
- Optional: Java JDK 16+ (for `JSMC.java`)

Install Python dependencies:

```bash
pip install graphviz requests
```

## Running the Experiments

```bash
python test.py
```

By default `test.py` runs all paper algorithm experiments (`sccreach`, `bfs`, `lnf`) and writes results to `results/`. The working directory must be the repository root, or run via:

```python
import os, test
os.chdir(r'path/to/dyngraph')
test.test_paper_algos()
```

To profile:

```bash
python -m cProfile -o results/profile test.py
python -c "import pstats; p = pstats.Stats('results/profile'); p.sort_stats('time').print_stats(100)"
```

To build the Cython extension:

```bash
python setup.py build_ext --inplace
```

## Key Algorithms

### Fully Dynamic SCC and Reachability (`sccreach.py`)
Supports online interleaved edge insertions and deletions while maintaining SCCs and full reachability information. Benchmarked against Tarjan and Nuutila on SATLIB-derived CFG instances.

### Dynamic Lex-BFS (`bfs.py`)
Incremental and decremental maintenance of Lex-BFS order and BFS tree on directed graphs using partition refinement. Includes rank-dynamic and semi-dynamic variants.

### Dynamic Loop Nesting Forest (`lnf.py`)
Incremental and decremental maintenance of the loop nesting forest under edge insertions/deletions, handling both reducible and irreducible CFGs. Builds on a dynamic DFS tree and dominator tree.

### Dominator Trees and DJ-Graphs (`dominators.py`)
Dynamic dominator tree maintenance with support for iterated dominance frontier computation (used in SSA construction).

## IDA Pro Integration

`gengraphs.idc` is an IDA Pro IDC script that extracts CFGs from binary functions for use as benchmark inputs. Run from the IDA Pro scripting console.

## Citation

If you use this code or build on this work, please cite:

```bibtex
@inproceedings{morse2026scc,
  author    = {Gregory Morse and Tam{\'{a}}s Kozsik},
  title     = {Fully Dynamic Strong Connectivity and Reachability in Digraphs},
  booktitle = {Proceedings of the International Conference on Applied Informatics (ICAI 2026)},
  year      = {2026},
  note      = {Submitted}
}
```

Additional manuscripts (BFS and LNF) will be linked here upon arxiv publication.

## License

MIT License — see [LICENSE](LICENSE).
