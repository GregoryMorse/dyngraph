#https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html
def getsatlib(cfgdir):
  import os
  fname = "uf20-91.tar.gz"
  outfile = os.path.join(cfgdir, fname)
  if not os.path.exists(outfile):
    import requests
    import tarfile
    response = requests.get("https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/" + fname, stream=True)
    if response.status_code == 200:
      with open(outfile, "wb") as out_file:
        out_file.write(response.raw.read())
    tar = tarfile.open(outfile)
    tar.extractall(path=cfgdir)
    tar.close()
def getrand3cnf(cfgdir):
  import glob
  import os
  for file in glob.glob(os.path.join(cfgdir, "uf20-*.cnf")):
    clauses = []
    with open(file, "r") as f:
      for line in f: #DIMACS format
        items = line.split()
        if len(items) == 0 or items[0] == 'c': continue #comment
        if items[0] == 'p': continue #p FORMAT=cnf VARIABLES CLAUSES
        if items[0] == '%': break
        clauses.append(tuple(int(x) for x in items if x != "0"))
    yield clauses
def getsatmap(clauses):
  map = dict()
  for clause in clauses:
    for x in clause:
      if not x in map: map[x] = set()
      if not -x in map: map[-x] = set()
      map[x].add(clause)
  return map
#multiple literals handled by using set for clauses
#unit propogation
def unit_prop(clauses, map): #if a clause=={var} then remove all clauses containing var and delete -var from all clauses containing it
  solvedvars = []
  clausestack = [c for c in clauses if len(c) == 1]
  while len(clausestack) != 0:
    clause = clausestack.pop()
    x = next(iter(clause))
    if not x in map: continue
    solvedvars.append(x)
    for c in map[x]: #delete satisfied clauses
      for y in c:
        if y == x: continue
        map[y].remove(c)
        #if len(map[y]) == 0 and len(map[-y]) == 0:
        #  del map[y]; del map[-y]
      clauses.remove(c)
    for c in map[-x]: #remove -x from clauses
      newc = c - {-x}
      clauses.remove(c)
      clauses.add(newc)
      if len(newc) == 1: clausestack.append(newc)
      for y in c:
        if y == -x: continue
        map[y].remove(c)
        map[y].add(newc)
      if len(newc) == 0: print(x); del map[x]; del map[-x]; return solvedvars #unsat
    #del map[x]
    #del map[-x]
  return solvedvars
#preserves SAT or UNSAT but does not preserve unique solutions
def pure_literal(clauses, map): #if -var never occurs in clauses, add {var} clause
  for var in (m for m in map if len(map[m]) == 0 and len(map[-m]) != 0):
    clause = frozenset((-var,))
    clauses.add(clause)
    map[-var].add(clause)
#preserves SAT or UNSAT but does not give information about variable used for splitting, leaves it as a free variable
def case_splitting(clauses, map, var):
  #(p or var) and (q or -var) === (p or q)
  for p in map[var]:
    for q in map[-var]:
      clause = frozenset((*(x for x in p if x != var), *(x for x in q if x != -var),))
      #subset rule - any superset clause of another clause is deleted
      if all(not clause.issuperset(c) for c in clauses):
        clauses.add(clause)
        for x in clause: map[x].add(clause)
  for c in map[var]:
    for y in c:
      if y == var: continue
      map[y].remove(c)
    clauses.remove(c)
  for c in map[-var]:    
    for y in c:
      if y == -var: continue
      map[y].remove(c)
    clauses.remove(c)
  #del map[var]
  #del map[-var]
def removesubsets(clauses, map):
  delclauses = []
  for clause in clauses:
    if any(clause.issuperset(c) for c in clauses if not clause is c):
      delclauses.append(clause)
  for clause in delclauses:
    clauses.remove(clause)
    for x in clause:
      map[x].remove(clause)
def tautology(clauses, map):
  for m in (m for m in map if m > 0):
    for c in [c for c in map[m] if c in map[-m]]:
      clauses.remove(c)
      for y in c:
        map[y].remove(c)
  #for m in (m for m in map if m > 0):
  #  if len(map[m]) == 0 and len(map[-m]) == 0:
  #    del map[m]; del map[-m]
def dpall(clauses):
  clauses = [x for x in clauses]
  allvars = {abs(y) for x in clauses for y in x} #set.union(*(set(abs(x) for x in c) for c in clauses))
  sol = dp(clauses)
  stack = [] if sol is None else [sol] 
  while len(stack) != 0:
    sol = stack.pop()
    if len(sol) != len(allvars):
      x = next(iter(allvars - set(abs(x) for x in sol)))
      for soln in (dp(clauses + [tuple((c,)) for c in sol] + [tuple((x,))]),
                   dp(clauses + [tuple((c,)) for c in sol] + [tuple((-x,))])):
        if not soln is None:
          if len(soln) == len(allvars):
            yield list(sorted(soln, key=lambda x: x if x > 0 else -x))
            clauses.append([-x for x in soln])
            soln = dp(clauses)
            if not soln is None: stack.append(soln)
          else: stack.append(soln)
    else:
      yield list(sorted(sol, key=lambda x: x if x > 0 else -x))
      clauses.append([-x for x in sol])
      sol = dp(clauses)
      if not sol is None: stack.append(sol)
def check_map(clauses, map):
  for clause in clauses:
    for c in clause:
      assert c in map and clause in map[c], (c, clause)
#Davis-Putnam algorithm https://en.wikipedia.org/wiki/Davis%E2%80%93Putnam_algorithm
#https://www.fi.muni.cz/~popel/lectures/complog/slides/davis-putnam.pdf
#https://people.eecs.berkeley.edu/~satishr/cs270.06/lecture1.pdf
#https://baldur.iti.kit.edu/sat/files/2016/l04.pdf
#https://people.eecs.berkeley.edu/~sseshia/219c/lectures/SATSolving.pdf
def dp(clauses):
  clauses = {frozenset(c) for c in clauses}
  map = getsatmap(clauses)
  solvedvars = []
  while True:
    tautology(clauses, map)
    removesubsets(clauses, map)
    while True:
      pure_literal(clauses, map)
      s = unit_prop(clauses, map)
      #check_map(clauses, map)
      solvedvars.extend(s)
      if len(s) == 0: break
      elif any(len(c) == 0 for c in clauses): return None #unsat
    if len(clauses) == 0: return solvedvars #sat
    x = next(iter(map))
    case_splitting(clauses, map, x)
#https://en.wikipedia.org/wiki/DPLL_algorithm
def dpllr(clauses, map, solvedvars):
  #while True:
  #pure_literal(clauses, map)
  s = unit_prop(clauses, map)
  solvedvars.extend(s)
  #if len(s) == 0: break
  if len(clauses) == 0:
    freeliterals = [m for m in map if m > 0]
    for x in range(1 << len(freeliterals)):
      yield list(sorted((*solvedvars, *(m if ((1 << i) & x) != 0 else -m for i, m in enumerate(freeliterals))),
                        key=lambda x: x if x > 0 else -x))
    return #sat
  elif any(len(c) == 0 for c in clauses):
    return #unsat
  x = next(iter(map))
  freeliterals = [m for m in map if m > 0 and len(map[m]) == 0 and len(map[-m]) == 0]
  posc = {frozenset(p) for p in clauses}
  posc.add(frozenset((x,)))
  pm = getsatmap(posc)
  for m in freeliterals: pm[m] = set(); pm[-m] = set()
  yield from dpllr(posc, pm, [z for z in solvedvars])
  negc = {frozenset(p) for p in clauses}
  negc.add(frozenset((-x,)))
  nm = getsatmap(negc)
  for m in freeliterals: nm[m] = set(); nm[-m] = set()
  yield from dpllr(negc, nm, [z for z in solvedvars])
#https://en.wikipedia.org/wiki/DPLL_algorithm
def dpll(clauses): #Davis-Putnam-Logemann-Loveland
  clauses = {frozenset(c) for c in clauses}
  map = getsatmap(clauses)
  tautology(clauses, map)
  #removesubsets(clauses, map)
  return dpllr(clauses, map, [])
