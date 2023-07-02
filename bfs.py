import queue
import graph
import dfs
import itertools

def is_lex_bfs(bfs_int, bfs_revint, pred, not_lex=False):
  #lex = []
  #for i in bfs_revint:
  #  lex.append(list(sorted([bfs_int[y] for y in pred[bfs_revint[i]] if y in bfs_int])))
  #print(lex)
  #for i in range(1, len(lex)-1):
    #print(lex[i], lex[i+1], lex[i] <= lex[i+1])
  #  assert lex[i] <= lex[i+1], ([bfs_revint[x] for x in bfs_revint], bfs_revint, pred)
  #return lex
  for ia in range(len(bfs_revint)-1, 0, -1):
    a = bfs_revint[ia]
    for c in pred[a]:
      if not c in bfs_int: continue
      ic = bfs_int[c]
      if ic > ia: continue
      for ib in range(ic+1, ia):
        b = bfs_revint[ib]
        if c in pred[b]: continue
        if any(bfs_int[d] < ic and (not_lex or not d in pred[a]) for d in pred[b] if d in bfs_int): continue #d == m, c == i, b = j, a = k
        print(c, b, a)
        return False
  return True
def do_lex_bfs(virtual_root, succ, pred, test_order=None):
  eT = graph.Tree(virtual_root, use_depth=True)
  bfs_int, bfs_revint, bfs_level = {}, {}, [1]
  parts, t, reachable = graph.PartitionRefinement(succ.keys()), 1, {virtual_root}
  parts.split(virtual_root)
  while True: #not parts.isEmpty():
    x = parts.pop()
    bfs_int[x] = t
    bfs_revint[t] = x
    if x != virtual_root and bfs_revint[t-1] != virtual_root and eT.level[x] != eT.level[bfs_revint[t-1]]: bfs_level.append(t-1)
    t += 1
    priors = {}
    for y in succ[x]:
      if x == y: continue
      reachable.add(y)
      s = parts.find(y)
      if not s is None:
        if not y in eT.pred: eT.add_node(y); eT.add_edge(x, y)
        if s in priors:
          parts.move(y, priors[s])
        else:
          priors[s] = parts.split(y)
    x = parts.next(None)
    if x is None or not x in reachable: break
  assert is_lex_bfs(bfs_int, bfs_revint, pred)
  return eT, bfs_int, bfs_revint, bfs_level
def do_lex_bfs_opt(virtual_root, succ, pred, test_order=None):
  eT = graph.Tree(virtual_root, use_depth=True)
  bfs_int, bfs_revint, bfs_level = {}, {}, [1]
  parts, t, reachable = graph.PartitionRefinement(succ.keys()), 1, {virtual_root}
  parts.split(virtual_root)
  x = None
  while True: #not parts.isEmpty():
    #check = parts.seq.headval.dataval.intersection(reachable)
    #if len(check) > 1:
    #  _, exitdisc, _ = dfs.dfs_interval({x: check.intersection(succ[x]) for x in check}, next(iter(check)))
    #  print(check, exitdisc)
    #  x = parts.pop(exitdisc, pred)
    #else:
    #x = parts.pop(test_order)
    x = parts.next(x)
    if x is None: break
    if not x in reachable:
      while not x is None:
        y = parts.next(x)
        parts.remove(x)
        x = y
      break
    bfs_int[x] = t
    bfs_revint[t] = x
    if x != virtual_root and bfs_revint[t-1] != virtual_root and eT.level[x] != eT.level[bfs_revint[t-1]]: bfs_level.append(t-1)
    t += 1
    priors = {}
    for y in succ[x]:
      if x == y or y in eT.pred and (eT.level[y] < eT.level[x] or eT.level[x] == eT.level[y] and (y in bfs_int or (eT.pred[y] == eT.pred[x] and x in parts.find(y).dataval))): continue
      reachable.add(y)
      s = parts.find(y)
      if not s is None:
        if not y in eT.pred: eT.add_node(y); eT.add_edge(x, y)
        if s in priors:
          parts.move(y, priors[s])
        else:
          priors[s] = parts.split(y)
    if not parts.isIsolatedItem(x):
      presplit = {z for z in s.dataval if z != x and z in bfs_int}
      decide = {z for z in presplit if z in succ[x]}
      #mustsucc = {z for z in succ[x] if not z in bfs_int and not z in s.dataval and eT.pred[z] == eT.pred[x]}
      
      postsplit = {z for z in s.dataval if z != x and not z in bfs_int}
      postdecide = {z for z in postsplit if not z in succ[x]}
      #splitx = {z for z in s.dataval if z != x and not x in succ[z]}
      print(x, presplit, decide, s.dataval, postsplit, postdecide) #, mustsucc)
      if len(decide) != 0 and len(decide) != len(presplit) or len(decide) == 0 and len(presplit) != 0 and (len(postsplit) != len(postdecide)):
        v = presplit.pop()
        parts.split(v); newset = parts.find(v)
        for z in presplit: parts.remove(z); parts.add(z, newset)
        decide = set()
      #print(splitx)
      #if len(splitx) > 1: parts.split(x)
      #postsplit = {z for z in s.dataval if z != x and not z in bfs_int and not z in succ[x]}
      #print(postsplit, s.dataval)
      if len(postdecide) != 0 and (len(decide) != 0 or len(postdecide) != len(postsplit)):
        postdecide = s.dataval - postdecide
        v = postdecide.pop()
        parts.split(v); newset = parts.find(v)
        for z in postdecide: parts.remove(z); parts.add(z, newset)
  if len(bfs_revint) != 1: bfs_level.append(len(bfs_revint))
  #print(tuple((x, y) for x in succ for y in succ[x]))
  #print(parts, bfs_revint)
  if not is_lex_bfs(bfs_int, bfs_revint, pred):
    print_bfst_part(None, None, eT.virtual_root, succ, eT, bfs_int, parts, eT, bfs_int, parts, [eT, bfs_int, parts], "")
  assert(is_lex_bfs(bfs_int, bfs_revint, pred))
  assert parts.isIsolatedItem(virtual_root)
  #naive permutation method is best to stabilize
  for i in range(1, len(bfs_revint)+1):  
    remaining = list(sorted(bfs_int[z] for z in eT.succ[bfs_revint[i]]))
    #print(loc.nextval.dataval, eT.succ[bfs_revint[i]], bfs_revint[i])
    while len(remaining) > 1:
      predcrit = set(filter(lambda q: q in bfs_int and bfs_int[q] < remaining[0], pred[bfs_revint[remaining[0]]]))
      curgroup = [remaining[0]] + list(itertools.takewhile(lambda z: set(filter(lambda q: q in bfs_int and bfs_int[q] < remaining[0], pred[bfs_revint[z]])) == predcrit, remaining[1:]))
      #print(loc.nextval.dataval, curgroup)
      while len(curgroup) > 1:
        for j in range(2, len(curgroup)+1):
          for comb in itertools.permutations(curgroup[:j]):
            c = [bfs_revint[z] for z in comb] + [bfs_revint[z] for z in curgroup[j:]]
            #print(c)
            if any(list(sorted(c.index(q) for q in pred[z] if q in c[:idx])) > list(sorted(c.index(q) for q in pred[c[idx]] if q in c[:idx])) for idx, z in enumerate(c[1:])):
              break
            checksucc = list(sorted({z for z in set.union(*(succ[c[idx]] for idx, z in enumerate(c))) if not z in c and bfs_int[z] > remaining[0]}, key=lambda z: bfs_int[z]))
            if any(list(sorted(c.index(q) for q in pred[z] if q in c)) > list(sorted(c.index(q) for q in pred[checksucc[idx]] if q in c)) for idx, z in enumerate(checksucc[1:])):
              break
          else: continue
          if len(loc.nextval.dataval) != j - 1:
            print_bfst_part(None, None, eT.virtual_root, succ, eT, bfs_int, parts, eT, bfs_int, parts, [eT, bfs_int, parts], "")
            assert False, (loc.nextval.dataval, curgroup, remaining, j)
          loc = loc.nextval
          remaining = remaining[j-1:]
          #curgroup = curgroup[j-1:]
          predcrit = set(filter(lambda q: q in bfs_int and bfs_int[q] < remaining[0], pred[bfs_revint[remaining[0]]]))
          curgroup = [remaining[0]] + list(itertools.takewhile(lambda z: set(filter(lambda q: q in bfs_int and bfs_int[q] < remaining[0], pred[bfs_revint[z]])) == predcrit, remaining[1:]))
          break
        else:
          if len(loc.nextval.dataval) != len(curgroup):
            print_bfst_part(None, None, eT.virtual_root, succ, eT, bfs_int, parts, eT, bfs_int, parts, [eT, bfs_int, parts], "")
            assert False, (loc.nextval.dataval, curgroup, remaining, len(curgroup))
          loc = loc.nextval
          break
      if len(curgroup) == 1:
        assert len(loc.nextval.dataval) == 1
        loc = loc.nextval      
      remaining = remaining[len(curgroup):]
    if len(remaining) == 1:
      assert len(loc.nextval.dataval) == 1
      loc = loc.nextval
  """
    if not bfs_revint[i] in loc.dataval:
      #any splits must be justified by difference in predecessors or a forward edge which has an order contingent dependency - should have been merged condition
      x0, x1 = next(iter(loc.dataval)), next(iter(loc.nextval.dataval))      
      if frozenset(y for y in pred[x0] if y in bfs_int and bfs_int[y] < bfs_int[x0] and not y in loc.dataval) == frozenset(y for y in pred[x1] if y in bfs_int and bfs_int[y] < bfs_int[x1] and not y in loc.nextval.dataval) and eT.pred[x0] == eT.pred[x1]:
        comb = loc.dataval | loc.nextval.dataval
        for x in comb:
          sibs = frozenset(y for y in comb if x != y and y in succ[x])
          if len(sibs) != 0 and len(sibs) != len(comb) - 1: break
        else:
          print_bfst_part(None, None, eT.virtual_root, succ, eT, bfs_int, parts, eT, bfs_int, parts, [eT, bfs_int, parts], "")
          assert False, (loc.dataval, loc.nextval.dataval, parts)
      loc = loc.nextval
      assert len(set(frozenset(y for y in pred[x] if y in bfs_int and bfs_int[y] < bfs_int[x] and not y in loc.dataval) for x in loc.dataval)) == 1, set(frozenset(y for y in pred[x] if y in bfs_int and bfs_int[y] < bfs_int[x] and not y in loc.dataval) for x in loc.dataval)
      if not bfs_revint[i] in loc.dataval: print_bfst_part(None, None, eT.virtual_root, succ, eT, bfs_int, parts, eT, bfs_int, parts, [eT, bfs_int, parts], "")
      assert bfs_revint[i] in loc.dataval, (bfs_revint[i], loc.dataval, parts)
      #any groups must not have inter group edges that would cause ordering required - need split condition
      for x in loc.dataval:
        sibs = frozenset(y for y in loc.dataval if x != y and y in succ[x])
        if not (len(sibs) == 0 or len(sibs) == len(loc.dataval) - 1): print_bfst_part(None, None, eT.virtual_root, succ, eT, bfs_int, parts, eT, bfs_int, parts, [eT, bfs_int, parts], "")
        assert len(sibs) == 0 or len(sibs) == len(loc.dataval) - 1, (sibs, parts)
  """
  #print(succ, bfs_int, bfs_revint, is_lex_bfs(bfs_int, bfs_revint, pred))
  return eT, bfs_int, bfs_revint, bfs_level, parts
