#https://en.wikipedia.org/wiki/Determinant
#https://en.wikipedia.org/wiki/Parity_of_a_permutation
#permutation parity is needed which is complex as sorting if not maintained during generation, although cycle decomposition can linearize it
#https://github.com/python/cpython/blob/main/Modules/itertoolsmodule.c
def permutations(iterable, r=None):
  pool = tuple(iterable)
  n = len(pool)
  r = n if r is None else r
  if r > n: return
  indices = list(range(n))
  cycles = list(range(n, n-r, -1))
  parity = 0
  yield tuple(pool[i] for i in indices[:r]), parity
  while n:
    for i in reversed(range(r)):
      cycles[i] -= 1
      if cycles[i] == 0:
        if ((n-i) & 1) == 0: parity = 1 - parity
        indices[i:] = indices[i+1:] + indices[i:i+1]
        cycles[i] = n - i
      else:
        j = cycles[i]
        parity, indices[i], indices[-j] = 1 - parity, indices[-j], indices[i]
        yield tuple(pool[i] for i in indices[:r]), parity
        break
    else: return
#https://www.researchgate.net/publication/235134418_A_Simplified_Fraction-Free_Integer_Gauss_Elimination_Algorithm
def gaussianElimInteger(x): #division-free Gaussian elimination
  h = 0 #Initialization of pivot row
  k = 0 #Initialization of pivot column
  oddswaps, mulFactor = False, 1
  m = x.shape[0]
  n = x.shape[1]
  while (h < m and k < n):
    #Find the k-th pivot
    res = [(abs(x[i, k]), i) for i in range(h, m) if x[i, k] != 0]
    i_max = -1 if len(res) == 0 else min(res)[1] #index of maximum which is first one with a bit set, also should consider absolute value but here its not applicable since no negative values though zero still possible
    if (i_max < h or x[i_max, k] == 0): #No pivot in this column, pass to next column
      k += 1
    else:
      #swap rows h and i_max
      if (h != i_max): x[[h, i_max]] = x[[i_max, h]]; oddswaps = not oddswaps
      #Do for all rows below pivot
      for i in range(h+1, m):
        #Do for all remaining elements in current row
        mulFactor *= x[h, k]
        for j in range(k+1, n): x[i, j] = x[h, k] * x[i, j] - x[i, k] * x[h, j]
        x[i, k] = 0
      h += 1
      k += 1 #Increase pivot row and column
  return x, oddswaps, mulFactor #ret
def backSubstitution(x):
  h = 0 #Initialization of pivot row
  k = 0 #Initialization of pivot column
  m = x.shape[0]
  n = x.shape[1]
  while (h < m and k < n):
    #Find the k-th pivot
    res = [(abs(x[i, k]), i) for i in range(h, m) if x[i, k] != 0]
    i_max = -1 if len(res) == 0 else min(res)[1] #index of maximum which is first one with a bit set, also should consider absolute value but here its not applicable since no negative values though zero still possible
    if (i_max < h or x[i_max, k] == 0): #No pivot in this column, pass to next column
      k += 1
    else:
      #swap rows h and i_max
      if (h != i_max): x[[h, i_max]] = x[[i_max, h]]
      #Do for all rows below pivot
      #reduced row echelon form (RREF) is obtained without a back substitution step by starting from 0 and skipping h      
      for j in range(n-1, k-1, -1): x[h, j] //= x[h, k]
      for i in range(m):
        if (h == i): continue
        f = x[i, k] // x[h, k]
        x[i, k] = 0
        #Do for all remaining elements in current row
        for j in range(k+1, n):
          x[i, j] -= (x[h, j] * f)
      h += 1
      k += 1 #Increase pivot row and column
  return x #ret
def gaussianElimIntegerPolynomial(x): #division-free Gaussian elimination
  h = 0 #Initialization of pivot row
  k = 0 #Initialization of pivot column
  oddswaps, mulFactor = False, [1]
  m = len(x)
  n = len(x[0])
  while (h < m and k < n):
    #Find the k-th pivot
    res = [(abs(x[i][k][0]), i) for i in range(h, m) if x[i][k] != [] and x[i][k] != [0]]
    i_max = -1 if len(res) == 0 else min(res)[1] #index of maximum which is first one with a bit set, also should consider absolute value but here its not applicable since no negative values though zero still possible
    if (i_max < h or x[i_max][k] == 0): #No pivot in this column, pass to next column
      k += 1
    else:
      #swap rows h and i_max
      if (h != i_max): x[h], x[i_max] = x[i_max], x[h]; oddswaps = not oddswaps
      #Do for all rows below pivot
      for i in range(h+1, m):
        mulFactor = mulPolyR(mulFactor, x[h][k], None)
        for j in range(k+1, n): x[i][j] = addPoly(mulPolyR(x[h][k], x[i][j], None), [-x for x in mulPolyR(x[i][k], x[h][j], None)])
        x[i][k] = []
      h += 1
      k += 1 #Increase pivot row and column
  return x, oddswaps, mulFactor #ret
def dosign(parity, x): return -x if parity else x
def plusminus(parity, base, x): return base - x if parity else base + x
def prod(x, y): return x * y
def multiprod(l):
  import functools
  return functools.reduce(prod, l)
def determinant(mat):
  n = len(mat)
  if n == 0: return 0
  return sum(dosign(parity, multiprod((mat[i][sigma[i]] for i in range(n)))) for sigma, parity in permutations(range(n)))
def determinant_gaussian(mat):
  import numpy as np
  ref, oddswaps, mulFactor = gaussianElimInteger(np.array(mat))
  return dosign(oddswaps, multiprod((ref[i, i] for i in range(len(ref))))) // mulFactor
