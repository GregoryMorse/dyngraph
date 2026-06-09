"""Boolean-function sequence utilities (standalone, no third-party deps).

Target sequences from Harrison/Sloane notes:
- A000654, A000133, A000612, A000370, A000613, A000614, A001320, A000610.

Also included because it is structurally central:
- A000585.

Status in this file:
- Implemented with formulas/combinatorial code: A000133, A001320, A000612,
  A000616, A000610, A000370.
- Implemented with cycle-index core: A000585, A000613, A000614.
- Implemented with exact group-action Burnside: A000654.

Notes:
- A000616 is included because it is used directly by A000370 and A000610.
- A000613 is derived as A000585 / 2.
- Current verification checks OEIS-listed terms for:
  A000585/A000613/A000614 through n=8 and A000654 through n=6.
"""

from __future__ import annotations

import math
from fractions import Fraction
from functools import reduce
from operator import mul


def _prime_factorization(n: int) -> dict[int, int]:
  """Return prime factorization of n as {prime: exponent}."""
  if n < 1:
    raise ValueError("n must be >= 1")
  fac: dict[int, int] = {}
  d = 2
  m = n
  while d * d <= m:
    while m % d == 0:
      fac[d] = fac.get(d, 0) + 1
      m //= d
    d += 1 if d == 2 else 2
  if m > 1:
    fac[m] = fac.get(m, 0) + 1
  return fac


def _mobius(n: int) -> int:
  """Mobius function mu(n)."""
  if n == 1:
    return 1
  fac = _prime_factorization(n)
  if any(e > 1 for e in fac.values()):
    return 0
  return -1 if (len(fac) % 2) else 1


