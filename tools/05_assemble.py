"""Assembla index.html da src/game.html + data/*.json.
Uso (dalla radice del repo): python3 tools/05_assemble.py"""

src = open("src/game.html", encoding="utf-8").read()
out = (src.replace("__MAP__", open("data/map_min.json", encoding="utf-8").read())
          .replace("__SAT__", open("data/sat_meta.json", encoding="utf-8").read()))
head = """<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}[hidden]{display:none!important}</style>
"""
i = out.index("</style>") + len("</style>")
page = head + out[:i] + "\n</head>\n<body>\n" + out[i:] + "\n</body>\n</html>\n"
open("index.html", "w", encoding="utf-8").write(page)
print("index.html scritto,", len(page), "byte")
