import graph
import cfg
import dfs

def dfs_reachability(succ): #naive O(n(n+m)) could even naively (without SCC) reduce to O(n^2+m+n) by doing set propogation and DFS reverse preorder
  reach = {}
  for x in succ:
    visit, visited = {x}, set()
    while len(visit) != 0:
      v = visit.pop()
      for w in succ[v]:
        if not w in visited: visit.add(w); visited.add(w)
    reach[x] = visited
  return reach
def floyd_warshall_reachability(succ): #O(n^3)
  v = len(succ)
  reach = {i: succ[i].copy() for i in succ}
  for k in succ:
    for i in succ:
      for j in succ:
        if k in reach[i] and j in reach[k]: reach[i].add(j)
  return reach
def tarjan_scc(succ, subg=None):
  index, s, indexes, lowlinks, onStack, allscc = 0, [], {}, {}, set(), []
  def strong_connect(v, index):
    stack = [(v, None, iter(succ[v]))]
    while len(stack) != 0:
      v, w, succv = stack.pop()
      if w is None:
        indexes[v] = index; lowlinks[v] = index; onStack.add(v)
        index += 1
        s.append(v)
      else: lowlinks[v] = min(lowlinks[v], lowlinks[w])
      for w in succv:
        if not subg is None and not w in subg: continue
        if not w in indexes: stack.append((v, w, succv)); stack.append((w, None, iter(succ[w]))); break
        elif w in onStack:
          lowlinks[v] = min(lowlinks[v], indexes[w])
      else:
        if lowlinks[v] == indexes[v]:
          scc = []
          while True:
            w = s.pop()
            onStack.remove(w)
            scc.append(w)
            if w == v: break
          allscc.append(scc)
    return index
  for v in succ.keys():
    if (subg is None or v in subg) and not v in indexes:
      index = strong_connect(v, index)
  return allscc
def nuutila_reach_scc(succ, subg=None):
  index, s, sc, sccs, reach = 0, [], [], {}, {}
  indexes, lowlink, croot, stackheight = {}, {}, {}, {}
  def nuutila(v, index):
    #index/D, lowlink/CCR/component candidate root, final component/C, component stack height/H
    stack = [(v, None, iter(succ[v]))]
    while len(stack) != 0:
      v, w, succv = stack.pop()
      if w is None:
        indexes[v], lowlink[v] = index, v
        stackheight[v] = len(sc)
        index += 1
        s.append(v)
      elif not w in croot:
        if indexes[lowlink[w]] < indexes[lowlink[v]]: lowlink[v] = lowlink[w]
      else: sc.append(croot[w])
      for w in succv:
        if not subg is None and not w in subg: continue
        forward_edge = False
        if not w in indexes: stack.append((v, w, succv)); stack.append((w, None, iter(succ[w]))); break #index = nuutila(w, index)
        else: forward_edge = indexes[v] < indexes[w]
        if not w in croot:
          if indexes[lowlink[w]] < indexes[lowlink[v]]: lowlink[v] = lowlink[w]
        elif not forward_edge: #(v, w) is not a forward edge - whether w on stack or not...
          sc.append(croot[w])
      else:
        if lowlink[v] == v:
          sccs[v] = set()
          is_self_loop = s[-1] != v or v in succ[v]
          while True:
            w = s.pop()
            sccs[v].add(w)
            if w == v: break
          reach[v] = set(sccs[v]) if is_self_loop else set()
          if not subg is None and len(subg) == len(sccs[v]): return index
          for x in sccs[v]: croot[x] = v
          l = set()
          while len(sc) != stackheight[v]:
            x = sc.pop()
            l.add(x)
            for x in sorted(l, reverse=True, key=lambda y: indexes[y]):
              if not x in reach[v]:
                reach[v] |= reach[x]; reach[v] |= sccs[x]
    return index
  for v in succ:
    if (subg is None or v in subg) and not v in indexes:
      index = nuutila(v, index)
  return sccs, reach #keys are SCCs, values are reachable vertices

def init_reach_scc():
  return graph.DisjointSet(), {}, {}
def add_node_reach_scc(n, djs_scc, sccs, reach):
  djs_scc.makeSet(n)
  reach[n] = set()
  sccs[n] = {n}
  #if not virtual_root is None:
  #  rootscc = djs_scc.find(virtual_root)
  #  reach[rootscc].add(n)