def _divisors(n: int) -> list[int]:
  """All positive divisors of n, sorted."""
  small: list[int] = []
  large: list[int] = []
  d = 1
  while d * d <= n:
    if n % d == 0:
      small.append(d)
      if d * d != n:
        large.append(n // d)
    d += 1
  return small + list(reversed(large))


def _partition_lin(n: int, d: int, depth: int = 0):
  """OEIS-style linear partition helper used by A000616/A000610 code."""
  if d == depth:
    if n == 0:
      yield ()
    return
  for i in range(n + 1):
    rem = n - i * (depth + 1)
    if rem < 0:
      break
    for item in _partition_lin(rem, d, depth=depth + 1):
      yield item + (i,)


def _partitions_nondec(n: int, min_part: int = 1):
  """Yield nondecreasing integer partitions of n as tuples."""
  if n == 0:
    yield ()
    return
  yield (n,)
  for i in range(min_part, n // 2 + 1):
    for p in _partitions_nondec(n - i, i):
      yield (i,) + p


def _num_equiv_bool_func_np(n: int, self_complementary: bool = False) -> int:
  """Core routine from OEIS A000370 program block.

  self_complementary=False gives A000616(n) for n >= 0.
  self_complementary=True gives A000610(n) for n >= 0.
  """

  def e(k: int) -> int:
    return sum((1 << d) * _mobius(k // d) for d in _divisors(k)) // k

  def g(two_k: int) -> int:
    return sum(
      (1 << (d // 2)) * _mobius(two_k // d)
      for d in _divisors(two_k)
      if (two_k // 2) % d != 0
    ) // two_k

  total = 0
  denom = math.factorial(n) * (1 << n)
  for j in _partition_lin(n, n):
    # Weight from cycle counts in S_n wr C_2 action.
    coeff_den = reduce(
      mul,
      (math.factorial(ji) * (2 * (n - i)) ** ji for i, ji in enumerate(j)),
      1,
    )
    outer = math.factorial(n) * (1 << n) // coeff_den

    if n == 0:
      products = [[(1, 1)]]
    else:
      products = None
      for i in range(1, n + 1):
        ji = j[n - i]
        for _ in range(ji):
          block = [
            [(d, e(d)) for d in _divisors(i)],
            [(d, g(d)) for d in _divisors(2 * i) if i % d != 0],
          ]
          if products is None:
            products = block
          else:
            next_products = []
            for a in products:
              for b in block:
                next_products.append(
                  [
                    (math.lcm(p, q), math.gcd(p, q) * ip * jq)
                    for p, ip in a
                    for q, jq in b
                  ]
                )
            products = next_products

    inner = 0
    for a in products:
      term = 1
      for d, x in a:
        if self_complementary and (d & 1):
          term = 0
          break
        term *= 1 << x
      inner += term

    total += outer * inner

  return total // denom


def a000616(n: int) -> int:
  """A000616 with true OEIS offset behavior.

  OEIS offset is -1 and a(-1) = 1 by convention.
  """
  if n == -1:
    return 1
  if n < -1:
    raise ValueError("A000616 is defined for n >= -1")
  return _num_equiv_bool_func_np(n, self_complementary=False)


def a000610(n: int) -> int:
  """A000610: number of self-complementary Boolean functions of n variables."""
  if n < 0:
    raise ValueError("A000610 is defined for n >= 0")
  return _num_equiv_bool_func_np(n, self_complementary=True)


def a000370(n: int) -> int:
  """A000370: NPN-equivalence classes of Boolean functions of n or fewer vars."""
  if n < 0:
    raise ValueError("A000370 is defined for n >= 0")
  return (a000616(n) + a000610(n)) // 2


def a000612(n: int) -> int:
  """A000612: P-equivalence classes of switching functions of n or fewer vars / 2."""
  if n < 0:
    raise ValueError("A000612 is defined for n >= 0")

  fracs: list[tuple[int, int]] = []
  for l in _partitions_nondec(n):
    w = math.lcm(*l) if l else 1
    num_exp = sum(reduce(mul, ((1 << math.gcd(t, li)) for li in l), 1) for t in range(1, w + 1)) // w
    x = 1 << num_exp

    max_j = max(l, default=0)
    y = 1
    for j in range(1, max_j + 1):
      c = sum(1 for li in l if li == j)
      y *= (j ** c) * math.factorial(c)
    fracs.append((x, y))

  m = math.lcm(*(z for _, z in fracs)) if fracs else 1
  return (sum(x * (m // y) for x, y in fracs) // m) // 2


def a001320(n: int) -> int:
  """A001320: self-complementary Boolean functions up to variable complementation."""
  if n < 1:
    raise ValueError("A001320 is defined for n >= 1")
  # a(n) = 2^(2^(n-1)) * (2^n - 1) / 2^n.
  return ((1 << (1 << (n - 1))) * ((1 << n) - 1)) >> n


def a000133(n: int) -> int:
  """A000133: number of Boolean functions of n variables."""
  if n < 1:
    raise ValueError("A000133 is defined for n >= 1")
  # a(n) = (2^(2^n) + (2^n-1)*2^(2^(n-1)+1)) / 2^(n+1)
  return ((1 << (1 << n)) + (((1 << n) - 1) << (1 + (1 << (n - 1))))) >> (n + 1)


# Table-backed placeholders for the hard cycle-index sequences.
# TODO: replace with explicit GL/AGL cycle-index code in pure Python.
def _gf2_rank(rows: list[int], n: int) -> int:
  """Rank over GF(2) for an n-bit row-matrix encoded as ints."""
  r = rows[:]
  rank = 0
  for col in range(n):
    pivot = None
    bit = 1 << col
    for i in range(rank, len(r)):
      if r[i] & bit:
        pivot = i
        break
    if pivot is None:
      continue
    r[rank], r[pivot] = r[pivot], r[rank]
    for i in range(len(r)):
      if i != rank and (r[i] & bit):
        r[i] ^= r[rank]
    rank += 1
    if rank == n:
      break
  return rank


def _iter_gl_n2_rows(n: int):
  """Yield all invertible n x n matrices over GF(2), as row-bitmasks."""
  all_rows = list(range(1 << n))

  def rec(cur: list[int]):
    if len(cur) == n:
      yield tuple(cur)
      return
    for row in all_rows:
      nxt = cur + [row]
      if _gf2_rank(nxt, n) == len(nxt):
        yield from rec(nxt)

  yield from rec([])


def _apply_gl_row_matrix_to_vec(mat_rows: tuple[int, ...], v: int) -> int:
  """Compute mat_rows * v over GF(2), vector v encoded as bits."""
  out = 0
  for i, row in enumerate(mat_rows):
    if ((row & v).bit_count() & 1) != 0:
      out |= 1 << i
  return out


def _num_cycles_on_vectors(mat_rows: tuple[int, ...], n: int) -> int:
  """Number of cycles in permutation induced by matrix on GF(2)^n."""
  size = 1 << n
  seen = [False] * size
  cycles = 0
  for x in range(size):
    if seen[x]:
      continue
    cycles += 1
    y = x
    while not seen[y]:
      seen[y] = True
      y = _apply_gl_row_matrix_to_vec(mat_rows, y)
  return cycles


def _a000585_gl_cycle_index_burnside(n: int) -> int:
  """A000585 via direct Burnside on GL(n,2) action on Boolean functions.

  For g in GL(n,2), fixed Boolean functions count is 2^{c(g)}, where c(g) is
  number of cycles of g on GF(2)^n. Orbit count is average over GL(n,2).
  """
  if n < 1:
    raise ValueError("A000585 is defined for n >= 1")
  total = 0
  gl_size = 1
  qn = 1 << n
  qk = 1
  for _ in range(n):
    gl_size *= (qn - qk)
    qk <<= 1
  for mat in _iter_gl_n2_rows(n):
    total += 1 << _num_cycles_on_vectors(mat, n)
  return total // gl_size


def _cycle_lengths_of_perm(perm: list[int]) -> list[int]:
  """Cycle lengths of a permutation represented as mapping list."""
  seen = [False] * len(perm)
  lens: list[int] = []
  for i in range(len(perm)):
    if seen[i]:
      continue
    k = 0
    j = i
    while not seen[j]:
      seen[j] = True
      j = perm[j]
      k += 1
    lens.append(k)
  return lens


def _cycle_type_of_perm(perm: list[int]) -> tuple[tuple[int, int], ...]:
  """Cycle type as sorted (length, multiplicity) pairs."""
  counts: dict[int, int] = {}
  for l in _cycle_lengths_of_perm(perm):
    counts[l] = counts.get(l, 0) + 1
  return tuple(sorted(counts.items()))


def _centralizer_size_from_cycle_type(cycle_type: tuple[tuple[int, int], ...]) -> int:
  """Centralizer size in S_N from cycle type."""
  z = 1
  for l, m in cycle_type:
    z *= (l ** m) * math.factorial(m)
  return z


# Compact cycle-index core (sufficient for GL/AG over GF(2)).
# A monomial is dict[int cycle_len, int exponent].
# A cycle index is dict[key -> Fraction], where key is sorted (len, exp) pairs.


def _mono_key(m: dict[int, int]) -> tuple[tuple[int, int], ...]:
  return tuple(sorted((k, v) for k, v in m.items() if v != 0))


def _key_to_mono(k: tuple[tuple[int, int], ...]) -> dict[int, int]:
  return {i: e for i, e in k}


def _ci_zero() -> dict[tuple[tuple[int, int], ...], Fraction]:
  return {}


def _ci_one() -> dict[tuple[tuple[int, int], ...], Fraction]:
  return {(): Fraction(1, 1)}


def _ci_from_mono(m: dict[int, int], coeff: Fraction = Fraction(1, 1)) -> dict[tuple[tuple[int, int], ...], Fraction]:
  return {_mono_key(m): coeff}


def _ci_add(dst: dict[tuple[tuple[int, int], ...], Fraction], src: dict[tuple[tuple[int, int], ...], Fraction]) -> dict[tuple[tuple[int, int], ...], Fraction]:
  out = dict(dst)
  for k, c in src.items():
    out[k] = out.get(k, Fraction(0, 1)) + c
    if out[k] == 0:
      del out[k]
  return out


def _mono_harary(a: dict[int, int], b: dict[int, int]) -> dict[int, int]:
  # Harary product on cycle monomials: lcm/gcd interaction of cycle structures.
  if not a:
    return dict(b)
  if not b:
    return dict(a)
  out: dict[int, int] = {}
  for i, ai in a.items():
    for j, bj in b.items():
      l = math.lcm(i, j)
      out[l] = out.get(l, 0) + math.gcd(i, j) * ai * bj
  return out


def _ci_harary_mul(a: dict[tuple[tuple[int, int], ...], Fraction], b: dict[tuple[tuple[int, int], ...], Fraction]) -> dict[tuple[tuple[int, int], ...], Fraction]:
  out = _ci_zero()
  for ka, ca in a.items():
    ma = _key_to_mono(ka)
    for kb, cb in b.items():
      mb = _key_to_mono(kb)
      k = _mono_key(_mono_harary(ma, mb))
      out[k] = out.get(k, Fraction(0, 1)) + ca * cb
      if out[k] == 0:
        del out[k]
  return out


def _ci_harary_pow(ci: dict[tuple[tuple[int, int], ...], Fraction], n: int) -> dict[tuple[tuple[int, int], ...], Fraction]:
  if n < 0:
    raise ValueError("negative power")
  if n == 0:
    return _ci_one()
  if n == 1:
    return dict(ci)
  r = _ci_one()
  b = dict(ci)
  e = n
  while e > 0:
    if e & 1:
      r = _ci_harary_mul(r, b)
    e >>= 1
    if e:
      b = _ci_harary_mul(b, b)
  return r


def _ci_scale(ci: dict[tuple[tuple[int, int], ...], Fraction], s: Fraction) -> dict[tuple[tuple[int, int], ...], Fraction]:
  if s == 0:
    return _ci_zero()
  return {k: c * s for k, c in ci.items()}


def _ci_apply_binary_colors(ci: dict[tuple[tuple[int, int], ...], Fraction]) -> int:
  # Z_G(2,2,...) = sum coeff * 2^(sum exponents)
  v = Fraction(0, 1)
  for k, c in ci.items():
    cycles = sum(e for _, e in k)
    v += c * (1 << cycles)
  if v.denominator != 1:
    raise ValueError("non-integer cycle-index evaluation")
  return v.numerator


def _ci_apply_01(ci: dict[tuple[tuple[int, int], ...], Fraction]) -> int:
  # apply(0,1): odd cycle variables mapped to 0, even to 2.
  v = Fraction(0, 1)
  for k, c in ci.items():
    ok = True
    power = 0
    for l, e in k:
      if (l & 1) == 1 and e > 0:
        ok = False
        break
      if (l & 1) == 0:
        power += e
    if ok:
      v += c * (1 << power)
  if v.denominator != 1:
    raise ValueError("non-integer cycle-index evaluation")
  return v.numerator


def _partitions_exact(n: int, max_part: int | None = None):
  """Yield integer partitions of n in nonincreasing form."""
  if n == 0:
    yield ()
    return
  if max_part is None:
    max_part = n
  for p in range(min(max_part, n), 1 - 1, -1):
    for rest in _partitions_exact(n - p, p):
      yield (p,) + rest


def _count_form(parts: tuple[int, ...], n: int) -> list[int]:
  c = [0] * (n + 1)
  for p in parts:
    c[p] += 1
  return c


def _compositions_nonneg(total: int, k: int):
  if k == 0:
    if total == 0:
      yield ()
    return
  if k == 1:
    yield (total,)
    return
  for x in range(total + 1):
    for tail in _compositions_nonneg(total - x, k - 1):
      yield (x,) + tail


def _phi(n: int) -> int:
  if n <= 0:
    raise ValueError("phi defined for positive integers")
  fac = _prime_factorization(n)
  out = n
  for p in fac:
    out = out // p * (p - 1)
  return out


def _get_exponents_gl(k: int, q: int = 2) -> tuple[list[list[int]], list[list[int]]]:
  # Port of getExponents from jOEIS GeneralLinearCycleIndex.
  a: list[list[int]] = []
  b: list[list[int]] = []
  seen: set[int] = set()
  for i in range(k):
    dd = i + 1
    aa: list[int] = []
    bb: list[int] = []
    c = q ** dd - 1
    for z in _divisors(c):
      if dd == 1 and z == 1:
        aa.append(z)
        bb.append(1)
        seen.add(z)
      else:
        f = _phi(z)
        if f % dd == 0 and z not in seen:
          aa.append(z)
          bb.append(f // dd)
          seen.add(z)
    a.append(aa)
    b.append(bb)
  return a, b


def _kung(d: int, lam_count: list[int], q: int = 2) -> int:
  mu = 0
  ans = 1
  for i in range(1, len(lam_count)):
    for j in range(i, len(lam_count)):
      mu += lam_count[j]
    qp = q ** (d * mu)
    for j in range(1, lam_count[i] + 1):
      ans *= (qp - (q ** ((mu - j) * d)))
  return ans


def _hypercompanion_cycle_type(d: int, exp: int, i: int, p: int = 2, q: int = 2) -> dict[int, int]:
  e = [0] * i
  e[0] = exp
  k = 1
  for j in range(1, i):
    e[j] = e[j - 1]
    if k < j + 1:
      k *= p
      e[j] *= p
  mm: dict[int, int] = {1: 1}
  t = q ** d
  t1 = t - 1
  mm[exp] = mm.get(exp, 0) + (t1 // exp)
  for j in range(1, i):
    t1 *= t
    mm[e[j]] = mm.get(e[j], 0) + (t1 // e[j])
  return mm


def _hypercompanion_cycle_type_aff(i: int, p: int = 2, q: int = 2) -> tuple[dict[int, int], Fraction]:
  e = 1
  while i > e:
    e *= p
  mono = {e: (q ** (i - 1)) // e}
  coeff = Fraction((q ** (i - 2)) * (q - 1), 1)
  return mono, coeff


def _multinomial_ext(a: int, count_form: list[int]) -> int:
  den = 1
  s = a
  for j in count_form:
    s -= j
    den *= math.factorial(j)
  den *= math.factorial(s)
  return math.factorial(a) // den


def _gl_cycle_type_poly_part(d: int, exp: int, mu: list[int], p: int = 2, q: int = 2) -> dict[tuple[tuple[int, int], ...], Fraction]:
  res = _ci_one()
  for i in range(1, len(mu)):
    if mu[i] != 0:
      hct = _hypercompanion_cycle_type(d, exp, i, p, q)
      res = _ci_harary_mul(res, _ci_harary_pow(_ci_from_mono(hct), mu[i]))
  return _ci_scale(res, Fraction(1, _kung(d, mu, q)))


def _ag_cycle_type_poly_part(d: int, exp: int, mu: list[int], p: int = 2, q: int = 2) -> dict[tuple[tuple[int, int], ...], Fraction]:
  res = _ci_one()
  if d != 1 or (q != 2 and exp != 1):
    for i in range(1, len(mu)):
      if mu[i] != 0:
        hct = _hypercompanion_cycle_type(d, exp, i, p, q)
        t = _ci_from_mono(hct, Fraction(q ** (d * i), 1))
        res = _ci_harary_mul(res, _ci_harary_pow(t, mu[i]))
  else:
    for i in range(1, len(mu)):
      if mu[i] != 0:
        hct = _hypercompanion_cycle_type(d, exp, i, p, q)
        t = _ci_from_mono(hct, Fraction(q ** (i - 1), 1))
        aff_mono, aff_coeff = _hypercompanion_cycle_type_aff(i + 1, p, q)
        t = _ci_add(t, _ci_from_mono(aff_mono, aff_coeff))
        res = _ci_harary_mul(res, _ci_harary_pow(t, mu[i]))
  return _ci_scale(res, Fraction(1, _kung(d, mu, q)))


def _general_linear_cycle_index(k: int, affine: bool = False, q: int = 2, p: int = 2) -> dict[tuple[tuple[int, int], ...], Fraction]:
  v1, v2 = _get_exponents_gl(k, q)
  res = _ci_zero()
  for part in _partitions_exact(k):
    c = _count_form(part, k)
    zs1 = _ci_from_mono({1: 1})
    for i in range(1, len(c)):
      if c[i] <= 0:
        continue
      zs2 = _ci_zero()
      choices = len(v1[i - 1])
      for c1 in _compositions_nonneg(c[i], choices):
        zs3 = _ci_one()
        for j, c1j in enumerate(c1):
          if c1j == 0:
            continue
          zs4 = _ci_zero()
          pc2k = v2[i - 1][j]
          for p2 in _partitions_exact(c1j):
            if len(p2) > pc2k:
              continue
            c2 = _count_form(p2, c1j)
            zs5 = _ci_one()
            for l in p2:
              if l == 0:
                continue
              zs6 = _ci_zero()
              for p3 in _partitions_exact(l):
                c3 = _count_form(p3, l)
                term = _ag_cycle_type_poly_part(i, v1[i - 1][j], c3, p, q) if affine else _gl_cycle_type_poly_part(i, v1[i - 1][j], c3, p, q)
                zs6 = _ci_add(zs6, term)
              zs5 = _ci_harary_mul(zs5, zs6)
            zs5 = _ci_scale(zs5, Fraction(_multinomial_ext(pc2k, c2), 1))
            zs4 = _ci_add(zs4, zs5)
          zs3 = _ci_harary_mul(zs3, zs4)
        zs2 = _ci_add(zs2, zs3)
      zs1 = _ci_harary_mul(zs1, zs2)
    res = _ci_add(res, zs1)
  if affine:
    res = _ci_scale(res, Fraction(1, q ** k))
  return res


def _iter_affine_perms(n: int):
  """Yield permutations induced by AG(n,2) maps x -> A*x xor b."""
  size = 1 << n
  for a in _iter_gl_n2_rows(n):
    for b in range(size):
      yield [(_apply_gl_row_matrix_to_vec(a, x) ^ b) for x in range(size)]


def _iter_signed_perm_perms(n: int):
  """Yield permutations induced by signed coordinate maps x -> P(x) xor c."""
  import itertools

  size = 1 << n
  for perm in itertools.permutations(range(n)):
    for c in range(size):
      mapping = [0] * size
      for x in range(size):
        y = 0
        for i, p in enumerate(perm):
          if (x >> p) & 1:
            y |= 1 << i
        mapping[x] = y ^ c
      yield mapping


_A000585_OEIS = [
  4,
  8,
  20,
  92,
  2744,
  950998216,
  2076795963681989019155896,
  21651217007530946175606768762255421159692845640522169779616,
]

_A000613_OEIS = [
  2,
  4,
  10,
  46,
  1372,
  475499108,
  1038397981840994509577948,
  10825608503765473087803384381127710579846422820261084889808,
]

_A000614_OEIS = [
  2,
  3,
  6,
  18,
  206,
  7888299,
  8112499583888855378066,
  42287533217833953489054778023401252726576585396037133766,
]

_A000654_OEIS = [
  1,
  2,
  52,
  142090700,
  17844701940501123640681816160,
  59757436204078657410908164193971330396709572693816353610758085074676243846093824,
]


def a000613(n: int) -> int:
  """A000613: number of Boolean-function classes for n variables.

  Formula from OEIS: a(n) = A000585(n) / 2.

  Implementation policy:
  - delegates to A000585, then divides by 2.
  """
  if n < 1:
    raise ValueError("A000613 is defined for n >= 1")
  return a000585(n) // 2


def a000585(n: int) -> int:
  """A000585: number of equivalence classes under GL(n,2).

  Current implementation:
  - n <= 3: direct Burnside over explicit GL(n,2) elements,
  - n >= 4: cycle-index core over GL(n,2).
  """
  if n < 1:
    raise ValueError("A000585 is defined for n >= 1")
  if n <= 3:
    return _a000585_gl_cycle_index_burnside(n)
  ci = _general_linear_cycle_index(n, affine=False, q=2, p=2)
  return _ci_apply_binary_colors(ci)


def a000614(n: int) -> int:
  """A000614: complemented types of Boolean functions under AG(n,2).

  Current implementation:
  - n <= 3: direct Burnside on explicit affine permutations,
  - n >= 4: cycle-index core over AG(n,2).
  """
  if n < 1:
    raise ValueError("A000614 is defined for n >= 1")
  if n <= 3:
    ag = list(_iter_affine_perms(n))
    total_plain = 0
    total_compl = 0
    for p in ag:
      lens = _cycle_lengths_of_perm(p)
      c = len(lens)
      fixed_plain = 1 << c
      total_plain += fixed_plain
      # f = 1 - f o p has solutions iff every cycle length is even.
      if all((l & 1) == 0 for l in lens):
        total_compl += fixed_plain
    return (total_plain + total_compl) // (2 * len(ag))
  ci = _general_linear_cycle_index(n, affine=True, q=2, p=2)
  return (_ci_apply_binary_colors(ci) + _ci_apply_01(ci)) // 2


def a000654(n: int) -> int:
  """A000654: invertible Boolean functions of n variables.

  Exact for n <= 6 via Burnside on left/right action of signed-permutation
  group B_n (domain/range variable permutations and complements).
  """
  if n < 1:
    raise ValueError("A000654 is defined for n >= 1")
  if n <= 6:
    h = list(_iter_signed_perm_perms(n))
    by_type: dict[tuple[tuple[int, int], ...], int] = {}
    for p in h:
      t = _cycle_type_of_perm(p)
      by_type[t] = by_type.get(t, 0) + 1
    total = 0
    for t, m in by_type.items():
      total += m * m * _centralizer_size_from_cycle_type(t)
    return total // (len(h) * len(h))
  raise NotImplementedError("A000654 currently computed exactly only for n <= 6")


def verify() -> None:
  """Assertion suite against current OEIS tables for implemented ranges."""
  assert [a000370(n) for n in range(0, 8)] == [
    1,
    2,
    4,
    14,
    222,
    616126,
    200253952527184,
    263735716028826576482466871188128,
  ]

  assert [a000610(n) for n in range(0, 8)] == [
    0,
    1,
    2,
    6,
    42,
    4094,
    98210640,
    148947659711650464,
  ]

  assert [a000616(n) for n in range(-1, 8)] == [
    1,
    2,
    3,
    6,
    22,
    402,
    1228158,
    400507806843728,
    527471432057653004017274030725792,
  ]

  assert [a000612(n) for n in range(0, 8)] == [
    1,
    2,
    6,
    40,
    1992,
    18666624,
    12813206169137152,
    33758171486592987164087845043830784,
  ]

  assert [a000133(n) for n in range(1, 9)] == [
    2,
    5,
    30,
    2288,
    67172352,
    144115192303714304,
    1329227995784915891206435945914040320,
    226156424291633194186662080095093570364871077725232774230036394136943198208,
  ]

  assert [a001320(n) for n in range(1, 9)] == [
    1,
    3,
    14,
    240,
    63488,
    4227858432,
    18302628885633695744,
    338953138925153547590470800371487866880,
  ]

  # Compare computed values against full OEIS right-hand lists.
  assert [a000585(n) for n in range(1, 9)] == _A000585_OEIS[0:8]
  assert [a000613(n) for n in range(1, 9)] == _A000613_OEIS[0:8]
  assert [a000614(n) for n in range(1, 9)] == _A000614_OEIS[0:8]
  assert [a000654(n) for n in range(1, 7)] == _A000654_OEIS[0:6]


if __name__ == "__main__":
  verify()
  print("All current assertions passed.")
  print("Implemented general code: A000133, A001320, A000612, A000610, A000616, A000370")
  print("Exact computed ranges: A000585/A000613/A000614 for n<=8, A000654 for n<=6")
