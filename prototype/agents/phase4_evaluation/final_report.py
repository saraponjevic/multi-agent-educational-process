"""
Agent za generisanje zavrsnog izvestaja.

STATUS: pravi agent (bez LLM-a) - sklapa izvestaj od rezultata drugih agenata.

Izlaz: {"summary": "...",
        "files": {"test.md": "...", "izvestaj.md": "..."}}
Fajlove iz polja "files" upisuje main.py u  output/materijali_<vreme>/.
"""

LEVELS = ["beginner", "intermediate", "advanced"]
LEVEL_NAMES = {"beginner": "pocetni", "intermediate": "srednji", "advanced": "napredni"}


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

    # --- Faza 3: cas ---
    lines += ["## 1. Cas (Faza 3)", "", "### Nastavnik", "", str(teacher.get("explanation", "")), ""]
    if teacher.get("question"):
        lines += [f"**Pitanje nastavnika:** {teacher['question']}", ""]
    for lvl in LEVELS:
        st = inp.get(f"student_{lvl}")
        if not st:
            continue
        lines += [f"**Ucenik ({LEVEL_NAMES[lvl]} nivo):** {st.get('answer', '')}"]
        if st.get("question_to_teacher"):
            lines += [f"  \n*Pitanje nastavniku:* {st['question_to_teacher']}"]
        lines.append("")

    # --- Faza 4: test ---
    grades = grader.get("grades", {})
    lines += ["## 2. Rezultati testa (Faza 4)", "",
              "| Ucenik | Ocena (0-100) | Komentar ocenjivaca |", "|---|---|---|"]
    for lvl in LEVELS:
        g = grades.get(f"student_test_{lvl}")
        if g:
            lines.append(f"| {LEVEL_NAMES[lvl]} | {g.get('score')} | {_cell(g.get('comment'))} |")
    lines += ["", f"**Prosek:** {grader.get('average')}", ""]

    q_text = {q.get("id"): q.get("text", "") for q in questions}
    for lvl in LEVELS:
        st = inp.get(f"student_test_{lvl}")
        g = grades.get(f"student_test_{lvl}") or {}
        if not st:
            continue
        pts = {p.get("question_id"): p for p in g.get("points", []) if isinstance(p, dict)}
        lines += [f"### Ucenik - {LEVEL_NAMES[lvl]} nivo", ""]
        for a in st.get("answers", []):
            qid = a.get("question_id")
            p = pts.get(qid, {})
            lines += [f"- **{qid}** {q_text.get(qid, '')}",
                      f"  - odgovor: {a.get('answer', '')}",
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