def remove_node_reach_scc(n, djs_scc, sccs, reach):
  djs_scc.delSet(n)
  del reach[n]
  del sccs[n]
  #if not virtual_root is None:
  #  rootscc = djs_scc.find(virtual_root)
  #  reach[rootscc].remove(n)
def do_inc_reach_scc(x, y, pred, djs_scc, sccs, reach):
  if x == y:
    if x in sccs: reach[x].add(y)
    return #record addition of self-loop
  xcomp, ycomp = djs_scc.find(x), djs_scc.find(y)
  if xcomp == ycomp: return #adding inner component edges has no effect
  visited, r = set(), {ycomp}; r |= reach[ycomp]
  r -= reach[xcomp]
  if xcomp in r: r.remove(xcomp)
  if xcomp in reach[ycomp]: #collapse components
    reach[ycomp].add(ycomp); reach[xcomp] |= reach[ycomp]
    for comp in reach[ycomp]:
      if not comp in sccs or comp == xcomp or not xcomp in reach[comp]: continue
      djs_scc.union(xcomp, comp, True)
      sccs[xcomp] |= sccs[comp]
      del sccs[comp]; del reach[comp]
    allpreds = {djs_scc.find(z) for w in sccs[xcomp] for z in pred[w] if z not in sccs[xcomp]}
  else: allpreds = {xcomp}
  while len(allpreds) != 0:
    v = allpreds.pop()
    visited.add(v)
    if ycomp in reach[v]: continue #or r.issubset(reach[v])
    reach[v] |= r
    for z in (djs_scc.find(z) for w in sccs[v] for z in pred[w] if z not in sccs[v]):
      if not z in visited: allpreds.add(z)
def do_dec_reach_scc(x, y, pred, succ, djs_scc, sccs, reach):
  if x == y:
    if x in sccs and len(sccs[x]) == 1: reach[x].remove(y)
    return #record removal of self-loop
  xcomp, ycomp = djs_scc.find(x), djs_scc.find(y)
  if xcomp == ycomp: #subgraph SCC
    def check_reach(v):
      visited, stack = set(), {v} #stack = [(v, iter(succ[v]))]        
      while len(stack) != 0:
        v = stack.pop()
        if v == x: return True
        for w in pred[v]:
          if w != v and not w in visited and w in sccs[xcomp]: stack.add(w); visited.add(w) #stack.append((v, succv)); stack.append((w, iter(succ[w]))); break
      return False
    if check_reach(y): return
    #subscc, subreach = nuutila_reach_scc({z: succ[z].intersection(oldscc) for z in oldscc})
    subscc, subreach = nuutila_reach_scc(succ, sccs[xcomp])
    #subscc = {next(iter(v)):set(v) for v in tarjan_scc(succ, oldscc)}
    #if len(subscc) == 1: return
    djs_scc.unmerge(sccs[xcomp])
    rs = reach[xcomp] - sccs[xcomp]
    reachset = set()
    for z in rs:
      if z in sccs: reachset.add(z)
    del sccs[xcomp]; del reach[xcomp]
    #subreach = {next(iter(v)): reach_sccs[v] for v in reach_sccs}
    allpreds = set()
    #rebuild sub-components
    for v in subscc:
      reachset.add(v); allpreds.add(v)
      sccs[v] = subscc[v]
      for w in subscc[v]:
        if w != v: djs_scc.union(v, w, True)
      #for w in subscc[v]:
      #  if v != w: djs_scc.union(v, w, True)
      reach[v] = rs | subreach[v]
    #reachset = {djs_scc.find(z) for z in reachset}
  else: #rebuild reachability information from component successors
    allpreds = {xcomp}
    reachset = {ycomp}
    for z in reach[ycomp]:
      if z in sccs: reachset.add(z)
  reachFrom = {}
  visited = set()
  while len(allpreds) != 0:
    v = allpreds.pop()
    visited.add(v)
    for z in (djs_scc.find(z) for w in sccs[v] for z in pred[w] if z not in sccs[v]):
      if not z in visited: allpreds.add(z)
  for r in reachset:
    if r in reachFrom: continue
    reachFrom[r] = set()
    stack = [(r, z) for z in {djs_scc.find(z) for u in sccs[r] for z in pred[u]}]
    while len(stack) != 0:
      r, v = stack.pop()
      if not v in reachFrom: stack.append((r, v)); reachFrom[v] = set(); stack.extend([(v, z) for z in {djs_scc.find(z) for u in sccs[v] for z in pred[u]}]); continue
      if v in reachFrom[r]: continue
      if v in visited: reachFrom[r].add(v)
      if v in reachFrom: reachFrom[r] |= reachFrom[v]; continue
      for w in {djs_scc.find(z) for u in sccs[v] for z in pred[u]}:
        if not w in reachFrom[r]: stack.append((r, w))
  #if {z:reachFrom[z].intersection(visited) for z in reachFrom}: raise ValueError(pred, reachFrom, reachOther, visited, reachset, sccs)
  #visited = set()
  #reachFrom = {z:reachFrom[z].intersection(visited) for z in reachFrom}
  for v in visited:
  #while len(allpreds) != 0:
    #v = allpreds.pop()
    #r = [reach[w] | {w} for w in {djs_scc.find(z) for u in sccs[v] for z in succ[u]} if w != v]
    #reach[v] -= (reachset - (set() if len(r) == 0 else set.union(*r)))
    #r = [reach[w] | sccs[w] for w in {djs_scc.find(z) for u in sccs[v] for z in succ[u]} if w != v]
    #reach[v] = (set() if len(r) == 0 else set.union(*r)) | (sccs[v] if len(sccs[v]) != 1 or v in succ[v] else set())
    for z in reachset: #reach[v].intersection(reachset)
      if z in reach[v] and not v in reachFrom[z]: reach[v] -= sccs[z]
    #visited.add(v)
    #allpreds |= {djs_scc.find(z) for w in sccs[v] for z in pred[w] if z not in sccs[v] and not z in visited}