def do_bfs(source, succ, test_order=None, test_order_ranked=False): #similar to DFS but no forward edges, and back-cross edges have maximum depth of 1
  eT = graph.Tree(source, use_depth=True)
  bfs_int, bfs_revint, bfs_level = {}, {}, [1]
  thisLevel, t, visited = {source}, 1, {source}
  while True:
    nextLevel = []
    for x in thisLevel:
      bfs_int[x] = t
      bfs_revint[t] = x
      t += 1
      for y in succ[x] if test_order is None else sorted(succ[x], key=lambda y: test_order[y]):
        if not y in visited:
          eT.add_node(y); eT.add_edge(x, y)
          visited.add(y)
          nextLevel.append(y)
    if len(nextLevel) != 0: bfs_level.append(len(nextLevel) + bfs_level[-1])
    thisLevel = nextLevel if not test_order_ranked else sorted(nextLevel, key=lambda y: test_order[y])
    if len(thisLevel) == 0: break
  assert test_order_ranked or is_lex_bfs(bfs_int, bfs_revint, graph.succ_to_pred(succ), True) #semi-dynamic algorithm is not a BFS order
  return eT, bfs_int, bfs_revint, bfs_level
def init_bfs(source): return graph.Tree(source, use_depth=True), {source: 1}, {1: source}, [1]
def do_partial_bfs(y, succ, bfs_tree, bfs_int, bfs_revint, bfs_level, test_order=None):
  start=1 if y == bfs_tree.virtual_root else bfs_level[bfs_tree.level[y]-1]+1
  end = bfs_level[bfs_tree.level[y]]
  redepths = []
  thisLevel, t, visited = (bfs_revint[z] for z in range(start, end+1)), start, {bfs_revint[z] for z in range(1, end+1)}
  del bfs_level[bfs_tree.level[y]+1:]
  while True:
    nextLevel = []
    for x in thisLevel:
      bfs_int[x] = t
      bfs_revint[t] = x
      t += 1
      for y in succ[x] if test_order is None else sorted(succ[x], key=lambda y: test_order[y]):
        if not y in visited:
          if not y in bfs_tree.pred:
            bfs_tree.add_node(y)
            bfs_tree.add_edge(x, y)
          if bfs_tree.pred[y] != x:
            bfs_tree.remove_edge(bfs_tree.pred[y], y, delay_redepth=True); bfs_tree.add_edge(x, y, delay_redepth=True)
            redepths.append(y)
          visited.add(y)
          nextLevel.append(y)
    if len(nextLevel) != 0: bfs_level.append(len(nextLevel) + bfs_level[-1])
    thisLevel = nextLevel
    if len(thisLevel) == 0: break
  bfs_tree.redepthSubTrees(redepths)
def do_inc_add_edge_bfs_basic(succ, bfs_tree, bfs_int, bfs_revint, bfs_level, x, y, test_order=None):
  if not x in bfs_tree.level: return
  if not y in bfs_tree.level or bfs_tree.level[y] > bfs_tree.level[x] + 1 or bfs_tree.level[y] == bfs_tree.level[x] + 1 and bfs_int[bfs_tree.pred[y]] > bfs_int[x]:
    do_partial_bfs(x, succ, bfs_tree, bfs_int, bfs_revint, bfs_level, test_order)
def do_dec_remove_edge_bfs_basic(succ, bfs_tree, bfs_int, bfs_revint, bfs_level, x, y, test_order=None):
  if not x in bfs_tree.level or not y in bfs_tree.level: return
  if bfs_tree.pred[y] != x: return #only need to process deleted tree edges
  do_partial_bfs(x, succ, bfs_tree, bfs_int, bfs_revint, bfs_level, test_order)
  if bfs_tree.pred[y] == x: #remove unreachable subtree
    for z in reversed(bfs_tree.bfsSubTree(y)):
      bfs_tree.remove_edge(bfs_tree.pred[z], z)
      bfs_tree.remove_node(z)
      del bfs_int[z]
      del bfs_revint[len(bfs_revint)]
def semi_dynamic_init_bfs(root): return graph.Tree(root, use_depth=True), {root: graph.DLinkedList()}
def semi_dynamic_add_node_bfs(bfs_tree, backward_star, n, fullydyn=True):
  if not fullydyn: backward_star[n] = graph.DLinkedList()
def semi_dynamic_remove_node_bfs(bfs_tree, backward_star, n, fullydyn=True):
  if not fullydyn: del backward_star[n]
