import graph
import sccreach
import dfs
import dominators
import cfg

NONHEADER, REDUCIBLE, IRREDUCIBLE, SELF = 0, 1, 2, 3
def init_lnf():
  root = 0; return [0, 0, 0], {root: 0}, {root: NONHEADER}, {}
def add_node_lnf(n, loopheaders, looptypes):
  loopheaders[n] = 0
  looptypes[n] = NONHEADER
def remove_node_lnf(n, loopheaders, looptypes):
  del loopheaders[n]
  del looptypes[n]
def do_inc_reducible_tarjan_lnf(x, y, pred, dfs_tree, dfs_int, loopcounts, loopheaders, looptypes, irreducible_is_error=True):
  #def find_loop_head(xs, head):
  #  while loopheaders[xs] != 0 and not dfs.do_isAncestor(dfs_int, loopheaders[xs], head): xs = loopheaders[xs]
  #  return xs
  #curloops = {}
  newloopheads = {}
  def find_loop_head(xs, head):
    #if xs in curloops: return curloops[xs]
    #checked = {xs}
    while (loopheaders[xs] != 0 or xs in newloopheads) and not dfs.do_isAncestor(dfs_int, loopheaders[xs] if not xs in newloopheads else newloopheads[xs], head):
      xs = loopheaders[xs] if not xs in newloopheads else newloopheads[xs]
      #checked.add(xs)
    #for x in checked: curloops[x] = xs
    return xs
  if x == y:
    if not irreducible_is_error: return True
    if looptypes[x] == NONHEADER: looptypes[x] = SELF; loopcounts[0] += 1
    return
  if (dfs.do_isForwardEdge(dfs_tree, dfs_int, x, y) or dfs.do_isCrossEdge(dfs_int, x, y)) and loopheaders[y] != 0 and not dfs.do_isAncestor(dfs_int, loopheaders[y], x):
    if not irreducible_is_error: return False
    raise ValueError("Irreducible")
  if dfs.do_isForwardEdge(dfs_tree, dfs_int, x, y) or dfs.do_isCrossEdge(dfs_int, x, y) and loopheaders[y] == 0:
    if not irreducible_is_error: return True
    return #forward edges are trivial case
  if dfs_tree.pred[y] == x:
    head = x
    while not head is None and head != 0:
      b = {find_loop_head(z, head) for z in pred[head] if z != head and dfs.do_isBackEdge(dfs_tree, dfs_int, z, head) and (loopheaders[z] == 0 or dfs.do_isAncestor(dfs_int, head, find_loop_head(z, head)))}
      if any(loopheaders[z] != head for z in b):
        if not irreducible_is_error: return False
        raise ValueError("Irreducible")
      head = dfs_tree.pred[head]
  if dfs.do_isBackEdge(dfs_tree, dfs_int, x, y):
    h = find_loop_head(x, y)
    if y == loopheaders[h]:
      if not irreducible_is_error: return True
      return
    head, worklist = y, {h}
  elif loopheaders[y] != 0:
    h = find_loop_head(x, loopheaders[y])
    if loopheaders[y] == loopheaders[h]:
      if not irreducible_is_error: return True
      return
    head, worklist = loopheaders[y], {h}
  elif dfs_tree.pred[y] == x:
    #for head in sorted(dfs_tree.subTree(y), key=lambda v: dfs_int[v][0]):
    #  if loopheaders[head] != 0 and not dfs.do_isAncestor(dfs_int, loopheaders[head], head):
    #    if not irreducible_is_error: return False
    #    raise ValueError("Irreducible")
    head = x
    while not head is None and head != 0:
      #totedge += len(pred[head])
      b = {find_loop_head(z, head) for z in pred[head] if z != head and dfs.do_isBackEdge(dfs_tree, dfs_int, z, head) and (loopheaders[z] == 0 or dfs.do_isAncestor(dfs_int, head, find_loop_head(z, head)))}
      #b = {z for z in pred[head] if loopheaders[z] == 0 and z != head and dfs.do_isBackEdge(dfs_tree, dfs_int, z, head)}
      if len(b) != 0:
        worklist = b
        break
      head = dfs_tree.pred[head]
    if head is None or head == 0:
      if not irreducible_is_error: return True
      return
    """
    xt, term = x, dfs_tree.lca(x, y)
    while True:
      b = {z for z in pred[xt] if loopheaders[z] == 0 and z != xt and dfs.do_isBackEdge(dfs_tree, dfs_int, z, xt)}
      if len(b) != 0:
        head, worklist = xt, b
        break
      xt = dfs_tree.pred[xt]
      if xt is None or xt == 0 or xt == term:
        if not irreducible_is_error: return True
        return
    """
  loopBody = set()
  while len(worklist) != 0:
    v = worklist.pop()
    loopBody.add(v)
    #totedge += len(pred[v])
    for w in pred[v]:
      if w == v or dfs.do_isBackEdge(dfs_tree, dfs_int, w, v): continue
      wprime = find_loop_head(w, head)
      if not dfs.do_isAncestor(dfs_int, head, wprime):
        if not irreducible_is_error: return False
        raise ValueError("Irreducible") #induced by cross, back or tree edges which extend a loop
      if wprime != head and loopheaders[wprime] != head: worklist.add(wprime)
  if not irreducible_is_error: return True
  if looptypes[head] == NONHEADER or looptypes[head] == SELF:
    if looptypes[head] == SELF: loopcounts[0] -= 1
    looptypes[head] = REDUCIBLE
    loopcounts[1] += 1
  for v in loopBody: loopheaders[v] = head
