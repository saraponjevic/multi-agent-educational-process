"""
AGENT INVOKER / ADAPTER.

Poziva agenta na isti način bez obzira da li je:
  - lokalni  -> obična Python funkcija
  - eksterni -> HTTP servis (šaljemo JSON, dobijamo JSON)

Takođe: meri vreme, hvata greške, proverava da li su stigli ulazi
i sve upisuje u evidenciju (log).
"""
import json
import threading
import time
import urllib.request
from datetime import datetime

from engine.registry import AgentSpec

_print_lock = threading.Lock()


def say(text: str):
    """Ispis koji se ne mesa kada vise agenata radi paralelno."""
    with _print_lock:
        print(text, flush=True)


def build_inputs(spec: AgentSpec, state: dict) -> dict:
    """Sakuplja ulaz za agenta: osnovni podaci + rezultati agenata od kojih zavisi."""
    results = state.get("results", {})
    return {
        "course": state.get("course", {}),
        "iteration": state.get("iteration", 0),
        "settings": state.get("settings", {}),
        "params": spec.params,
        "inputs": {dep: results.get(dep) for dep in spec.requires},
    }


def call_remote(spec: AgentSpec, payload: dict) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        spec.endpoint, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=spec.timeout_seconds) as resp:
        return json.loads(resp.read().decode("utf-8"))


def make_agent_node(spec: AgentSpec, phase_name: str):
    """Pravi LangGraph čvor (funkciju) za jednog agenta."""

    def node(state: dict) -> dict:
        iteration = state.get("iteration", 0)
        payload = build_inputs(spec, state)

        missing = [dep for dep, val in payload["inputs"].items() if val is None]
        if missing:
            say(f"   [!] {spec.id}: nedostaju ulazi od {missing} (nastavljam bez njih)")

        say(f"   > pokrecem  {spec.id:<28} ({spec.type})")
        start = time.perf_counter()
        try:
            if spec.type == "local":
                output = spec.callable(payload)
            else:
                output = call_remote(spec, payload)
            if not isinstance(output, dict):
                raise TypeError(f"agent mora da vrati dict, a vratio je {type(output).__name__}")
            status, error = "ok", None
        except Exception as e:  # agent je pukao -> ne rušimo ceo sistem
            output = {"error": str(e)}
            status, error = "error", str(e)

        duration = round(time.perf_counter() - start, 3)
        mark = "OK " if status == "ok" else "GRESKA"
        say(f"   < {mark:<6}    {spec.id:<28} {duration}s" + (f"  -> {error}" if error else ""))

        log_key = f"iter{iteration}|{spec.phase}|{spec.step}|{spec.id}"
        return {
            "results": {spec.id: output},
            "log": {
                log_key: {
                    "agent": spec.id,
                    "phase": phase_name,
                    "step": spec.step,
                    "iteration": iteration,
                    "status": status,
                    "error": error,
                    "duration_s": duration,
                    "finished_at": datetime.now().isoformat(timespec="seconds"),
                }
            },
        }

    return node
