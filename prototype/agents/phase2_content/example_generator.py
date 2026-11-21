"""
Agent za generisanje primera.

STATUS: pravi agent (bez LLM-a). Ne izmislja nove primere, nego iz svake lekcije
izdvaja delove "reseni_primer" i "kod" (lesson_generator ih pise na podacima iz studije
slucaja) i pravi od njih zbirku primera, povezanu sa jedinicom i ishodima.
Tako primeri u zbirci i primeri na casu su ISTI (nema neslaganja brojeva).

Izlaz: {"examples": [{"id": "P1", "unit": 1, "title": "...", "worked_solution": "...",
                      "code": "...", "outcomes": ["O1"]}]}
"""


def run(data: dict) -> dict:
    lessons = (data["inputs"].get("lesson_generator") or {}).get("lessons", [])
    plan = (data["inputs"].get("curriculum_structure") or {}).get("units", [])
    outcomes_by_unit = {u.get("unit"): u.get("outcomes", []) for u in plan}

    examples = []
    for lesson in lessons:
        sections = {s.get("type"): s for s in lesson.get("sections", []) if isinstance(s, dict)}
        worked = sections.get("reseni_primer")
        if not worked:
            continue
        code = sections.get("kod")
        examples.append({
            "id": f"P{len(examples) + 1}",
            "unit": lesson.get("unit"),
            "title": worked.get("title") or f"Primer iz lekcije {lesson.get('title')}",
            "worked_solution": worked.get("content", ""),
            "code": code.get("content", "") if code else "",
            "outcomes": outcomes_by_unit.get(lesson.get("unit"), []),
        })
    return {"examples": examples,
            "message": f"Izdvojeno {len(examples)} resenih primera iz {len(lessons)} lekcija."}