def do_inc_batch_reach_scc(edges, pred, succ, djs_scc, sccs, reach, fullrebuild=True):
  edgescomp, edgesprop = set(), set()
  for x, y in edges:
    if x == y:
      if x in sccs: reach[x].add(y)
      continue
    xcomp, ycomp = djs_scc.find(x), djs_scc.find(y)
    if xcomp == ycomp: continue
    if xcomp in reach[ycomp]:
      edgescomp.add((xcomp, ycomp))
    else:
      edgesprop.add((xcomp, ycomp))
  if len(edgescomp) + len(edgesprop) == 1:
    x, y = next(iter(edgescomp)) if len(edgescomp) == 1 else next(iter(edgesprop))
    do_inc_reach_scc(x, y, pred, djs_scc, sccs, reach)
    return
  reachset = set()
  #print(edgescomp, edgesprop)
  for x, y in edgescomp:
    xcomp = djs_scc.find(x) if not x in sccs else x
    ycomp = djs_scc.find(y) if not y in sccs else y
    if xcomp == ycomp: continue
    reachset.add(xcomp)
    reach[ycomp].add(ycomp); reach[xcomp] |= reach[ycomp]
    for comp in reach[ycomp]:
      if not comp in sccs or comp == xcomp or not xcomp in reach[comp]: continue
      if comp in reachset: reachset.remove(comp)
      djs_scc.union(xcomp, comp, True)
      sccs[xcomp] |= sccs[comp]
      if comp != ycomp: reach[xcomp] |= reach[comp]
      del sccs[comp]; del reach[comp]
  #if len(edgesprop) == 1:
  #  x, y = next(iter(edgesprop))
  #  xcomp = djs_scc.find(x); ycomp = djs_scc.find(y)
  #  reachset.add(xcomp); reachset.add(ycomp)
  if len(edgesprop) != 0:
    if not fullrebuild:
      subgnodes = set()
      for x, y in edgesprop:
        xcomp = djs_scc.find(x); ycomp = djs_scc.find(y)
        subgnodes.add(xcomp); subgnodes.add(ycomp)
        subgnodes |= reach[xcomp]; subgnodes |= reach[ycomp]
      subgnodes |= reachset
      subscc, subreach = nuutila_reach_scc({z: {djs_scc.find(w) for v in sccs[z] for w in succ[v] if w in subgnodes} for z in subgnodes if z in sccs})
      #print(edgesprop, edgescomp, subscc, subreach, succ)
    else: subscc, subreach = nuutila_reach_scc({z: {djs_scc.find(w) for v in sccs[z] for w in succ[v]} for z in sccs})
    #print(subscc, subreach)
    for v in reversed(subscc):
      reachset.add(v)
      for z in subreach[v]:
        if z in sccs: reach[v] |= sccs[z]; reach[v] |= reach[z]
      reach[v] |= subreach[v]
      if len(subscc[v]) == 1: continue
      for w in subscc[v]:
        if w == v: continue
        if w in reachset: reachset.remove(w)
        djs_scc.union(v, w, True)
        sccs[v] |= sccs[w]
        del sccs[w]; del reach[w]
    if fullrebuild: return
  reachFrom = {}
  allpreds = {djs_scc.find(z) for xcomp in reachset for w in sccs[xcomp] for z in pred[w] if z not in sccs[xcomp]}
  visited = set()
  while len(allpreds) != 0:
    v = allpreds.pop()
    visited.add(v)
    for z in (djs_scc.find(z) for w in sccs[v] for z in pred[w] if z not in sccs[v]):
      if not z in visited: allpreds.add(z)
  for r in reachset:
    if r in reachFrom: continue
    reachFrom[r] = set()
    stack = [(r, z) for z in {djs_scc.find(z) for u in sccs[r] for z in pred[u]}]
    while len(stack) != 0:
      r, v = stack.pop()
      if not v in reachFrom: stack.append((r, v)); reachFrom[v] = set(); stack.extend([(v, z) for z in {djs_scc.find(z) for u in sccs[v] for z in pred[u]}]); continue
      if v in reachFrom[r]: continue
      if v in visited: reachFrom[r].add(v)
      if v in reachFrom: reachFrom[r] |= reachFrom[v]; continue
      for w in {djs_scc.find(z) for u in sccs[v] for z in pred[u]}:
        if not w in reachFrom[r]: stack.append((r, w))
  #print(edgescomp, edgesprop, visited, reachset, reachFrom)
  for v in visited:
    for z in reachset:
      if v in reachFrom[z]: reach[v] |= sccs[z]
