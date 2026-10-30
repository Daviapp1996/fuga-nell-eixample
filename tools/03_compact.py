"""Arrotonda le coordinate al metro per ridurre il peso della mappa.
Uso: python3 tools/03_compact.py map_rot.json data/map_min.json"""
import json, sys

d = json.load(open(sys.argv[1]))
R = lambda a: [round(v) for v in a]
d["nodes"] = [R(n) for n in d["nodes"]]
d["edges"] = [[e[0], e[1], R(e[2]), e[3], e[4]] for e in d["edges"]]
d["deco"] = [[R(p), b] for p, b in d["deco"]]
d["buildings"] = [R(b) for b in d["buildings"] if len(b) >= 6]
d["parks"] = [R(b) for b in d["parks"] if len(b) >= 6]
d["bounds"] = R(d["bounds"])
d["play"] = R(d["play"])
s = json.dumps(d, separators=(",", ":"), ensure_ascii=False)
open(sys.argv[2], "w").write(s)
print(len(s), "byte")
