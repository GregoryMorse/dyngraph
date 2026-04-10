"""
requires pip install graphviz and graphviz in the path
e.g. os.environ['PATH']+=";"+graphviz_path for Windows
or os.environ['LD_LIBRARY_PATH']+=":"+graphviz_path for Linux
import sccreach
cfg_dir = os.path.join('D:', 'Source', 'repos', 'efop', 'efop_362', 'work', 'wp-a', 'a11', 'morse', 'dyngraph', 'cfgs') #set control flow graph folder
output_dir = os.path.join('D:', 'Source', 'repos', 'efop', 'efop_362', 'work', 'wp-a', 'a11', 'morse', 'dyngraph', 'results') #set output folder
sccreach.paper_inc_dec_scc(cfg_dir, output_dir)
"""

#import os
#from xml.dom.expatbuilder import parseString
import graph
import sccreach
import bfs
import lnf
import dfs
import dominators

class Digraph: #should derive from digraph
  def __init__(self, sources=[], init=None, node_order=None):
    self.succ, self.pred, self.sources = {}, {}, []
    self.dfs_tree, self.dfs_int, self.dfs_revint = dfs.init_dfs()
    self.doms, self.bfsts = {}, {}    
    self.djs_scc, self.sccs, self.reach = sccreach.init_reach_scc()
    self.loopcounts, self.loopheaders, self.looptypes, self.loopentries = lnf.init_lnf()
    for x in sources:
      self.bfsts[x] = bfs.init_bfs(x)
      self.doms[x] = dominators.init_dom(x)
      self.sources.append(x)
      Digraph.add_node(self, x)
    if not init is None:
      for x in range(1, len(init)+1):
        if not node_order is None: x = node_order[x - 1] + 1
        if not x in self.succ: Digraph.add_node(self, x)
      for i, x in enumerate(init):
        #if not node_order is None: i = node_order[i]
        for y in x: Digraph.add_edge(self, i + 1, y)
  def graphviz_dot_digraph(self, pre=""): return graph.do_graphviz_dot_digraph(self.succ, pre)
  def graphviz_dot_digraph_interval(self, pre=""): return dfs.graphviz_dot_digraph_interval(self.succ, self.dfs_int, pre)
  def graphviz_dot_jungle(self): return dfs.graphviz_dot_jungle(self.succ, self.dfs_tree, self.dfs_int)
  def graphviz_dot_bfst(self, source): return bfs.graphviz_dot_bfst(self.succ, *self.bfsts[source])
  def graphviz_dot_dj(self, pre="d"): return dominators.graphviz_dot_dj(self.succ, self.doms[self.sources[0]][0], pre)
  def graphviz_dot_lnf(self): return lnf.graphviz_dot_lnf(self.loopheaders, self.looptypes)
  GRAPH_MAIN, GRAPH_MAIN_DFS_INTERVAL, GRAPH_DFST, GRAPH_JUNGLE, GRAPH_BFST, GRAPH_DOMTREE, GRAPH_DJ, GRAPH_LNF, GRAPH_SCC = 1, 2, 4, 8, 16, 32, 64, 128, 256
  def graphviz_dot_text(self, items=GRAPH_MAIN | GRAPH_MAIN_DFS_INTERVAL | GRAPH_JUNGLE | GRAPH_DJ | GRAPH_LNF | GRAPH_SCC):
    strs = ""
    if (items & Digraph.GRAPH_MAIN) != 0:
      strs.append(self.graphviz_dot_digraph())
    if (items & Digraph.GRAPH_MAIN_DFS_INTERVAL) != 0:
      strs.append(self.graphviz_dot_digraph_interval())
    if (items & Digraph.GRAPH_DFST) != 0:
      strs.append(self.dfs_tree.graphviz_dot("t"))
    if (items & Digraph.GRAPH_JUNGLE) != 0:
      strs.append(self.graphviz_dot_jungle())
    if (items & Digraph.GRAPH_BFST) != 0:
      strs.append(self.graphviz_dot_bfst())
    if (items & Digraph.GRAPH_DOMTREE) != 0:
      strs.append(self.doms[self.sources[0]][0].graphviz_dot("d"))
    if (items & Digraph.GRAPH_DJ) != 0:
      strs.append(self.graphviz_dot_dj())
    if (items & Digraph.GRAPH_LNF) != 0:
      strs.append(self.graphviz_dot_lnf())
    if (items & Digraph.GRAPH_SCC) != 0:
      strs.append(self.graphviz_dot_text_scc_reach())
    graph.do_graphviz_dot_text(strs)
  def graphviz_dot_text_scc_reach(self): return sccreach.do_graphviz_dot_text_scc_reach(self.succ, self.djs_scc, self.sccs, self.reach)
  def graphviz_dot_text_scc_reach_comp(self, x, y): return sccreach.do_graphviz_dot_text_scc_reach_comp(x, y, self.succ, self.djs_scc, self.sccs)
  def graphviz_dot(self, output_dir): graph.do_graphviz_dot(self.graphviz_dot_text(), output_dir)
  def add_node(self, n):
    self.succ[n], self.pred[n] = set(), set()
    dfs.add_node_dfs(self.dfs_tree, self.dfs_int, self.dfs_revint, n)
    sccreach.add_node_reach_scc(n, self.djs_scc, self.sccs, self.reach)
    lnf.add_node_lnf(n, self.loopheaders, self.looptypes)
    self.check_graph()
  def remove_node(self, n):
    #print(n, self.succ[n], self.pred[n])
    if len(self.succ[n]) == 0 and len(self.pred[n]) == 0:
      del self.succ[n]; del self.pred[n]
      dfs.remove_node_dfs(self.dfs_tree, self.dfs_int, self.dfs_revint, n)
      sccreach.remove_node_reach_scc(n, self.djs_scc, self.sccs, self.reach)
      lnf.remove_node_lnf(n, self.loopheaders, self.looptypes)
    else: raise ValueError
    self.check_graph()
  def add_edge(self, x, y):
    self.succ[x].add(y); self.pred[y].add(x)
    self.inc_add_edge_dfs(x, y)
    self.inc_add_edge_bfs(x, y)
    self.inc_reach_scc(x, y)
    for source in self.sources:
      dominators.inc_dom_sreedhar_gao_lee(self.succ, *self.doms[source], x, y)
    lnf.inc_havlak_lnf(x, y, self.succ, self.pred, self.dfs_tree, self.dfs_int, self.loopcounts, self.loopheaders, self.looptypes, self.loopentries)
    self.check_graph()
  def remove_edge(self, x, y):
    assert y in self.succ[x]
    self.succ[x].remove(y); self.pred[y].remove(x)
    #print("Delete", x, y, self.classify_edge(x, y))
    cur_edge = self.classify_edge(x, y)
    self.dec_remove_edge_dfs(x, y)
    self.dec_remove_edge_bfs(x, y)
    #self.classify_deleted_edge(x, y, cur_edge)
    self.dec_reach_scc(x, y)
    lnf.dec_havlak_lnf(x, y, cur_edge == dfs.FORWARD_EDGE, self.succ, self.pred, self.dfs_tree, self.dfs_int, self.loopcounts, self.loopheaders, self.looptypes, self.loopentries)
    for source in self.sources:
      dominators.dec_dom_sreedhar_gao_lee(self.succ, self.pred, *self.doms[source], self.dfs_tree, self.dfs_int, self.loopentries, x, y)
    self.check_graph()
  def check_graph(self):
    visit, visited, ls, lp = set(self.succ), set(), 0, 0
    while len(visit) != 0:
      x = visit.pop()
      if x in visited: continue
      visited.add(x)
      ls += len(self.succ[x]); lp += len(self.pred[x])
      for y in self.succ[x]:
        if not x in self.pred[y]: raise ValueError("Bad Precessors")
        if not y in visited: visit.add(y)
    if ls != lp: raise ValueError("Bad Successors")
    dfs.check_dfs(self.sources, self.succ, self.dfs_tree, self.dfs_int, self.dfs_revint)
    lnf.check_havlak(self.succ, self.dfs_int, self.loopcounts, self.loopheaders, self.looptypes, self.loopentries)
    sccreach.check_scc(self.succ, self.djs_scc, self.sccs, self.reach)
    for source in self.sources:
      bfs.check_bfs(source, self.succ, *self.bfsts[source])
      dominators.check_dom(source, self.succ, *self.doms[source])
  def classify_edge(self, x, y): return dfs.do_classify_edge(self.dfs_tree, self.dfs_int, x, y)
  def isBackEdge(self, x, y): return dfs.do_isBackEdge(self.dfs_tree, self.dfs_int, x, y)
  def isForwardEdge(self, x, y): return dfs.do_isForwardEdge(self.dfs_tree, self.dfs_int, x, y)
  def isForwardCrossEdge(self, x, y): return dfs.do_isForwardCrossEdge(self.dfs_int, x, y)
  def isBackCrossEdge(self, x, y): return dfs.do_isBackCrossEdge(self.dfs_int, x, y)
  def isCrossEdge(self, x, y): return self.isBackCrossEdge(x, y) or self.isForwardCrossEdge(x, y)
  def isAncestor(self, x, y): return dfs.do_isAncestor(self.dfs_int, x, y)
  def inc_add_edge_dfs(self, x, y):
    dfs.do_inc_add_edge_dfs(self.succ, self.dfs_tree, self.dfs_int, self.dfs_revint, x, y)
  def dec_remove_edge_dfs(self, x, y):
    dfs.do_dec_remove_edge_dfs(self.succ, self.pred, self.dfs_tree, self.dfs_int, self.dfs_revint, x, y)
  def bfs(self, n, test_order=False):
    return bfs.do_bfs(n, self.succ, test_order)
  def inc_add_edge_bfs(self, x, y):
    for source in self.sources:
      bfs.do_inc_add_edge_bfs(self.succ, *self.bfsts[source], x, y)
  def dec_remove_edge_bfs(self, x, y):
    for source in self.sources:
      bfs.do_dec_remove_edge_bfs(self.pred, *self.bfsts[source], x, y)
  def inc_reach_scc(self, x, y):
    sccreach.do_inc_reach_scc(x, y, self.pred, self.djs_scc, self.sccs, self.reach)
  def dec_reach_scc(self, x, y):
    sccreach.do_dec_reach_scc(x, y, self.pred, self.succ, self.djs_scc, self.sccs, self.reach)
  def tarjan_dominators(self, source, use_ds=True):
    return dominators.tarjan_doms(source, self.succ, use_ds)
  def compute_idf(self, source, alphaNodes):
    return dominators.compute_idf(*self.doms[source], alphaNodes)
  def inc_reducible_tarjan_lnf(self, x, y):
    lnf.do_inc_reducible_tarjan_lnf(x, y, self.pred, self.dfs_tree, self.dfs_int, self.loopheaders, self.looptypes)
  def dec_reducible_tarjan_lnf(self, x, y, is_forward_edge):
    lnf.do_dec_reducible_tarjan_lnf(x, y, is_forward_edge, self.pred, self.dfs_tree, self.dfs_int, self.loopheaders, self.looptypes)
  def tarjan_is_reducible(self):
    return lnf.do_tarjan_is_reducible(self.pred, self.dfs_tree, self.dfs_int, self.dfs_revint)
  def tarjan_loops(self):
    return lnf.do_tarjan_loops(self.pred, self.dfs_tree, self.dfs_int, self.dfs_revint)
  def havlak_loops(self):
    return lnf.havlak_loops(self.pred, self.dfs_tree, self.dfs_int, self.dfs_revint)
  def linear_havlak_loops(self):
    return lnf.linear_havlak_loops(self.pred, self.dfs_tree, self.dfs_int, self.dfs_revint)
  def reduced_havlak_loops(self):
    return lnf.reduced_havlak_loops(self.pred, self.dfs_tree, self.dfs_int, self.dfs_revint)
  def new_algo_loops(self):
    return lnf.new_algo_loops(self.succ, self.dfs_int)
  def sreedhar_gao_lee_loops(self, source):
    return lnf.sreedhar_gao_lee_loops(self.pred, self.dfs_tree, self.dfs_int, self.doms[source][0])
  def modified_sreedhar_gao_lee_loops(self, source):
    return lnf.modified_sreedhar_gao_lee_loops(self.pred, self.dfs_tree, self.dfs_int, self.doms[source][0])
  def steensgaard_loops(self):
    return lnf.steensgaard_loops(self.pred, self.dfs_int)
  def graph_slice(self, source, sinks): #all paths between source ns and sink set
    Sg, dfsStack, visited = set(), [(source, None)], set() #node, iterator, visited
    while len(dfsStack) != 0:
      x, pre = dfsStack.pop()
      if pre is None:
        visited.add(x)
        pre = iter(self.succ[x])
      for y in pre:
        if not y in visited:
          dfsStack.append((x, pre)); dfsStack.append((y, None))
          if y in sinks: Sg |= set(z[0] for z in dfsStack)
          break
        elif y in Sg and not any(y == z[0] for z in dfsStack): Sg.add(x); Sg |= set(z[0] for z in dfsStack)
    return Sg
  def __repr__(self): return str(self)
  def __str__(self): return str(self.succ)

