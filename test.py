#import os; os.chdir(os.path.join('D:\\', 'Source', 'repos', 'efop', 'efop_362', 'work', 'wp-a', 'a11', 'morse', 'dyngraph')); exec(open('test.py').read()); test_paper_algos()
#import sys; sys.modules.clear(); import os; os.chdir(os.path.join('D:\\', 'Source', 'repos', 'efop', 'efop_362', 'work', 'wp-a', 'a11', 'morse', 'dyngraph')); exec(open('cfg.py').read()); test_paper_algos()
#CD /D D:\Source\Repos\efop\EFOP_362\work\wp-a\a11\morse\dyngraph
#"c:\program files\python38\python" test.py
#"c:\program files\python38\python" -m cProfile -o results\profile test.py
#"c:\program files\python38\python" -c "import pstats; p = pstats.Stats('results/profile'); p.sort_stats('time').print_stats(100)"
import os
import cfg
import sccreach
import dfs
import bfs
import dominators
import lnf
import graph

def test_paper_algos():
  if os.name == 'nt':
    graphviz_path = os.path.join(os.environ['PROGRAMFILES'], "Graphviz 2.44.1", "bin")
    os.environ['PATH'] += ";" + graphviz_path
  this_dir = os.path.dirname(os.path.abspath(__file__))
  cfg_dir = os.path.join(this_dir, 'cfgs')
  output_dir = os.path.join(this_dir, 'results')
  
  #cfg.test_cfg_rev_graph(output_dir)
  #cfg.test_interval_paper()
  #cfg.test_parenthesis()
  #cfg.test_boolexp()
  #cfg.test_dream()
  #cfg.test_cfg_minimize(output_dir)
  #lnf.verify_dyn_reducible_lnf(output_dir, True)
  #print(graph.graph_seqs(50000, lambda x: graph.graph_enum(x, lambda y: graph.enum_connected_digraphs(y, True))))
  #lnf.paper_inc_dec_reducible_lnf(output_dir)
  #lnf.timing_inc_dec_reducible_lnf(output_dir)
  #assert False
  """
  print(graph.graph_seqs(10 ** 10, graph.count_digraphs))
  print(graph.graph_seqs(10 ** 10, graph.count_simple_digraphs))
  print(graph.graph_seqs(10 ** 10, graph.count_dags))
  print(graph.graph_seqs(10 ** 10, graph.count_connected_dags))
  print(graph.graph_seqs(10 ** 10, graph.count_simple_connected_digraphs))
  print(graph.graph_seqs(10 ** 10, graph.count_connected_digraphs))
  print(graph.graph_seqs(10 ** 10, graph.itilda))
  print(graph.graph_seqs(10 ** 10, graph.s_n))
  print(graph.graph_seqs(10 ** 10, graph.count_simple_rooted_connected_digraphs))
  print(graph.graph_seqs(10 ** 10, graph.i_n))
  print(graph.graph_seqs(10 ** 10, graph.i_n_selfloops))
  print(graph.graph_seqs(10 ** 10, graph.count_dags_one_outpoint))
  print(graph.graph_seqs(10 ** 10, graph.count_topo_hist_dag))
  """
  #graph.check_topo(5)
  
  #print([(x, sum(x[y]*y for y in x)) for x in [graph.topo_histogram(n) for n in range(5)]])
  #print(graph.graph_seqs(50000, lambda x: graph.graph_enum(x, graph.enum_digraphs)))
  #print(graph.graph_seqs(50000, lambda x: graph.graph_enum(x, graph.enum_simple_digraphs)))
  #print(graph.graph_seqs(50000, lambda x: graph.graph_enum(x, graph.enum_dags)))
  #print(graph.graph_seqs(50000, lambda x: graph.graph_enum(x, lambda y: graph.enum_connected_dags(y, False))))
  #print(graph.graph_seqs(50000, lambda x: graph.graph_enum(x, lambda y: graph.enum_connected_dags(y, True))))
  #print(graph.graph_seqs(50000, lambda x: graph.graph_enum(x, lambda y: graph.enum_connected_digraphs(y, False))))
  #print(graph.graph_seqs(50000, lambda x: graph.graph_enum(x, lambda y: graph.enum_connected_digraphs(y, False, True))))
  #print(graph.graph_seqs(50000, lambda x: graph.graph_enum(x, lambda y: graph.enum_connected_digraphs(y, True, True))))
  #print(graph.graph_seqs(50000, lambda x: graph.graph_enum(x, lambda y: graph.enum_connected_digraphs(y, True))))
  
  #return
  sccreach.paper_tarjan_scc()
  sccreach.paper_nuutila_scc_reach()
  sccreach.test_fully_online_reach_scc()
  sccreach.paper_inc_dec_scc(output_dir)
  #sccreach.verify_dyn_scc_reach()
  #sccreach.timing_dyn_scc_reach(cfg_dir, output_dir)
  #bfs.verify_inc_dec_lex_bfs(output_dir)
  bfs.verify_inc_dec_general_lex_bfs(output_dir)
  """
  bfs.paper_inc_dec_bfs(output_dir)
  bfs.verify_rank_dynamic_inc_dec_general_bfs(output_dir)
  bfs.verify_semi_dynamic_inc_dec_general_bfs(output_dir)
  bfs.verify_inc_dec_general_bfs(output_dir, True)
  bfs.verify_inc_dec_general_bfs(output_dir)
  bfs.timing_inc_dec_general_bfs_real(cfg_dir, output_dir)
  bfs.timing_inc_dec_general_bfs(cfg_dir, output_dir, True)
  bfs.timing_inc_dec_general_bfs(cfg_dir, output_dir)
  dfs.paper_tarjan_dfs()
  dfs.paper_inc_dec_dfs()
  dfs.test_edge_classify()
  """
  dominators.paper_tarjan_dom()
  dominators.test_sgl_phi_nodes()
  dominators.test_sgl_inc_dec_dominators()
  dominators.verify_inc_dec_dominators_lnf(output_dir)
  #dominators.verify_inc_dec_dominators(output_dir, dominators.METHOD_TARJAN) #FIXME rare errors
  #dominators.verify_inc_dec_dominators(output_dir, dominators.METHOD_TREE_SGL)
  #dominators.verify_inc_dec_dominators(output_dir)
  #lnf.paper_inc_dec_reducible_lnf(output_dir)
  #lnf.paper_inc_dec_irreducible_lnf(output_dir)
  #lnf.verify_dyn_reducible_lnf(output_dir, True)
  #lnf.verify_dyn_irreducible_lnf(output_dir, True)
  #lnf.verify_dyn_reducible_lnf(output_dir, False) #FIXME incremental/decremental non-connected
  #lnf.verify_dyn_irreducible_lnf(output_dir, False)
  #lnf.timing_inc_dec_reducible_lnf(output_dir)
  #lnf.timing_inc_dec_irreducible_lnf(output_dir)
  #lnf.test_inc_dec_graph_random()
  lnf.test_tarjan_loops()
  lnf.test_sreedhar_gao_lee_loops()
  lnf.test_havlak_loops()
  lnf.test_linear_havlak_mod_sgl()
  lnf.test_ramalingam_reduced_havlak()
  lnf.test_new_algo_loops()
  lnf.test_steensgaard_loops()
  lnf.test_tarjan_loops()  
test_paper_algos()