import graph
import dfs
import cfg

#https://en.wikipedia.org/wiki/Tarjan%27s_off-line_lowest_common_ancestors_algorithm
def tarjanOLCA(graph, root, p):
  lca = graph.DisjointSet(graph.keys())
  color, ancestors = {x: False for x in graph}, {x: x for x in graph}
  query = {}
  def innerOLCA(u):
    for v in graph[u]:
      innerOLCA(v)
      lca.union(u, v)
      ancestors[lca.find(u)] = u
    color[u] = True
    for x, y in p:
      if u == x:
        if color[y]: query[(x, y)] = ancestors[lca.find(y)]
      elif u == y:
        if color[x]: query[(y, x)] = ancestors[lca.find(y)]
  innerOLCA(root)
def lca(parents, x, y):
  pathx, pathy = [x], [y]
  while parents[x] != 0:
    x = parents[x]
    pathx.append(x)
  while parents[y] != 0:
    y = parents[y]
    pathy.append(y)
  return next(iter(z for z in pathx if z in pathy))

def get_j_edges(succ, dom_tree):
  return {x:{y for y in succ[x] if dom_tree.pred[y] != x} for x in succ if x in dom_tree.pred}
D_EDGE, BACK_J_EDGE, CROSS_J_EDGE = 0, 1, 2
def classify_dom_edge(dom_tree, x, y):
  if isDomEdge(dom_tree, x, y): return D_EDGE
  if dom_tree.isAncestor(x, y): return BACK_J_EDGE
  return CROSS_J_EDGE
def isDomEdge(dom_tree, x, y): return dom_tree.pred[y] == x
def isBackJEdge(dom_tree, x, y): return dom_tree.pred[y] != x and dom_tree.isAncestor(x, y)
def isCrossJEdge(dom_tree, x, y): return not dom_tree.isAncestor(x, y)
def compute_idf(dom_tree, jsucc, alphaNodes):
  def visit(x):
    for y in jsucc[x] | set(dom_tree.succ[x]):
      if y in jsucc[x]:
        if dom_tree.level[y] <= currentLevel:
          if not y in idf:
            idf.add(y)
            if not y in alphaNodes: piggyBank[dom_tree.level[y]].add(y)
      else:
        if not y in visited: visited.add(y); visit(y)
  idf = set()
  visited = set()
  maxLevel = max(dom_tree.level[x] for x in alphaNodes)
  piggyBank = [set() for _ in range(maxLevel+1)]
  for x in alphaNodes: piggyBank[dom_tree.level[x]].add(x)
  while True: #GetNode
    for currentLevel in range(maxLevel, -1, -1):
      if len(piggyBank[currentLevel]) != 0:
        currentRoot = piggyBank[currentLevel].pop(); break
    else: break
    visited.add(currentRoot)
    visit(currentRoot)
  return idf
def tarjan_doms(root, succ, use_ds = True):
  n = 0
  pred = {v: set() for v in succ}
  bucket = {v: set() for v in succ}
  semi = {v: 0 for v in succ}
  vertex = []
  dom = {v: 0 for v in succ}
  label, parent, ancestor = {}, {}, {}
  if use_ds: child, size = {}, {0: 0}; label[0] = 0; semi[0] = 0
  def ds_eval(v):
    if ancestor[v] == 0: return label[v]
    else: compress(v); return label[v] if semi[label[ancestor[v]]] >= semi[label[v]] else label[ancestor[v]]   
  def ds_link(v, w):
    s = w
    while semi[label[w]] < semi[label[child[s]]]:
      if size[s] + size[child[child[s]]] >= size[child[s]] << 1:
        ancestor[child[s]] = s; child[s] = child[child[s]]
      else:
        size[child[s]] = size[s]; ancestor[s] = child[s]; s = ancestor[s]
    label[s] = label[w]
    size[v] += size[w]
    if size[v] < size[w] << 1: s, child[v] = child[v], s
    while s != 0: ancestor[s] = v; s = child[s]
  def compress(v):
    if ancestor[ancestor[v]] != 0:
      compress(ancestor[v])
      if semi[label[ancestor[v]]] < semi[label[v]]:
        label[v] = label[ancestor[v]]
      ancestor[v] = ancestor[ancestor[v]]
  def eval(v):
    if ancestor[v] == 0: return v
    else: compress(v); return label[v]
  def link(v, w): ancestor[w] = v
  visit = [(root, None)]
  while len(visit) != 0:
    v, pre = visit.pop()
    if pre is None:
      n += 1
      semi[v] = n
      label[v] = v
      ancestor[v] = 0
      if use_ds: child[v], size[v] = 0, 1
      vertex.append(v)
      pre = iter(succ[v])
    for w in pre:
      pred[w].add(v)
      if semi[w] == 0: parent[w] = v; visit.append((v, pre)); visit.append((w, None)); break
  for i in range(n, 1, -1):
    w = vertex[i-1]
    for v in pred[w]:
      u = ds_eval(v) if use_ds else eval(v)
      if semi[u] < semi[w]: semi[w] = semi[u]
    bucket[vertex[semi[w]-1]].add(w)
    if use_ds: ds_link(parent[w], w)
    else: link(parent[w], w)
    for v in bucket[parent[w]]:
      u = ds_eval(v) if use_ds else eval(v)
      dom[v] = u if semi[u] < semi[v] else parent[w]
    bucket[parent[w]].clear()
  for i in range(2, n+1):
    w = vertex[i-1]
    if dom[w] != vertex[semi[w]-1]: dom[w] = dom[dom[w]]
  dom[root] = 0
  return graph.Tree(root, dict_pred_init={d: dom[d] for d in dom if dom[d] != 0}, use_depth=True) #return dom #[dom[x] for x in sorted(dom.keys())]
