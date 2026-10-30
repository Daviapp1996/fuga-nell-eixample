import glob, json, math, sys
import xml.etree.ElementTree as ET

SRC = sys.argv[1]
OUT = sys.argv[2]
LON0, LAT0, LON1, LAT1 = 2.1600, 41.3870, 2.1780, 41.3990

nodes = {}
ways = {}
for f in sorted(glob.glob(SRC + "/t_*.osm")):
    for ev, el in ET.iterparse(f):
        if el.tag == "node":
            nodes[el.get("id")] = (float(el.get("lon")), float(el.get("lat")))
        elif el.tag == "way":
            wid = el.get("id")
            if wid not in ways:
                tags = {t.get("k"): t.get("v") for t in el.findall("tag")}
                ways[wid] = ([n.get("ref") for n in el.findall("nd")], tags)
            el.clear()

# local projection in metres, y up -> we flip later for screen
mlat = 111320.0
mlon = 111320.0 * math.cos(math.radians((LAT0 + LAT1) / 2))
W = (LON1 - LON0) * mlon
H = (LAT1 - LAT0) * mlat
def proj(lon, lat):
    return (round((lon - LON0) * mlon, 1), round((LAT1 - lat) * mlat, 1))
def inside(lon, lat, pad=0.0):
    return LON0 - pad <= lon <= LON1 + pad and LAT0 - pad <= lat <= LAT1 + pad

ROADS = {"motorway","trunk","primary","secondary","tertiary","unclassified","residential",
         "living_street","pedestrian","primary_link","secondary_link","tertiary_link"}
BIG = {"primary","secondary","trunk","motorway"}

road_ways = []
buildings = []
parks = []
for wid, (refs, tags) in ways.items():
    hw = tags.get("highway")
    pts = [nodes[r] for r in refs if r in nodes]
    if len(pts) < 2:
        continue
    if hw in ROADS and tags.get("area") != "yes" and tags.get("tunnel") not in ("yes",):
        road_ways.append((refs, tags))
    elif "building" in tags and refs[0] == refs[-1]:
        if all(inside(*p, 0.0003) for p in pts):
            buildings.append([c for p in pts for c in proj(*p)])
    elif (tags.get("leisure") in ("park", "garden", "playground") or tags.get("landuse") in ("grass",)) and refs[0] == refs[-1]:
        if any(inside(*p) for p in pts):
            parks.append([c for p in pts for c in proj(*p)])

# graph: count usage to find intersections
use = {}
for refs, tags in road_ways:
    for i, r in enumerate(refs):
        use[r] = use.get(r, 0) + (2 if i in (0, len(refs) - 1) else 1)

# keep nodes inside bbox only; split ways at intersections and at bbox exit
gid = {}
gnodes = []
def g(r):
    if r not in gid:
        gid[r] = len(gnodes)
        gnodes.append(proj(*nodes[r]))
    return gid[r]

edges = []  # [a, b, [x,y,...polyline], big, name]
names = {}
for refs, tags in road_ways:
    seg = []
    def flush():
        if len(seg) >= 2:
            a, b = seg[0], seg[-1]
            if a != b:
                poly = [c for r in seg for c in proj(*nodes[r])]
                edges.append([g(a), g(b), poly, 1 if tags.get("highway") in BIG else 0,
                              tags.get("name", "")])
    for r in refs:
        if r not in nodes or not inside(*nodes[r]):
            flush(); seg = []; continue
        seg.append(r)
        if use.get(r, 0) > 1 and len(seg) > 1:
            flush(); seg = [r]
    flush()

# dedupe edges, drop tiny components
adj = {}
for i, e in enumerate(edges):
    adj.setdefault(e[0], []).append(i); adj.setdefault(e[1], []).append(i)
seen = set(); best = []
for s in adj:
    if s in seen: continue
    comp = []; st = [s]; seen.add(s)
    while st:
        n = st.pop(); comp.append(n)
        for ei in adj[n]:
            e = edges[ei]; o = e[1] if e[0] == n else e[0]
            if o not in seen: seen.add(o); st.append(o)
    if len(comp) > len(best): best = comp
keep = set(best)
edges = [e for e in edges if e[0] in keep]
# remap
idx = {}
nn = []
for e in edges:
    for k in (0, 1):
        if e[k] not in idx:
            idx[e[k]] = len(nn); nn.append(gnodes[e[k]])
        e[k] = idx[e[k]]

data = {"w": round(W), "h": round(H), "nodes": nn, "edges": edges,
        "buildings": buildings, "parks": parks}
json.dump(data, open(OUT, "w"), separators=(",", ":"))
print("W,H", round(W), round(H), "nodes", len(nn), "edges", len(edges),
      "buildings", len(buildings), "parks", len(parks))
nm = {}
for e in edges:
    if e[4]: nm[e[4]] = nm.get(e[4], 0) + 1
print(sorted(nm.items(), key=lambda x: -x[1])[:30])
