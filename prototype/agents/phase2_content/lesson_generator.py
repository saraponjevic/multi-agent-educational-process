"""
Agent za generisanje lekcija.                    *** KLJUCNI AGENT (LLM) ***

Ulaz:  nastavni plan, ishodi, (u doradi) primedbe optimizatora
Izlaz: {"lessons": [{"unit": 1, "title": "...", "text": "..."}]}

GRAF: plan NE uzima kao tekst od drugog agenta, nego ga cita iz grafa znanja
(SPARQL upit ispod): jedinica -> teme -> preduslovi -> ishodi sa pokazateljima.
Tako dobija strukturu koju su upisali i proverili agenti iz Faze 1.
"""
from engine.llm import ask_json, to_text

SYSTEM = (
    "Ti si iskusan nastavnik koji pise jasne, kratke i tacne lekcije prilagodjene nivou ucenika. "
    "Koristis jednostavan jezik i konkretne primere."
)


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

    user = f"""Kurs: {course['topic']}
Ciljna grupa: {course['target_group']}
Nastavni plan:
{to_text(units)}
Nastavni ishodi:
{to_text(outcomes)}
{rework_note}
Za SVAKU nastavnu jedinicu napisi lekciju od najvise 250 reci. Pisi na jeziku: {course['language']}.
Vrati JSON:
{{"lessons": [{{"unit": 1, "title": "...", "text": "..."}}]}}"""

    version = data["iteration"] + 1
    fallback = {"lessons": [
        {"unit": u.get("unit"), "title": u.get("title"), "text": f"(hello world tekst lekcije, verzija {version})"}
        for u in units
    ]}
    return ask_json(SYSTEM, user, fallback)

def write_graph(result: dict, g):
    """GRAF:  :Lekcija_1 a :Lekcija ; :zaJedinicu :Jedinica_1 ; :tekst "..." ."""
    for lesson in result.get("lessons", []):
        lek = g.node("Lekcija", f"Lekcija_{lesson['unit']}", label=lesson.get("title"))
        g.link(lek, "zaJedinicu", g.ref(f"Jedinica_{lesson['unit']}"))
        g.value(lek, "tekst", lesson.get("text"))
