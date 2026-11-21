"""
Agent nastavnik (Teaching Agent).                *** KLJUCNI AGENT (LLM) ***

FAZA PODUCAVANJA (ne vise samo "nastavnik pita, ucenik odgovara"):
  Nastavnik lekcije deli na DELOVE (segmente) i isporucuje ih ucenicima JEDAN PO JEDAN.
  Faza 3 ima PETLJU (config/agents.yaml, loop kod faze teaching):

      nastavnik preda deo 1 -> aktivnost 'learning' (ucenici usvajaju) ->
      nastavnik preda deo 2 -> aktivnost 'learning' -> ... dok nastavnik ne kaze done = true

  Prvi poziv: pripremi sve delove - JEDAN poziv modela PO LEKCIJI (ne u svakom krugu petlje).
  Sledeci pozivi: samo uzme sledeci deo iz svog prethodnog rezultata (data["previous"]).

Izlaz u svakom krugu:
  {"segment": {"id": "S2", "unit": 1, "concept": "...", "content": "...", "outcomes": ["O1"]},
   "index": 1, "total": 6, "done": false,
   "segments": [...svi delovi...], "explanation": "ceo predat tekst (za izvestaj)"}
"""
from agents import graph_context
from engine.llm import ask_json, to_text

SYSTEM = (
    "Ti si nastavnik koji drzi cas. Gradivo delis na male celine koje ucenik moze da usvoji "
    "jednu po jednu, i objasnjavas jasno i strpljivo."
)

MOCK_PARTS = ["osnovna ideja", "kljucni pojmovi", "primer"]


def run(data: dict) -> dict:
    prev = data.get("previous") or {}
    same_pass = prev.get("iteration") == data["iteration"] and prev.get("segments") and not prev.get("done")

    if same_pass:                                   # sledeci krug petlje -> sledeci deo
        segments = prev["segments"]
        index = prev["index"] + 1
        source = prev.get("_source")
    else:                                           # prvi krug -> pripremi sve delove
        segments, source = prepare_segments(data)
        index = 0

    if not segments:
        return {"segment": None, "index": 0, "total": 0, "done": True, "segments": [],
                "explanation": "", "iteration": data["iteration"], "_source": source}

    segment = segments[index]
    done = index >= len(segments) - 1
    delivered = segments[: index + 1]
    return {
        "segment": segment,
        "index": index,
        "total": len(segments),
        "done": done,
        "segments": segments,
        "explanation": "\n\n".join(f"[{s['concept']}] {s['content']}" for s in delivered),
        "iteration": data["iteration"],
        "_source": source,
    }


def prepare_segments(data: dict) -> tuple[list, str]:
    course = data["course"]
    kg = data.get("kg")
    lessons = graph_context.lessons(kg) if kg else \
        (data["inputs"].get("lesson_generator") or {}).get("lessons", [])
    # delovi lekcije (uvod, objasnjenje, reseni primer...) dolaze od agenta za lekcije;
    # iz grafa uzimamo ishode jedinice
    sections = {l.get("unit"): l.get("sections", [])
                for l in (data["inputs"].get("lesson_generator") or {}).get("lessons", [])}
    lessons = [{**l, "sections": sections.get(l.get("unit"), [])} for l in lessons]
    for l in lessons:
        if l["sections"]:
            l.pop("text", None)          # ne saljemo isti sadrzaj dva puta
    scenario = (data["inputs"].get("teaching_scenario") or {}).get("scenario", [])

    # JEDAN POZIV MODELA PO LEKCIJI (manji zahtevi - besplatni nalozi imaju limit tokena po minutu)
    segments, source = [], None
    for lesson in lessons:
        segs, source = _lesson_segments(course, scenario, lesson)
        segments += segs
    for i, seg in enumerate(segments, 1):
        seg["id"] = f"S{i}"
    return segments, source


def _lesson_segments(course: dict, scenario, lesson: dict) -> tuple[list, str]:
    user = f"""Drzis cas iz kursa "{course['topic']}" za: {course['target_group']}.
Scenario casa: {to_text(scenario)}
Sada predajes OVU lekciju (uz nju su ishodi koje pokriva).
Lekcija ima delove (sections): uvod, objasnjenje, reseni primer, kod, ceste greske, rezime, provera.
{to_text(lesson)}

Pretvori lekciju u DELOVE CASA, redom kojim ih predajes. Prati delove lekcije (uvod -> objasnjenje ->
reseni primer -> ...), a dugacak deo podeli na vise delova casa (ukupno 4-8 delova). Svaki deo casa je
jedna mala celina (jedan pojam, formula ili korak primera) koju ucenik moze da usvoji ili ne usvoji,
oko 60-100 reci, kao da govoris u ucionici. U resenom primeru zadrzi ISTE brojeve kao u lekciji.
Deo "provera" pretvori u pitanje razredu. Za svaki deo navedi koje ishode (id, npr. "O1") podrzava -
koristi SAMO ishode navedene uz ovu lekciju.
Pisi na jeziku: {course['language']}.
Vrati JSON:
{{"segments": [{{"concept": "kratak naziv pojma", "content": "...", "outcomes": ["O1"]}}]}}"""

    parts = lesson.get("sections") or [{"title": p} for p in MOCK_PARTS]
    fallback = {"segments": [
        {"concept": f"{lesson.get('title')}: {s.get('title') or s.get('type')}",
         "content": f"(hello world) {s.get('content', '')}", "outcomes": lesson.get("outcomes") or []}
        for s in parts
    ]}
    result = ask_json(SYSTEM, user, fallback)

    segments = []
    for i, s in enumerate(result.get("segments", []), 1):
        if not isinstance(s, dict):
            continue
        segments.append({"unit": lesson.get("unit"), "concept": s.get("concept", f"deo {i}"),
                         "content": s.get("content", ""),
                         "outcomes": s.get("outcomes") or lesson.get("outcomes") or []})
    return segments, result.get("_source")
