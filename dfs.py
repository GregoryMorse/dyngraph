import graph
import cfg

"""
def dfs(graph, root):
  discovered = {}
  def inner_dfs(g):
    if g in discovered: return
    discovered[g] = len(discovered)
    for v in graph[g]: inner_dfs(v)
  inner_dfs(root)
  #for g in graph: inner_dfs(g)
  return discovered
"""
#https://www.csd.uoc.gr/~hy583/papers/ch3_4.pdf
#http://statmath.wu.ac.at/~boehm/book/chapter3.pdf
#http://www.cs.yale.edu/homes/aspnes/pinewiki/DepthFirstSearch.html
def dfs_interval(graph, root):
  discovered, exitdisc, parent = {}, {}, {root: 0}
  def interval_dfs(g):
    if g in discovered: return
    discovered[g] = len(discovered)
    for v in graph[g]:
      if not v in discovered: parent[v] = g
      interval_dfs(v)
    exitdisc[g] = len(discovered) - 1
  interval_dfs(root)
  for g in graph.keys():
    if not g in discovered:
      parent[g] = 0
      interval_dfs(g)
  return discovered, exitdisc, parent
def dfs_classify_edges(graph, root):
  discovered, exitdisc, parent = dfs_interval(graph, root)
  def isAncestor(x, y): return discovered[x] <= discovered[y] and discovered[y] <= exitdisc[x]
  def classify_edge(x, y):
    if x == y or isAncestor(y, x): return BACK_EDGE
    elif isAncestor(x, y):
      return TREE_EDGE if parent[y] == x else FORWARD_EDGE
    else: return BACK_CROSS_EDGE
  return {x:[classify_edge(x, y) for y in graph[x]] for x in graph}
def init_dfs(): root = 0; return graph.Tree(root), {root: [1, 2]}, {1: root, 2: root}
def add_node_dfs(dfs_tree, dfs_int, dfs_revint, n):
  dfs_tree.add_node(n)
  dfs_tree.add_edge(dfs_tree.virtual_root, n)
  l = dfs_int[dfs_tree.virtual_root][1]
  dfs_int[n] = [l, l + 1]; dfs_revint[l] = dfs_revint[l + 1] = n
  dfs_int[dfs_tree.virtual_root][1] += 2; dfs_revint[dfs_int[dfs_tree.virtual_root][1]] = dfs_tree.virtual_root
def remove_node_dfs(dfs_tree, dfs_int, dfs_revint, n):
  dfs_tree.remove_edge(dfs_tree.virtual_root, n)
  dfs_tree.remove_node(n) #need to update dfs_int and dfs_revint
  for i in range(dfs_int[n][1]+1, dfs_int[dfs_tree.virtual_root][1]+1):
    if dfs_int[dfs_revint[i]][0] == i: dfs_int[dfs_revint[i]][0] -= 2
    else: dfs_int[dfs_revint[i]][1] -= 2
    dfs_revint[i-2] = dfs_revint[i]
  del dfs_revint[dfs_int[dfs_tree.virtual_root][1]+1]; del dfs_revint[dfs_int[dfs_tree.virtual_root][1]+2]
  del dfs_int[n]

def do_inc_add_edge_dfs(succ, dfs_tree, dfs_int, dfs_revint, x, y):
  visited = set()
  def insHybridDFS(u, t, ts):
    visited.add(u)
    if dfs_int[u][0] >= dfs_int[t][0]:
      dfs_int[u][0] = ts; dfs_revint[ts] = u; ts += 1
    if dfs_tree.isAncestor(u, t): #Graph Search
      for x in dfs_tree.succ[u]: dfs_tree.remove_edge(u, x)
      for v in succ[u] if u != dfs_tree.virtual_root else (dfs_revint[w] for w in dfs_revint if w == dfs_int[dfs_revint[w]][0]):
        if range_overlap(dfs_int[v], ci) and not range_subsetof(ci, dfs_int[v]) and not v in visited:
          dfs_tree.remove_edge(dfs_tree.pred[v], v)
          dfs_tree.add_edge(u, v)
          ci[1] = max(ci[1], dfs_int[v][1])
          ts = insHybridDFS(v, t, ts)
    else: #Tree Search
      for v in dfs_tree.succ[u]:
        if range_overlap(dfs_int[v], ci) and not v in visited:
          ts = insHybridDFS(v, t, ts)
    if dfs_int[u][1] <= ci[1]:
      dfs_int[u][1] = ts; dfs_revint[ts] = u; ts += 1
    return ts
  if dfs_int[x][1] > dfs_int[y][0]: return #not a forward cross edge
  r = dfs_tree.lca(x, y)
  ci = [dfs_int[x][1], dfs_int[y][1]]
  dfs_tree.remove_edge(dfs_tree.pred[y], y)
  dfs_tree.add_edge(x, y)
  ts = ci[0]
  insHybridDFS(r, y, ts)
  