class ASTCFG(): #gotos become continues, breaks or labeled gotos, tree elisions can easily reconstruct original graph
  #IFTHEN, IFTHENELSE, WHILE, DOWHILE argument is a Boolean expression, CASE is an integral expression and a list of matching integral expressions
  #INFLOOP, SEQ is representative with no data, CODE is a string expression, GOTO is a label expression
  IFTHEN, IFTHENELSE, CASE, WHILE, DOWHILE, INFLOOP, SEQ, CODE, GOTO, RETURN, EXIT, CFGVAR = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
  def __init__(self):
    self.nodes, self.nodetypes, self.nodedata, self.current_nodepath = {}, {}, {}, []
    self.nodemap = {}
    self.enter_node()
  def enter_node(self):
    n = len(self.nodes) + 1
    self.nodes[n] = []
    self.nodetypes[n] = ASTCFG.SEQ
    self.nodedata[n] = None
    if len(self.current_nodepath) != 0: self.nodes[self.current_nodepath[-1]].append(n)
    self.current_nodepath.append(n)
  def leave_node(self):
    x = self.current_nodepath.pop()
    n = self.current_nodepath[-1]
    if self.nodetypes[n] == ASTCFG.IFTHENELSE:
      if len(self.nodes[n]) == 2: self.current_nodepath.pop()
      else: self.enter_node()
    elif self.nodetypes[n] == ASTCFG.CASE:
      if len(self.nodes[n]) == len(self.nodedata[n][1]): self.current_nodepath.pop()
      else: self.enter_node()
    elif self.nodetypes[n] in (ASTCFG.IFTHEN, ASTCFG.WHILE, ASTCFG.DOWHILE, ASTCFG.INFLOOP):
      self.current_nodepath.pop()
  def add_to_node(self, t, c):
    n = self.current_nodepath[-1]
    x = len(self.nodes) + 1
    self.nodes[x] = []
    self.nodetypes[x] = t
    self.nodedata[x] = c[1] if t in (ASTCFG.CODE, ASTCFG.RETURN, ASTCFG.EXIT) else c
    if t in (ASTCFG.CODE, ASTCFG.RETURN, ASTCFG.EXIT):
      self.nodemap[c[0]] = x
    self.nodes[n].append(x)
    if t in (ASTCFG.IFTHEN, ASTCFG.IFTHENELSE, ASTCFG.CASE, ASTCFG.WHILE, ASTCFG.DOWHILE, ASTCFG.INFLOOP):
      self.current_nodepath.append(x)
      self.enter_node()
  def goto_targets(self):
    s = [(1, None)]
    targets = set()
    while len(s) != 0:
      n, it = s.pop()
      if it is None:
        it = iter(self.nodes[n])
        if self.nodetypes[n] == ASTCFG.GOTO: targets.add(self.nodemap[self.nodedata[n]])
      x = next(it, None)
      if not x is None: s.append((n, it)); s.append((x, None))
    return targets
  def remove_deadcode(self, deadnodes):
    s = [(1, None)]
    while len(s) != 0:
      n, it = s.pop()
      if it is None:
        for x in deadnodes:
          if x in self.nodes[n]: self.nodes[n].remove(x)
        it = iter(self.nodes[n])
      x = next(it, None)
      if not x is None: s.append((n, it)); s.append((x, None))
    for x in deadnodes:
      del self.nodes[x]
      del self.nodetypes[x]
      del self.nodedata[x]
    self.nodemap = {x: self.nodemap[x] for x in self.nodemap if not self.nodemap[x] in deadnodes}
  def ast_to_graph(self, resolve_var):
    #rules: SEQ node elides to next SEQ node except for GOTO/RETURN
    #IFTHEN or IFTHENELSE or CASE nodes elide in next SEQ node
    #INFLOOP, WHILE elides to loop header
    #DOWHILE elides to latch node
    #if next SEQ node is last node in SEQ elides to containing block next SEQ node, leading to simple bottom-up tree traversal algorithm
    #code in SEQ node after DOWHILE whose latch is dead/INFLOOP/GOTO/RETURN is dead code and removed
    #code in SEQ node after IFTHENELSE/CASE is dead code if all children recursively terminate (no paths to follow node)
    #dead code only until next CODE, if and only if CODE is target of a GOTO
    #INFLOOP included as GOTOs to code target rule handles the scenario of a break
    #the only proper way to do this is to build a graph, find what is reachable from the root node via a DFS or BFS, and removing any nodes not reachable
    s = [(1, None)]
    nextseq = {1: None}
    termnodes = set()
    loopstarthead = {self.nodes[self.nodes[n][0]][0]:n for n in self.nodes if self.nodetypes[n] in (ASTCFG.INFLOOP, ASTCFG.DOWHILE)}
    g = {x: [] for x in self.nodes}
    while len(s) != 0:
      n, it = s.pop()
      if it is None:
        it = iter(self.nodes[n])
        if self.nodetypes[n] == ASTCFG.RETURN: termnodes.add(n)
        elif resolve_var and self.nodetypes[n] == ASTCFG.CFGVAR:
          x = self.nodemap[self.nodedata[n][1]]
          g[n].append(loopstarthead[x] if x in loopstarthead else x); termnodes.add(n)
        elif self.nodetypes[n] == ASTCFG.GOTO:
          x = self.nodemap[self.nodedata[n]]
          g[n].append(loopstarthead[x] if x in loopstarthead else x); termnodes.add(n)
        elif self.nodetypes[n] == ASTCFG.SEQ:
          if len(self.nodes[n]) != 0:
            termnodes.add(n)
            g[n].append(self.nodes[n][0])
            for i in range(len(self.nodes[n])-1):
              nextseq[self.nodes[n][i]] = self.nodes[n][i+1]
            nextseq[self.nodes[n][-1]] = nextseq[n]
        elif self.nodetypes[n] in (ASTCFG.IFTHEN, ASTCFG.IFTHENELSE, ASTCFG.CASE):
          g[n].extend(self.nodes[n])
          if self.nodetypes[n] == ASTCFG.IFTHENELSE and all(len(self.nodes[x]) != 0 for x in self.nodes[n]) or self.nodetypes[n] == ASTCFG.CASE and len(self.nodes[self.nodes[n][-1]]) != 0: termnodes.add(n)
          if self.nodetypes[n] == ASTCFG.CASE:
            for i in range(len(self.nodes[n])-1):
              nextseq[self.nodes[n][i]] = self.nodes[n][i+1]
            nextseq[self.nodes[n][-1]] = nextseq[n]
          else:
            for x in self.nodes[n]: nextseq[x] = nextseq[n]
        elif self.nodetypes[n] in (ASTCFG.WHILE, ASTCFG.INFLOOP, ASTCFG.DOWHILE):
          g[n].extend(self.nodes[n])
          if self.nodetypes[n] == ASTCFG.INFLOOP: termnodes.add(n)
          for x in self.nodes[n]: nextseq[x] = n
      x = next(it, None)
      if not x is None: s.append((n, it)); s.append((x, None))
    #any non-reachable code is dead code
    #if a DOWHILE condition is not reached, then it can be transformed to an INFLOOP
    #any goto which matches its next sequence can be eliminated as dead code
    for x in nextseq:
      if not x in termnodes:
        if self.nodetypes[x] == ASTCFG.DOWHILE:
          if not self.nodes[self.nodes[x][-1]][-1] in termnodes:
            g[self.nodes[self.nodes[x][-1]][-1]].append(nextseq[x])
          else: nextseq[x] = None
        else: g[x].append(nextseq[x])
    if not resolve_var:
      reachable = bfs.do_bfs(1, g)
      deadnodes = set(g) - set(reachable[1])
      #print(self.nodes, nextseq, g)
      self.remove_deadcode(deadnodes)
      for x in nextseq:
        while nextseq[x] in deadnodes:
          nextseq[x] = nextseq[nextseq[x]]
      for x in deadnodes:
        if x in nextseq: del nextseq[x]
        if x in termnodes: termnodes.remove(x)
        del g[x]
      #print("Removed dead nodes: ", deadnodes, termnodes)
    return g, nextseq, termnodes
  def calc_elision(self):
    revnodemap = {self.nodemap[x]: x for x in self.nodemap}
    s = [(1, None)]
    while len(s) != 0:
      n, it = s.pop()
      if it is None:
        it = iter(self.nodes[n])
        if self.nodetypes[n] == ASTCFG.SEQ and len(self.nodes[n]) != 0:
          for i in range(len(self.nodes[n])-1):
            if self.nodetypes[self.nodes[n][i]] == ASTCFG.CODE and not self.nodes[n][i+1] in revnodemap:
              revnodemap[self.nodes[n][i+1]] = revnodemap[self.nodes[n][i]]
      x = next(it, None)
      if not x is None: s.append((n, it)); s.append((x, None))
      elif self.nodetypes[n] == ASTCFG.SEQ:
        for i in range(len(self.nodes[n])-1, -1, -1):
          if not self.nodes[n][i] in revnodemap:
            if len(self.nodes[self.nodes[n][i]]) != 0:
              revnodemap[self.nodes[n][i]] = revnodemap[self.nodes[self.nodes[n][i]][0]]
            elif i != 0:
              if self.nodetypes[self.nodes[n][i-1]] == ASTCFG.DOWHILE:
                revnodemap[self.nodes[n][i]] = revnodemap[self.nodes[self.nodes[self.nodes[n][i-1]][-1]][-1]]
              else: revnodemap[self.nodes[n][i]] = revnodemap[self.nodes[n][i-1]]
      elif self.nodetypes[n] in (ASTCFG.IFTHEN, ASTCFG.IFTHENELSE, ASTCFG.CASE, ASTCFG.WHILE, ASTCFG.INFLOOP, ASTCFG.DOWHILE):
        for x in self.nodes[n]:
          if len(self.nodes[x]) == 0: revnodemap[x] = revnodemap[n]
          elif self.nodes[x][0] in revnodemap: revnodemap[x] = revnodemap[self.nodes[x][0]]
          else: revnodemap[self.nodes[x][0]] = revnodemap[x] = revnodemap[n]
        if self.nodetypes[n] in (ASTCFG.INFLOOP, ASTCFG.DOWHILE): revnodemap[n] = revnodemap[self.nodes[n][0]]
    revnodemap[1] = revnodemap[self.nodes[1][0]]
    return revnodemap
  def check_vars(self): #each var can only follow one path to its destination
    g = self.to_graph()
    s = [(1, None)]
    while len(s) != 0:
      n, it = s.pop()
      if it is None:
        it = iter(self.nodes[n])
        if self.nodetypes[n] == ASTCFG.CFGVAR:
          src, dest = n, self.nodemap[self.nodedata[n][1]]
          while src != dest:
            assert len(g[src]) != 0
            if len(g[src]) == 1: src = next(iter(g[src]))
            elif len(g[src]) == 2: #IFTHEN, IFTHENELSE, WHILE, DOWHILE
              assert self.nodedata[src][0] == self.nodedata[n] or "!" + self.nodedata[src][0] == self.nodedata[n]
              #src = self.nodedata[src][0] == self.nodedata[n]
            else:
              assert self.nodedata[n][0] == self.nodedata[src][0]
              src = self.nodes[self.nodedata[src][1].index(self.nodedata[n][1])]
      x = next(it, None)
      if not x is None: s.append((n, it)); s.append((x, None))
  def to_graph(self):
    self.raw_ast()
    origg, nextseq, termnodes = self.ast_to_graph(True)
    revnodemap = self.calc_elision()
    g = {x: [] for x in self.nodemap}; g[2].append(3); g[3] = []
    s = [(1, None)]
    #loops, loopswitchs = [], []
    while len(s) != 0:
      n, it = s.pop()
      if it is None:
        it = iter(self.nodes[n])
        if self.nodetypes[n] == ASTCFG.GOTO:
          g[revnodemap[n]].append(self.nodedata[n])
        elif self.nodetypes[n] == ASTCFG.CFGVAR:
          g[revnodemap[n]].append(self.nodedata[n][1])
        elif self.nodetypes[n] in (ASTCFG.IFTHEN, ASTCFG.IFTHENELSE, ASTCFG.CASE, ASTCFG.WHILE, ASTCFG.INFLOOP, ASTCFG.DOWHILE):
          g[revnodemap[n]].extend(revnodemap[x] for x in self.nodes[n] if revnodemap[x] != revnodemap[n])
        if not n in termnodes and not nextseq[n] is None and not revnodemap[nextseq[n]] in g[revnodemap[n]] and (revnodemap[nextseq[n]] != revnodemap[n] or self.nodetypes[nextseq[n]] in (ASTCFG.WHILE, ASTCFG.DOWHILE, ASTCFG.INFLOOP)):
          if self.nodetypes[n] == ASTCFG.DOWHILE:
            if not self.nodes[self.nodes[n][-1]][-1] in termnodes and revnodemap[nextseq[n]] != revnodemap[self.nodes[self.nodes[n][-1]][-1]]:
              g[revnodemap[self.nodes[self.nodes[n][-1]][-1]]].append(revnodemap[nextseq[n]])            
          else: g[revnodemap[n]].append(revnodemap[nextseq[n]])
        #if self.nodetypes[n] == ASTCFG.CASE: loopswitchs.append(nextseq[n])
        #elif self.nodetypes[n] in (ASTCFG.WHILE, ASTCFG.INFLOOP):
        #  loops.append(n); loopswitchs.append(nextseq[n])
        #elif self.nodetypes[n] == ASTCFG.DOWHILE:
        #  loops.append(self.nodes[self.nodes[n][-1]][-1]); loopswitchs.append(nextseq[n])
      x = next(it, None)
      if not x is None: s.append((n, it)); s.append((x, None))
      #elif self.nodetypes[n] in (ASTCFG.DOWHILE, ASTCFG.WHILE, ASTCFG.INFLOOP): loops.pop(); loopswitchs.pop()
      #elif self.nodetypes[n] == ASTCFG.CASE: loopswitchs.pop()
    if 0 in g: del g[0] #for state machine
    #print(g, self.nodes, self.nodemap, revnodemap, nextseq)
    return {x: set(g[x]) for x in g}
  def min_ast(self): pass
  def raw_ast(self):
    origg, nextseq, termnodes = self.ast_to_graph(False)
    assert (origg, nextseq, termnodes) == self.ast_to_graph(False), ((origg, nextseq, termnodes), self.ast_to_graph(False))
    g, nextseq, termnodes = self.ast_to_graph(True)
    revnodemap = self.calc_elision()
    code = "void cfg() {\n"
    indent, s = 1, [(1, None)]
    while len(s) != 0:
      n, it = s.pop()
      if it is None:
        it = iter(self.nodes[n])
        code += "//node: " + str(n) + " Elision: " + str(nextseq[n]) + " Original: " + str(revnodemap[n]) + ("!" if self.nodemap[revnodemap[n]] == n else "") + "\n"
        if self.nodetypes[n] != ASTCFG.SEQ: code += "\t"*indent; indent += 1
        if self.nodetypes[n] in (ASTCFG.CODE, ASTCFG.RETURN): code += "L" + str(revnodemap[n]) + ": "
        if self.nodetypes[n] == ASTCFG.GOTO:
          code += "goto " + "L" + str(self.nodedata[n]) + ";\n"
        elif self.nodetypes[n] == ASTCFG.CODE and not self.nodedata[n] is None:
          code += self.nodedata[n] #+ "\n"
        elif self.nodetypes[n] == ASTCFG.CFGVAR:
          code += self.nodedata[n][0] + " = " + str(self.nodedata[n][1]) + ";\n"
        elif self.nodetypes[n] == ASTCFG.RETURN:
          code += "return;\n"
        elif self.nodetypes[n] in (ASTCFG.IFTHEN, ASTCFG.IFTHENELSE):
          code += "if (" + self.nodedata[n] + ") {\n"
        elif self.nodetypes[n] == ASTCFG.CASE:
          code += "switch (" + self.nodedata[n][0] + ") {\n"
        elif self.nodetypes[n] == ASTCFG.INFLOOP:
          code += "while (true) {\n"
        elif self.nodetypes[n] == ASTCFG.WHILE:
          code += "while (" + self.nodedata[n] + ") {\n"
        elif self.nodetypes[n] == ASTCFG.DOWHILE:
          code += "do {\n"        
      x = next(it, None)
      if not x is None:
        if self.nodetypes[n] == ASTCFG.CASE:
          code += "\t"*(indent-1) + "case " + str(self.nodedata[n][1][self.nodes[n].index(x)]) + ":\n"
        elif self.nodetypes[n] == ASTCFG.IFTHENELSE and x == self.nodes[n][1]:
          code += "\t"*(indent-1) + "} else {\n"
        s.append((n, it)); s.append((x, None))
      else:
        if self.nodetypes[n] != ASTCFG.SEQ: indent -= 1
        if self.nodetypes[n] in (ASTCFG.IFTHEN, ASTCFG.IFTHENELSE, ASTCFG.CASE, ASTCFG.WHILE, ASTCFG.INFLOOP):
          code += "\t"*indent + "}\n"
        elif self.nodetypes[n] == ASTCFG.DOWHILE:
          code += "\t"*indent + "} while (" + self.nodedata[n] + ");\n"
    code += "}\n"
    #print(code)
  def to_ast(self):
    assert self.current_nodepath == [1]