#https://en.wikipedia.org/wiki/Conflict-driven_clause_learning
#http://ssa-school-2016.it.uu.se/wp-content/uploads/2016/06/LaurentSimon.pdf
def cdcl(clauses): #conflict-driven clause learning
  clauses = {frozenset(c) for c in clauses}
  map = getsatmap(clauses)
  tautology(clauses, map)
  #removesubsets(clauses, map)
  stack = [(0, False, clauses, map, [])]
  while len(stack) != 0:
    x, enumch, cs, mp, solved = stack[-1]
    if not enumch:
      solvedvars = unit_prop(cs, mp)
      satunsat = False
      if len(cs) == 0: #sat
        freeliterals = [m for m in mp if m > 0]
        solvedvars.extend(solved)
        for _, _, _, _, sv in stack: solvedvars.extend(sv)
        for b in range(1 << len(freeliterals)):
          yield list(sorted((*solvedvars, *(m if ((1 << i) & b) != 0 else -m for i, m in enumerate(freeliterals))),
                            key=lambda y: y if y > 0 else -y))
        satunsat = True
      elif any(len(c) == 0 for c in cs): #unsat, learn clause and non-chronological backtrack
        curconflict = [x for x in solvedvars]
        solvedvars.extend(solved) #one or more of the new unit clauses had to be the conflict
        for _, _, _, _, sv in stack: solvedvars.extend(sv)
        negsolvedvars = {-z for z in solvedvars}
        #unitconflicts = set()
        #conflict = set()
        #for clause in clauses:
        #  if clause.issubset(negsolvedvars):
        #    conflict.add(clause)
        #  clause = clause - negsolvedvars
          #if len(clause) == 1 
        #conflictvars = frozenset.union(*conflict)
        #for z in conflictvars:
        #  for c in map[z]:
        print(negsolvedvars, curconflict)
        print(solvedvars, map[curconflict[-1]], curconflict[-1])
        pclause = next(iter(clause for clause in map[curconflict[-1]] if clause.issubset(negsolvedvars | frozenset(solvedvars))))
        nclause = next(iter(clause for clause in map[-curconflict[-1]] if clause.issubset(negsolvedvars)))
        resolvant = (pclause | nclause) - {curconflict[-1], -curconflict[-1]}
        if resolvant.issubset(negsolvedvars):
          print(resolvant)
        print(pclause, nclause, resolvant)
        #stack.pop()
        #clauses.add(newclause)
        satunsat = True
    if enumch or satunsat:
      stack.pop()
      if x != 0:
        _, _, cs, mp, _ = stack[-1]
        freeliterals = [m for m in mp if m > 0 and len(mp[m]) == 0 and len(mp[-m]) == 0]
        negc = {frozenset(p) for p in cs}
        negc.add(frozenset((-x,)))
        nm = getsatmap(negc)
        for m in freeliterals: nm[m] = set(); nm[-m] = set()
        stack.append((0, False, negc, nm, solved))
      continue
    stack[-1] = (x, True, cs, mp, solved)
    for x in (-1, 3, -2, 7):
      if x in mp: break
    else: x = next(iter(mp))    
    freeliterals = [m for m in mp if m > 0 and len(mp[m]) == 0 and len(mp[-m]) == 0]
    posc = {frozenset(p) for p in cs}
    posc.add(frozenset((x,)))
    pm = getsatmap(posc)
    for m in freeliterals: pm[m] = set(); pm[-m] = set()
    stack.append((x, False, posc, pm, solvedvars))
def solve_dnf(clauses):
  allvars = {abs(y) for x in clauses for y in x} #set.union(*(set(abs(x) for x in c) for c in clauses))
  clauses = {frozenset(c) for c in clauses} #removal duplicate literals
  #if clause implies the rest of the formula, drop the clause - or programmatically speaking if clause is subset of other clause, can drop it
  #can drop any literal the rest of whose clause implies the entire formula
  map = getsatmap(clauses)
  tautology(clauses, map)
  if len(clauses) == 0: return #UNSAT
  usedfreevarcombs = set()
  for clause in clauses:
    if any(-c in clause for c in clause): continue #drop clauses whose literal and negation appear
    freevars = allvars - set(abs(x) for x in clause)
    for perm in range(1 << len(freevars)):
      freevarcomb = clause | {x if (perm & (1 << i)) != 0 else -x for i, x in enumerate(freevars)}
      if any(x.issubset(freevarcomb) for x in usedfreevarcombs): continue
      yield list(freevarcomb)
    usedfreevarcombs.add(clause)
def check_sat(clauses, solution):
  s = frozenset(solution)
  return all(any(c in s for c in clause) for clause in clauses)
def check_dnf(clauses, solution):
  s = frozenset(solution)
  #print(clauses, solution)
  return any(all(c in s for c in clause) for clause in clauses)
def is_sat(clauses, solver):
  for sol in solver(clauses): return True
  return False
def problem_to_sat(problem, transforms, solver):
  tlist = []
  for t in transforms:
    problem, solfunc, checkfunc = t(problem)
    tlist.append((solfunc, checkfunc))
  for sol in solver(problem):
    for f, fc in reversed(tlist):
      sol = f(sol)
      assert fc(sol)
    yield sol
  return ()
def sat_to_tsat_clauses(clauses, parsimonius=True):
  newclauses = []
  #number of new variables and clauses is s where
  #s = sum(len(c) - 3 for c in clauses if len(c) > 3, 0)
  #if we replace every pair of variables for clauses with more than 3 variables
  #x0 or x1 == y === not((x0 or x1) xor y) === not((x0 or x1) and not y or not (x0 or x1) and y)
  #not((x0 or x1) and not y) and not(not (x0 or x1) and y)
  #(not x0 and not x1 or y) and (x0 or x1) or not y
  #(not x0 or y) and (not x1 or y) and (x0 or x1 or not y)
  vs = {abs(y) for x in clauses for y in x}
  nxt = max(vs)+1
  for c in clauses:
    if len(c) == 0: return None
    #elif len(c) == 1: newclauses.append([c[0], c[0], c[0]])
    #elif len(c) == 2: newclauses.append([c[0], c[0], c[1]])
    elif len(c) <= 3: newclauses.append(c)
    else: #transform to conjunction of n-2 clauses
      newclauses.append((c[0], c[1], nxt))
      if parsimonius: newclauses.append((-c[0], -nxt)); newclauses.append((-c[1], -nxt))
      for x in range(len(c)-2-2):
        if parsimonius: newclauses.append((nxt, -nxt-1)); newclauses.append((-c[2+x], -nxt-1))
        newclauses.append((-nxt, c[2+x], nxt+1)); nxt += 1
      newclauses.append((-nxt, c[-2], c[-1])); nxt += 1
  return newclauses, lambda sat: [x for x in sat if x in vs or -x in vs], lambda sol: check_sat(clauses, sol)
def dnf_to_tdnf_clauses(clauses): return #any clause with more than 3 entries - take any 2 e.g. A and B, introduce AB, ~AB, A~B,~A~B, substitute in all later clauses, if clause only uses A or B then duplicate into two clauses, use substitution table to recover solution
def sat_to_monotone_clauses(clauses, parsimonius=True):
  newclauses = []
  vs = {abs(y) for x in clauses for y in x}
  nxt = max(vs)+1
  for c in clauses:
    if len(c) == 0: return None
    numpos = sum(x > 0 for x in c)
    if numpos == 0 or numpos == len(c): newclauses.append(c); continue
    newclauses.append((*(x for x in c if x > 0), nxt))
    newclauses.append((*(x for x in c if x < 0), -nxt))
    if parsimonius:
      if numpos > len(c) - numpos:
        newclauses.extend([(-x, nxt) for x in c if x < 0])
      else: newclauses.extend([(-x, -nxt) for x in c if x > 0])
    nxt += 1
  return newclauses, lambda sat: [x for x in sat if x in vs or -x in vs], lambda sol: check_sat(clauses, sol)
