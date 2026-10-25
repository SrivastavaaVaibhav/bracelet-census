# bracelet-census

An original Terminal-Bench-style benchmark task for evaluating AI coding agents on exact combinatorial counting. It includes a reference solution, an all-or-nothing verifier, and two independent engines used to validate the expected answers.

## The task

Count **bracelets**: circular arrangements of `n` coloured beads, considered the same under rotation and reflection, where some pairs of colours may not sit next to each other. There are 39 instances:

| Group | Instances | What it tests |
|---|---|---|
| Small, exact | 17 | Correct definitions and edge cases (odd cycles with proper 2-colourings, colours banned next to themselves, unconstrained cases) |
| Medium, exact | 12 | Big-integer output (up to 232 digits), `n` up to 401 |
| Large, modular | 10 | `n` up to ~10^12 (primes, 2^40, numbers with 6,720 divisors), modulo a prime |

The agent reads `/app/instances.json` and must write every answer as an exact decimal string to `/app/answers.json`. Scoring is all-or-nothing.

## Why it is hard

A correct solution needs Burnside's lemma over the dihedral group combined with a transfer matrix, plus three separate reflection cases:

- **Odd `n`:** the axis passes through one bead and the opposite gap. That gap joins a bead to its own mirror image, so the colour there must be allowed next to itself.
- **Even `n`, axis through two beads:** a simple path count.
- **Even `n`, axis through two gaps:** both end beads touch their mirror image, so both need the self-adjacency check.

It also needs divisor and totient enumeration for `n ≈ 10^12`, a modular inverse of `2n`, and exact big-integer output. Brute force can't reach the large instances.

## Validation

`validation/generate_and_check.py` builds the instances and expected answers, then checks them against:

1. **Brute force**: enumerates every colouring and keeps the canonical representative of each orbit (17 instances).
2. **Explicit Burnside**: iterates over all `2n` group elements, builds each quotient graph and counts its colourings directly, without the closed-form reflection formulas (29 exact instances, plus the 2 modular instances with `n ≤ 2000`).
3. **A random sweep of 300 extra cases** compared against both engines and two primes, plus checks of the divisor/totient enumeration (`Σ φ(n/d) = n` for `n < 3000` and every large `n`).

`validation/mutants.py` confirms that the verifier **rejects** plausible wrong solutions:

| Wrong solution | Result |
|---|---|
| Counts necklaces only (forgets reflections) | caught |
| Drops the self-adjacency check on reflection axes | caught |
| Computes big answers in floating point | caught |
| Writes JSON numbers instead of decimal strings | caught |

## Layout

```
instruction.md            task prompt given to the agent
task.toml                 metadata and time limits
environment/Dockerfile    python:3.12-slim + instances.json at /app
solution/solve.py         reference solution (standard library only)
solution/solve.sh
tests/test.sh             runs pytest, writes 0/1 reward to /logs/verifier/reward.txt
tests/test_outputs.py     exact-match verifier
tests/expected.json       expected answers (hidden from the agent)
validation/               generator, independent engines, mutant checks
```

## Running it

```bash
python3 validation/generate_and_check.py     # regenerate + cross-check (~30 s)
python3 solution/solve.py environment/data/instances.json answers.json
ANSWERS_PATH=answers.json python3 -m pytest -q tests/test_outputs.py
python3 validation/mutants.py                # verifier must reject every mutant
```

The reference solution solves all 39 instances in about 2 seconds.

## Author

Vaibhav Srivastava · [LinkedIn](https://www.linkedin.com/in/srivastavaavaibhav09) · [GitHub](https://github.com/SrivastavaaVaibhav)