#labels and gotos will be represented specially
class AST(graph.Tree): #child ordered tree
  IFNODE, SWITCHNODE, WHILENODE, DOWHILENODE, SEQNODE, CODENODE, LABELNODE = 1, 2, 3, 4, 5, 6, 7
  def __init__(self):
    self.nodestatements = {}
class IntegralComparison:
  EQ, NEQ, LT, GT, LTE, GTE = 1, 2, 3, 4, 5, 6
  def __init__(self, op, left, right): #integral value on right
    self.op, self.left, self.right = op, left, right
  def isCommon(self, other):
    return self.left == other.left
class BoolExp:
  VAR, FALSE, TRUE, AND, OR, XOR, NOT = 1, 2, 3, 4, 5, 6, 7 #NAND, NOR, XNOR
  def __init__(self, op, nodes):
    while (op == BoolExp.AND or op == BoolExp.OR or op == BoolExp.XOR) and len(nodes) == 1:
      op, nodes = nodes[0].op, nodes[0].nodes
    if op == BoolExp.VAR or op == BoolExp.NOT: assert len(nodes) == 1
    elif op == BoolExp.FALSE or op == BoolExp.TRUE: assert len(nodes) == 0
    elif op == BoolExp.AND and len(nodes) == 0: op = BoolExp.TRUE #similar to all([])
    elif op == BoolExp.OR and len(nodes) == 0: op = BoolExp.FALSE #similar to any([])
    elif op == BoolExp.XOR and len(nodes) == 0: op = BoolExp.FALSE #empty sum mod 2
    self.op, self.nodes = op, tuple(nodes)
  def isTrue(self):
    return self.simplify().op == BoolExp.TRUE
  def isFalse(self):
    return self.simplify().op == BoolExp.FALSE
  def doubleOrLiteralNegation(self):
    #Double Negation: NOT NOT ... -> ...
    if self.op == BoolExp.NOT and self.nodes[0].op == BoolExp.NOT:
      return self.nodes[0].nodes[0]
    elif self.op == BoolExp.NOT and self.nodes[0].op == BoolExp.TRUE:
      return BoolExp(BoolExp.FALSE, [])
    elif self.op == BoolExp.NOT and self.nodes[0].op == BoolExp.FALSE:
      return BoolExp(BoolExp.TRUE, [])
    return self
  def annulment(self):
    #Annulment: A+1=1 A.0=0
    if self.op == BoolExp.OR and any(x.op == BoolExp.TRUE for x in self.nodes):
      return BoolExp(BoolExp.TRUE, [])
    elif self.op == BoolExp.AND and any(x.op == BoolExp.FALSE for x in self.nodes):
      return BoolExp(BoolExp.FALSE, [])      
    elif self.op == BoolExp.XOR: #Annulment: A XOR A=0
      s = set()
      for x in self.nodes:
        if x in s: s.remove(x)
        else: s.add(x)
      if len(s) != len(self.nodes): return BoolExp(self.op, list(s))
    return self
  def associativity(self):
    import itertools
    #Associativity: BOP (BOP ...) (...) -> BOP ... (...) where BOP=AND/OR/XOR
    if self.op == BoolExp.AND or self.op == BoolExp.OR or self.op == BoolExp.XOR:
      t1, t2 = itertools.tee(self.nodes)
      pred = lambda x: x.op == self.op
      p1, p2 = itertools.filterfalse(pred, t1), list(filter(pred, t2))
      if len(p2) != 0: return BoolExp(self.op, [*p1, *(y for x in p2 for y in x.nodes)])
    return self
  def idempotency(self):
    #Idempotency: A+A=A, A.A=A
    if self.op == BoolExp.OR or self.op == BoolExp.AND:
      s = set(self.nodes)
      if len(s) != len(self.nodes): return BoolExp(self.op, list(s))
    return self
  def identity(self):
    #Identity: A+0=A, A.1=A, A XOR 0=A
    if self.op == BoolExp.OR or self.op == BoolExp.XOR:
      nodes = list(filter(lambda x: x.op != BoolExp.FALSE, self.nodes))
      if len(nodes) != len(self.nodes): return BoolExp(self.op, nodes)
    elif self.op == BoolExp.AND:
      nodes = list(filter(lambda x: x.op != BoolExp.TRUE, self.nodes))
      if len(nodes) != len(self.nodes): return BoolExp(self.op, nodes)
    return self
  def complement(self):
    #Complement: A+!A=1, A.!A=0
    if self.op == BoolExp.AND or self.op == BoolExp.OR:
      s = set(self.nodes)
      if any(BoolExp(BoolExp.NOT, [x]).simplifyNot() in s for x in self.nodes):
        return BoolExp(BoolExp.TRUE if self.op == BoolExp.OR else BoolExp.FALSE, [])
    elif self.op == BoolExp.XOR: #A XOR !A XOR ...=1 XOR ...
      s = set(self.nodes)
      dups = 0
      for x in self.nodes:
        nx = BoolExp(BoolExp.NOT, [x]).simplifyNot()
        if nx in s: s.remove(nx); s.remove(x); dups += 1
      if len(s) != len(self.nodes):
        return BoolExp(self.op, list(s) if (dups & 1) == 0 else [BoolExp(BoolExp.TRUE, []), *s])
    return self
  def absorptive(self):
    #Absorptive: A+(A.B)=A A(A+B)=A
    if self.op == BoolExp.AND or self.op == BoolExp.OR:
      s = set(self.nodes)
      for x in self.nodes:
        if x.op == (BoolExp.OR if self.op == BoolExp.AND else BoolExp.AND):
          if len(s.intersection(set(x.nodes))) != 0:
            s.remove(x)
      if len(s) != len(self.nodes): return BoolExp(self.op, list(s))
    return self
  def deMorgan(self):
    #DeMorgan's law (NAND, NOR): !(A.B)=!A+!B, !(A+B)=!A.!B
    if self.op == BoolExp.NOT and self.nodes[0].op == BoolExp.AND:
      return BoolExp(BoolExp.OR, [BoolExp(BoolExp.NOT, [x]).simplifyNot() for x in self.nodes[0].nodes])
    elif self.op == BoolExp.NOT and self.nodes[0].op == BoolExp.OR:
      return BoolExp(BoolExp.AND, [BoolExp(BoolExp.NOT, [x]).simplifyNot() for x in self.nodes[0].nodes])
    elif self.op == BoolExp.NOT and self.nodes[0].op == BoolExp.XOR: #!(A XOR B XOR ...) = !A XOR B XOR ...
      return BoolExp(BoolExp.XOR, [BoolExp(BoolExp.NOT, [self.nodes[0].nodes[0]]).simplifyNot(), *self.nodes[0].nodes[1:]])
    return self
  def nonExpansiveDistributive(self):
    #Non-expansive distributive: A(!A+B)=AB, A+(!A.B)=A+B
    if self.op == BoolExp.AND:
      s = set(self.nodes)
      for x in self.nodes:
        search = BoolExp(BoolExp.NOT, [x]).simplifyNot()
        for y in self.nodes:
          if y.op == BoolExp.OR and search in y.nodes:
            s.remove(y)
            return BoolExp(self.op, [BoolExp(y.op, [z for z in y.nodes if z != search]), *s])
    elif self.op == BoolExp.OR:
      s = set(self.nodes)
      for x in self.nodes:
        search = BoolExp(BoolExp.NOT, [x]).simplifyNot()
        for y in self.nodes:
          if y.op == BoolExp.AND and search in y.nodes:
            s.remove(y)
            return BoolExp(self.op, [BoolExp(y.op, [z for z in y.nodes if z != search]), *s])
    return self
  def toDNF(self): #disjunctive normal form
    if self.op == BoolExp.TRUE or self.op == BoolExp.FALSE: return self
    exp = BoolExp(self.op, [x.toDNF() if isinstance(x, BoolExp) else x for x in self.nodes])
    exp = exp.simplifyNot()
    exp = exp.annulment()
    exp = exp.associativity()
    exp = exp.idempotency()
    exp = exp.identity()
    exp = exp.complement()
    exp = exp.absorptive()
    exp = exp.nonExpansiveDistributive()
    #XOR: A XOR B=A!B+!AB=(A+B)(!A+!B)
    if exp.op == BoolExp.XOR:
      remain = BoolExp(exp.op, exp.nodes[1:]).toDNF()
      exp = BoolExp(BoolExp.OR, [BoolExp(BoolExp.AND, [exp.nodes[0], BoolExp(BoolExp.NOT, [remain])]), BoolExp(BoolExp.AND, [BoolExp(BoolExp.NOT, [exp.nodes[0]]), remain])]).toDNF()
    #Distributive: A(B+C)=AB+AC
    if exp.op == BoolExp.AND:
      s = set(exp.nodes)
      for x in exp.nodes:
        if x.op == BoolExp.OR:
          s.remove(x)
          exp = BoolExp(x.op, [BoolExp(exp.op, [y, *s]) for y in x.nodes]).toDNF()
          break
    return exp
  def toCNF(self): #conjunctive normal form
    if self.op == BoolExp.TRUE or self.op == BoolExp.FALSE: return self
    exp = BoolExp(self.op, [x.toCNF() if isinstance(x, BoolExp) else x for x in self.nodes])
    exp = exp.simplifyNot()
    exp = exp.annulment()
    exp = exp.associativity()
    exp = exp.idempotency()
    exp = exp.identity()
    exp = exp.complement()
    exp = exp.absorptive()
    exp = exp.nonExpansiveDistributive()
    #XOR: A XOR B=A!B+!AB=(A+B)(!A+!B)
    if exp.op == BoolExp.XOR:
      remain = BoolExp(exp.op, exp.nodes[1:]).toCNF()
      exp = BoolExp(BoolExp.AND, [BoolExp(BoolExp.OR, [exp.nodes[0], remain]), BoolExp(BoolExp.OR, [BoolExp(BoolExp.NOT, [exp.nodes[0]]), BoolExp(BoolExp.NOT, [remain])])]).toCNF()
    #Distributive: A+(BC)=(A+B)(A+C)
    if exp.op == BoolExp.OR:
      s = set(exp.nodes)
      for x in exp.nodes:
        if x.op == BoolExp.AND:
          s.remove(x)
          exp = BoolExp(x.op, [BoolExp(exp.op, [y, *s]) for y in x.nodes]).toCNF()
          break
    return exp
  def toANF(self): #algebraic normal form
    if self.op == BoolExp.TRUE or self.op == BoolExp.FALSE: return self
    exp = BoolExp(self.op, [x.toANF() if isinstance(x, BoolExp) else x for x in self.nodes])
    #NOT A -> 1 XOR A
    if exp.op == BoolExp.NOT:
      exp = BoolExp(BoolExp.XOR, [BoolExp(BoolExp.TRUE, []), exp.nodes[0]])
    #A OR B -> A XOR B XOR AB
    if exp.op == BoolExp.OR:
      exp = BoolExp(exp.op, [BoolExp(BoolExp.XOR, [exp.nodes[0], exp.nodes[1], BoolExp(BoolExp.AND, exp.nodes[:2])]), *exp.nodes[2:]]).toANF()
    #Distributive: A(B XOR C)=AB XOR AC
    if exp.op == BoolExp.AND:
      s = set(exp.nodes)
      for x in exp.nodes:
        if x.op == BoolExp.XOR:
          s.remove(x)
          exp = BoolExp(x.op, [BoolExp(exp.op, [y, *s]) for y in x.nodes]).toANF()
          break
    exp = exp.annulment()
    exp = exp.idempotency()
    exp = exp.identity()
    exp = exp.complement()
    exp = exp.associativity()          
    return exp
  def simplifyNot(self):
    exp = self
    exp = exp.doubleOrLiteralNegation()
    exp = exp.deMorgan()
    return exp
  def simplify(self):
    if self.op == BoolExp.TRUE or self.op == BoolExp.FALSE: return self
    exp = BoolExp(self.op, [x.simplify() if isinstance(x, BoolExp) else x for x in self.nodes])
    exp = exp.simplifyNot()
    exp = exp.annulment()
    exp = exp.associativity()
    exp = exp.idempotency()
    exp = exp.identity()
    exp = exp.complement()
    exp = exp.absorptive()
    exp = exp.nonExpansiveDistributive()
    #XOR: A!B+!AB=(A+B)(!A+!B)=A XOR B
    #XNOR: AB+!A!B=(A+!B)(!A+B)=A XNOR B=NOT (A XOR B)
    #Material conditional: x->y=!x+y
    #Distributive (only one can be applied so only for normal forms otherwise infinite expansion): A(B+C)=AB+AC A+(B.C)=(A+B).(A+C) A(B XOR C)=AB XOR AC
    #Tseytin transformation
    return exp
  def factor(a, b):
    pass #return common, left, right
  def __hash__(self):
    return hash((self.op, frozenset(self.nodes)))
  ANF, CNF, DNF = 1, 2, 3
  def checkEq(self, other, form=ANF):
    if form == BoolExp.ANF:
      a, b = self.toANF(), other.toANF()
    elif form == BoolExp.CNF:
      a, b = self.toCNF(), other.toCNF()
    elif form == BoolExp.DNF:
      a, b = self.toDNF(), other.toDNF()
    return a.op == b.op and set(a.nodes) == set(b.nodes)
  def __eq__(self, other):
    if isinstance(other, BoolExp):
      return self.checkEq(other)
    return NotImplemented
  def __rep__(self): return str(self)
  def opPriority(op):
    if op == BoolExp.NOT: return 1
    elif op == BoolExp.AND: return 2
    elif op == BoolExp.XOR: return 3
    elif op == BoolExp.OR: return 4
    else: return 0 #TRUE, FALSE, VAR
  def paren(self, innerop, innertext):
    return innertext if BoolExp.opPriority(self.op) >= BoolExp.opPriority(innerop) else "(" + innertext + ")"
  def __str__(self): #precedence: NOT > AND > XOR > OR
    if self.op == BoolExp.VAR: return str(self.nodes[0])
    if self.op == BoolExp.TRUE: return "1"
    elif self.op == BoolExp.FALSE: return "0"
    elif self.op == BoolExp.NOT: return "¬" + self.paren(self.nodes[0].op, str(self.nodes[0])) #"!"
    elif self.op == BoolExp.AND: return "⋅".join(self.paren(self.nodes[0].op, str(x)) for x in self.nodes) #"."
    elif self.op == BoolExp.OR: return "+".join(self.paren(self.nodes[0].op, str(x)) for x in self.nodes)
    elif self.op == BoolExp.XOR: return "⊕ ".join(self.paren(self.nodes[0].op, str(x)) for x in self.nodes) #Unicode Character Circled Plus “⊕” (U+2295)

