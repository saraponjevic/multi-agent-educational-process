"""
DOGADJAJI (events) - "dnevnik uzivo" simulacije.

Engine na svakom bitnom mestu javi sta se desilo:
    emit("agent_start", agent="teacher", phase="teaching")
    emit("student_learned", student="student_beginner", absorbed=True, ...)

Ko god zeli, moze da "slusa" te dogadjaje:
  - main.py ih na kraju cuva u output/events_<vreme>.json (za kasniju reprodukciju),
  - app.py (vizuelna platforma) ih salje web stranici koja crta simulaciju.

Agenti i aktivnosti NE moraju da znaju za ovo - engine sam javlja dogadjaje.
"""
import threading
import time

_lock = threading.Lock()
_events: list[dict] = []
_listeners: list = []


def reset():
    """Pocetak nove simulacije - brise stare dogadjaje."""
    with _lock:
        _events.clear()


def subscribe(callback):
    """callback(event) se poziva za svaki novi dogadjaj."""
    with _lock:
        _listeners.append(callback)


def emit(kind: str, **data):
    with _lock:
        event = {"seq": len(_events), "time": round(time.time(), 3), "type": kind, **data}
        _events.append(event)
        listeners = list(_listeners)
    for cb in listeners:
        try:
            cb(event)
        except Exception:
            pass   # vizualizacija nikad ne sme da obori simulaciju


def since(seq: int) -> list[dict]:
    """Svi dogadjaji od rednog broja seq (web stranica pita: 'sta je novo od poslednjeg puta?')."""
    with _lock:
        return _events[seq:]


def all_events() -> list[dict]:
    with _lock:
        return list(_events)