def do_dec_batch_reach_scc(edges, pred, succ, djs_scc, sccs, reach):
  allpreds, reachset, rebuild = set(), set(), {}
  for x, y in edges:
    if x == y:
      if x in sccs and len(sccs[x]) == 1: reach[x].remove(y)
      continue
    xcomp, ycomp = djs_scc.find(x), djs_scc.find(y)
    if xcomp == ycomp:
      if not xcomp in rebuild: rebuild[xcomp] = set()
      rebuild[xcomp].add((x, y))
    else: allpreds.add(xcomp); reachset |= reach[ycomp]; reachset.add(ycomp)
  if len(rebuild) != 0:
    def check_reach(v, target, xcomp):
      visited, stack = set(), {v} #stack = [(v, iter(succ[v]))]        
      while len(stack) != 0:
        v = stack.pop()
        if v == target: return True
        for w in pred[v]:
          if w != v and not w in visited and w in sccs[xcomp]: stack.add(w); visited.add(w) #stack.append((v, succv)); stack.append((w, iter(succ[w]))); break
      return False
    oldscc, rs = set(), {}
    for z in rebuild:
      #if ((len(sccs[z]) * len(sccs[z])) >> 1) < len(rebuild[z]) and all(check_reach(ys, xs, z) for xs, ys in rebuild[z]): continue
      oldscc |= sccs[z]
      reachset |= reach[z]; reachset.add(z)
      r = reach[z] - sccs[z]
      for v in sccs[z]: rs[v] = r
      djs_scc.unmerge(sccs[z])
      del sccs[z]; del reach[z]
    allpreds -= oldscc
    subscc, subreach = nuutila_reach_scc(succ, oldscc)
    for v in subscc:
      allpreds.add(v)
      sccs[v] = subscc[v]
      for w in subscc[v]:
        if w != v: djs_scc.union(v, w, True)
      reach[v] = rs[v] | subreach[v]
  reachFrom = {}
  reachset = {z for z in reachset if z in sccs}
  visited = set()
  while len(allpreds) != 0:
    v = allpreds.pop()
    visited.add(v)
    for z in (djs_scc.find(z) for w in sccs[v] for z in pred[w] if z not in sccs[v]):
      if not z in visited: allpreds.add(z)
  for r in reachset:
    if r in reachFrom: continue
    reachFrom[r] = set()
    stack = [(r, z) for z in {djs_scc.find(z) for u in sccs[r] for z in pred[u]}]
    while len(stack) != 0:
      r, v = stack.pop()
      if not v in reachFrom: stack.append((r, v)); reachFrom[v] = set(); stack.extend([(v, z) for z in {djs_scc.find(z) for u in sccs[v] for z in pred[u]}]); continue
      if v in reachFrom[r]: continue
      if v in visited: reachFrom[r].add(v)
      if v in reachFrom: reachFrom[r] |= reachFrom[v]; continue
      for w in {djs_scc.find(z) for u in sccs[v] for z in pred[u]}:
        if not w in reachFrom[r]: stack.append((r, w))
  for v in visited:
    for z in reach[v].intersection(reachset):
      if not v in reachFrom[z]: reach[v] -= sccs[z]