#for functions, return node is an acceptable multi-exit case from loops or conditionals, but nonetheless we make it single-exit for simplification of evaluation
#out-of-band exit cases however are multi-exit case from loops or conditionals, which cannot be restructured without eliminating functions by inlining or using loops
#but they do not require any specific evaluation given the special case of termination
#in case of no normal returns and all exits, the return node can be fictitiously attached to the exit node
#the key is that the exit node should not be considered as part of the post-dominators for the non-exit nodes
class CFG(Digraph):
  def __init__(self, root=1, ret=2, exit=3, init=None, node_order=None):
    Digraph.__init__(self, [root])
    self.ret = ret
    Digraph.add_node(self, ret)
    Digraph.add_node(self, exit)
    Digraph.add_edge(self, ret, exit)
    self.rev_graph = Digraph([exit, ret])
    self.rev_graph.add_node(root)
    self.rev_graph.add_edge(exit, root)
    self.rev_graph.add_edge(exit, ret)
    if not init is None:
      for x in range(1, len(init)+1):
        if x != root and x != ret and x != exit: self.add_node(x if node_order is None else node_order[x - 1] + 1)
      for i, x in enumerate(init):
        if not node_order is None: i = node_order[i]; x = init[i]
        for y in x:
          self.add_edge(i + 1, y)
          self.remove_edge(i + 1, y)
          self.add_edge(i + 1, y)
    #nodes with multiple successors are conditions, and those edges values
    self.basic_blocks, self.conditions, self.cond_values = {}, {}, {}
    for x in self.succ:
      self.basic_blocks[x] = x
      if len(self.succ[x]) >= 2:
        self.conditions[x] = x
        for i, y in enumerate(self.succ[x]):
          self.cond_values[(x, y)] = i == 0 if len(self.succ[x]) == 2 else i
  def add_node(self, n):
    Digraph.add_node(self, n)
    self.rev_graph.add_node(n)
    self.rev_graph.add_edge(self.rev_graph.sources[0], n)
  def remove_node(self, n):
    Digraph.remove_node(self, n)
    self.rev_graph.remove_node(n)
    self.rev_graph.remove_edge(self.rev_graph.sources[0], n)
  def add_edge(self, x, y):
    Digraph.add_edge(self, x, y)
    retreach = set(self.rev_graph.bfsts[self.ret][0].pred)
    self.rev_graph.add_edge(y, x)
    additions, removals = [], []
    if x == self.ret and y == self.rev_graph.sources[0]: return
    if not x in retreach and x in self.rev_graph.bfsts[self.ret][0].pred:
      for u in set(self.rev_graph.bfsts[self.ret][0].pred) - retreach:
        for v in self.rev_graph.pred[u]:
          if not v in self.rev_graph.bfsts[self.ret][0].pred:
            removals.append((v, u))
        for v in self.pred[u] - self.rev_graph.succ[u]:
          additions.append((u, v))
    elif not x in retreach:
      u, bFirst = self.rev_graph.djs_scc.find(y), True
      for v in self.rev_graph.reach[u]:
        if v in self.rev_graph.succ[self.rev_graph.sources[0]]:
          if v in self.rev_graph.sccs[u] and bFirst: bFirst = False; continue
          removals.append((self.rev_graph.sources[0], v))
    for u, v in removals: self.rev_graph.remove_edge(u, v)
    for u, v in additions: self.rev_graph.add_edge(u, v)
    self.check_cfg()
  def remove_edge(self, x, y):
    Digraph.remove_edge(self, x, y)
    retreach = set(self.rev_graph.bfsts[self.ret][0].pred)
    self.rev_graph.remove_edge(y, x)
    additions, removals = [], []
    if x == self.ret and y == self.rev_graph.sources[0]: return
    if x in retreach and not x in self.rev_graph.bfsts[self.ret][0].pred:
      for u in retreach - set(self.rev_graph.bfsts[self.ret][0].pred):
        for v in self.succ[u]:
          if not v in self.rev_graph.pred[u]:
            additions.append((v, u))
        for v in self.rev_graph.succ[u]:
          if v in self.rev_graph.bfsts[self.ret][0].pred:
            removals.append((u, v))
      u = self.rev_graph.djs_scc.find(x)
      if all(self.rev_graph.pred[v].issubset(self.rev_graph.sccs[u]) for v in self.rev_graph.sccs[u]):
        additions.append((self.rev_graph.sources[0], u))
    elif not x in retreach:
      for u in self.rev_graph.sccs:
        if u == self.rev_graph.sources[0]: continue
        if all(self.rev_graph.pred[v].issubset(self.rev_graph.sccs[u]) for v in self.rev_graph.sccs[u]):
          additions.append((self.rev_graph.sources[0], u))
    for u, v in removals: self.rev_graph.remove_edge(u, v)
    for u, v in additions: self.rev_graph.add_edge(u, v)
    self.check_cfg()
  def check_cfg(self):
    assert self.get_rev_graph().succ == self.rev_graph.succ, (self.get_rev_graph().succ, self.rev_graph.succ)
    assert self.rev_graph.doms[self.rev_graph.sources[0]][0].pred == self.get_post_dom().pred
    #self.graphviz_dot(output_dir); assert False, (cfg.rev_graph.doms[cfg.rev_graph.sources[0]][0].pred, cfg.get_post_dom().pred)
    assert self.findImmPostDominators().pred == self.post_doms(), (self.findImmPostDominators(), self.post_doms())
    assert self.get_fixed_revgraph_post_dom().pred == self.rev_graph.doms[self.rev_graph.sources[0]][0].pred, (self.get_fixed_revgraph_post_dom().pred, self.rev_graph.doms[self.rev_graph.sources[0]][0].pred)

  def minimum_root_connectivity(self):
    realsucc = {**self.succ}
    realsucc[self.sources[0]] = self.root_succ
    sccs, reach = Digraph.nuutila_reach_scc(realsucc)
    roots = {x for x in sccs}
    for z in sccs:
      isSCC = z in roots and z in reach[z]
      roots -= reach[z]
      if isSCC: roots.add(z)
    roots.remove(self.sources[0])
    return roots
  def graphviz_dot_text_rev_dj(self):
    s = self.graphviz_dot_digraph()
    t = self.graphviz_dot_digraph_interval()
    rs = self.rev_graph.graphviz_dot_digraph("r")
    rt = self.rev_graph.graphviz_dot_digraph_interval("r")
    dj = self.graphviz_dot_dj()
    correctpdom = self.get_post_dom().graphviz_dot("c")    
    #rdj = self.rev_graph.graphviz_dot_dj("rd")
    #pdom = self.get_fixed_revgraph_post_dom().graphviz_dot("rd") 
    pdom = self.rev_graph.doms[self.rev_graph.sources[0]][0].graphviz_dot("tc")
    return graph.do_graphviz_dot_text([s, t, rs, rt, dj, correctpdom, pdom])
  def graphviz_dot(self, output_dir):
    graph.do_graphviz_dot(self.graphviz_dot_text_rev_dj(), output_dir)
  def reaches(self, x):
    r = set()
    def inner_reaches(z):
      r.add(z)
      for y in self.pred[z]:
        if not y in r: inner_reaches(y)
    inner_reaches(x)
    return r
  def get_interval(head, succ, pred):
    ival = {}
    heads = {head}
    while len(heads) != 0:
      n = heads.pop()
      ival[n] = {n}
      while True:
        newval = {m for m in succ if not m in ival[n] and not m in ival and all(p in ival[n] for p in pred[m])}
        if len(newval) == 0: break
        ival[n] |= newval
      heads |= {m for m in succ if not m in heads and not m in ival[n] and not m in ival and any(p in ival[n] for p in pred[m])}
    return ival
  #derived sequence algorithm
  #the final graph is not always the canonical irreducible graph if there are multiple irreducible loops
  def get_intervals(self):
    g = [(self.sources[0], self.succ, self.pred)]
    i = [CFG.get_interval(*g[-1])]
    while True:
      revint = {}
      for ihead in i[-1]:
        for node in i[-1][ihead]: revint[node] = ihead
      #O(n^2) - can be optimized to O(m)
      gi = (self.sources[0], {m:[n for n in i[-1] if n!=m and any(k in g[-1][1][j] for j in i[-1][m] for k in i[-1][n])] for m in i[-1]}, {m: [n for n in i[-1] if n!=m and any(k in g[-1][2][m] for k in i[-1][n])] for m in i[-1]})
      if gi == g[-1]: assert(len(g[-1][1]) == 1 or len(i[-1]) == len(CFG.get_interval(*g[-1]))), g[-1]; break
      g.append(gi)
      i.append(CFG.get_interval(*g[-1]))
    return g, i
  SEQ, LOOP, COND, LOOPCOND = 1, 2, 3, 4 #structType
  IFTHEN, IFELSE, IFTHENELSE, CASE = 1, 2, 3, 4 #condType
  PRETESTED, POSTTESTED, ENDLESS = 1, 2, 3 #loopType
  def isReturn(self, n): return self.ret == n
  def tagNodesInCase(self, n, h, f, caseHead, structType, condFollow):
    if n != h: caseHead[n] = h
    if n in structType and structType[n] == CFG.CASE and condFollow[n] != f:
      self.tagNodesInCase(condFollow[n], h, f, caseHead, structType, condFollow)
    else:
      for c in self.succ[n]:
        if not c in caseHead and c != f and not self.isBackEdge(n, c):
          self.tagNodesInCase(c, h, f, caseHead, structType, condFollow)
  def structConds(self):
    structType, condType, caseHead, condFollow = {}, {}, {}, {}
    for widx in self.dfs_revint: #reverse post-order
      n = self.dfs_revint[widx]
      if n == 0 or self.dfs_int[n][0] == widx: continue
      if len(self.succ[n]) <= 1: continue
      structType[n] = CFG.COND
      if any(self.isBackEdge(n, m) for m in self.succ[n]) and len(self.succ[n]) == 2:
        condType[n] = CFG.IFTHENELSE; continue
      condFollow[n] = self.post_dom_tree().pred[n]
      f = condFollow[n]
      if len(self.succ[n]) >= 3:
        condType[n] = CFG.CASE
        self.tagNodesInCase(n, n, f, caseHead, structType, condFollow)
      elif not f in self.succ[n]: condType[n] = CFG.IFTHENELSE
      else: condType[n] = CFG.IFELSE if self.cond_values[(n, f)] else CFG.IFTHEN
    return structType, condType, caseHead, condFollow
  def loopNodes(self, y, x, ival):
    nodesInLoop = set()
    for idx in range(self.dfs_int[y][1], self.dfs_int[x][1]):
      n = self.dfs_revint[idx]
      if self.dfs_int[n][0] == idx or not n in ival: continue
      nodesInLoop.add(n)
    return nodesInLoop
  def inParen(x, y, paren):
    return paren[0][y][0] < paren[0][x][0] < paren[0][x][1] < paren[0][y][1] or paren[1][y][0] < paren[1][x][0] < paren[1][x][1] < paren[1][y][1]
  def setParenthesis(self):
    truesucc = {x: list(sorted(self.succ[x], key=lambda y: None if not (x, y) in self.cond_values else self.cond_values[(x, y)])) for x in self.succ}
    return (dfs.do_dfs(self.sources, truesucc)[1], dfs.do_dfs(self.sources, {x: list(reversed(truesucc[x])) for x in truesucc})[1])
  def loopNodesParenthesis(self, y, x, paren):
    nodesInLoop = set()
    for idx in range(self.dfs_int[y][1], self.dfs_int[x][1]):
      m = self.dfs_revint[idx]
      if self.dfs_int[m][0] == idx: continue
      if CFG.inParen(m, x, paren) and (CFG.inParen(y, m, paren) or m == y):
        nodesInLoop.add(m)
    return nodesInLoop
  def loopStructParen(self, structType, caseHead, condFollow, paren):
    loopHead, loopType, loopFollow, loopLatch = {}, {}, {}, {}
    for widx in self.dfs_revint:
      h = self.dfs_revint[widx]
      if h == 0 or self.dfs_int[h][1] == widx: continue
      for x in self.pred[h]:
        if (loopHead[x] == loopHead[h] if x in loopHead and h in loopHead else not x in loopHead and not h in loopHead) and (caseHead[x] == caseHead[h] if x in caseHead and h in caseHead else not x in caseHead and not h in caseHead) and self.isBackEdge(x, h) and not any(self.dfs_int[y][1] < self.dfs_int[x][1] for y in self.pred[h]):
          #if x != h: structType[x] = CFG.SEQ
          structType[h] = CFG.LOOP
          nodesInLoop = self.markNodesInLoop(h, self.loopNodesParenthesis(x, h, paren), loopHead, True)
          self.findLoopType(x, h, nodesInLoop, loopType, structType, condFollow)
          self.findLoopFollow(x, h, nodesInLoop, loopType, loopFollow, condFollow, True)
          loopLatch[h] = x
          break
    return loopHead, loopType, loopFollow, loopLatch
  def markNodesInLoop(self, x, nodesInLoop, loopHead, use_paren):
    for n in nodesInLoop:
      if use_paren or not n in loopHead: loopHead[n] = x
    return nodesInLoop
  def findLoopType(self, y, x, nodesInLoop, loopType, structType, condFollow):
    #cannot be a pre-test loop if code is in header
    if not x in self.basic_blocks and len(self.succ[x]) == 2 and any(z == condFollow[x] for z in self.succ[x]):
      loopType[x] = CFG.PRETESTED
    else:
      loopType[x] = CFG.POSTTESTED if len(self.succ[y]) == 2 and not all(z==x or z in nodesInLoop for z in self.succ[y]) else CFG.ENDLESS
      if len(self.succ[x]) == 2 and x != y or len(self.succ[x]) >= 3: structType[x] = CFG.LOOPCOND
  def findLoopFollow(self, y, x, nodesInLoop, loopType, loopFollow, condFollow, isParen):
    if loopType[x] == CFG.PRETESTED:
      loopFollow[x] = next(z for z in self.succ[x] if not z in nodesInLoop and z!=x)
    elif loopType[x] == CFG.POSTTESTED:
      loopFollow[x] = next(z for z in self.succ[y] if not z in nodesInLoop and z!=x)
    else:
      if isParen:
        loopNodes, candidates = list(sorted((x, *nodesInLoop), key=lambda z: self.dfs_int[z][1], reverse=True)), []
        while len(loopNodes) != 0:
          m = loopNodes.pop(0)
          if len(self.succ[m]) >= 2 and m in condFollow and (condFollow[m] == x or condFollow[m] in nodesInLoop):
            if self.dfs_int[m][1] > self.dfs_int[condFollow[m]][1]:
              while loopNodes[0] != condFollow[m]: loopNodes.pop(0)
            else: break
          else: candidates.extend([z for z in self.succ[m] if not z in nodesInLoop and z!=x])
      else:
        candidates = [z for n in (x, *nodesInLoop) if len(self.succ[n]) >= 2 for z in self.succ[n] if not z in nodesInLoop and z!=x]
      if len(candidates) != 0:
        loopFollow[x] = max(candidates, key=lambda x: self.dfs_int[x][1])        
  def restructureTwoWays(self, paren, condType, condFollow, caseHead, loopHead, loopLatch):
    for n in self.succ:
      if not n in condType or condType[n] == CFG.CASE: continue
      f = condFollow[n] if n in condFollow else None
      if loopHead[n] != loopHead[f] if n in loopHead and f in loopHead else n in loopHead or f in loopHead:
        l = loopLatch[loopHead[n]] if n in loopHead else None
        hf = loopHead[f] if f in loopHead else None
        if not l is None and any(x == l or CFG.inParen(l, x, paren) for x in self.succ[n]):
          x = next(x for x in self.succ[n] if x == l or CFG.inParen(l, x, paren))
          tb = next(y for y in self.succ[n] if self.cond_values[(n, y)])
          if x == tb: condType[n] = CFG.IFTHEN; condFollow[n] = next(iter(self.succ[n] - {tb}))
          else: condType[n] = CFG.IFELSE; condFollow[n] = tb
        elif any(x == hf or CFG.inParen(hf, x, paren) for x in self.succ[n]):
          x = next(x for x in self.succ[n] if x == hf or CFG.inParen(hf, x, paren))
          tb = next(y for y in self.succ[n] if self.cond_values[(n, y)])
          if x == tb: condType[n] = CFG.IFTHEN; condFollow[n] = next(iter(self.succ[n] - {tb}))
          else: condType[n] = CFG.IFELSE; condFollow[n] = tb
      elif f != (condFollow[caseHead[n]] if n in caseHead else None) and any((caseHead[n] if n in caseHead else None) != (caseHead[x] if x in caseHead else None) for x in self.succ[n]):
        x = next(x for x in self.succ[n] if (caseHead[n] if n in caseHead else None) != (caseHead[x] if x in caseHead else None))
        tb = next(y for y in self.succ[n] if self.cond_values[(n, y)])
        if x == tb: condType[n] = CFG.IFTHEN; condFollow[n] = next(iter(self.succ[n] - {tb}))
        else: condType[n] = CFG.IFELSE; condFollow[n] = tb
      elif not n in condFollow:
        tb = next(y for y in self.succ[n] if self.cond_values[(n, y)])
        if self.isBackEdge(n, tb):
          condType[n] = CFG.IFTHEN; condFollow[n] = next(iter(self.succ[n] - {tb}))
        else: condType[n] = CFG.IFELSE; condFollow[n] = tb
  def whole_interval(ivals, s):
    for ival in reversed(ivals):
      ns = set()
      for x in s: ns |= ival[x]
      s = ns
    return s
  def isLatchNode(self, n, loopLatch):
    return any(n != x and loopLatch[x] == n for x in loopLatch)
  def loopStruct(self, g, ivals, structType, caseHead, condFollow):
    loopHead, loopType, loopFollow, loopLatch = {}, {}, {}, {}
    for i, gi in enumerate(g):
      for h in ivals[i]:
        for x in sorted(gi[2][h], key=lambda x: self.dfs_int[x][1]):
          if not x in ivals[i][h]: continue
          #adjust since x is the interval header, not the actual graph node which is the single-exit node
          if not h in self.succ[x]:
            m = {z for ival in reversed(ivals[:i]) for z in ival[x] if h in self.succ[z]}
            if len(m) == 0: continue
            x = next(iter(m))
          if not x in loopHead and (caseHead[x] == caseHead[h] if x in caseHead and h in caseHead else not x in caseHead and not h in caseHead):
            if h in structType and structType[h] == CFG.LOOP:
              l = loopLatch[h] #condType[l] never changes, and the reset nodes should be remarked so no point to this
              #structType[l] = CFG.COND if len(self.succ[l}) >= 2
            nodesInLoop = self.markNodesInLoop(h, self.loopNodes(x, h, CFG.whole_interval(ivals[:i], ivals[i][h])), loopHead, False) #ivals[i].keys()
            #if x != h: structType[x] = CFG.SEQ
            structType[h] = CFG.LOOP
            self.findLoopType(x, h, nodesInLoop, loopType, structType, condFollow)
            self.findLoopFollow(x, h, nodesInLoop, loopType, loopFollow, condFollow, False)
            loopLatch[h] = x
            break
    return loopHead, loopType, loopFollow, loopLatch
  def compoundConditionals(self):
    for x in self.succ:
        if len(x) == 2:
          for y in self.succ[x]:
            if len(self.succ[y]) == 2 and len(self.pred[y]) == 1 and len(self.succ[x].intersection(self.succ[y])) == 1:
              pass #if not y in self.basic_blocks: #y must be condition only node
  def indent(i): return "\t"*i
  def BBstr(self, n):
    if n == self.ret: return "return; //return node\n" 
    elif n == self.rev_graph.sources[0]: return "exit(EXIT_FAILURE); //exit node\n"
    return "BB" + str(self.basic_blocks[n]) + "; //code block " + str(n) + ("(root)" if n == self.sources[0] else "") + "\n"
  def writeBB(self, n, i):
    return [i, self.BBstr(n), []]
  def strCond(self, n): return self.NwayReg(n) if len(self.succ[n]) >= 3 else self.asmCond(n)
  def asmCond(self, n): return "cond_BB" + str(self.conditions[n])
  def emitGotoAndLabel(n, i): return CFG.indent(i) + "goto L" + str(n) + ";\n"
  def NwayReg(self, n): return "mcond_BB" + str(self.conditions[n])
  def writeNway(self, n, i, latch, followSet, gotoSet, traversed, code, revCode, ast, structType, condType, caseHead, condFollow, loopHead, loopType, loopFollow, loopLatch):
    f = condFollow[n]
    followSet.append(f if not f in followSet else None)
    ast.add_to_node(ASTCFG.CODE, (n, self.BBstr(n)))
    code.append(self.writeBB(n, i)); revCode[n] = len(code)
    ast.add_to_node(ASTCFG.CASE, (self.NwayReg(n), [str(self.cond_values[(n, s)]) for s in self.succ[n]]))
    code[-1][1] += CFG.indent(i) + "switch (" + self.NwayReg(n) + ") {\n"
    for s in self.succ[n]:
      code[-1][1] += CFG.indent(i+1) + "case " + str(self.cond_values[(n, s)]) + ":\n"
      if s in traversed:
        ast.add_to_node(ASTCFG.GOTO, s)
        code[-1][1] += CFG.emitGotoAndLabel(s, i+2); code[-1][2].append(s)
      else:
        self.codeGen(s, i+2, latch, followSet, gotoSet, traversed, code, revCode, ast, structType, condType, caseHead, condFollow, loopHead, loopType, loopFollow, loopLatch)
        ast.add_to_node(ASTCFG.GOTO, f)
        code[-1][1] += CFG.indent(i+2) + "break;\n"
      ast.leave_node()
    code[-1][1] += CFG.indent(i) + "}\n"
    del followSet[-1] #if not inFollowSet and f in followSet: followSet.remove(f)
    if f in traversed: code[-1][1] += CFG.emitGotoAndLabel(f, i); code[-1][2].append(f)
    else: self.codeGen(f, i, latch, followSet, gotoSet, traversed, code, revCode, ast, structType, condType, caseHead, condFollow, loopHead, loopType, loopFollow, loopLatch)
  def write2way(self, n, i, latch, followSet, gotoSet, traversed, code, revCode, ast, structType, condType, caseHead, condFollow, loopHead, loopType, loopFollow, loopLatch):
    if n in loopFollow and loopFollow[n] in self.succ[n]:
      f = next(iter(self.succ[n] - {loopFollow[n]}))
      condType[n] = CFG.IFTHEN if self.cond_values[(n, loopFollow[n])] else CFG.IFELSE
    else:
      f = condFollow[n]
    newGotos = set()
    if self.post_dom_tree().pred[n] == f: followSet.append(f if not f in followSet else None)
    else:
      if condType[n] != CFG.CASE and any(loopHead[n] != loopHead[x] if n in loopHead and x in loopHead else n in loopHead or x in loopHead for x in self.succ[n]):
        followSet.append(None); newGotos.add(self.post_dom_tree().pred[n]); newGotos.add(latch)
        if f in loopHead: newGotos.add(loopHead[f])
        newGotos -= gotoSet; gotoSet |= newGotos
      elif any((caseHead[n] if n in caseHead else None) != (caseHead[x] if x in caseHead else None) for x in self.succ[n]):
        followSet.append(f if not f in followSet else None)
      else: followSet.append(None)
    ast.add_to_node(ASTCFG.CODE, (n, self.BBstr(n)))
    code.append(self.writeBB(n, i)); revCode[n] = len(code)
    ast.add_to_node(ASTCFG.IFTHENELSE if condType[n] == CFG.IFTHENELSE else ASTCFG.IFTHEN, ("!" if condType[n] == CFG.IFELSE else "") + self.asmCond(n))
    code[-1][1] += CFG.indent(i) + "if (" + ("!" if condType[n] == CFG.IFELSE else "") + self.asmCond(n) + ") {\n"
    c = next(y for y in self.succ[n] if self.cond_values[(n, y)] == (False if condType[n] == CFG.IFELSE else True))
    if c in traversed or n in loopHead and loopHead[n] in loopFollow and c == loopFollow[loopHead[n]] or n in loopFollow and loopFollow[n] in self.succ[n]:
      ast.add_to_node(ASTCFG.GOTO, c)
      code[-1][1] += CFG.emitGotoAndLabel(c, i+1); code[-1][2].append(c)
    else: self.codeGen(c, i+1, latch, followSet, gotoSet, traversed, code, revCode, ast, structType, condType, caseHead, condFollow, loopHead, loopType, loopFollow, loopLatch)
    if condType[n] == CFG.IFTHENELSE:
      ast.leave_node()
      code[-1][1] += CFG.indent(i) + "} else {\n"
      fb = next(y for y in self.succ[n] if self.cond_values[(n, y)] == False)
      if fb in traversed:
        ast.add_to_node(ASTCFG.GOTO, fb)
        code[-1][1] += CFG.emitGotoAndLabel(fb, i+1); code[-1][2].append(fb)
      else: self.codeGen(fb, i+1, latch, followSet, gotoSet, traversed, code, revCode, ast, structType, condType, caseHead, condFollow, loopHead, loopType, loopFollow, loopLatch)
    ast.leave_node()
    code[-1][1] += CFG.indent(i) + "}\n"
    del followSet[-1]; gotoSet -= newGotos
    if not f is None:
      if f in traversed or f in followSet:
        ast.add_to_node(ASTCFG.GOTO, f)
        code[-1][1] += CFG.emitGotoAndLabel(f, i); code[-1][2].append(f)
      else: self.codeGen(f, i, latch, followSet, gotoSet, traversed, code, revCode, ast, structType, condType, caseHead, condFollow, loopHead, loopType, loopFollow, loopLatch)
  def writeSeq(self, n, i, latch, followSet, gotoSet, traversed, code, revCode, ast, structType, condType, caseHead, condFollow, loopHead, loopType, loopFollow, loopLatch):
    if self.isReturn(n):
      ast.add_to_node(ASTCFG.RETURN, (n, None))
      code.append([i, "return;\n", []]); revCode[n] = len(code)
    else:
      ast.add_to_node(ASTCFG.CODE, (n, self.BBstr(n)))
      code.append(self.writeBB(n, i)); revCode[n] = len(code)
      if len(self.succ[n]) != 0:
        s = next(iter(self.succ[n]))
        if s in traversed or (loopHead[s] != loopHead[n] if s in loopHead and n in loopHead else s in loopHead or n in loopHead) and (any(not p in traversed for p in self.pred[s]) or s in followSet) or latch in loopHead and loopHead[latch] in loopFollow and s == loopFollow[loopHead[latch]] or (caseHead[s] != caseHead[n] if s in caseHead and n in caseHead else s in caseHead or n in caseHead) and n in caseHead and s != condFollow[caseHead[n]]:
          ast.add_to_node(ASTCFG.GOTO, s)
          code[-1][1] += CFG.emitGotoAndLabel(s, i); code[-1][2].append(s)
        else:
          self.codeGen(s, i, latch, followSet, gotoSet, traversed, code, revCode, ast, structType, condType, caseHead, condFollow, loopHead, loopType, loopFollow, loopLatch)
  def writeLoop(self, n, i, latch, followSet, gotoSet, traversed, code, revCode, ast, structType, condType, caseHead, condFollow, loopHead, loopType, loopFollow, loopLatch):
    traversed.add(n)
    followSet.append(loopFollow[n] if n in loopFollow and not loopFollow[n] in followSet else None) # and loopType[n] != CFG.ENDLESS
    l = loopLatch[n]
    if loopType[n] == CFG.PRETESTED:
      ast.add_to_node(ASTCFG.CODE, (n, self.BBstr(n)))
      code.append(self.writeBB(n, i)); revCode[n] = len(code)
      ast.add_to_node(ASTCFG.WHILE, ("!" if self.cond_values[(n, loopFollow[n])] else "") + self.asmCond(n))
      code[-1][1] += CFG.indent(i) + "while (" + ("!" if self.cond_values[(n, loopFollow[n])] else "") + self.asmCond(n) + ") {\n"
    elif loopType[n] == CFG.POSTTESTED:
      ast.add_to_node(ASTCFG.DOWHILE, ("!" if self.cond_values[(l, loopFollow[n])] else "") + self.asmCond(l))
      code[-1][1] += CFG.indent(i) + "do {\n"
    else:
      ast.add_to_node(ASTCFG.INFLOOP, None)
      code[-1][1] += CFG.indent(i) + "while (true) {\n"
    if loopType[n] == CFG.PRETESTED:
      #original algorithm does not handle N-way conditionals on pre-test loops, would yield many gotos
      self.codeGen(next(iter(self.succ[n] - {loopFollow[n]})), i+1, l, followSet, gotoSet, traversed, code, revCode, ast, structType, condType, caseHead, condFollow, loopHead, loopType, loopFollow, loopLatch)
    elif structType[n] == CFG.LOOPCOND:
      traversed.remove(n); structType[n] = CFG.COND
      self.codeGen(n, i+1, l, followSet, gotoSet, traversed, code, revCode, ast, structType, condType, caseHead, condFollow, loopHead, loopType, loopFollow, loopLatch)
    else:
      ast.add_to_node(ASTCFG.CODE, (n, self.BBstr(n)))
      code.append(self.writeBB(n, i+1)); revCode[n] = len(code)
      self.codeGen(next(iter(self.succ[n])), i+1, l, followSet, gotoSet, traversed, code, revCode, ast, structType, condType, caseHead, condFollow, loopHead, loopType, loopFollow, loopLatch)
    if not l in traversed:
      self.codeGen(l, i+1, latch, followSet, gotoSet, traversed, code, revCode, ast, structType, condType, caseHead, condFollow, loopHead, loopType, loopFollow, loopLatch)
      #ast.add_to_node(ASTCFG.CODE, (l, self.BBstr(l)))
      #code.append(self.writeBB(l, i+1)); revCode[l] = len(code)
    ast.leave_node()
    if loopType[n] == CFG.PRETESTED:
      code[-1][1] += CFG.indent(i) + "}\n"
    elif loopType[n] == CFG.POSTTESTED:
      code[-1][1] += CFG.indent(i) + "} while (" + ("!" if self.cond_values[(l, loopFollow[n])] else "") + self.asmCond(l) + ");\n"
    else:
      code[-1][1] += CFG.indent(i) + "}\n"
    del followSet[-1]
    if n in loopFollow:
      if not loopFollow[n] in traversed:
        self.codeGen(loopFollow[n], i, latch, followSet, gotoSet, traversed, code, revCode, ast, structType, condType, caseHead, condFollow, loopHead, loopType, loopFollow, loopLatch)
      else:
        ast.add_to_node(ASTCFG.GOTO, loopFollow[n])
        code[-1][1] += CFG.emitGotoAndLabel(loopFollow[n], i); code[-1][2].append(loopFollow[n])
  def codeGen(self, n, i, latch, followSet, gotoSet, traversed, code, revCode, ast, structType, condType, caseHead, condFollow, loopHead, loopType, loopFollow, loopLatch):
    recentFoll = None if len(followSet) == 0 else followSet[-1]
    if n in gotoSet and not self.isLatchNode(n, loopLatch) and (not latch is None and loopHead[latch] in loopFollow and n == loopFollow[loopHead[latch]] or any(not p in traversed for p in self.pred[n])):
      ast.add_to_node(ASTCFG.GOTO, n)
      code[-1][1] += CFG.emitGotoAndLabel(n, i); code[-1][2].append(n)
    elif n in followSet and not self.isLatchNode(n, loopLatch):
      if n != recentFoll:
        #print("follow goto", n, latch, recentFoll, followSet)
        ast.add_to_node(ASTCFG.GOTO, n)
        code[-1][1] += CFG.emitGotoAndLabel(n, i); code[-1][2].append(n)
    elif self.isLatchNode(n, loopLatch) and (n in traversed or not n in loopLatch and n in loopHead and loopHead[n] in revCode and (i != code[revCode[loopHead[n]]-1][0] + (1 if loopType[loopHead[n]] == CFG.PRETESTED else 0))):
      #print("latch goto", n, latch, i, code[revCode[loopHead[n]]-1][0] + (1 if loopType[loopHead[n]] == CFG.PRETESTED else 0))
      ast.add_to_node(ASTCFG.GOTO, n)
      code[-1][1] += CFG.emitGotoAndLabel(n, i); code[-1][2].append(n)
    elif not n in traversed:
      traversed.add(n)      
      if n in structType and (structType[n] == CFG.LOOP or structType[n] == CFG.LOOPCOND):
        self.writeLoop(n, i, latch, followSet, gotoSet, traversed, code, revCode, ast, structType, condType, caseHead, condFollow, loopHead, loopType, loopFollow, loopLatch)
      elif n in condType:
        if condType[n] == CFG.CASE:
          self.writeNway(n, i, latch, followSet, gotoSet, traversed, code, revCode, ast, structType, condType, caseHead, condFollow, loopHead, loopType, loopFollow, loopLatch)
        else:
          self.write2way(n, i, latch, followSet, gotoSet, traversed, code, revCode, ast, structType, condType, caseHead, condFollow, loopHead, loopType, loopFollow, loopLatch)
      else: #if structType[n] == CFG.SEQ:
        self.writeSeq(n, i, latch, followSet, gotoSet, traversed, code, revCode, ast, structType, condType, caseHead, condFollow, loopHead, loopType, loopFollow, loopLatch)
  def funcProlog(): return "void" + " " + "cfg" + "(" + ") {\n"
  def funcEpilog(): return "}\n"
  def doCodeGen(self, use_paren=True):
    structType, condType, caseHead, condFollow = self.structConds()
    code, revCode = [[0, "", []]], {0: 1}
    if use_paren:
      paren = self.setParenthesis()
      loopHead, loopType, loopFollow, loopLatch = self.loopStructParen(structType, caseHead, condFollow, paren)
      self.restructureTwoWays(paren, condType, condFollow, caseHead, loopHead, loopLatch)
    else:
      g, ivals = self.get_intervals()
      loopHead, loopType, loopFollow, loopLatch = self.loopStruct(g, ivals, structType, caseHead, condFollow)
    ast = ASTCFG()
    self.codeGen(self.virtual_root(), 1, None, [], set(), set(), code, revCode, ast, structType, condType, caseHead, condFollow, loopHead, loopType, loopFollow, loopLatch)
    codeNode = {revCode[x]: x for x in revCode}
    labelsused = set.union(*(set(c[2]) for c in code))
    assert self.succ == ast.to_graph(), (self.succ, ast.to_graph())
    return ast, CFG.funcProlog() + "".join([("L" + str(codeNode[x+1]) + ":" if codeNode[x+1] in labelsused else "") + CFG.indent(i) + s for x, (i, s, _) in enumerate(code)]) + CFG.funcEpilog()
  def conditionBasedRefinement(topoOrder, reachConds):
    for i, x in enumerate(topoOrder):
      for j in range(i+1, len(topoOrder)):
        if reachConds[x] == BoolExp(BoolExp.NOT, reachConds[topoOrder[j]]):
          pass #if-then-else
    for i, x in enumerate(topoOrder):
      for j in range(i+1, len(topoOrder)):
        common, left, right = reachConds[x].factor(reachConds[topoOrder[j]])
        if left == BoolExp(BoolExp.NOT, right):
          pass #if-then-else
  def conditionAwareRefinement(topoOrder, reachConds):
    for i, x in enumerate(topoOrder):
      for conds in reachConds[x].allIntegralComparisons():
        for j in range(i+1, len(topoOrder)):
          for inner in reachConds[topoOrder[j]].allIntegralComparisons():
            if conds.isSameForm(inner): pass
  def reachabilityBasedRefinement(topoOrder, reachConds, succ):
    sccs, reach = sccreach.nuutila_reach_scc(succ)
    revsccs = {}
    for i, x in enumerate(reversed(topoOrder)):
      curExp = reachConds[x]
      if curExp.isTrue(): continue
      for j in range(i, -1, -1):
        if topoOrder[j] in reach[revsccs[x]]: continue
        curExp = BoolExp(BoolExp.OR, [curExp, reachConds[topoOrder[j]]])
        if curExp.isTrue(): pass #if - else if - else
  def reachingConditions(self, slice):
    topoOrder = graph.topo_kahn({x: self.succ[x] & slice for x in slice})
    reachCond = {x: [] for x in slice}
    for x in topoOrder:
      reachCond[x] = BoolExp(BoolExp.OR, [BoolExp(BoolExp.AND, [reachCond[v], IntegralComparison(IntegralComparison.EQ, self.conditions[v], self.cond_values(v, x))]) for v in self.pred[x] if v in slice])
    return reachCond
  def loopRefinement(): pass
  def restructureLoopEntries(self, entries): pass
  def restructureLoopExits(self, exits): pass
  def identLoops(self, x, backEdges):
    loopNodes = self.graph_slice(x, backEdges)
    multiEntries = {y for y in loopNodes if y != x and any(not z in loopNodes for z in self.pred[y])}
    if len(multiEntries) != 0: self.restructureLoopEntries(multiEntries)
    exits, exitLoopNodes = set(), set()
    newExits = {z for y in loopNodes for z in self.succ[y] if not z in loopNodes} #successor refinement
    while len(newExits) != 0 and len(exits) + len(newExits) > 1:
      newLoopNodes = {y for y in exits if self.dom_tree().isAncestor(x, y)}
      exits |= newExits - newLoopNodes
      newExits = {z for y in loopNodes for z in self.succ[y] if not z in loopNodes and not z in newLoopNodes}
      exitLoopNodes |= newLoopNodes
    exits |= newExits
    if len(exits) > 1: self.restructureLoopExits(exits)
  def simplifyConditions(self, x, sink):
    slice = self.graph_slice(x, {sink})
    reachConds = self.reachingConditions(x, slice)
    topoOrder = graph.topo_kahn({x: self.succ[x] & slice for x in slice})
    self.conditionBasedRefinement(topoOrder, reachConds)
    self.conditionAwareRefinement(topoOrder, reachConds)
    self.reachabilityBasedRefinement(topoOrder, reachConds)
  def dream_reduction(self):
    for widx in self.dfs_revint: #reverse post-order
      x = self.dfs_revint[widx]
      if x == 0 or self.dfs_int[x][0] == widx: continue
      backEdges = {self.isBackEdge(x, y) for y in self.succ[x]}
      if len(backEdges) != 0: #loop header
        self.identLoops(x, backEdges)
      else: #head of acyclic region
        acycRegion = self.dom_tree().subTree(x)
        sinks = {self.succ[z] for z in acycRegion if not z in acycRegion}
        if len(sinks) == 1:
        #if all(self.pred[z].issubset(acycRegion) for z in acycRegion):
          self.simplifyConditions(x, next(iter(sinks)))
  #http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.470.3729&rep=rep1&type=pdf
  def node_splitting(self):
    #for efficiency should maintain successors as well
    pred = {x: {y for y in self.pred[x]} for x in self.pred}
    nextnode = len(pred) + 1
    del pred[self.rev_graph.sources[0]]; del pred[self.ret]
    while len(pred) != 1:
      for x in pred: #T1 remove self-loops
        if x in pred[x]: pred[x].remove(x)
      #T2 combine single predecessor nodes
      allsing = {x for x in pred if len(pred[x]) == 1}
      for x in allsing:
        if not x in pred: continue
        y = next(iter(pred[x]))
        pred[x] = pred[y]; del pred[y]
        for z in pred:
          if y in pred[z]: pred[z].remove(y); pred[z].add(x)
      if len(allsing) != 0: continue
      #T3 choose any node with at least two predecessors and duplicate it
      dupnode = next(iter(pred))
      for i, y in enumerate({x for x in pred[dupnode]}):
        if i == 0: continue
        dup = nextnode; nextnode += 1
        pred[dupnode].remove(y)
        pred[dup] = set((y,))
        for x in pred:
          if dupnode in pred[x]: pred[x].add(dup)
    addednodes = nextnode - len(self.pred) - 1
    return addednodes
  def complete_graph():
    g = [[2, 3], [4], [4], []] #if-then-else
    cfg = CFG(init = cfg_succ_relabel(g))
    cfg.add_edge(4+2, 2)
    #print(cfg.doCodeGen())
    for k in range(1, 4):
      cfg = CFG(init=cfg_succ_relabel([list(range(1, k+1))] * k))
      assert ((k-1) * (k-2)) >> 1 == cfg.node_splitting()
      #if k == 7:
      cfg.add_edge(1, 2)
      if len(cfg.succ[1]) == 2: cfg.conditions[1] = 1
      if len(cfg.succ[1]) == 2: cfg.cond_values[(1, 1)] = True; cfg.cond_values[(1, 2)] = False
      else:
        cfg.cond_values[(1, 2)] = len(cfg.succ[1])-1
        if len(cfg.succ[1]) == 3:
          z0, z1 = cfg.succ[1] - {2}
          cfg.cond_values[(1, z0)] = 0; cfg.cond_values[(1, z1)] = 1
      print(cfg.doCodeGen())
  def writeStateNode(self, ast, code, x):
    if len(self.succ[x]) == 0 or x == self.ret: return
    if len(self.succ[x]) == 1:
      ast.add_to_node(ASTCFG.CFGVAR, ("state", next(iter(self.succ[x]))))
      code.extend(("\t\t\tstate = ", str(next(iter(self.succ[x]))), "\n"))
    elif len(self.succ[x]) == 2:
      tnode, fnode = self.succ[x]
      if not self.cond_values[(x, tnode)]: tnode, fnode = fnode, tnode
      ast.add_to_node(ASTCFG.IFTHENELSE, self.asmCond(x))
      ast.add_to_node(ASTCFG.CFGVAR, ("state", tnode)); ast.leave_node()
      ast.add_to_node(ASTCFG.CFGVAR, ("state", fnode)); ast.leave_node()
      code.extend(("\t\t\tstate = ", self.asmCond(x), " ? ", str(tnode), " : ", str(fnode), ";\n"))
    else:
      ast.add_to_node(ASTCFG.CASE, (self.NwayReg(x), [self.cond_values[(x, y)] for y in self.succ[x]]))
      code.extend(("\t\t\tswitch (", self.NwayReg(x), ") {\n"))
      for y in self.succ[x]:
        ast.add_to_node(ASTCFG.CFGVAR, ("state", y)); ast.leave_node()
        code.extend(("\t\t\tcase ", str(self.cond_values[(x, y)]), ":\n",
                      "\t\t\t\tstate = ", str(y), ";\n",
                      "\t\t\t\tbreak;\n"))
      code.append("\t\t\t}\n")
  def codeGenStateMachine(self):
    code = [CFG.funcProlog(),
            "\tunsigned long state = ", str(self.sources[0]), ";\n",
            "\twhile (true) {\n",
            "\t\tswitch (state) {\n"]
    ast = ASTCFG()
    #ast.add_to_node(ASTCFG.CODE, (0, None))
    #ast.add_to_node(ASTCFG.CFGVAR, ("state", self.sources[0]))
    ast.add_to_node(ASTCFG.INFLOOP, None)
    ast.add_to_node(ASTCFG.CODE, (0, None))
    ast.add_to_node(ASTCFG.CASE, ("state", list(self.succ)))
    for x in self.succ:
      if x == self.rev_graph.sources[0]: continue
      if self.isReturn(x): ast.add_to_node(ASTCFG.RETURN, (x, None))
      else: ast.add_to_node(ASTCFG.CODE, (x, self.BBstr(x)))
      code.extend(("\t\tcase ", str(x), ":\n",
                  "\t\t\t", self.BBstr(x)))
      self.writeStateNode(ast, code, x)
      ast.leave_node()
      if len(self.succ[x]) == 0 or x == self.ret: continue
      code.append("\t\t\tbreak;\n")
    ast.leave_node()
    code.extend(("\t\t}\n",
                 "\t}\n",
                 CFG.funcEpilog()))
    assert self.succ == ast.to_graph(), (self.succ, ast.to_graph())
    return ast, "".join(code)
  def codeGenUnstructured(self):
    code = [CFG.funcProlog()]
    ast = ASTCFG()
    dfsorder = [] #simple DFS preorder
    for widx in self.dfs_revint:
      n = self.dfs_revint[widx]
      if n == 0 or self.dfs_int[n][1] == widx: continue
      dfsorder.append(n)
    nextdfs = {x: dfsorder[i+1] if i != len(dfsorder)-1 else None for i, x in enumerate(dfsorder)}
    labels = set(y for y in self.pred if any(y != nextdfs[x] for x in self.pred[y]))
    for n in dfsorder:
      if n == self.rev_graph.sources[0]: continue
      if self.isReturn(n): ast.add_to_node(ASTCFG.RETURN, (n, None))
      else: ast.add_to_node(ASTCFG.CODE, (n, self.BBstr(n)))
      code.extend((("L", str(n), ":") if n in labels else ()) + ("\t", self.BBstr(n)))
      skipone = nextdfs[n] in self.succ[n]
      if len(self.succ[n]) == 0 or n == self.ret or len(self.succ[n]) == 1 and skipone: continue
      if len(self.succ[n]) == 1:
        ast.add_to_node(ASTCFG.GOTO, next(iter(self.succ[n])))
        code.extend(("\tgoto ", "L", str(next(iter(self.succ[n]))), ";\n"))
      elif len(self.succ[n]) == 2 and skipone:
        tnode, fnode = self.succ[n]
        if tnode == nextdfs[n]: tnode = fnode
        ast.add_to_node(ASTCFG.IFTHEN, ("" if self.cond_values[(n, tnode)] else "!") + self.asmCond(n))
        ast.add_to_node(ASTCFG.GOTO, tnode); ast.leave_node()
        code.extend(("\tif (", "" if self.cond_values[(n, tnode)] else "!", self.asmCond(n), ") ", "goto ", "L", str(tnode), ";\n"))
      elif len(self.succ[n]) == 2:
        tnode, fnode = self.succ[n]
        if not self.cond_values[(n, tnode)]: tnode, fnode = fnode, tnode
        ast.add_to_node(ASTCFG.IFTHENELSE, self.asmCond(n))
        ast.add_to_node(ASTCFG.GOTO, tnode); ast.leave_node()
        ast.add_to_node(ASTCFG.GOTO, fnode); ast.leave_node()
        code.extend(("\tif (", self.asmCond(n) + ") ", "goto ", "L", str(tnode), ";\n",
                      "\telse ", "goto ", "L", str(fnode), ";\n"))
      else:
        ast.add_to_node(ASTCFG.CASE, (self.NwayReg(n), [str(self.cond_values[(n, y)]) for y in self.succ[n]]))
        code.extend(("\tswitch (", self.NwayReg(n), ") {\n"))
        for y in self.succ[n]:
          ast.add_to_node(ASTCFG.GOTO, y); ast.leave_node()
          if y == nextdfs[n]: continue
          code.extend(("\tcase ", str(self.cond_values[(n, y)]), ":\n",
                       "\t\tgoto ", "L", str(y), ";\n"))
        code.append("\t}\n")
    code.append(CFG.funcEpilog())
    #assert self.succ == ast.to_graph(), (self.succ, ast.to_graph())
    return ast, "".join(code)
  def virtual_root(self):
    assert len(self.sources) == 1
    return self.sources[0]
  def dom_tree(self):
    return self.doms[self.sources[0]][0]
  def post_doms(self):
    symexits = {} #self.rev_graph.succ[self.rev_graph.sources[0]] - self.pred[self.rev_graph.sources[0]]
    pdtree = self.post_dom_tree()
    return {x: None if x in symexits else pdtree.pred[x] for x in pdtree.pred}
  def post_dom_tree(self):
    return self.rev_graph.doms[self.rev_graph.sources[0]][0]
  def codeGenDFS(self):
    #short circuits needed "&&" "||"
    code, s, blocks, i = CFG.funcProlog(), [self.virtual_root()], [], 1 #blocks is stack for breaks, but can be used for continues also
    visited, elide = set(), 0
    BLOCKEND, ELSE, CASE, LOOPEND = 1, 2, 3, 4
    #"continue;\n", "break;\n", "goto " + ";\n"
    closures = {}
    while len(s) != 0:
      print(closures, s)
      n = s.pop()
      if n in closures:
        while len(closures[n]) != 0:
          x, y = closures[n].pop(); i-=1
          if x == BLOCKEND: code += "\t"*i + "}" + "\n"; blocks.pop()
          elif x == ELSE: code += "\t"*i + "} else {\n"; i+=1
          elif x == CASE: code += "\t"*i + "case " + str(self.cond_values[(y, n)]) + ":" + "\n"; i+=1
          elif x == LOOPEND: code += "\t"*i + "} while (" + ("" if self.cond_values[(elide, n)] else "!") + self.asmCond(elide) + ");\n"; blocks.pop()
        del closures[n]
      elide = n
      code += "\t"*i + self.BBstr(n)
      if self.looptypes[n]:
        backedges = [x for x in self.pred[n] if self.isBackEdge(x, n)]
        follow = self.post_dom_tree().lca(n, self.post_dom_tree().lcam([self.post_dom_tree().pred[x] for x in backedges] + [self.post_dom_tree().pred[n]]))
        print(n, backedges, self.post_dom_tree().pred[n], follow)
        print(self.succ)
        #assert n==8, False
        if not follow in closures: closures[follow] = []
        if follow == self.rev_graph.sources[0]: #infinite loop
          code += "\t"*i + "while (true) {\n"
          closures[follow].append((BLOCKEND, n))
          remsucc = self.succ[n]
        elif follow in self.succ[n]: #prioritize while
          code += "\t"*i + "while (" + ("" if self.cond_values[(n, follow)] else "!") + self.asmCond(n) + ") {\n"
          closures[follow].append((BLOCKEND, n))
          remsucc = self.succ[n]
        else:
          code += "\t"*i + "do {\n"
          closures[follow].append((LOOPEND, n))
          remsucc = self.succ[n]
        if not follow in visited: s.append(follow); visited.add(follow)
        s.extend([x for x in remsucc if not x in visited]); visited |= set(remsucc)
        blocks.append(n); i+=1
      else: remsucc = self.succ[n]
      #backedges = [x for x in remsucc if self.isBackEdge(n, x)]
      visitededges = [x for x in remsucc if x in visited]
      if len(remsucc) == 2 and len(visitededges) != 0:
        code += "\t"*i + "if (" + ("" if self.cond_values[(n, visitededges[0])] else "!") + self.asmCond(n) + ") goto " + "L" + str(visitededges[0]) + ";\n"
        if len(visitededges) == 2: code == "\t"*i + "goto " + "L" + str(visitededges[1]) + ";\n"
        remsucc = [x for x in remsucc if not x in visited]
      elif len(remsucc) == 1 and len(visitededges) != 0:
        code == "\t"*i + "goto " + "L" + str(visitededges[0]) + ";\n"
        remsucc = []
      #loopEntries = [x for x in remsucc if self.loopheaders[x] != 0 and n in self.loopentries[self.loopheaders[x]]]
      if len(remsucc) >= 3:
        pcdom = self.post_dom_tree().lcam(remsucc)
        if not pcdom in s: s.append(pcdom); visited.add(pcdom)
        if not pcdom in closures: closures[pcdom] = []
        closures[pcdom].append((BLOCKEND, n))
        for x in remsucc:
          if not x in closures: closures[x] = []
          closures[x].append((CASE, i+1))
        s.extend(remsucc); visited |= set(remsucc)
        code += "\t"*i + "switch (" + self.NwayReg(n) + ") {\n"
        blocks.append(n); i+=1
      elif len(remsucc) == 2:
        print(remsucc)
        pcdom = self.post_dom_tree().lcam(remsucc)
        if not pcdom in s: s.append(pcdom); visited.add(pcdom)
        if not pcdom in closures: closures[pcdom] = []
        closures[pcdom].append((BLOCKEND, n))
        falsecond, truecond = tuple(remsucc)
        if falsecond == pcdom:
          s.append(truecond); visited.add(truecond)
        elif truecond == pcdom:
          s.append(falsecond); visited.add(falsecond)
        else:
          if not truecond in closures: closures[truecond] = []
          closures[truecond].append((ELSE, None))
          s.extend([truecond, falsecond]); visited |= set(remsucc)
        code += "\t"*i + "if (" + ("" if self.cond_values[(n, falsecond)] else "!") + self.asmCond(n) + ") {\n"
        blocks.append(n); i+= 1
      elif len(remsucc) == 1:
        s.append(next(iter(remsucc))); visited.add(next(iter(remsucc)))
      #if len(s) == 0 and self.rev_graph.sources[0] in closures:
      #  s.append(self.rev_graph.sources[0]); visited.add(self.rev_graph.sources[0])
    assert len(closures) == 0 and i == 1
    return code + CFG.funcEpilog()
  def commPostDom(ipd, s, ipdom, dfs_int):
    if ipd is None: ipd = s
    elif not s is None:
      while not ipd is None and not s is None and ipd != s:
        if dfs_int[ipd][1] > dfs_int[s][1]: s = ipdom[s]
        else: ipd = ipdom[ipd]
    return ipd
  def findImmPostDominators(self): #does not handle with infinite loops globally/appropriately rather uses local post-dominator in the infinte loop - but not a tree then!
    ipdom = {}
    rev = self.get_rev_graph()
    for widx in reversed(rev.dfs_revint): #reverse post-order of reverse graph
      n = rev.dfs_revint[widx]
      if n == 0 or rev.dfs_int[n][0] == widx: continue
      ipdom[n] = None
      for c in rev.pred[n]:
        if rev.dfs_int[c][1] > rev.dfs_int[n][1]:
          ipdom[n] = CFG.commPostDom(ipdom[n], c, ipdom, rev.dfs_int)
    for widx in self.dfs_revint:
      n = self.dfs_revint[widx]
      if n == 0 or self.dfs_int[n][0] == widx: continue
      for c in rev.pred[n]:
        ipdom[n] = CFG.commPostDom(ipdom[n], c, ipdom, rev.dfs_int)
    for widx in self.dfs_revint:
      n = self.dfs_revint[widx]
      if n == 0 or self.dfs_int[n][0] == widx: continue
      for c in rev.pred[n]:
        ipdom[n] = CFG.commPostDom(ipdom[n], ipdom[c] if self.isBackEdge(n, c) and self.dfs_int[c][1] < self.dfs_int[n][1] else c, ipdom, rev.dfs_int)
    return graph.Tree(self.rev_graph.sources[0], pred_init=[ipdom[x] for x in sorted(ipdom)])
  def get_ret_exit_nodes(self):
    retnodes = self.reaches(self.ret)
    assert retnodes == set(self.rev_graph.bfsts[self.ret][0].pred)
    exitnodes = set(self.succ) - retnodes
    return (retnodes, exitnodes)
  def get_ret_exit_subgraphs(self):
    retnodes, exitnodes = self.get_ret_exit_nodes()
    retsucc = {x:{y for y in self.pred[x] if y in retnodes} for x in retnodes}
    exitsucc = {x:{y for y in self.pred[x] if y in exitnodes} for x in exitnodes}
    exited = {self.djs_scc.find(x) for x in exitsucc[self.rev_graph.sources[0]]}
    for x in self.sccs:
      if x in exited or x == self.rev_graph.sources[0]: continue
      if any(not self.succ[z].issubset(self.sccs[x]) for z in self.sccs[x]): continue
      exitsucc[self.rev_graph.sources[0]].add(x)
    return (retsucc, exitsucc)
  def get_rev_graph(self):
    retsucc, exitsucc = self.get_ret_exit_subgraphs()
    exitsucc[self.rev_graph.sources[0]].add(self.ret)
    succ = {**retsucc, **exitsucc}
    return Digraph([self.rev_graph.sources[0]], [succ[x] for x in sorted(succ)]) 
  def get_post_dom(self):
    retsucc, exitsucc = self.get_ret_exit_subgraphs()
    retdoms = dominators.tarjan_doms(self.ret, retsucc)
    exitdoms = dominators.tarjan_doms(self.rev_graph.sources[0], exitsucc)
    combdict = {**retdoms.pred, **exitdoms.pred}
    combine = graph.Tree(self.rev_graph.sources[0], pred_init=[self.rev_graph.sources[0] if x == self.ret else combdict[x] for x in sorted(combdict)])
    return combine
  def pred_set_recurse(self, s, reachset):    
    reach, notreach = set(), set()
    while len(s) != 0:
      for x in s:
        if x in reachset: reach.add(x)
        else: notreach.add(x)
      s -= reach
      s = set.union(*(self.pred[x] - notreach for x in s)) if len(s) != 0 else set()
    return reach, notreach
  def get_rev_connect_graph(self):
    succ = {x: {y for y in self.pred[x]} for x in self.succ}
    exited = {self.djs_scc.find(x) for x in succ[self.rev_graph.sources[0]]}
    for x in self.sccs:
      if x in exited or x == self.rev_graph.sources[0]: continue
      if any(not self.succ[z].issubset(self.sccs[x]) for z in self.sccs[x]): continue
      succ[self.rev_graph.sources[0]].add(x)
    return succ
  def get_fixed_revgraph_post_dom(self, strategy=1):
    retnodes, exitnodes = self.get_ret_exit_nodes()
    succ = self.get_rev_connect_graph()
    if strategy == 0: #simple remove all edges method
      allfence, _ = self.pred_set_recurse(exitnodes, retnodes)
      allfence.remove(self.ret)
      for x in allfence:
        for y in self.succ[x].intersection(exitnodes):
          succ[y].remove(x)
    elif strategy == 1: #remove all edges except one treating all exits as one big subgraph
      x = self.rev_graph.sources[0]
      fence, _ = self.pred_set_recurse(succ[self.rev_graph.sources[0]] - {self.ret}, retnodes)
      if len(fence) != 0:
        newfence = {next(iter(fence))}
        for y in newfence:
          for z in self.succ[y] - set.union(*(self.reach[z] for z in self.succ[y])):
            succ[z].add(x)
        for y in fence - newfence:
          for z in self.succ[y].intersection(exitnodes):
            if y in succ[z]: succ[z].remove(y)
    elif strategy == 2: #remove all edges except one per exit subgraph method
      #first determine the exit subgraphs
      exitsubg = {x for x in succ[self.rev_graph.sources[0]] if x != self.ret and len(self.reach[self.djs_scc.find(x)].intersection(exitnodes)) == 0}
      for x in exitsubg:
        fence, _ = self.pred_set_recurse({x}, retnodes)
        if len(fence) == 0: continue
        #newfence = fence - set.union(*(self.reach[z] for z in fence))
        #exclude = set.union(*(self.reach[z] for z in fence - newfence)) if len(fence) != len(newfence) else set()
        #newfence = {z for z in fence if len(fence.intersection(self.reach[z])) == 0}
        newfence = {next(iter(fence))}
        for y in newfence:
          for z in self.succ[y] - set.union(*(self.reach[z] for z in self.succ[y])):
            succ[z].add(x)
        for y in fence - newfence:
          for z in self.succ[y].intersection(exitnodes):
            if y in succ[z]: succ[z].remove(y)
        #allsucc = set()
        #for y in fence: allsucc |= self.succ[y]
        #for z in allsucc - set.union(*(self.reach[z] for z in allsucc)):
        #  print(x, z)
        #  succ[z].add(x)      
    dg = Digraph(self.rev_graph.sources, [succ[x] for x in sorted(succ)])
    dg = dg.doms[dg.sources[0]][0]
    for x in exitnodes:
      if dg.pred[x] in retnodes: dg.remove_edge(dg.pred[x], x); dg.add_edge(dg.sources[0], x)
    return dg

