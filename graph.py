import os
class DisjointSet: #Union-Find https://en.wikipedia.org/wiki/Disjoint-set_data_structure
  def __init__(self, items = None):
    self.djs_forest = dict()
    if not items is None:
      for x in items: self.djs_forest[x] = DisjointSet.DisjointSetItem(x)
  def makeSet(self, x):
    if not x in self.djs_forest:
      self.djs_forest[x] = DisjointSet.DisjointSetItem(x)
  def delSet(self, x):
    #if self.djs_forest[x].parent != self.djs_forest[x] and any(self.djs_forest[x] == y.parent for y in self.djs_forest): raise ValueError
    del self.djs_forest[x]
  def unmerge(self, tree):
    for x in tree: self.djs_forest[x].parent = self.djs_forest[x]
  def find(self, item):
    return DisjointSet._find_internal(self.djs_forest[item]).value
  def _find_internal(item): #path compression
    #if item.parent != item: item.parent = DisjointSet._find_internal(item.parent)
    #return item.parent
    root = item #non-recursive path compression algorithm
    while root.parent != root:
      root = root.parent
    while item.parent != root:
      parent = item.parent
      item.parent = root
      item = parent
    return root
  def union(self, set1, set2, ordered = False):
    return DisjointSet._union_internal(self.djs_forest[set1], self.djs_forest[set2], ordered)
  def _union_internal(set1, set2, ordered):
    root1 = DisjointSet._find_internal(set1)
    root2 = DisjointSet._find_internal(set2)
    if root1 == root2: return
    #if root1.size < root2.size:
    if not ordered and root1.rank < root2.rank:
      root1, root2 = root2, root1
    root2.parent = root1
    if root1.rank == root2.rank: root1.rank += 1
    #root1.size += root2.size
  def __repr__(self): return str(self)
  def __str__(self): return str({str((x, str(self.djs_forest[x]))) for x in self.djs_forest})
  class DisjointSetItem:
    def __init__(self, x):
      self.value = x
      self.parent = self
      self.rank = 0
      #self.size = 1
    def __repr__(self): return str(self)
    def __str__(self): return str((self.value, self.parent.value, self.rank))
#https://en.wikipedia.org/wiki/Partition_refinement
class PartitionRefinement:
  def __init__(self, items = None):
    self.seq = DLinkedList()
    self.sdict, self.ldict = {}, {}
    if not items is None:
      s = DLinkedList.Node(DLinkedList())
      self.seq.add_node(s)
      for x in items:
        self.sdict[x] = s
        self.ldict[x] = DLinkedList.Node(x)
        s.dataval.add_node(self.ldict[x])
  def add(self, item, toset=None):
    if toset is None:
      toset = DLinkedList.Node(DLinkedList())
      self.seq.add_node(toset)
    self.sdict[item] = toset
    self.ldict[item] = DLinkedList.Node(item)
    toset.dataval.add_node(self.ldict[item])
  def isEmpty(self): return self.seq.isEmpty()
  def isIsolatedItem(self, x):
    s = self.find(x)
    return s.dataval.headval is s.dataval.headval.nextval
  def find(self, item): return None if not item in self.sdict else self.sdict[item]
  def enumerate(self):
    x = None
    while True:
      x = self.next(x)
      if x is None: return ()
      yield x
  def next(self, item):
    if self.isEmpty(): return None
    if item is None: return self.seq.headval.dataval.headval.dataval
    l, s = self.ldict[item], self.sdict[item]
    if l.nextval == s.dataval.headval:
      if s.nextval == self.seq.headval: return None
      return s.nextval.dataval.headval.dataval
    else: return l.nextval.dataval
  def pop(self):
    item = self.seq.headval.dataval.headval.dataval
    self.remove(item)
    return item
  def move(self, item, newset):
    l, s = self.ldict[item], self.sdict[item]
    s.dataval.remove_node(l)
    newset.dataval.add_node(l)
    self.sdict[item] = newset
    if s.dataval.isEmpty(): self.seq.remove_node(s)
  def split(self, item, after=False):
    l, s = self.ldict[item], self.sdict[item]
    if l.nextval == l: return s
    toset = DLinkedList.Node(DLinkedList())
    s.dataval.remove_node(l); toset.dataval.add_node(l)
    self.sdict[item] = toset
    if after: self.seq.add_node_after(toset, s)
    else: self.seq.add_node_before(toset, s)
    return toset
  def remove(self, item):
    l, s = self.ldict[item], self.sdict[item]
    del self.ldict[item]; del self.sdict[item]
    s.dataval.remove_node(l)
    if s.dataval.isEmpty(): self.seq.remove_node(s)
  def __eq__(self, other):
    return self.seq == other.seq
  def __str__(self): return self.__repr__()
  def __repr__(self):
    ptr = self.seq.headval
    vals = []
    while not ptr is None:
      vals.append(ptr.dataval)
      ptr = ptr.nextval
      if ptr is self.seq.headval: break
    return str(vals)
class SLinkedList:
  def __init__(self):
    self.headval = None
  def isEmpty(self): return self.headval is None
  def add_node(self, node):
    if self.headval is None: node.nextval = node; self.headval = node; return
    n = self.headval
    while not n.nextval is self.headval:
      n = n.nextval
    n.nextval = node
    node.nextval = self.headval
  def remove_node(self, node):
    if self.headval is self.headval.nextval: self.headval = None; return
    n = self.headval
    while not n.nextval is node:
      n = n.nextval
    n.nextval = node.nextval
  class Node:
    def __init__(self, dataval=None):
      self.dataval = dataval
      self.nextval = None
