"""Pomocne funkcije koje koristi vise agenata."""


def hello(data: dict, who: str, **extra) -> dict:
    """Vraca standardan hello world odgovor + spisak od koga je agent dobio ulaz."""
    return {
        "message": f"Zdravo, ja sam {who}.",
        "received_from": list(data.get("inputs", {}).keys()),
        **extra,
    }


def lessons_brief(lessons: list, full_lessons: list | None = None,
                  keep=("objasnjenje", "reseni_primer", "kod"), max_chars: int = 2200) -> list:
    """
    SKRACENE lekcije za prompt (besplatni LLM nalozi imaju limit tokena po zahtevu):
    zadrzava naslov, jedinicu, teme, ishode i samo bitne delove (objasnjenje, reseni primer, kod).

    lessons       - lekcije iz grafa (imaju ishode i teme) ili od agenta za lekcije
    full_lessons  - lekcije od agenta za lekcije (imaju delove 'sections'); ako ih nema, koristi se 'text'
    """
    sections = {l.get("unit"): l.get("sections", []) for l in (full_lessons or lessons)}
    out = []
    for l in lessons:
        secs = [s for s in sections.get(l.get("unit"), []) if isinstance(s, dict) and s.get("type") in keep]
        content = "\n\n".join(f"[{s.get('type')}] {s.get('content', '')}" for s in secs) or str(l.get("text", ""))
        if len(content) > max_chars:
            content = content[:max_chars] + " ..."
        out.append({k: l.get(k) for k in ("unit", "title", "topics", "outcomes") if l.get(k)} | {"content": content})
    return out


def course_context(course: dict) -> str:
    """
    Tekst za prompt: STUDIJA SLUCAJA i OGRANICENJA iz config/course.yaml.
    Isti tekst dobijaju lekcije, zadaci i test - zato pricaju o istom primeru.
    Ako u course.yaml nema ovih polja, vraca prazan tekst (agenti rade kao ranije, za bilo koju temu).
    """
    lines = []
    if course.get("case_study"):
        lines.append("STUDIJA SLUCAJA (koristi je kao primer kroz ceo kurs):\n" + str(course["case_study"]).strip())
    else:
        lines.append("Izaberi JEDAN konkretan, realan primer iz ove oblasti i koristi ga kroz ceo kurs.")
    if course.get("constraints"):
        lines.append("OGRANICENJA (obavezno postuj):\n" + "\n".join(f"- {c}" for c in course["constraints"]))
    return "\n\n".join(lines)