#Strong bridge detector much better than this
"""
def does_root_reach_without(virtual_root, succ, root_succ, x, y):
  visit, visited = {virtual_root}, set()
  while len(visit) != 0:
    v = visit.pop()
    if v == y: return True
    visited.add(v)
    for w in succ[v] if v != virtual_root else root_succ:
      if v == x and w == y: continue
      if not w in visited: visit.add(w)
  return False
"""

def verify_reach_sccs(sccs, reach, nsccs, nreach):
  first = {frozenset(y): reach[x] for x, y in sccs.items() if x != 0}
  second = {frozenset(y): nreach[x] for x, y in nsccs.items() if x != 0}
  return first == second
  
def check_scc(succ, djs_scc, sccs, reach):
  #if floyd_warshall_reachability(succ) != {x: reach[djs_scc.find(x)] for x in succ}:
    #raise ValueError(floyd_warshall_reachability(succ), reach)
  nsccs, nreach = nuutila_reach_scc(succ)
  #tscc = tarjan_scc(succ)
  #if {frozenset(sccs[x]) for x in sccs} != {frozenset(x) for x in tscc}:
  #  raise ValueError(sccs, tscc)
  #dfsreach = dfs_reachability(succ)
  #if dfsreach != {x: reach[djs_scc.find(x)] for x in succ}:
  #  raise ValueError(dfsreach, reach)
  verify_reach_sccs(sccs, reach, nsccs, nreach)

def do_graphviz_dot_text_scc_reach(succ, djs_scc, sccs, reach):
  t = ";".join("r" + str(x) + "->r" + str(djs_scc.find(z)) for x in sccs for y in sccs[x] for z in succ[y] if djs_scc.find(x) != djs_scc.find(z))
  r = ";".join("r" + str(x) + " [label=" + "\"" + str(x) + " [" + str(sccs[x]) + ", " + ("{}" if len(reach[x]) == 0 else str(reach[x])) + "]\"" + "]" for x in sccs)
  return t + ";" + r
def do_graphviz_dot_text_scc_reach_comp(x, y, succ, djs_scc, sccs):
  xcomp = djs_scc.find(x) 
  oldscc = sccs[xcomp]
  subg = {z: succ[z].intersection(oldscc) for z in oldscc}
  subg[x].remove(y)
  subscc, subreach = nuutila_reach_scc(subg)
  djs_scc = graph.DisjointSet(oldscc)
  for x in subscc:
    for y in subscc[x] - {x}:
      djs_scc.union(x, y, True)
  return do_graphviz_dot_text_scc_reach(subg, djs_scc, subscc, subreach)