def propogate_bfs(edges, revedge, bfs_tree, succ):
  k = 0
  while k < len(edges):
    edge = edges[k].headval
    if edge is None: k += 1; continue
    a, b = edge.dataval
    edge = edge.nextval
    while not edge is edges[k].headval:
      a, b = min((a, b), edge.dataval)
      edge = edge.nextval
    for l, edge in revedge[b]: edges[l].remove_node(edge)
    newnode = not b in bfs_tree.pred
    if newnode: bfs_tree.add_node(b)
    else: bfs_tree.remove_edge(bfs_tree.pred[b], b, delay_redepth=True)
    bfs_tree.add_edge(a, b, delay_redepth=True)
    if newnode or bfs_tree.level[b] is None or bfs_tree.level[b] > bfs_tree.level[a] + 1:
      bfs_tree.level[b] = bfs_tree.level[a] + 1
      for c in succ[b]:
        if not c in bfs_tree.level or bfs_tree.level[c] is None or bfs_tree.level[c] > bfs_tree.level[b] + 1 or bfs_tree.level[c] == bfs_tree.level[b] + 1 and b < bfs_tree.pred[c]:
          while len(edges) <= bfs_tree.level[b]: edges.append(graph.DLinkedList())
          newedge = graph.DLinkedList.Node((b, c))
          edges[bfs_tree.level[b]].add_node(newedge)
          if not c in revedge: revedge[c] = []
          revedge[c].append((bfs_tree.level[b], newedge))
def semi_dynamic_add_edge_bfs(bfs_tree, succ, backward_star, x, y, fullydyn=True):
  if not fullydyn: backward_star[y].add_node_sorted(graph.DLinkedList.Node(x))
  if not x in bfs_tree.level: return
  newnode = not y in bfs_tree.level
  if not (newnode or bfs_tree.level[y] > bfs_tree.level[x] + 1 or bfs_tree.level[y] == bfs_tree.level[x] + 1 and bfs_tree.pred[y] > x): return
  edges = graph.DLinkedList()
  newedge = graph.DLinkedList.Node((x, y))
  edges.add_node(newedge)
  propogate_bfs([graph.DLinkedList()] * bfs_tree.level[x] + [edges], {y: [(bfs_tree.level[x], newedge)]}, bfs_tree, succ)
  #bfs_tree.checkTreeValid()
def semi_dynamic_remove_edge_bfs(bfs_tree, succ, backward_star, x, y, fullydyn=True):
  if not fullydyn:
    idx = backward_star[y].find_node(x); backward_star[y].remove_node(idx)
    idx = None if idx is idx.nextval or idx.nextval is backward_star[y].headval else idx.nextval
  if not x in bfs_tree.level or not y in bfs_tree.level: return
  if x == bfs_tree.pred[y]:
    #if not fullydyn:
    #  bfs_tree.remove_edge(bfs_tree.pred[y], y, delay_redepth=True)
    #  if not idx is None:
    #    bfs_tree.add_edge(idx.dataval, y, delay_redepth=True)
    notreach, unreachset = [], set()
    for b in bfs_tree.bfsSubTree(y):
      if not fullydyn:
        idx = backward_star[b].find_node(bfs_tree.pred[b]) if b != y else idx
        idx = None if idx is None or idx is idx.nextval or idx.nextval is backward_star[b].headval else idx
        samedepth = [a for a in backward_star[b].get_nodes_before(idx) if a in bfs_tree.level and not bfs_tree.level[a] is None and bfs_tree.level[a] + 1 == bfs_tree.level[b]] if not idx is None else []
      else:
        samedepth = [a for a in backward_star[b] if a in bfs_tree.level and not bfs_tree.level[a] is None and bfs_tree.level[a] + 1 == bfs_tree.level[b]]
      if len(samedepth) != 0:
        bfs_tree.remove_edge(bfs_tree.pred[b], b, delay_redepth=True)
        bfs_tree.add_edge(min(samedepth), b, delay_redepth=True)
      else: notreach.append(b); unreachset.add(b); bfs_tree.level[b] = None
    if len(notreach) != 0:
      edges, edgerev = [], {}
      for b in notreach:
        if not fullydyn: a = min((a for a in backward_star[b].get_nodes() if a in bfs_tree.level and not bfs_tree.level[a] is None), key=lambda z: bfs_tree.level[z], default=None)
        else: a = min((a for a in backward_star[b] if a in bfs_tree.level and not bfs_tree.level[a] is None), key=lambda z: (bfs_tree.level[z], z), default=None)
        if not a is None:
          while len(edges) <= bfs_tree.level[a]: edges.append(graph.DLinkedList())
          edge = graph.DLinkedList.Node((a, b))
          edges[bfs_tree.level[a]].add_node(edge)
          if not b in edgerev: edgerev[b] = []
          edgerev[b].append((bfs_tree.level[a], edge))
      propogate_bfs(edges, edgerev, bfs_tree, succ)
    for z in reversed(notreach):
      if not bfs_tree.level[z] is None: continue
      bfs_tree.remove_edge(bfs_tree.pred[z], z, delay_redepth=True)
      bfs_tree.remove_node(z)
  #bfs_tree.checkTreeValid()