class DLinkedList:
  def __init__(self):
    self.headval = None
  def isEmpty(self): return self.headval is None
  def add_node(self, node):
    if self.headval is None: node.nextval = node; node.prevval = node; self.headval = node; return
    node.nextval = self.headval
    node.prevval = self.headval.prevval
    self.headval.prevval.nextval = node
    self.headval.prevval = node
  def add_node_before(self, node, priornode):
    if priornode is self.headval:
      self.add_node(node); self.headval = node; return
    node.nextval = priornode
    node.prevval = priornode.prevval
    priornode.prevval.nextval = node
    priornode.prevval = node
  def add_node_after(self, node, postnode):
    node.nextval = postnode.nextval
    node.prevval = postnode
    postnode.nextval.prevval = node
    postnode.nextval = node
  def add_node_sorted(self, node):
    if self.headval is None: node.nextval = node; node.prevval = node; self.headval = node; return
    if node.dataval < self.headval.dataval:
      self.add_node(node); self.headval = node; return
    n = self.headval.nextval
    while not n is self.headval and n.dataval < node.dataval:
      n = n.nextval
    node.nextval = n
    node.prevval = n.prevval
    n.prevval.nextval = node
    n.prevval = node
  def find_node(self, value):
    n = self.headval
    while n.dataval < value: n = n.nextval
    return n
  def get_nodes(self, start=None):
    if start is None: start = self.headval
    if start is None: return []
    nodes = [start.dataval]
    start = start.nextval
    while start != self.headval: nodes.append(start.dataval); start = start.nextval
    return nodes
  def get_nodes_before(self, end):
    if self.headval == end: return []
    nodes = []
    end = end.prevval
    while end != self.headval: nodes.append(end.dataval); end = end.prevval
    nodes.append(self.headval.dataval)
    return nodes
  def remove_node(self, node):
    if self.headval is self.headval.nextval: self.headval = None; return
    node.prevval.nextval = node.nextval
    node.nextval.prevval = node.prevval
    if self.headval is node: self.headval = node.nextval
  def __eq__(self, other):
    x, y = self.headval, other.headval
    while True:
      if x.dataval != y.dataval: return False
      x, y = x.nextval, y.nextval
      if x == self.headval or y == other.headval: return x == self.headval and y == other.headval
  def __str__(self):
    if self.headval is None: return str([])
    datas = [self.headval.dataval]
    node = self.headval.nextval
    while not node is self.headval:
      datas.append(node.dataval)
      node = node.nextval
    return str(datas)
  def __repr__(self): return str(self)
  class Node:
    def __init__(self, dataval=None):
      self.dataval = dataval
      self.nextval = None
      self.prevval = None
class Tree:
  def __init__(self, root=1, init=None, pred_init=None, dict_pred_init=None, check_validity=False, use_depth=False):
    self.virtual_root = root; self.succ, self.pred = {root: []}, {root: None}
    if use_depth: self.level = {root: 0}
    self.check_validity = check_validity; self.use_depth = use_depth
    self.root_succ = []
    if not init is None:
      for x in range(1, len(init)+1):
        if x != root: self.add_node(x)
      for i, x in enumerate(init):
        for y in x: self.add_edge(i + 1, y)
    elif not pred_init is None:
      for i, x in enumerate(pred_init):
        if i + 1 == self.virtual_root: continue
        self.add_node(i + 1)
      for i, x in enumerate(pred_init):
        if i + 1 == self.virtual_root: continue
        self.add_edge(x, i + 1)
    elif not dict_pred_init is None:
      for x in dict_pred_init:
        if x == self.virtual_root: continue
        self.add_node(x)
      for x in dict_pred_init:
        if x == self.virtual_root: continue
        self.add_edge(dict_pred_init[x], x)
  def graphviz_dot(self, lbl, ordered=None):
    if len(self.succ) == 1: return str(self.virtual_root)
    s = ";".join(lbl + str(x) + "->" + lbl + str(y) for x in self.succ for y in (self.succ[x] if ordered is None else sorted(self.succ[x], key=lambda z: ordered[z])))
    return s #return "digraph { rankdir=TB; " + s + "}"
  def add_node(self, n):
    self.succ[n], self.pred[n] = [], self.virtual_root
    if self.use_depth: self.level[n] = self.level[self.virtual_root] + 1
    self.succ[self.virtual_root].append(n)
    if self.check_validity: self.checkTreeValid()
  def remove_node(self, n):
    #print(n, self.succ[n], self.pred[n], self.root_succ)
    if len(self.succ[n]) == 0 and self.pred[n] == self.virtual_root and not n in self.root_succ:
      del self.succ[n]; del self.pred[n]; self.succ[self.virtual_root].remove(n)
      if self.use_depth: del self.level[n]
    else: raise ValueError
    if self.check_validity: self.checkTreeValid()
  def add_edge(self, x, y, delay_redepth=False):
    if self.pred[y] != self.virtual_root: raise ValueError
    if x == self.virtual_root:
      self.root_succ.append(y)
      return
    self.succ[self.virtual_root].remove(y)
    self.succ[x].append(y); self.pred[y] = x
    if self.use_depth and not delay_redepth: self.level[y] = self.level[x] + 1; self.redepthSubTree(y)
    if self.check_validity: self.checkTreeValid()
  def add_edge_first(self, x, y, delay_redepth=False):
    if self.pred[y] != self.virtual_root: raise ValueError
    if x == self.virtual_root:
      self.root_succ.insert(0, y)
      self.succ[x].remove(y)
      self.succ[x].insert(0, y)
      return
    self.succ[self.virtual_root].remove(y)
    self.succ[x].insert(0, y); self.pred[y] = x
    if self.use_depth and not delay_redepth: self.level[y] = self.level[x] + 1; self.redepthSubTree(y)
    if self.check_validity: self.checkTreeValid()
  def add_edge_after(self, x, y, v, delay_redepth=False):
    if self.pred[y] != self.virtual_root: raise ValueError
    if x == self.virtual_root:
      self.root_succ.insert(self.root_succ.index(v)+1, y)
      self.succ[x].remove(y)
      self.succ[x].insert(self.succ[x].index(v)+1, y)
      return
    self.succ[self.virtual_root].remove(y)
    self.succ[x].insert(self.succ[x].index(v)+1, y); self.pred[y] = x
    if self.use_depth and not delay_redepth: self.level[y] = self.level[x] + 1; self.redepthSubTree(y)
    if self.check_validity: self.checkTreeValid()
  def remove_edge(self, x, y, delay_redepth=False):
    #print((x, y))
    if not y in self.succ[x]: raise ValueError
    if x == self.virtual_root:
      if y in self.root_succ: self.root_succ.remove(y)
    else: self.succ[self.virtual_root].append(y); self.succ[x].remove(y); self.pred[y] = self.virtual_root
    if self.use_depth and not delay_redepth: self.level[y] = self.level[self.virtual_root] + 1; self.redepthSubTree(y)
    if self.check_validity: self.checkTreeValid()
  def redepthSubTrees(self, xs): #xs must be sorted in by least ancestor
    i, visited = 0, set()
    while len(xs) != i:
      x = xs[i]
      if x in visited: i += 1; continue
      redepth = [x]
      self.level[x] = self.level[self.pred[x]] + 1
      while len(redepth) != 0:
        x = redepth.pop()
        visited.add(x)
        for y in self.succ[x]:
          self.level[y] = self.level[x] + 1
          redepth.append(y)
      i += 1
  def redepthSubTree(self, x):
    redepth = [x]
    while len(redepth) != 0:
      x = redepth.pop()
      for y in self.succ[x]:
        self.level[y] = self.level[x] + 1
        redepth.append(y)
  def lca(self, x, y):
    path = set()
    while not y is None: path.add(y); y = self.pred[y]
    while not x in path and x != self.virtual_root: x = self.pred[x]#; if x is None: raise ValueError
    return x
  def lcam(self, nodes):
    it = iter(nodes)
    n = next(it)
    for x in it:
      n = self.lca(n, x)
    return n
  def allAncestors(self, x, top = None):
    path = set()
    while x != top and not x is None: path.add(x); x = self.pred[x]
    return path
  def isAncestor(self, x, y):
    while not x is None:
      if x == y: return True
      x = self.pred[x]
    return False
  def subTree(self, x):
    visit, subtree = [x], set()
    while len(visit) != 0:
      x = visit.pop(); subtree.add(x)
      visit.extend(self.succ[x])
    return subtree
  def bfsSubTree(self, x):
    visit, idx = [x], 0
    while len(visit) > idx:
      visit.extend(self.succ[visit[idx]])
      idx += 1
    return visit
  def treeByLevel(self):
    visit, levels = [self.virtual_root], []
    while len(visit) != 0:
      x = visit.pop()
      if len(levels) == self.level[x]: levels.append([])
      levels[self.level[x]].append(x)
      visit.extend(self.succ[x])
    return levels
  def __eq__(self, other):
    return self.pred == other.pred
  def checkTreeValid(self):
    for x in self.root_succ:
      if not x in self.succ[self.virtual_root]: raise ValueError("Bad Virtual Root", self.root_succ, self.succ[self.virtual_root])
    visit = [self.virtual_root]
    l = 0
    while len(visit) != 0:
      x = visit.pop(); l += 1
      for y in self.succ[x]:
        if self.pred[y] != x: raise ValueError("Bad Predecessor", x, y)
        if self.use_depth and self.level[y] != self.level[x] + 1: raise ValueError("Bad Level", x, y)
      visit.extend(self.succ[x])
    if len(self.succ) != l: raise ValueError("Bad Successors", self.succ, l)
  def __repr__(self): return str(self)
  def __str__(self): return str(self.pred)
    