def init_dom(root):
  return graph.Tree(root, use_depth=True), {root: set()}
def inc_dom_sreedhar_gao_lee(succ, dom_tree, jsucc, x, y):
  if not x in dom_tree.pred: return
  if not y in dom_tree.pred:
    s, newedges = [(x, y)], []
    while len(s) != 0:
      x, y = s.pop()
      if y in dom_tree.pred: newedges.append((x, y)); continue
      dom_tree.add_node(y)
      dom_tree.add_edge(x, y); jsucc[y] = set()
      for z in succ[y]:
        if not z in dom_tree.pred: s.append((y, z))
        else: newedges.append((y, z))
    for y, z in newedges: #this might be batchable if incremental generalized by taking a common lca
      do_inc_dom_sreedhar_gao_lee(succ, dom_tree, jsucc, y, z)
  else: do_inc_dom_sreedhar_gao_lee(succ, dom_tree, jsucc, x, y)
def do_inc_dom_sreedhar_gao_lee(succ, dom_tree, jsucc, x, y):
  z = dom_tree.lca(x, y)
  if z != x or x == y: jsucc[x].add(y)
  if x == y: return
  domAffected = {w for w in {y} | compute_idf(dom_tree, jsucc, [y]) if dom_tree.level[w] > dom_tree.level[z] + 1}
  for w in domAffected:
    u = dom_tree.pred[w]
    dom_tree.remove_edge(u, w)
    if w in succ[u]: jsucc[u].add(w)
    dom_tree.add_edge(z, w)
METHOD_TARJAN, METHOD_SGL, METHOD_TREE_SGL, METHOD_LNF = 0, 1, 2, 3
def dec_dom_sreedhar_gao_lee(succ, pred, dom_tree, jsucc, dfs_tree, dfs_int, loopentries, x, y, method=METHOD_LNF):
  if not x in dom_tree.pred: return
  if dom_tree.pred[y] == x and all(not z in dom_tree.pred or dom_tree.isAncestor(z, y) for z in pred[y]):
    jtargets = set()
    for z in reversed(dom_tree.bfsSubTree(y)):
      dom_tree.remove_edge(dom_tree.pred[z], z); dom_tree.remove_node(z)
      jtargets |= jsucc[z]
      del jsucc[z]
    #print(jtargets)
    for y in jtargets: #this is easily batched if decremental generalized as compute_idf takes alphanodes...
      if y in dom_tree.pred:
        do_dec_dom_sreedhar_gao_lee(succ, pred, dom_tree, jsucc, dfs_tree, dfs_int, loopentries, None, y, method)
  else: do_dec_dom_sreedhar_gao_lee(succ, pred, dom_tree, jsucc, dfs_tree, dfs_int, loopentries, x, y, method)