def cfg_succ_relabel(succ, returns=set()):
  n = [([2] if len(x) == 0 or i+1 in returns else []) + [y if y == 1 else y+2 for y in x] for i, x in enumerate(succ)]
  return [n[0], [], [], *n[1:]]
def revdict(dict): return {dict[x]: x for x in dict}
def cfg_to_ordered_list(root, g):
  labeltonode = {x: i+1 for i, x in enumerate(g)}
  if labeltonode[root] != 1:
    labeltonode[root], labeltonode[next(iter(g))] = 1, labeltonode[root]
  revlblmap = revdict(labeltonode)
  return [[labeltonode[x] for x in g[revlblmap[i+1]]] for i in range(len(labeltonode))], labeltonode, revlblmap
#https://www.cs.columbia.edu/~suman/secure_sw_devel/p1-allen.pdf
#https://link.springer.com/content/pdf/10.1007%2F3-540-61053-7_55.pdf
def test_interval_paper():
  origmap = {1: 2, 13: 1, 12: 13, 11: 12, 10: 11, 9: 10, 8: 9, 7: 8, 6: 7, 5: 6, 4: 5, 3: 4, 2: 3}
  cfg = CFG(init=cfg_succ_relabel(([2, 13], [], [13], [3], [3], [3, 10], [3], [6, 7], [7], [8, 9], [4, 5, 10], [4, 11], [2, 12])))
  updorigmap = {x: origmap[x] if origmap[x] == 1 else origmap[x]+2 for x in origmap}
  revmap = {origmap[x]: x for x in origmap}
  paperpostdom = [None, 12, 2, 2, 2, 2, 2, 6, 2, 2, 2, 1, 1]
  tpostdom = [None if x==3 else (3 if x==2 else (2 if paperpostdom[revmap[x if x == 1 else x-2]-1] is None else updorigmap[paperpostdom[revmap[x if x == 1 else x-2]-1]])) for x in range(1, len(origmap)+2+1)]
  assert cfg.findImmPostDominators().pred == {x+1: tpostdom[x] for x in range(len(tpostdom))}
  #cfg.add_edge(2+2, 2)
  g, ivals = cfg.get_intervals()
  assert ivals == [{1: {1}, 4: {2, 3, 4}, 15: {6, 7, 13, 14, 15}, 12: {8, 9, 10, 11, 12}, 5: {5}}, {1: {1}, 4: {4}, 15: {12, 5, 15}}, {1: {1, 4, 15}}, {1: {1}}]
  cfg = CFG(init=cfg_succ_relabel(([2, 5], [3, 4], [5], [5], [6], [7, 12], [8, 9], [9, 10], [10], [11], [], [13], [14], [13, 15], [6])))
  #cfg.add_edge(11+2, 2)
  g, ivals = cfg.get_intervals()
  assert ivals == [{1: {1, 4, 5, 6, 7}, 8: {2, 3, 8, 9, 10, 11, 12, 13, 14}, 15: {16, 17, 15}}, {1: {1}, 8: {8, 15}}, {1: {8, 1}}, {1: {1}}]
  cfg.doCodeGen()
  cfg.codeGenDFS()
  root, g = 8, {8: [5, 7], 5: [3, 4], 3: [2], 4: [2], 2: [1], 7: [1, 6], 1: [8], 6: []}  
  init, lblmap, revlblmap = cfg_to_ordered_list(root, g)
  cfg = CFG(init=cfg_succ_relabel(init))
  cfg.doCodeGen(True)
  CFG.complete_graph()
  for i, succs in enumerate(graph.get_random_cfgs(100, 10, False, 1)):
    cfg = CFG(init=[x if i == 2 or x != [] else [2] for i, x in enumerate(succs)])
    print("Graph", i); cfg.doCodeGen(True) #print(cfg.codeGenStateMachine())
