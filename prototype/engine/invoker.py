"""
AGENT INVOKER / ADAPTER.

Poziva agenta na isti način bez obzira da li je:
  - lokalni  -> obična Python funkcija
  - eksterni -> HTTP servis (šaljemo JSON, dobijamo JSON)

Takođe: meri vreme, hvata greške, proverava da li su stigli ulazi
i sve upisuje u evidenciju (log).

GRAF ZNANJA: lokalni agent dobija data["kg"] (citanje grafa SPARQL-om).
Ako agent ima funkciju write_graph(result, g), invoker posle uspesnog rada
prevodi njegov rezultat u cvorove grafa i upisuje ih uz proveru pravila.
"""
import json
import sys
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
        "inputs": {dep: results.get(dep) for dep in spec.requires + spec.optional},
    }


def call_remote(spec: AgentSpec, payload: dict) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        spec.endpoint, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=spec.timeout_seconds) as resp:
        return json.loads(resp.read().decode("utf-8"))


def write_to_graph(spec: AgentSpec, kg, output: dict, iteration: int):
    """Ako agent ima write_graph(result, g) -> upisi njegov rezultat u graf znanja (uz proveru pravila)."""
    if kg is None or spec.type != "local":
        return None
    write_graph = getattr(sys.modules[spec.callable.__module__], "write_graph", None)
    if write_graph is None:
        return None
    g = kg.writer(spec.id, iteration)
    write_graph(output, g)
    report = kg.commit(spec.id, g)
    msg = f"      [graf] {spec.id}: upisano {report['upisano_trojki']} trojki"
    if report["odbijeno"]:
        msg += f", ODBIJENO {len(report['odbijeno'])}: " + "; ".join(report["odbijeno"][:3])
    say(msg)
    return report


def make_agent_node(spec: AgentSpec, phase_name: str, kg=None):
    """Pravi LangGraph čvor (funkciju) za jednog agenta."""

    def node(state: dict) -> dict:
        iteration = state.get("iteration", 0)
        log_key = f"iter{iteration}|{spec.phase}|{spec.step}|{spec.id}"

        # Ako je neki raniji agent pukao (i stop_on_error je ukljucen), ne trosimo vise LLM poziva
        if state.get("abort"):
            say(f"   - preskacem {spec.id:<28} (rad je prekinut zbog ranije greske)")
            return {"log": {log_key: {"agent": spec.id, "phase": phase_name, "step": spec.step,
                                      "iteration": iteration, "status": "skipped", "error": None,
                                      "duration_s": 0, "finished_at": None}}}

        payload = build_inputs(spec, state)

        missing = [dep for dep in spec.requires if payload["inputs"].get(dep) is None]
        if missing:
            say(f"   [!] {spec.id}: nedostaju ulazi od {missing} (nastavljam bez njih)")

        say(f"   > pokrecem  {spec.id:<28} ({spec.type})")
        start = time.perf_counter()
        graph_report = None
        try:
            if spec.type == "local":
                output = spec.callable({**payload, "kg": kg})   # lokalni agent moze da cita graf
            else:
                output = call_remote(spec, payload)             # eksterni dobija samo JSON
            if not isinstance(output, dict):
                raise TypeError(f"agent mora da vrati dict, a vratio je {type(output).__name__}")
            graph_report = write_to_graph(spec, kg, output, iteration)
            status, error = "ok", None
        except Exception as e:  # agent je pukao -> ne rušimo ceo sistem
            output = {"error": str(e)}
            status, error = "error", str(e)

        duration = round(time.perf_counter() - start, 3)
        mark = "OK " if status == "ok" else "GRESKA"
        say(f"   < {mark:<6}    {spec.id:<28} {duration}s" + (f"  -> {error}" if error else ""))

        update = {
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
                    "graph": graph_report,
                }
            },
        }
        if status == "error" and state.get("settings", {}).get("stop_on_error", True):
            say(f"   !!! PREKIDAM rad zbog greske u agentu '{spec.id}' (stop_on_error: true)")
            update["abort"] = {spec.id: error}
        return update

    return node
