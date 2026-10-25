Count bracelets with forbidden colour adjacencies.

The file `/app/instances.json` contains a list of counting problems. Solve all of them and write the answers to `/app/answers.json`.

## Definitions

Each instance gives:

- `k`: the number of colours, labelled `0 … k-1`.
- `forbidden`: a list of unordered pairs `[a, b]`. Two beads that are next to each other may not have colours `a` and `b` (in either order). A pair `[a, a]` means two adjacent beads may not both have colour `a`.
- `n`: the number of beads, `n ≥ 3`.
- `mod`: either `null` or a prime that does not divide `2n`.

A **valid colouring** assigns a colour to each of `n` beads placed in a circle so that every pair of neighbouring beads, including the pair formed by the last bead and the first, is allowed.

Two valid colourings are **the same bracelet** if one can be turned into the other by rotating the circle, flipping it over, or both. In other words, colourings are counted up to the dihedral group of order `2n`.

For each instance, compute the number of distinct bracelets. If `mod` is `null`, give the exact count. Otherwise give the count modulo `mod`. When `mod` is set, the count is the exact number of bracelets reduced modulo `mod`, which is well-defined because `mod` does not divide `2n`.

## Output format

Write `/app/answers.json` as a JSON object of this form:

```json
{"answers": {"q01": "2", "q02": "17", "...": "..."}}
```

Every instance id must be present. Every value must be a **decimal string** of the exact non-negative integer, with no exponent, separator or leading zeros. Some exact answers have more than 200 digits.

## Constraints

- Use any language available in the container. No network access is needed.
- The full set must finish within the time limit. Some instances have `n` close to `10^12`, so enumerating colourings will not work for them.
- Scoring is all-or-nothing: every answer must match exactly.