def do_graphviz_dot_digraph(succ, pre=""):
  return ";".join(pre + str(x) + "->" + pre + str(y) for x in succ for y in succ[x])
def do_graphviz_dot_text(l):
  strs = ["digraph { rankdir=TB "] + l
  strs.append("}")
  return ";".join(strs)

def make_graphviz_dot_text(succ, text):
  return do_graphviz_dot_text([do_graphviz_dot_digraph(succ), text])
def do_graphviz_dot(src, output_dir, filename='graph'):
  #print(src)
  from graphviz import Source
  outfile = os.path.join(output_dir, filename)
  Source(src).render(outfile, format='svg', view=True)
  if os.path.isfile(outfile + ".dot"): os.remove(outfile + ".dot")
  os.rename(outfile, outfile + ".dot")
  with open(outfile + ".tex", "w") as tex:
    tex.write(src.replace("\n", "\\noexpand\\n").replace("digraph {", "\digraph{" + filename + "}{\n"))

def succ_to_pred(succ):
  pred = {x: set() for x in succ}
  for x in succ:
    for y in succ[x]:
      pred[y].add(x)
  return pred

def inc_dec_batch_algo(edges):
  additions, deletions = {}, {}
  for isAddition, edge in edges:
    if isAddition:
      if edge in deletions: deletions.remove(edge)
      else: additions.add(edge)
    else:
      if edge in additions: additions.remove(edge)
      else: deletions.add(edge)
  return additions, deletions
  
#http://snap.stanford.edu/data/web-Stanford.html
#http://law.di.unimi.it/datasets.php

def enum_digraphs(n): #2^(n^2)
  for i in range(count_digraphs(n)):
    yield {x+1:tuple(y+1 for y in range(n) if ((1 << (x * n + y)) & i) != 0) for x in range(n)}
def enum_simple_digraphs(n): #2^(n^2-n)
  #for i in range(count_simple_digraphs(n)):
  for i in range(count_digraphs(n)):
    if any(((1 << (x * n + x)) & i) != 0 for x in range(n)): continue
    yield {x+1:tuple(y+1 for y in range(n) if ((1 << (x * n + y)) & i) != 0) for x in range(n)}
def enum_dags(n):
  #for i in range(1 << n):
  #  root_nodes = [x for x in range(n) if (1 << x) & i != 0]
  import sccreach
  for i in range(count_digraphs(n)):
    if any(((1 << (x * n + x)) & i) != 0 for x in range(n)): continue
    g = {x+1:tuple(y+1 for y in range(n) if ((1 << (x * n + y)) & i) != 0) for x in range(n)}
    if len(sccreach.tarjan_scc(g)) != len(g): continue
    yield g
def is_topo(g, topo):
  topdict = {}
  for i, x in enumerate(topo):
    topdict[x] = i
  for x in g:
    for y in g[x]:
      if topdict[x] >= topdict[y]: return False
  return True
def topo_kahn(g, randomize=False):
  if randomize: import random
  topo, S, k = [], [], 0
  inc = {u: 0 for u in g}
  for u in g:
    for v in g[u]: inc[v] += 1
  for u in g:
    if inc[u] == 0: S.append(u)
  while len(S) != 0:
    u = S.pop(0 if not randomize else random.randint(0, len(S)-1)); k += 1
    topo.append(u)
    for v in g[u]:
      inc[v] -= 1
      if inc[v] == 0: S.append(v)
  if k < len(g): raise ValueError
  return topo
def topo_kahn_levels(g):
  levels, topo, S, k = [set(), set()], [], [], 0
  inc = {u: 0 for u in g}
  for u in g:
    for v in g[u]: inc[v] += 1
  curlvl = 0
  for u in g:
    if inc[u] == 0: levels[curlvl].add(u); S.append(u)
  while len(S) != 0:
    u = S.pop(); k += 1
    if not u in levels[curlvl]: curlvl += 1; levels.append(set())
    topo.append(u)
    for v in g[u]:
      inc[v] -= 1
      if inc[v] == 0: levels[curlvl+1].add(u); S.append(v)
  if k < len(g): raise ValueError
  return topo, levels

