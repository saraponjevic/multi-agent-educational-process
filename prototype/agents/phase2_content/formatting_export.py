"""
Agent za formatiranje i eksport.

STATUS: pravi agent (bez LLM-a) - samo formatira ono sto su napravili drugi agenti.

Ulaz:  ishodi, nastavni plan, lekcije, primeri, zadaci, resenja (Faza 1 i 2)
Izlaz: {"format": "markdown",
        "files": {"kurikulum.md": "...", "lekcije.md": "...", "zadaci.md": "..."}}

Agent NE pise fajlove na disk (da bi mogao da radi i kao eksterni HTTP agent).
Fajlove iz polja "files" na kraju upisuje main.py u  output/materijali_<vreme>/.
"""


def run(data: dict) -> dict:
    inp = data["inputs"]
    course = data["course"]
    outcomes = (inp.get("learning_outcomes") or {}).get("outcomes", [])
    units = (inp.get("curriculum_structure") or {}).get("units", [])
    lessons = (inp.get("lesson_generator") or {}).get("lessons", [])
    examples = (inp.get("example_generator") or {}).get("examples", [])
    exercises = (inp.get("exercise_generator") or {}).get("exercises", [])
    solutions = (inp.get("exercise_solver") or {}).get("solutions", {})

    files = {
        "kurikulum.md": curriculum_md(course, outcomes, units),
        "lekcije.md": lessons_md(course, lessons, examples),
        "zadaci.md": exercises_md(course, exercises, solutions),
    }
    return {"format": "markdown", "files": files,
            "received_from": [k for k, v in inp.items() if v]}


# ----------------------------------------------------------------------
def curriculum_md(course, outcomes, units) -> str:
    lines = [f"# Kurikulum: {course.get('topic', '')}", ""]
    if course.get("target_group"):
        lines += [f"**Ciljna grupa:** {course['target_group']}", ""]
    lines += ["## Nastavni ishodi", "", "| ID | Ishod | Nivo | Pokazatelj ostvarenosti |", "|---|---|---|---|"]
    for o in outcomes:
        lines.append(f"| {o.get('id', '')} | {_cell(o.get('text'))} | {_cell(o.get('level'))} "
                     f"| {_cell(o.get('indicator'))} |")
    lines += ["", "## Nastavni plan", ""]
    for u in units:
        lines.append(f"### {u.get('unit', '')}. {u.get('title', '')}")
        for t in u.get("topics", []):
            lines.append(f"- {t}")
        if u.get("outcomes"):
            lines.append(f"\n*Ishodi:* {', '.join(map(str, u['outcomes']))}")
        lines.append("")
    return "\n".join(lines)


def lessons_md(course, lessons, examples) -> str:
    lines = [f"# Lekcije: {course.get('topic', '')}", ""]
    for les in lessons:
        lines += [f"## {les.get('unit', '')}. {les.get('title', '')}", "", str(les.get("text", "")), ""]
    if examples:
        lines += ["## Primeri", ""] + [f"- {_text(e)}" for e in examples] + [""]
    return "\n".join(lines)


def exercises_md(course, exercises, solutions) -> str:
    lines = [f"# Zadaci: {course.get('topic', '')}", ""]
    for ex in exercises:
        meta = ", ".join(str(x) for x in (f"jedinica {ex.get('unit')}" if ex.get("unit") else None,
                                          ex.get("difficulty"), ex.get("outcome")) if x)
        lines += [f"### {ex.get('id', '')}" + (f" ({meta})" if meta else ""), "", str(ex.get("text", "")), ""]
        sol = solutions.get(ex.get("id")) if isinstance(solutions, dict) else None
        if sol:
            lines += [f"> **Resenje:** {_text(sol)}", ""]
    return "\n".join(lines)


def _text(x) -> str:
    if isinstance(x, dict):
        return x.get("text") or x.get("solution") or str(x)
    return str(x)


def _cell(x) -> str:
    return str(x or "").replace("|", "/").replace("\n", " ")