def dnf_to_monotone_clauses(clauses):
  newclauses = []
  vs = {abs(y) for x in clauses for y in x}
  nxt = max(vs)+1
  substitutions, revsubst = {}, {}
  for c in clauses:
    numpos = sum(x > 0 for x in c)
    if numpos == 0 or numpos == len(c): newclauses.append(c); continue
    if numpos > len(c) - numpos:
      s = set(x for x in c if x < 0)
    else: s = set(x for x in c if x > 0)
    for x in s:
      if not x in substitutions: substitutions[x], substitutions[-x] = -nxt if x > 0 else nxt, nxt if x > 0 else -nxt; revsubst[-nxt if x > 0 else nxt], revsubst[nxt if x > 0 else -nxt] = x, -x; nxt += 1
    newclauses.append(tuple(x if not x in s else substitutions[x] for x in c))
  return newclauses, lambda sat: [x if not x in revsubst else revsubst[x] for x in sat], lambda sol: check_dnf(clauses, sol)
def cnf_to_not_dnf(clauses):
  return [tuple(-y for y in x) for x in clauses]
def monotone_dnf_to_twosat(clauses):
  newclauses = []
  vs = {abs(y) for x in clauses for y in x}
  nxt = max(vs)+1
  for c in clauses:
    if len(c) == 0: continue
    #newclauses.append((nxt, -c[0]))
    for i in range(len(c)-1):
      newclauses.append((c[i], -c[i+1]))
    #newclauses.append((c[-1], -nxt))
    newclauses.append((c[-1], -c[0]))
    #nxt += 1
  return newclauses, lambda sat: [x for x in sat], lambda sol: check_dnf(clauses, sol)
def check_hamiltonian_cycle(g, path):
    return len(path) == len(g) and all(path[i+1 if i != len(path)-1 else 0]
                                       in g[path[i]] for i in range(len(path)))
def check_hamiltonian_path(g, path):
  return len(path) == len(g) and all(path[i+1] in g[path[i]]
                                     for i in range(len(path)-1))
#https://dl.acm.org/doi/pdf/10.1145/321850.321854
def hamiltonian_path_admissibility_check(required, requiredrev, undecided, undecidedrev, check):
  while len(check) != 0:
    x = check.pop()
    if len(undecided[x]) == 0 and len(undecidedrev[x]) == 0: continue
    #print(x, required, requiredrev, deleted, deletedrev, undecided, undecidedrev)
    #R1
    if len(undecided[x]) == 1 and not x in required:
      v = next(iter(undecided[x]))      
      if v in requiredrev: return False #F4
      requiredrev[v] = x; undecidedrev[v].remove(x)
      required[x] = v; undecided[x].clear()
      check.add(v)
    if len(undecidedrev[x]) == 1 and not x in requiredrev:
      v = next(iter(undecidedrev[x]))
      if v in required: return False #F4
      required[v] = x; undecided[v].remove(x)
      requiredrev[x] = v; undecidedrev[x].clear()
      check.add(v)
    #D2
    if x in required:
      for y in undecided[x]:
        undecidedrev[y].remove(x) #deletedrev[y].add(x)
        if len(undecidedrev[y]) == 0 and not y in requiredrev: return False
        check.add(y)
      undecided[x].clear() #deleted[x] |= undecided[x]
    if x in requiredrev:
      for y in undecidedrev[x]:        
        undecided[y].remove(x) #deleted[y].add(x)
        if len(undecided[y]) == 0 and not y in required: return False
        check.add(y)
      undecidedrev[x].clear() #deletedrev[x] |= undecidedrev[x]
  return True
def succ_to_pred(succ):
  pred = {x: set() for x in succ}
  for x in succ:
    for y in succ[x]:
      pred[y].add(x)
  return pred
def hamiltonian_path_naive(g, circuit=False):
  allsucc = set.union(*(set(g[x]) for x in g))
  if len(allsucc) == len(g): root = next(iter(g))
  elif len(allsucc) != len(g)-1: return ()
  else: root = next(iter(set(g)-allsucc))
  admiss = [({}, {},  {x: set(g[x]) for x in g}, succ_to_pred(g))]
  path, s, visited = [], [(root, None)], set()
  while len(s) != 0:
    x, pre = s.pop()    
    if pre is None:
      path.append(x)
      visited.add(x)
      pre = iter(g[x])
      if len(path) == 1 or not path[-2] in r or not r[path[-2]] == x:
        if len(path) != 1:
          r, rr, u, ur = admiss[-1]
          admiss.append((r.copy(), rr.copy(), {y: u[y].copy() for y in u}, {y: ur[y].copy() for y in ur}))
          r, rr, u, ur = admiss[-1]
          if not path[-2] in r and x in u[path[-2]]:
            r[path[-2]] = x; rr[x] = path[-2]
            u[path[-2]].remove(x); ur[x].remove(path[-2])
        else: r, rr, u, ur = admiss[-1]
        if not hamiltonian_path_admissibility_check(r, rr, u, ur, set(g) if len(path) == 1 else {path[-2], x}):
          visited.remove(x); path.pop(); admiss.pop()
          continue
      else: admiss.append(admiss[-1])
    for y in pre:
      if y in visited: continue
      s.append((x, pre)); s.append((y, None)); break
    else:
      if len(path) == len(g) and ((not circuit) or root in g[x]): yield list(path)
      visited.remove(x); path.pop(); admiss.pop()
  return ()
#https://www.csie.ntu.edu.tw/~lyuu/complexity/2011/20111018.pdf
def hamiltonian_path_to_sat(g):
  clauses = [] #generic construction
  for x in g: 
    #all nodes must be on the path
    clauses.append([(x-1) * len(g) + y for y in g])
    #all positions in the path must be occupied
    clauses.append([(y-1) * len(g) + x for y in g])
    for y in g: 
      if x < y:
        for z in g: 
          #no node is on the path twice
          clauses.append([-((x-1) * len(g) + z),
                          -((y-1) * len(g) + z)])
          #no two nodes are at the same position on the path
          clauses.append([-((z-1) * len(g) + x),
                          -((z-1) * len(g) + y)])
      if not y in g[x]:
        for k in g: #no edge present
          if k == len(g): continue
          clauses.append([-((k-1) * len(g) + x), -(k * len(g) + y)])
  return clauses, lambda sat: [(x-1) % len(g) + 1 for x in sat if x > 0], lambda sol: check_hamiltonian_path(g, sol)
