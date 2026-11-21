"""
Agent za generisanje lekcija.                    *** KLJUCNI AGENT (LLM) ***

Ulaz:  nastavni plan, ishodi, studija slucaja i ograničenja (course.yaml), (u doradi) primedbe optimizatora
Izlaz: {"lessons": [{"unit": 1, "title": "...", "sections": [...], "text": "..."}]}

LEKCIJA KAO PRAVA LEKCIJA - svaka ima iste delove (SECTION_TYPES):
    uvod -> objasnjenje -> reseni_primer -> kod -> ceste_greske -> rezime -> provera
Rešeni primer koristi STUDIJU SLUCAJA iz course.yaml (isti primer kroz ceo kurs).
"text" = svi delovi spojeni u jedan tekst (za graf znanja i agente koji citaju ceo tekst).

GRAF: plan NE uzima kao tekst od drugog agenta, nego ga cita iz grafa znanja
(SPARQL upit ispod): jedinica -> teme -> preduslovi -> ishodi sa pokazateljima.
Tako dobija strukturu koju su upisali i proverili agenti iz Faze 1.
"""
from agents.common import course_context
from engine.llm import ask_json, to_text

SYSTEM = (
    "Ti si iskusan nastavnik koji pise jasne i tacne lekcije prilagodjene nivou ucenika. "
    "Lekcija ima strukturu prave lekcije: motivacija, objasnjenje, primer resen korak po korak "
    "sa konkretnim brojevima, cest greske i kratak rezime."
)

# redosled i znacenje delova lekcije (isti za svaku temu)
SECTION_TYPES = {
    "uvod": "Uvod i motivacija - zasto je ovo bitno, veza sa studijom slucaja (2-4 recenice)",
    "objasnjenje": "Objasnjenje kljucnih pojmova (definicije, formule ako su dozvoljene)",
    "reseni_primer": "Primer resen KORAK PO KORAK na konkretnim podacima iz studije slucaja "
                     "(mala tabela ili brojevi, svaki korak racuna/zakljucka)",
    "kod": "Kratak kod koji radi isto sto i reseni primer (ako tema ima smisla za kod; inace izostavi)",
    "ceste_greske": "2-3 tipicne greske ucenika i kako ih izbeci",
    "rezime": "Rezime u 3-5 teza",
    "provera": "2 kratka pitanja za samoproveru (bez odgovora)",
}

PLAN_IZ_GRAFA = """
SELECT ?rb ?jedinica ?tema ?preduslov ?ishod ?pokazatelj WHERE {
  ?j a :NastavnaJedinica ; :redniBroj ?rb ; rdfs:label ?jedinica .
  OPTIONAL { ?j :sadrziTemu ?t . ?t rdfs:label ?tema .
             OPTIONAL { ?t :imaPreduslov/rdfs:label ?preduslov } }
  OPTIONAL { ?j :pokrivaIshod ?i . ?i rdfs:label ?ishod .
             OPTIONAL { ?i :pokazatelj ?pokazatelj } }
}
ORDER BY ?rb
"""


def plan_from_graph(kg) -> list:
    """Rezultat SPARQL upita -> lista jedinica sa temama, preduslovima i ishodima."""
    units = {}
    for row in kg.query(PLAN_IZ_GRAFA):
        u = units.setdefault(row["rb"], {"unit": row["rb"], "title": row["jedinica"],
                                         "topics": [], "prerequisites": [], "outcomes": []})
        for key, val in (("topics", row["tema"]), ("prerequisites", row["preduslov"])):
            if val and val not in u[key]:
                u[key].append(val)
        if row["ishod"]:
            o = {"text": row["ishod"], "indicator": row["pokazatelj"]}
            if o not in u["outcomes"]:
                u["outcomes"].append(o)
    return list(units.values())


def run(data: dict) -> dict:
    course = data["course"]
    kg = data.get("kg")
    units = plan_from_graph(kg) if kg is not None else []
    if not units:   # bez grafa -> kao ranije, tekst od agenta za plan
        units = (data["inputs"].get("curriculum_structure") or {}).get("units", [])
    outcomes = (data["inputs"].get("learning_outcomes") or {}).get("outcomes", [])
    # Ako smo u doradi (povratna sprega), optimizator je ostavio primedbe:
    corrections = (data["inputs"].get("optimizer") or {}).get("corrections", [])

    rework_note = ""
    if data["iteration"] > 0 and corrections:
        rework_note = f"\nOVO JE DORADA. Uvazi sledece primedbe evaluacije:\n{to_text(corrections)}\n"

    sections_spec = "\n".join(f'  "{k}": {v}' for k, v in SECTION_TYPES.items())
    user = f"""Kurs: {course['topic']}
Ciljna grupa: {course['target_group']}
Nastavni plan:
{to_text(units)}
Nastavni ishodi:
{to_text(outcomes)}

{course_context(course)}
{rework_note}
Za SVAKU nastavnu jedinicu napisi lekciju (ukupno 400-600 reci) sa delovima (type), ovim redom:
{sections_spec}
Primer i kod moraju koristiti ISTE podatke (iste brojeve) i biti tacni.
Pisi na jeziku: {course['language']}. Kod stavi u markdown blok (```).
Vrati JSON:
{{"lessons": [{{"unit": 1, "title": "...", "sections": [{{"type": "uvod", "title": "...", "content": "..."}}]}}]}}"""

    version = data["iteration"] + 1
    fallback = {"lessons": [
        {"unit": u.get("unit"), "title": u.get("title"),
         "sections": [{"type": t, "title": t.replace("_", " ").capitalize(),
                       "content": f"(hello world) {t} - lekcija '{u.get('title')}', verzija {version}"}
                      for t in SECTION_TYPES]}
        for u in units
    ]}
    result = ask_json(SYSTEM, user, fallback)
    for lesson in result.get("lessons", []):
        lesson["sections"] = [s for s in lesson.get("sections", []) if isinstance(s, dict)]
        lesson["text"] = lesson_text(lesson)
    return result


def lesson_text(lesson: dict) -> str:
    """Svi delovi lekcije spojeni u jedan markdown tekst."""
    if not lesson.get("sections"):
        return str(lesson.get("text", ""))
    return "\n\n".join(f"### {s.get('title') or s.get('type')}\n{s.get('content', '')}"
                       for s in lesson["sections"])


def write_graph(result: dict, g):
    """GRAF:  :Lekcija_1 a :Lekcija ; :zaJedinicu :Jedinica_1 ; :tekst "..." ."""
    for lesson in result.get("lessons", []):
        lek = g.node("Lekcija", f"Lekcija_{lesson['unit']}", label=lesson.get("title"))
        g.link(lek, "zaJedinicu", g.ref(f"Jedinica_{lesson['unit']}"))
        g.value(lek, "tekst", lesson.get("text"))
