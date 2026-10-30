#!/usr/bin/env bash
# Scarica le strade di OpenStreetMap per l'area di gioco, in 8 riquadri
# (l'API OSM rifiuta richieste oltre 50.000 nodi).
# Uso: tools/00_download_osm.sh osm/
set -euo pipefail
OUT=${1:-osm}
mkdir -p "$OUT"
LON0=2.1600; LAT0=41.3870
for i in 0 1 2 3; do
  for j in 0 1; do
    lon0=$(python3 -c "print(round($LON0+0.0045*$i,4))"); lon1=$(python3 -c "print(round($LON0+0.0045*($i+1),4))")
    lat0=$(python3 -c "print(round($LAT0+0.006*$j,4))");  lat1=$(python3 -c "print(round($LAT0+0.006*($j+1),4))")
    curl -s -m 90 -o "$OUT/t_${i}_${j}.osm" "https://api.openstreetmap.org/api/0.6/map?bbox=$lon0,$lat0,$lon1,$lat1"
    echo "riquadro $i $j: $(wc -c < "$OUT/t_${i}_${j}.osm") byte"
  done
done
