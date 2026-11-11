"""
GLAVNI PROGRAM - pokretanje celog sistema.

    python main.py              -> pokreni ceo nastavni proces
    python main.py --list       -> samo prikazi registrovane agente
    python main.py --graph      -> sacuvaj dijagram grafa (docs/graph.md)
    python main.py --course "Uvod u baze podataka"
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from engine.orchestrator import build_main_graph
from engine.registry import AgentRegistry

ROOT = Path(__file__).parent

# Da Windows terminal ne pravi problem sa nasim slovima
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--course", default="Uvod u masinsko ucenje")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--graph", action="store_true")
    args = parser.parse_args()

    # 1) ENGINE: ucitaj sve agente iz config fajla
    registry = AgentRegistry(ROOT / "config" / "agents.yaml")
    registry.print_summary()
    if args.list:
        return

    # 2) ORKESTRATOR: napravi LangGraph graf od registrovanih agenata
    graph = build_main_graph(registry)

    if args.graph:
        mermaid = graph.get_graph(xray=True).draw_mermaid()
        out = ROOT / "docs" / "graph.md"
        out.parent.mkdir(exist_ok=True)
        out.write_text("```mermaid\n" + mermaid + "\n```\n", encoding="utf-8")
        print(f"Dijagram grafa sacuvan u {out}")
        return

    # 3) POKRENI ceo nastavni proces
    initial_state = {
        "course": {"topic": args.course, "target_group": "studenti 3. godine"},
        "settings": registry.settings,
        "iteration": 0,
        "results": {},
        "log": {},
    }
    final_state = graph.invoke(initial_state, config={"recursion_limit": 100})

    # 4) EVIDENCIJA: sacuvaj sve u output/ folder
    out_dir = ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / f"run_{datetime.now():%Y%m%d_%H%M%S}.json"
    out_file.write_text(json.dumps(final_state, ensure_ascii=False, indent=2), encoding="utf-8")

    errors = [v for v in final_state["log"].values() if v["status"] != "ok"]
    print("\n================ KRAJ ================")
    print(f"Pokrenuto agenata (ukupno poziva): {len(final_state['log'])}")
    print(f"Broj dorada (povratna sprega):     {final_state['iteration']}")
    print(f"Greske:                            {len(errors)}")
    for e in errors:
        print(f"   - {e['agent']}: {e['error']}")
    print(f"Ceo rezultat sacuvan u:            {out_file.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