def topo_kahn_enum(g): #O((m+n)*n!)
  topo, S, k = [], set(), 0
  inc = {u: 0 for u in g}
  for u in g:
    for v in g[u]: inc[v] += 1
  for u in g:
    if inc[u] == 0: S.add(u)
  unprocessed = {0: set(S)}
  while len(unprocessed[k]) != 0:
    while len(S) != 0:
      u = unprocessed[k].pop(); S.remove(u); k += 1
      topo.append(u)
      for v in g[u]:
        inc[v] -= 1
        if inc[v] == 0: S.add(v)
      unprocessed[k] = set(S)
    if k < len(g): raise ValueError
    yield list(topo)
    while True:
      u = topo.pop(); k -= 1
      for v in g[u]:
        if inc[v] == 0: S.remove(v)
        inc[v] += 1
      S.add(u)
      if k == 0 or len(unprocessed[k]) != 0: break
  return ()
def get_sources(g):
  return [x for x, y in succ_to_pred(g).items() if len(y) == 0]
def topo_dfs(g):
  topo, topoperm, visited = [], set(), set()
  for n in g:
    if n in topoperm: continue
    s = [(n, None)]
    while len(s) != 0:
      x, pre = s.pop()
      if pre is None:
        visited.add(x)
        pre = iter(g[x])
      for y in pre:
        if y in visited: raise ValueError
        if not y in topoperm: 
          s.append((x, pre)); s.append((y, None)); break
      else: visited.remove(x); topoperm.add(x); topo.append(x)
  return list(reversed(topo))
def do_lex_bfs_topo(succ):
  parts, t = PartitionRefinement(succ.keys()), 1
  pred = succ_to_pred(succ)
  bfs_revint, bfsrint, reachable = [], [], set()
  lvl = {}
  for x in succ:
    if len(succ[x]) == 0:
      reachable.add(x)
      parts.split(x)
      lvl[x] = 1
  i, x = 0, None
  while True:
    x = parts.next(x)
    print(x, parts)
    if x is None: break
    t += 1
    priors = {}
    for y in pred[x]:
      if x == y: continue
      after = y in lvl and lvl[x]==lvl[y]
      lvl[y]=lvl[x]+1
      reachable.add(y)
      s = parts.find(y)
      if not s is None:
        if s in priors:
          parts.move(y, priors[s])
        else:
          priors[s] = parts.split(y, after)
  return list(reversed([x for x in parts.enumerate()]))
def topo_dfs_enum(g):
  topo, topoperm, visited = [], set(), set()
  for n in g:
    if n in topoperm: continue
    s = [(n, None)]
    while len(s) != 0:
      x, pre = s.pop()
      if pre is None:
        visited.add(x)
        pre = iter(g[x])
      for y in pre:
        if y in visited: raise ValueError
        if not y in topoperm: 
          s.append((x, pre)); s.append((y, None)); break
      else: visited.remove(x); topoperm.add(x); topo.append(x)
  return list(reversed(topo))
def check_topo(n):
  for g in enum_dags(n):
    #print(g)
    #assert is_topo(g, do_lex_bfs_topo(g)), (g, do_lex_bfs_topo(g))
    assert is_topo(g, topo_dfs(g))
    assert is_topo(g, topo_kahn(g))
def topo_histogram(n):
  hist = {}
  import itertools
  for g in enum_dags(n):
    topocount = 0
    if len(g) != 0:
      for topo in itertools.permutations(g):
        if is_topo(g, topo): topocount += 1
    if not topocount in hist: hist[topocount] = 0
    print(g, [x for x in topo_kahn_enum(g)])
    assert topocount == len([x for x in topo_kahn_enum(g)])
    hist[topocount] += 1
  return hist