def hamilitonian_to_graphviz(g, s, t, cols, nvars, colorder, badpath):
  order = [s, *range(1, cols*nvars+1), t, *range(cols*nvars+1, s), *range(t+1, len(g)+1)]
  badpath = {badpath[i]: badpath[i+1] for i in range(len(badpath)-1)}
  return ("digraph {" + ';'.join(str(x) + "->" + str(y) + ("[color=red]" if x in badpath and badpath[x] == y else "") + (
      "[constraint=false]" if x>cols*nvars and x<s or y>cols*nvars and y<t or x<s and y<s and (x-1)//cols==(y-1)//cols else "") for x in order for y in g[x]) +
      "".join("{rank=same;" + "->".join(str(y*cols+1+x) for x in colorder) + "[style=invis]}" for y in range(nvars))
        + "}")
#https://opendsa-server.cs.vt.edu/ODSA/Books/Everything/html/threeSAT_to_hamiltonianCycle.html
#https://www.cs.princeton.edu/~wayne/kleinberg-tardos/pearson/08PolynomialTimeReductions-2x2.pdf
#https://www.mog.dog/files/SP2019/Sipser_Introduction.to.the.Theory.of.Computation.3E.pdf
#3k+3 instead of 2k fixes path issues leading to ambiguous solutions...
def tsat_to_hamiltonian_path(clauses, noambiguity=True, someambiguity=False, necklace=False):
    #necklace like method of putting gating nodes between variable levels, does not help resolve 2K  but does resolve 2K+2 case, not needed in 3K+3, just for proof and drawing clarity
    vs = {abs(y) for x in clauses for y in x}
    g = {}
    cols = 3 * (len(clauses) + 1) if noambiguity else 2 * len(clauses) + (2 if someambiguity else 0)
    s = len(clauses) + cols * len(vs) + 1
    t = s+1
    for x in vs:
        if noambiguity:
            for i, c in enumerate(clauses):
                g[(x-1)*cols+3*i+1] = [(x-1)*cols+3*i+2, (x-1)*cols+3*i
                                       if i != 0 else
                                       (x-1)*cols+len(clauses)*3+2]
                g[(x-1)*cols+3*i+2] = [(x-1)*cols+3*i+1, (x-1)*cols+3*i+3]
                g[(x-1)*cols+3*i+3] = [(x-1)*cols+3*i+2, (x-1)*cols+3*i+4
                                       if i != len(clauses)-1 else
                                       (x-1)*cols+len(clauses)*3+3]
            g[(x-1)*cols+len(clauses)*3+1] = [
                (x-1)*cols+len(clauses)*3+2] + (
                ([x*cols+len(clauses)*3+1, x*cols+len(clauses)*3+3] if not necklace else [t+x])
                if x != len(vs) else [t])
            g[(x-1)*cols+len(clauses)*3+2] = [
                (x-1)*cols+len(clauses)*3+1, (x-1)*cols+1]
            g[(x-1)*cols+len(clauses)*3+3] = [
                (x-1)*cols+len(clauses)*3] + (
                ([x*cols+len(clauses)*3+1, x*cols+len(clauses)*3+3] if not necklace else [t+x])
                if x != len(vs) else [t])
            if necklace and x!=1: g[t+x-1] = [(x-1)*cols+len(clauses)*3+1, (x-1)*cols+len(clauses)*3+3]
        elif someambiguity:
            for i, c in enumerate(clauses):
                g[(x-1)*cols+2*i+1] = [(x-1)*cols+2*i+2, (x-1)*cols+2*i
                                       if i != 0 else
                                       (x-1)*cols+len(clauses)*2+1]
                g[(x-1)*cols+2*i+2] = [(x-1)*cols+2*i+1, (x-1)*cols+2*i+3
                                       if i != len(clauses)-1 else
                                       (x-1)*cols+len(clauses)*2+2]
            g[(x-1)*cols+len(clauses)*2+1] = [
                (x-1)*cols+1] + (
                ([x*cols+len(clauses)*2+1, x*cols+len(clauses)*2+2] if not necklace else [t+x])
                if x != len(vs) else [t])
            g[(x-1)*cols+len(clauses)*2+2] = [
                (x-1)*cols+len(clauses)*2] + (
                ([x*cols+len(clauses)*2+1, x*cols+len(clauses)*2+2] if not necklace else [t+x])
                if x != len(vs) else [t])            
            if necklace and x!=1: g[t+x-1] = [(x-1)*cols+len(clauses)*2+1, (x-1)*cols+len(clauses)*2+2]
        else:
            for i, c in enumerate(clauses):
                g[(x-1)*cols+2*i+1] = [(x-1)*cols+2*i+2, (x-1)*cols+2*i
                                       if i != 0 else
                                       (t if x == len(vs) else (x*cols+1 if not necklace else t+x))]
                g[(x-1)*cols+2*i+2] = [(x-1)*cols+2*i+1, (x-1)*cols+2*i+3
                                       if i != len(clauses)-1 else
                                       (t if x == len(vs) else ((x+1)*cols if not necklace else t+x))]
                if not necklace and (i == 0 or i == len(clauses)-1) and x != len(vs):
                    if i == 0: g[(x-1)*cols+2*i+1].append((x+1)*cols)
                    elif i == len(clauses)-1: g[(x-1)*cols+2*i+2].append(x*cols+1)
            if necklace and x!=1: g[t+x-1] = [(x-1)*cols+1, (x-1)*cols+2*i+2]
    for i, c in enumerate(clauses):
        g[cols * len(vs)+i+1] = []
        for x in c: #left-to-right is the negation of a variable's path
            g[cols * len(vs)+i+1].append(
                (abs(x)-1)*cols+(3 if noambiguity else 2)*i+(1 if x > 0 else 2))
            g[(abs(x)-1)*cols+(3 if noambiguity else 2)*i+(2 if x > 0 else 1)].append(
                cols * len(vs)+i+1)
    #g[t] = [s] for hamiltonian cycle equivalent
    g[s], g[t] = [len(clauses)*3+1 if noambiguity else (len(clauses)*2+1 if someambiguity else 1), cols], [] #[s] if circuit
    assert len(g) == 2 + len(clauses) + cols * len(vs) + (len(vs)-1 if necklace else 0)
    clauserange = {cols * len(vs)+i+1 for i in range(len(clauses))}
    #if necklace: clauserange = clauserange | set(range(t, t+len(vs)))
    def sat_to_sol(osol):
      sol = {osol[i]: osol[i+1] for i in range(len(osol)-1)}
      #if circuit: sol = {osol[i]: osol[(i+1)%len(osol)] for i in range(len(osol))}
      check = [{sol[cols*x+(3 if noambiguity else 2)*j+1] in
        {cols*x+(3 if noambiguity else 2)*j+2} | clauserange for j in range(len(clauses))}
          for x in range(len(vs))]
      #assert all(len(x)==1 for x in check)
      if not all(len(x)==1 for x in check):
        print(clauses, hamilitonian_to_graphviz(g, s, t, cols, len(vs), [cols-3, cols-2, *range(cols-3), cols-1] if noambiguity else [cols-2, *range(cols-2), cols-1] if someambiguity else range(cols), osol))
        assert False, osol
      sol = [-i-1 if next(iter(x)) else i+1 for i, x in enumerate(check)]
      if not check_sat(clauses, sol):
        print(clauses, hamilitonian_to_graphviz(g, s, t, cols, len(vs), [cols-3, cols-2, *range(cols-3), cols-1] if noambiguity else [cols-2, *range(cols-2), cols-1] if someambiguity else range(cols), osol))
        assert False
      #sol = [x for x in osol if x <= cols * len(vs)]
      #if not noambiguity and not all(
      #    set(sol[i:i+cols])==set(range(i+1, cols+i+1))
      #    for i in range(0, cols*len(vs), cols)): raise ValueError
      """
      if not all(sol[i+2*j+2] == sol[i+2*j+3] + (1 if sol[i] % cols == 0 else -1) for j in range(len(clauses)-1)
        for i in range(0, cols*len(vs), cols)):
          print(clauses, hamilitonian_to_graphviz(g, s, t, cols, len(vs), [cols-3, cols-2, *range(cols-3), cols-1] if noambiguity else [cols-2, *range(cols-2), cols-1] if someambiguity else range(cols), osol))
          assert False, osol
      sol = [((sol[i]-1) // cols + 1) * (
          (1 if sol[i] % cols == 0 else -1) if noambiguity or someambiguity else 
          (-1 if (sol[i]-1) % cols == 0 else 1))
             for i in range(0, cols*len(vs), cols)]
      if not check_sat(clauses, sol) or 1 in sol and -1 in sol:
        print(clauses, hamilitonian_to_graphviz(g, s, t, cols, len(vs), [cols-3, cols-2, *range(cols-3), cols-1] if noambiguity else [cols-2, *range(cols-2), cols-1] if someambiguity else range(cols), osol))
        assert False, osol
      """
      return sol
    return g, sat_to_sol, lambda sol: check_sat(clauses, sol)
def digraph_to_gvc(g, cycle):
  return "digraph {" + ";".join(str(x) + "->" + str(y) +
                                ("[color=blue;fillcolor=blue]"
                                 if cycle.index(x) == (cycle.index(y)-1) % len(g) else "")
                                for x in g for y in g[x]) + "}"
def graph_to_gvc(g, cycle):
  return "graph {" + ";".join(str(x) + "--" + str(y) +
                              ("[color=blue;fillcolor=blue]"
                               if cycle.index(x) == (cycle.index(y)-1) % len(g) or 
                               cycle.index(y) == (cycle.index(x)-1) % len(g) else "")
                              for x in g for y in g[x] if x > y) + "}"
def digraph_to_gvp(g, path):
  p = {path[i]: path[i+1] for i in range(len(path)-1)}
  return "digraph {" + ";".join(str(x) + "->" + str(y) +
                                ("[color=blue;fillcolor=blue]" if x in p and p[x]==y else "")
                                for x in g for y in g[x]) + "}"
def graph_to_gvp(g, path):
  p = {path[i]: path[i+1] for i in range(len(path)-1)}
  return "graph {" + ";".join(str(x) + "--" + str(y) +
                              ("[color=blue;fillcolor=blue]"
                               if x in p and p[x] == y or y in p and p[y] == x else "")
                              for x in g for y in g[x] if x > y) + "}"
    
#Stalmarck's method
#https://research.cs.wisc.edu/wpis/papers/tr1699.pdf
def pysat(clauses):
  from pysat.solvers import Glucose3
  g = Glucose3()
  for clause in clauses: g.add_clause(clause)
  if g.solve():
    return g.enum_models()
  return ()
def pycosat(clauses):
  import pycosat
  return pycosat.itersolve(clauses)
def pycryptosat(clauses):
  from pycryptosat import Solver
  g = Solver()
  for clause in clauses: g.add_clause(clause)
  sat, solution = g.solve()
  while sat:
    sol = [i if x else -i for i, x in enumerate(solution) if not x is None]
    yield sol
    g.add_clause([-x for x in sol])
    sat, solution = g.solve()
def satnaive(clauses): #O(2^n) naive variant
  vars = set(y if y > 0 else -y for x in clauses for y in x)
  for i in range(0, 1 << len(vars)):
    curvars = {z if (i & (1 << j)) != 0 else -z for j, z in enumerate(vars)}
    if all(len(curvars.intersection(z)) != 0 for z in clauses):
      yield list(sorted(curvars, key=lambda x: x if x > 0 else -x))
  #0 yielded solutions is UNSAT
def gettwosatgraph(clauses):
  succ = {}
  for x, y in clauses:
    if not -x in succ: succ[-x] = list(); succ[x] = list()
    if not -y in succ: succ[-y] = list(); succ[y] = list()
    succ[-x].append(y)
    if x != y: succ[-y].append(x)
  return succ
def twosat(clauses): #O(m+n) variant using SCCs
  import sccreach
  sccs = [set(scc) for scc in sccreach.tarjan_scc(gettwosatgraph(clauses))]
  sol = set()
  #enumerating topological sorts would yield redundant answers - storing all solutions hardly ideal nor is extra complexity of such an operation
  #one simple idea e.g. pycrpytosat style would be adding clauses to block previously found solutions
  #only topological sorts which have non-dependency conflicting changes occur would have unique solutions - how to do this?
  #note that counting topological sorts is in #P complete as is #2SAT
  for scc in sccs:
    for x in scc:
      if -x in scc: return #UNSAT
      if not x in sol and not -x in sol: sol.add(x)
  return list(sorted(sol, key=lambda x: x if x > 0 else -x))
def latexformula(clauses):
  return "\\wedge".join("(" + "\\vee ".join(("" if x > 0 else "\lnot ") + "x_" + str(abs(x)) for x in clause) + ")" for clause in clauses)
def htmlsatformula(clauses):
  return "&and;".join("(" + "&or;".join(str(x) for x in clause) + ")" for clause in clauses)
def twosatvisual(clauses, showunsat, outdir): #O(m+n) variant using SCCs
  import sccreach
  succ = gettwosatgraph(clauses)
  import graph
  sccs = [set(scc) for scc in sccreach.tarjan_scc(gettwosatgraph(clauses))]
  nodetoscc = {x: i for i, scc in enumerate(sccs) for x in scc}
  formula = htmlsatformula(clauses)  
  implications = "&and;".join("(" + str(-x) + "&rArr;" + str(y) + ")&and;(" + str(-y) + "&rArr;" + str(x) + ")" for x, y in clauses)
  dot = ["".join(["subgraph " + "cluster_" + str(i) + " {\n\tnode[style=filled];\n\t" + (graph.do_graphviz_dot_digraph({x: {y for y in succ[x] if y in scc} for x in succ if x in scc}) if len(scc) != 1 else str(next(iter(scc)))) + ";\n\tcolor=blue;\n\tlabel=\"" + str(i+1) + "\";" + "\n}\n" for i, scc in enumerate(sccs)]), graph.do_graphviz_dot_digraph({x: {y for y in succ[x] if nodetoscc[x] != nodetoscc[y]} for x in succ}), "labelloc=t; label=<" + formula + "<br/>" + implications + ">"]
  sol = set()
  for scc in sccs:
    for x in scc:
      if -x in scc:
        #graph.do_graphviz_dot(graph.do_graphviz_dot_text(dot + [str(x) + "[color=red];" + str(-x) + "[color=red]"]), outdir, "twosat")
        if showunsat: graph.do_graphviz_dot(graph.do_graphviz_dot_text(dot + [";".join(str(x) + "[style=filled; color=red];" + str(-x) + "[style=filled; color=red]" for x in succ if x > 0 and nodetoscc[x] == nodetoscc[-x])]), outdir, "twosat" + str(hash(tuple(clauses))))
        return #UNSAT
      if not x in sol and not -x in sol: sol.add(x)
  graph.do_graphviz_dot(graph.do_graphviz_dot_text(dot + [";".join(str(x) + "[style=filled; color=green]" for x in sol)]), outdir, "twosat" + str(hash(tuple(clauses))))
  print(latexformula(clauses))
  print("\\wedge".join("(" + ("" if -x > 0 else "\lnot ") + "x_" + str(abs(-x)) + "\implies " + ("" if y > 0 else "\lnot ") + "x_" + str(abs(y)) + ")\wedge(" + ("" if -y > 0 else "\lnot ") + "x_" + str(abs(-y)) + "\implies " + ("" if x > 0 else "\lnot ") + "x_" + str(abs(x)) + ")" for x, y in clauses))
  return list(sorted(sol, key=lambda x: x if x > 0 else -x))
def alltwosat(clauses, f):
  sol = f(clauses)
  #print(sol)
  stack = [(sol, 0)] if not sol is None else []
  while len(stack) != 0:
    sol, idx = stack.pop()
    yield sol
    for i, x in enumerate(sol[idx:]):
      solin = f(clauses + [(y, y) for y in sol[:idx+i]] + [(-x, -x)])
      if not solin is None: stack.append((solin, idx+i+1))
CALL, NOP, RET, MODINST, PUSH, POP, PEEK, FUNC, JC, JMP, DATA, LOAD, STORE = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
OPSTRINGS = ["CALL", "NOP", "RET", "MODINST", "PUSH", "POP", "PEEK", "FUNC", "JC", "JMP", "DATA", "LOAD", "STORE"]
SAT, UNSAT = -1, -2
def selfmodvm(instructions): pass
def selfmodtwosat(clauses):
  def setsol(x):
    #print(x)
    if not x in sol and not -x in sol: sol.add(x)
  sol = set() #only output
  succ = gettwosatgraph(clauses) #only input
  #print(succ)
  instructions, registers, s = [], [0], []
  nodeaddr = {}
  index = len(instructions)
  instructions.append((DATA, 0)) #index
  def makenodeaddr(x, y): return lambda: nodeaddr[x] + y
  def getsuccaddr(x, y): return lambda: makenodeaddr(succ[x][registers[0]-1], y)()
  def checklowlink(x): return lambda: registers[0] >= instructions[nodeaddr[x]+lowlinkloc][1]
  def makefinishscc(x): return lambda: nodeaddr[x]+callloc+1 != registers[0]  
  def checksamescc(x): return lambda: registers[0] != instructions[nodeaddr[-x]+nodeaddrsetloc][1]
  def checkonstack(x): return lambda: len(s) != x
  #def checknotonstack(x): return lambda: len(s) == x
  def makesetsol(x): return lambda: setsol(x)
  def getval(x): return lambda: x
  #def makeprint(x): return lambda: print(x, instructions[nodeaddr[x]+nodeaddrloc][1], instructions[nodeaddr[x]+lowlinkloc][1], s)
  for x in succ:
    instructions.append((CALL, makenodeaddr(x, 0)))
  starttopo = len(instructions)
  instructions.append((DATA, starttopo+1)) #topoptr
  instructions.append((JMP, lambda: SAT))
  blueprint = []
  nodeaddrloc = len(blueprint)
  blueprint.append(lambda x: (DATA, None)) #index
  blueprint.append(lambda x: (LOAD, index))
  #blueprint.append(lambda x: (FUNC, makeprint(x)))
  blueprint.append(lambda x: (STORE, lambda: registers[0], makenodeaddr(x, nodeaddrloc)))
  blueprint.append(lambda x: (STORE, lambda: registers[0], makenodeaddr(x, lowlinkloc)))
  blueprint.append(lambda x: (STORE, lambda: registers[0] + 1, lambda: index))
  peekretloc = len(blueprint)
  blueprint.append(lambda x: (POP,))
  blueprint.append(lambda x: (MODINST, makenodeaddr(x, retloc), lambda: (JMP, getval(registers[0]))))
  blueprint.append(lambda x: (MODINST, makenodeaddr(x, onstackloc), lambda: (JC, checkonstack(len(s)), checksccloc-onstackloc)))
  blueprint.append(lambda x: (MODINST, makenodeaddr(x, topopstackloc), lambda: (JC, checkonstack(len(s)), callloc-topopstackloc)))
  blueprint.append(lambda x: (MODINST, makenodeaddr(x, nodeaddrloc+1), lambda: (RET,)))
  counterloc = len(blueprint)
  blueprint.append(lambda x: (DATA, len(succ[x])))
  loopedgeloc = len(blueprint)
  blueprint.append(lambda x: (JC, lambda: registers[0] == 0, onstackloc-loopedgeloc))
  blueprint.append(lambda x: (STORE, lambda: registers[0] - 1, makenodeaddr(x, counterloc)))
  topopstackloc = len(blueprint)
  blueprint.append(lambda x: (JC, lambda: True, callloc-topopstackloc))
  blueprint.append(lambda x: (MODINST, getsuccaddr(x, peekretloc), lambda: (PEEK,)))
  callloc = len(blueprint)
  blueprint.append(lambda x: (CALL, getsuccaddr(x, 0)))
  checklowlinkloc = len(blueprint)
  blueprint.append(lambda x: (JC, checklowlink(x), counterloc - checklowlinkloc))
  blueprint.append(lambda x: (STORE, lambda: registers[0], makenodeaddr(x, lowlinkloc)))
  blueprint.append(lambda x: (MODINST, makenodeaddr(x, checksccloc), lambda: (JC, lambda: True, lowlinkloc-checksccloc)))
  nextedgeloc = len(blueprint)
  blueprint.append(lambda x: (JC, lambda: True, counterloc - nextedgeloc))
  onstackloc = len(blueprint)
  blueprint.append(lambda x: (JC, lambda: True, checksccloc-onstackloc))
  blueprint.append(lambda x: (PUSH, makenodeaddr(x, callloc+1)))
  checksccloc = len(blueprint)
  blueprint.append(lambda x: (JC, lambda: False, lowlinkloc-checksccloc))
  #blueprint.append(lambda x: (FUNC, makeprint(x)))
  nextnodeloc = len(blueprint)
  blueprint.append(lambda x: (POP,))
  blueprint.append(lambda x: (MODINST, lambda: instructions[starttopo][1], lambda: (JMP, getval(registers[0]+nodeaddrsetloc-(callloc+1)))))
  blueprint.append(lambda x: (STORE, makenodeaddr(x, nodeaddrloc), lambda: registers[0]+nodeaddrsetloc-(callloc+1)))
  blueprint.append(lambda x: (STORE, lambda: registers[0]+nexttopoloc-(callloc+1), lambda: starttopo))
  blueprint.append(lambda x: (STORE, lambda: len(succ), lambda: registers[0]+nodeaddrloc-(callloc+1)))
  gotonextnodeloc = len(blueprint)
  blueprint.append(lambda x: (JC, makefinishscc(x), nextnodeloc-gotonextnodeloc))
  currentnodeloc = len(blueprint)
  lowlinkloc = len(blueprint)
  blueprint.append(lambda x: (DATA, None)) #lowlink
  #blueprint.append(lambda x: (FUNC, makeprint(x)))
  retloc = len(blueprint)
  blueprint.append(lambda x: (JMP, lambda: 0))
  nodeaddrsetloc = len(blueprint)
  blueprint.append(lambda x: (DATA, None)) #scc id
  checksamesccloc = len(blueprint)
  blueprint.append(lambda x: (JC, checksamescc(x), satloc-checksamesccloc))
  blueprint.append(lambda x: (JMP, lambda: UNSAT))
  satloc = len(blueprint)
  blueprint.append(lambda x: (FUNC, makesetsol(x)))
  nexttopoloc = len(blueprint)
  blueprint.append(lambda x: (JMP, lambda: SAT))
  for x in succ:
    nodeaddr[x] = len(instructions)
    instructions.extend([b(x) for b in blueprint])
  #print(len(instructions), nodeaddr, checklowlinkloc)
  #print({x: nodeaddr[x]+callloc+1 for x in succ})
  instptr = 0
  while instptr != SAT and instptr != UNSAT:
    #print(instptr, OPSTRINGS[instructions[instptr][0]], registers[0], s)
    if instructions[instptr][0] == CALL:
      s.append(instptr+1)
      instptr = instructions[instptr][1]()
    elif instructions[instptr][0] == FUNC:
      instructions[instptr][1](); instptr += 1
    elif instructions[instptr][0] == PEEK:
      registers[0] = s[-1]; instptr += 1
    elif instructions[instptr][0] == PUSH:
      s.append(instructions[instptr][1]()); instptr += 1
    elif instructions[instptr][0] == POP:
      registers[0] = s.pop(); instptr += 1
    elif instructions[instptr][0] == RET:
      instptr = s.pop()
    elif instructions[instptr][0] == JC:
      if instructions[instptr][1](): instptr += instructions[instptr][2]
      else: instptr += 1
    elif instructions[instptr][0] == JMP:
      instptr = instructions[instptr][1]()
    elif instructions[instptr][0] == NOP: instptr += 1
    elif instructions[instptr][0] == DATA:
      registers[0] = instructions[instptr][1]; instptr += 1
    elif instructions[instptr][0] == LOAD:
      registers[0] = instructions[instructions[instptr][1]][1]; instptr += 1
    elif instructions[instptr][0] == STORE:
      assert instructions[instructions[instptr][2]()][0] == DATA
      instructions[instructions[instptr][2]()] = (DATA, instructions[instptr][1]()); instptr += 1
    elif instructions[instptr][0] == MODINST:
      #print("MODINST", instructions[instptr][1](), instructions[instptr][2]()[0])
      instructions[instructions[instptr][1]()] = instructions[instptr][2](); instptr += 1
    else: assert False
  if instptr == UNSAT: return None
  assert len(s) == 0, s
  #print("SAT" if instptr == SAT else "UNSAT", len(s), s)
  return list(sorted(sol, key=lambda x: x if x > 0 else -x))
def kpartitions(l, k):
  import itertools
  if k == 1: yield [l]; return
  for i in range(1, len(l)-k+1+1):
    s = set(range(1, len(l)))
    for comb in itertools.combinations(s, i-1):
      for t in kpartitions([l[idx] for idx in s - set(comb)], k-1):
        yield [[l[0], *(l[idx] for idx in comb)], *t]
def stirlingsecond(n, k): import math; return sum((-1 if (i & 1 != 0) else 1) * math.comb(k, i)*((k-i)**n) for i in range(k+1)) // math.factorial(k)
def kpartsizes(n, k, min=1):
  if k == 1:
    if min is None or n >= min: yield [n]
    return
  for i in range(1 if min is None else min, n-k+2):
    for t in kpartsizes(n-i, k-1, min=i if not min is None else min):
      yield [i, *t]
assert len(list(kpartitions([3,5,7,11,13], 3))) == stirlingsecond(5, 3)
assert len(list(kpartitions([2,3,5,7,11,13], 3))) == stirlingsecond(6, 3)
#print(list(kpartsizes(7, 3, None)), list(kpartsizes(7, 3)))
def random_sat_gen(n, k, acs, iterations):
  import random
  vars = [-i for i in range(1, n+1)] + [i for i in range(1, n+1)]
  for sizes in kpartsizes(k*acs, k):
    for _ in range(iterations):
      clauses = []
      for size in sizes:
        clauses.append([random.choice(vars) for _ in range(size)])
      yield clauses
def verify_sat():
  funcs = [satnaive, pysat, dpll, dpall]#, cdcl]
  for testformula in random_sat_gen(8, 5, 3, 10):
    res = [[(check_sat(testformula, x), frozenset(x)) for x in f(testformula)] for f in funcs]
    if (all(len(x)==0 for x in res)): continue
    assert(all(x[0] for x in res))
    assert len({len(x) for x in res}) == 1
    assert len({frozenset(x) for x in res}) == 1
    print(testformula)
def enum_sat(free_vars): #symmetric solutions are included
  for clause_map in range(1<<(1<<free_vars)):
    yield [[k+1 if (1<<k) & j != 0 else -k-1 for k in range(free_vars)] for j in range(1<<free_vars) if (1<<j) & clause_map != 0]
def enum_3sat(free_vars):
  import math, itertools
  if free_vars <= 2: yield from enum_sat(free_vars); return
  ncombs = math.comb(free_vars, 3)
  combs = list(itertools.combinations(range(1, free_vars+1), 3))
  for clause_map in range(1<<(2*2*2*ncombs)):
    yield [
      [combs[comb][x] if j & (1<<x) & j != 0 else -combs[comb][x] for x in range(3)] for j in range(2*2*2) for comb in range(ncombs) if 1<<(j+comb*8) & clause_map != 0
    ]
def smallest_counter_example():
  for free_vars in range(1, 5):
    for testformula in enum_3sat(free_vars): #enum_sat(free_vars):
      if len(testformula) == 0: continue
      s = set.union(*(set(x) for x in testformula))
      if not all(x in s or -x in s for x in range(1, free_vars+1)): continue
      print(testformula)
      psat = [(check_sat(testformula, x), frozenset(x)) for x in pysat(testformula)]      
      #hsat = [(check_sat(testformula, x), frozenset(x)) for x in problem_to_sat(testformula, [sat_to_tsat_clauses, tsat_to_hamiltonian_path], hamiltonian_path_naive)]
      #hsatn = [(check_sat(testformula, x), frozenset(x)) for x in problem_to_sat(testformula, [sat_to_tsat_clauses, lambda x: tsat_to_hamiltonian_path(x, True, False, True)], hamiltonian_path_naive)]
      #fails with [[1, -2]] digraph {6->1[color=red];6->2;1->2[color=red][constraint=false];1->3;1->4;2->1[constraint=false];2->4;2->5[color=red][constraint=false];3->4[constraint=false];3->7[color=red];3->5[constraint=false];4->3[color=red][constraint=false];4->7;5->1[constraint=false];5->4[color=red][constraint=false]{rank=same;1->2[style=invis]}{rank=same;3->4[style=invis]}}
      #hsat2k = [(check_sat(testformula, x), frozenset(x)) for x in problem_to_sat(testformula, [sat_to_tsat_clauses, lambda x: tsat_to_hamiltonian_path(x, False, False, False)], hamiltonian_path_naive)]
      #fails with [[-1, -2], [1, -2]] digraph {11->1;11->4[color=red];1->2[constraint=false];1->13;1->9[color=red][constraint=false];2->1[color=red][constraint=false];2->3[constraint=false];3->4[constraint=false];3->2[color=red][constraint=false];4->3[constraint=false];4->13[color=red];4->10[constraint=false];5->6[constraint=false];5->12[color=red];5->9[constraint=false];6->5[color=red][constraint=false];6->7[constraint=false];7->8[constraint=false];7->6[constraint=false];7->10[color=red][constraint=false];8->7[color=red][constraint=false];8->12;9->2[constraint=false];9->6[color=red][constraint=false];10->3[color=red][constraint=false];10->8[constraint=false];13->5;13->8[color=red]{rank=same;1->2->3->4[style=invis]}{rank=same;5->6->7->8[style=invis]}}
      #hsat2kn = [(check_sat(testformula, x), frozenset(x)) for x in problem_to_sat(testformula, [sat_to_tsat_clauses, lambda x: tsat_to_hamiltonian_path(x, False, False, True)], hamiltonian_path_naive)]
      #fails with [[-1, 2]] digraph {10->3;10->4[color=red];1->2[constraint=false];1->3[color=red][constraint=false];1->9[constraint=false];2->1[color=red][constraint=false];2->4[constraint=false];3->1[constraint=false];3->7;3->8[color=red];4->2[constraint=false];4->7[color=red];4->8;5->6[color=red][constraint=false];5->7[constraint=false];6->5[constraint=false];6->8[constraint=false];6->9[color=red][constraint=false];7->5[color=red][constraint=false];7->11;8->6[constraint=false];8->11[color=red];9->2[color=red][constraint=false];9->5[constraint=false]{rank=same;3->1->2->4[style=invis]}{rank=same;7->5->6->8[style=invis]}}
      #hsat2k2 = [(check_sat(testformula, x), frozenset(x)) for x in problem_to_sat(testformula, [sat_to_tsat_clauses, lambda x: tsat_to_hamiltonian_path(x, False, True, False)], hamiltonian_path_naive)]
      hsat2k2n = [(check_sat(testformula, x), frozenset(x)) for x in problem_to_sat(testformula, [sat_to_tsat_clauses, lambda x: tsat_to_hamiltonian_path(x, False, True, True)], hamiltonian_path_naive)]
      #print(len(psat), len(hsat), len(hsatn), len(hsat2k2n))
      #assert len({frozenset(x) for x in (psat, hsat)}) == 1
      #assert len({frozenset(x) for x in (psat, hsatn)}) == 1
      #assert len({frozenset(x) for x in (psat, hsat2k)}) == 1
      #assert len({frozenset(x) for x in (psat, hsat2kn)}) == 1
      #assert len({frozenset(x) for x in (psat, hsat2k2)}) == 1
      assert len({frozenset(x) for x in (psat, hsat2k2n)}) == 1
smallest_counter_example()
#verify_sat()
def test_sat():
  import timeit
  import os
  this_dir = os.path.join('D:\\', 'Source', 'repos', 'efop', 'efop_362', 'work', 'wp-a', 'a11', 'morse', 'dyngraph')
  cfg_dir = os.path.join(this_dir, 'cfgs')
  output_dir = os.path.join(this_dir, 'results')
  getsatlib(cfg_dir)
  hg1 = {1: [2, 5, 6], 2: [1, 3, 8], 3: [2, 4, 10], 4: [3, 5, 12], 5: [1, 4, 14],
         6: [1, 7, 15], 7: [6, 8, 19], 8: [2, 7, 9], 9: [8, 10, 20], 10: [3, 9, 11],
         11: [10, 12, 16], 12: [4, 11, 13], 13: [12, 14, 17], 14: [5, 13, 15], 15: [6, 14, 18],
         16: [11, 17, 20], 17: [13, 16, 18], 18: [15, 17, 19], 19: [7, 18, 20], 20: [9, 16, 19]}
  hg2 = {1: [2, 5, 6], 2: [1, 3, 4, 5], 3: [2, 4], 4: [2, 3, 5, 6],
         5: [1, 2, 4, 6], 6: [1, 4, 5]}
  for testgraph in (hg1,hg2):
    satht = [x for x in problem_to_sat(testgraph, [hamiltonian_path_to_sat], pysat)]
    nht = [x for x in hamiltonian_path_naive(testgraph)]
    assert len(satht) == len(nht) and {frozenset(x) for x in satht} == {frozenset(x) for x in nht}
  testf1 = [(1, 2, 3), (-1, -2, 3), (1, -2, -3), (-1, 2, -3)]
  testf2 = [(1, 2, -3), (2, 3), (-2,), (-1, 3)]
    #print([(check_sat(testformula, x), x) for x in satnaive(testformula)])
  #https://codegolf.stackexchange.com/questions/1933/solve-2-sat-boolean-satisfiability
  testformula1 = [(1, 2), (-1, 2), (-2, 1), (-1, -2)] #2x4 UNSAT
  testformula2 = [(1, 2), (2, 3), (3, 4), (-1, -3), (-2, -4)] #4x5 single solution
  testformula3 = [(1, 4), (-2, 5), (3, 7), (2, -5), (-8, -2), (3, -1), (4, -3), (5, -4), (-3, -7), (6, 7), (1, 7), (-7, -1)] #8x12 3 solutions
  #[x for x in alltwosat(testformula3, lambda x: twosatvisual(x, testformula3 == x, output_dir))]
  testformula4 = [(21, 34), (-49, -12), (7, 18), (-5, -1), (28, 17), (3, 55), (36, 33), (-6, -50), (44, -41), (-55, 3), (14, -54), (-30, 13), (-13, 60), (54, -16), (-48, 41), (3, 6), (49, -48), (34, -4), (14, -46), (58, -20), (52, 54), (-37, -25), (56, -1), (50, -9), (-58, 11), (-19, 58), (17, 8), (56, 51), (38, 49), (-13, 36), (24, 9), (18, -29), (6, 49), (-30, 4), (-13, -20), (31, -9), (54, -4), (37, 17), (-48, -8), (-7, -45), (-3, -42), (27, -22), (-50, -27), (47, 19), (-21, 20), (-20, -37), (-42, 12), (-35, 1), (-41, -19), (11, 30), (-17, -48), (21, -49), (16, -53), (57, 57), (15, 2), (-6, -7), (-23, -28), (-12, -17), (-59, -36), (38, -6), (-16, -6), (21, -14), (17, -7), (3, -49), (-55, -13), (22, -52), (24, -56), (22, -42), (13, -4), (-8, -16), (-55, -7), (-12, 48), (52, 18), (-47, 44), (-22, -23), (-29, -23), (-53, 57), (-38, 54), (43, -53), (49, -18), (-60, 58), (-5, -14), (16, 34), (-24, -43), (10, -21), (-52, -40), (-45, -22), (-5, -11), (-32, -11), (-15, 11), (-24, 44), (-17, -15), (10, -27), (8, -26), (-36, 24), (13, 1), (59, -34), (-40, -25), (11, -22)] #60x99 large sat
  testformula5 = [(1, 4), (1, -3, -8), (1, 8, 12), (2, 11), (-3, -7, 13), (-3, -7, -13, 9), (8, -7, -9), (5, 6, 10)]
  testformula6 = [(1, 2, 3, 4, 5, 6, 7), (-1, 2, 3, 4, -5, -6, -7)]
  for testformula in (testformula1, testformula2, testformula3, testformula5, testformula6,): #(testf1, testf2, testformula1, testformula2, testformula3): #, testformula4):
    satn = [(check_sat(testformula, x), frozenset(x)) for x in satnaive(testformula)]
    psat = [(check_sat(testformula, x), frozenset(x)) for x in pysat(testformula)]
    dpl = psat #[(check_sat(testformula, x), frozenset(x)) for x in dpll(testformula)]
    dpa = psat #[(check_sat(testformula, x), frozenset(x)) for x in dpall(testformula)]
    cdc = psat #[(check_sat(testformula, x), frozenset(x)) for x in cdcl(testformula)]
    tsat = [(check_sat(testformula, x), frozenset(x)) for x in problem_to_sat(testformula, [sat_to_tsat_clauses], pysat)]
    hsat = [(check_sat(testformula, x), frozenset(x)) for x in problem_to_sat(testformula, [sat_to_tsat_clauses, lambda x: tsat_to_hamiltonian_path(x, False, True, True), hamiltonian_path_to_sat], pysat)]
    print(hsat)
    print(len(satn), len(psat), len(dpl), len(dpa), len(cdc), len(tsat), len(hsat))
    #assert len({len(x) for x in (satn, psat, dpl, dpa, cdc, tsat, hsat)}) == 1
    assert len({frozenset(x) for x in (satn, psat, dpl, dpa, cdc, tsat, hsat)}) == 1
  for testformula in getrand3cnf(cfg_dir):
    results = []
    for lbl, f in (("pysat", pysat), ("DPLL", dpll), ("DP", dpall), ("CDCL", cdcl)):
      print(lbl, timeit.timeit(lambda: results.append({(check_sat(testformula, x), frozenset(x)) for x in f(testformula)}), number=1))
    assert all(results[0] == x for x in results[1:])
  for testformula in (testformula1, testformula2, testformula3, testformula4):
    print([(check_sat(testformula, x), x) for x in satnaive(testformula)])
    print([(check_sat(testformula, x), x) for x in pysat(testformula)])
    print([(check_sat(testformula, x), x) for x in pycosat(testformula)])
    print([(check_sat(testformula, x), x) for x in pycryptosat(testformula)])
    print([(check_sat(testformula, x), x) for x in alltwosat(testformula, twosat)])
    print([(check_sat(testformula, x), x) for x in alltwosat(testformula, selfmodtwosat)])
    print([(check_sat(testformula, x), x) for x in (twosat(testformula),) if not x is None])
    print([(check_sat(testformula, x), x) for x in (selfmodtwosat(testformula),) if not x is None])
def test_csat():
  testformula = [(1, -2, -3), (-4, 5, 6)]
  allvars = {abs(y) for x in testformula for y in x} #set.union(*(set(abs(x) for x in c) for c in testformula))
  psat = [(check_sat(testformula, x), frozenset(x)) for x in pysat(testformula)]
  msat = [(check_sat(testformula, x), frozenset(x)) for x in problem_to_sat(testformula, [sat_to_monotone_clauses], pysat)]
  dnfformula = cnf_to_not_dnf(testformula)
  assert set(cnf_to_not_dnf(sat_to_monotone_clauses(testformula)[0])) == set(sat_to_monotone_clauses(dnfformula)[0])
  monotonednf = cnf_to_not_dnf(sat_to_monotone_clauses(testformula)[0])
  #invsat = [(check_dnf(dnfformula, x), frozenset(x)) for x in solve_dnf(dnfformula)]
  #invsat = [(check_dnf(monotonednf, x), frozenset(x)) for x in solve_dnf(monotonednf)]
  invsat = [(check_dnf(dnfformula, x), frozenset(x)) for x in problem_to_sat(dnfformula, [lambda x: dnf_to_monotone_clauses(x)], solve_dnf)]
  twsat = [(check_dnf(monotonednf, x), frozenset(x)) for x in problem_to_sat(monotonednf, [monotone_dnf_to_twosat], lambda x: alltwosat(x, twosat))]
  #twsat = [(check_dnf(dnfformula, x), frozenset(x)) for x in problem_to_sat(dnfformula, [lambda x: dnf_to_monotone_clauses(x), monotone_dnf_to_twosat], lambda x: alltwosat(x, twosat))]
  print(dnfformula, monotonednf, monotone_dnf_to_twosat(monotonednf)[0], twsat)
  assert len(psat) == len(set(psat))
  assert len(invsat) == len(set(invsat)), (len(invsat), len(set(invsat)))
  print(len(allvars), 1 << len(allvars), len(msat), len(set(msat)), len(psat), len(invsat), len(twsat))
#test_csat()
test_sat()
#https://people.sc.fsu.edu/~jburkardt/data/cnf/cnf.html
#https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html