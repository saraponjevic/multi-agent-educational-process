"""
POKRETANJE JEDNE SIMULACIJE - zajednicko za terminal (main.py) i vizuelnu platformu (app.py).

    result = run_simulation(topic="Osnove SQL upita")

Tok:  registar -> graf znanja -> LangGraph graf -> pokretanje -> cuvanje u output/
Usput engine salje DOGADJAJE (engine/events.py) koje platforma crta uzivo.
"""
import json
from datetime import datetime
from pathlib import Path

import yaml

from engine import events, llm
from engine.knowledge_graph import KnowledgeGraph
from engine.orchestrator import build_main_graph
from engine.registry import AgentRegistry

ROOT = Path(__file__).resolve().parent.parent


def load_course(topic: str | None = None) -> dict:
    course = yaml.safe_load((ROOT / "config" / "course.yaml").read_text(encoding="utf-8"))
    if topic and topic.strip() != str(course.get("topic", "")).strip():
        course["topic"] = topic
        # studija slucaja i ogranicenja u course.yaml su pisani za NJEGOVU temu (masinsko ucenje);
        # za drugu temu ih izbacujemo, pa agenti sami izaberu primer iz te oblasti
        course.pop("case_study", None)
        course.pop("constraints", None)
    return course


def run_simulation(topic: str | None = None, use_kg: bool = True, verbose: bool = True) -> dict:
    events.reset()
    registry = AgentRegistry(ROOT / "config" / "agents.yaml")
    if verbose:
        registry.print_summary()
        print(llm.describe())

    course = load_course(topic)
    kg = None
    if use_kg:
        kg = KnowledgeGraph(ROOT / "knowledge")
        kg.register_system(registry, course)
        print(f"Graf znanja: ucitana ontologija i {len(kg.rules)} pravila ({', '.join(kg.rules)})")

    graph = build_main_graph(registry, kg)
    print(f"Kurs koji se simulira: {course['topic']}")
    events.emit("run_start", topic=course["topic"], course=course, system=registry.describe(),
                llm=llm.describe())

    initial_state = {"course": course, "settings": registry.settings, "iteration": 0,
                     "results": {}, "log": {}, "abort": {}, "students": {}, "rounds": {}}
    final_state = graph.invoke(initial_state, config={"recursion_limit": 500})

    # ---------------- EVIDENCIJA ----------------
    out_dir = ROOT / "output"
    out_dir.mkdir(exist_ok=True)
    stamp = f"{datetime.now():%Y%m%d_%H%M%S}"
    out_file = out_dir / f"run_{stamp}.json"
    out_file.write_text(json.dumps(final_state, ensure_ascii=False, indent=2), encoding="utf-8")

    errors = [v for v in final_state["log"].values() if v["status"] == "error"]
    skipped = [v for v in final_state["log"].values() if v["status"] == "skipped"]
    print("\n================ KRAJ ================")
    print(f"Pokrenuto agenata/aktivnosti (ukupno poziva): {len(final_state['log'])}")
    print(f"Broj dorada (povratna sprega):     {final_state['iteration']}")
    print(f"Greske:                            {len(errors)}")
    for e in errors:
        print(f"   - {e['agent']}: {str(e['error'])[:200]}")
    if skipped:
        print(f"Preskoceno (zbog prekida):         {len(skipped)}")
    report = final_state["results"].get("final_report", {}).get("summary")
    if report:
        print(f"Zavrsni izvestaj:                  {report}")
    print(f"Ceo rezultat sacuvan u:            {out_file.relative_to(ROOT)}")

    # MATERIJALI: agenti koji vrate polje "files" dobijaju fajlove u output/materijali_<vreme>/
    docs = {}
    for result in final_state["results"].values():
        if isinstance(result, dict) and isinstance(result.get("files"), dict):
            docs.update(result["files"])
    if docs:
        mat_dir = out_dir / f"materijali_{stamp}"
        mat_dir.mkdir(exist_ok=True)
        for name, content in docs.items():
            (mat_dir / Path(name).name).write_text(str(content), encoding="utf-8")
        print(f"Materijali (markdown) sacuvani u:  {mat_dir.relative_to(ROOT)}  ({', '.join(docs)})")

    violations = []
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

    events.emit("run_end", summary=report, errors=len(errors), iterations=final_state["iteration"],
                files=docs, violations=violations, students=final_state.get("students", {}))

    events_file = out_dir / f"events_{stamp}.json"
    events_file.write_text(json.dumps(events.all_events(), ensure_ascii=False, indent=1, default=str),
                           encoding="utf-8")
    print(f"Dogadjaji (za reprodukciju u app.py): {events_file.relative_to(ROOT)}")
    return {"state": final_state, "stamp": stamp, "events_file": events_file}
