"""
GLAVNI PROGRAM - pokretanje celog sistema.

    python main.py              -> pokreni ceo nastavni proces
    python main.py --list       -> samo prikazi registrovane agente
    python main.py --graph      -> sacuvaj dijagram grafa (docs/graph.md)
    python main.py --course "Osnove SQL upita"   -> druga tema (inace se cita config/course.yaml)
    python main.py --no-kg      -> pokreni BEZ grafa znanja (kao ranije)

Vizuelna platforma (pregledac):  python app.py
"""
import argparse
import sys
from pathlib import Path

from engine import llm
from engine.orchestrator import build_main_graph
from engine.registry import AgentRegistry
from engine.simulation import run_simulation

ROOT = Path(__file__).parent

# Da Windows terminal ne pravi problem sa nasim slovima
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--course", help="tema kursa (ako se ne navede, cita se iz config/course.yaml)")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--graph", action="store_true")
    parser.add_argument("--test-llm", action="store_true", help="samo jedan probni poziv modela")
    parser.add_argument("--no-kg", action="store_true", help="bez grafa znanja")
    args = parser.parse_args()

    if args.test_llm:
        llm.test_connection()
        return

    # 1) ENGINE: ucitaj sve agente iz config fajla
    registry = AgentRegistry(ROOT / "config" / "agents.yaml")
    registry.print_summary()
    print(llm.describe())
    if args.list:
        return

    # 2) GRAF (samo crtez) - dijagram toka sa fazama, koracima, petljama i aktivnostima
    if args.graph:
        graph = build_main_graph(registry, None)
        mermaid = graph.get_graph(xray=True).draw_mermaid()
        out = ROOT / "docs" / "graph.md"
        out.parent.mkdir(exist_ok=True)
        out.write_text("```mermaid\n" + mermaid + "\n```\n", encoding="utf-8")
        print(f"Dijagram grafa sacuvan u {out}")
        return

    # 3) POKRENI ceo nastavni proces (engine/simulation.py)
    run_simulation(topic=args.course, use_kg=not args.no_kg, verbose=False)


if __name__ == "__main__":
    main()