def do_inc_add_edge_bfs_opt(succ, bfs_tree, bfs_int, bfs_revint, bfs_level, x, y, is_lex=None):
  if not x in bfs_tree.level: return
  newnode = not y in bfs_tree.level
  #print(newnode, x, y)
  lexonly = not newnode and not is_lex is None and (bfs_tree.level[y] == bfs_tree.level[x] and bfs_int[y] > bfs_int[x] or bfs_tree.level[y] == bfs_tree.level[x] + 1 and bfs_int[bfs_tree.pred[y]] < bfs_int[x])
  if not (newnode or bfs_tree.level[y] > bfs_tree.level[x] + 1 or bfs_tree.level[y] == bfs_tree.level[x] + 1 and bfs_int[bfs_tree.pred[y]] > bfs_int[x] or
    lexonly): return
  lvl = bfs_tree.level[x]+(1 if not lexonly or bfs_tree.level[y] != bfs_tree.level[x] else 0)
  start = 1 if x == bfs_tree.virtual_root else bfs_level[lvl-1-1]+1
  end = bfs_level[lvl-1]
  p = end + 1
  thisLevel = {bfs_tree.pred[y] if lexonly else x: {y}}
  nextLevel = dict()
  exclude = {y}
  monitor = {y} if lexonly else set()
  #print(lexonly, thisLevel)
  if not is_lex is None and not newnode:
    is_lex.split(y); #print("split", x, y)
  while True:
    nextstart = p
    while start <= end:
      node = bfs_revint[start]
      e = bfs_tree.succ[node] if start != 1 else bfs_tree.root_succ
      i = len(e)
      if not node in thisLevel and (i == 0 or is_lex is None and bfs_int[e[0]] == p): p += i
      else:
        if not is_lex is None:
          if i != 0 and not next(iter(is_lex.find(bfs_revint[p-1]).nextval.dataval)) in e:
            l, preval = 0, bfs_revint[p-1]
            s = is_lex.find(min(e, key=lambda z: bfs_int[z]))
            if not s in is_lex.find(preval).nextval.dataval:
              while l != i:
                is_lex.moveset(s, is_lex.find(preval))
                s, preval = s.nextval, s
                l += len(s.dataval)
          if node in thisLevel:
            rem = {z for z in thisLevel[node]}
            for q in thisLevel[node]: #must carefully merge knowing that new nodes can never have any predecessors between the new predecessor and the old predecessor
              preval = bfs_revint[p-1]
              curset = is_lex.enumerate(preval, i, rem)
              curval = next(curset, None)
              if not q in bfs_tree.pred: is_lex.add(q)
              curpreds = []
              #if q in bfs_tree.pred and bfs_tree.pred[q] != node:
              for z in range(bfs_int[node]+1, bfs_int[bfs_tree.pred[q]] if q in bfs_tree.pred and bfs_tree.level[q] == bfs_tree.level[node]+1 else end+1):
                while curval in succ[bfs_revint[z]]: preval, curval = curval, next(curset, None)
              if not curval is None and (not q in bfs_tree.pred or bfs_tree.level[q] != bfs_tree.level[node] or curval in succ[bfs_tree.pred[q]]):
                for z in range(bfs_int[bfs_tree.pred[q]] if q in bfs_tree.pred and bfs_tree.level[q] == bfs_tree.level[node]+1 else end+1, p):
                  if curval in succ[bfs_revint[z]] and not q in succ[bfs_revint[z]]:
                    preval, curval = curval, next(curset, None) #must check all prior predecessors
                    if not all(curval in succ[p] for p in curpreds): break
                  elif not curval in succ[bfs_revint[z]] and q in succ[bfs_revint[z]]:
                    curpreds.append(bfs_revint[z]); break
                  elif q in succ[bfs_revint[z]]: curpreds.append(bfs_revint[z])
                else:
                  for z in is_lex.enumerate(bfs_revint[p-1], i, rem): #idea is to find the last possible insertion point, not the first one to minimize monitoring and its associated edge enumeration
                    #if curval != z and curval in succ[z] and not q in succ[z]:
                    #if z == curval: break
                    if z in succ[curval] and not z in succ[q]:
                      l = list(is_lex.enumerate(bfs_revint[p-1], i))
                      while not curval is None and l.index(curval) <= l.index(z):
                        while True:
                          preval, curval = curval, next(curset, None)
                          if is_lex.find(preval) != is_lex.find(curval): break
                      if curval is None: break
                    if curval in succ[z] and not q in succ[z]:
                      while True:
                        preval, curval = curval, next(curset, None)
                        if is_lex.find(preval) != is_lex.find(curval): break
                      if curval is None: break
                    if not curval in succ[z] and q in succ[z]:
                      l = list(is_lex.enumerate(bfs_revint[p-1], i, rem))
                      while not curval is None and l.index(curval) <= l.index(z):
                        while True:
                          preval, curval = curval, next(curset, None)
                          if is_lex.find(preval) != is_lex.find(curval): break
                      curpreds.append(z); break
                    elif q in succ[z]:
                      while True:
                        preval, curval = curval, next(curset, None)
                        if is_lex.find(preval) != is_lex.find(curval): break
                      curpreds.append(z)
              if not q in bfs_tree.pred or bfs_tree.pred[q] != node: i += 1
              #print(preval, curval, q, curpreds, is_lex)
              if not curval is None and len(is_lex.find(curval).dataval) != 1:
                newsplit = {v for v in is_lex.find(curval).dataval if v in succ[q]}
                if len(newsplit) != 0:
                  if len(newsplit) == len(is_lex.find(curval).dataval):
                    preval, curval = curval, next(curset, None)
                  else:
                    while curval in newsplit:
                      preval, curval = curval, next(curset, None)
                    v = newsplit.pop(); is_lex.split(v); newset = is_lex.find(v)
                    for z in newsplit: is_lex.remove(z); is_lex.add(z, newset)
              elif curval is None and preval != bfs_revint[p-1] and len(is_lex.find(preval).dataval) != 1:
                newsplit = {v for v in is_lex.find(preval).dataval if q in succ[v]}
                #print(newsplit)
                if len(newsplit) != 0 and len(newsplit) != len(is_lex.find(preval).dataval):
                  newsplit = is_lex.find(preval).dataval - newsplit
                  v = newsplit.pop(); is_lex.split(v); newset = is_lex.find(v)
                  for z in newsplit: is_lex.remove(z); is_lex.add(z, newset)
              if curval == q: pass
              elif not curval is None and all(z != curval and curval in succ[z] for z in curpreds): print(preval, curval, q); is_lex.remove(q); is_lex.add(q, is_lex.find(curval))
              else: is_lex.moveset(is_lex.find(q), is_lex.find(preval))
              rem.remove(q)
          #print(is_lex, e, node, thisLevel, bfs_revint[p-1], i, list(is_lex.enumerate(bfs_revint[p-1], i))); #e = is_lex.enumerate(bfs_revint[p-1], i)
          it = list(is_lex.enumerate(bfs_revint[p-1], i))
        else: it = itertools.chain(e, thisLevel[node]) if node in thisLevel else e
        #print(node, e, thisLevel[node] if node in thisLevel else [])
        for q in it:
          #print(q)
          changelvl, isnew = node in thisLevel and q in thisLevel[node], not q in bfs_tree.pred
          if isnew: bfs_tree.add_node(q)
          if not q in monitor and changelvl and (bfs_tree.pred[q] != node or bfs_tree.pred[q] == bfs_tree.virtual_root):
            if bfs_tree.pred[q] != bfs_tree.virtual_root or q in bfs_tree.root_succ: bfs_tree.remove_edge(bfs_tree.pred[q], q, delay_redepth=True)
            bfs_tree.add_edge(node, q, delay_redepth=True); bfs_tree.level[q] = lvl
          elif q in monitor: bfs_tree.level[q] = lvl
          bfs_int[q] = p
          bfs_revint[p] = q
          p += 1
          if changelvl or q in monitor:
            #any changes that occur requires the successors of the whole subtree to be scanned
            if not is_lex is None: priors = {}
            for z in succ[q]:
              #if not is_lex is None and (isnew and z in bfs_tree.pred and q != z and not z in exclude or not isnew) and (bfs_tree.pred[z] != q and bfs_tree.level[z] > bfs_tree.level[q] or bfs_tree.level[z] == bfs_tree.level[q] and bfs_int[bfs_tree.pred[z]] >= bfs_int[node]):
              #  is_lex.split(z); print("split", q, z)
              if z == q or z in exclude: continue
              reparent = not z in bfs_tree.level or bfs_tree.pred[z] == q or bfs_tree.level[z] > lvl + 1 or bfs_tree.level[z] == lvl + 1 and (bfs_revint[bfs_int[bfs_tree.pred[z]]] != bfs_tree.pred[z] or bfs_int[bfs_tree.pred[z]] > bfs_int[q] or node in thisLevel and bfs_tree.pred[z] in thisLevel[node])
              if reparent or not is_lex is None and (bfs_tree.level[z] == lvl + 1 or bfs_tree.level[z] == lvl and bfs_int[bfs_tree.pred[z]] > bfs_int[node]):
                par = q if reparent else bfs_tree.pred[z]   
                if z in bfs_tree.level and bfs_tree.level[z] == lvl:
                  if not par in thisLevel: thisLevel[par] = set()
                  thisLevel[par].add(z)
                else:
                  if not par in nextLevel: nextLevel[par] = set()
                  if z in bfs_tree.pred and bfs_tree.pred[z] == par: monitor.add(z)
                  else: nextLevel[par].add(z)
                exclude.add(z)
                if not is_lex is None and z in bfs_tree.pred:
                  #print(z)
                  s = is_lex.find(z)
                  if s in priors: is_lex.move(z, priors[s])
                  else: priors[s] = is_lex.split(z)
      start += 1
    if lvl < len(bfs_level): bfs_level[lvl] = p - 1
    elif newnode and lvl >= len(bfs_level)-1: bfs_level.append(p-1)
    if len(nextLevel) != 0 or newnode and p - 1 != len(bfs_int): pass #or newnode
    elif p - 1 == len(bfs_revint): del bfs_level[lvl+1:]; break
    elif p - 1 == bfs_level[lvl - 1]: del bfs_level[lvl:]; break
    start, end = nextstart, p - 1
    thisLevel = nextLevel; nextLevel = dict()
    lvl += 1
  #print(bfs_level, bfs_int, bfs_tree)
