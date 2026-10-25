"""Generate the instance file, the expected answers, and cross-check them.

Run from the task root:  python3 validation/generate_and_check.py
Writes environment/data/instances.json and tests/expected.json.
"""
import json
import os
import random
import sys
from math import gcd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "solution"))
sys.path.insert(0, os.path.join(ROOT, "validation"))

from solve import count, divisors_with_phi  # noqa: E402
from independent import brute_force, burnside_explicit  # noqa: E402

rng = random.Random(20261025)
P1, P2 = 1_000_000_007, 998_244_353


def random_forbidden(k, p_pair=0.3, p_self=0.4):
    out = []
    for a in range(k):
        if rng.random() < p_self:
            out.append([a, a])
        for b in range(a + 1, k):
            if rng.random() < p_pair:
                out.append([b, a] if rng.random() < 0.5 else [a, b])
    rng.shuffle(out)
    return out


instances = []


def add(k, forbidden, n, mod=None):
    instances.append({"id": f"q{len(instances) + 1:02d}", "k": k, "forbidden": forbidden, "n": n, "mod": mod})


# --- small, exact (brute-forceable) --------------------------------------
for n, k in [(3, 2), (4, 3), (5, 3), (6, 2), (6, 4), (7, 3), (8, 3), (9, 3), (10, 4), (11, 3), (12, 3), (13, 3)]:
    add(k, random_forbidden(k), n)
# hand-picked edge cases
add(3, [[0, 0], [1, 1], [2, 2]], 6)            # proper 3-colourings of C6
add(2, [[0, 0], [1, 1]], 9)                    # odd cycle, proper 2-colouring: zero
add(4, [], 10)                                 # unconstrained bracelets
add(3, [[0, 1], [1, 2], [0, 2]], 8)            # only monochrome runs allowed
add(2, [[1, 1]], 12)                           # no two adjacent 1s

# --- medium, exact (big integers) ----------------------------------------
for n, k in [(24, 3), (37, 4), (60, 5), (97, 3), (128, 4), (150, 6), (210, 5), (257, 4), (360, 6), (401, 5)]:
    add(k, random_forbidden(k), n)
add(5, [[i, i] for i in range(5)], 300)        # proper 5-colourings of C300
add(6, [], 250)                                # unconstrained, 6 colours

# --- large, modular ------------------------------------------------------
large_ns = [
    10**9 + 9,            # prime
    2**40,                # pure power of two
    735_134_400,          # 1344 divisors
    963_761_198_400,      # 6720 divisors
    10**12 - 1,
    999_999_999_989,      # large prime
    3**25,
    2 * 3 * 5 * 7 * 11 * 13 * 17 * 19 * 23 * 29,
]
for i, n in enumerate(large_ns):
    k = [3, 4, 5, 4, 6, 3, 5, 4][i]
    mod = P1 if i % 2 == 0 else P2
    assert gcd(2 * n, mod) == 1
    add(k, random_forbidden(k), n, mod)
# modular versions of medium cases (checkable against exact values)
add(4, random_forbidden(4), 384, P1)
add(5, random_forbidden(5), 385, P2)

# ------------------------------------------------------------------------
expected = {}
checks = {"brute_force": 0, "burnside_explicit": 0, "mod_vs_exact": 0}
for inst in instances:
    k, fb, n, mod = inst["k"], inst["forbidden"], inst["n"], inst["mod"]
    val = count(k, fb, n, mod)
    expected[inst["id"]] = str(val)
    if mod is None:
        if k ** n <= 5_000_000:
            assert brute_force(k, fb, n) == val, inst
            checks["brute_force"] += 1
        if n <= 420:
            assert burnside_explicit(k, fb, n) == val, inst
            checks["burnside_explicit"] += 1
    elif n <= 2000:
        assert count(k, fb, n, None) % mod == val, inst
        assert burnside_explicit(k, fb, n) % mod == val, inst
        checks["mod_vs_exact"] += 1

# extra random sweep: reference vs both engines on many small/medium cases
sweep = 0
for _ in range(300):
    k = rng.randint(1, 5)
    n = rng.randint(3, 14)
    fb = random_forbidden(k, rng.random(), rng.random())
    ref = count(k, fb, n, None)
    if k ** n <= 2_000_000:
        assert brute_force(k, fb, n) == ref, (k, fb, n)
    assert burnside_explicit(k, fb, n) == ref, (k, fb, n)
    for m in (P1, P2):
        assert count(k, fb, n, m) == ref % m
    sweep += 1

# divisor/phi enumeration sanity: sum of phi(n/d) over d | n equals n
for n in list(range(1, 3000)) + large_ns:
    dp = divisors_with_phi(n)
    assert sum(ph for _, ph in dp) == n
    assert len({d for d, _ in dp}) == len(dp)

os.makedirs(os.path.join(ROOT, "environment", "data"), exist_ok=True)
with open(os.path.join(ROOT, "environment", "data", "instances.json"), "w") as f:
    json.dump({"instances": instances}, f, indent=1)
with open(os.path.join(ROOT, "tests", "expected.json"), "w") as f:
    json.dump({"answers": expected}, f, indent=1)

print(f"{len(instances)} instances written")
print("cross-checks:", checks, "| random sweep cases:", sweep)
print("largest exact answer has", max(len(v) for i, v in expected.items()
                                       if next(x for x in instances if x['id'] == i)['mod'] is None), "digits")
