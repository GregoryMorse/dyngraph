# Legacy interactive-session stubs (kept for reference):
#   import os; os.chdir(os.path.join('D:\\', 'Source', 'repos', 'efop', 'efop_362', 'work', 'wp-a', 'a11', 'morse', 'dyngraph')); exec(open('test.py').read()); test_paper_algos()
#   import sys; sys.modules.clear(); import os; os.chdir(...); exec(open('cfg.py').read()); test_paper_algos()
#   CD /D D:\Source\Repos\efop\EFOP_362\work\wp-a\a11\morse\dyngraph
#   "c:\program files\python38\python" test.py
#   "c:\program files\python38\python" -m cProfile -o results\profile test.py
#   "c:\program files\python38\python" -c "import pstats; p = pstats.Stats('results/profile'); p.sort_stats('time').print_stats(100)"
import argparse
import os
import cfg
import sccreach
import dfs
import bfs
import dominators
import lnf
import graph

# ── shared setup ──────────────────────────────────────────────────────────────

def _setup():
  if os.name == 'nt':
    import shutil, glob
    if not shutil.which('dot'):
      candidates = []
      for pf_var in ('PROGRAMFILES', 'PROGRAMFILES(X86)'):
        pf = os.environ.get(pf_var, '')
        if pf:
          candidates += glob.glob(os.path.join(pf, 'Graphviz*', 'bin'))
      if candidates:
        os.environ['PATH'] += os.pathsep + sorted(candidates)[-1]  # latest version
  this_dir = os.path.dirname(os.path.abspath(__file__))
  return os.path.join(this_dir, 'cfgs'), os.path.join(this_dir, 'results')

# ── cfg ───────────────────────────────────────────────────────────────────────

def cfg_paper(cfg_dir, output_dir):
  """Correctness tests for CFG construction and structure algorithms."""
  cfg.test_cfg_rev_graph(output_dir)
  cfg.test_interval_paper()
  cfg.test_parenthesis()
  cfg.test_boolexp()
  cfg.test_dream()
  cfg.test_cfg_minimize(output_dir)

def cfg_sequences(cfg_dir, output_dir):
  """Assert graph-counting OEIS sequences and run enumeration cross-checks."""
  graph.verify_graph_seqs()
  graph.check_topo(5)
  print([(x, sum(x[y]*y for y in x)) for x in [graph.topo_histogram(n) for n in range(5)]])

# ── scc / reachability ────────────────────────────────────────────────────────

def scc_paper(cfg_dir, output_dir):
  """Correctness tests for Tarjan SCC, Nuutila SCC+reach, and online SCC."""
  sccreach.paper_tarjan_scc()
  sccreach.paper_nuutila_scc_reach()
  sccreach.test_fully_online_reach_scc()
  sccreach.paper_inc_dec_scc(output_dir)

def scc_verify(cfg_dir, output_dir):
  """Verify the fully-dynamic SCC/reachability algorithms against references."""
  sccreach.verify_dyn_scc_reach()

def scc_timing(cfg_dir, output_dir):
  """Timing benchmarks for dynamic SCC/reachability on real-world CFGs."""
  sccreach.timing_dyn_scc_reach(cfg_dir, output_dir)

# ── bfs ───────────────────────────────────────────────────────────────────────

def bfs_paper(cfg_dir, output_dir):
  """Correctness tests for the incremental/decremental BFS paper algorithms."""
  bfs.paper_inc_dec_bfs(output_dir)

def bfs_verify(cfg_dir, output_dir):
  """Verify all dynamic BFS variants against the reference implementations."""
  bfs.verify_inc_dec_lex_bfs(output_dir)
  bfs.verify_inc_dec_general_lex_bfs(output_dir)
  bfs.verify_rank_dynamic_inc_dec_general_bfs(output_dir)
  bfs.verify_semi_dynamic_inc_dec_general_bfs(output_dir)
  bfs.verify_inc_dec_general_bfs(output_dir, True)
  bfs.verify_inc_dec_general_bfs(output_dir)

def bfs_timing(cfg_dir, output_dir):
  """Timing benchmarks for dynamic BFS on real-world CFGs."""
  bfs.timing_inc_dec_general_bfs_real(cfg_dir, output_dir)
  bfs.timing_inc_dec_general_bfs(cfg_dir, output_dir, True)
  bfs.timing_inc_dec_general_bfs(cfg_dir, output_dir)

# ── dfs ───────────────────────────────────────────────────────────────────────

def dfs_paper(cfg_dir, output_dir):
  """Correctness tests for Tarjan DFS and incremental/decremental DFS tree."""
  dfs.paper_tarjan_dfs()
  dfs.paper_inc_dec_dfs()
  dfs.test_edge_classify()

# ── dominators ────────────────────────────────────────────────────────────────

def dom_paper(cfg_dir, output_dir):
  """Correctness tests for Tarjan and SGL dominator/DJ-graph algorithms."""
  dominators.paper_tarjan_dom()
  dominators.test_sgl_phi_nodes()
  dominators.test_sgl_inc_dec_dominators()

def dom_verify(cfg_dir, output_dir):
  """Verify dynamic dominator algorithms against the reference implementations."""
  dominators.verify_inc_dec_dominators_lnf(output_dir)
  #dominators.verify_inc_dec_dominators(output_dir, dominators.METHOD_TARJAN)  # FIXME: rare errors
  dominators.verify_inc_dec_dominators(output_dir, dominators.METHOD_TREE_SGL)
  dominators.verify_inc_dec_dominators(output_dir)