def do_inc_add_edge_bfs(succ, bfs_tree, bfs_int, bfs_revint, bfs_level, x, y):
  #only need to process added forward and forward-cross edges
  if not x in bfs_tree.level: return
  newnode = not y in bfs_tree.level
  if not (newnode or bfs_tree.level[y] > bfs_tree.level[x] + 1 or bfs_tree.level[y] == bfs_tree.level[x] + 1 and bfs_int[bfs_tree.pred[y]] > bfs_int[x]): return
  #print(x, y)
  #stack = queue.SimpleQueue(); stack.put((y, x)) 
  stack, idx = [(y, x)], 0
  #stack = [(y, x)]
  newPreds, newLevels = {}, {}
  levels = {}
  newnodes, changednodes = set(), set()
  #while not stack.empty():
  while len(stack) != idx:
    #q, p = stack.get()
    q, p = stack[idx] #pop(0) #need to use a queue here not a stack...
    idx += 1
    if q in newPreds:
      if newLevels[q] <= newLevels[p]: continue
      newPreds[q].append(p)
      if newLevels[q] != newLevels[p]+1: raise ValueError(q, p, newLevels[q], newLevels[p]) #would need to fix levels...
    else:
      newPreds[q] = [p]
      newLevels[q] = newLevels[p]+1 if p in newLevels else bfs_tree.level[p]+1
      if not q in bfs_tree.pred:
        newnodes.add(p); changednodes.add(p)
        bfs_tree.add_node(q)
        bfs_tree.add_edge(p, q)
        l = len(bfs_revint)
        bfs_int[q] = l + 1; bfs_revint[l + 1] = q
        #if len(bfs_level) == bfs_tree.level[p] + 1: bfs_level.append(bfs_level[-1] + 1)
      if bfs_tree.level[bfs_tree.pred[q]] + 1 == newLevels[q]: newPreds[q].append(bfs_tree.pred[q])
      #newPreds[q] = [z for z in pred[q] if q != z and (newLevels[z] if z in newLevels else bfs_tree.level[z]) == newLevels[q]-1]
    for z in succ[q]:
      if z == q: continue
      if not z in bfs_tree.level or bfs_tree.level[z] >= newLevels[q] + 1:
        #stack.put((z, q))
        stack.append((z, q))
    if not bfs_tree.level[q] in levels: levels[bfs_tree.level[q]] = set()
    if newLevels[q] == bfs_tree.level[q]: # or bfs_tree.isAncestor(q, y) and bfs_tree.level[y] == bfs_tree.level[x] + 1:
      levels[bfs_tree.level[q]].add((q, None))
    else:
      if not newLevels[q] in levels: levels[newLevels[q]] = set()
      levels[newLevels[q]].add((q, True))
      levels[bfs_tree.level[q]].add((q, False))
    #stack.extend(bfs_tree.succ[q])
  #print(stack, levels, newLevels, newPreds)
  #start = bfs_int[x]
  #while start != 1 and bfs_tree.level[bfs_revint[start]] == bfs_tree.level[bfs_revint[start-1]]: start-=1
  #end = bfs_int[x]
  #while bfs_tree.level[bfs_revint[end]] == bfs_tree.level[bfs_revint[end+1]]: end+=1
  #p = min(bfs_int[z] for z, q in levels[min(levels)] if q != True)
  #while bfs_tree.level[bfs_revint[p]] == bfs_tree.level[bfs_revint[p-1]]: p-=1
  #start = bfs_int[bfs_tree.pred[bfs_revint[p]]]
  #while start != 1 and bfs_tree.level[bfs_revint[start]] == bfs_tree.level[bfs_revint[start-1]]: start-=1
  #p = min(bfs_int[z] for z in bfs_tree.treeByLevel()[min(levels)])
  #start = min(bfs_int[z] for z in (bfs_tree.treeByLevel()[min(levels)-1]))
  start = 1 if x == bfs_tree.virtual_root else bfs_level[bfs_tree.level[x]-1]+1
  end = bfs_level[bfs_tree.level[x]]
  p = end + 1
  redepths = []
  #print(start, p, levels, bfs_level, newPreds)
  for lvl in range(min(levels), max(levels)+1 if not newnode else max(bfs_tree.level.values())+1):
    childs, dellvls = {}, set()
    if lvl in levels:
      for z, addmod in levels[lvl]:
        #if addmod == False: dellvls.add(z); continue
        if z in newnodes: continue
        m = min(bfs_int[q] for q in newPreds[z])
        if bfs_tree.pred[z] == bfs_revint[m]: continue
        #if (z, None) in levels[lvl]: dellvls.add(z)
        if not m in childs: childs[m] = set()
        childs[m].add(z)
    #print(dellvls, childs, start, end, bfs_tree.treeByLevel())
    nextstart = p
    while start <= end:
      e = bfs_tree.succ[bfs_revint[start]] if start != 1 else bfs_tree.root_succ
      i = len(e)
      if i == 0 or not bfs_revint[start] in changednodes and bfs_int[e[0]] == p: p += i
      else:
        while i > 0:
          z = e[-i]
          #if z in dellvls: bfs_tree.remove_edge(bfs_revint[start], z, delay_redepth=True); i -= 1; continue
          #if not newnode:
          #  bfs_int[bfs_revint[p]] = bfs_int[z]
          #  bfs_revint[bfs_int[z]] = bfs_revint[p]
          bfs_int[z] = p
          bfs_revint[p] = z
          p += 1; i -= 1
      if start in childs:
        for q in childs[start]:
          if bfs_tree.pred[q] != bfs_tree.virtual_root or q in bfs_tree.root_succ: changednodes.add(bfs_tree.pred[q]); bfs_tree.remove_edge(bfs_tree.pred[q], q, delay_redepth=True)
          bfs_tree.add_edge(bfs_revint[start], q, delay_redepth=True)
          redepths.append(q)
          #if not newnode:
          #  bfs_int[bfs_revint[p]] = bfs_int[q]
          #  bfs_revint[bfs_int[q]] = bfs_revint[p]
          bfs_int[q] = p
          bfs_revint[p] = q
          p += 1 #relidx += 1
      start += 1
    if lvl < len(bfs_level): bfs_level[lvl] = p - 1
    elif newnode and lvl >= len(bfs_level)-1: bfs_level.append(p-1)
    if p - 1 == len(bfs_revint): del bfs_level[lvl+1:]; break
    elif p - 1 == bfs_level[lvl - 1]: del bfs_level[lvl:]; break
    start, end = nextstart, p - 1
  bfs_tree.redepthSubTrees(redepths)
  #bfs_tree.checkTreeValid()
def do_dec_remove_edge_bfs_opt(pred, bfs_tree, bfs_int, bfs_revint, bfs_level, x, y, is_lex=None):
  if not x in bfs_tree.level or not y in bfs_tree.level: return
  if bfs_tree.pred[y] != x: return #only need to process deleted tree edges
  thisLevel = {x: {y}}
  nextLevel = dict()
  addLevel = dict()
  unreachable = set()
  unreachord = []
  monitor = set()
  #first must scan subtree in BFS order to find first reachable nodes, then subtrees of those reachable nodes do not need to be scanned
  while len(thisLevel) != 0:
    for node in thisLevel:
      for q in thisLevel[node]:
        for z in pred[q]:
          if z == q or not z in bfs_tree.pred: continue
          if not z in addLevel: addLevel[z] = set()
          addLevel[z].add(q)
          if not bfs_tree.isAncestor(z, y) or z in monitor and not z in unreachable:
            monitor.add(q)
        nextLevel[q] = bfs_tree.succ[q]
        if not node in monitor and not q in monitor:
          unreachord.append(q); unreachable.add(q)
    thisLevel = nextLevel; nextLevel = {}
  lvl = bfs_tree.level[x] + 1
  start = 1 if x == bfs_tree.virtual_root else bfs_level[bfs_tree.level[x]-1]+1
  end = bfs_level[bfs_tree.level[x]]
  p = end + 1
  exclude = set()
  bfs_tree.remove_edge(x, y, delay_redepth=True)
  while True:
    nextstart = p
    while start <= end:
      node = bfs_revint[start]
      e = bfs_tree.succ[node] if start != 1 else bfs_tree.root_succ
      #i = len(e)
      for z in e:
        if z in unreachable or z in monitor:
          if bfs_tree.pred[z] != node: continue # or node in addLevel and z in addLevel[node]: continue
          bfs_tree.level[z] = lvl; exclude.add(z)
          if z in unreachable: unreachable.remove(z)
        bfs_int[z] = p
        bfs_revint[p] = z
        p += 1
      if node in addLevel:
        for z in addLevel[node]:
          if z in exclude: continue
          exclude.add(z)
          if z in unreachable: unreachable.remove(z)
          if bfs_tree.pred[z] != node:
            bfs_tree.remove_edge(bfs_tree.pred[z], z, delay_redepth=True)
            bfs_tree.add_edge(node, z, delay_redepth=True)
          bfs_tree.level[z] = lvl
          bfs_int[z] = p
          bfs_revint[p] = z
          p += 1
      start += 1
    if lvl - 1 == len(bfs_level): bfs_level.append(end)
    else: bfs_level[lvl - 1] = end
    if p > len(bfs_revint) or p == start: del bfs_level[lvl:]; break
    start, end = nextstart, p - 1
    lvl += 1
  if bfs_level[-1] != len(bfs_revint) - len(unreachable): bfs_level.append(len(bfs_revint) - len(unreachable))
  for z in reversed(unreachord):
    if not z in unreachable: continue
    bfs_tree.remove_edge(bfs_tree.pred[z], z, delay_redepth=True)
    bfs_tree.remove_node(z)
    del bfs_int[z]
    del bfs_revint[len(bfs_revint)]
