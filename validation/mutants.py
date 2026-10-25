"""Plausible wrong solutions. Each must FAIL the verifier.

Run from the task root:  python3 validation/mutants.py
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "solution"))
import solve  # noqa: E402

INSTANCES = os.path.join(ROOT, "environment", "data", "instances.json")


def answers_with(fn):
    with open(INSTANCES) as f:
        insts = json.load(f)["instances"]
    out = {}
    for i in insts:
        try:
            out[i["id"]] = fn(i)
        except Exception:
            out[i["id"]] = "0"
    return {"answers": out}


def necklaces_only(i):
    """Counts up to rotation only (forgets reflections)."""
    k, fb, n, mod = i["k"], i["forbidden"], i["n"], i["mod"]
    A = [[1] * k for _ in range(k)]
    for a, b in fb:
        A[a][b] = A[b][a] = 0
    rot = sum(ph * sum(solve.mat_pow(A, d, mod)[t][t] for t in range(k))
              for d, ph in solve.divisors_with_phi(n))
    return str(rot * pow(n, -1, mod) % mod if mod else rot // n)


def ignores_self_loop_on_axis(i):
    """Treats every reflection like the unconstrained case (drops diag(A) terms)."""
    k, fb, n, mod = i["k"], i["forbidden"], i["n"], i["mod"]
    A = [[1] * k for _ in range(k)]
    for a, b in fb:
        A[a][b] = A[b][a] = 0
    rot = sum(ph * sum(solve.mat_pow(A, d, mod)[t][t] for t in range(k))
              for d, ph in solve.divisors_with_phi(n))
    m = n // 2
    P = solve.mat_pow(A, m, mod)
    wrong = n * sum(map(sum, P))
    total = rot + wrong
    return str(total * pow(2 * n, -1, mod) % mod if mod else total // (2 * n))


def float_arithmetic(i):
    """Exact path done in floating point (loses digits on big answers)."""
    v = solve.count(i["k"], i["forbidden"], i["n"], i["mod"])
    return str(v) if i["mod"] else str(int(float(v)))


def integer_json(i):
    """Right numbers, wrong type (JSON numbers, not strings)."""
    return solve.count(i["k"], i["forbidden"], i["n"], i["mod"])


MUTANTS = [necklaces_only, ignores_self_loop_on_axis, float_arithmetic, integer_json]


def verify(payload):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(payload, f)
    env = dict(os.environ, ANSWERS_PATH=f.name)
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", os.path.join(ROOT, "tests", "test_outputs.py")],
                       env=env, capture_output=True, text=True)
    os.unlink(f.name)
    return r.returncode == 0


ok = verify(answers_with(lambda i: str(solve.count(i["k"], i["forbidden"], i["n"], i["mod"]))))
print(f"reference solution          -> {'PASS' if ok else 'FAIL'}")
assert ok
for m in MUTANTS:
    passed = verify(answers_with(m))
    print(f"{m.__name__:<28}-> {'PASS (BAD!)' if passed else 'FAIL (caught)'}")
    assert not passed
print("verifier rejects every mutant")