"""
  while True:
    while len(worklist) != 0:
      v = worklist.pop()
      newloopheads[v] = head
      for w in pred[v]:
        if w == v or dfs.do_isBackEdge(dfs_tree, dfs_int, w, v): continue
        wprime = find_loop_head(w, head)
        if not dfs.do_isAncestor(dfs_int, head, wprime):
          if not irreducible_is_error: return False
          raise ValueError("Irreducible") #induced by cross, back or tree edges which extend a loop
        if wprime != head and not wprime in newloopheads: worklist.add(wprime) # and loopheaders[wprime] != head
    if dfs_tree.pred[y] == x:
      head = dfs_tree.pred[head]
      while not head is None and head != 0:
        b = {find_loop_head(z, head) for z in pred[head] if z != head and dfs.do_isBackEdge(dfs_tree, dfs_int, z, head) and (loopheaders[z] == 0 and not z in newloopheads or dfs.do_isAncestor(dfs_int, head, find_loop_head(z, head)))}
        if len(b) != 0:
          worklist = b
          break
        head = dfs_tree.pred[head]
      if head is None or head == 0: break
    else: break
  if not irreducible_is_error: return True
  for v in newloopheads:
    head = newloopheads[v]
    if looptypes[head] == NONHEADER or looptypes[head] == SELF:
      if looptypes[head] == SELF: loopcounts[0] -= 1
      looptypes[head] = REDUCIBLE
      loopcounts[1] += 1
    loopheaders[v] = head
"""
"""
def do_inc_reducible_tarjan_lnf(x, y, pred, dfs_tree, dfs_int, loopcounts, loopheaders, looptypes, irreducible_is_error=True):
  def find_loop_head(xs, head):
    while loopheaders[xs] != 0 and not dfs.do_isAncestor(dfs_int, loopheaders[xs], head): xs = loopheaders[xs]
    return xs
  if x == y:
    if not irreducible_is_error: return True
    if looptypes[x] == NONHEADER: looptypes[x] = SELF; loopcounts[0] += 1
    return
  if (dfs.do_isForwardEdge(dfs_tree, dfs_int, x, y) or dfs.do_isCrossEdge(dfs_int, x, y)) and loopheaders[y] != 0 and not dfs.do_isAncestor(dfs_int, loopheaders[y], x):
    if not irreducible_is_error: return False
    raise ValueError("Irreducible")
  if dfs_tree.pred[y] == x:
    head = x
    while not head is None and head != 0:
      b = {find_loop_head(z, head) for z in pred[head] if dfs.do_isBackEdge(dfs_tree, dfs_int, z, head) and z != head and (loopheaders[z] == 0 or dfs.do_isAncestor(dfs_int, head, find_loop_head(z, head)))}
      if any(loopheaders[z] != head for z in b):
        if not irreducible_is_error: return False
        raise ValueError("Irreducible")
      head = dfs_tree.pred[head]
  if dfs.do_isForwardEdge(dfs_tree, dfs_int, x, y) or dfs.do_isCrossEdge(dfs_int, x, y) and loopheaders[y] == 0:
    if not irreducible_is_error: return True
    return #forward edges are trivial case
  if dfs.do_isBackEdge(dfs_tree, dfs_int, x, y):
    h = find_loop_head(x, y)
    if y == loopheaders[h]:
      if not irreducible_is_error: return True
      return
    head, worklist = y, {h}
  elif (dfs.do_isCrossEdge(dfs_int, x, y) or dfs_tree.pred[y] == x) and loopheaders[y] != 0:
    h = find_loop_head(x, loopheaders[y])
    if loopheaders[y] == loopheaders[h]:
      if not irreducible_is_error: return True
      return
    head, worklist = loopheaders[y], {h}
  elif dfs_tree.pred[y] == x:
    xt, term = x, dfs_tree.lca(x, y)
    while True:
      b = {z for z in pred[xt] if dfs.do_isBackEdge(dfs_tree, dfs_int, z, xt) and loopheaders[z] == 0 and z != xt}
      if len(b) != 0:
        head, worklist = xt, b
        break
      xt = dfs_tree.pred[xt]
      if xt is None or xt == 0 or xt == term:
        if not irreducible_is_error: return True
        return
  loopBody = set()
  while len(worklist) != 0:
    v = worklist.pop()
    loopBody.add(v)
    for w in pred[v]:
      if w == v or dfs.do_isBackEdge(dfs_tree, dfs_int, w, v): continue
      wprime = find_loop_head(w, head)
      if not dfs.do_isAncestor(dfs_int, head, wprime):
        if not irreducible_is_error: return False
        raise ValueError("Irreducible") #induced by cross, back or tree edges which extend a loop
      if wprime != head and loopheaders[wprime] != head: worklist.add(wprime)
  if not irreducible_is_error: return True
  if looptypes[head] == NONHEADER or looptypes[head] == SELF:
    if looptypes[head] == SELF: loopcounts[0] -= 1
    looptypes[head] = REDUCIBLE
    loopcounts[1] += 1
  for v in loopBody: loopheaders[v] = head
"""
def inc_havlak_lnf(x, y, succ, pred, dfs_tree, dfs_int, loopcounts, loopheaders, looptypes, loopentries):
  def find_loop_head(x, head):
    xs = x
    while loopheaders[xs] != 0 and not dfs.do_isAncestor(dfs_int, loopheaders[xs], head): xs = loopheaders[xs] #dfs_int[loopheaders[xt]][0] > dfs_int[yt][0]:
    return xs
  def loop_preds(x, head):
    xs = find_loop_head(x, head)
    worklist = {xs}
    for xt in set.union(pred[x], *(loopentries[xs][z] for z in loopentries[xs]) if xs in loopentries else set()):
      if xt == x or dfs.do_isBackEdge(dfs_tree, dfs_int, xt, x): continue
      xprime = find_loop_head(xt, head)
      if not dfs.do_isAncestor(dfs_int, head, xprime): continue
      if xprime != head: worklist.add(xprime)
    return worklist
  def loop_preds_actual(x, head):
    worklist = {}
    for z, zt in ({x: pred[x], **loopentries[x]} if x in loopentries else {x: pred[x]}).items():
      for xt in zt:
        if xt == z or dfs.do_isBackEdge(dfs_tree, dfs_int, xt, z): continue
        xprime = find_loop_head(xt, head)
        if xprime != head:
          if not xprime in worklist: worklist[xprime] = set()
          worklist[xprime].add((xt, z))
    return worklist
  def propogate_irreducible(head, v, w):
    #print("Propogate", head, v, w, loopentries)
    while head != 0 and not dfs.do_isAncestor(dfs_int, head, w):
      if looptypes[head] != IRREDUCIBLE:
        if looptypes[head] != NONHEADER: loopcounts[1 if looptypes[head] == REDUCIBLE else 0] -= 1
        looptypes[head] = IRREDUCIBLE
        loopcounts[2] += 1
      if not head in loopentries: loopentries[head] = dict()
      if not v in loopentries[head]: loopentries[head][v] = set()
      if w in loopentries[head][v]: return
      loopentries[head][v].add(w)
      if v in loopentries:
        for e in loopentries[v]:
          preds = {f for f in loopentries[v][e] if not dfs.do_isAncestor(dfs_int, head, f)}
          if len(preds) != 0:
            if not e in loopentries[head]: loopentries[head][e] = set()
            loopentries[head][e] |= preds
      head = loopheaders[head]
    return head
  def reparent_irreducibles(top):
    def loop_preds_actual(x, head):
      worklist = {}
      for z, zt in ({x: pred[x], **loopentries[x]} if x in loopentries else {x: pred[x]}).items():
        for xt in zt:
          if xt == z or dfs.do_isBackEdge(dfs_tree, dfs_int, xt, z): continue
          xprime = find_loop_head_partial(xt, head)
          #print(x, head, z, xt, xprime)
          if xprime != head:
            if not xprime in worklist: worklist[xprime] = set()
            worklist[xprime].add((xt, z))
      return worklist
    def find_loop_head_partial(x, head):
      xs = x
      while loopheaders[xs] != 0 and not dfs.do_isAncestor(dfs_int, loopheaders[xs], head):
        if loopheaders[xs] in corrected and not xs in loopbody: break
        xs = loopheaders[xs]
      return xs
    #nonlocal x, y
    #print(x, y, top, loopheaders, loopentries)
    allentries, worklists = set(), {}
    for head in sorted(dfs_tree.subTree(top), key=lambda v: dfs_int[v][0]):
      #if head in allentries: continue
      if head in loopentries:
        for v in loopentries[head]:
          t = {w for w in loopentries[head][v] if dfs.do_isAncestor(dfs_int, head, w)}
          if len(t) != 0:
            allentries |= {head} | t
          if dfs.do_isAncestor(dfs_int, head, v): continue
          lca = dfs_tree.lca(head, v)
          allentries |= {head, v} | dfs_tree.allAncestors(head, lca) | dfs_tree.allAncestors(v, lca)
      if loopheaders[head] != 0 and not dfs.do_isAncestor(dfs_int, loopheaders[head], head):
        lca = dfs_tree.lca(head, loopheaders[head])
        allentries |= {head, loopheaders[head]} | dfs_tree.allAncestors(head, lca) | dfs_tree.allAncestors(loopheaders[head], lca)
      #else:
        #worklist = {z for z in pred[head] if z != head and dfs.do_isBackEdge(dfs_tree, dfs_int, z, head)}
        #if looptypes[head] == REDUCIBLE or looptypes[head] == IRREDUCIBLE:
        #  if len(worklist) == 0:
        #    allentries.add(head)
        #    if head in loopentries:
        #      allentries |= {v for w in loopentries[head] for v in loopentries[head][w] if dfs.do_isAncestor(dfs_int, top, v)}
        #elif len(worklist) != 0: allentries.add(head)
    #print(top, allentries)
    for w in sorted(allentries, key=lambda v: dfs_int[v][0]):
      worklist = {z for z in pred[w] if z != w and dfs.do_isBackEdge(dfs_tree, dfs_int, z, w)}
      toploop = loopheaders[w]
      if toploop != 0: lca = dfs_tree.lca(w, toploop)
      while toploop != 0 and not dfs.do_isAncestor(dfs_int, toploop, lca): toploop = loopheaders[toploop]
      if toploop in allentries: toploop = loopheaders[toploop]
      loopheaders[w] = toploop
      if len(worklist) != 0:
        if looptypes[w] != REDUCIBLE:
          if looptypes[w] != NONHEADER: loopcounts[0 if looptypes[w] == SELF else 2] -= 1
          looptypes[w] = REDUCIBLE
          loopcounts[1] += 1
        worklists[w] = worklist
        if w in loopentries: del loopentries[w]
      elif looptypes[w] == REDUCIBLE or looptypes[w] == IRREDUCIBLE:
        loopcounts[1 if looptypes[w] == REDUCIBLE else 2] -= 1
        looptypes[w] = NONHEADER if not w in succ[w] else SELF; worklists[w] = worklist
        if w in succ[w]: loopcounts[0] += 1
        if w in loopentries: del loopentries[w]
    loopbody, corrected = set(), set()
    for w in sorted(worklists.keys(), key=lambda v: dfs_int[v][0], reverse=True):
      #if len(worklists[w]) == 0 and not loopheaders[w] in worklists: continue
      worklist = {find_loop_head_partial(z, w) for z in worklists[w]}
      while len(worklist) != 0:
        v = worklist.pop()
        loopheaders[v] = w
        if v in loopentries:
          loopentries[v] = {z: {q for q in pred[z] if not dfs.do_isAncestor(dfs_int, v, q)} for z, zt in loopentries[v].items() if dfs.do_isAncestor(dfs_int, v, z)}
        for yt, ypreds in loop_preds_actual(v, w).items():
          if not dfs.do_isAncestor(dfs_int, w, yt):
            for e, f in ypreds: propogate_irreducible(w, f, e)
          elif yt != w and not yt in loopbody: worklist.add(yt)
        loopbody.add(v)
      corrected.add(w)
  def havlak_reparent_irreducibles(top):
    toploopdict = {}
    for head in sorted(dfs_tree.subTree(top), key=lambda x: dfs_int[x][0]):
      if loopheaders[head] == 0: continue
      lca = dfs_tree.lca(head, loopheaders[head])
      if lca in toploopdict: continue
      if loopheaders[head] != 0 and not dfs.do_isAncestor(dfs_int, loopheaders[head], head):
        for x in dfs_tree.subTree(lca):
          if x in toploopdict: raise ValueError
          toploop = loopheaders[x]
          if toploop != 0: lca = dfs_tree.lca(x, toploop)
          while toploop != 0 and not dfs.do_isAncestor(dfs_int, toploop, lca): toploop = toploopdict[toploop] if toploop in toploopdict else loopheaders[toploop]
          #while toploop in allentries: toploop = loopheaders[toploop]
          toploopdict[x] = toploop
          loopheaders[x] = 0
          if x in loopentries: del loopentries[x]
    for w in sorted(toploopdict, key=lambda x: dfs_int[x][0], reverse=True):
      worklist = {find_loop_head(z, w) for z in pred[w] if z != w and dfs.do_isBackEdge(dfs_tree, dfs_int, z, w) and (loopheaders[z] == 0 or dfs.do_isAncestor(dfs_int, w, find_loop_head(z, w)))}
      if len(worklist) != 0:
        if looptypes[w] != REDUCIBLE:
          if looptypes[w] != NONHEADER: loopcounts[0 if looptypes[w] == SELF else 2] -= 1
          looptypes[w] = REDUCIBLE
          loopcounts[1] += 1
      else:
        loopcounts[1 if looptypes[w] == REDUCIBLE else 2] -= 1
        looptypes[w] = NONHEADER if not w in succ[w] else SELF
        if w in succ[w]: loopcounts[0] += 1
      while len(worklist) != 0:
        x = worklist.pop()
        loopheaders[x] = w
        for y, ypreds in loop_preds_actual(x, w).items():
          if not dfs.do_isAncestor(dfs_int, w, y):
            for e, f in ypreds: propogate_irreducible(w, f, e)
          elif y != w and loopheaders[y] != w: worklist.add(y)
    for w in toploopdict:
      if loopheaders[w] == 0: loopheaders[w] = toploopdict[w]
  if loopcounts[2] == 0:
    try:
      do_inc_reducible_tarjan_lnf(x, y, pred, dfs_tree, dfs_int, loopcounts, loopheaders, looptypes)
      return
    except ValueError: pass
  if x == y:
    if looptypes[x] == NONHEADER: looptypes[x] = SELF; loopcounts[0] += 1
    return
  if (dfs.do_isForwardEdge(dfs_tree, dfs_int, x, y) or dfs.do_isCrossEdge(dfs_int, x, y)) and loopheaders[y] == 0: return #forward edges are trivial case
  if dfs.do_isForwardEdge(dfs_tree, dfs_int, x, y) and loopheaders[y] != 0:
    propogate_irreducible(loopheaders[y], y, x)
    return
  if dfs.do_isBackEdge(dfs_tree, dfs_int, x, y):
    head, worklist = y, loop_preds(x, y)
  elif dfs.do_isCrossEdge(dfs_int, x, y) and loopheaders[y] != 0:
    #print("Cross Edge", x, y, loopheaders[y])
    head = propogate_irreducible(loopheaders[y], y, x)
    if head == 0: return
    worklist = loop_preds(x, head)
  elif dfs_tree.pred[y] == x:
    #print(x, y)
    #o = loopheaders.copy(), looptypes.copy(), loopentries.copy()
    #havlak_reparent_irreducibles(y)
    #q = loopheaders, looptypes, loopentries
    #loopheaders, looptypes, loopentries = o
    #print(x, y, loopheaders, looptypes, loopentries)
    reparent_irreducibles(y)
    #if (loopheaders, looptypes, loopentries) != q:
    #  loopheaders, looptypes, loopentries = q
    #  print(o, q)
    #  return
    #term = dfs_tree.lca(x, y)
    head = x
    while not head is None and head != 0:
      b = {find_loop_head(z, head) for z in pred[head] if z != head and dfs.do_isBackEdge(dfs_tree, dfs_int, z, head) and (loopheaders[z] == 0 or dfs.do_isAncestor(dfs_int, head, find_loop_head(z, head)))}
      #print(head, b, pred[head], {find_loop_head(z, head) for z in pred[head] if dfs.do_isBackEdge(dfs_tree, dfs_int, z, head) and z != head})
      if len(b) != 0:
        worklist = b
        break
      head = dfs_tree.pred[head]
    if head is None or head == 0: return
    h = head
    while not h is None:
      if h in loopentries:
        #print(head, h, loopentries[h])
        #loopentries[h] -= {v} | (loopentries[v] if v in loopentries else set())
        #loopentries[h] = {e: set() for e in loopentries[h] if any(not dfs.do_isAncestor(dfs_int, h, f) for f in pred[e] if f != e and not dfs.do_isBackEdge(dfs_tree, dfs_int, f, e))}
        loopentries[h] = {e: f for e, f in ((e, {f for f in loopentries[h][e] if not dfs.do_isAncestor(dfs_int, h, f)}) for e in loopentries[h]) if len(f) != 0}
        #for e in loopentries[h].copy():
        #  loopentries[h][e] = 
        #  if len(loopentries[h][e]) == 0: del loopentries[h][e]
        if len(loopentries[h]) == 0:
          del loopentries[h] #need to check for NONHEADER, SELF???
          looptypes[h] = REDUCIBLE; loopcounts[2] -= 1; loopcounts[1] += 1
      h = dfs_tree.pred[h] #if loopheaders[h] == 0 else loopheaders[h]
  #print(head, worklist, loopheaders[head], loopheaders, loopentries)
  while True:
    if looptypes[head] == NONHEADER or looptypes[head] == SELF:
      if looptypes[head] == SELF: loopcounts[0] -= 1
      looptypes[head] = REDUCIBLE
      loopcounts[1] += 1
    while len(worklist) != 0:
      v = worklist.pop()
      loopheaders[v] = head
      """
      if v in loopentries:
        for e in loopentries[v]:
          for f in loopentries[v][e]:
            if e != f and not dfs.do_isBackEdge(dfs_tree, dfs_int, f, e):
              propogate_irreducible(head, e, f)
      """
      for w, wpreds in loop_preds_actual(v, head).items():
        #print(head, v, w)
        if not dfs.do_isAncestor(dfs_int, head, w):
          for e, f in wpreds: propogate_irreducible(head, f, e)
        elif w != head: worklist.add(w) #and loopheaders[w] != head
    if dfs.do_isBackEdge(dfs_tree, dfs_int, x, y) or dfs.do_isCrossEdge(dfs_int, x, y):
      if loopheaders[head] == 0: break
      worklist = loop_preds(head, loopheaders[head])
      head = loopheaders[head]
    elif dfs_tree.pred[y] == x:
      head = dfs_tree.pred[head]
      while not head is None and head != 0:
        b = {find_loop_head(z, head) for z in pred[head] if z != head and dfs.do_isBackEdge(dfs_tree, dfs_int, z, head) and (loopheaders[z] == 0 or dfs.do_isAncestor(dfs_int, head, find_loop_head(z, head)))}
        if len(b) != 0:
          worklist = b
          break
        head = dfs_tree.pred[head]
      if head is None or head == 0: break
    else: break
    #print(head, worklist)
def do_dec_reducible_tarjan_lnf(x, y, is_forward_edge, pred, dfs_tree, dfs_int, loopcounts, loopheaders, looptypes):
  curloops = {}
  def find_loop_head(xs, head):
    if xs in curloops: return curloops[xs]
    checked = {xs}
    while loopheaders[xs] != 0 and not dfs.do_isAncestor(dfs_int, loopheaders[xs], head):
      xs = loopheaders[xs]
      checked.add(xs)
    for x in checked: curloops[x] = xs
    return xs
  if x == y:
    if looptypes[x] == SELF: looptypes[x] = NONHEADER; loopcounts[0] -= 1
    return
  if is_forward_edge or dfs.do_isBackCrossEdge(dfs_int, x, y) and loopheaders[y] == 0: return
  if loopheaders[x] == 0: return
  if dfs.do_isBackCrossEdge(dfs_int, x, y):
    head = loopheaders[y]
    while head != 0 and not dfs.do_isAncestor(dfs_int, head, x):
      head = loopheaders[head]
    if head == 0: return
    worklist = {find_loop_head(x, head)} # | {find_loop_head(z, head) for z in pred[x] if dfs.do_isBackEdge(dfs_tree, dfs_int, z, x) and z != x}
  elif y == loopheaders[x]: #back edge removed
    head, worklist = y, {x}
    #assert dfs.do_isBackEdge(dfs_tree, dfs_int, x, y)
  elif x == loopheaders[y]: #tree edge removed
    head, worklist = x, {y}
    #assert not dfs.do_isBackEdge(dfs_tree, dfs_int, x, y)
    #head = dfs_tree.lca(x, y)
    #worklist = {find_loop_head(x, head)}
  else: #tree or back edge removed
    parentx, s = [], x #compute nearest common ancestor
    while s != 0: parentx.append(s); s = loopheaders[s]
    head = y
    while head != 0 and not head in parentx: head = loopheaders[head]
    if head == 0: return
    worklist = {find_loop_head(x, head)}
  term = loopheaders[dfs_tree.lca(x, y)]
  wl = {v for v in (find_loop_head(z, head) for z in pred[head] if z != head and dfs.do_isBackEdge(dfs_tree, dfs_int, z, head) and z != head) if loopheaders[v] == head}
  if len(wl) == 0 and (looptypes[head] == REDUCIBLE or looptypes[head] == IRREDUCIBLE):
    loopcounts[1] -= 1
    looptypes[head] = SELF if head in pred[head] else NONHEADER
    if head in pred[head]: loopcounts[0] += 1
  newhead = head
  loopbody = set()
  #print(head, worklist, wl)
  while True: #must recompute reachability
    if all(any(dfs.do_isAncestor(dfs_int, z, w) for w in wl) for z in worklist): break #reachability shortcut for some cases where cross edges are not involved
    #either worklist is a cross edge or no longer reaches a loop back edge removing it from the loop
    #one idea is to try to use the DFS tree and minimize graph checks
    #a cross edge still reaches a loop back edge if: any of its DFS tree children reaches a loop back edge or one of its successor cross edges does
    while len(wl) != 0:
      v = wl.pop()
      loopheaders[v] = newhead
      loopbody.add(v)
      if v in worklist: worklist.remove(v)
      for w in pred[v]:
        if w == v or dfs.do_isBackEdge(dfs_tree, dfs_int, w, v): continue
        wprime = find_loop_head(w, head)
        if (loopheaders[wprime] == head or loopheaders[wprime] == newhead) and not wprime in loopbody: wl.add(wprime)
    newhead = loopheaders[newhead]
    if newhead == 0 or len(worklist) == 0: break
    wl = {v for v in (find_loop_head(z, head) for z in pred[newhead] if z != newhead and dfs.do_isBackEdge(dfs_tree, dfs_int, z, newhead)) if (loopheaders[v] == head or loopheaders[v] == newhead) and not v in loopbody}
  while len(worklist) != 0:
    v = worklist.pop()
    loopheaders[v] = newhead
    for w in pred[v]:
      if w == v or dfs.do_isBackEdge(dfs_tree, dfs_int, w, v): continue
      wprime = find_loop_head(w, head)
      if loopheaders[wprime] == head and not wprime in loopbody: worklist.add(wprime)