#https://oeis.org/A011266 a(n) = 2^(n*(n-1)/2)*n!.
def enum_topo_hist_dag(n): pass
def count_topo_hist_dag(n):
  import math
  return (1 << (n * (n-1) // 2)) * math.factorial(n)
def dfs_connect(g):
  visited = set()
  s = [(next(iter(g)), None)]
  while len(s) != 0:
    x, pre = s.pop()
    if pre is None:
      visited.add(x)
      pre = iter(g[x])
    for y in pre:
      if not y in visited:
        s.append((x, pre)); s.append((y, None)); break
  return len(visited) == len(g)
def sccs_to_dag(preds, sccs):
  g = {}
  for scc in sccs:
    s = set(scc)
    g[next(iter(s))] = set.union(*(preds[x] for x in s)) - s
  return g
"""
def sage_digraphs_loops(vertices, property=lambda x: True, size=None, sparse=True):
  if size is not None:
      extra_property = lambda x: x.size() == size
  else:
      extra_property = lambda x: True
  from sage.graphs.graph_generators import canaug_traverse_edge
  g = DiGraph(vertices, loops=True, sparse=sparse)
  gens = []
  for i in range(vertices-1):
      gen = list(range(i))
      gen.append(i+1); gen.append(i)
      gen += list(range(i+2, vertices))
      gens.append(gen)
  for gg in canaug_traverse_edge(g, gens, property, dig=True, loops=True, sparse=sparse):
      if extra_property(gg):
          yield gg
#[len(list(sage_digraphs_loops(n))) for n in range(Integer(5))]
"""
#import functools, math
def gensums(base, n):
  if n == 0: yield []; return
  if base == n: yield [1]
  if base >= n: return
  for i in range(0, n+1, base):
    yield from ([i//base] + x for x in gensums(base+1, n-i))
#[sum((1<<sum(math.gcd(i+1, j+1)*s[i]*s[j] for i in range(len(s)) for j in range(len(s))))/functools.reduce(prod, ((i+1)**s[i]*math.factorial(s[i]) for i in range(len(s)))) for s in gensums(1, n)) for n in range(1, 6)] #A000595 Relations: number of nonisomorphic unlabeled binary relations on n labeled nodes.
#[len(list(x for x in digraphs(n) if len(x.strongly_connected_components_digraph().sources())<=1)) for n in range(7)]
def enum_connected_digraphs(n, rooted=False, simple=False, nonacyclic=None, reducible=None):
  import sccreach, dfs, lnf
  for i in range(count_digraphs(n)):
    if simple and any(((1 << (x * n + x)) & i) != 0 for x in range(n)): continue  
    g = {x+1:tuple(y+1 for y in range(n) if ((1 << (x * n + y)) & i) != 0) for x in range(n)}    
    preds = succ_to_pred(g)
    #if sum(len(y - {x}) == 0 for x, y in preds.items()) > 1: continue
    if not rooted and len(g) != 0 and not dfs_connect({x: preds[x] | set(g[x]) for x in g}): continue
    elif rooted:
      sccs = sccreach.tarjan_scc(g)
      #if sum(all(len(preds[x] - set(scc)) == 0 for x in scc) for scc in sccs) > 1: continue
      sccpreds = sccs_to_dag(preds, sccs)
      if sum(len(sccpreds[x]) == 0 for x in sccpreds) > 1: continue
      if not nonacyclic is None:
        isacyclic = len(sccs) == len(g) and not any(x in g[x] for x in g)
        if nonacyclic and isacyclic or not nonacyclic and not isacyclic: continue
      if not reducible is None:
        isreducible = lnf.do_tarjan_is_reducible(preds, *dfs.do_dfs(list(range(n)), g))
        if reducible and not isreducible or not reducible and isreducible: continue
    yield g
#[len(list(digraphs(n, property=lambda g: g.is_directed_acyclic()))) for n in range(7)] #A003087 Number of acyclic digraphs with n unlabeled nodes.
def enum_connected_dags(n, rooted=False):
  import sccreach
  for i in range(count_digraphs(n)):
    if any(((1 << (x * n + x)) & i) != 0 for x in range(n)): continue
    g = {x+1:tuple(y+1 for y in range(n) if ((1 << (x * n + y)) & i) != 0) for x in range(n)}
    if len(sccreach.tarjan_scc(g)) != len(g): continue
    preds = succ_to_pred(g)
    #roots = [x for x, y in succ_to_pred(g).items() if len(y) == 0]
    if not rooted and len(g) != 0 and not dfs_connect({x: preds[x] | set(g[x]) for x in g}): continue
    elif rooted and sum(len(preds[x]) == 0 for x in preds) > 1: continue
    yield g
def relabel(g, perm):
  return {perm[x]:{perm[y] for y in g[x]} for x in g}
#https://github.com/sagemath/sage/blob/master/src/sage/groups/perm_gps/partn_ref/automorphism_group_canonical_label.pyx
#https://github.com/sagemath/sage/blob/master/src/sage/groups/perm_gps/partn_ref/refinement_graphs.pyx
def search_tree(G_in, partition, certificate=True, dig=False): #dig for digraphs or graphs with loops
  pass
#https://github.com/sagemath/sage/blob/develop/src/sage/graphs/graph_generators.py
def canaug_traverse_edge(g, aut_gens, property, dig=False, loops=False): #dig for directed vs undirected, loops for self-loops
  if not property(g): return
  yield g
  n = len(g)
  max_size = n*(n-1) if dig else (n*(n-1))>>1
  if loops: max_size += n
  if sum(len(g[x]) for x in g) < max_size:
    if dig: children = [[(j,i) for i in range(n)] for j in range(n)]
    else: children = [[(j,i) for i in range(j)] for j in range(n)]
    orbits = list(range(n))
    for gen in aut_gens: # union-find C(g) under Aut(g)
      for iii in range(n):
        if orbits[gen[iii]] != orbits[iii]:
          temp = orbits[gen[iii]]
          for jjj in range(n):
            if orbits[jjj] == temp: orbits[jjj] = orbits[iii]
        if dig: jjj_range = list(range(iii)) + list(range(iii + 1, n))
        else: jjj_range = list(range(iii))  # iii > jjj
        for jjj in jjj_range:
          i, j = iii, jjj
          if dig: x, y = gen[i], gen[j]
          else: y, x = sorted([gen[i], gen[j]])
          if children[i][j] != children[x][y]:
            x_val, y_val = x, y
            i_val, j_val = i, j
            if dig:
              while (x_val, y_val) != children[x_val][y_val]:
                x_val, y_val = children[x_val][y_val]
              while (i_val, j_val) != children[i_val][j_val]:
                i_val, j_val = children[i_val][j_val]
            else:
              while (x_val, y_val) != children[x_val][y_val]:
                y_val, x_val = sorted(children[x_val][y_val])
              while (i_val, j_val) != children[i_val][j_val]:
                j_val, i_val = sorted(children[i_val][j_val])
            while (x, y) != (x_val, y_val):
              xx, yy = x, y
              x, y = children[x][y]
              children[xx][yy] = (x_val, y_val)
            while (i, j) != (i_val, j_val):
              ii, jj = i, j
              i, j = children[i][j]
              children[ii][jj] = (i_val, j_val)
            if x < i:
              children[i][j] = (x, y)
            elif x > i:
              children[x][y] = (i, j)
            elif y < j:
              children[i][j] = (x, y)
            elif y > j:
              children[x][y] = (i, j)
            else:
              continue
    roots = [] # find representatives of orbits of C(g)
    for i in range(n):
      if dig: j_range = list(range(i)) + list(range(i + 1, n))
      else: j_range = list(range(i))
      for j in j_range:
        if children[i][j] == (i, j): roots.append((i,j))
    if loops:
      seen = set()
      for i in range(n):
        if orbits[i] not in seen:
          roots.append((i,i))
          seen.add(orbits[i])
    for i, j in roots:
      if j in g[i]: continue
      # construct a z for each edge in roots...
      z = {x: g[x].copy() for x in g}
      z[i].add(j)
      if not property(z): continue
      z_aut_gens, _, canonical_relabeling = search_tree(z, [z.vertices()], certificate=True, dig=(dig or loops))
      relabel_inverse = [0]*n
      for ii in range(n):
        relabel_inverse[canonical_relabeling[ii]] = ii
      z_can = relabel(z, canonical_relabeling)
      cut_edge_can = z_can.edges(labels=False, sort=True)[-1]
      cut_edge = [relabel_inverse[cut_edge_can[0]], relabel_inverse[cut_edge_can[1]]]
      if dig: cut_edge = tuple(cut_edge)
      else: cut_edge = tuple(sorted(cut_edge))
      m_z = {x : z[x].copy() for x in z}
      m_z[cut_edge[0]].remove(cut_edge[1])
      if m_z == g:
        for a in canaug_traverse_edge(z, z_aut_gens, property, dig=dig, loops=loops):
            yield a
      else:
        for possibility in check_aut_edge(z_aut_gens, cut_edge, i, j, n, dig=dig):
          if relabel(m_z, possibility) == g:
            for a in canaug_traverse_edge(z, z_aut_gens, property, dig=dig, loops=loops):
              yield a
            break
def check_aut_edge(aut_gens, cut_edge, i, j, n, dig=False):
  perm = list(range(n))
  seen_perms = {perm}
  unchecked_perms = [perm]
  while unchecked_perms:
    perm = unchecked_perms.pop(0)
    for gen in aut_gens:
      new_perm = perm.copy()
      for ii in range(n):
        new_perm[ii] = gen[perm[ii]]
      if new_perm not in seen_perms:
        seen_perms.add(new_perm)
        unchecked_perms.append(new_perm)
        if new_perm[cut_edge[0]] == i and new_perm[cut_edge[1]] == j:
          yield new_perm
        if not dig and new_perm[cut_edge[0]] == j and new_perm[cut_edge[1]] == i:
          yield new_perm  
#[math.factorial(x) for x in range(20)]
#[2**(x**2) for x in range(20)]
#https://oeis.org/A002416 a(n) = 2^(n^2).
def count_digraphs(n):
  return 1 << (n * n)
#https://oeis.org/A053763 a(n) = 2^(n^2 - n).
def count_simple_digraphs(n): #a(n)=2^(n(n-1))
  return 1 << (n * (n - 1))
#https://oeis.org/A003024/a003024.pdf
#https://oeis.org/A003024 Number of acyclic digraphs (or DAGs) with n labeled nodes.
def count_dags(n): #a(n)=sum{k=1..n}(-1^(k-1))(n choose k)*2^(k(n-k))a(n-k) a(0)=1
  if n == 0: return 1
  import math
  return sum((1 if k & 1 != 0 else -1) * math.comb(n, k) * (1 << (k * (n - k))) * count_dags(n - k) for k in range(1, n+1))
#https://oeis.org/A003087 Number of acyclic digraphs with n unlabeled nodes.
#Counting unlabeled acyclic digraphs by RW Robinson 1977
#https://oeis.org/A003025 Number of n-node labeled acyclic digraphs with 1 out-point.
def a_km(k, m):
  if m == 0: return 1
  import math
  return sum(math.comb(k+m, k) * (2 ** k - 1) ** s * 2 ** (k * (m-s)) * a_km(s, m-s) for s in range(1, m+1))
def count_dags_one_outpoint(n): return a_km(1, n)
#http://oeis.org/A082402 - Number of n-node labeled weakly connected acyclic digraphs.
def count_connected_dags(n):
  if n == 0: return 1
  import math
  return count_dags(n) - sum(math.comb(n-1, k-1)*count_connected_dags(k)*count_dags(n-k) for k in range(1, n))
#http://oeis.org/A003027 Number of weakly connected digraphs with n nodes.
def count_simple_connected_digraphs(n):
  if n == 0: return 1
  import math
  return 2 ** (n * n - n) - sum(k * math.comb(n, k) * count_simple_connected_digraphs(k) * 2 ** ((n-k)*(n-k)-(n-k)) for k in range(1, n)) // n
#https://oeis.org/A062738 Number of connected labeled relations.
def count_connected_digraphs(n):
  if n == 0: return 1
  import math
  return 2 ** (n * n) - sum(k * math.comb(n, k) * count_connected_digraphs(k) * 2 ** ((n-k)*(n-k)) for k in range(1, n)) // n  
  #return count_simple_connected_digraphs(n) * 2 ** n
#https://core.ac.uk/download/pdf/82730926.pdf
def lmbda_mn(m, n):
  if n == 0: return 1
  import math
  return 2 ** (n*(n+m-1)) - sum(math.comb(n, k) * 2 ** ((n-k)*(n-1)) * lmbda_mn(m, k) for k in range(n))
def lmbda_knm(k, n, m):
  if m == 0: return 1
  import math
  return lmbda_mn(k, m) * 2 ** (m * n) - sum(math.comb(m, i) * lmbda_mn(k+i, m-i) * lmbda_knm(k, n, i) for i in range(m))
def itilda(n): #number of initially connected digraphs with n points and a fixed source
  if n == 0: return 1
  import math
  return 2 ** (n * n - n) - sum(math.comb(n-1, k-1) * itilda(k) * 2 ** ((n-k)*(n-1)) for k in range(1, n))
def i_kn(k, n):
  import math
  return math.comb(n, k) * lmbda_mn(k, n-k) * s_n(k)
def i_n_selfloops(n):
  return i_n(n) * 2**n
#https://oeis.org/A003028 Number of n-node digraphs with a source.
def i_n(n):
  return sum(i_kn(j, n) for j in range(1, n+1))
#https://oeis.org/A003030 Number of strongly connected digraphs with n labeled nodes.
def s_n(n): #number of SCCs with n points
  if n <= 1: return 1
  import math
  return itilda(n) - sum(math.comb(n-1, j-1) * lmbda_mn(j, n-j) * s_n(j) for j in range(1, n)) 
def lmbda_bar(i, j, k):
  return (2 ** (i * j) - 1) if k == 0 else (2 ** (i * j) * lmbda_knm(i, j, k))
def alpha_ni(n, i):
  if n == i: return s_n(n)
  import math
  return s_n(i) * (lmbda_mn(i, n-i) - sum(sum(2 ** (k*(n-j-k)) * math.comb(n-i, j) * math.comb(n-i-j, k) * lmbda_bar(j, i, n-i-j-k) * alpha_ni(j+k, j) for k in range(n-i-j+1)) for j in range(1, n-i+1))) #i < n
#https://oeis.org/A049414 Number of quasi-initially connected digraphs with n labeled nodes.
def count_simple_rooted_connected_digraphs(n):
  import math
  return sum(sum(math.comb(n, i) * math.comb(n-i, j) * 2 ** (j*(n-i-j)) * lmbda_mn(i, n - i - j) * alpha_ni(i+j, i) for j in range(n-i+1)) for i in range(1, n+1))
def graph_seqs(max, func):
  n, l = 0, []
  while True:
    c = func(n)
    l.append(c)
    if c > max: break
    n += 1
  print(l)
  return l
def graph_enum(n, func):
  return sum(1 for _ in func(n))
  l = [x for x in func(n)]
  assert len(l) == len({frozenset(x.items()) for x in l})
  print(len(l))
  return len(l)
def get_real_graph(digraph_dir):
  edges = []
  filePath = os.path.join(digraph_dir, "web-Stanford.txt")
  with open(filePath) as fp:
    line = fp.readline()
    while line:
      if line[0] != '#':
        edge = line.split("\t")
        edges.append((int(edge[0]), int(edge[1])))
      line = fp.readline()
  return edges
def get_random_cfgs(count, size, acyclic=False, randseed=None):
  import random
  random.seed(randseed)
  for _ in range(count):
    reaching = dict()
    succs = []
    for i in range(1, size+1):
      if i == 2: reaching[3] = True; succs.append([3])
      elif i == 3: succs.append([])
      else:
        if i == 1: nxt = 4
        elif i == size: nxt = 2
        else: nxt = i + 1
        if nxt in reaching: num = random.randint(1, 5); succs.append([])
        else: num = random.randint(1, 4); reaching[nxt] = True; succs.append([nxt])
        for j in range(1, num+1):
          r = random.randint(1, size - 1)
          ne = i + r if i == 1 else (i + r - size if i + r > size else i + r)
          if ne == 3: continue
          if (ne == 2 or ne == 3) and succs[-1] != [] or succs[-1] == [2] or succs[-1] == [3]: continue
          if acyclic and ne != 2 and ne != 3 and i >= ne: continue
          reaching[ne] = True
          succs[-1].append(ne)
    yield [list(set(x)) for x in succs]
def random_digraph(size, maintain_conn=True):
  import random
  #random.seed()
  reach = [1]
  edges = []
  edgeset = set()
  for x in range((size * size) >> 1):
    while True:
      source = random.choice(reach) if maintain_conn else random.randint(1, size)
      dest = random.randint(1, size)
      if not (source, dest) in edgeset: break
    reach.append(dest)
    edges.append((source, dest))
    edgeset.add((source, dest))
  return edges
def random_local_digraph(size, out_degree, locality):
  import random
  #random.seed()
  reach = [1]
  edges = []
  edgeset = set()
  for x in range(size * out_degree):
    source = random.choice(reach)
    while True:
      dest = random.randint(x - locality, x + locality) % size + 1
      if not (source, dest) in edgeset: break
    reach.append(dest)
    edges.append((source, dest))
    edgeset.add((source, dest))
  return edges
#IDA v7.0 Freeware Download Page: https://www.hex-rays.com/products/ida/support/download_freeware/
#gengraphs.idc script will export call graphs      
def get_real_cfgs(cfg_dir):
  import glob
  import os
  import re
  libNames = ["kernel32.dll", "user32.dll", "explorer.exe", "sendmail", "smbd", "vsftpd"]
  allEdges = []
  for libName in libNames:
    for filePath in glob.glob(cfg_dir + "/" + libName + "/*.gdl"):
      edges = []
      with open(filePath) as fp:
        line = fp.readline()
        while line:
          match = re.search("^edge: { sourcename: \"(\w+)\" targetname: \"(\w+)\" label: \"\w+\" color: \w+ }\n$", line)
          if match is None: match = match = re.search("^edge: { sourcename: \"(\w+)\" targetname: \"(\w+)\" }\n$", line)
          if not match is None:
            edges.append((int(match[1]), int(match[2])))
          line = fp.readline()
      if len(edges) != 0: allEdges.append(edges)
  print(len(allEdges))
  return allEdges
  
def batch_gen(l, batch_size):
  return [l // batch_size + (1 if z < l % batch_size else 0) for z in range(batch_size)]

def verification_algo_test(iterations, edge_gen, init_funcs, add_node_funcs, 
    remove_node_funcs, add_edge_funcs, remove_edge_funcs, compare_funcs, comparer=lambda x, y: x == y,
    batches=None, batch_init_funcs=None, batch_add_node_funcs=None, batch_remove_node_funcs=None,
    batch_add_funcs=None, batch_remove_funcs=None, edge_condition=None, inc_edge_condition=None, dec_edge_condition=None, print_func=None, seed=None):
  import random
  random.seed(seed)
  root = 1
  for i in range(iterations):
    #print(i)
    pred, succ = {root: set()}, {root: set()}
    edges = edge_gen()
    graph_data = [x(root) for x in init_funcs]
    if not batches is None: batch_sizes, batchnum, batch, batch_graph_data = batch_gen(len(edges), batches), 0, set(), [x(root) for x in batch_init_funcs]
    for a, b in edges:
      if not a in succ:
        succ[a] = set(); pred[a] = set()
        for i, x in enumerate(add_node_funcs): x(a, graph_data[i])
        if not batches is None:
          for i, x in enumerate(batch_add_node_funcs): x(a, batch_graph_data[i])      
      if not b in succ:
        succ[b] = set(); pred[b] = set()
        for i, x in enumerate(add_node_funcs): x(b, graph_data[i])
        if not batches is None:
          for i, x in enumerate(batch_add_node_funcs): x(b, batch_graph_data[i])
      if not batches is None: batch.add((a, b))
      succ[a].add(b); pred[b].add(a)
      if not edge_condition is None:
        result = [x(a, b, root, succ, pred, graph_data) for x in edge_condition]
        for x in result[1:]: assert x == result[0]
        for i, x in enumerate(inc_edge_condition):
          if result[0] != x(a, b, root, succ, pred, graph_data[i], graph_data):
            if not print_func is None: print_func(a, b, root, succ, pred, graph_data, None)
            assert False, "Adding Edge Condition %d->%d (%s)" % (a, b, result[0])
        if not result[0]:
          succ[a].remove(b); pred[b].remove(a)
          for i, x in enumerate(dec_edge_condition):
            x(a, b, root, succ, pred, graph_data[i], graph_data)
          if not all([x(a, b, root, succ, pred, graph_data) for x in edge_condition]):
            if not print_func is None: print_func(a, b, root, succ, pred, graph_data, None)
            assert False, "Removing Edge Condition %d->%d (%s)" % (a, b, result[0])
          continue
      for i, x in enumerate(add_edge_funcs): x(a, b, root, succ, pred, graph_data[i], graph_data)
      if not batches is None and len(batch) == batch_sizes[batchnum]:
        for i, x in enumerate(batch_add_funcs): x(batch, root, succ, pred, batch_graph_data[i])
        batchnum += 1; batch.clear()
      result = [x(a, b, root, succ, pred, graph_data) for x in compare_funcs]
      for x in graph_data:
        if not comparer(x, result[0]):
          if not print_func is None: print_func(a, b, root, succ, pred, graph_data, result[0])
          assert False, "Adding Edge %d->%d %s %s" % (a, b, x, result[0])
      for x in result[1:]: assert comparer(x, result[0])
      if not batches is None and len(batch) == 0:
        for x in batch_graph_data: assert comparer(x, result[0])
    if not batches is None: batchnum, batchsucc, batchpred = 0, {x: y.copy() for x, y in succ.items()}, {x: y.copy() for x, y in pred.items()}
    while len(edges) != 0:
      a, b = edges.pop()
      if not batches is None: batch.add((a, b))
      if not edge_condition is None and not b in succ[a]: continue
      succ[a].remove(b); pred[b].remove(a)
      if not batches is None: batchsucc[a].remove(b); batchpred[b].remove(a)
      for i, x in enumerate(remove_edge_funcs): x(a, b, root, succ, pred, graph_data[i], graph_data)
      if a != root and len(pred[a]) == 0 and len(succ[a]) == 0:
        del succ[a]; del pred[a]
        for i, x in enumerate(remove_node_funcs): x(a, graph_data[i])
      if a != b and b != root and len(pred[b]) == 0 and len(succ[b]) == 0:
        del succ[b]; del pred[b]
        for i, x in enumerate(remove_node_funcs): x(b, graph_data[i])
      if not batches is None and len(batch) == batch_sizes[batchnum]:
        for i, x in enumerate(batch_remove_funcs): x(batch, root, batchsucc, batchpred, batch_graph_data[i])        
        for _, b in batch:
          if b != root and b in batchpred and len(batchpred[b]) == 0:
            del batchsucc[b]; del batchpred[b]
            for i, x in enumerate(batch_remove_node_funcs): x(b, batch_graph_data[i])
        batchnum += 1; batch.clear()
      result = [x(a, b, root, succ, pred, graph_data) for x in compare_funcs]
      for x in graph_data:
        if not comparer(x, result[0]):
          if not print_func is None: print_func(a, b, root, succ, pred, graph_data, result[0])
          assert False, "Removing Edge %d->%d" % (a, b)
      for x in result[1:]: assert comparer(x, result[0])
      if not batches is None and len(batch) == 0:
        for x in batch_graph_data: assert comparer(x, result[0])

def timing_test(iterations, edge_gen, repeat, init_funcs, add_node_funcs,
    remove_node_funcs, add_edge_funcs, remove_edge_funcs, offline_funcs,
    batches=None, batch_init_funcs=None, batch_add_node_funcs=None, batch_remove_node_funcs=None,
    batch_add_funcs=None, batch_remove_funcs=None, edge_condition=None, inc_edge_condition=None, dec_edge_condition=None, seed=None, delete_first=False):
  import random
  import timeit
  random.seed(seed)
  root = 1
  offlinecumtotals, offlinetotals = [0 for x in offline_funcs], [0 for x in offline_funcs]
  itotals, dtotals = [0 for x in init_funcs], [0 for x in init_funcs]
  if not batches is None: bitotals, bdtotals, offlinebatchtotals = [0 for x in batch_init_funcs], [0 for x in batch_init_funcs], [0 for x in offline_funcs]
  for i in range(iterations):
    #print(i)
    edges = edge_gen()
    if not batches is None: batch_sizes, batch = batch_gen(len(edges), batches), set()
    for _ in range(repeat):
      pred, succ = {root: set()}, {root: set()}
      graph_data = [x(root) for x in init_funcs]
      if not batches is None: batchnum, batch_graph_data = 0, [x(root) for x in batch_init_funcs]
      check = 0
      for a, b in edges:
        check += 1
        if check % 10000 == 0: print(check)
        ot = []
        if not a in succ:
          succ[a] = set(); pred[a] = set()
          for i, x in enumerate(add_node_funcs): x(a, graph_data[i])
          if not batches is None:
            for i, x in enumerate(batch_add_node_funcs): x(a, batch_graph_data[i])        
        if not b in succ:
          succ[b] = set(); pred[b] = set()
          for i, x in enumerate(add_node_funcs): x(b, graph_data[i])
          if not batches is None:
            for i, x in enumerate(batch_add_node_funcs): x(b, batch_graph_data[i])
        if not batches is None: batch.add((a, b))
        succ[a].add(b); pred[b].add(a)
        if not edge_condition is None:
          result = [x(a, b, root, succ, pred, graph_data) for x in edge_condition]
          for x in result[1:]: assert x == result[0]
          for i, x in enumerate(inc_edge_condition):
            assert result[0] == x(a, b, root, succ, pred, graph_data[i], graph_data)
          if not result[0]:
            succ[a].remove(b); pred[b].remove(a)
            for i, x in enumerate(dec_edge_condition):
              x(a, b, root, succ, pred, graph_data[i], graph_data)
            continue        
        for i, x in enumerate(add_edge_funcs):
          itotals[i] += timeit.timeit(lambda: x(a, b, root, succ, pred, graph_data[i], graph_data), number=1)
        for i, x in enumerate(offline_funcs):
          ot.append(timeit.timeit(lambda: x(a, b, root, succ, pred, graph_data), number=1))
        if not batches is None and len(batch) == batch_sizes[batchnum]:
          for i, x in enumerate(batch_add_funcs):
            bitotals[i] += timeit.timeit(lambda: x(batch, root, succ, pred, batch_graph_data[i]), number=1)
          for i, x in enumerate(ot): offlinebatchtotals[i] += x
          batchnum += 1; batch.clear()
        for i, x in enumerate(ot): offlinecumtotals[i] += x
      if not batches is None: batchnum, batchsucc, batchpred = 0, {x: y.copy() for x, y in succ.items()}, {x: y.copy() for x, y in pred.items()}
      for i, x in enumerate(ot): offlinetotals[i] += x
      for a, b in reversed(edges):
        if not batches is None: batch.add((a, b))
        if not edge_condition is None and not b in succ[a]: continue
        succ[a].remove(b); pred[b].remove(a)
        if not batches is None: batchsucc[a].remove(b); batchpred[b].remove(a)
        for i, x in enumerate(remove_edge_funcs):
          dtotals[i] += timeit.timeit(lambda: x(a, b, root, succ, pred, graph_data[i], graph_data), number=1)
        if a != root and len(pred[a]) == 0 and len(succ[a]) == 0:
          del succ[a]; del pred[a]
          for i, x in enumerate(remove_node_funcs): x(a, graph_data[i])
        if a != b and b != root and len(pred[b]) == 0 and len(succ[b]) == 0:
          del succ[b]; del pred[b]
          for i, x in enumerate(remove_node_funcs): x(b, graph_data[i])
        if not batches is None and len(batch) == batch_sizes[batchnum]:
          for i, x in enumerate(batch_remove_funcs):
            bdtotals[i] += timeit.timeit(lambda: x(batch, root, batchsucc, batchpred, batch_graph_data[i]), number=1)        
          for _, b in batch:
            if b != root and b in batchpred and len(batchpred[b]) == 0:
              del batchsucc[b]; del batchpred[b]
              for i, x in enumerate(batch_remove_node_funcs): x(b, batch_graph_data[i])
          batchnum += 1; batch.clear()
  if batches is None: return itotals, dtotals, offlinecumtotals, offlinetotals
  return itotals, dtotals, offlinecumtotals, offlinetotals, bitotals, bdtotals, offlinebatchtotals
def param_timing_test(): pass