def do_dec_remove_edge_dfs(succ, pred, dfs_tree, dfs_int, dfs_revint, x, y):
  visited = set()
  def delHybridDFS(u, ts, trigger, r):
    visited.add(u)
    if dfs_int[u][0] >= ci[0] or u in vc:
      dfs_int[u][0] = ts; dfs_revint[ts] = u; ts += 1
    if u in vc: #Graph Search
      vc.remove(u)
      for v in dfs_tree.succ[u]: dfs_tree.remove_edge(u, v)
      for v in succ[u] if u != dfs_tree.virtual_root else (dfs_revint[w] for w in dfs_revint if w == dfs_int[dfs_revint[w]][0]):
        if v in vc and not v in visited:
          dfs_tree.remove_edge(dfs_tree.pred[v], v)
          dfs_tree.add_edge(u, v)
          ts, trigger, r = delHybridDFS(v, ts, trigger, r)
    else: #Tree Search
      for v in dfs_tree.succ[u] if u != dfs_tree.virtual_root else dfs_tree.root_succ:
        if range_overlap(dfs_int[v], ci) or v in vc:
          ts, trigger, r = delHybridDFS(v, ts, trigger, r)
          if v == trigger:
            if len(vc) == 0: ci[1] = ts - 1
            else: trigger, r = locateNextTrigger(trigger, r)
    if ci[1] is None or dfs_int[u][1] <= ci[1]:
      dfs_int[u][1] = ts; dfs_revint[ts] = u; ts += 1
      ci[0] = ts
    return ts, trigger, r
  def locateNextTrigger(trigger, r):
    earlyVisitCache = {}
    def localEarliestVisitTime(p):
      return max(dfs_int[p][0] + 1, max((dfs_int[v][1] for v in (dfs_tree.succ[p] if p != dfs_tree.virtual_root else dfs_tree.root_succ) if dfs_int[v][0] <= dfs_int[y if trigger is None else trigger][0]), default=dfs_int[p][0])+1)
    def earliestVisitTimePotPar(u):
      return min(((localEarliestVisitTime(p), p) for p in (dfs_tree.virtual_root, *pred[u]) if not p in vc), default=(None, None))
    ev, p, _, trigger = min(filter(lambda v: not v[0] is None, ((*earliestVisitTimePotPar(v), dfs_int[v][0], v) for v in vc)))
    v = dfs_revint[ev - 1]
    dfs_tree.remove_edge(dfs_tree.pred[trigger], trigger)
    if v == p: dfs_tree.add_edge_first(p, trigger)
    else: dfs_tree.add_edge_after(p, trigger, v)
    r = dfs_tree.lca(x if r is None else r, p)
    return trigger, r
  if dfs_tree.pred[y] != x: return
  trigger, r = None, None
  dfs_tree.remove_edge(x, y)
  vc = dfs_tree.subTree(y)
  ci = [dfs_int[y][0], None] #None represents positive infinity
  ts = ci[0]
  trigger, r = locateNextTrigger(trigger, r)
  while len(vc) != 0: ts, trigger, r = delHybridDFS(r, ts, trigger, r)
  