def do_dec_remove_edge_bfs(pred, bfs_tree, bfs_int, bfs_revint, bfs_level, x, y):
  if not x in bfs_tree.level or not y in bfs_tree.level: return
  if bfs_tree.pred[y] != x: return #only need to process deleted tree edges
  #bfs_tree, bfs_int, bfs_revint = bfs(); return
  newPreds, newLevels = {}, {}
  levels = {}
  stack = [y]
  succInTree = {}
  revLevels = {}
  while len(stack) != 0:
    q = stack.pop()
    predlevels = {}
    for z in pred[q]:
      if z == q or not z in bfs_tree.pred: continue
      if bfs_tree.isAncestor(z, y):
        if not z in succInTree: succInTree[z] = set()
        succInTree[z].add(q)
        continue
      lvl = bfs_tree.level[z]
      if not lvl in predlevels: predlevels[lvl] = []
      predlevels[lvl].append(z)
    stack.extend(bfs_tree.succ[q])
    if len(predlevels) == 0: newPreds[q] = set(); continue
    lvl = min(predlevels) #min(bfs_tree.level[z] for z in pred[q])
    newPreds[q] = predlevels[lvl]
    newLevels[q] = lvl
    if not lvl in revLevels: revLevels[lvl] = set()
    revLevels[lvl].add(q)
  if len(revLevels) != 0:
    lvl = min(revLevels)
    while True:
      if lvl in revLevels:
        for q in revLevels[lvl]:
          if q in succInTree:
            for z in succInTree[q]:
              if not z in newLevels or newLevels[z] > lvl+1:
                newPreds[z] = [q]
                if z in newLevels: revLevels[newLevels[z]].remove(z)
                newLevels[z] = lvl+1
                if not lvl+1 in revLevels: revLevels[lvl+1] = set()
                revLevels[lvl+1].add(z)
              elif newLevels[z] == lvl+1: newPreds[z].append(q)
          if lvl+1 != bfs_tree.level[q]:
            if not bfs_tree.level[q] in levels: levels[bfs_tree.level[q]] = set()
            levels[bfs_tree.level[q]].add((q, False))
            if not lvl+1 in levels: levels[lvl+1] = set()
            levels[lvl+1].add((q, True))
          else:
            if not lvl+1 in levels: levels[lvl+1] = set()
            levels[lvl+1].add((q, None))
      lvl += 1
      if lvl > max(revLevels): break
  unreachable = [q for q in reversed(newPreds) if len(newPreds[q]) == 0]
  changednodes = {bfs_tree.pred[q] for q in unreachable}
  #if len(unreachable) != 0:
  #  raise ValueError(unreachable, newLevels)
  #print(x, y, newPreds, newLevels, levels)
  #p = min(bfs_int[z] for z, _ in levels[min(levels)])
  #start = bfs_tree.pred[bfs_revint[p]]
  #end = max(bfs_int[z] for z in (bfs_tree.treeByLevel()[min(levels)-1]))
  #print(p, start, end, levels)
  
  #p = min(bfs_int[z] for z, q in levels[min(levels)] if q != True)
  #while bfs_tree.level[bfs_revint[p]] == bfs_tree.level[bfs_revint[p-1]]: p-=1
  #start = bfs_int[bfs_tree.pred[bfs_revint[p]]]
  #while start != 1 and bfs_tree.level[bfs_revint[start]] == bfs_tree.level[bfs_revint[start-1]]: start-=1
  #print(start, p)
  #p = min(bfs_int[z] for z in bfs_tree.treeByLevel()[min(levels)])
  #start = min(bfs_int[z] for z in (bfs_tree.treeByLevel()[min(levels)-1]))
  start = 1 if x == bfs_tree.virtual_root else bfs_level[bfs_tree.level[x]-1]+1
  end = bfs_level[bfs_tree.level[x]]
  p = end + 1
  #print(start, p, min(levels), bfs_tree.level[x])
  #print(bfs_level)
  redepths = []
  for lvl in range(min(levels) if len(unreachable) == 0 else (bfs_tree.level[y] if len(levels) == 0 else min(min(levels), bfs_tree.level[y])), max(levels)+1 if len(unreachable) == 0 else (max(bfs_tree.level.values())+1 if len(levels) == 0 else max(max(levels), max(bfs_tree.level.values()))+1)):
    childs, dellvls = {}, set()
    if lvl in levels:
      for z, addmod in levels[lvl]:
        if addmod == False: dellvls.add(z); changednodes.add(bfs_tree.pred[z]); continue
        m = min(bfs_int[q] for q in newPreds[z])
        if bfs_tree.pred[z] == bfs_revint[m]: continue
        if (z, None) in levels[lvl]: dellvls.add(z); changednodes.add(bfs_tree.pred[z])
        if not m in childs: childs[m] = set()
        childs[m].add(z)
    #print(dellvls, childs, start, end, bfs_tree.treeByLevel())
    nextstart = p
    while start <= end:
      #print(start, p)
      e = bfs_tree.succ[bfs_revint[start]] if start != 1 else bfs_tree.root_succ
      i = len(e)
      if i == 0 or not bfs_revint[start] in changednodes and bfs_int[e[0]] == p: p += i
      else:
        while i > 0:
          z = e[-i]
          if z in dellvls: bfs_tree.remove_edge(bfs_revint[start], z, delay_redepth=True); i -= 1; continue
          if z in unreachable: i -= 1; continue
          bfs_int[z] = p
          bfs_revint[p] = z
          p += 1; i -= 1 
      if start in childs:
        for q in childs[start]:
          if bfs_tree.pred[q] != bfs_tree.virtual_root or q in bfs_tree.root_succ: bfs_tree.remove_edge(bfs_tree.pred[q], q, delay_redepth=True)
          bfs_tree.add_edge(bfs_revint[start], q, delay_redepth=True)
          redepths.append(q)
          bfs_int[q] = p
          bfs_revint[p] = q
          p += 1 #relidx += 1
      start += 1
    if lvl - 1 == len(bfs_level): bfs_level.append(end)
    else: bfs_level[lvl - 1] = end
    if p > len(bfs_revint) - len(unreachable): del bfs_level[lvl:]; break
    start, end = nextstart, p - 1
  if bfs_level[-1] != len(bfs_revint) - len(unreachable): bfs_level.append(len(bfs_revint) - len(unreachable))
  for z in unreachable:
    bfs_tree.remove_edge(bfs_tree.pred[z], z, delay_redepth=True)
    bfs_tree.remove_node(z)
    del bfs_int[z]
    del bfs_revint[len(bfs_revint)]
  bfs_tree.redepthSubTrees(redepths)
  #bfs_tree.checkTreeValid()