def dec_havlak_lnf(x, y, is_forward_edge, succ, pred, dfs_tree, dfs_int, loopcounts, loopheaders, looptypes, loopentries):
  def find_loop_head(x, head):
    xs = x
    while loopheaders[xs] != 0 and not dfs.do_isAncestor(dfs_int, loopheaders[xs], head): xs = loopheaders[xs]
    return xs
  def loop_preds(x, head):
    xs = find_loop_head(x, head)
    worklist = {xs}
    for xt in set.union(pred[x], *(loopentries[xs][z] for z in loopentries[xs]) if xs in loopentries else set()):
      if xt == x or dfs.do_isBackEdge(dfs_tree, dfs_int, xt, x): continue
      xprime = find_loop_head(xt, head)
      if not dfs.do_isAncestor(dfs_int, head, xprime): continue
      if xprime != head: worklist.add(xprime)
    return worklist
  def loop_preds_actual(x, head, oldhead, loopbody):
    worklist = {}
    for z, zt in ({x: pred[x], **loopentries[x]} if x in loopentries else {x: pred[x]}).items():
      if (z != x and head != oldhead or x == oldhead) and head != 0 and not find_loop_head(z, oldhead) in loopbody: continue
      for xt in zt:
        if xt == z or dfs.do_isBackEdge(dfs_tree, dfs_int, xt, z): continue
        xprime = find_loop_head(xt, oldhead)
        if xprime in loopbody and head == 0: continue
        if xprime in loopbody: xprime = find_loop_head(xprime, head)
        #print(x, head, oldhead, z, xt, xprime)
        if xprime != head:
          if not xprime in worklist: worklist[xprime] = set()
          worklist[xprime].add(z)
    return worklist
  def unpropogate_irreducible(head, v, w, propogate=True):
    #print("Propogate", head, v, w, loopentries)
    #print(head, v, w, loopheaders)
    while head != 0 and head in loopentries and (not propogate or loopheaders[find_loop_head(v, head)] != head): # and (w == 0 or not dfs.do_isAncestor(dfs_int, head, w)):
      #print(head, v, w)
      if v in loopentries[head]:
        if w in loopentries[head][v]:
          loopentries[head][v].remove(w)
        if len(loopentries[head][v]) == 0: del loopentries[head][v]
      if propogate and v in loopentries:
        for e in loopentries[v]:
          #if all(dfs.do_isAncestor(dfs_int, head, f) for f in pred[e] if f != e and not dfs.do_isBackEdge(dfs_tree, dfs_int, f, e)):
          if e in loopentries[head]: del loopentries[head][e]
      if len(loopentries[head]) == 0:
        del loopentries[head]
        if looptypes[head] == IRREDUCIBLE: looptypes[head] = REDUCIBLE; loopcounts[2] -= 1; loopcounts[1] += 1
      head = loopheaders[head]
    return head
  def propogate_irreducible(head, v, w):
    #print("Propogate", head, v, w, loopentries)
    while head != 0 and not dfs.do_isAncestor(dfs_int, head, w):
      if looptypes[head] != IRREDUCIBLE:
        if looptypes[head] != NONHEADER: loopcounts[1 if looptypes[head] == REDUCIBLE else 0] -= 1
        looptypes[head] = IRREDUCIBLE
        loopcounts[2] += 1
      if not head in loopentries: loopentries[head] = dict()
      if not v in loopentries[head]: loopentries[head][v] = set()
      if w in loopentries[head][v]: return
      loopentries[head][v].add(w)
      if v in loopentries:
        for e in loopentries[v]:
          preds = {f for f in loopentries[v][e] if not dfs.do_isAncestor(dfs_int, head, f)}
          if len(preds) != 0:
            if not e in loopentries[head]: loopentries[head][e] = set()
            loopentries[head][e] |= preds
      head = loopheaders[head]
    return head
  def reparent_irreducibles(top, x):
    def loop_preds_actual(x, head):
      worklist = {}
      for z, zt in ({x: pred[x], **loopentries[x]} if x in loopentries else {x: pred[x]}).items():
        for xt in zt:
          if xt == z or dfs.do_isBackEdge(dfs_tree, dfs_int, xt, z): continue
          xprime = find_loop_head_partial(xt, head) if head != 0 else xt
          #print(x, head, z, xt, xprime)
          if xprime != head:
            if not xprime in worklist: worklist[xprime] = set()
            worklist[xprime].add((xt, z))
      return worklist
    def find_loop_head_partial(x, head):
      xs = x
      while loopheaders[xs] != 0 and not dfs.do_isAncestor(dfs_int, loopheaders[xs], head):
        if loopheaders[xs] in corrected and not xs in loopbody: break
        xs = loopheaders[xs]
      return xs
    #nonlocal x, y
    #print(x, y, top, loopheaders, loopentries)
    allentries, worklists = set(), {}
    for head in sorted(dfs_tree.subTree(top), key=lambda v: dfs_int[v][0]):
      #if head in allentries: continue
      if head in loopentries:
        for v in loopentries[head]:
          t = {w for w in loopentries[head][v] if dfs.do_isAncestor(dfs_int, head, w)}
          if len(t) != 0:
            allentries |= {head} | t
          if dfs.do_isAncestor(dfs_int, head, v): continue
          lca = dfs_tree.lca(head, v)
          allentries |= {head, v} | dfs_tree.allAncestors(head, lca) | dfs_tree.allAncestors(v, lca)
      if not dfs.do_isAncestor(dfs_int, loopheaders[head], head):
        lca = dfs_tree.lca(head, loopheaders[head])
        allentries |= {head, loopheaders[head]} | dfs_tree.allAncestors(head, lca) | dfs_tree.allAncestors(loopheaders[head], lca)
      #else:
        #worklist = {z for z in pred[head] if dfs.do_isBackEdge(dfs_tree, dfs_int, z, head) and z != head}
        #if looptypes[head] == REDUCIBLE or looptypes[head] == IRREDUCIBLE:
        #  if len(worklist) == 0:
        #    allentries.add(head)
        #    if head in loopentries:
        #      allentries |= {v for w in loopentries[head] for v in loopentries[head][w] if dfs.do_isAncestor(dfs_int, top, v)}
        #elif len(worklist) != 0: allentries.add(head)
    for w in sorted(allentries, key=lambda v: dfs_int[v][0]):
      worklist = {z for z in pred[w] if dfs.do_isBackEdge(dfs_tree, dfs_int, z, w) and z != w}
      toploop = loopheaders[w]
      if toploop != 0: lca = dfs_tree.lca(w, toploop)
      while toploop != 0 and not dfs.do_isAncestor(dfs_int, toploop, lca): toploop = loopheaders[toploop]
      if toploop in allentries: toploop = loopheaders[toploop]
      loopheaders[w] = toploop
      if len(worklist) != 0:
        if looptypes[w] != REDUCIBLE:
          if looptypes[w] != NONHEADER: loopcounts[0 if looptypes[w] == SELF else 2] -= 1
          looptypes[w] = REDUCIBLE
          loopcounts[1] += 1
        worklists[w] = worklist
        if w in loopentries: del loopentries[w]
      elif looptypes[w] == REDUCIBLE or looptypes[w] == IRREDUCIBLE:
        loopcounts[1 if looptypes[w] == REDUCIBLE else 2] -= 1
        looptypes[w] = NONHEADER if not w in succ[w] else SELF; worklists[w] = worklist
        if w in succ[w]: loopcounts[0] += 1
        if w in loopentries: del loopentries[w]
    if len(allentries) == 0: return
    loopbody, corrected = set(), set()
    for w in sorted(worklists.keys(), key=lambda v: dfs_int[v][0], reverse=True):
      #if len(worklists[w]) == 0 and not loopheaders[w] in worklists: continue
      worklist = {find_loop_head_partial(z, w) for z in worklists[w]}
      while len(worklist) != 0:
        v = worklist.pop()
        loopheaders[v] = w
        if v in loopentries:
          loopentries[v] = {z: {q for q in pred[z] if not dfs.do_isAncestor(dfs_int, v, q)} for z, zt in loopentries[v].items() if dfs.do_isAncestor(dfs_int, v, z)}
        for yt, ypreds in loop_preds_actual(v, w).items():
          if not dfs.do_isAncestor(dfs_int, w, yt):
            for e, f in ypreds: propogate_irreducible(w, f, e)
          elif yt != w and not yt in loopbody: worklist.add(yt)
        loopbody.add(v)
      corrected.add(w)
    #print(allentries, worklists, loopbody, corrected)
    worklist, notloopbody = {x}, set()
    while len(worklist) != 0:
      v = worklist.pop()
      if not v in loopbody and loopheaders[v] in corrected: #v != find_loop_head(x, top) and loopheaders[v] != top:
        o = loopheaders[v]
        while o in corrected: o = loopheaders[o]
        loopheaders[v] = o #top
        if o in loopentries:
          for e, f in [(e, f) for e in loopentries[o] if o in loopentries and e in loopentries[o] for f in loopentries[o][e]]:
            unpropogate_irreducible(o, e, f)
      notloopbody.add(v)
      for w, wpreds in loop_preds_actual(v, 0).items():
        if dfs.do_isAncestor(dfs_int, w, top): continue
        elif w != top and not w in notloopbody: worklist.add(w)
  def havlak_reparent_irreducibles(top):
    def loop_preds_actual(x, head):
      worklist = {}
      for z, zt in ({x: pred[x], **loopentries[x]} if x in loopentries else {x: pred[x]}).items():
        for xt in zt:
          if xt == x or dfs.do_isBackEdge(dfs_tree, dfs_int, xt, x): continue
          xprime = find_loop_head(xt, head)
          if xprime != head:
            if not xprime in worklist: worklist[xprime] = set()
            worklist[xprime].add((xt, z))
      return worklist
    allentries, toploopdict = set(), {}
    for head in sorted(dfs_tree.subTree(top), key=lambda x: dfs_int[x][0]):
      if loopheaders[head] == 0: continue
      lca = dfs_tree.lca(head, loopheaders[head])
      if lca in allentries: continue
      if loopheaders[head] != 0 and not dfs.do_isAncestor(dfs_int, loopheaders[head], head):
        allentries |= dfs_tree.subTree(lca)
    for x in allentries:
      toploop = loopheaders[x]
      while toploop in allentries: toploop = toploopdict[toploop] if toploop in toploopdict else loopheaders[toploop]
      if toploop != 0: toploop = dfs_tree.lca(x, toploop)
      toploopdict[x] = toploop
      loopheaders[x] = 0
      if x in loopentries: del loopentries[x]
    #print(toploopdict)
    for w in sorted(allentries, key=lambda x: dfs_int[x][0], reverse=True):
      worklist = {find_loop_head(z, w) for z in pred[w] if dfs.do_isBackEdge(dfs_tree, dfs_int, z, w) and z != w and (loopheaders[z] == 0 or dfs.do_isAncestor(w, find_loop_head(z, w)))}
      if len(worklist) != 0:
        if looptypes[w] != REDUCIBLE:
          if looptypes[w] != NONHEADER: loopcounts[0 if looptypes[w] == SELF else 2] -= 1
          looptypes[w] = REDUCIBLE
          loopcounts[1] += 1      
      else:
        loopcounts[1 if looptypes[w] == REDUCIBLE else 2] -= 1
        looptypes[w] = NONHEADER if not w in succ[w] else SELF
        if w in succ[w]: loopcounts[0] += 1
      while len(worklist) != 0:
        x = worklist.pop()
        loopheaders[x] = w
        for y, ypreds in loop_preds_actual(x, w).items():
          if not dfs.do_isAncestor(dfs_int, w, y):
            looptypes[w] = IRREDUCIBLE; loopcounts[1] -= 1; loopcounts[2] += 1
            for e, f in ypreds: propogate_irreducible(w, f, e)
          elif y != w and loopheaders[y] != w: worklist.add(y)
    for w in toploopdict:
      if loopheaders[w] == 0: loopheaders[w] = toploopdict[w]
  if loopcounts[2] == 0:
    do_dec_reducible_tarjan_lnf(x, y, is_forward_edge, pred, dfs_tree, dfs_int, loopcounts, loopheaders, looptypes)
    return
  #else:
  #  loopheaders, looptypes, loopentries = new_algo_loops(succ, dfs_int)
  #  return
  if x == y:
    if looptypes[x] == SELF: looptypes[x] = NONHEADER; loopcounts[0] -= 1
    return
  #if loopheaders[x] == 0 and looptypes[x] != IRREDUCIBLE: return
  #if isForwardEdge(x, y) and loopheaders[y] == 0 and looptypes[y] != REDUCIBLE and looptypes[y] != IRREDUCIBLE: return
  if (is_forward_edge or dfs.do_isBackCrossEdge(dfs_int, x, y)) and loopheaders[y] == 0: return
  #print("Delete", x, y)
  #elif loopheaders[x] == 0: return
  if is_forward_edge:
    head = loopheaders[y]
    while head != 0 and not dfs.do_isAncestor(dfs_int, head, x):
      #if all(dfs.do_isAncestor(dfs_int, head, f) for f in pred[y] if f != y and not dfs.do_isBackEdge(dfs_tree, dfs_int, f, y)):
      unpropogate_irreducible(head, y, x, False)
      head = loopheaders[head]
    return
  if dfs.do_isBackCrossEdge(dfs_int, x, y):
    head = loopheaders[y]
    while head != 0 and not dfs.do_isAncestor(dfs_int, head, x):
      #if all(dfs.do_isAncestor(dfs_int, head, f) for f in pred[y] if f != y and not dfs.do_isBackEdge(dfs_tree, dfs_int, f, y)):
      unpropogate_irreducible(head, y, x, False)
      head = loopheaders[head]
    if head == 0: return
    worklist = loop_preds(x, head)
  elif y == loopheaders[x]: #back edge removed
    head, worklist = y, {x}
    if x in loopentries:
      worklist |= {find_loop_head(p, head) for z in loopentries[x] for p in pred[z]}
  elif x == loopheaders[y] or not dfs.do_isBackEdge(dfs_tree, dfs_int, x, y): #tree or forward or cross edge removed
    #print("Tree edge", loopentries)
    #loopheaders, looptypes, loopentries = new_algo_loops(succ, dfs_int)
    #return
    head = dfs_tree.lca(x, y)
    reparent_irreducibles(head, x)
    #havlak_reparent_irreducibles(head)
    if head == 0: return
    worklist = {find_loop_head(x, head)}
    #print(x, loopheaders[y], head, worklist)
  else: #tree or back edge removed
    #if dfs.do_isForwardEdge(dfs_tree, dfs_int, x, y) or dfs.do_isForwardCrossEdge(dfs_int, x, y):
    #  loopheaders, looptypes, loopentries, _ = new_algo_loops(succ, dfs_int)
    #  return
    parentx, s = [], x #compute nearest common ancestor
    while s != 0: parentx.append(s); s = loopheaders[s]
    head = y
    while head != 0 and not head in parentx: head = loopheaders[head]
    #if head == 0: return
    #xt = x
    #while xt != 0 and loopheaders[xt] != head: xt = loopheaders[xt]
    #worklist = {xt}
    worklist = {find_loop_head(x, head)}
  wl = {v for v in (find_loop_head(z, head) for z in pred[head] if dfs.do_isBackEdge(dfs_tree, dfs_int, z, head) and z != head) if loopheaders[v] == head}
  if len(wl) == 0 and (looptypes[head] == REDUCIBLE or looptypes[head] == IRREDUCIBLE):
    loopcounts[1 if looptypes[head] == REDUCIBLE else 2] -= 1
    looptypes[head] = SELF if head in pred[head] else NONHEADER
    if head in pred[head]: loopcounts[0] += 1
  #print(head, wl, worklist)
  newhead = head
  loopbody = set()
  while True:
    while len(wl) != 0:
      v = wl.pop()
      if loopheaders[v] != newhead:
        o = loopheaders[v]
        loopheaders[v] = newhead
        #print(newhead, v, o)
        if dfs.do_isAncestor(dfs_int, newhead, v) and o in loopentries:
          for e, f in [(e, f) for e in loopentries[o] if o in loopentries and e in loopentries[o] for f in loopentries[o][e]]:
            unpropogate_irreducible(o, e, f)
        #unpropogate_irreducible(loopheaders[v], v, newhead)
        #if v in loopentries:
        #  for e in loopentries[v]:
        #    for f in loopentries[v][e]:
        #      unpropogate_irreducible(loopheaders[v], e, f)
      loopbody.add(v)
      if v in worklist: worklist.remove(v)
      for w, wpreds in loop_preds_actual(v, newhead, head, loopbody).items():
        if not dfs.do_isAncestor(dfs_int, newhead, w): continue
        elif not w in loopbody: wl.add(w)
    newhead = dfs_tree.pred[newhead] #loopheaders[newhead] if loopheaders[newhead] != 0 else dfs_tree.pred[newhead]
    if newhead is None or newhead == 0: newhead = 0; break
    wl = {v for v in (find_loop_head(z, head) if not find_loop_head(z, head) in loopbody else find_loop_head(z, newhead) for z in pred[newhead] if dfs.do_isBackEdge(dfs_tree, dfs_int, z, newhead) and z != newhead) if dfs.do_isAncestor(dfs_int, newhead, v) and not v in loopbody}
    #print(newhead, loopbody, wl, loopentries, list(find_loop_head(z, newhead) for z in pred[newhead] if dfs.do_isBackEdge(dfs_tree, dfs_int, z, newhead) and z != newhead))
  #print(loopbody)
  while len(worklist) != 0:
    v = worklist.pop()
    loopbody.add(v)
    o = loopheaders[v]
    loopheaders[v] = newhead
    #print(v, o)
    if o in loopentries:
      for e, f in [(e, f) for e in loopentries[o] if o in loopentries and e in loopentries[o] for f in loopentries[o][e]]:
        unpropogate_irreducible(o, e, f)
    for w, wpreds in loop_preds_actual(v, newhead, head, loopbody).items():
      if dfs.do_isAncestor(dfs_int, w, head): continue
      elif w != head and not w in loopbody: worklist.add(w)