BACK_EDGE, TREE_EDGE, FORWARD_EDGE, BACK_CROSS_EDGE, FORWARD_CROSS_EDGE = 0, 1, 2, 3, 4
def classify_deleted_edge(dfs_tree, dfs_int, x, y, cur_edge):
  if do_isBackEdge(dfs_tree, dfs_int, x, y): #x == y
    assert cur_edge == BACK_EDGE
    #return BACK_EDGE
  elif do_isBackCrossEdge(dfs_int, x, y):
    assert cur_edge == BACK_CROSS_EDGE
    #return BACK_CROSS_EDGE
  elif do_isForwardCrossEdge(dfs_int, x, y):
    assert cur_edge == TREE_EDGE
    #return TREE_EDGE
  elif do_isForwardEdge(dfs_tree, dfs_int, x, y): #it is not determinable in all cases whether it is a tree or forward edge, but criterion for whether loops are not effected, effected for propogation, effected for reparenting must be derived
    #if any loop headers became invalid with respect to ancestors, consider it effectively as a tree edge, otherwise a forward edge
    #if its not a loop header, and its not in a loop, can skip loop header checking
    assert cur_edge == TREE_EDGE or cur_edge == FORWARD_EDGE
    #return FORWARD_EDGE
  else: raise ValueError
def do_classify_edge(dfs_tree, dfs_int, x, y):
  if dfs_tree.pred[y] == x: return TREE_EDGE
  elif do_isBackEdge(dfs_tree, dfs_int, x, y): return BACK_EDGE
  elif do_isAncestor(dfs_int, x, y): return FORWARD_EDGE
  elif do_isForwardCrossEdge(dfs_int, x, y): return FORWARD_CROSS_EDGE
  elif do_isBackCrossEdge(dfs_int, x, y): return BACK_CROSS_EDGE
def do_isBackEdge(dfs_tree, dfs_int, x, y): return dfs_tree.pred[y] != x and do_isAncestor(dfs_int, y, x)
def do_isForwardEdge(dfs_tree, dfs_int, x, y): return dfs_tree.pred[y] != x and do_isAncestor(dfs_int, x, y)
def do_isForwardCrossEdge(dfs_int, x, y): return dfs_int[x][1] < dfs_int[y][0]
def do_isBackCrossEdge(dfs_int, x, y): return dfs_int[y][1] < dfs_int[x][0]
def do_isCrossEdge(dfs_int, x, y): return do_isBackCrossEdge(dfs_int, x, y) or do_isForwardCrossEdge(dfs_int, x, y)
def do_isAncestor(dfs_int, x, y): return range_subsetof(dfs_int[y], dfs_int[x])
def range_overlap(r1, r2): return (r2[1] is None or r1[0] <= r2[1]) and r2[0] <= r1[1]
def range_subsetof(r1, r2): return r1[0] >= r2[0] and r1[1] <= r2[1]
def do_dfs(sources, succ, test_order=None):
  virtual_root = 0
  allsources = sources + list(filter(lambda x: not x in sources, succ))
  stack, t, visited = [(virtual_root, None)], 1, set()
  dfs_tree, dfs_int, dfs_revint = graph.Tree(virtual_root), {}, {}
  while len(stack) != 0:
    x, pre = stack.pop()
    if pre is None:
      visited.add(x)
      dfs_int[x] = [t, None]
      dfs_revint[t] = x
      t += 1
      pre = iter(succ[x] if x != virtual_root else allsources) if test_order is None else sorted(succ[x] if x != virtual_root else allsources, key=lambda y: test_order[y][0])
    for y in pre:
      if not y in visited:
        dfs_tree.add_node(y); dfs_tree.add_edge(x, y)
        stack.append((x, pre)); stack.append((y, None)); break
    else:
      dfs_int[x][1] = t
      dfs_revint[t] = x
      t += 1
  return dfs_tree, dfs_int, dfs_revint
def check_dfs(sources, succ, dfs_tree, dfs_int, dfs_revint):
  cdfs_tree, cdfs_int, cdfs_revint = do_dfs(sources, succ, dfs_int)
  if dfs_tree.pred != cdfs_tree.pred: raise ValueError("Bad DFS")
  if dfs_int != cdfs_int: raise ValueError("Bad DFS order", dfs_int, cdfs_int)
  if dfs_revint != cdfs_revint: raise ValueError("Bad DFS Reverse order")