def permanent(mat):
  import itertools
  n = len(mat)
  if n == 0: return 1
  return sum(multiprod((mat[i][sigma[i]] for i in range(n))) for sigma in itertools.permutations(range(n)))
def graySet(i, n):
  return [j for j in range(n) if (i & (1 << j)) != 0]
def grayCode(n): return (graySet(i ^ i >> 1, n) for i in range(0, 1<<n))
#print(list(len(x) for x in grayCode(5)))
#https://www2.math.upenn.edu/~wilf/website/CombinatorialAlgorithms.pdf pages 222-223
def permanent_ryser(mat):
  n = len(mat)
  if n == 0: return 1
  invset = {i for i in range(n-1)}
  #this is not O(2^(n-1)*n) as it is still n^2 without the Gray code yielding indices to add and subtract making the inner summation O(1) instead of O(n)
  #return dosign((n & 1) != 0, sum(dosign((len(S) & 1) != 0, multiprod((sum(mat[i][j] for j in S) for i in range(n)))) for S in grayCode(n)))
  rowadj = [mat[i][n-1] - sum(mat[i][j] for j in range(n-1)) for i in range(n)]
  return dosign(((n-1) & 1) != 0, sum(dosign((len(S) & 1) != 0, multiprod((rowadj[i] + (sum(mat[i][j] for j in S)<<1) for i in range(n)))) for S in grayCode(n-1))) >> (n-1)
def lsbIndex(x): return ((1 + (x ^ (x-1))) >> 1).bit_length() #count of consecutive trailing zero bits
def nextGrayCode(gcode, i):
  idx = lsbIndex(i)-1
  gcode[idx] = 1 - gcode[idx]
  return idx
#print([lsbIndex(x) for x in range(16)])
def permanent_ryser_gray(mat): #optimal row-major order
  n = len(mat)
  if n == 0: return 1
  gcode, rowsums = [0 for _ in range(n)], [mat[i][n-1] - sum(mat[i][j] for j in range(n-1)) for i in range(n)] #[0 for _ in range(n)]
  tot = multiprod(rowsums)
  #additions: (1+n)(2^n-1) multiplications: (2^n-1)(n-1)
  for i in range(1, 1<<(n-1)):
    idx = nextGrayCode(gcode, i)
    if gcode[idx]:
      for j in range(n): rowsums[j] += (mat[j][idx] << 1)
    else:
      for j in range(n): rowsums[j] -= (mat[j][idx] << 1)
    tot = plusminus((i & 1) != 0, tot, multiprod(rowsums))
  return dosign(((n-1) & 1) != 0, tot)>>(n-1)
#def getDeltas(n): return ([1 if (i & (1 << j)) != 0 else -1 for j in range(n)] for i in range(1<<n))
def getDeltas(n): return ([1 if (i & (1 << j)) != 0 else 0 for j in range(n)] for i in range(1<<n))
def permanent_glynn(mat):
  #Gray code order of deltas would yield reduction from n^2 to n similar to Ryser
  n = len(mat)
  if n == 0: return 1
  #return sum(dosign((sum(x < 0 for x in delta) & 1) != 0, multiprod((sum(delta[i] * mat[i][j] for i in range(n)) for j in range(n)))) for delta in [[1] + x for x in getDeltas(n-1)]) >> (n-1)
  return sum(dosign((sum(delta) & 1) != 0, multiprod((mat[n-1][j] + sum(dosign(delta[i]!=0, mat[i][j]) for i in range(n-1)) for j in range(n)))) for delta in getDeltas(n-1)) >> (n-1)
def permanent_glynn_gray(mat): #optimal row-major order
  n = len(mat)
  if n == 0: return 1
  #additions: n(n-1)+2^(n-1)-1 multiplications: n-1
  delta, rowsums = [1 for _ in range(n)], [sum(mat[i]) for i in range(n)] #[0 for _ in range(n)]
  tot = multiprod(rowsums)
  for i in range(1, 1<<(n-1)):
    idx = nextGrayCode(delta, i)
    if delta[idx]:
      for j in range(n): rowsums[j] += (mat[j][idx] << 1) #mat[j][idx]
    else:
      for j in range(n): rowsums[j] -= (mat[j][idx] << 1) #mat[j][idx]
    tot = plusminus((i & 1) != 0, tot, multiprod(rowsums))
  return tot >> (n-1) #tot
#can extend matrix and preserve permanent by putting ones on the diagonal
#print(list(permanent([[1 if i == j or i < 3 and j < 3 else 0 for j in range(n)] for i in range(n)]) for n in range(3, 8)))
#print(list(permanent([[1 for _ in range(n)] for _ in range(n)]) for n in range(7)))
#print(list(permanent_ryser([[1 for _ in range(n)] for _ in range(n)]) for n in range(7)))
#print(list(permanent_ryser_gray([[1 for _ in range(n)] for _ in range(n)]) for n in range(7)))
#print(list(permanent_glynn([[1 for _ in range(n)] for _ in range(n)]) for n in range(7)))
#print(list(permanent_glynn_gray([[1 for _ in range(n)] for _ in range(n)]) for n in range(7)))
permfuncs = [
  permanent, permanent_ryser, permanent_ryser_gray, permanent_glynn, permanent_glynn_gray]
#empirical validation of correctness
def validate_permanent():
  import math
  nmax = 8
  alloneresult = list(math.factorial(n) for n in range(0, nmax))
  for n in range(nmax):
    Adiag = [[1 if i == j or i < 3 and j < 3 else 0 for j in range(n)] for i in range(n)]
    A = [[1 for _ in range(n)] for _ in range(n)]
    for func in permfuncs:
      res = func(A)
      assert res == alloneresult[n], (func.__name__, n, res, alloneresult[n])
      res = func(Adiag)
      assert res == alloneresult[min(3, n)], (func.__name__, n, res, alloneresult[min(3, n)]) 
