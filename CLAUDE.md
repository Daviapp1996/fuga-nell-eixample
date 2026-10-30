# Fuga nell'Eixample

Gioco 2D visto dall'alto sulle vere strade dell'Eixample di Barcellona. Online su GitHub Pages:
https://daviapp1996.github.io/fuga-nell-eixample/ (si aggiorna da solo a ogni push su `main`).

## Visione del progetto
- Sempre **2D visto dall'alto**, mai 3D. Al massimo, in futuro, una vista inclinata stile navigatore ma restando 2D.
- Mappe di **città reali** come campo di gioco: le strade vere sono i percorsi.
- Un personaggio originale (**Kiko**) con **skin intercambiabili**; più avanti se ne aggiungeranno altre.
- Modalità attuale: inseguimento a labirinto (raccogli tessere, scappa dai piccioni). Idea successiva:
  **cattura la bandiera a squadre** con basi ai lati opposti della città (es. Montjuïc contro Besòs).
- Niente nomi, personaggi o grafica di giochi esistenti (es. Pac-Man): tutto deve essere originale.
- L'utente parla italiano: rispondi in italiano.

## Struttura
- `index.html` — il sito pubblicato. **Generato**: non modificarlo a mano.
- `src/game.html` — il codice vero del gioco (HTML + CSS + JS in un file). Contiene i segnaposto
  `__MAP__` e `__SAT__`, sostituiti in fase di assemblaggio.
- `data/map_min.json` — rete stradale e strati della mappa, già ruotati (griglia dritta).
- `data/sat_meta.json` — posizione e trasformazione di ogni blocco di foto aerea.
- `sat/` — foto aeree in blocchi da 1024 px + `overview.jpg` a bassa risoluzione.
- `tools/` — pipeline per rigenerare i dati (anche per altre zone o città).

## Flusso di lavoro
1. Modifica `src/game.html`.
2. `python3 tools/05_assemble.py` per rigenerare `index.html`.
3. Prova in locale: `python3 -m http.server` e apri http://localhost:8000
   (serve un server: le foto in `sat/` non si caricano aprendo il file direttamente).
4. Commit e push su `main`: GitHub Pages pubblica in 1-2 minuti.

## Pipeline dati (solo per cambiare zona o città)
1. `tools/00_download_osm.sh osm/` — strade da OpenStreetMap (API ufficiale, a riquadri per il limite di 50.000 nodi).
2. `python3 tools/01_build_graph.py osm eixample.json` — grafo incroci/strade, edifici, parchi.
3. `python3 tools/02_rotate_playfield.py eixample.json map_rot.json 1100 -80 20`
   — ruota di -44.7° (la griglia di Cerdà è inclinata di ~45°) e ritaglia il campo di gioco
   (lato 1100 m, centro spostato di -80, +20 m). Elenca anche i luoghi famosi dentro il campo.
4. `python3 tools/03_compact.py map_rot.json data/map_min.json`
5. `python3 tools/04_build_sat.py eixample.json` — foto aeree ICGC, zoom 19.
6. `python3 tools/05_assemble.py`

Bbox, angolo e centro sono ripetuti in più script: se li cambi, cambiali ovunque.
I file grezzi (`osm/`, `orto_tiles/`, `eixample.json`, `map_rot.json`) non sono nel repo: si rigenerano.

## Come funziona il gioco (src/game.html)
- Coordinate in metri, già ruotate; la camera segue Kiko con zoom (rotella, +/−, pinch).
- Movimento sul grafo: ogni entità sta su un arco (`e`) a una distanza (`s`) con verso (`dir`).
  Agli incroci si sceglie l'arco più allineato alla direzione desiderata.
- Piccioni: 4 comportamenti (`chase`, `ahead`, `pincer`, `shy`), percorso minimo con Dijkstra
  (risultati in cache), fasi alternate di dispersione (6 s) e inseguimento (20 s).
- Churros sui luoghi famosi: i piccioni diventano vulnerabili; se presi volano al nido sopra i tetti.
- **Modalità**: oggetto `MODES` (`chase` = fuga dai piccioni, `ctf` = ruba bandiera). Ogni modalità ha
  `init`, `update`, `drawWorld`, `drawEntities`, `mini`, `hud`/`hudHTML`, `hint`, `legend`, `pauseText`;
  il motore comune (grafo, movimento, camera, mappa, bussola) le chiama. La scelta è salvata in localStorage.
- **Scatto** (Spazio/Shift o ⚡ su telefono): `tryDash`, vale per tutti i personaggi (anche CPU).
- **Ruba bandiera** (`CTF`, `TEAMS`, `ROSTER`): 3 contro 3, Llobregat (sud, Kiko + 2 CPU) contro Besòs (nord, 3 CPU).
  Basi scelte con `setBases`; la metà campo si decide con `sideOf` (chi è nella propria metà prende l'avversario).
  I personaggi CPU usano `stepAI` (percorso minimo verso `goal = {e,s}`, evitando gli incroci presidiati)
  e `ctfThink` (ruoli `att`/`def`/`flex`). I parametri in `CTF` sono stati bilanciati con partite CPU contro CPU:
  se cambi basi o parametri, rifai la prova (la metà sud, verso Gran Via, è più facile da attaccare).
- Skin: oggetto `SKINS` (colori corpo, cappellino, visiera, scarpe; `tiles:true` per il motivo trencadís).
  Per una nuova skin basta aggiungere una voce. La scelta è salvata in localStorage.
- Due viste: `sat` (foto aerea, predefinita) e `night` (mappa vettoriale scura). Tasto V.
- Le foto si caricano a blocchi solo quando visibili; l'overview è sempre presente.

## Crediti obbligatori (già nel menu e nel README, non toglierli)
- Strade © OpenStreetMap contributors (ODbL).
- Foto aerea: Ortofoto territorial © Institut Cartogràfic i Geològic de Catalunya (ICGC).
  Prima di un uso pubblico più ampio o commerciale verificare le condizioni d'uso sul sito ICGC.
  Non usare immagini di Google Maps: le condizioni d'uso non lo consentono.