def edge_count_max(n):
  succ = {}
  dfs_tree, dfs_int, dfs_revint = init_dfs()
  for x in range(1, n+1):
    add_node_dfs(dfs_tree, dfs_int, dfs_revint, x)  
  #do_inc_add_edge_dfs(succ, dfs_tree, dfs_int, dfs_revint, x, y)
  
def graphviz_dot_digraph_interval(succ, dfs_int, pre=""):
  return ";".join(pre + str(x) + " [label=" + "\"" + str(x) + " [" + str(dfs_int[x][0]) + "," + str(dfs_int[x][1]) + "]\"" + "]" for x in succ)
def graphviz_dot_jungle(succ, dfs_tree, dfs_int):
  nonTreeEdges = ";".join("t" + str(x) + "->t" + str(y) + "[style=dashed;constraint=false]" for x in succ for y in succ[x] if dfs_tree.pred[y] != x)
  return dfs_tree.graphviz_dot("t") + ";" + graphviz_dot_digraph_interval(succ, dfs_int, "t") + ("" if nonTreeEdges == "" else ";" + nonTreeEdges)
  
def paper_tarjan_dfs():
  #http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.327.8418&rep=rep1&type=pdf
  #DEPTH-FIRST SEARCH AND LINEAR GRAPH ALGORITHMS
  #ROBERT TARJAN
  gsucc = {1: [2], 2: [3], 3: [4], 4: [5], 5: [6, 8], 6: [1, 2, 7], 7: [2, 4], 8: [1, 3]}
  correctdfstree = graph.Tree(0, [[2], [3], [4], [5], [6, 8], [7], [], []])
  correctdfsint = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8}
  d = dfs_interval(gsucc, 1)
  g = cfg.Digraph([1], list(gsucc.values()))
  assert g.dfs_tree == correctdfstree
  correctdfstpred = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 5}
  assert correctdfstpred == d[2] and {x: y+1 for x, y in d[0].items()} == correctdfsint
def paper_inc_dec_dfs():
  #http://www.vldb.org/pvldb/vol13/p142-yang.pdf
  #Fully Dynamic Depth-First Search in Directed Graphs
  #Bohua Yang, Dong Wen, Lu Qin, Ying Zhang, Xubo Wang, and Xuemin Lin
  g = cfg.Digraph([1], [[2, 5, 20], [3], [4], [2], [6, 7, 12, 14, 18], [2], [8, 13], [9, 10, 12], [4, 7], [11], [], [], [10], [13, 15, 17], [8, 16], [10, 14], [], [14, 19], [14], [5]])
  correct_dfs_int = [[1, 40], [2, 7], [3, 6], [4, 5], [8, 37], [9, 10], [11, 24], [12, 21], [13, 14], [15, 18], [16, 17], [19, 20], [22, 23], [25, 32], [26, 29], [27, 28], [30, 31], [33, 36], [34, 35], [38, 39]] 
  correct_dfs_tree = graph.Tree(0, [[2, 5, 20], [3], [4], [], [6, 7, 14, 18], [], [8, 13], [9, 10, 12], [], [11], [], [], [], [15, 17], [16], [], [], [19], [], []])
  assert all(g.dfs_int[i+1] == [x[0]+1,x[1]+1] for i, x in enumerate(correct_dfs_int)), g.dfs_tree == correct_dfs_tree
  remove_dfs_int = [[1, 40], [2, 7], [3, 6], [4, 5], [8, 37], [9, 10], [11, 18], [23, 26], [24, 25], [13, 16], [14, 15], [19, 20], [12, 17], [21, 32], [22, 29], [27, 28], [30, 31], [33, 36], [34, 35], [38, 39]]
  remove_dfs_tree = graph.Tree(1, [[2, 5, 20], [3], [4], [], [6, 7, 12, 14, 18], [], [13], [9], [], [11], [], [], [10], [15, 17], [8, 16], [], [], [19], [], []])
  g.remove_edge(7, 8)
  assert all(g.dfs_int[i + 1] == [x[0]+1,x[1]+1] for i, x in enumerate(remove_dfs_int)), g.dfs_tree == remove_dfs_tree
  #g.add_edge(7, 8) #will be valid but not equal to original
  g = cfg.Digraph([1], [[2, 5, 20], [3], [4], [2], [6, 7, 12, 14, 18], [2], [8, 13], [9, 10, 12], [4, 7], [11], [], [], [10], [13, 15, 17], [8, 16], [10, 14], [], [14, 19], [14], [5]])
  assert all(g.dfs_int[i + 1] == [x[0]+1,x[1]+1] for i, x in enumerate(correct_dfs_int)), g.dfs_tree == correct_dfs_tree
  add_dfs_int = [[1, 40], [2, 7], [3, 6], [4, 5], [8, 37], [9, 10], [11, 32], [12, 31], [13, 14], [15, 28], [16, 17], [29, 30], [21, 22], [20, 25], [18, 27], [19, 26], [23, 24], [33, 36], [34, 35], [38, 39]]
  add_dfs_int[12], add_dfs_int[16] = add_dfs_int[16], add_dfs_int[12] #{13, 17} == {17, 13} likely due to balanced trees algorithm for unordered set
  add_dfs_tree = graph.Tree(1, [[2, 5, 20], [3], [4], [], [6, 7, 18], [], [8], [9, 10, 12], [], [11, 15], [], [], [], [13, 17], [16], [14], [], [19], [], []])
  g.add_edge(10, 15)
  assert all(g.dfs_int[i + 1] == [x[0]+1,x[1]+1] for i, x in enumerate(add_dfs_int)), g.dfs_tree == add_dfs_tree
  #g.remove_edge(10, 15) #will be valid but not equal to original
  
