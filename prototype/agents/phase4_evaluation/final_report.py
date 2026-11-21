"""
Agent za generisanje zavrsnog izvestaja.

STATUS: pravi agent (bez LLM-a) - sklapa izvestaj od rezultata drugih agenata.

Izlaz: {"summary": "...",
        "files": {"test.md": "...", "izvestaj.md": "..."}}
Fajlove iz polja "files" upisuje main.py u  output/materijali_<vreme>/.
"""


def run(data: dict) -> dict:
    inp = data["inputs"]
    course = data["course"]
    fb = inp.get("feedback_manager") or {}
    grader = inp.get("answer_grader") or {}
    quality = inp.get("quality_evaluator") or {}
    questions = (inp.get("test_generator") or {}).get("questions", [])

    summary = (f"Prolaz {data['iteration'] + 1}: ocena kvaliteta {fb.get('score')}, "
               f"prosek na testu {grader.get('average')}, potrebna dorada: {fb.get('needs_rework')}")
    return {
        "summary": summary,
        "files": {
            "test.md": test_md(course, questions),
            "izvestaj.md": report_md(data, inp, questions, grader, quality, fb, summary),
        },
    }


# ----------------------------------------------------------------------
def test_md(course, questions) -> str:
    lines = [f"# Test: {course.get('topic', '')}", ""]
    for i, q in enumerate(questions, 1):
        lines += [f"**{i}. ({q.get('id')}, ishod {q.get('outcome')})** {q.get('text', '')}", ""]
    lines += ["---", "", "## Kljuc (ocekivani odgovori)", ""]
    for q in questions:
        lines.append(f"- **{q.get('id')}:** {q.get('expected_answer', '')}")
    return "\n".join(lines) + "\n"


def report_md(data, inp, questions, grader, quality, fb, summary) -> str:
    course = data["course"]
    teacher = inp.get("teacher") or {}
    lines = [f"# Izvestaj o simulaciji nastave: {course.get('topic', '')}", "", summary, ""]

    # --- Faza 3: cas (nastavnik isporucuje delove, ucenici usvajaju ili ne) ---
    knowledge = (inp.get("knowledge_state") or {}).get("knowledge", {})
    lines += ["## 1. Cas (Faza 3)", "", "### Delovi lekcije koje je nastavnik isporucio", ""]
    for s in teacher.get("segments", []):
        who = [sid for sid, k in knowledge.items() if s.get("concept") in k.get("learned_concepts", [])]
        lines.append(f"- **{s.get('id')} [{s.get('concept')}]** {s.get('content', '')}  ")
        lines.append(f"  *usvojili:* {', '.join(who) if who else 'niko'}")
    lines += ["", "### Stanje znanja posle casa", "",
              "| Ucenik | Usvojio delova | Nivo znanja | Usvojene teme |", "|---|---|---|---|"]
    for sid, k in knowledge.items():
        lines.append(f"| {sid} | {k.get('learned')}/{k.get('heard')} | {k.get('estimate')} | "
                     f"{_cell(', '.join(k.get('mastered_topics', [])) or '-')} |")
    lines.append("")

    # --- Faza 4: test (aktivnost test_taking) ---
    grades = grader.get("grades", {})
    taking = (inp.get("test_taking") or {}).get("participants") or {}
    lines += ["## 2. Rezultati testa (Faza 4)", "",
              "| Ucenik | Ocena (0-100) | Komentar ocenjivaca |", "|---|---|---|"]
    for sid, g in grades.items():
        lines.append(f"| {sid} | {g.get('score')} | {_cell(g.get('comment'))} |")
    lines += ["", f"**Prosek:** {grader.get('average')}", ""]

    q_text = {q.get("id"): q.get("text", "") for q in questions}
    for sid, st in taking.items():
        g = grades.get(sid) or {}
        if not st:
            continue
        pts = {p.get("question_id"): p for p in g.get("points", []) if isinstance(p, dict)}
        plan = st.get("answer_plan") or {}
        lines += [f"### {sid}", ""]
        for a in st.get("answers", []):
            qid = a.get("question_id")
            p = pts.get(qid, {})
            lines += [f"- **{qid}** {q_text.get(qid, '')}",
                      f"  - odgovor: {a.get('answer', '')}",
                      f"  - plan iz memorije: {plan.get(qid, '?')}",
                      f"  - poeni: {p.get('points', '?')}/2 - {p.get('reason', '')}"]
        lines.append("")

    # --- Evaluacija i povratna sprega ---
    lines += ["## 3. Evaluacija i povratna sprega", "",
              f"- Ocena kvaliteta: {quality.get('score')}",
              f"- Potrebna dorada: {fb.get('needs_rework')}",
              f"- Vracanje na fazu: {fb.get('return_to') or '-'}",
              f"- Razlog: {fb.get('reason', '')}", ""]
    return "\n".join(lines)


def _cell(x) -> str:
    return str(x or "").replace("|", "/").replace("\n", " ")
