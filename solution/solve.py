#!/usr/bin/env python3
"""Reference solution: count bracelets with forbidden colour adjacencies.

Burnside's lemma over the dihedral group D_n, with a transfer matrix A for
allowed neighbouring colours. Standard library only.

  rotations   sum_{d | n} phi(n/d) * tr(A^d)
  reflections n odd : n     * (1^T A^m s),            m = (n-1)/2
              n even: n/2   * (1^T A^(n/2) 1)          axis through two beads
                      n/2   * (s^T A^(n/2-1) s)        axis through two gaps
  where s = diag(A) (colours allowed next to themselves).

  answer = (rotations + reflections) / (2n), exactly or modulo a prime.
"""
import json
import sys


def mat_mul(X, Y, mod):
    k = len(X)
    out = [[0] * k for _ in range(k)]
    for i in range(k):
        Xi, Oi = X[i], out[i]
        for t in range(k):
            x = Xi[t]
            if x:
                Yt = Y[t]
                for j in range(k):
                    Oi[j] += x * Yt[j]
        if mod:
            for j in range(k):
                Oi[j] %= mod
    return out


def mat_pow(A, e, mod):
    k = len(A)
    R = [[int(i == j) for j in range(k)] for i in range(k)]
    B = [row[:] for row in A]
    while e:
        if e & 1:
            R = mat_mul(R, B, mod)
        e >>= 1
        if e:
            B = mat_mul(B, B, mod)
    return R


def factorize(n):
    f, d = {}, 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def divisors_with_phi(n):
    """Yield (d, phi(n // d)) for every divisor d of n."""
    items = list(factorize(n).items())
    out = [(1, 1)]  # (divisor e, phi(e)) for e built so far
    for p, a in items:
        nxt = []
        for e, ph in out:
            pk, phk = 1, 1
            for i in range(a + 1):
                nxt.append((e * pk, ph * phk))
                phk = (p - 1) if i == 0 else phk * p
                pk *= p
        out = nxt
    return [(n // e, ph) for e, ph in out]


def count(k, forbidden, n, mod):
    A = [[1] * k for _ in range(k)]
    for a, b in forbidden:
        A[a][b] = A[b][a] = 0
    s = [A[i][i] for i in range(k)]
    red = (lambda x: x % mod) if mod else (lambda x: x)

    rot = 0
    for d, ph in divisors_with_phi(n):
        P = mat_pow(A, d, mod)
        rot = red(rot + ph * red(sum(P[i][i] for i in range(k))))

    if n % 2:
        P = mat_pow(A, (n - 1) // 2, mod)
        fixed = sum(P[i][j] * s[j] for i in range(k) for j in range(k))
        refl = red(n * red(fixed))
    else:
        P = mat_pow(A, n // 2, mod)
        through_beads = sum(P[i][j] for i in range(k) for j in range(k))
        Q = mat_pow(A, n // 2 - 1, mod)
        through_gaps = sum(s[i] * Q[i][j] * s[j] for i in range(k) for j in range(k))
        refl = red((n // 2) * red(through_beads + through_gaps))

    total = rot + refl
    if mod:
        return total * pow(2 * n, -1, mod) % mod
    q, r = divmod(total, 2 * n)
    assert r == 0, "Burnside sum not divisible by group order"
    return q


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "/app/instances.json"
    dst = sys.argv[2] if len(sys.argv) > 2 else "/app/answers.json"
    with open(src) as f:
        instances = json.load(f)["instances"]
    answers = {}
    for inst in instances:
        val = count(inst["k"], inst["forbidden"], inst["n"], inst.get("mod"))
        answers[inst["id"]] = str(val)
    with open(dst, "w") as f:
        json.dump({"answers": answers}, f, indent=2)


if __name__ == "__main__":
    main()