def timing_permanent():
  import timeit
  nmax = 8
  xaxis = list(range(nmax))
  results = [[] for _ in permfuncs]
  for n in xaxis:
    A = [[1 for _ in range(n)] for _ in range(n)]
    for i, func in enumerate(permfuncs):
      results[i].append(timeit.timeit(lambda: func(A), number=2)) 
  import matplotlib.pyplot as plt
  fig = plt.figure()
  ax1 = fig.add_subplot(111)
  for i, resset in enumerate(results):
    ax1.plot(xaxis, resset, label=permfuncs[i].__name__)
  ax1.set_xlabel("Size (n)")
  ax1.set_ylabel("Time (s)")
  ax1.legend()
  ax1.set_title("0-1 Permanent Computation of Square Matrix A (n=|A|)")
  fig.savefig("zonepermtime.svg", format="svg")
validate_permanent()
timing_permanent()
#http://oeis.org/A072831 Number of bits in n!.
def get_fact_bitsizes(n):
  import math
  return math.factorial(n).bit_length()
print(list(get_fact_bitsizes(n) for n in range(64)))
#https://en.wikipedia.org/wiki/Hafnian
#https://the-walrus.readthedocs.io/en/latest/hafnian.html
def hafnian(mat): #symmetric matrix
  if (len(mat) & 1) != 0: return 0
  n = len(mat) // 2
  if n == 0: return 1
  import itertools, math
  return sum(multiprod((mat[sigma[2*i]][sigma[2*i+1]] for i in range(n))) for sigma in itertools.permutations(range(2*n))) // (math.factorial(n) * (1 << n))
def complete_graph_perf_match(iterable): #O(n^2) and recursive...
  pool = tuple(iterable)
  n = len(pool) // 2
  if n == 0: return
  elif n == 1: yield [pool]; return
  for i in range(1, n*2):
    yield from [[(pool[0], pool[i]), *x] for x in complete_graph_perf_match(pool[1:i] + pool[i+1:])]