def test_parenthesis():
  cfg = CFG(init=cfg_succ_relabel(([2, 13], [], [13], [3], [3], [3, 10], [3], [6, 7], [7], [8, 9], [4, 5, 10], [4, 11], [2, 12])))
  paren = cfg.setParenthesis()
  assert paren == ({0: [1, 32], 1: [2, 31], 15: [3, 30], 14: [4, 23], 6: [5, 8], 5: [6, 7], 13: [9, 22], 12: [10, 19], 11: [11, 14], 9: [12, 13], 10: [15, 18], 8: [16, 17], 7: [20, 21], 4: [24, 29], 2: [25, 28], 3: [26, 27]}, {0: [1, 32], 1: [2, 31], 4: [3, 8], 2: [4, 7], 3: [5, 6], 15: [9, 30], 14: [10, 29], 13: [11, 28], 7: [12, 15], 5: [13, 14], 6: [16, 17], 12: [18, 27], 10: [19, 24], 8: [20, 21], 9: [22, 23], 11: [25, 26]})
  print(cfg.doCodeGen())
def test_dream():
  cfg = CFG(init=cfg_succ_relabel(([2, 3], [4, 5], [6, 7], [8], [8, 9], [10, 11], [3], [12], [12], [13], [14], [15], [14], [], [16, 17], [18, 14], [18, 14], [15])))
  assert {16, 17, 18, 19} == cfg.graph_slice(15+2, {14+2})


