# Frontend – vizuelna platforma (React + Vite)

Stranica koja crta simulaciju nastavnog procesa. Podatke dobija od FastAPI servera (`../app.py`).

## Pokretanje

**Prvi put:** `npm install`

**Razvoj** (izmene se odmah vide u pregledaču), u dva terminala:
```powershell
# terminal 1 (folder prototype)
python app.py --no-browser
# terminal 2 (folder prototype/frontend)
npm run dev          # otvori http://localhost:5173
```

**Gotova verzija** (jedan server, jedna adresa):
```powershell
npm run build        # napravi folder dist/
cd ..
python app.py        # http://127.0.0.1:8000 servira i API i stranicu
```

## Struktura

| Fajl | Šta radi |
|---|---|
| `src/api.js` | pozivi ka serveru (`/api/system`, `/api/start`, `/api/events`, `/api/runs`, `/api/replay`) |
| `src/simulation/reducer.js` | stanje stranice: kako svaki događaj simulacije menja prikaz |
| `src/simulation/useSimulation.js` | hook: pokretanje, praćenje uživo, snimci, red čekanja događaja |
| `src/simulation/labels.js` | boje faza, nazivi artefakata i nivoa učenika |
| `src/App.jsx` | slaže stranicu od komponenti |
| `src/components/Header.jsx` | gornja traka (LLM režim, status, brzina, snimci) |
| `src/components/Chat.jsx` | razgovor: unos teme i šta se dešava |
| `src/components/Phases.jsx` | četiri faze |
| `src/components/PhaseBoard.jsx` | tok izabrane faze: agenti, aktivnosti, petlja |
| `src/components/Classroom.jsx` | učionica: nastavnik → učenici (tačkice), znanje i ocene |
| `src/components/Artifacts.jsx` | lista artefakata, prozor sa sadržajem, dnevnik |
| `src/components/Content.jsx` | prikaz markdown fajlova i JSON izlaza agenata |
| `src/index.css` | izgled (svetla i tamna tema) |

`npm run lint` proverava kod (oxlint).