def steensgaard_to_sgl(succ, pred, dfs_tree, dfs_int, dom_tree, steensgaard): #SGL finds more reducible loops, while Steensgaard finds nested irreducibles
  def reachUnder(header, worklist):
    loopBody = set()
    while len(worklist) != 0:
      y = worklist.pop()
      loopBody.add(y)
      for z in pred[y] | (set.union(*(pred[z] for z in steensgaard[2][y])) if y in steensgaard[2] else set()):
        zprime = findLoopParent(z, header)
        if not dfs.do_isAncestor(dfs_int, header, zprime): pass
        elif zprime != header and not zprime in loopBody and not zprime in worklist:
          worklist.add(zprime)
    return loopBody
  def findLoopParent(z, x):
    while steensgaard[0][z] != 0 and dom_tree.level[steensgaard[0][z]] > dom_tree.level[x]:
      z = steensgaard[0][z]
    return z
  def needFlatten(x): return steensgaard[1][x] == IRREDUCIBLE and (steensgaard[0][x] == 0 or dom_tree.level[steensgaard[0][x]] < dom_tree.level[x])
  sgl = steensgaard[0].copy(), steensgaard[1].copy(), {}
  levels = dom_tree.treeByLevel()
  for i in range(len(levels) - 1, -1, -1):
    for x in levels[i]:
      checkx = steensgaard[0][x]
      while checkx != 0 and not needFlatten(checkx) and (steensgaard[0][checkx] == 0 or dom_tree.level[steensgaard[0][checkx]] >= dom_tree.level[checkx]):
        checkx = steensgaard[0][checkx]
      if steensgaard[1][x] == IRREDUCIBLE or checkx != 0 and needFlatten(checkx):
        bjEdges = set()
        for w in {findLoopParent(z, x) for z in pred[x]}:
          if w != x and dominators.isBackJEdge(dom_tree, w, x): bjEdges.add(w)
        if len(bjEdges) != 0:
          r = reachUnder(x, bjEdges)
          for z in r:
            zprime = z
            while zprime != 0:
              if steensgaard[0][zprime] in sgl[2]:
                if z in sgl[2][steensgaard[0][zprime]]: sgl[2][steensgaard[0][zprime]].remove(z); break
              zprime = steensgaard[0][zprime]
            sgl[0][z] = x
            if any(y != z and dfs.do_isBackEdge(dfs_tree, dfs_int, y, z) for y in pred[z]):
              if not z in sgl[2]: sgl[1][z] = REDUCIBLE
            else:
              sgl[1][z] = NONHEADER if not z in succ[z] else SELF
      if checkx != 0 and needFlatten(checkx):
        sgl[0][x] = 0
        sgl[1][x] = IRREDUCIBLE
        if not checkx in sgl[2]: sgl[2][checkx] = set()
        sgl[2][checkx].add(x)
  return sgl
def check_havlak(succ, dfs_int, loopcounts, loopheaders, looptypes, loopentries):
  new_loops = adapt_offline_havlak(new_algo_loops(succ, dfs_int))
  if new_loops != (loopcounts, loopheaders, looptypes, loopentries):
    #graphviz_dot()
    raise ValueError(succ, loopcounts, loopheaders, looptypes, loopentries, new_loops)
def check_loops(virtual_root, succ, pred, dfs_tree, dfs_int, dfs_revint, dom_tree, loopheaders, looptypes, loopentries):
  acyclic, acyclic_no_self_loops = is_acyclic(succ, dfs_tree, dfs_int), is_acyclic_no_self_loops(succ, dfs_tree, dfs_int)
  lin_loops = linear_havlak_loops(pred, dfs_tree, dfs_int, dfs_revint)
  hl = havlak_loops(pred, dfs_tree, dfs_int, dfs_revint)
  if hl != lin_loops:
    raise ValueError
  new_loops = new_algo_loops(succ, dfs_int)
  if lin_loops != new_loops[:2]: raise ValueError(lin_loops, new_loops)
  #new_loops = (*new_loops[0:2], {x: set(new_loops[2][x].keys()) for x in new_loops[2]})
  #if new_loops != (loopheaders, looptypes, {x: set(loopentries[x].keys()) for x in loopentries}):
  if new_loops != (loopheaders, looptypes, loopentries):
    #graphviz_dot()
    raise ValueError(succ, loopheaders, looptypes, loopentries, new_loops) #hl)
  rlh_loops = reduced_havlak_loops(pred, dfs_tree, dfs_int, dfs_revint)
  htorh = havlak_to_reduced_havlak(virtual_root, succ, dfs_int, dfs_revint, dom_tree)
  if rlh_loops != htorh:
    #graphviz_dot()
    raise ValueError(new_loops, rlh_loops, htorh)
  sglloops = sreedhar_gao_lee_loops(pred, dfs_tree, dfs_int, dom_tree)
  steensgaard = steensgaard_loops(virtual_root, pred, dfs_int)
  if do_tarjan_is_reducible(pred, dfs_tree, dfs_int, dfs_revint):
    if sglloops[0] != loopheaders or sglloops[1] != looptypes:
      #graphviz_dot()
      raise ValueError(sglloops, loopheaders, looptypes)
    if steensgaard[0] != loopheaders or steensgaard[1] != looptypes:
      #graphviz_dot()
      raise ValueError(steensgaard, loopheaders, looptypes)
  msglloops = modified_sreedhar_gao_lee_loops(pred, dfs_tree, dfs_int, dom_tree)
  if sglloops != msglloops:
    #graphviz_dot()
    raise ValueError(sglloops, msglloops)
  stosgl = steensgaard_to_sgl(succ, pred, dfs_tree, dfs_int, dom_tree, steensgaard)
  if sglloops[0] != stosgl[0] or sglloops[1] != stosgl[1]:
    #graphviz_dot()
    raise ValueError(steensgaard, stosgl, sglloops)
def is_acyclic(succ, dfs_tree, dfs_int):
  return not any(dfs.do_isBackEdge(dfs_tree, dfs_int, x, y) for x in succ for y in succ[x])
def is_acyclic_no_self_loops(succ, dfs_tree, dfs_int):
  return not any(dfs.do_isBackEdge(dfs_tree, dfs_int, x, y) for x in succ for y in succ[x] if x != y)
def do_tarjan_is_reducible(pred, dfs_tree, dfs_int, dfs_revint):
  lp = graph.DisjointSet(pred.keys())
  for widx in reversed(dfs_revint):
    w = dfs_revint[widx]
    if w == 0 or dfs_int[w][1] == widx: continue
    p = set()
    worklist = {lp.find(v) for v in pred[w] if dfs.do_isBackEdge(dfs_tree, dfs_int, v, w)}
    if w in worklist: worklist.remove(w)
    while len(worklist) != 0:
      x = worklist.pop()
      p.add(x)
      for y in pred[x]:
        if y == x or dfs.do_isBackEdge(dfs_tree, dfs_int, y, x): continue
        yprime = lp.find(y)
        if not dfs.do_isAncestor(dfs_int, w, yprime):
          #assert any(x == IRREDUCIBLE for x in havlak_loops(pred, dfs_tree, dfs_int, dfs_revint)[1].values())
          return False
        if not yprime in p and yprime != w: worklist.add(yprime)
    for x in p: lp.union(w, x, True)
  return True
def do_tarjan_loops(pred, dfs_tree, dfs_int, dfs_revint):
  #do_tarjan_is_reducible(pred, dfs_tree, dfs_int, dfs_revint) == True
  loopParent, type = {x: 0 for x in pred}, {x: NONHEADER for x in pred}
  loopParent[0] = 0; type[0] = NONHEADER
  lp = graph.DisjointSet(pred.keys())
  for widx in reversed(dfs_revint):
    w = dfs_revint[widx]
    if w == 0 or dfs_int[w][1] == widx: continue
    loopBody = set()
    worklist = {lp.find(y) for y in pred[w] if dfs.do_isBackEdge(dfs_tree, dfs_int, y, w)}
    if w in worklist: worklist.remove(w); type[w] = SELF
    if len(worklist) != 0: type[w] = REDUCIBLE
    while len(worklist) != 0:
      x = worklist.pop()
      loopBody.add(x)
      for z in pred[x]:
        if z == x or dfs.do_isBackEdge(dfs_tree, dfs_int, z, x): continue
        zprime = lp.find(z)
        if not dfs.do_isAncestor(dfs_int, w, zprime): raise ValueError("Irreducible")
        if not zprime in loopBody and zprime != w and not zprime in worklist:
          worklist.add(zprime)
    for z in loopBody:
      loopParent[z] = w
      lp.union(w, z, True)
  return loopParent, type
def havlak_loops(pred, dfs_tree, dfs_int, dfs_revint):
  header, type = {x: 0 for x in pred}, {x: NONHEADER for x in pred}
  header[0] = 0; type[0] = NONHEADER
  djs = graph.DisjointSet(pred)
  nonBackPreds = {x: set(filter(lambda y: not dfs.do_isBackEdge(dfs_tree, dfs_int, y, x), pred[x])) for x in pred}
  for widx in reversed(dfs_revint):
    w = dfs_revint[widx]
    if w == 0 or dfs_int[w][1] == widx: continue
    p = set()
    for v in pred[w]:
      if not dfs.do_isBackEdge(dfs_tree, dfs_int, v, w): continue
      if v != w: p.add(djs.find(v))
      else: type[w] = SELF
    worklist = p.copy()
    if len(p) != 0: type[w] = REDUCIBLE
    while len(worklist) != 0:
      x = worklist.pop()
      for y in nonBackPreds[x]:
        yprime = djs.find(y)
        if not dfs.do_isAncestor(dfs_int, w, yprime):
          type[w] = IRREDUCIBLE
          nonBackPreds[w].add(yprime)
        elif not yprime in p and yprime != w:
          p.add(yprime); worklist.add(yprime)
    for x in p:
      header[x] = w
      djs.union(w, x, True)
  return header, type #, {x: {y for y in nonBackPreds[x] if not y in pred[x]} for x in nonBackPreds if not nonBackPreds[x].issubset(pred[x])}
def havlak_fix_loops(pred, dfs_tree, dfs_int, dfs_revint): #insert new header nodes so when reducible and irreducible loops share a header, the reducible loop will be identified
  redBackIn, otherIn = {}, {}
  added_nodes, added_edges, deleted_edges = set(), set(), set()
  wprime = len(pred) + 1
  for widx in dfs_revint:
    w = dfs_revint[widx]
    if w == 0 or dfs_int[w][1] == widx: continue
    redBackIn[w] = set(); otherIn[w] = set()
    for v in pred[w]:
      if dfs.do_isBackEdge(dfs_tree, dfs_int, v, w): redBackIn[w].add(v)
      else: otherIn[w].add(v)
    if len(redBackIn[w]) != 0 and len(otherIn[w]) > 1:
      added_nodes.add(wprime)
      added_edges.add((wprime, w))
      for v in otherIn[w]:
        added_edges.add((v, wprime))
        deleted_edges.add((v, w))
      wprime += 1
  return added_nodes, added_edges, deleted_edges
def refined_havlak_loops(pred, dfs_tree, dfs_int, dfs_revint):
  header, type = havlak_loops(pred, dfs_tree, dfs_int, dfs_revint)
  for x in header:
    if type[x] == IRREDUCIBLE and any(dfs.do_isBackEdge(dfs_tree, dfs_int, y, x) for y in pred[x]):
      pass
