"""Two independent counting engines used to validate the reference solution.

brute_force   enumerates every valid colouring and keeps the lexicographically
              smallest member of each dihedral orbit (feasible for k**n <~ 5e6).

burnside_explicit
              walks all 2n group elements explicitly. For each one it builds the
              quotient graph (one node per cycle of positions, one edge per
              adjacency) and counts colourings of that graph directly, with no
              closed-form reflection formulas. Exact integers, feasible to n ~ 400.
"""
from itertools import product
from math import gcd


def allowed_matrix(k, forbidden):
    A = [[True] * k for _ in range(k)]
    for a, b in forbidden:
        A[a][b] = A[b][a] = False
    return A


def brute_force(k, forbidden, n):
    A = allowed_matrix(k, forbidden)
    seen = set()
    for c in product(range(k), repeat=n):
        if not all(A[c[i]][c[(i + 1) % n]] for i in range(n)):
            continue
        variants = []
        for r in range(n):
            rot = c[r:] + c[:r]
            variants.append(rot)
            variants.append(tuple(reversed(rot)))
        seen.add(min(variants))
    return len(seen)


def _count_graph_colourings(num_nodes, edges, A, k):
    """Count colourings of a graph with max degree 2 (paths/cycles, self-loops allowed)."""
    adj = [[] for _ in range(num_nodes)]
    loops = [False] * num_nodes
    for u, v in edges:
        if u == v:
            loops[u] = True
        else:
            adj[u].append(v)
            adj[v].append(u)
    # collapse duplicate edges (a 2-cycle in the quotient is one constraint)
    adj = [sorted(set(x)) for x in adj]
    allowed_self = [A[c][c] for c in range(k)]

    visited = [False] * num_nodes
    total = 1
    for start in range(num_nodes):
        if visited[start]:
            continue
        # gather component
        comp, stack = [], [start]
        visited[start] = True
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in adj[u]:
                if not visited[v]:
                    visited[v] = True
                    stack.append(v)
        ends = [u for u in comp if len(adj[u]) <= 1]
        first = ends[0] if ends else comp[0]
        is_cycle = not ends and len(comp) > 1
        # walk the component in order
        order, prev, cur = [first], None, first
        while True:
            nxt = [v for v in adj[cur] if v != prev and v not in order]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
            order.append(cur)
        assert len(order) == len(comp)

        def node_ok(u, c):
            return allowed_self[c] or not loops[u]

        comp_total = 0
        starts = range(k)
        for c0 in starts:
            if not node_ok(order[0], c0):
                continue
            ways = [0] * k
            ways[c0] = 1
            for u in order[1:]:
                ways = [
                    sum(ways[a] for a in range(k) if A[a][b]) if node_ok(u, b) else 0
                    for b in range(k)
                ]
            if is_cycle:
                comp_total += sum(ways[b] for b in range(k) if A[b][c0])
            else:
                comp_total += sum(ways)
        total *= comp_total
    return total


def burnside_explicit(k, forbidden, n):
    A = allowed_matrix(k, forbidden)
    group = []
    for r in range(n):
        group.append([(i + r) % n for i in range(n)])
        group.append([(r - i) % n for i in range(n)])
    acc = 0
    for g in group:
        cycle_of = [-1] * n
        cyc = 0
        for i in range(n):
            if cycle_of[i] == -1:
                j = i
                while cycle_of[j] == -1:
                    cycle_of[j] = cyc
                    j = g[j]
                cyc += 1
        edges = {tuple(sorted((cycle_of[i], cycle_of[(i + 1) % n]))) for i in range(n)}
        acc += _count_graph_colourings(cyc, edges, A, k)
    q, r = divmod(acc, 2 * n)
    assert r == 0
    return q
