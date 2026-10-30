"""Scarica l'ortofoto ICGC (zoom 19, ~22 cm/pixel), la taglia in blocchi da 1024 px
e calcola per ogni blocco la trasformazione che lo posa sotto le strade ruotate.

Uso: python3 tools/04_build_sat.py eixample.json
Scrive: sat/*.jpg (blocchi + overview) e data/sat_meta.json

eixample.json e' l'uscita di 01_build_graph.py (prima della rotazione).
I parametri devono restare uguali a quelli di 02_rotate_playfield.py (bbox e angolo).
"""
import json, math, os, subprocess, sys, concurrent.futures as cf
from PIL import Image

Z = 19
LON0, LAT0, LON1, LAT1 = 2.1600, 41.3870, 2.1780, 41.3990
ANGLE = -44.7
TILE_DIR = "orto_tiles"
URL = "https://geoserveis.icgc.cat/icc_mapesmultibase/noutm/wmts/orto/GRID3857/{z}/{x}/{y}.jpeg"

def tile_xy(lon, lat, z):
    n = 2 ** z
    return int((lon + 180) / 360 * n), int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)

X0, Y0 = tile_xy(LON0, LAT1, Z)
X1, Y1 = tile_xy(LON1, LAT0, Z)
X1 += 1; Y1 += 1

os.makedirs(TILE_DIR, exist_ok=True)
def get(xy):
    x, y = xy
    f = f"{TILE_DIR}/{x}_{y}.jpg"
    if os.path.exists(f) and os.path.getsize(f) > 1000:
        return 0
    return subprocess.run(["curl", "-s", "-m", "30", "--retry", "2", "-o", f, URL.format(z=Z, x=x, y=y)]).returncode
jobs = [(x, y) for x in range(X0, X1) for y in range(Y0, Y1)]
with cf.ThreadPoolExecutor(4) as ex:
    fails = sum(1 for r in ex.map(get, jobs) if r)
print(len(jobs), "tessere,", fails, "fallite")

d = json.load(open(sys.argv[1]))
mlat = 111320.0
mlon = 111320.0 * math.cos(math.radians((LAT0 + LAT1) / 2))
cx, cy = d["w"] / 2, d["h"] / 2
A = math.radians(ANGLE); ca, sa = math.cos(A), math.sin(A)
n = 2 ** Z
lon_l = X0 / n * 360 - 180
lat_t = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * Y0 / n))))
lat_b = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * Y1 / n))))
Wpx, Hpx = (X1 - X0) * 256, (Y1 - Y0) * 256
ox, oy = (lon_l - LON0) * mlon, (LAT1 - lat_t) * mlat
sx, sy = (360 / n / 256) * mlon, (lat_t - lat_b) * mlat / Hpx

mos = Image.new("RGB", (Wpx, Hpx))
for x in range(X0, X1):
    for y in range(Y0, Y1):
        mos.paste(Image.open(f"{TILE_DIR}/{x}_{y}.jpg").convert("RGB"), ((x - X0) * 256, (y - Y0) * 256))

def aff(px, py, scx, scy):
    lx, ly = ox + px * sx - cx, oy + py * sy - cy
    return [round(scx * ca, 6), round(scx * sa, 6), round(-scy * sa, 6), round(scy * ca, 6),
            round(lx * ca - ly * sa, 3), round(lx * sa + ly * ca, 3)]

os.makedirs("sat", exist_ok=True)
C = 1024; chunks = []
for i in range(0, Wpx, C):
    for j in range(0, Hpx, C):
        w, h = min(C, Wpx - i), min(C, Hpx - j)
        fn = f"sat/c_{i // C}_{j // C}.jpg"
        mos.crop((i, j, i + w, j + h)).save(fn, quality=74, optimize=True, progressive=True)
        a = aff(i, j, sx, sy)
        chunks.append({"f": fn, "w": w, "h": h, "m": a,
                       "c": [round(a[4] + a[0] * w / 2 + a[2] * h / 2, 1), round(a[5] + a[1] * w / 2 + a[3] * h / 2, 1)],
                       "r": round(math.hypot(w * sx, h * sy) / 2 + 2, 1)})
ov = mos.resize((Wpx // 4, Hpx // 4), Image.LANCZOS)
ov.save("sat/overview.jpg", quality=78, optimize=True)
json.dump({"chunks": chunks, "overview": {"f": "sat/overview.jpg", "w": ov.width, "h": ov.height, "m": aff(0, 0, sx * 4, sy * 4)}},
          open("data/sat_meta.json", "w"), separators=(",", ":"))
print(len(chunks), "blocchi scritti in sat/")