def lin_havlak_loops(pred, dfs_tree, dfs_int, dfs_revint):
  #discovered, exitdisc, parents = dfs_interval(graph, root)
  #revdisc = {y: x for x, y in discovered.items()}
  #def isAncestor(x, y): return discovered[x] <= discovered[y] and discovered[y] <= exitdisc[x]
  loopParent, type = {x: 0 for x in pred}, {x: NONHEADER for x in pred}
  loopParent[0] = 0; type[0] = NONHEADER
  crossFwdEdges = {x: set() for x in pred}
  lp, rlh = graph.DisjointSet(pred), graph.DisjointSet(pred)
  preds = {x: set(filter(lambda y: dfs.do_isBackEdge(dfs_tree, dfs_int, y, x), pred[x])) for x in pred}
  for y in pred:
    for x in pred[y]:
      if dfs.do_isCrossEdge(dfs_int, x, y) or dfs.do_isAncestor(dfs_int, x, y):
        crossFwdEdges[dfs_tree.lca(x, y)].add((x, y))
  for widx in reversed(dfs_revint):
    w = dfs_revint[widx]
    if w == 0 or dfs_int[w][1] == widx: continue
    for x, y in crossFwdEdges[w]:
      preds[lp.find(y)].add(lp.find(x))
      t = loopParent[y]          
      while t != 0:
        u = rlh.find(t)
        type[u] = IRREDUCIBLE #mark u as irreducible loop header
        #print(w, x, y, t, u, loopParent[u])
        t = loopParent[u]
        if t != 0: rlh.union(t, u, True)
    loopBody = set()
    worklist = {lp.find(y) for y in preds[w] if dfs.do_isBackEdge(dfs_tree, dfs_int, y, w)} - {w}
    if w in preds[w]: type[w] = SELF
    if len(worklist) != 0: type[w] = REDUCIBLE
    while len(worklist) != 0:
      x = worklist.pop()
      loopBody.add(x)
      for z in preds[x]:
        if dfs.do_isBackEdge(dfs_tree, dfs_int, z, x): continue
        zprime = lp.find(z)
        if not zprime in loopBody and zprime != w and not zprime in worklist:
          worklist.add(zprime)
    for z in loopBody:
      loopParent[z] = w
      lp.union(w, z, True)
  return loopParent, type, rlh
def linear_havlak_loops(pred, dfs_tree, dfs_int, dfs_revint):
  return lin_havlak_loops(pred, dfs_tree, dfs_int, dfs_revint)[:2]
def reduced_havlak_loops(pred, dfs_tree, dfs_int, dfs_revint):
  #note Ramalingam omits the details in the paper for the algorithm due to lack of space
  #its identical to the information in the rlh disjoint set, however this only joins irreducible loops with a common entry
  #theoretically the minimal forest would also join irreducible loops which do not dominate each other
  loopParent, type, rlh = lin_havlak_loops(pred, dfs_tree, dfs_int, dfs_revint)
  #print(str(rlh))
  loopHeads = {}
  for x in loopParent:
    if x == 0: continue
    xprime = rlh.find(x)
    if xprime != x:
      if not xprime in loopHeads: loopHeads[xprime] = set()
      loopHeads[xprime].add(x)
    if loopParent[x] != 0:
      lp = rlh.find(loopParent[x])
      if lp != loopParent[x]: loopParent[x] = lp
  return loopParent, type, loopHeads
def havlak_to_reduced_havlak(virtual_root, succ, dfs_int, dfs_revint, dom_tree): #problem of finding only merges with common entry vertex without building the LCA forward cross edges
  #loopParent, type = linear_havlak_loops(pred, dfs_tree, dfs_int, dfs_revint)
  loopParent, type, entries = new_algo_loops(succ, dfs_int)
  loopHeads = {}
  rlh = graph.DisjointSet(succ)
  for widx in dfs_revint:
    x = dfs_revint[widx]
    if dfs_int[x][1] == widx: continue
    if type[x] == IRREDUCIBLE: #only irreducible loops who have parent-child relationship have the Undom property and a common entry vertex
      #if not x in loopHeads: loopHeads[x] = set()
      #loopHeads[x].add(x)        
      if loopParent[x] != 0 and type[loopParent[x]] == IRREDUCIBLE and not dom_tree.isAncestor(x, loopParent[x]) and len(set(entries[x]).intersection(entries[loopParent[x]])) != 0:
        lp = rlh.find(loopParent[x])
        if not lp in loopHeads: loopHeads[lp] = set()
        loopHeads[lp] |= {x} | (set() if not x in loopHeads else loopHeads[x])
        #print(x, lp, loopParent[x])
        rlh.union(lp, x, True)
        if x in loopHeads: del loopHeads[x]
        #x = loopParent[x]
    if loopParent[x] != 0:
      lp = rlh.find(loopParent[x])
      if lp != loopParent[x]: loopParent[x] = lp
  return loopParent, type, loopHeads
def new_algo_loops(succ, dfs_int):
  def tag_lhead(b, h):
    if b == h or h == 0: return
    cur1, cur2 = b, h
    while traversed[cur1][1] != 0:
      ih = traversed[cur1][1]
      if ih == cur2: return
      if traversed[ih][0] < traversed[cur2][0]:
        traversed[cur1][1] = cur2; cur1 = cur2; cur2 = ih
      else: cur1 = ih
    traversed[cur1][1] = cur2
  traversed = {0: [0, 0, NONHEADER]}
  reentryEdges = {}
  def trav_loops_dfs(b0, dfsp_pos):
    traversed[b0] = [dfsp_pos, 0, NONHEADER]
    for b in sorted(succ[b0], key=lambda x: dfs_int[x][0]):
      if not b in traversed:
        nh = trav_loops_dfs(b, dfsp_pos + 1)
        tag_lhead(b0, nh)
      else:
        if traversed[b][0] > 0: #mark b as loop header
          tag_lhead(b0, b)
          if b == b0 and traversed[b][2] == NONHEADER: traversed[b][2] = SELF
          elif traversed[b][2] == NONHEADER or traversed[b][2] == SELF: traversed[b][2] = REDUCIBLE
        elif traversed[b][1] == 0: pass            
        else:
          h = traversed[b][1]
          if traversed[h][0] > 0: tag_lhead(b0, h); traversed[h][2] = REDUCIBLE
          else:
            if not h in reentryEdges: reentryEdges[h] = {}
            if not b in reentryEdges[h]: reentryEdges[h][b] = set()
            reentryEdges[h][b].add(b0) #mark b and (b0, b) as re-entry
            traversed[h][2] = IRREDUCIBLE #mark loop of h as irreducible
            while traversed[h][1] != 0:
              h = traversed[h][1]
              if traversed[h][0] > 0: tag_lhead(b0, h); traversed[h][2] = REDUCIBLE; break
              traversed[h][2] = IRREDUCIBLE #mark loop of h as irreducible
              if not h in reentryEdges: reentryEdges[h] = {}
              if not b in reentryEdges[h]: reentryEdges[h][b] = set()
              reentryEdges[h][b].add(b0) #mark b and (b0, b) as re-entry
    traversed[b0][0] = 0
    return traversed[b0][1]
  for source in sorted(succ, key=lambda x: dfs_int[x][0]):
    if source != 0 and not source in traversed: trav_loops_dfs(source, 1)
  return {x: traversed[x][1] for x in traversed}, {x: traversed[x][2] for x in traversed}, reentryEdges #, loopHeaded(0)

def sreedhar_gao_lee_loops(pred, dfs_tree, dfs_int, dom_tree):
  def reachUnder(header, worklist):
    loopBody = set()
    while len(worklist) != 0:
      y = worklist.pop()
      loopBody.add(y)
      for z in pred[y] | (set.union(*(pred[z] for z in loopHeaders[y])) if y in loopHeaders else set()):
        zprime = lp.find(z)
        if not dfs.do_isAncestor(dfs_int, header, zprime): pass
        elif zprime != header and not zprime in loopBody and not zprime in worklist:
          worklist.add(zprime)
    return loopBody
  levels = dom_tree.treeByLevel()
  lp = graph.DisjointSet(pred)
  loopParent, loopType, loopHeaders = {x: 0 for x in pred}, {x: NONHEADER for x in pred}, {}
  for i in range(len(levels) - 1, -1, -1):
    irreducible = False
    for n in levels[i]:
      bjEdges = set()
      for m in {lp.find(z) for z in pred[n]}:
        if m == n: loopType[n] = SELF
        elif dominators.isCrossJEdge(dom_tree, m, n) and dfs.do_isBackEdge(dfs_tree, dfs_int, m, n): irreducible = True
        elif dominators.isBackJEdge(dom_tree, m, n): bjEdges.add(m)
      if len(bjEdges) != 0:
        r = reachUnder(n, bjEdges)
        loopType[n] = REDUCIBLE
        for x in r: loopParent[x] = n; lp.union(n, x, True)
    if irreducible:
      subgraph = {}
      for l in range(i, len(levels)):
        for n in levels[l]:
          nprime = lp.find(n)
          subgraph[nprime] = {lp.find(z) for z in pred[nprime] | (set.union(*(pred[z] for z in loopHeaders[nprime])) if nprime in loopHeaders else set())}
      subgraph = {n: list(filter(lambda x: n != x and x in subgraph, subgraph[n])) for n in subgraph}
      for x in sccreach.tarjan_scc(subgraph):
        if len(x) == 1: continue
        header = min(x, key=lambda z: dfs_int[z][0])
        loopType[header] = IRREDUCIBLE
        loopHeaders[header] = set(filter(lambda z: z != header, x))
        for z in loopHeaders[header]:
          loopType[z] = IRREDUCIBLE
          lp.union(header, z, True)
  return loopParent, loopType, loopHeaders
def modified_sreedhar_gao_lee_loops(pred, dfs_tree, dfs_int, dom_tree):
  def findLoop(header, worklist):
    if len(worklist) != 0:
      loopType[header] = REDUCIBLE
      loopBody = set() #{header}
      while len(worklist) != 0:
        y = worklist.pop()
        loopBody.add(y)
        processed[y] = True
        for z in pred[y] | (loopEntries[y] if y in loopEntries else set()):
          zprime = lp.find(z)
          if not dfs.do_isAncestor(dfs_int, header, zprime):
            loopType[header] = IRREDUCIBLE
            if not header in loopEntries: loopEntries[header] = set()
            loopEntries[header].add(zprime)
          elif zprime != header and not zprime in loopBody and not zprime in worklist:
            worklist.add(zprime)
      if loopType[header] == IRREDUCIBLE: loopHeaders[header] = loopBody
      for z in loopBody: #collapse loopBody into loopRep
        if loopType[header] == IRREDUCIBLE: loopType[z] = IRREDUCIBLE
        else: loopParent[z] = header
        lp.union(header, z, True)
  levels = dom_tree.treeByLevel()
  loopParent, loopType, processed = {x: 0 for x in pred}, {x: NONHEADER for x in pred}, {x: False for x in pred}
  loopHeaders, loopEntries = {}, {}
  lp = graph.DisjointSet(pred)
  for i in range(len(levels) - 1, -1, -1):
    for n in levels[i]:
      w = {lp.find(m) for m in pred[n] if dfs.do_isBackEdge(dfs_tree, dfs_int, m, n) and dom_tree.isAncestor(m, n)}
      if n in w: loopType[n] = SELF
      findLoop(n, w - {n})
    for n in sorted(levels[i], key=lambda x: dfs_int[x][0]):
      if not processed[n]:
        w = {lp.find(m) for m in pred[n] if dfs.do_isBackEdge(dfs_tree, dfs_int, m, n) and not dom_tree.isAncestor(m, n)}
        findLoop(n, w - {n})
  return loopParent, loopType, loopHeaders
def steensgaard_loops(virtual_root, pred, dfs_int):
  loopParent, loopType, loopEntries = {}, {}, {}
  def scc_loops(subg, parent):
    #print(subg, sccreach.tarjan_scc(subg))
    for scc in sccreach.tarjan_scc(subg):
      if len(scc) == 1:
        if scc[0] != parent:
          loopParent[scc[0]] = parent
          loopType[scc[0]] = SELF if scc[0] in subg[scc[0]] else NONHEADER
      else:
        entries = {}
        for x in scc:
          e = {z for z in subg[x] if not z in scc}
          if len(e) != 0: entries[x] = e
        #print(entries, scc)
        if len(entries) == 0:
          if virtual_root in scc: entries[virtual_root] = set()
          else:
            for x in scc:
              if x != parent:
                loopParent[x] = parent
                loopType[x] = SELF if x in subg[x] else NONHEADER
            continue
        if len(entries) != 1:
          header = min(entries, key=lambda z: dfs_int[z][0])
          #reduciblepart = {z for z in subg[header] if z in scc}
          loopParent[header] = parent
          loopType[header] = IRREDUCIBLE
          for x in entries:
            if x == header: continue
            loopParent[x] = virtual_root
            loopType[x] = IRREDUCIBLE
          loopEntries[header] = entries
        else:
          header = next(iter(entries))
          loopParent[header] = parent
          loopType[header] = REDUCIBLE
        nextgraph = {}
        #print(scc, entries)
        for x in scc:
          #if not x in entries:
          nextgraph[x] = {z for z in subg[x] if z in scc} if not x in entries else set() #if x != header else {z for z in subg[x] if z in scc and not dfs.do_isBackEdge(dfs_tree, dfs_int, z, x)} #if x != header else set()
        scc_loops(nextgraph, header)
  scc_loops(pred, 0)
  return loopParent, loopType, loopEntries

def modified_sreedhar_gao_lee_steensgaard_loops(graph, root): pass

def graphviz_dot_lnf(loopheaders, looptypes, loopentries, pre="l", is_latex=False):
  looptypenames = ["-", "R", "I", "S"]
  edges = ";".join(pre + str(loopheaders[x]) + "->" + pre + str(x) + (" [style=invis]" if loopheaders[x] == 0 else "") for x in loopheaders)
  lbls = ";".join(pre + str(x) + " [label=" + "\"" + str(x) + " [" + looptypenames[looptypes[x]] + "]" + (("\\noexpand" if is_latex else "") + "\\n" + str(loopentries[x]) if x in loopentries else "") + "\"" + "]" for x in loopheaders)
  return edges + ";" + pre + "0 [style=invis,label=\"\"];" + lbls

