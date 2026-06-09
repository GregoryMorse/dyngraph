# dyngraph — Dynamic Graph Algorithms for Control Flow Graphs

Research implementation accompanying the PhD dissertation of Gregory Morse, covering fully dynamic algorithms on digraphs with applications to control flow graph (CFG) analysis under self-modifying code.

## Authors

- **Gregory Morse** — [gregory.morse@live.com](mailto:gregory.morse@live.com) — [GregoryMorse](https://github.com/GregoryMorse)
- **Tamás Kozsik** — co-author on the SCC/reachability work

## Research Context

This repository supports a PhD dissertation and three associated manuscripts:

| Status | Description |
|--------|-------------|
| Preprint | **Fully Dynamic Breadth First Search and Spanning Trees in Directed Graphs** — Gregory Morse; Tamás Kozsik. *arXiv:2604.12370 [cs.DS], April 2026.* https://arxiv.org/abs/2604.12370 |
| Preprint | **Fully Dynamic Maintenance of Loop Nesting Forests in Reducible Flow Graphs** — Gregory Morse; Tamás Kozsik. *arXiv:2604.13664 [cs.DS], April 2026.* https://arxiv.org/abs/2604.13664 |
| Accepted | **Fully Dynamic Strong Connectivity and Reachability in Digraphs** — Gregory Morse; Tamás Kozsik. *Accepted for publication in Annales Mathematicae et Informaticae (selected paper from ICAI 2026).* |

Conference presentations for the SCC/reachability work:

- Gregory Morse and Tamás Kozsik. **Fully Dynamic Strong Connectivity and Reachability in Digraphs**. 13th Joint Conference on Mathematics and Computer Science (MaCS 2020). October 2nd, 2020, 15:00-15:20. Virtual, Eötvös Loránd University, Budapest, Hungary. https://macs2020.elte.hu/wp-content/uploads/2020/10/friday.pdf
- Gregory Morse and Tamás Kozsik. **Fully Dynamic Strong Connectivity and Reachability in Digraphs**. The 13th International Conference on Applied Informatics (ICAI 2026). Eszterházy Károly Catholic University, Eger, February 19, 2026, 13:50-14:10. https://icai.uni-eszterhazy.hu/2026/program/

Extended abstract for the SCC/reachability work:

- Gregory Morse and Tamás Kozsik. **Fully Dynamic Strong Connectivity and Reachability in Digraphs**. In: 13th Joint Conference on Mathematics and Informatics (Collection of Abstracts), pp. 121-122, 2 p. (2020). https://macs2020.elte.hu/booklet/macs2020abstractBooklet.pdf

Additional conference presentation related to this project:

- Gregory Morse. **Dynamic Graph Algorithms, Refactoring Decompiled Code, and Obfuscation Techniques**. 3in Conference on Software and Artificial Intelligence. November 6th, 2020, 13:20-13:40. Virtual, EFOP-3.6.2-16-2017-00013, Hungary. https://www.inf.elte.hu/invitation-3in-conference-on-software-and-artificial-intelligence

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
| `cfgs/` | IDA Pro **7.0 Freeware** (last freeware release; see comment in `graph.py`) CFGs in GDL format, generated via `gengraphs.idc`. Linux x86-64 ELF binaries (exact package versions unrecorded): `sendmail/` (1 599 functions), `smbd/` (799), `vsftpd/` (705). Windows 10 x64 PE binaries (build ≥ 1803, inferred from WIL `FeatureStateManager` symbols in `explorer.exe`; exact build unrecorded): `explorer.exe/` (11 703 functions), `kernel32.dll/` (2 533), `user32.dll/` (2 651). Windows-derived folders have `*_sanitized/` counterparts (topology + edge labels only, disassembly stripped) for clean public redistribution. Also `web-Stanford.txt` (SNAP Stanford web crawl 2002, 281 903 nodes / 2 312 497 edges). |
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
  journal   = {Annales Mathematicae et Informaticae},
  note      = {Accepted; selected paper from ICAI 2026}
}
```

arXiv preprints:

```bibtex
@misc{morse2026bfs,
  author        = {Gregory Morse and Tam{\'{a}}s Kozsik},
  title         = {Fully Dynamic Breadth First Search and Spanning Trees in Directed Graphs},
  year          = {2026},
  eprint        = {2604.12370},
  archivePrefix = {arXiv},
  primaryClass  = {cs.DS},
  doi           = {10.48550/arXiv.2604.12370},
  url           = {https://arxiv.org/abs/2604.12370}
}

@misc{morse2026lnf,
  author        = {Gregory Morse and Tam{\'{a}}s Kozsik},
  title         = {Fully Dynamic Maintenance of Loop Nesting Forests in Reducible Flow Graphs},
  year          = {2026},
  eprint        = {2604.13664},
  archivePrefix = {arXiv},
  primaryClass  = {cs.DS},
  doi           = {10.48550/arXiv.2604.13664},
  url           = {https://arxiv.org/abs/2604.13664}
}
```

## License

MIT License — see [LICENSE](LICENSE).