def paper_inc_dec_scc(output_dir):
  import os
  root, init = 1, [[2, 3, 5], [7], [4], [3, 7, 9], [6, 10], [7], [5, 6, 8], [], [], []]
  new_edge = (5, 3)
  succ, pred = {}, {}
  djs_scc, sccs, reach = init_reach_scc()
  for x, s in enumerate(init):
    if not x+1 in succ:
      succ[x+1] = set(); pred[x+1] = set()
      add_node_reach_scc(x+1, djs_scc, sccs, reach)
    for y in s:
      if not y in pred:
        succ[y] = set(); pred[y] = set()
        add_node_reach_scc(y, djs_scc, sccs, reach)
      succ[x+1].add(y); pred[y].add(x+1)
      do_inc_reach_scc(x+1, y, pred, djs_scc, sccs, reach)
  output = "A digraph and its corresponding SCC DAG with its SCCs and reachability shown:\n"
  output += graph.make_graphviz_dot_text(succ, do_graphviz_dot_text_scc_reach(succ, djs_scc, sccs, reach)) + "\n"
  succ[new_edge[0]].add(new_edge[1]); pred[new_edge[1]].add(new_edge[0])
  do_inc_reach_scc(new_edge[0], new_edge[1], pred, djs_scc, sccs, reach)
  output += "\nThe digraph with edge (%d, %d) added:\n" % new_edge
  output += graph.make_graphviz_dot_text(succ, do_graphviz_dot_text_scc_reach(succ, djs_scc, sccs, reach)) + "\n"
  output += "\nThe sub-graph and its corresponding SCC DAG with its SCC and reachability when edge (%d, %d) is removed:\n" % new_edge
  output += graph.make_graphviz_dot_text(succ, do_graphviz_dot_text_scc_reach_comp(new_edge[0], new_edge[1], succ, djs_scc, sccs)) + "\n"
  succ[new_edge[0]].remove(new_edge[1]); pred[new_edge[1]].remove(new_edge[0])
  do_dec_reach_scc(new_edge[0], new_edge[1], pred, succ, djs_scc, sccs, reach)
  #graph.do_graphviz_dot(make_graphviz_dot_text(succ, do_graphviz_dot_text_scc_reach(succ, djs_scc, sccs, reach)), output_dir)
  with open(os.path.join(output_dir, 'scc_graph_dot.txt'), "w") as f:
    f.write(output)

def adapt_nuutila(data, ndata):
  djs_scc, sccs, reach = data; nsccs, nreach = ndata
  return djs_scc, {djs_scc.find(x): y for x, y in nsccs.items()}, {djs_scc.find(x): y for x, y in nreach.items()}
def verify_dyn_scc_reach(connected=True):
  iterations, nodes = 100, 10
  graph.verification_algo_test(iterations, lambda: graph.random_digraph(nodes, connected), [lambda root: init_reach_scc()],
    [lambda n, data: add_node_reach_scc(n, data[0], data[1], data[2])],
    [lambda n, data: remove_node_reach_scc(n, data[0], data[1], data[2])],
    [lambda x, y, root, succ, pred, data, _: do_inc_reach_scc(x, y, pred, data[0], data[1], data[2])],
    [lambda x, y, root, succ, pred, data, _: do_dec_reach_scc(x, y, pred, succ, data[0], data[1], data[2])],
    [lambda x, y, root, succ, pred, graph_data: adapt_nuutila(graph_data[0], nuutila_reach_scc(succ))],
    batches=5,
    batch_init_funcs=[lambda root: init_reach_scc()],
    batch_add_node_funcs=[lambda n, data: add_node_reach_scc(n, data[0], data[1], data[2])],
    batch_remove_node_funcs=[lambda n, data: remove_node_reach_scc(n, data[0], data[1], data[2])],
    batch_add_funcs=[lambda batch, root, succ, pred, data: do_inc_batch_reach_scc(batch, pred, succ, data[0], data[1], data[2], True)],
    batch_remove_funcs=[lambda batch, root, succ, pred, data: do_dec_batch_reach_scc(batch, pred, succ, data[0], data[1], data[2])],
    comparer=lambda x, y: verify_reach_sccs(x[1], x[2], y[1], y[2]))