def test_tarjan_loops():
  #https://core.ac.uk/download/pdf/82032035.pdf
  #Testing Flow Graph Reducibility (1974)
  #R. Endre Tarjan
  gsucc = {1: [3, 2], 2: [6, 4, 8], 3: [7, 5], 4: [8], 5: [9, 11], 6: [10], 7: [11], 8: [10], 9: [11], 10: [2, 12], 11: [1, 12], 12: [1]}
  g = cfg.Digraph([1], [[3, 2], [6, 4, 8], [7, 5], [8], [9, 11], [10], [11], [10], [11], [2, 12], [1, 12], [1]])
  assert g.tarjan_is_reducible()
  correctdfsparents = {1: 0, 2: 1, 3: 1, 4: 2, 5: 3, 6: 2, 7: 3, 8: 4, 9: 5, 10: 6, 11: 7, 12: 11}
  correctdfspreorder = {1: 0, 3: 1, 7: 2, 11: 3, 12: 4, 5: 5, 9: 6, 2: 7, 6: 8, 10: 9, 4: 10, 8: 11}
  dfstest = dfs.dfs_interval(gsucc, 1)
  assert dfstest[0] == correctdfspreorder
  assert dfstest[2] == correctdfsparents
  #HIGHPT is the loopheaders with DFS pre order numbers instead of vertices
  correcthighpts = {0: 0, 1: 0, 2: 1, 3: 1, 4: 8, 5: 1, 6: 8, 7: 1, 8: 8, 9: 1, 10: 8, 11: 1, 12: 1}
  lnftypes = {0: 0, 1: 1, 2: 1, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0}
  tl = g.tarjan_loops()
  assert {x: 0 if y == 0 else dfstest[0][y]+1 for x, y in tl[0].items()} == correcthighpts
  assert tl[1] == lnftypes
  #SNUMBER is just a DFS ordering of the DFS tree effectively plus one
  correctsnumber = {x: y-1 for x, y in {1: 1, 2: 2, 3: 7, 4: 3, 5: 8, 6: 5, 7: 10, 8: 4, 9: 9, 10: 6, 11: 11, 12: 12}.items()}
  gsucc = {1: [2, 3], 2: [4, 6], 3: [5, 7], 4: [8], 5: [9], 6: [10], 7: [11], 8: [], 9: [], 10: [], 11: [12], 12: []}
  assert dfs.dfs_interval(gsucc, 1)[0] == correctsnumber
  
def test_sreedhar_gao_lee_loops():
  #http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.42.3972&rep=rep1&type=pdf
  #Identifying loops using DJ graphs (1995)
  #by Vugranam C. Sreedhar , Guang R. Gao , Yong-fong Lee , Yong-fong Leey
  g = cfg.Digraph([1], [[2, 6], [3], [4], [2, 5], [3, 6], []]) #reducible flow graph, paper has mistake in d->END edge direction
  lnf = ({1: 0, 2: 0, 3: 2, 4: 3, 5: 3, 6: 0}, {1: 0, 2: 1, 3: 1, 4: 0, 5: 0, 6: 0}, {})
  assert g.sreedhar_gao_lee_loops(1) == lnf
  g = cfg.Digraph([1], [[2, 3], [3], [2]]) #irreducible core
  lnf = ({1: 0, 2: 0, 3: 0}, {1: 0, 2: 2, 3: 2}, {2: {3}})
  assert g.sreedhar_gao_lee_loops(1) == lnf
  g = cfg.Digraph([1], [[2, 3], [3, 4], [2], [5, 6], [6], [3, 5]]) #irreducible graph with 2 irreducible loops
  correctdom = graph.Tree(1, pred_init=[0, 1, 1, 2, 4, 4])
  correctjsucc = {1: set(), 2: {3}, 3: {2}, 4: set(), 5: {6}, 6: {3, 5}}
  assert g.tarjan_dominators(1) == correctdom and g.doms[1][1] == correctjsucc
  lnf = ({1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}, {1: 0, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2}, {5: {6}, 2: {3, 4, 5}})
  assert g.sreedhar_gao_lee_loops(1) == lnf
  #graph = {1: [2, 10], 2: [3, 4], 3: [5], 4: [5, 6], 5: [7, 8], 6: [7], 7: [9], 8: [5, 9], 9: [2, 4, 10], 10: []}
  g = cfg.Digraph([1], [[2, 10], [3, 4], [5], [5, 6], [7, 8], [7], [9], [5, 9], [2, 4, 10], []])
  correctdom = graph.Tree(1, pred_init=[0, 1, 2, 2, 2, 4, 2, 5, 2, 1])
  correctjsucc = {1: set(), 2: set(), 3: {5}, 4: {5}, 5: {7}, 6: {7}, 7: {9}, 8: {5, 9}, 9: {2, 4, 10}, 10: set()}
  assert g.tarjan_dominators(1) == correctdom and g.doms[1][1] == correctjsucc
  correct_loop = {1: 0, 2: 0, 3: 2, 4: 0, 5: 2, 6: 0, 7: 0, 8: 5, 9: 0, 10: 0}
  correct_type = {1: 0, 2: 1, 3: 0, 4: 2, 5: 2, 6: 2, 7: 2, 8: 0, 9: 2, 10: 0}
  correct_head = {5: {4, 9, 7, 6}}
  assert g.sreedhar_gao_lee_loops(1) == (correct_loop, correct_type, correct_head)
  #assert g.modified_sreedhar_gao_lee_loops() == (correct_loop, correct_type, correct_head)
  #g.steensgaard_loops()
def test_havlak_loops():
  #https://www.researchgate.net/publication/220404846_Nesting_of_Reducible_and_Irreducible_Loops
  #Nesting of Reducible and Irreducible Loops
  #Paul Havlak
  #ACM Transactions on Programming Languages and Systems, Vol. 19, No. 4, July 1997, Pages 557-567.
  gsucc = {1: [2, 9], 2: [3, 5], 3: [4], 4: [5, 6], 5: [4, 7], 6: [3, 6, 8], 7: [5], 8: [2, 9], 9: []}
  g = cfg.Digraph([1], [[2, 9], [3, 5], [4], [5, 6], [4, 7], [3, 6, 8], [5], [2, 9], []])
  dom = g.tarjan_dominators(1)
  correctdom = graph.Tree(1, pred_init=[0, 1, 2, 2, 2, 4, 5, 6, 1])
  correctdfsparents = {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 4, 7: 5, 8: 6, 9: 8}
  assert g.tarjan_dominators(1) == correctdom and dfs.dfs_interval(gsucc, 1)[2] == correctdfsparents
  correct_header = {0: 0, 1: 0, 2: 0, 3: 2, 4: 3, 5: 4, 6: 3, 7: 5, 8: 2, 9: 0}
  correct_type = {0: NONHEADER, 1: NONHEADER, 2: REDUCIBLE, 3: IRREDUCIBLE, 4: IRREDUCIBLE, 5: REDUCIBLE, 6: SELF, 7: NONHEADER, 8: NONHEADER, 9: NONHEADER}
  #g = cfg.Digraph([1], list(gsucc.values()))
  header, type = g.havlak_loops()
  assert header == correct_header and type == correct_type
  gpred = graph.succ_to_pred(gsucc)
  added_nodes, added_edges, deleted_edges = havlak_fix_loops(gpred, g.dfs_tree, g.dfs_int, g.dfs_revint)
  correctmod = ({10}, {(4, 10), (10, 5), (2, 10)}, {(4, 5), (2, 5)})
  assert (added_nodes, added_edges, deleted_edges) == correctmod
  for x in added_nodes: g.add_node(x)
  for x, y in added_edges: g.add_edge(x, y)
  for x, y in deleted_edges: g.remove_edge(x, y)
  #paper has an error where delta' -> gamma is shown not delta -> gamma
  gsplit = {1: [2, 9], 2: [3, 10], 3: [4], 4: [10, 6], 10: [5], 5: [4, 7], 6: [3, 6, 8], 7: [5], 8: [2, 9], 9: []}
  assert {x: set(y) for x, y in gsplit.items()} == g.succ
  header, type = g.havlak_loops()
  correct_header = {0: 0, 1: 0, 2: 0, 3: 2, 4: 3, 5: 4, 6: 3, 7: 5, 8: 2, 9: 0, 10: 4}
  correct_type = {0: NONHEADER, 1: NONHEADER, 2: REDUCIBLE, 3: IRREDUCIBLE, 4: IRREDUCIBLE, 5: REDUCIBLE, 6: SELF, 7: NONHEADER, 8: NONHEADER, 9: NONHEADER, 10: NONHEADER}
  assert header == correct_header and type == correct_type
  
  gsucc = {1: [2, 9], 2: [5, 3], 3: [4], 4: [5, 6], 5: [4, 7], 6: [3, 6, 8], 7: [5], 8: [2, 9], 9: []} #same graph with different DFST
  correctdfsparents = {1: 0, 2: 1, 3: 6, 4: 5, 5: 2, 6: 4, 7: 5, 8: 6, 9: 8}
  assert dfs.dfs_interval(gsucc, 1)[2] == correctdfsparents
  g = cfg.Digraph([1], list(gsucc.values()))
  header, type = g.havlak_loops()
  correct_header = {0: 0, 1: 0, 2: 0, 3: 4, 4: 5, 5: 2, 6: 4, 7: 5, 8: 2, 9: 0}
  correct_type = {0: NONHEADER, 1: NONHEADER, 2: REDUCIBLE, 3: NONHEADER, 4: IRREDUCIBLE, 5: IRREDUCIBLE, 6: SELF, 7: NONHEADER, 8: NONHEADER, 9: NONHEADER}
  assert header == correct_header and type == correct_type
  #note that the newly inserted nodes must be effectively added first as tree edges in DFS as in node 2
  gsplit = {1: [2, 9], 2: [10, 3], 3: [4], 4: [10, 6], 5: [4, 7], 6: [3, 6, 8], 7: [5], 8: [2, 9], 9: [], 10: [5]}
  g = cfg.Digraph([1], list(gsplit.values()))
  header, type = g.havlak_loops()
  correct_header = {0: 0, 1: 0, 2: 0, 3: 4, 4: 10, 5: 10, 6: 4, 7: 5, 8: 2, 9: 0, 10: 2}
  correct_type = {0: NONHEADER, 1: NONHEADER, 2: REDUCIBLE, 3: NONHEADER, 4: IRREDUCIBLE, 5: REDUCIBLE, 6: SELF, 7: NONHEADER, 8: NONHEADER, 9: NONHEADER, 10: IRREDUCIBLE}
  assert header == correct_header and type == correct_type

def test_linear_havlak_mod_sgl():
  #http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.57.5381&rep=rep1&type=pdf
  #Identifying Loops In Almost Linear Time
  #G. RAMALINGAM
  def generate_quadratic_counter_example(k):
    gsucc = {1: [2]}
    for i in range(2, k+2):
      gsucc[i] = [i+1, 2*k+3 - i] if 2*k+3 != i else [i+1]
    for i in range(k+2, 2*k+2):
      gsucc[i] = [i+1]
    for i in range(2*k+2, 3*k+2):
      gsucc[i] = [i+1, 2*(2*k+2) - i - 1]
    gsucc[3*k+2] = []
    return gsucc
  gsucc = generate_quadratic_counter_example(3)
  g = cfg.Digraph([1], list(gsucc.values()))
  assert g.dfs_tree.pred == {0: None, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8, 10: 9, 11: 10}
  lnf = ({0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 5, 7: 6, 8: 7, 9: 6, 10: 5, 11: 0}, {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 2, 6: 2, 7: 1, 8: 0, 9: 0, 10: 0, 11: 0})
  assert g.havlak_loops() == lnf
  assert g.linear_havlak_loops() == lnf
  def generate_sgl_quadratic_counter_example(k):
    gsucc = {1: [2, 3, 4, 5], 2: [8], 3: [6], 4: [5, 7], 5: [9], 6: [4], 7: [3]}
    for i in range(8, 8+k*2-5):
      gsucc[i] = [i+2]
      gsucc[i+1] = [i+3]
    gsucc[8+k*2-4] = [3]
    gsucc[8+k*2-3] = []
    return gsucc
  gsucc = generate_sgl_quadratic_counter_example(3)
  g = cfg.Digraph([1], list(gsucc.values()))
  lnf = ({1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0}, {1: 0, 2: 0, 3: 2, 4: 2, 5: 0, 6: 2, 7: 2, 8: 0, 9: 0, 10: 0, 11: 0}, {3: {4, 6, 7}})
  assert g.sreedhar_gao_lee_loops(1) == lnf
  assert g.modified_sreedhar_gao_lee_loops(1) == lnf
  #modified_sreedhar_gao_lee_steensgaard_loops(1)
  pass
def test_ramalingam_reduced_havlak():
  #http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.35.8991&rep=rep1&type=pdf
  #On Loops, Dominators, and Dominance Frontiers
  #G. Ramalingam
  gsucc = {1: [2, 3], 2: [4], 3: [5], 4: [2, 5, 6], 5: [3, 4, 6], 6: []}
  g = cfg.Digraph([1], [[2, 3], [4], [5], [2, 5, 6], [3, 4, 6], []])
  gpred = graph.succ_to_pred(gsucc)
  dom = dominators.tarjan_doms(1, gsucc)
  jg = dominators.get_j_edges(gsucc, dom)
  dfs_tree, dfs_int, dfs_revint = dfs.do_dfs([1], gsucc)
  sgllnf = ({1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}, {1: 0, 2: 2, 3: 2, 4: 2, 5: 2, 6: 0}, {2: {3, 4, 5}})
  assert sreedhar_gao_lee_loops(gpred, dfs_tree, dfs_int, dom) == sgllnf
  steensgaardlnf = ({1: 0, 2: 0, 3: 2, 4: 2, 5: 4, 6: 0}, {1: 0, 2: 2, 3: 0, 4: 2, 5: 0, 6: 0}, {2: {3: {1}, 2: {1}}, 4: {4: {2}, 5: {3}}})
  assert steensgaard_loops(1, gpred, dfs_int) == steensgaardlnf
  havlaklnf = g.havlak_loops()
  linhavlaklnf = g.linear_havlak_loops()
  correctredhavlak = ({0: 0, 1: 0, 2: 0, 3: 2, 4: 2, 5: 2, 6: 0}, {0: 0, 1: 0, 2: 2, 3: 0, 4: 2, 5: 2, 6: 0}, {2: {4, 5}})
  redhavlaklnf = g.reduced_havlak_loops()
  assert correctredhavlak == redhavlaklnf
  newalgolnf = g.new_algo_loops()
  lnf = ({0: 0, 1: 0, 2: 0, 4: 2, 5: 4, 3: 5, 6: 0}, {0: 0, 1: 0, 2: 2, 4: 2, 5: 2, 3: 0, 6: 0}, {5: {3: {1}}, 4: {3: {1}}, 2: {3: {1}}})
  assert lnf == newalgolnf
  assert havlaklnf == linhavlaklnf
  assert lnf[:2] == havlaklnf
  #print(graph.make_graphviz_dot_text(gsucc, ';'.join((dfs.graphviz_dot_jungle(gsucc, dfs_tree, dfs_int), dominators.graphviz_dot_dj(gsucc, dominators.tarjan_doms(1, gsucc)), graphviz_dot_lnf(*newalgolnf)))))