#https://oeis.org/A000085
def num_single_pair_match(n):
  import math
  fact = math.factorial(n)
  return sum(fact // ((math.factorial(n-2*k)*math.factorial(k)) << k) for k in range(n // 2 + 1))
def complete_graph_single_pair_match(iterable):
  pool = tuple(iterable)
  n = len(pool)
  if n == 0: return
  if n == 1: yield [(pool[0], pool[0])]
  elif n == 2: yield from [[pool], [(pool[0], pool[0]), (pool[1], pool[1])]]; return
  for i in range(1, n):
    yield from [[(pool[0], pool[i]), *x] for x in complete_graph_single_pair_match(pool[1:i] + pool[i+1:])]
  yield from [[(pool[0], pool[0]), *x] for x in complete_graph_single_pair_match(pool[1:])]
#print(list(complete_graph_single_pair_match(range(4))))
#print([num_single_pair_match(x) for x in range(10)])
#assert all(len(list(complete_graph_single_pair_match(range(n)))) == num_single_pair_match(n) for n in range(1, 10))
#http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.52.3057&rep=rep1&type=pdf
def linear_extension_perf_match(iterable):
  #partial ordered set (poset) relations since groups are all size 2, are the even elements are ordered, and each pair of elements are ordered
  pool = tuple(iterable); n = len(pool)
  le, li = list(range(n)), list(range(n))
  a, b = [le[i] for i in range(1, n-1, 2)], [le[i] for i in range(2, n-1, 2)]  
  MaxPair = n // 2 - 1
  IsPlus = [True]
  #MaxPair, n, le, li, a, b = 2, 4, [0, 1, 2, 3], [0, 1, 2, 3], [0, 2], [1, 3] #a1,b1,a2,b2 = 0, 1, 2, 3
  def toSet(): return [(iterable[li[i*2]], iterable[li[i*2+1]]) for i in range(n // 2)]
  yield toSet()
  def transpose(x, y):
    le[li[x]], le[li[y]], li[x], li[y] = le[li[y]], le[li[x]], li[y], li[x]
  def Switch(i):
    if i == -1: IsPlus[0] = not IsPlus[0]
    else:
      transpose(a[i], b[i]); a[i], b[i] = b[i], a[i]
  def Move(x, isRight):
    transpose(x, le[li[x]+(1 if isRight else -1)])
  def isComparable(x, y):
    #return x==0 and y==2 or x==1 and y==3 #or y==0 and x==2 or y==1 and x==3
    return (x & 1) == 0 and (y & 1) == 0 and x < y or (x & 1) == 0 and y == x+1
  def Right(x, i): return li[x] != n-1 and not isComparable(le[li[x]], le[li[x]+1]) and (i is None or le[li[x]+1] != b[i])
  def GenLE(i):
    if i >= 0:
      yield from GenLE(i-1)
      mrb = 0; typical = False
      while i < MaxPair and Right(b[i], None):
        mrb += 1; Move(b[i], True)
        if IsPlus[0]: yield toSet()
        yield from GenLE(i-1)
        mra = 0
        if Right(a[i], i):
          typical = True
          while True:
            mra += 1; Move(a[i], True)
            if IsPlus[0]: yield toSet()
            yield from GenLE(i-1)
            if not Right(a[i], i): break
        if typical:
          Switch(i-1)
          if IsPlus[0]: yield toSet()
          yield from GenLE(i-1)
          mla = mra + (-1 if (mrb & 1) != 0 else 1)
          for _ in range(0, mla):
            Move(a[i], False)
            if IsPlus[0]: yield toSet()
            yield from GenLE(i-1)
      if typical and (mrb & 1) != 0: Move(a[i], False)
      else: Switch(i-1)
      if IsPlus[0]: yield toSet()
      yield from GenLE(i-1)
      for _ in range(mrb):
        Move(b[i], False)
        if IsPlus[0]: yield toSet()
        yield from GenLE(i-1)
  yield from GenLE(MaxPair)
#print(list(complete_graph_perf_match(range(2))))
#print(list(complete_graph_perf_match(range(4))))
#assert sorted(list(complete_graph_perf_match(range(6)))) == sorted(list(linear_extension_perf_match(range(6))))
#assert sorted(list(complete_graph_perf_match(range(8)))) == sorted(list(linear_extension_perf_match(range(8))))
def hafnian_perf_match(mat, isLoop=False, linExt=True): #symmetric matrix
  if (len(mat) & 1) != 0: return 0
  n = len(mat) // 2
  if n == 0: return 1
  if isLoop: matchfunc = complete_graph_single_pair_match
  elif linExt: matchfunc = linear_extension_perf_match
  else: matchfunc = complete_graph_perf_match
  return sum(multiprod((mat[u][v] for u, v in matches)) for matches in matchfunc(range(2*n)))
#for Hafnian, adding [[0 1] [1 0]] direct sum along the added pairs of diagonals preserves the computation
#print(list(hafnian_perf_match([[1 if i>=4 and j>=4 and (i==j+1 or j==i+1) or i < 4 and j < 4 else 0 for j in range(n)] for i in range(n)]) for n in range(4, 11, 2)))
#for loop Hafnian, adding ones on the diagonal extends the matrix while preserving the computation
#print(list(hafnian_perf_match([[1 if i==j or i < 4 and j < 4 else 0 for j in range(n)] for i in range(n)], isLoop=True) for n in range(4, 11, 2)))
def addPoly(a, b):
  alen, blen = len(a), len(b)
  c = [0] * max(alen, blen)
  clen = len(c)
  for i in range(0, clen):
    if (i >= alen): c[i] = b[i]
    elif (i >= blen): c[i] = a[i]
    else: c[i] = a[i] + b[i]
  import itertools
  return c if clen == 0 or c[-1] != 0 else list(reversed(list(itertools.dropwhile(lambda cr: cr == 0, reversed(c)))))
def mulPolyR(a, b, clen):
  alen, blen = len(a), len(b)
  if (alen == 0): return a
  if (blen == 0): return b
  if clen is None: clen = alen + blen -1
  p = [0] * min(clen, (alen + blen - 1))
  for i in range(0, blen):
    if (b[i] == 0): continue
    for j in range(0, alen):
      if (a[j] == 0) or i + j >= clen: continue
      p[i + j] += a[j] * b[i]
  import itertools
  return list(reversed(list(itertools.dropwhile(lambda c: c == 0, reversed(p)))))
#https://en.wikipedia.org/wiki/Polynomial_long_division#Pseudo-code
def divmodPoly(a, b):
  #if (len(b) == 0) raise ValueError
  alen, blen = len(a), len(b)
  q, r = [0] * alen, a
  bneg = mulPolyR(b, [-1], None)
  rlen = len(r)
  d = (rlen - 1) - (blen - 1)
  while (rlen != 0 and d >= 0):
    aoffs = d
    assert r[-1] == (r[-1] // b[-1]) * b[-1]
    q[aoffs] = r[-1] // b[-1]
    if (q[aoffs] == 0): break
    r = addPoly(r, q[:aoffs] + mulPolyR(bneg, [q[aoffs]], None))
    rlen = len(r)
    d = (rlen - 1) - (blen - 1)
  assert r == []
  import itertools
  return list(reversed(list(itertools.dropwhile(lambda c: c == 0, reversed(q)))))
#https://arxiv.org/abs/1107.4466
def hafnian_ryser_time(mat):
  if (len(mat) & 1) != 0: return 0
  n = len(mat) // 2
  if n == 0: return 1
  B = [[[c] for c in r] for r in mat]
  h = 0
  for X in powerset(list(range(1, n+1))):
    X = set(X)
    g = [1]
    Bl = B
    for i in range(1, n+1):
      if i in X:
        g = mulPolyR(g, [1] + Bl[0][1], n+1)
        Bl = [[addPoly([0] + addPoly(mulPolyR(Bl[0][j+2], Bl[1][k+2], n), mulPolyR(Bl[0][k+2], Bl[1][j+2], n))[:n-1], Bl[j+2][k+2])
              if j != k else 0 for k in range(2*(n-i))] for j in range(2*(n-i))]
      else:
        Bl = [r[2:] for r in Bl[2:]]
    if len(g) > n: h += dosign(((n - len(X)) & 1) != 0, g[n])
  return h
def characteristicPolynomial(mat):
  import functools
  ref, oddswaps, mulFactor = gaussianElimIntegerPolynomial([[[-c] if j != i else [-c, 1] for j, c in enumerate(r)] for i, r in enumerate(mat)])
  #ref, oddswaps, mulFactor = gaussianElimIntegerPolynomial([[[c] if j != i else [c, -1] for j, c in enumerate(r)] for i, r in enumerate(mat)])
  print(list(ref[i][i] for i in range(len(ref))))
  poly = [dosign(oddswaps, x) for x in functools.reduce(lambda x, y: mulPolyR(x, y, None), (ref[i][i] for i in range(len(ref))))]  
  poly = divmodPoly(poly, mulFactor)
  #import numpy as np
  #assert poly == [round(x) for x in reversed(np.poly(np.array(mat)))], (poly, [round(x) for x in reversed(np.poly(np.array(mat)))])
  return poly #if poly[-1] != -1 else [-x for x in poly]
assert characteristicPolynomial([[-1, 4, 0, 0, 0], [0, 3, 0, 0, 0], [0, -4, -1, 0, 0], [3, -8, -4, 2, 1], [1, 5, 4, 1, 4]]) == [-21, -17, 20, 8, -7, 1]
def matMul(mat1, mat2):
  m1, n1, m2, n2 = len(mat1), len(mat1[0]), len(mat2), len(mat2[0])
  assert n1 == m2
  out = [[0 for _ in range(n2)] for _ in range(m1)]
  for i in range(m1):
    for j in range(n2):
      for k in range(n1):
        out[i][j] += mat1[i][k] * mat2[k][j]
  return out
def directSum(mat1, mat2):
  m1, n1, m2, n2 = len(mat1), len(mat1[0]), len(mat2), len(mat2[0])
  return ([[r[i] if i < len(r) else 0 for i in range(n1+n2)] for r in mat1] +
          [[r[i-m1] if i >= m1 else 0 for i in range(n1+n2)] for r in mat2])
#http://bulletin.pan.pl/(56-4)391.pdf
def minimalPolynomial(mat):
  #lbda = characteristicPolynomial(mat)
  z, n = mat, len(mat)
  M = [[0 for _ in range(n+1)] for _ in range(n*n)]
  for i in range(n):
    for j in range(n):
      if i == j: M[i*n+j][0] = 1
  for k in range(n):
    for i in range(n):
      for j in range(n):
        M[i*n+j][k+1] = -z[i][j] if k == n-1 else z[i][j]
    if k != n-1: z = matMul(z, mat)
  import numpy as np
  ref, _, _ = gaussianElimInteger(np.array(M))
  rank = sum(1 for i in range(n+1) if ref[i, i] != 0)
  #assert rank == np.linalg.matrix_rank(np.array(M)), (rank, np.linalg.matrix_rank(np.array(M)))
  return [-x for x in backSubstitution(ref[:rank, :rank+1])[:, rank]] + [1]
assert minimalPolynomial([[3, -3, 2], [-1, 5, -2], [-1, 3, 0]]) == [8, -6, 1]
#http://oeis.org/A003418 Least common multiple (or LCM) of {1, 2, ..., n} for n >= 1, a(0) = 1.
def factoriallcms(n):
  import math, functools
  return functools.reduce(lambda x, y: x*y//math.gcd(x, y), range(1, n+1))
#[factoriallcms(n) for n in range(1, 15)]
#https://arxiv.org/pdf/1805.12498.pdf
def hafnian_eff(mat, isInt=False, isLoop=False):
  if (len(mat) & 1) != 0: return 0
  n = len(mat) // 2
  import functools, math
  if isInt: fact = math.factorial(n); nfact = multiprod([fact] * n)
  if n == 0: return 1
  h = 0
  for X in powerset(list(range(0, n))):
    AZ = matix(mat, [z for y in ((2*x, 2*x+1) for x in X) for z in y])
    colswap = functools.reduce(directSum, [[[0, 1], [1, 0]]] * len(X))
    B = matMul(colswap, AZ) #paper says column swap but this is a row swap AZ*colswap is a column swap, does not matter as long as loop correction is opposite to it
    #minpoly = minimalPolynomial(B)
    #characteristicPolynomial(B)
    tr = [sum(B[i][i] for i in range(len(B)))]
    Bpow = B
    while len(tr) != n:
      Bpow = matMul(Bpow, B)
      #if len(tr) >= len(minpoly)-1:
      #  assert sum(Bpow[i][i] for i in range(len(Bpow))) == -sum((0 if j >= len(minpoly) else minpoly[j])*tr[j + len(tr)-len(minpoly)+1] for j in range(len(minpoly)-1))
      tr.append(sum(Bpow[i][i] for i in range(len(Bpow))))
      #tr.append(-sum((0 if j >= len(minpoly) else minpoly[j])*tr[j + len(tr)-len(minpoly)+1] for j in range(len(minpoly)-1)))
    if isLoop:
      v = [[AZ[i][i] for i in range(len(AZ))]]; vt = [[x] for x in v[0]]
      loopCorrections = [] #[matMul(matMul(v,  colswap), vt)[0][0]]
      #w = [[v[0][i^1]] for i in range(len(v[0]))]
      w = matMul(colswap, vt)
      #paper has mistake that (XB)^(k-1) where it should be (B^(k-1))X
      while len(loopCorrections) != n:
        #Bpow = B if len(loopCorrections) == 1 else matMul(Bpow, B)
        #loopCorrections.append(matMul(matMul(v, matMul(Bpow, colswap)), vt)[0][0])
        loopCorrections.append(matMul(v, w)[0][0])
        w = matMul(B, w)
      if isInt: lbda = [0] + [tr[k-1] * (fact // k) + loopCorrections[k-1] * fact for k in range(1, n+1)]
      else: lbda = [0] + [tr[k-1] / (2 * k) + loopCorrections[k-1] / 2 for k in range(1, n+1)]
    else:
      if isInt: lbda = [0] + [tr[k-1] * (fact // k) for k in range(1, n+1)]
      else: lbda = [0] + [tr[k-1] / (2 * k) for k in range(1, n+1)]
    if isInt: poly, powfact, fixfact, = [1], nfact, fact
    else: poly, fixfact = [1], 1
    z = 0
    for j in range(1, n+1):
      if isInt: fixfact //= j; powfact //= fact
      else: fixfact *= j
      poly = mulPolyR(lbda, poly, None)
      if len(poly) > n:
        if isInt: z += ((poly[n] * fixfact) * powfact) << (n-j)
        else: z += poly[n] / fixfact
    h += -z if ((n - len(X)) & 1) != 0 else z
  return (h >> n) // (fact * nfact) if isInt else h
#https://the-walrus.readthedocs.io/en/latest/_modules/thewalrus/_torontonian.html
def powerset(s): #empty set handled as special case
  import itertools
  for i in range(1, len(s)+1):
    yield from itertools.combinations(s, i)
#https://the-walrus.readthedocs.io/en/latest/code/quantum.html pip install thewalrus
def genident(n):
  return [[1 if i == j else 0 for j in range(n)] for i in range(n)]
def submat(A, B): n = len(A); return [[A[i][j] - B[i][j] for j in range(n)] for i in range(n)]
def matix(mat, ix): return [[mat[i][j] for j in ix] for i in ix]
def torontonian(mat):
  N = len(mat); assert((N & 1) == 0) #N=2*d
  N >>= 1 #determinant of empty matrix is 1
  return sum((1 if ((N - len(Z)) & 1) == 0 else -1)/np.sqrt(determinant(submat(genident(len(Z)<<1), matix(mat, [*Z, *(x + N for x in Z)])))) for Z in powerset(list(range(N)))) + (1 if (N & 1) == 0 else -1)
#https://en.wikipedia.org/wiki/Cholesky_decomposition
def cholesky(mat): #Cholesky–Banachiewicz algorithm
  #return [] if len(mat) == 0 else np.linalg.cholesky(mat)
  n = len(mat)
  L = [[0. for _ in range(n)] for _ in range(n)]
  for i in range(n):
    for j in range(i):
      L[i][j] = (mat[i][j] - sum(L[i][k]*L[j][k].conjugate() for k in range(j)))/L[j][j]
    L[i][i] = np.sqrt(mat[i][i] - sum(L[i][k]*L[i][k].conjugate() for k in range(i)))
  #if n != 0: print(L, np.linalg.cholesky(mat))
  return L
def quad_cholesky(L, Z, idx, mat):
  Ls = matix(L, Z)
  for i in range(idx, len(mat)):
    for j in range(idx, i):
      Ls[i][j] = (mat[i][j] - sum(Ls[i][k]*Ls[j][k].conjugate() for k in range(j)))/Ls[j][j]
    Ls[i][i] = np.sqrt(mat[i][i] - sum(Ls[i][k]*Ls[i][k].conjugate() for k in range(i)))
  return Ls
#https://arxiv.org/pdf/2109.04528.pdf
def rec_torontonian(mat):
  def recursiveTor(L, modes, mat, n):
    tor, start = 0., 0 if len(modes) == 0 else modes[-1]+1
    for i in range(start, n):
      nextModes = modes + [i]
      nm, idx = len(mat) >> 1, (i - len(modes))*2
      Z = [x for x in range(nm*2) if x != idx and x != idx+1]
      Az = matix(mat, Z); nm -= 1
      #Ls = cholesky(submat(genident(2*nm), Az))
      Ls = quad_cholesky(L, Z, idx, submat(genident(2*nm), Az))
      det = 1 if nm == 0 else multiprod((Ls[i][i]*Ls[i][i] for i in range(2*nm)))
      tor += (1 if (len(nextModes) & 1) == 0 else -1)/np.sqrt(det) + recursiveTor(Ls, nextModes, Az, n)
    return tor
  n = len(mat) >> 1
  mat = matix(mat, [j for i in range(n) for j in (i, i + n)])
  L = cholesky(submat(genident(2*n), mat))
  det = multiprod((L[i][i]*L[i][i] for i in range(2*n)))
  return 1/np.sqrt(det) + recursiveTor(L, [], mat, n) #(1 if (n & 1) == 0 else -1)

assert determinant([[-2, -1, 2], [2, 1, 4], [-3, 3, -1]]) == 54
assert determinant_gaussian([[-2, -1, 2], [2, 1, 4], [-3, 3, -1]]) == 54
#M = MatrixSpace(QQ, 3, 3)
#A = M([-2, -1, 2, 2, 1, 4, -3, 3, -1])
#A.charpoly(); A.minpoly()
assert characteristicPolynomial([[-2, -1, 2], [2, 1, 4], [-3, 3, -1]]) == [-54, -5, 2, 1]
assert determinant([[3, 4], [5, 6]]) == -2
permexample = [[1, 1, 1, 1], [2, 1, 0, 0], [3, 0, 1, 0], [4, 0, 0, 1]]
assert permanent(permexample) == 10
assert permanent_ryser(permexample) == 10
assert permanent_ryser_gray(permexample) == 10
assert permanent_glynn(permexample) == 10
assert permanent_glynn_gray(permexample) == 10
haftest = (
  ([[0, 0, 0, 1, 0, 0], [0, 0, 0, 1, 1, 0], [0, 0, 0, 1, 1, 1], [1, 1, 1, 0, 0, 0], [0, 1, 1, 0, 0, 0], [0, 0, 1, 0, 0, 0]], 1),
  ([[-1, 1, 1, -1, 0, 0, 1, -1], [1, 0, 1, 0, -1, 0, -1, -1], [1, 1, -1, 1, -1, -1, 0, -1], [-1, 0, 1, -1, -1, 1, -1, 0], [0, -1, -1, -1, -1, 0, 0, -1], [0, 0, -1, 1, 0, 0, 1, 1], [1, -1, 0, -1, 0, 1, 1, 0], [-1, -1, -1, 0, -1, 1, 0, 1]], 4),
  ([[1, 1, 0, 0, 0, 0, 0, 1, 0, 0], [1, 1, -1, 0, -1, 1, 1, 1, 0, -1], [0, -1, -1, -1, 0, -1, -1, 0, -1, 1], [0, 0, -1, 1, -1, 1, -1, 0, 1, -1], [0, -1, 0, -1, -1, -1, -1, 1, -1, 1], [0, 1, -1, 1, -1, 1, -1, -1, 1, -1], [0, 1, -1, -1, -1, -1, 1, 0, 0, 0], [1, 1, 0, 0, 1, -1, 0, 1, 1, -1], [0, 0, -1, 1, -1, 1, 0, 1, 1, 1], [0, -1, 1, -1, 1, -1, 0, -1, 1, 1]], -13),
  ([[-1, 0, -1, -1, 0, -1, 0, 1, -1, 0, 0, 0], [0, 0, 0, 0, 0, -1, 0, 1, -1, -1, -1, -1], [-1, 0, 0, 1, 0, 0, 0, 1, -1, 1, -1, 0], [-1, 0, 1, -1, 1, -1, -1, -1, 0, -1, -1, -1], [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, -1, 0], [-1, -1, 0, -1, 0, 0, 1, 1, 1, 1, 1, 0], [0, 0, 0, -1, 0, 1, 1, -1, -1, 0, 1, 0], [1, 1, 1, -1, 0, 1, -1, 1, -1, -1, -1, -1], [-1, -1, -1, 0, 0, 1, -1, -1, -1, 1, -1, 0], [0, -1, 1, -1, 1, 1, 0, -1, 1, -1, 1, 1], [0, -1, -1, -1, -1, 1, 1, -1, -1, 1, 0, -1], [0, -1, 0, -1, 0, 0, 0, -1, 0, 1, -1, 1]], 13),
  ([[-1, 1, 0, 1, 0, -1, 0, 0, -1, 1, -1, 1, 0, -1], [1, -1, 1, -1, 1, 1, -1, 0, -1, 1, 1, 0, 0, -1], [0, 1, 1, 1, -1, 1, -1, -1, 0, 0, -1, 0, -1, -1], [1, -1, 1, -1, 1, 0, 1, 1, -1, -1, 0, 0, 1, 1], [0, 1, -1, 1, 0, 1, 0, 1, -1, -1, 1, 1, 0, -1], [-1, 1, 1, 0, 1, 1, -1, 0, 1, -1, -1, -1, 1, -1], [0, -1, -1, 1, 0, -1, -1, -1, 0, 1, -1, 0, 1, -1], [0, 0, -1, 1, 1, 0, -1, 0, 0, -1, 0, 0, 0, 1], [-1, -1, 0, -1, -1, 1, 0, 0, 1, 1, 0, 1, -1, 0], [1, 1, 0, -1, -1, -1, 1, -1, 1, 1, 1, 0, 1, 0], [-1, 1, -1, 0, 1, -1, -1, 0, 0, 1, -1, 0, -1, 0], [1, 0, 0, 0, 1, -1, 0, 0, 1, 0, 0, 1, 1, 1], [0, 0, -1, 1, 0, 1, 1, 0, -1, 1, -1, 1, 1, -1], [-1, -1, -1, 1, -1, -1, -1, 1, 0, 0, 0, 1, -1, -1]], 83),
  ([[0, 4.7, 4.6, 4.5], [4.7, 0, 2.1, 0.4], [4.6, 2.1, 0, 1.2], [4.5, 0.4, 1.2, 0]], 16.93),
  ([[0, 0, 1, -1, 1, 0, -1, -1, -1, 0, -1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1], [0, 0, 1, 0, 0, -1, -1, -1, -1, 0, 1, 1, 1, 1, 0, -1, -1, 0, 0, 1, 1, -1, 0, 0], [-1, -1, 0, 1, 0, 1, -1, 1, -1, 1, 0, 0, 1, -1, 0, 0, 0, -1, 0, -1, 1, 0, 0, 0], [1, 0, -1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, -1, -1, -1, -1, 1, 0, -1], [-1, 0, 0, -1, 0, 0, 1, -1, 0, 1, -1, -1, -1, 1, 1, 0, 1, 1, 1, 0, -1, 1, -1, -1], [0, 1, -1, -1, 0, 0, 1, -1, -1, -1, 0, -1, 1, 0, 0, 0, -1, 0, 0, 1, 0, 0, 0, -1], [1, 1, 1, 0, -1, -1, 0, -1, -1, 0, 1, 1, -1, 0, 1, -1, 0, 0, 1, -1, 0, 0, 0, -1], [1, 1, -1, -1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, -1, 1, 0, 0], [1, 1, 1, -1, 0, 1, 1, 0, 0, -1, 1, -1, 1, 1, 1, 0, -1, -1, -1, -1, 0, 1, 1, -1], [0, 0, -1, 0, -1, 1, 0, -1, 1, 0, 1, 0, 0, 0, 0, 0, 1, -1, 0, 0, 0, 1, -1, -1], [1, -1, 0, 0, 1, 0, -1, 0, -1, -1, 0, 0, 1, 0, 0, -1, 0, -1, -1, -1, -1, -1, 1, -1], [-1, -1, 0, 0, 1, 1, -1, -1, 1, 0, 0, 0, -1, 0, 0, -1, 0, -1, -1, 0, 1, -1, 0, 0], [0, -1, -1, -1, 1, -1, 1, 0, -1, 0, -1, 1, 0, 1, -1, -1, 1, -1, 1, 0, 1, -1, 1, -1], [-1, -1, 1, 0, -1, 0, 0, 0, -1, 0, 0, 0, -1, 0, 0, -1, 1, -1, -1, 0, 1, 0, -1, -1], [-1, 0, 0, 0, -1, 0, -1, 0, -1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, -1, -1, 0, -1, -1], [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, -1, 0, 0, 1, -1, -1, -1, 0, -1, -1], [0, 1, 0, -1, -1, 1, 0, -1, 1, -1, 0, 0, -1, -1, -1, 0, 0, -1, 1, 0, 0, -1, -1, 1], [-1, 0, 1, 1, -1, 0, 0, 0, 1, 1, 1, 1, 1, 1, -1, -1, 1, 0, 1, 1, -1, -1, -1, 1], [0, 0, 0, 1, -1, 0, -1, -1, 1, 0, 1, 1, -1, 1, -1, 1, -1, -1, 0, 1, 1, 0, 0, -1], [0, -1, 1, 1, 0, -1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, -1, -1, 0, 0, 0, 1, 0], [-1, -1, -1, 1, 1, 0, 0, 1, 0, 0, 1, -1, -1, -1, 1, 1, 0, 1, -1, 0, 0, 0, 0, 0], [0, 1, 0, -1, -1, 0, 0, -1, -1, -1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0], [-1, 0, 0, 0, 1, 0, 0, 0, -1, 1, -1, 0, -1, 1, 1, 1, 1, 1, 0, -1, 0, -1, 0, 1], [-1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, -1, -1, 1, 0, 0, 0, -1, 0]], -6773))
import timeit
for mat, sol in haftest:
  #assert hafnian(mat) == sol
  #import numpy as np;from thewalrus import hafnian
  #print(hafnian(np.array(mat), loop=True))
  assert hafnian_perf_match(mat, isLoop=True) == hafnian_eff(mat, isInt=isinstance(sol, int), isLoop=True), (hafnian_perf_match(mat, isLoop=True), hafnian_eff(mat, isInt=isinstance(sol, int), isLoop=True))
  assert hafnian_perf_match(mat) == sol
  assert hafnian_ryser_time(mat) == sol
  assert hafnian_eff(mat, isInt=isinstance(sol, int)) == sol, (hafnian_eff(mat), sol)
  #print(timeit.timeit(lambda: hafnian_ryser_time(mat), number=1000))
  #print(timeit.timeit(lambda: hafnian_eff(mat, isInt=True), number=1000))
  print(sol)
#print([permanent_glynn_gray([[1 for _ in range(i)] for _ in range(i)]) for i in range(1, 10)])
def test_perm():
  import timeit
  import numpy as np
  from thewalrus import perm #pip install thewalrus
  Along = permexample
  A = np.array(Along, dtype=np.double)
  print(perm(A, quad=True, fsum=False, method='ryser'))
  print(perm(A, quad=True, fsum=False, method='bbfg'))
  print(timeit.timeit(lambda: perm(A, quad=True, fsum=False, method='ryser'), number=1000))
  print(timeit.timeit(lambda: perm(A, quad=True, fsum=False, method='bbfg'), number=1000))
  print(timeit.timeit(lambda: permanent(Along), number=1000))
  print(timeit.timeit(lambda: permanent_ryser(Along), number=1000))
  print(timeit.timeit(lambda: permanent_ryser_gray(Along), number=1000))
  print(timeit.timeit(lambda: permanent_glynn(Along), number=1000))
  print(timeit.timeit(lambda: permanent_glynn_gray(Along), number=1000))
test_perm()
#print([math.ceil(math.log2(math.factorial(n))) for n in range(1, 41)])
import numba #pip install numba
import numpy as np #pip install numpy
@numba.jit(nopython=True)
def numba_ix(arr, rows, cols):
  return arr[rows][:, cols]
@numba.jit(nopython=True)
def quad_cholesky_np(L, Z, idx, mat):
  Ls = numba_ix(L, Z, Z)
  for i in range(idx, len(mat)):
    for j in range(idx, i):
      z = 0.
      for k in range(j): z += Ls[i,k]*Ls[j,k].conjugate()
      Ls[i,j] = (mat[i][j] - z)/Ls[j,j]
    z = 0.
    for k in range(i): z += Ls[i,k]*Ls[i,k].conjugate()
    Ls[i,i] = np.sqrt(mat[i,i] - z)
  return Ls
@numba.jit(nopython=True)
def recursiveTor_np(L, modes, A, n):
  tor, start = 0., 0 if len(modes) == 0 else modes[-1]+1
  for i in range(start, n):
    nextModes = np.append(modes, i)
    nm, idx = len(A) >> 1, (i - len(modes))*2
    Z = np.concatenate((np.arange(idx), np.arange(idx+2, nm*2)), axis=0); nm -= 1
    Az = numba_ix(A, Z, Z)
    #Ls = np.linalg.cholesky(np.eye(2*nm) - Az)
    Ls = quad_cholesky_np(L, Z, idx, np.eye(2*nm) - Az)
    det = np.square(np.prod(np.diag(Ls)))
    tor += ((-1) ** len(nextModes))/np.sqrt(det) + recursiveTor_np(Ls, nextModes, Az, n)
  return tor
@numba.jit(nopython=True)
def rec_torontonian_np(A):
  n = A.shape[0] >> 1
  #Z = np.zeros(2*n, dtype=np.int_)
  #for i in range(n): Z[2*i] = i; Z[2*i+1] = i+n
  Z = np.empty((2*n,), dtype=np.int_)
  Z[0::2] = np.arange(0, n)
  Z[1::2] = np.arange(n, 2*n)
  A = numba_ix(A, Z, Z)
  L = np.linalg.cholesky(np.eye(2*n) - A)
  det = np.square(np.prod(np.diag(L)))
  return 1/np.sqrt(det) + recursiveTor_np(L, np.empty(0, dtype=np.int_), A, n)
def test_tor():
  import timeit
  from thewalrus import tor, numba_tor
  from thewalrus.random import random_covariance
  from thewalrus.quantum.conversions import Amat, Xmat
  for N in range(1, 10):
    cov = random_covariance(N)
    O = Xmat(N) @ Amat(cov)
    t1 = tor(O)
    t2 = numba_tor(O)
    #t3 = torontonian(O)
    t4 = rec_torontonian(O)
    t5 = rec_torontonian_np(O)
    print(t1, t2, t4, t5)
    print(timeit.timeit(lambda: numba_tor(O), number=1000))
    print(timeit.timeit(lambda: rec_torontonian_np(O), number=1000))
test_tor()