def graphviz_dot_cfg(cfg, pre="c"):
  return (";".join(str(x) + "[label=\"" + cfg.BBstr(x) + (cfg.strCond(x) + "==" if x in cfg.conditions else "") + "\"]" for x in cfg.succ) + ";" +
          ";".join(str(x) + "->" + str(y) + ("[label=\"" + str(cfg.cond_values[(x, y)]) + "\"]" if (x, y) in cfg.cond_values else "") for x in cfg.succ for y in cfg.succ[x]))

#https://www.researchgate.net/profile/Paul-Havlak/publication/220404846_Nesting_of_Reducible_and_Irreducible_Loops/links/0deec5193bdcca8bf7000000/Nesting-of-Reducible-and-Irreducible-Loops.pdf
def test_cfg_minimize(output_dir):
  cfg = CFG(init = cfg_succ_relabel(([2], [1, 2]), [1, 2]))
  #print(cfg.codeGenStateMachine())
  #print(cfg.codeGenUnstructured())
  cfg = CFG(init = cfg_succ_relabel(([2, 3, 4], [3], [4], [1]), {2}))
  print(cfg.doCodeGen())
  #print(cfg.codeGenStateMachine())
  src = graph.do_graphviz_dot_text([graphviz_dot_cfg(cfg)])
  graph.do_graphviz_dot(src, output_dir, filename='cfgswitchhead')
  cfg = CFG(init = cfg_succ_relabel(([2, 3], [3, 4], [2, 5], [2], [3]), [4, 5]))
  #print(cfg.doCodeGen())
  src = graph.do_graphviz_dot_text([graphviz_dot_cfg(cfg)])
  #graph.do_graphviz_dot(src, output_dir, filename='cfgredirred')
  #print(cfg.doCodeGen())
  cfg = CFG(init = cfg_succ_relabel(([2, 3], [3, 4], [2, 5], [6], [7], [4, 3], [5, 2]), [4, 5]))
  src = graph.do_graphviz_dot_text([graphviz_dot_cfg(cfg)])
  #graph.do_graphviz_dot(src, output_dir, filename='cfgredirredfix')
  #print(cfg.doCodeGen())