def test_new_algo_loops():
  #https://lenx.100871.net/papers/loop-SAS.pdf
  #A New Algorithm for Identifying Loops in Decompilation
  #Tao Wei, Jian Mao, Wei Zou, Yu Chen
  gsucc = {1: [2, 3], 2: [3], 3: [2]} #irreducible core
  lnf = ({0: 0, 1: 0, 2: 0, 3: 2}, {0: 0, 1: 0, 2: 2, 3: 0}, {2: {3: {1}}})
  assert new_algo_loops(gsucc, dfs.do_dfs([1], gsucc)[1]) == lnf
  gsucc = {1: [2, 6], 2: [3], 3: [4], 4: [3, 5], 5: [2, 11], 6: [7], 7: [8], 8: [7, 9], 9: [10], 10: [6, 9, 11], 11: []} #CFG with nested loops
  lnf = ({0: 0, 1: 0, 2: 0, 3: 2, 4: 3, 5: 2, 11: 0, 6: 0, 7: 6, 8: 7, 9: 6, 10: 9}, {0: 0, 1: 0, 2: 1, 3: 1, 4: 0, 5: 0, 11: 0, 6: 1, 7: 1, 8: 0, 9: 1, 10: 0}, {})
  assert new_algo_loops(gsucc, dfs.do_dfs([1], gsucc)[1]) == lnf
  
  gsucc = {1: [2, 5], 2: [3], 3: [2, 4, 6], 4: [3, 5, 6], 5: [4], 6: []} #classic irreducible CFG
  lnf = ({0: 0, 1: 0, 2: 0, 3: 2, 4: 3, 5: 4, 6: 0}, {0: 0, 1: 0, 2: 2, 3: 2, 4: 2, 5: 0, 6: 0}, {4: {5: {1}}, 3: {5: {1}}, 2: {5: {1}}})
  assert new_algo_loops(gsucc, dfs.do_dfs([1], gsucc)[1]) == lnf
  
  gsucc = {1: [2], 2: [3], 3: [4], 4: [5], 5: [6], 6: []} #case A
  lnf = ({0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}, {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}, {})
  assert new_algo_loops(gsucc, dfs.do_dfs([1], gsucc)[1]) == lnf
  gsucc = {1: [2], 2: [3], 3: [4], 4: [5], 5: [3]} #case B
  lnf  = ({0: 0, 1: 0, 2: 0, 3: 0, 4: 3, 5: 3}, {0: 0, 1: 0, 2: 0, 3: 1, 4: 0, 5: 0}, {})
  assert new_algo_loops(gsucc, dfs.do_dfs([1], gsucc)[1]) == lnf
  gsucc = {1: [2], 2: [3], 3: [4, 5], 4: [6], 5: [6], 6: [7], 7: []} #case C
  lnf = ({0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 6: 0, 7: 0, 5: 0}, {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 6: 0, 7: 0, 5: 0}, {})
  assert new_algo_loops(gsucc, dfs.do_dfs([1], gsucc)[1]) == lnf
  gsucc = {1: [2], 2: [3], 3: [4], 4: [5, 6], 5: [7], 6: [7], 7: [8], 8: [3]} #case D
  lnf = ({0: 0, 1: 0, 2: 0, 3: 0, 4: 3, 5: 3, 7: 3, 8: 3, 6: 3}, {0: 0, 1: 0, 2: 0, 3: 1, 4: 0, 5: 0, 7: 0, 8: 0, 6: 0}, {})
  assert new_algo_loops(gsucc, dfs.do_dfs([1], gsucc)[1]) == lnf
  gsucc = {1: [2], 2: [3], 3: [4, 5], 4: [6], 5: [7], 6: [8], 7: [8], 8: [9], 9: [2, 6]} #case E
  lnf = ({0: 0, 1: 0, 2: 0, 3: 2, 4: 2, 6: 2, 8: 6, 9: 6, 5: 2, 7: 2}, {0: 0, 1: 0, 2: 1, 3: 0, 4: 0, 6: 2, 8: 0, 9: 0, 5: 0, 7: 0}, {6: {8: {7}}})
  assert new_algo_loops(gsucc, dfs.do_dfs([1], gsucc)[1]) == lnf
  gsucc = {1: [2], 2: [3], 3: [4], 4: [2, 5], 5: [3, 6], 6: [4, 5]} #tagging
  lnf = ({0: 0, 1: 0, 2: 0, 3: 2, 4: 3, 5: 4, 6: 5}, {0: 0, 1: 0, 2: 1, 3: 1, 4: 1, 5: 1, 6: 0}, {})
  assert new_algo_loops(gsucc, dfs.do_dfs([1], gsucc)[1]) == lnf
  gsucc = {1: [2], 2: [3], 3: [4, 5], 4: [6], 5: [7], 6: [8], 7: [8], 8: [6, 9], 9: [4, 10], 10: [2]} #multientry unstructuredness
  lnf = ({0: 0, 1: 0, 2: 0, 3: 2, 4: 2, 6: 4, 8: 6, 9: 4, 10: 2, 5: 2, 7: 2}, {0: 0, 1: 0, 2: 1, 3: 0, 4: 2, 6: 2, 8: 0, 9: 0, 10: 0, 5: 0, 7: 0}, {6: {8: {7}}, 4: {8: {7}}})
  assert new_algo_loops(gsucc, dfs.do_dfs([1], gsucc)[1]) == lnf
  gsucc = {1: [2], 2: [3], 3: [4], 4: [5], 5: [6], 6: [2, 7], 7: [3, 8], 8: [4, 9], 9: [5]} #overlapping unstructuredness
  lnf = ({0: 0, 1: 0, 2: 0, 3: 2, 4: 3, 5: 4, 6: 5, 7: 5, 8: 5, 9: 5}, {0: 0, 1: 0, 2: 1, 3: 1, 4: 1, 5: 1, 6: 0, 7: 0, 8: 0, 9: 0}, {})
  assert new_algo_loops(gsucc, dfs.do_dfs([1], gsucc)[1]) == lnf
def test_steensgaard_loops():
  #http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.48.5416&rep=rep1&type=pdf
  #Sequentializing Program Dependence Graphs for Irreducible Programs (1993)
  #by Bjarne Steensgaard
  #gsucc = {1: [2], 2: [5, 7, 8], 3: [5, 7, 8], 4: [5, 7, 8], 5: [3, 4], 6: [3, 4], 7: [6, 9], 8: [6, 9], 9: []}
  gsucc = {1: [2], 2: [3, 4], 3: [5, 6], 4: [7], 5: [], 6: [4], 7: []} #sample CDG with no loops
  gpred = graph.succ_to_pred(gsucc)
  dfs_tree, dfs_int, dfs_revint = dfs.do_dfs([1], gsucc)
  lnf = ({1: 0, 2: 0, 3: 0, 6: 0, 4: 0, 5: 0, 7: 0}, {1: 0, 2: 0, 3: 0, 6: 0, 4: 0, 5: 0, 7: 0}, {}) #digraph with a loop
  assert steensgaard_loops(1, gpred, dfs_int) == lnf
  gsucc = {1: [2, 3], 2: [3], 3: [4], 4: [2]}
  gpred = graph.succ_to_pred(gsucc)
  dfs_tree, dfs_int, dfs_revint = dfs.do_dfs([1], gsucc)
  lnf = ({1: 0, 2: 0, 3: 2, 4: 2}, {1: 0, 2: 2, 3: 0, 4: 0}, {2: {3: {1}, 2: {1}}}) #digraph with nested loops
  assert steensgaard_loops(1, gpred, dfs_int) == lnf
  gsucc = {1: [2], 2: [3], 3: [4], 4: [2, 3]}
  gpred = graph.succ_to_pred(gsucc)
  dfs_tree, dfs_int, dfs_revint = dfs.do_dfs([1], gsucc)
  lnf = ({1: 0, 2: 0, 3: 2, 4: 3}, {1: 0, 2: 1, 3: 1, 4: 0}, {})
  assert steensgaard_loops(1, gpred, dfs_int) == lnf
  
  gsucc = {1: [2, 3, 4], 2: [], 3: [], 4: [5, 6], 5: [7, 8], 6: [9, 10], 7: [], 8: [6], 9: [5], 10: []} #example CDG with irreducible loop
  gpred = graph.succ_to_pred(gsucc)
  dfs_tree, dfs_int, dfs_revint = dfs.do_dfs([1], gsucc)
  lnf = ({1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 5, 8: 5, 9: 5, 7: 0, 10: 0}, {1: 0, 2: 0, 3: 0, 4: 0, 5: 2, 6: 0, 8: 0, 9: 0, 7: 0, 10: 0}, {5: {6: {4}, 5: {4}}}) 
  assert steensgaard_loops(1, gpred, dfs_int) == lnf
  
  gsucc = {1: [2, 3, 4], 2: [], 3: [], 4: [5, 6], 5: [7, 8], 6: [9, 10], 7: [], 8: [11], 9: [12], 10: [], 11: [6], 12: [5]} #example CDG modified to add closing edge nodes
  gpred = graph.succ_to_pred(gsucc)
  dfs_tree, dfs_int, dfs_revint = dfs.do_dfs([1], gsucc)
  lnf = ({1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 5, 8: 5, 11: 5, 9: 5, 12: 5, 7: 0, 10: 0}, {1: 0, 2: 0, 3: 0, 4: 0, 5: 2, 6: 0, 8: 0, 11: 0, 9: 0, 12: 0, 7: 0, 10: 0}, {5: {6: {4}, 5: {4}}})
  assert steensgaard_loops(1, gpred, dfs_int) == lnf
  
def paper_inc_dec_reducible_lnf(output_dir):
  import os
  """
  #totdigraphs = [graph.count_digraphs(n) for n in range(10)] #A002416
  totsdigraphs = [graph.count_simple_digraphs(n) for n in range(10)] #A053763
  totacycliccfgs = graph.graph_seqs(300, lambda x: graph.graph_enum(x, lambda y: graph.enum_connected_dags(y, True))) #A003025
  totcfgs = graph.graph_seqs(50000, lambda x: graph.graph_enum(x, lambda y: graph.enum_connected_digraphs(y, True, False)))
  totscfgs = graph.graph_seqs(300, lambda x: graph.graph_enum(x, lambda y: graph.enum_connected_digraphs(y, True, True))) #A003028
  print(totcfgs, totscfgs)
  totnonacyclicirredcfgs = graph.graph_seqs(300, lambda x: graph.graph_enum(x, lambda y: graph.enum_connected_digraphs(y, True, False, nonacyclic=True, reducible=False)))
  totnonacyclicirredscfgs = graph.graph_seqs(300, lambda x: graph.graph_enum(x, lambda y: graph.enum_connected_digraphs(y, True, True, nonacyclic=True, reducible=False)))
  totnonacyclicredcfgs = graph.graph_seqs(400, lambda x: graph.graph_enum(x, lambda y: graph.enum_connected_digraphs(y, True, False, nonacyclic=True, reducible=True)))
  totnonacyclicredscfgs = graph.graph_seqs(300, lambda x: graph.graph_enum(x, lambda y: graph.enum_connected_digraphs(y, True, True, nonacyclic=True, reducible=True)))
  cols = [totsdigraphs, totacycliccfgs, totcfgs, totscfgs, totnonacyclicirredcfgs, totnonacyclicirredscfgs, totnonacyclicredcfgs, totnonacyclicredscfgs]
  print(cols)
  """
  root, init = 1, [[2, 3, 5], [7], [4, 6], [3, 7, 9], [10], [3, 7, 9], [5, 8], [], [], [1, 10]]
  new_edge = (9, 3)
  succ, pred = {}, {}
  dfs_tree, dfs_int, dfs_revint = dfs.init_dfs()
  loopcounts, loopheaders, looptypes, loopentries = init_lnf()
  for x, s in enumerate(init):
    if not x+1 in succ:
      succ[x+1] = set(); pred[x+1] = set()
      dfs.add_node_dfs(dfs_tree, dfs_int, dfs_revint, x+1)
      add_node_lnf(x+1, loopheaders, looptypes)
    for y in s:
      if not y in pred:
        succ[y] = set(); pred[y] = set()
        dfs.add_node_dfs(dfs_tree, dfs_int, dfs_revint, y)
        add_node_lnf(y, loopheaders, looptypes)
      succ[x+1].add(y); pred[y].add(x+1)
      dfs.do_inc_add_edge_dfs(succ, dfs_tree, dfs_int, dfs_revint, x+1, y)
      do_inc_reducible_tarjan_lnf(x+1, y, pred, dfs_tree, dfs_int, loopcounts, loopheaders, looptypes)
      if y != root and len(pred[y]) == 1:
        bind_dec_dfs_reducible_lnf(root, y, root, succ, pred, ((dfs_tree, dfs_int, dfs_revint), (loopcounts, loopheaders, looptypes)), None)
  output = "Initial Graph with its Jungle, Dominators and LNF:\n"
  output += graph.make_graphviz_dot_text(succ, ';'.join((dfs.graphviz_dot_jungle(succ, dfs_tree, dfs_int), dominators.graphviz_dot_dj(succ, dominators.tarjan_doms(root, succ)), graphviz_dot_lnf(loopheaders, looptypes, loopentries)))) + "\n"
  succ[new_edge[0]].add(new_edge[1]); pred[new_edge[1]].add(new_edge[0])
  dfs.do_inc_add_edge_dfs(succ, dfs_tree, dfs_int, dfs_revint, new_edge[0], new_edge[1])
  do_inc_reducible_tarjan_lnf(new_edge[0], new_edge[1], pred, dfs_tree, dfs_int, loopcounts, loopheaders, looptypes)
  output += "\nGraph, Jungle, Dominators and LNF On Edge Addition (%d, %d):\n" % new_edge
  output += graph.make_graphviz_dot_text(succ, ';'.join((dfs.graphviz_dot_jungle(succ, dfs_tree, dfs_int), dominators.graphviz_dot_dj(succ, dominators.tarjan_doms(root, succ)), graphviz_dot_lnf(loopheaders, looptypes, loopentries)))) + "\n"
  new_edge = (2, 6)
  succ[new_edge[0]].add(new_edge[1]); pred[new_edge[1]].add(new_edge[0])
  dfs.do_inc_add_edge_dfs(succ, dfs_tree, dfs_int, dfs_revint, new_edge[0], new_edge[1])
  inc_havlak_lnf(new_edge[0], new_edge[1], succ, pred, dfs_tree, dfs_int, loopcounts, loopheaders, looptypes, loopentries)
  output += "\nGraph, Jungle, Dominators and LNF On Edge Addition (%d, %d):\n" % new_edge
  output += graph.make_graphviz_dot_text(succ, ';'.join((dfs.graphviz_dot_jungle(succ, dfs_tree, dfs_int), dominators.graphviz_dot_dj(succ, dominators.tarjan_doms(root, succ)), graphviz_dot_lnf(loopheaders, looptypes, loopentries)))) + "\n"
  #output += "\nGraph, Jungle, Dominators and LNF On Edge Deletion (%d, %d):\n" % new_edge
  #succ[new_edge[0]].remove(new_edge[1]); pred[new_edge[1]].remove(new_edge[0])
  #bind_dec_dfs_reducible_lnf(new_edge[0], new_edge[1], root, succ, pred, ((dfs_tree, dfs_int, dfs_revint), (loopcounts, loopheaders, looptypes)), None)
  #output += graph.make_graphviz_dot_text(succ, ';'.join((dfs.graphviz_dot_jungle(succ, dfs_tree, dfs_int), dominators.graphviz_dot_dj(succ, dominators.tarjan_doms(root, succ)), graphviz_dot_lnf(loopheaders, looptypes, loopentries)))) + "\n"
  with open(os.path.join(output_dir, 'reducible_lnf_graph_dot.txt'), "w") as f:
    f.write(output)
