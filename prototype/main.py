"""
GLAVNI PROGRAM - pokretanje celog sistema.

    python main.py              -> pokreni ceo nastavni proces
    python main.py --list       -> samo prikazi registrovane agente
    python main.py --graph      -> sacuvaj dijagram grafa (docs/graph.md)
    python main.py --course "Osnove SQL upita"   -> druga tema (inace se cita config/course.yaml)
    python main.py --no-kg      -> pokreni BEZ grafa znanja (kao ranije)
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import yaml

from engine import llm
from engine.knowledge_graph import KnowledgeGraph
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

    # 2) GRAF ZNANJA: ontologija + pravila za agente + SPARQL pravila kvaliteta
    course = yaml.safe_load((ROOT / "config" / "course.yaml").read_text(encoding="utf-8"))
    if args.course:
        course["topic"] = args.course
    kg = None
    if not args.no_kg:
        kg = KnowledgeGraph(ROOT / "knowledge")
        kg.register_system(registry, course)
        print(f"Graf znanja: ucitana ontologija i {len(kg.rules)} pravila ({', '.join(kg.rules)})")

    # 3) ORKESTRATOR: napravi LangGraph graf od registrovanih agenata
    graph = build_main_graph(registry, kg)

    if args.graph:
        mermaid = graph.get_graph(xray=True).draw_mermaid()
        out = ROOT / "docs" / "graph.md"
        out.parent.mkdir(exist_ok=True)
        out.write_text("```mermaid\n" + mermaid + "\n```\n", encoding="utf-8")
        print(f"Dijagram grafa sacuvan u {out}")
        return

    # 4) POKRENI ceo nastavni proces
    print(f"Kurs koji se simulira: {course['topic']}")

    initial_state = {
        "course": course,
        "settings": registry.settings,
        "iteration": 0,
        "results": {},
        "log": {},
        "abort": {},
    }
    final_state = graph.invoke(initial_state, config={"recursion_limit": 100})

    # 5) EVIDENCIJA: sacuvaj sve u output/ folder
    out_dir = ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    stamp = f"{datetime.now():%Y%m%d_%H%M%S}"
    out_file = out_dir / f"run_{stamp}.json"
    out_file.write_text(json.dumps(final_state, ensure_ascii=False, indent=2), encoding="utf-8")

    errors = [v for v in final_state["log"].values() if v["status"] == "error"]
    skipped = [v for v in final_state["log"].values() if v["status"] == "skipped"]
    print("\n================ KRAJ ================")
    print(f"Pokrenuto agenata (ukupno poziva): {len(final_state['log'])}")
    print(f"Broj dorada (povratna sprega):     {final_state['iteration']}")
    print(f"Greske:                            {len(errors)}")
    for e in errors:
        print(f"   - {e['agent']}: {str(e['error'])[:200]}")
    if skipped:
        print(f"Preskoceno agenata (zbog prekida): {len(skipped)}")
    report = final_state["results"].get("final_report", {}).get("summary")
    if report:
        print(f"Zavrsni izvestaj:                  {report}")
    print(f"Ceo rezultat sacuvan u:            {out_file.relative_to(ROOT)}")

    if kg is not None:
        files = kg.save(out_dir, f"graf_{stamp}")
        print("\n================ GRAF ZNANJA ================")
        for name, n in kg.stats().items():
            print(f"   {name:<28} {n:>4} trojki")
        violations = kg.check()
        print(f"Prekrsena pravila na kraju:        {len(violations)}")
        for v in violations:
            print(f"   - [{v['pravilo']}] {v['poruka']}  (odgovoran: {v['odgovoran']})")
        print(f"Graf sacuvan u:                    {', '.join(str(f.relative_to(ROOT)) for f in files)}")
        print("   (.ttl fajl moze da se otvori u Protege-u; upiti: python kg_query.py)")


if __name__ == "__main__":
    main()