def timing_dyn_scc_reach(cfg_dir, output_dir):
  import os
  repeat = 1
  output = ""
  for experiment, rng in enumerate([lambda: range(10, 210, 10), lambda: range(50, 1050, 50), lambda: graph.get_real_cfgs(cfg_dir)]):
    rng = rng()
    output += ("Experiment %d\n" % experiment)
    #"Random Connected Graph Edge Addition and Deletion Performance Execution Time Averaged Over 10 Runs"
    #"Random Fixed Locality=5 and Average Out-Degree=5 Connected Graph Edge Addition and Deletion Execution Time Averaged Over 10 Runs"
    #"Real Control Flow Graph Edge Addition and Edge Deletion Execution Time"
    iterations = 1 if experiment == 2 else 10
    results = {}
    for c in rng:
      if experiment == 0:
        edge_gen = lambda: graph.random_digraph(c)
      elif experiment == 1:
        edge_gen = lambda: graph.random_local_digraph(c, 5, 5)
      elif experiment == 2:
        edge_gen = lambda: c
      results[c] = graph.timing_test(iterations, edge_gen, repeat, [lambda root: init_reach_scc()],
        [lambda n, data: add_node_reach_scc(n, data[0], data[1], data[2])],
        [lambda n, data: remove_node_reach_scc(n, data[0], data[1], data[2])],
        [lambda x, y, root, succ, pred, data: do_inc_reach_scc(x, y, pred, data[0], data[1], data[2])],
        [lambda x, y, root, succ, pred, data: do_dec_reach_scc(x, y, pred, succ, data[0], data[1], data[2])],
        [lambda x, y, root, succ, pred, graph_data: nuutila_reach_scc(succ)],
        batches=5,
        batch_init_funcs=[lambda root: init_reach_scc()],
        batch_add_node_funcs=[lambda n, data: add_node_reach_scc(n, data[0], data[1], data[2])],
        batch_remove_node_funcs=[lambda n, data: remove_node_reach_scc(n, data[0], data[1], data[2])],
        batch_add_funcs=[lambda batch, root, succ, pred, data: do_inc_batch_reach_scc(batch, pred, succ, data[0], data[1], data[2], True)],
        batch_remove_funcs=[lambda batch, root, succ, pred, data: do_dec_batch_reach_scc(batch, pred, succ, data[0], data[1], data[2])],
        maintain_conn=False)
      print(results[c])
    for x in sorted(results):
      output += ("%d %s %s %s %s %s %s %s\n" % (x, *(repr(z[0] / (iterations * repeat)) for z in results[x])))
  with open(os.path.join(output_dir, 'scc_paper.txt'), "w") as f:
    f.write(output)

def paper_tarjan_scc():
  #http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.327.8418&rep=rep1&type=pdf
  #DEPTH-FIRST SEARCH AND LINEAR GRAPH ALGORITHMS
  #ROBERT TARJAN
  correct = [[6], [7, 5, 4, 3], [8, 2, 1]]
  gsucc = {1: [2], 2: [3, 8], 3: [4, 7], 4: [5], 5: [3, 6], 6: [], 7: [4, 6], 8: [1, 7]}
  correctdfsparents = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 3, 8: 2}
  #checking component roots and low links would require expanding the algorithm for returning such details
  #correctlowlinks = {1: 1, 2: 1, 3: 3, 4: 3, 5: 3, 6: 6, 7: 4, 8: 1}
  #componentroots = {3, 6}
  assert dfs.dfs_interval(gsucc, 1)[2] == correctdfsparents
  assert tarjan_scc(gsucc) == correct
def paper_nuutila_scc_reach():
  #All Esko Nuutila transitive closure papers: http://www.cs.hut.fi/~enu/tc.html
  #https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.40.9019&rep=rep1&type=pdf
  #On Finding the Strongly Connected Components in a Directed Graph
  #by Esko Nuutila and Eljas Soisalon-Soininen
  #http://www.cs.hut.fi/~enu/thesis.pdf
  #Efficient Transitive Closure Computation in Large Digraphs
  #dissertation of Esko Nuutila
  #http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.42.5639&rep=rep1&type=pdf
  #An efficient transitive closure algorithm for cyclic digraphs
  #Esko Nuutila
  pass #dissertation contains several examples
def test_fully_online_reach_scc():
  g = cfg.Digraph([1], [[2], [3, 8], [4, 7], [5], [3, 6], [], [4, 6], [1, 7]])
  nsccs, nreach = nuutila_reach_scc(g.succ)
  assert verify_reach_sccs(g.sccs, g.reach, nsccs, nreach)