def check_bfs(source, succ, bfs_tree, bfs_int, bfs_revint, bfs_level):
  cbfs_tree, cbfs_int, cbfs_revint, cbfs_level = do_bfs(source, succ, bfs_int)
  if bfs_tree.pred != cbfs_tree.pred: raise ValueError("Bad BFS", bfs_tree.pred, cbfs_tree.pred)
  if bfs_int != cbfs_int: raise ValueError("Bad BFS order", bfs_int, cbfs_int)
  if bfs_revint != cbfs_revint: raise ValueError("Bad BFS Reverse order", bfs_revint, cbfs_revint)
  if bfs_level != cbfs_level: raise ValueError("Bad BFS Levels", bfs_level, cbfs_level)

def graphviz_dot_bfst(succ, bfs_tree, bfs_int, pre="b"):
  nonTreeEdges = ";".join(pre + str(x) + "->" + pre + str(y) + "[style=dashed;constraint=false]" for x in bfs_tree.pred for y in succ[x] if bfs_tree.pred[y] != x)
  t = ";".join(pre + str(x) + " [label=" + "\"" + str(x) + (" [" + str(bfs_int[x]) + "]" if not bfs_int is None else "") + "\"" + "]" for x in bfs_tree.pred)
  return ";".join(filter(lambda x: x != "", (bfs_tree.graphviz_dot(pre, bfs_int), t, nonTreeEdges)))

def graphviz_dot_bfst_part(succ, bfs_tree, bfs_int, is_lex, pre="b"):
  clusters = ""
  x = is_lex.seq.headval
  while True:
    clusters += "subgraph " + "cluster_" + pre + str(next(iter(x.dataval))) + " {\n\tnode[style=filled];\n\t" + ";".join(pre + str(z) for z in sorted(x.dataval, key=lambda z: bfs_int[z], reverse=True)) + ";\n\tcolor=blue;" + "\n}\n"
    x = x.nextval
    if x is is_lex.seq.headval: break  
  nonTreeEdges = ";".join(pre + str(x) + "->" + pre + str(y) + "[style=dashed;constraint=false]" for x in bfs_tree.pred for y in succ[x] if bfs_tree.pred[y] != x)
  t = ";".join(pre + str(x) + " [label=" + "\"" + str(x) + (" [" + str(bfs_int[x]) + "]" if not bfs_int is None else "") + "\"" + "]" for x in bfs_tree.pred)
  return clusters + ";".join(filter(lambda x: x != "", (bfs_tree.graphviz_dot(pre, bfs_int), t, nonTreeEdges)))

def paper_inc_dec_bfs(output_dir):
  import os
  root, init = 1, [[2, 3, 5], [7], [4], [3, 7, 9], [6, 10], [7, 9], [5, 6, 8], [], [3], []]
  new_edge = (root, 7)
  del_edge = (root, 3)
  succ, pred = {1: set()}, {1: set()}
  bfs_tree, bfs_int, bfs_revint, bfs_level = init_bfs(root)
  for x, s in enumerate(init):
    if not x+1 in succ:
      succ[x+1] = set(); pred[x+1] = set()
      #add_node_bfs(bfs_tree, bfs_int, bfs_revint, bfs_level, x+1)
    for y in s:
      if not y in pred:
        succ[y] = set(); pred[y] = set()
        #add_node_bfs(bfs_tree, bfs_int, bfs_revint, bfs_level, y)
      succ[x+1].add(y); pred[y].add(x+1)
      do_inc_add_edge_bfs(succ, bfs_tree, bfs_int, bfs_revint, bfs_level, x+1, y)
      if y != root and len(pred[y]) == 1:
        do_dec_remove_edge_bfs(pred, bfs_tree, bfs_int, bfs_revint, bfs_level, root, y)
  output = "Initial Graph with its BFST and Intervals:\n"
  output += graph.make_graphviz_dot_text(succ, graphviz_dot_bfst(succ, bfs_tree, bfs_int)) + "\n"
  succ[new_edge[0]].add(new_edge[1]); pred[new_edge[1]].add(new_edge[0])
  do_inc_add_edge_bfs(succ, bfs_tree, bfs_int, bfs_revint, bfs_level, new_edge[0], new_edge[1])
  output += "\nGraph, BFST and Intervals On Edge Addition (%d, %d):\n" % new_edge
  output += graph.make_graphviz_dot_text(succ, graphviz_dot_bfst(succ, bfs_tree, bfs_int)) + "\n"
  output += "\nGraph, BFST and Intervals On Edge Deletion (%d, %d):\n" % del_edge
  succ[del_edge[0]].remove(del_edge[1]); pred[del_edge[1]].remove(del_edge[0])
  do_dec_remove_edge_bfs(pred, bfs_tree, bfs_int, bfs_revint, bfs_level, del_edge[0], del_edge[1])
  output += graph.make_graphviz_dot_text(succ, graphviz_dot_bfst(succ, bfs_tree, bfs_int)) + "\n"
  with open(os.path.join(output_dir, 'bfs_graph_dot.txt'), "w") as f:
    f.write(output)

def timing_inc_dec_general_bfs_real(cfg_dir, output_dir):
  import os
  iterations, repeat = 1, 1
  output = ""
  results = {}
  for edges in (graph.get_real_graph(cfg_dir),):
    c = len(edges)
    results[c] = graph.timing_test(iterations, lambda: edges, repeat, [init_bfs] * 2 + [semi_dynamic_init_bfs],
      [lambda n, data: None] * 2 + [lambda n, data: semi_dynamic_add_node_bfs(data[0], data[1], n)],
      [lambda n, data: None] * 2 + [lambda n, data: semi_dynamic_remove_node_bfs(data[0], data[1], n)],
      [lambda x, y, root, succ, pred, data, _: do_inc_add_edge_bfs_opt(succ, data[0], data[1], data[2], data[3], x, y),
       lambda x, y, root, succ, pred, data, _: do_inc_add_edge_bfs_basic(succ, data[0], data[1], data[2], data[3], x, y),
       lambda x, y, root, succ, pred, data, _: semi_dynamic_add_edge_bfs(data[0], succ, pred, x, y)],
      [lambda x, y, root, succ, pred, data, _: do_dec_remove_edge_bfs_opt(pred, data[0], data[1], data[2], data[3], x, y),
       lambda x, y, root, succ, pred, data, _: do_dec_remove_edge_bfs_basic(succ, data[0], data[1], data[2], data[3], x, y),
       lambda x, y, root, succ, pred, data, _: semi_dynamic_remove_edge_bfs(data[0], succ, pred, x, y)], [], delete_first=True) #[lambda x, y, root, succ, pred, data: do_bfs(root, succ)]
    print(results[c])
  for x in sorted(results):
    output += ("%d %s %s %s %s %s %s\n" % (x, *(repr(z / (iterations * repeat)) for y in results[x] for z in y)))
  with open(os.path.join(output_dir, 'bfs_gpaper.txt'), "w") as f:
    f.write(output)
    
def timing_inc_dec_general_bfs(cfg_dir, output_dir, connected=False):
  import os
  iterations, repeat = 10, 1
  output = ""
  results = {}
  for c in range(100, 150, 10):
    results[c] = graph.timing_test(iterations, lambda: graph.random_digraph(c, connected), repeat, [init_bfs] * 2 + [semi_dynamic_init_bfs],
      [lambda n, data: None] * 2 + [lambda n, data: semi_dynamic_add_node_bfs(data[0], data[1], n)],
      [lambda n, data: None] * 2 + [lambda n, data: semi_dynamic_remove_node_bfs(data[0], data[1], n)],
      [lambda x, y, root, succ, pred, data, _: do_inc_add_edge_bfs_opt(succ, data[0], data[1], data[2], data[3], x, y),
       lambda x, y, root, succ, pred, data, _: do_inc_add_edge_bfs_basic(succ, data[0], data[1], data[2], data[3], x, y),
       lambda x, y, root, succ, pred, data, _: semi_dynamic_add_edge_bfs(data[0], succ, pred, x, y)],
      [lambda x, y, root, succ, pred, data, _: do_dec_remove_edge_bfs_opt(pred, data[0], data[1], data[2], data[3], x, y),
       lambda x, y, root, succ, pred, data, _: do_dec_remove_edge_bfs_basic(succ, data[0], data[1], data[2], data[3], x, y),
       lambda x, y, root, succ, pred, data, _: semi_dynamic_remove_edge_bfs(data[0], succ, pred, x, y)], []) #[lambda x, y, root, succ, pred, data: do_bfs(root, succ)]
    print(results[c])
  for x in sorted(results):
    output += ("%d %s %s %s %s %s %s\n" % (x, *(repr(z / (iterations * repeat)) for y in results[x] for z in y)))
  with open(os.path.join(output_dir, 'bfs_paper.txt'), "w") as f:
    f.write(output)