def paper_inc_dec_irreducible_lnf(output_dir): pass

def do_inc_is_reducible_tarjan_lnf(a, b, pred, dfs_tree, dfs_int, loopheaders, looptypes):
  try:
    do_inc_reducible_tarjan_lnf(a, b, pred, dfs_tree, dfs_int, loopheaders, looptypes)
    #do_dec_reducible_tarjan_lnf(a, b, cur_edge == dfs.FORWARD_EDGE, pred, dfs_tree, dfs_int, loopheaders, looptypes)
    return True
  except ValueError:
    return False
def init_dfs_with_root(root):
  d = dfs.init_dfs()
  dfs.add_node_dfs(*d, root)
  return d  
def timing_inc_dec_reducible_lnf(output_dir):
  import os
  iterations, repeat = 10, 1
  output = ""
  results = {}
  for c in range(10, 70, 10):
    results[c] = graph.timing_test(iterations, lambda: graph.random_digraph(c), repeat, [lambda root: (*init_dfs_with_root(root), [None]), lambda root: init_with_root_lnf(root, init_lnf())],
    [lambda n, data: dfs.add_node_dfs(data[0], data[1], data[2], n), lambda n, data: add_node_lnf(n, data[1], data[2])],
    [lambda n, data: dfs.remove_node_dfs(data[0], data[1], data[2], n), lambda n, data: remove_node_lnf(n, data[1], data[2])],
    [lambda x, y, root, succ, pred, data, _: dfs.do_inc_add_edge_dfs(succ, data[0], data[1], data[2], x, y),
     lambda x, y, root, succ, pred, data, graph_data: do_inc_reducible_tarjan_lnf(x, y, pred, graph_data[0][0], graph_data[0][1], data[0], data[1], data[2])],
    [lambda x, y, root, succ, pred, data, _: bind_dfs_curedge(succ, pred, data[0], data[1], data[2], data[3], x, y),
     lambda x, y, root, succ, pred, data, graph_data: do_dec_reducible_tarjan_lnf(x, y, graph_data[0][3][0] == dfs.FORWARD_EDGE, pred, graph_data[0][0], graph_data[0][1], data[0], data[1], data[2])],
    [lambda x, y, root, succ, pred, graph_data: dfs.do_dfs([root], succ, graph_data[0][1]),
     lambda x, y, root, succ, pred, graph_data: do_tarjan_loops(pred, graph_data[0][0], graph_data[0][1], graph_data[0][2])],
    edge_condition=[lambda x, y, root, succ, pred, graph_data: check_is_reducible(x, y, root, succ, pred, graph_data[0][1])],
    inc_edge_condition=[lambda x, y, root, succ, pred, data, graph_data: inc_is_reducible(x, y, succ, pred, graph_data[0][0], graph_data[0][1], graph_data[0][2], graph_data[1][0], graph_data[1][1], graph_data[1][2], graph_data[1][3])],
    dec_edge_condition=[lambda x, y, root, succ, pred, data, graph_data: dec_is_reducible(x, y, succ, pred, graph_data[0][0], graph_data[0][1], graph_data[0][2], graph_data[1][0], graph_data[1][1], graph_data[1][2], graph_data[1][3])])
    print(results[c])
  for x in sorted(results):
    output += ("%d %s %s %s %s %s %s %s %s\n" % (x, *(repr(z / (iterations * repeat)) for y in results[x] for z in y)))
  with open(os.path.join(output_dir, 'lnf_reducible_paper.txt'), "w") as f:
    f.write(output)
  import matplotlib.pyplot as plt
  from matplotlib.ticker import MaxNLocator
  fig = plt.figure()
  ax1 = fig.add_subplot(111)
  ax1.plot(results.keys(), [results[x][0][0] for x in results], label="Incremental DFS")
  ax1.plot(results.keys(), [results[x][0][1] for x in results], label="Incremental LNF")
  ax1.plot(results.keys(), [results[x][1][0] for x in results], label="Decremental DFS")
  ax1.plot(results.keys(), [results[x][1][1] for x in results], label="Decremental LNF")
  ax1.plot(results.keys(), [results[x][2][0] for x in results], label="Offline DFS")
  ax1.plot(results.keys(), [results[x][2][1] for x in results], label="Offline LNF")
  #ax1.plot(results.keys(), [results[x][0][0] for x in results], label="Offline DFS")
  #ax1.plot(results.keys(), [results[x][0][1] for x in results], label="Offline LNF")
  ax1.set_xlabel("Size")  
  #ax1.set_yscale('log', base=10)
  ax1.set_ylabel("Time (s)")
  ax1.legend()
  ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
  ax1.set_title("Cumulative times for DFS and LNF (n nodes, $\\frac{n^2}{2}$ edges)")
  fig.savefig(os.path.join(output_dir, "lnf_reducible.svg"), format="svg")

def bind_dfs_curedge(succ, pred, dfs_tree, dfs_int, dfs_revint, curedge, x, y):
  curedge[0] = dfs.do_classify_edge(dfs_tree, dfs_int, x, y)
  dfs.do_dec_remove_edge_dfs(succ, pred, dfs_tree, dfs_int, dfs_revint, x, y)
def timing_inc_dec_irreducible_lnf(output_dir):
  import os
  iterations, repeat = 10, 1
  output = ""
  results = {}
  for c in range(10, 50, 10):
    results[c] = graph.timing_test(iterations, lambda: graph.random_digraph(c), repeat, [lambda root: (*init_dfs_with_root(root), [None]), lambda root: init_with_root_lnf(root, init_lnf())],
    [lambda n, data: dfs.add_node_dfs(data[0], data[1], data[2], n), lambda n, data: add_node_lnf(n, data[1], data[2])],
    [lambda n, data: dfs.remove_node_dfs(data[0], data[1], data[2], n), lambda n, data: remove_node_lnf(n, data[1], data[2])],
    [lambda x, y, root, succ, pred, data, _: dfs.do_inc_add_edge_dfs(succ, data[0], data[1], data[2], x, y),
     lambda x, y, root, succ, pred, data, graph_data: inc_havlak_lnf(x, y, succ, pred, graph_data[0][0], graph_data[0][1], data[0], data[1], data[2], data[3])],
    [lambda x, y, root, succ, pred, data, _: bind_dfs_curedge(succ, pred, data[0], data[1], data[2], data[3], x, y),
     lambda x, y, root, succ, pred, data, graph_data: dec_havlak_lnf(x, y, graph_data[0][3][0] == dfs.FORWARD_EDGE, succ, pred, graph_data[0][0], graph_data[0][1], data[0], data[1], data[2], data[3])],
    [lambda x, y, root, succ, pred, graph_data: dfs.do_dfs([root], succ, graph_data[0][1]),
     lambda x, y, root, succ, pred, graph_data: new_algo_loops(succ, graph_data[0][1])])
    print(results[c])
  for x in sorted(results):
    output += ("%d %s %s %s %s %s %s %s %s\n" % (x, *(repr(z / (iterations * repeat)) for y in results[x] for z in y)))
  with open(os.path.join(output_dir, 'lnf_paper.txt'), "w") as f:
    f.write(output)
    
def adapt_offline_havlak(data):
  from collections import Counter
  lc = Counter(data[1].values())
  return [lc[SELF], lc[REDUCIBLE], lc[IRREDUCIBLE]], data[0], data[1], data[2]
def adapt_offline_tarjan(data):
  from collections import Counter
  lc = Counter(data[1].values())
  return [lc[SELF], lc[REDUCIBLE], lc[IRREDUCIBLE]], data[0], data[1]
def bind_dec_dfs_lnf(x, y, root, succ, pred, data, _):
  cur_edge = dfs.do_classify_edge(data[0][0], data[0][1], x, y)
  dfs.do_dec_remove_edge_dfs(succ, pred, data[0][0], data[0][1], data[0][2], x, y)
  dec_havlak_lnf(x, y, cur_edge == dfs.FORWARD_EDGE, succ, pred, data[0][0], data[0][1], data[1][0], data[1][1], data[1][2], data[1][3])
def bind_dec_dfs_reducible_lnf(x, y, root, succ, pred, data, _):
  cur_edge = dfs.do_classify_edge(data[0][0], data[0][1], x, y)
  dfs.do_dec_remove_edge_dfs(succ, pred, data[0][0], data[0][1], data[0][2], x, y)
  do_dec_reducible_tarjan_lnf(x, y, cur_edge == dfs.FORWARD_EDGE, pred, data[0][0], data[0][1], data[1][0], data[1][1], data[1][2])
def print_lnf(x, y, root, succ, dfs_tree, dfs_int, loopheaders, looptypes, loopentries, base, output_dir):
  graph.do_graphviz_dot(graph.make_graphviz_dot_text(succ, ';'.join((dfs.graphviz_dot_jungle(succ, dfs_tree, dfs_int), dominators.graphviz_dot_dj(succ, dominators.tarjan_doms(root, succ)), *([graphviz_dot_lnf(base[1][1], base[1][2], base[1][3], pre="bl")] if not base is None else []), graphviz_dot_lnf(loopheaders, looptypes, loopentries)))), output_dir)
def init_with_root_lnf(root, l):
  add_node_lnf(root, *l[1:3])
  return l
def verify_dyn_irreducible_lnf(output_dir, connected=False):
  iterations, nodes = 1000, 10
  graph.verification_algo_test(iterations, lambda: graph.random_digraph(nodes, connected), [lambda root: (init_dfs_with_root(root), init_with_root_lnf(root, init_lnf()))],
    [lambda n, data: (dfs.add_node_dfs(data[0][0], data[0][1], data[0][2], n), add_node_lnf(n, data[1][1], data[1][2]))],
    [lambda n, data: (dfs.remove_node_dfs(data[0][0], data[0][1], data[0][2], n), remove_node_lnf(n, data[1][1], data[1][2]))],
    [lambda x, y, root, succ, pred, data, _: (dfs.do_inc_add_edge_dfs(succ, data[0][0], data[0][1], data[0][2], x, y), inc_havlak_lnf(x, y, succ, pred, data[0][0], data[0][1], data[1][0], data[1][1], data[1][2], data[1][3]))],
    [bind_dec_dfs_lnf],
    [lambda x, y, root, succ, pred, graph_data: (dfs.do_dfs([root], succ, graph_data[0][0][1]), adapt_offline_havlak(new_algo_loops(succ, graph_data[0][0][1])))],
    print_func=lambda x, y, root, succ, pred, graph_data, base: print_lnf(x, y, root, succ, graph_data[0][0][0], graph_data[0][0][1], graph_data[0][1][1], graph_data[0][1][2], graph_data[0][1][3], base, output_dir))
def inc_is_reducible(x, y, succ, pred, dfs_tree, dfs_int, dfs_revint, loopcounts, loopheaders, looptypes, loopentries):
  dfs.do_inc_add_edge_dfs(succ, dfs_tree, dfs_int, dfs_revint, x, y)
  isreduce = do_inc_reducible_tarjan_lnf(x, y, pred, dfs_tree, dfs_int, loopcounts, loopheaders, looptypes, False)
  if not isreduce:
    inc_havlak_lnf(x, y, succ, pred, dfs_tree, dfs_int, loopcounts, loopheaders, looptypes, loopentries)
  return isreduce
def dec_is_reducible(x, y, succ, pred, dfs_tree, dfs_int, dfs_revint, loopcounts, loopheaders, looptypes, loopentries):
  cur_edge = dfs.do_classify_edge(dfs_tree, dfs_int, x, y)
  dfs.do_dec_remove_edge_dfs(succ, pred, dfs_tree, dfs_int, dfs_revint, x, y)
  dec_havlak_lnf(x, y, cur_edge == dfs.FORWARD_EDGE, succ, pred, dfs_tree, dfs_int, loopcounts, loopheaders, looptypes, loopentries)
def check_is_reducible(x, y, root, succ, pred, test_order):
  dfs_tree, dfs_int, dfs_revint = dfs.do_dfs([root], succ, test_order)
  return do_tarjan_is_reducible(pred, dfs_tree, dfs_int, dfs_revint)
def verify_dyn_reducible_lnf(output_dir, connected=False):
  iterations, nodes = 1000, 12
  graph.verification_algo_test(iterations, lambda: graph.random_digraph(nodes, connected), [lambda root: (init_dfs_with_root(root), init_with_root_lnf(root, init_lnf()))],
    [lambda n, data: (dfs.add_node_dfs(data[0][0], data[0][1], data[0][2], n), add_node_lnf(n, data[1][1], data[1][2]))],
    [lambda n, data: (dfs.remove_node_dfs(data[0][0], data[0][1], data[0][2], n), remove_node_lnf(n, data[1][1], data[1][2]))],
    [lambda x, y, root, succ, pred, data, _: (dfs.do_inc_add_edge_dfs(succ, data[0][0], data[0][1], data[0][2], x, y), do_inc_reducible_tarjan_lnf(x, y, pred, data[0][0], data[0][1], data[1][0], data[1][1], data[1][2]))],
    [bind_dec_dfs_reducible_lnf],
    [lambda x, y, root, succ, pred, graph_data: (dfs.do_dfs([root], succ, graph_data[0][0][1]), adapt_offline_tarjan(do_tarjan_loops(pred, graph_data[0][0][0], graph_data[0][0][1], graph_data[0][0][2])))],
    comparer=lambda x, y: x[0] == y[0] and x[1][:3] == y[1],
    edge_condition=[lambda x, y, root, succ, pred, graph_data: check_is_reducible(x, y, root, succ, pred, graph_data[0][0][1])],
    inc_edge_condition=[lambda x, y, root, succ, pred, data, _: inc_is_reducible(x, y, succ, pred, data[0][0], data[0][1], data[0][2], data[1][0], data[1][1], data[1][2], data[1][3])],
    dec_edge_condition=[lambda x, y, root, succ, pred, data, _: dec_is_reducible(x, y, succ, pred, data[0][0], data[0][1], data[0][2], data[1][0], data[1][1], data[1][2], data[1][3])],
    print_func=lambda x, y, root, succ, pred, graph_data, base: print_lnf(x, y, root, succ, graph_data[0][0][0], graph_data[0][0][1], graph_data[0][1][1], graph_data[0][1][2], {}, (base[0], (*base[1], {})) if not base is None else None, output_dir))