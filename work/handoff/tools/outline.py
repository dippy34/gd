"""Trace the silhouette of the built geometry as clean polylines.

The corridor is a staircase of 15-unit squares, so its raw boundary is a saw of
5-unit faces. Chaining the faces into closed loops and simplifying them turns
that saw back into the straight 45-degree runs the layout is actually made of --
which is what lets the level be drawn as ONE crisp edge instead of 12,000 beads.
"""
import math
G = 5.0

def loops(cells):
    """cells: set of (cx, cy) occupied grid cells -> list of closed point loops."""
    edges = {}
    for (cx, cy) in cells:
        x0, y0, x1, y1 = cx * G, cy * G, (cx + 1) * G, (cy + 1) * G
        if (cx, cy + 1) not in cells: edges[(x1, y1)] = (x0, y1)   # top,    right->left
        if (cx, cy - 1) not in cells: edges[(x0, y0)] = (x1, y0)   # bottom, left->right
        if (cx - 1, cy) not in cells: edges[(x0, y1)] = (x0, y0)   # left,   top->bottom
        if (cx + 1, cy) not in cells: edges[(x1, y0)] = (x1, y1)   # right,  bottom->top
    out = []
    seen = set()
    for start in list(edges):
        if start in seen: continue
        loop = [start]; seen.add(start); p = edges.get(start)
        guard = 0
        while p is not None and p != start and guard < 400000:
            if p in seen: break
            loop.append(p); seen.add(p); p = edges.get(p); guard += 1
        if len(loop) > 3: out.append(loop)
    return out

def _perp(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    d2 = dx * dx + dy * dy
    if d2 == 0: return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / d2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))

def simplify(pts, tol=3.6):
    """Iterative Douglas-Peucker."""
    if len(pts) < 3: return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1: continue
        best, bd = -1, tol
        for k in range(i + 1, j):
            d = _perp(pts[k], pts[i], pts[j])
            if d > bd: bd, best = d, k
        if best >= 0:
            keep[best] = True
            stack.append((i, best)); stack.append((best, j))
    return [p for p, k in zip(pts, keep) if k]

def segments(cells, tol=3.6, min_len=6.0):
    """[(x0, y0, x1, y1)] straight runs covering the whole silhouette."""
    segs = []
    for lp in loops(cells):
        pts = simplify(lp + [lp[0]], tol)
        for a, b in zip(pts, pts[1:]):
            if math.dist(a, b) >= min_len: segs.append((a[0], a[1], b[0], b[1]))
    return segs