def do_dec_dom_sreedhar_gao_lee(succ, pred, dom_tree, jsucc, dfs_tree, dfs_int, loopentries, x, y, method=METHOD_LNF):
  if not x is None and x != dom_tree.pred[y]: jsucc[x].remove(y)
  if x == y: return
  z = dom_tree.pred[y]
  if z is None: return #root not considered
  domAffected = {w for w in {y} | compute_idf(dom_tree, jsucc, [y]) if dom_tree.level[w] == dom_tree.level[y]}
  if method == METHOD_LNF: # and tarjan_is_reducible(): #is_acyclic():
    for w in sorted(domAffected, key=lambda z: dfs_int[z][1], reverse=True):
      immDom = None
      for p in pred[w] | ({z for p in loopentries[w] for z in loopentries[w][p]} if w in loopentries else set()):
        if not p in dom_tree.pred: continue
        if dfs.do_isBackEdge(dfs_tree, dfs_int, p, w): continue
        if immDom is None: immDom = p
        else: immDom = dom_tree.lca(p, immDom)
      if not immDom is None and immDom != dom_tree.pred[w]:
        if w in succ[dom_tree.pred[w]]: jsucc[dom_tree.pred[w]].add(w)
        if w in jsucc[immDom]: jsucc[immDom].remove(w)
        dom_tree.remove_edge(dom_tree.pred[w], w); dom_tree.add_edge(immDom, w)
  elif method == METHOD_TARJAN:
    subt = dom_tree.subTree(z)
    newDom = tarjan_doms(z, {n: succ[n].intersection(subt) for n in subt})
    if x is None: print(newDom)
    for w in domAffected:
      immDom = newDom.pred[w]
      if immDom != 0 and immDom != z:
        if w in succ[dom_tree.pred[w]]: jsucc[dom_tree.pred[w]].add(w)
        if w in jsucc[immDom]: jsucc[immDom].remove(w)
        dom_tree.remove_edge(dom_tree.pred[w], w); dom_tree.add_edge(immDom, w)
  elif method == METHOD_TREE_SGL:
    changes = {x for x in domAffected}
    pseudoAffected, monitor, changed = {}, {}, set()
    def calcDoms(x, pseudoDom):
      nextPseudo = x if x in domAffected else pseudoDom
      for y in dom_tree.succ[x]: calcDoms(y, nextPseudo)
      if not pseudoDom is None: pseudoAffected[x] = pseudoDom
    calcDoms(z, None)
    for w in domAffected:
      for p in pred[w]:
        if not p in dom_tree.pred: continue
        q = p if not p in pseudoAffected else pseudoAffected[p]
        if q != w and q in domAffected:
          if not q in monitor: monitor[q] = set()
          monitor[q].add(w)
    olddom = {x: dom_tree.pred[x] for x in domAffected}
    while len(changes) != 0:
      w, domTemp = changes.pop(), None
      #print(w, dom_tree.succ, changes)
      for p in pred[w]:
        if not p in dom_tree.pred: continue
        d = p if not p in pseudoAffected or pseudoAffected[p] in changed else pseudoAffected[p]
        if d in domAffected and not d in changed: continue
        if domTemp is None: domTemp = d
        else: domTemp = dom_tree.lca(domTemp, d)
      if not domTemp is None and (domTemp != dom_tree.pred[w] or not w in changed):
        changed.add(w)
        #changes = domAffected - {w}
        dom_tree.remove_edge(dom_tree.pred[w], w); dom_tree.add_edge(domTemp, w)
        #for z in dom_tree.subTree(w):
        for z in domAffected:
          if dom_tree.lca(z, w) != w: continue
          if z in monitor:
            changes |= {x for x in monitor[z] if not x in changed or not dom_tree.lca(dom_tree.pred[x], z) in {z, dom_tree.pred[x]}}
      elif not domTemp is None: raise ValueError(w, domTemp, changes)
    for w in domAffected:
      if olddom[w] != dom_tree.pred[w]:
        if w in succ[olddom[w]]: jsucc[olddom[w]].add(w)
        if w in jsucc[dom_tree.pred[w]]: jsucc[dom_tree.pred[w]].remove(w)
  else:
    changes = {x for x in domAffected}
    pseudoAffected, monitor, domSt, domDy = {}, {}, {}, {}
    def calcDoms(x, domPath, pseudoDom):
      isAffected = x in domAffected
      nextDomPath = set() if isAffected else domPath | {x}
      nextPseudo = x if isAffected else pseudoDom
      for y in dom_tree.succ[x]: calcDoms(y, nextDomPath, nextPseudo)
      domSt[x] = set() if isAffected else nextDomPath
      domDy[x] = None if isAffected or not pseudoDom is None else set()
      if not pseudoDom is None: pseudoAffected[x] = pseudoDom
    calcDoms(z, set(), None)
    for w in domAffected:
      for p in pred[w]:
        if not p in dom_tree.pred: continue
        if not p in domSt: domSt[p] = dom_tree.allAncestors(p, dom_tree.pred[z]); domDy[p] = set()
        q = p if not p in pseudoAffected else pseudoAffected[p]
        if q != w and q in domAffected:
          if not q in monitor: monitor[q] = set()
          monitor[q].add(w)
    while len(changes) != 0:
      w, domTemp = changes.pop(), None
      for p in pred[w]:
        if not p in dom_tree.pred: continue
        d = domDy[p] if not p in pseudoAffected else domDy[pseudoAffected[p]]
        if not d is None: domTemp = domTemp.intersection(domSt[p].union(d)) if not domTemp is None else domSt[p].union(d)
      if not domTemp is None: domTemp |= {w}
      if domDy[w] != domTemp:
        domDy[w] = domTemp
        if w in monitor: changes |= {z for z in monitor[w] if domDy[z] is None or len(domDy[z] - {z} - domTemp) != 0}
    for w in domAffected:
      if domDy[w] is None: continue
      immDom, allDoms = 0, domDy[w] - {w}
      for u in allDoms:
        if len(allDoms) == len((domDy[u] if not u in pseudoAffected else domDy[pseudoAffected[u]]) | domSt[u]): immDom = u; break
      if immDom != 0 and immDom != z:
        if w in succ[dom_tree.pred[w]]: jsucc[dom_tree.pred[w]].add(w)
        if w in jsucc[immDom]: jsucc[immDom].remove(w)
        dom_tree.remove_edge(dom_tree.pred[w], w); dom_tree.add_edge(immDom, w)