# ── lnf ───────────────────────────────────────────────────────────────────────

def lnf_paper(cfg_dir, output_dir):
  """Correctness tests for LNF paper algorithms (Tarjan, Havlak, Steensgaard, Sreedhar-Gao-Lee, etc.)."""
  lnf.test_tarjan_loops()
  lnf.test_sreedhar_gao_lee_loops()
  lnf.test_havlak_loops()
  lnf.test_linear_havlak_mod_sgl()
  lnf.test_ramalingam_reduced_havlak()
  lnf.test_new_algo_loops()
  lnf.test_steensgaard_loops()
  lnf.paper_inc_dec_reducible_lnf(output_dir)
  lnf.paper_inc_dec_irreducible_lnf(output_dir)
  lnf.test_inc_dec_graph_random()

def lnf_verify(cfg_dir, output_dir):
  """Verify dynamic LNF algorithms against the reference implementations."""
  lnf.verify_dyn_reducible_lnf(output_dir, True)
  lnf.verify_dyn_irreducible_lnf(output_dir, True)
  #lnf.verify_dyn_reducible_lnf(output_dir, False)  # FIXME: incremental/decremental non-connected
  lnf.verify_dyn_irreducible_lnf(output_dir, False)

def lnf_timing(cfg_dir, output_dir):
  """Timing benchmarks for dynamic LNF on real-world CFGs."""
  lnf.timing_inc_dec_reducible_lnf(output_dir)
  lnf.timing_inc_dec_irreducible_lnf(output_dir)

# ── dispatch ──────────────────────────────────────────────────────────────────

_DISPATCH = {
  'cfg': {'paper': cfg_paper, 'sequences': cfg_sequences},
  'scc': {'paper': scc_paper, 'verify': scc_verify, 'timing': scc_timing},
  'bfs': {'paper': bfs_paper, 'verify': bfs_verify, 'timing': bfs_timing},
  'dfs': {'paper': dfs_paper},
  'dom': {'paper': dom_paper, 'verify': dom_verify},
  'lnf': {'paper': lnf_paper, 'verify': lnf_verify, 'timing': lnf_timing},
}

def _run_module(module, subcmd, cfg_dir, output_dir):
  table = _DISPATCH[module]
  if subcmd == 'all':
    for fn in table.values():
      fn(cfg_dir, output_dir)
  elif subcmd in table:
    table[subcmd](cfg_dir, output_dir)
  else:
    available = ', '.join(sorted(table)) + ', all'
    raise SystemExit(f"'{module}' has no '{subcmd}' subcommand. Available: {available}")

# ── legacy entry point ────────────────────────────────────────────────────────

def test_paper_algos():
  """Legacy entry point (used in old exec()-based sessions). Runs all paper-correctness tests."""
  cfg_dir, output_dir = _setup()
  for mod in _DISPATCH:
    _run_module(mod, 'paper', cfg_dir, output_dir)

# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    prog='test.py',
    description='Dyngraph algorithm test and benchmark runner.',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""modules and their subcommands:
  cfg   paper, sequences
  scc   paper, verify, timing
  bfs   paper, verify, timing
  dfs   paper
  dom   paper, verify
  lnf   paper, verify, timing
  all   runs the subcommand across every applicable module

subcommands:
  paper       correctness tests for reference paper algorithms  [default]
  verify      validate our dynamic algorithms against references
  timing      performance benchmarks on real-world CFGs (requires cfgs/)
  sequences   OEIS graph-counting and enumeration checks       (cfg only)
  all         run all subcommands for the selected module

examples:
  python test.py                    run all paper-correctness tests
  python test.py lnf                lnf paper-correctness tests
  python test.py lnf verify         verify dynamic LNF vs reference
  python test.py lnf timing         LNF timing benchmarks
  python test.py lnf all            run all lnf subcommands
  python test.py cfg sequences      print graph-counting OEIS sequences
  python test.py all verify         verify all dynamic algorithms
  python test.py all timing         all timing benchmarks
  python test.py all all            run everything
""")
  parser.add_argument(
    'module', nargs='?', default='all',
    choices=['cfg', 'scc', 'bfs', 'dfs', 'dom', 'lnf', 'all'],
    metavar='module',
    help='Module to test (default: all). Choices: cfg scc bfs dfs dom lnf all')
  parser.add_argument(
    'subcommand', nargs='?', default='paper',
    choices=['paper', 'verify', 'timing', 'sequences', 'all'],
    metavar='subcommand',
    help='What to run (default: paper). Choices: paper verify timing sequences all')
  args = parser.parse_args()
  cfg_dir, output_dir = _setup()

  if args.module == 'all':
    if args.subcommand == 'sequences':
      cfg_sequences(cfg_dir, output_dir)
    elif args.subcommand == 'all':
      for mod in _DISPATCH:
        _run_module(mod, 'all', cfg_dir, output_dir)
    else:
      for mod in _DISPATCH:
        if args.subcommand in _DISPATCH[mod]:
          _DISPATCH[mod][args.subcommand](cfg_dir, output_dir)
  else:
    _run_module(args.module, args.subcommand, cfg_dir, output_dir)