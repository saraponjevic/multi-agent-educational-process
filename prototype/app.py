"""
VIZUELNA PLATFORMA - BACKEND (FastAPI).

    python app.py        -> server na http://127.0.0.1:8000
                            (+ React stranica iz frontend/dist, ako je napravljena sa `npm run build`)
    http://127.0.0.1:8000/docs   -> automatska dokumentacija API-ja (FastAPI je pravi sam)

Server NE radi simulaciju sam - samo je pokrece (engine/simulation.py) i prosledjuje
DOGADJAJE (engine/events.py) React stranici (folder frontend/).

API:
    GET  /api/system            opis sistema: faze, koraci, agenti, aktivnosti, ucenici, LLM rezim
    POST /api/start             {"topic": "..."} -> pokreni simulaciju u pozadini
    GET  /api/events?since=N    dogadjaji od rednog broja N (stranica pita svakih pola sekunde)
    GET  /api/runs              spisak snimaka ranijih pokretanja (output/events_*.json)
    GET  /api/replay?name=...   dogadjaji jednog snimka

Razvoj stranice (dva terminala):
    1) python app.py
    2) cd frontend && npm run dev      -> http://localhost:5173 (Vite salje /api zahteve ovom serveru)
"""
import json
import sys
import threading
import traceback
import webbrowser
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from engine import events, llm
from engine.registry import AgentRegistry
from engine.simulation import run_simulation

ROOT = Path(__file__).parent
FRONTEND_DIST = ROOT / "frontend" / "dist"
HOST, PORT = "127.0.0.1", 8000

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

app = FastAPI(title="Simulator nastavnog procesa",
              description="API vizuelne platforme multiagentskog sistema za simulaciju nastave.")

# ----------------------------------------------------------------------
#  Simulacija u pozadini (jedna u isto vreme)
# ----------------------------------------------------------------------
_run = {"thread": None, "error": None}


def _running() -> bool:
    return bool(_run["thread"] and _run["thread"].is_alive())


def _start(topic: str):
    def work():
        _run["error"] = None
        try:
            run_simulation(topic=topic or None, verbose=False)
        except Exception as e:
            traceback.print_exc()
            _run["error"] = str(e)
            events.emit("run_error", error=str(e))

    t = threading.Thread(target=work, daemon=True)
    _run["thread"] = t
    t.start()


# ----------------------------------------------------------------------
#  API
# ----------------------------------------------------------------------
class StartRequest(BaseModel):
    topic: str = ""


@app.get("/api/system")
def system():
    registry = AgentRegistry(ROOT / "config" / "agents.yaml")
    return {"system": registry.describe(), "llm": llm.describe(),
            "llm_enabled": llm.ENABLED, "running": _running()}


@app.post("/api/start")
def start(req: StartRequest):
    if _running():
        raise HTTPException(409, "simulacija vec radi - sacekaj da se zavrsi")
    _start(req.topic.strip())
    return {"ok": True}


@app.get("/api/events")
def get_events(since: int = 0):
    return {"events": events.since(since), "total": len(events.all_events()),
            "running": _running(), "error": _run["error"]}


@app.get("/api/runs")
def runs():
    files = sorted((ROOT / "output").glob("events_*.json"), reverse=True)
    return {"runs": [f.name for f in files[:30]]}


@app.get("/api/replay")
def replay(name: str):
    name = Path(name).name                    # samo ime fajla - ne sme da se izadje iz output/
    f = ROOT / "output" / name
    if not (name.startswith("events_") and f.exists()):
        raise HTTPException(404, "nema tog snimka")
    return {"events": json.loads(f.read_text(encoding="utf-8"))}


# ----------------------------------------------------------------------
#  React stranica (napravljena sa: cd frontend && npm run build)
# ----------------------------------------------------------------------
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
else:
    @app.get("/", response_class=HTMLResponse)
    def no_frontend():
        return ("<h2>React stranica jos nije napravljena</h2>"
                "<p>U terminalu: <code>cd frontend</code>, <code>npm install</code>, <code>npm run build</code>, "
                "pa ponovo <code>python app.py</code>.</p>"
                "<p>Ili za razvoj: <code>npm run dev</code> i otvori http://localhost:5173</p>"
                "<p>API dokumentacija: <a href='/docs'>/docs</a></p>")


if __name__ == "__main__":
    print(llm.describe())
    print(f"Vizuelna platforma: http://{HOST}:{PORT}   (API dokumentacija: /docs, Ctrl+C za gasenje)")
    if "--no-browser" not in sys.argv:
        threading.Timer(1.5, lambda: webbrowser.open(f"http://{HOST}:{PORT}")).start()
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")