def print_bfst_part(x, y, root, succ, bfs_tree, bfs_int, is_lex, pbfs_tree, pbfs_int, pis_lex, base, output_dir):
  graph.do_graphviz_dot(graph.make_graphviz_dot_text(succ, ';'.join((graphviz_dot_bfst_part(succ, base[0], base[1], base[2], pre="bb"), graphviz_dot_bfst_part(succ, pbfs_tree, pbfs_int, pis_lex, pre="bp"), graphviz_dot_bfst_part(succ, bfs_tree, bfs_int, is_lex)))), output_dir)
def print_bfst(x, y, root, succ, bfs_tree, bfs_int, pbfs_tree, pbfs_int, base, output_dir):
  graph.do_graphviz_dot(graph.make_graphviz_dot_text(succ, ';'.join((graphviz_dot_bfst(succ, base[0], base[1], pre="bb"), graphviz_dot_bfst(succ, pbfs_tree, pbfs_int, pre="bp"), graphviz_dot_bfst(succ, bfs_tree, bfs_int)))), output_dir)

def print_sd_bfst(x, y, root, succ, bfs_tree, base, output_dir):
  graph.do_graphviz_dot(graph.make_graphviz_dot_text(succ, ';'.join((graphviz_dot_bfst(succ, base[0], None, pre="bb"), graphviz_dot_bfst(succ, bfs_tree, None)))), output_dir)
  
def verify_inc_dec_general_bfs(output_dir, connected=False):
  iterations, nodes = 1000, 15
  graph.verification_algo_test(iterations, lambda: graph.random_digraph(nodes, connected), [init_bfs] * 2,
    [lambda n, data: None] * 2,
    [lambda n, data: None] * 2,
    [lambda x, y, root, succ, pred, data, _: do_inc_add_edge_bfs_opt(succ, data[0], data[1], data[2], data[3], x, y),
     lambda x, y, root, succ, pred, data, graph_data: do_inc_add_edge_bfs_basic(succ, data[0], data[1], data[2], data[3], x, y, graph_data[0][1])],
    [lambda x, y, root, succ, pred, data, _: do_dec_remove_edge_bfs_opt(pred, data[0], data[1], data[2], data[3], x, y),
     lambda x, y, root, succ, pred, data, graph_data: do_dec_remove_edge_bfs_basic(succ, data[0], data[1], data[2], data[3], x, y, graph_data[0][1])],
    [lambda x, y, root, succ, pred, graph_data: do_bfs(root, succ, graph_data[0][1])],
    print_func=lambda x, y, root, succ, pred, graph_data, base: print_bfst(x, y, root, succ, graph_data[0][0], graph_data[0][1], graph_data[1][0], graph_data[1][1], base, output_dir))
    
def verify_inc_dec_general_lex_bfs(output_dir):
  iterations, nodes = 1000, 15
  graph.verification_algo_test(iterations, lambda: graph.random_digraph(nodes, False), #[lambda root: (*init_bfs(root), graph.PartitionRefinement([root]))],
    #[lambda n, data: None],
    #[lambda n, data: None],
    #[lambda x, y, root, succ, pred, data, _: do_inc_add_edge_bfs_opt(succ, data[0], data[1], data[2], data[3], x, y, data[4])],
    #[lambda x, y, root, succ, pred, data, _: do_dec_remove_edge_bfs_opt(pred, data[0], data[1], data[2], data[3], x, y, data[4])],
    [], [], [], [], [],
    [lambda x, y, root, succ, pred, graph_data: do_lex_bfs_opt(root, succ, pred)], #, graph_data[0][1]
    print_func=lambda x, y, root, succ, pred, graph_data, base: print_bfst(x, y, root, succ, graph_data[0][0], graph_data[0][1], graph_data[0][0], graph_data[0][1], base, output_dir), seed=1)

def verify_rank_dynamic_inc_dec_general_bfs(output_dir):
  iterations, nodes = 1000, 15
  graph.verification_algo_test(iterations, lambda: graph.random_digraph(nodes, False), [semi_dynamic_init_bfs],
    [lambda n, data: semi_dynamic_add_node_bfs(data[0], data[1], n)],
    [lambda n, data: semi_dynamic_remove_node_bfs(data[0], data[1], n)],
    [lambda x, y, root, succ, pred, data, _: semi_dynamic_add_edge_bfs(data[0], succ, pred, x, y)],
    [lambda x, y, root, succ, pred, data, _: semi_dynamic_remove_edge_bfs(data[0], succ, pred, x, y)],
    [lambda x, y, root, succ, pred, graph_data: do_bfs(root, succ, {x: x for x in graph_data[0][0].pred}, True)], #succ
    comparer=lambda x, y: x[0] == y[0],
    print_func=lambda x, y, root, succ, pred, graph_data, base: print_sd_bfst(x, y, root, succ, graph_data[0][0], base, output_dir))
    
def verify_semi_dynamic_inc_dec_general_bfs(output_dir):
  iterations, nodes = 1000, 15
  graph.verification_algo_test(iterations, lambda: graph.random_digraph(nodes, False), [semi_dynamic_init_bfs],
    [lambda n, data: semi_dynamic_add_node_bfs(data[0], data[1], n, False)],
    [lambda n, data: semi_dynamic_remove_node_bfs(data[0], data[1], n, False)],
    [lambda x, y, root, succ, pred, data, _: semi_dynamic_add_edge_bfs(data[0], succ, data[1], x, y, False)],
    [lambda x, y, root, succ, pred, data, _: semi_dynamic_remove_edge_bfs(data[0], succ, data[1], x, y, False)],
    [lambda x, y, root, succ, pred, graph_data: do_bfs(root, succ, {x: x for x in graph_data[0][0].pred}, True)], #succ
    comparer=lambda x, y: x[0] == y[0],
    print_func=lambda x, y, root, succ, pred, graph_data, base: print_sd_bfst(x, y, root, succ, graph_data[0][0], base, output_dir))

def verify_inc_dec_lex_bfs(output_dir):
  iterations, nodes = 1000, 15
  graph.verification_algo_test(iterations, lambda: graph.random_digraph(nodes), [lambda root: (*init_bfs(root), graph.PartitionRefinement([root]))],
    #[lambda n, data: add_node_bfs(data[0], data[1], data[2], data[3], n, data[4])],
    #[lambda n, data: remove_node_bfs(data[0], data[1], data[2], data[3], n, data[4])],
    [], [],
    [lambda x, y, root, succ, pred, data, _: do_inc_add_edge_bfs_opt(succ, data[0], data[1], data[2], data[3], x, y, data[4])],
    [lambda x, y, root, succ, pred, data, _: do_dec_remove_edge_bfs_opt(pred, data[0], data[1], data[2], data[3], x, y, data[4])],
    [lambda x, y, root, succ, pred, graph_data: do_lex_bfs_opt(root, succ, pred, graph_data[0][1])],
    print_func=lambda x, y, root, succ, pred, graph_data, base: print_bfst(x, y, root, succ, graph_data[0][0], graph_data[0][1], graph_data[0][0], graph_data[0][1], base, output_dir))