def test_cfg_rev_graph(output_dir):
  import random
  random.seed(1)
  for succs in graph.get_random_cfgs(1000, 10, True):
    print(succs)
    cfg = CFG(init=[x if i == 2 or x != [] else [2] for i, x in enumerate(succs)])
def test_boolexp():
  #x + (y ⋅ ¬z) == 
  exp = BoolExp(BoolExp.OR, [BoolExp(BoolExp.VAR, ["x"]), BoolExp(BoolExp.AND, [BoolExp(BoolExp.VAR, ["y"]), BoolExp(BoolExp.NOT, [BoolExp(BoolExp.VAR, ["z"])])])])
  print(exp)
  print(exp.toANF()) #x ⊕ y ⊕ xy ⊕ yz ⊕ xyz
  print(exp.toDNF())
  print(exp.toCNF())
  assert exp.checkEq(exp.toANF(), BoolExp.CNF)
  assert exp.checkEq(exp.toDNF(), BoolExp.CNF)
  assert exp.checkEq(exp.toCNF(), BoolExp.CNF)
  assert exp.toDNF().checkEq(exp.toCNF(), BoolExp.CNF)
  assert exp.toANF().checkEq(exp.toDNF(), BoolExp.CNF)
  assert exp.toANF().checkEq(exp.toCNF(), BoolExp.CNF)
"""
//pre-test loop condition as part of switch
while (true) {
  switch (x) {
    case 0: goto end;
    case 1: block1(); break;
    default: block2(); break;
  }
  loopBody();
} end:
//pre-test loop condition removed from switch
while (x != 0) {
  if (x == 1) block1();
  else block2();
  loopBody();
}
//post-test loop condition as part of switch
do {
  loopBody();
  switch (x) {
    case 0: break;
    case 1: block1(); continue;
    default: block2(); continue;
  }
} while (false);
//post-test loop condition removed from switch
do {
  loopBody();
  if (x == 1) block1();
  else if (x != 0) block2();
} while (x != 0);
"""