def check_dom(root, succ, dom_tree, jsucc):
  dom = tarjan_doms(root, succ)
  #if tarjan_doms(succ, False) != dom: raise ValueError("Bad Dominator Algorithm")
  if dom != dom_tree: 
    raise ValueError("Bad Dominators", succ, dom.succ, dom_tree.succ)
  j = get_j_edges(succ, dom_tree)
  if j != jsucc: raise ValueError("Bad Join Edges", jsucc, j, dom_tree)
  
def graphviz_dot_dj(succ, dom_tree, pre="d"):
  dj = ";".join(pre + str(x) + "->" + pre + str(y) + "[style=dashed;constraint=false]" for x in succ for y in succ[x] if not y in dom_tree.pred or dom_tree.pred[y] != x)
  lbls = ";".join(pre + str(x) + " [label=" + "\"" + str(x) +  "\"" + "]" for x in succ)
  return dom_tree.graphviz_dot(pre) + (";" + dj if not dj == "" else "") + ";" + lbls

def print_doms(x, y, root, succ, dom_tree, jedges, base, output_dir):
  print(x, y, dom_tree, base)
  graph.do_graphviz_dot(graph.make_graphviz_dot_text(succ, ';'.join((graphviz_dot_dj(succ, base[0], pre="dd"), graphviz_dot_dj(succ, dom_tree)))), output_dir)

  
def paper_tarjan_dom():
  #https://www.cs.princeton.edu/courses/archive/spr03/cs423/download/dominators.pdf
  #A Fast Algorithm for Finding Dominators in a Flowgraph
  #THOMAS LENGAUER and ROBERT ENDRE TARJAN 
  #correct = [0, 1, 1, 1, 1, 1, 4, 4, 1, 1, 8, 1, 5]
  domtree = graph.Tree(1, [[2, 3, 4, 5, 6, 9, 10, 12], [], [], [7, 8], [13], [], [], [11], [], [], [], [], []])
  correctdfs = graph.Tree(0, [[3, 4], [5], [2, 6], [7, 8], [13], [9], [10], [11], [], [12], [], [], []])
  #g = {1: [4, 3, 2], 2: [3, 5], 3: [1, 6, 2, 5], 4: [7, 8], 5: [13], 6: [9], 7: [10], 8: [10, 11], 9: [6, 12], 10: [12], 11: [10], 12: [1, 10], 13: [9]}
  g = cfg.Digraph([1], [[4, 3, 2], [3, 5], [1, 6, 2, 5], [7, 8], [13], [9], [10], [10, 11], [6, 12], [12], [10], [1, 10], [9]], [0, 3, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1])
  assert g.dfs_tree == correctdfs and g.tarjan_dominators(1) == domtree and g.tarjan_dominators(1, False) == domtree and g.tarjan_dominators(1, True) == domtree, (g.dfs_tree, correctdfs)
  g = cfg.Digraph([1], [[4, 3, 2], [5], [6, 2, 5], [7, 8], [13], [9], [10], [10, 11], [6, 12], [12], [10], [1, 10], [9]], [0, 3, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1])
  assert g.dfs_tree == correctdfs and g.tarjan_dominators(1) == domtree and g.tarjan_dominators(1, False) == domtree and g.tarjan_dominators(1, True) == domtree