def test_edge_classify():
  #example from course slides found online, should find a proper research paper about edge classification
  #also would be nice if the DFS being a topological sort proof is found in a research paper rather than sketched out in endless course slides or lecture notes
  correct = {1: [TREE_EDGE, TREE_EDGE, FORWARD_EDGE, FORWARD_EDGE], 2: [TREE_EDGE], 3: [BACK_CROSS_EDGE, BACK_CROSS_EDGE], 4: [TREE_EDGE, FORWARD_EDGE], 5: [BACK_EDGE, TREE_EDGE], 6: [], 7: [BACK_CROSS_EDGE, TREE_EDGE], 8: [BACK_CROSS_EDGE]}
  g = {1: [2, 3, 4, 6], 2: [4], 3: [4, 5], 4: [5, 6], 5: [1, 6], 6: [], 7: [2, 8], 8: [4]}
  assert dfs_classify_edges(g, 1) == correct
  correct = {1: [TREE_EDGE, TREE_EDGE, FORWARD_EDGE, FORWARD_EDGE], 2: [TREE_EDGE], 3: [BACK_CROSS_EDGE, BACK_CROSS_EDGE], 4: [TREE_EDGE, TREE_EDGE], 5: [BACK_EDGE, BACK_CROSS_EDGE], 6: [], 7: [BACK_CROSS_EDGE, TREE_EDGE], 8: [BACK_CROSS_EDGE]}
  g = {1: [2, 3, 4, 6], 2: [4], 3: [4, 5], 4: [6, 5], 5: [1, 6], 6: [], 7: [2, 8], 8: [4]}
  assert dfs_classify_edges(g, 1) == correct
  correct = {1: [TREE_EDGE, TREE_EDGE, FORWARD_EDGE, FORWARD_EDGE], 2: [BACK_CROSS_EDGE], 3: [TREE_EDGE, TREE_EDGE], 4: [BACK_CROSS_EDGE, BACK_CROSS_EDGE], 5: [BACK_EDGE, TREE_EDGE], 6: [], 7: [BACK_CROSS_EDGE, TREE_EDGE], 8: [BACK_CROSS_EDGE]}
  g = {1: [3, 2, 4, 6], 2: [4], 3: [5, 4], 4: [5, 6], 5: [1, 6], 6: [], 7: [2, 8], 8: [4]}
  assert dfs_classify_edges(g, 1) == correct
