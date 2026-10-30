import json, math, sys
d = json.load(open(sys.argv[1]))
ANG = math.radians(-44.7)
cx, cy = d["w"] / 2, d["h"] / 2
ca, sa = math.cos(ANG), math.sin(ANG)
def rot(x, y):
    x -= cx; y -= cy
    return (round(x * ca - y * sa, 1), round(x * sa + y * ca, 1))
def rotflat(a):
    out = []
    for i in range(0, len(a), 2):
        out += rot(a[i], a[i + 1])
    return out

LON0, LAT0, LON1, LAT1 = 2.1600, 41.3870, 2.1780, 41.3990
mlat = 111320.0
mlon = 111320.0 * math.cos(math.radians((LAT0 + LAT1) / 2))
def geo(lat, lon):
    return rot((lon - LON0) * mlon, (LAT1 - lat) * mlat)

HALF = float(sys.argv[3]) / 2
OX, OY = float(sys.argv[4]), float(sys.argv[5])  # playfield centre offset
def inplay(p):
    return abs(p[0] - OX) <= HALF and abs(p[1] - OY) <= HALF

nodes = [rot(*n) for n in d["nodes"]]
edges = [[e[0], e[1], rotflat(e[2]), e[3], e[4]] for e in d["edges"]]
play, deco = [], []
for e in edges:
    pts = [(e[2][i], e[2][i + 1]) for i in range(0, len(e[2]), 2)]
    (play if all(inplay(p) for p in pts) else deco).append(e)

# largest connected component of play edges
adj = {}
for i, e in enumerate(play):
    adj.setdefault(e[0], []).append(i); adj.setdefault(e[1], []).append(i)
seen, best = set(), []
for s in adj:
    if s in seen: continue
    comp, st = [], [s]; seen.add(s)
    while st:
        n = st.pop(); comp.append(n)
        for ei in adj[n]:
            e = play[ei]; o = e[1] if e[0] == n else e[0]
            if o not in seen: seen.add(o); st.append(o)
    if len(comp) > len(best): best = comp
keep = set(best)
deco += [e for e in play if e[0] not in keep]
play = [e for e in play if e[0] in keep]

# merge nodes closer than 3 m (tidies doubled intersections)
idx, pn = {}, []
for e in play:
    for k in (0, 1):
        if e[k] not in idx:
            idx[e[k]] = len(pn); pn.append(nodes[e[k]])
        e[k] = idx[e[k]]

landmarks = [
    ("Casa Batlló", 41.39164, 2.16497),
    ("La Pedrera", 41.39525, 2.16196),
    ("Plaça de Catalunya", 41.38703, 2.17005),
    ("Plaça de Tetuan", 41.39472, 2.17553),
    ("Passeig de Gràcia", 41.39380, 2.16330),
    ("Rambla de Catalunya", 41.39250, 2.16200),
    ("Plaça d'Urquinaona", 41.38930, 2.17330),
    ("Casa Amatller", 41.39167, 2.16466),
]
lm = []
for n, la, lo in landmarks:
    p = geo(la, lo)
    lm.append({"name": n, "x": p[0], "y": p[1], "play": inplay(p)})

allpts = [c for e in edges for c in e[2]]
xs, ys = allpts[0::2], allpts[1::2]
out = {
    "bounds": [min(xs), min(ys), max(xs), max(ys)],
    "play": [OX - HALF, OY - HALF, OX + HALF, OY + HALF],
    "nodes": pn,
    "edges": [[e[0], e[1], e[2], e[3], e[4]] for e in play],
    "deco": [[e[2], e[3]] for e in deco],
    "buildings": [rotflat(b) for b in d["buildings"]],
    "parks": [rotflat(b) for b in d["parks"]],
    "landmarks": lm,
    "north": math.degrees(ANG),
}
L = 0
for e in play:
    p = e[2]
    for i in range(0, len(p) - 2, 2):
        L += math.hypot(p[i + 2] - p[i], p[i + 3] - p[i + 1])
json.dump(out, open(sys.argv[2], "w"), separators=(",", ":"))
print("play nodes", len(pn), "edges", len(play), "km", round(L / 1000, 2), "deco", len(deco))
for l in lm: print(l)