def test_sgl_phi_nodes():
  #https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.8.1979&rep=rep1&type=pdf
  #A Linear Time Algorithm for Placing phi-Nodes
  #Vugranam C. Sreedhar Guang R. Gao
  g = cfg.Digraph([17], [[2, 3, 4], [4, 7], [9], [5], [6], [2, 8], [8], [7, 15], [10, 11], [12], [12], [13], [3, 14, 15], [12], [16], [], [1, 16]])
  correct_dom = graph.Tree(17, pred_init=[17, 1, 1, 1, 4, 5, 1, 1, 3, 9, 9, 9, 12, 13, 1, 17, 0])
  jg = [[], [4, 7], [], [], [], [2, 8], [8], [7, 15], [], [12], [12], [], [3, 15], [12], [16], [], []]
  assert g.tarjan_dominators(17) == g.doms[17][0] and g.doms[17][0] == correct_dom and all(set(x) == g.doms[17][1][i+1] for i, x in enumerate(jg)), (g, g.doms[17][0], g.tarjan_dominators(17))
  assert g.compute_idf(17, [5, 13]) == set([15, 3, 12, 8, 2] + [7, 4, 16])
  g = cfg.Digraph([8], [[3], [3, 4], [5], [5, 6], [7], [7], [], [1, 2]])
  correct_dom = graph.Tree(8, pred_init=[8, 8, 8, 2, 8, 4, 8, 0])
  jg = [[3], [3], [5], [5], [7], [7], [], []]
  assert g.tarjan_dominators(8) == g.doms[8][0] and g.doms[8][0] == correct_dom and all(set(x) == g.doms[8][1][i+1] for i, x in enumerate(jg))
  assert g.compute_idf(8, [8, 2]) == set([7, 5, 3])
def test_sgl_inc_dec_dominators():
  #https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.46.3846&rep=rep1&type=pdf
  #Incremental Computation of Dominator Trees
  #Vugranam C. Sreedhar, Guang R. Gao, Yong-fong Lee
  #g = cfg.Digraph(1, [[2, 10], [3, 4], [10], [5, 6, 9], [7], [7], [8], [4, 9], [10], []])
  #correct_dom = [0, 1, 2, 2, 4, 4, 4, 7, 4, 1]
  #correct_j = [[], [], [10], [], [7], [7], [], [4, 9], [10], []]
  g = cfg.Digraph([10], [[2, 3], [9], [4, 5, 8], [6], [6], [7], [3, 8], [9], [], [1, 9]])
  correct_dom = graph.Tree(10, pred_init=[10, 1, 1, 3, 3, 3, 6, 3, 10, 0])
  correct_j = [[], [9], [], [6], [6], [], [3, 8], [9], [], []]
  next_dom = graph.Tree(10, pred_init=[10, 1, 1, 1, 3, 1, 6, 1, 10, 0])
  next_j = [[], [9, 4], [4, 8], [6], [6], [], [3, 8], [9], [], []]
  assert g.tarjan_dominators(10) == g.doms[10][0] and g.doms[10][0] == correct_dom and all(set(x) == g.doms[10][1][i+1] for i, x in enumerate(correct_j))
  g.add_edge(2, 4) #cfg.add_edge(3, 5)
  assert g.tarjan_dominators(10) == g.doms[10][0] and g.doms[10][0] == next_dom and all(set(x) == g.doms[10][1][i+1] for i, x in enumerate(next_j))
  g.remove_edge(2, 4) #cfg.remove_edge(3, 5)
  assert g.tarjan_dominators(10) == g.doms[10][0] and g.doms[10][0] == correct_dom and all(set(x) == g.doms[10][1][i+1] for i, x in enumerate(correct_j))
  
def tarjan_doms_jedges(root, succ):
  doms = tarjan_doms(root, succ)
  return doms, get_j_edges(succ, doms)
  
def verify_inc_dec_dominators(output_dir, delete_method=METHOD_SGL):
  iterations, nodes = 1000, 15
  graph.verification_algo_test(iterations, lambda: graph.random_digraph(nodes, False), [init_dom],
    [lambda n, data: None],
    [lambda n, data: None],
    [lambda x, y, root, succ, pred, data, _: inc_dom_sreedhar_gao_lee(succ, data[0], data[1], x, y)],
    [lambda x, y, root, succ, pred, data, _: dec_dom_sreedhar_gao_lee(succ, pred, data[0], data[1], None, None, None, x, y, delete_method)],
    [lambda x, y, root, succ, pred, graph_data: tarjan_doms_jedges(root, succ)],
    print_func=lambda x, y, root, succ, pred, graph_data, base: print_doms(x, y, root, succ, graph_data[0][0], graph_data[0][1], base, output_dir))
    
def verify_inc_dec_dominators_lnf(output_dir): pass