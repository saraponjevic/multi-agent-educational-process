"""
CITANJE IZ GRAFA ZNANJA - zajednicki upiti koje koriste agenti.

Umesto da agent dobije TEKST (JSON) od drugog agenta, on pita graf i dobija
STRUKTURU koju su upisali i proverili svi prethodni agenti zajedno.

Svaka funkcija vraca podatke u ISTOM obliku koji su agenti i ranije koristili,
pa promena u agentu je samo jedan red:

    outcomes = graph_context.outcomes(kg) if kg else <stari nacin iz data["inputs"]>

Ako je sistem pokrenut bez grafa (python main.py --no-kg), kg je None
i agent radi po starom.
"""


def _id(node: str, prefix: str) -> str:
    """':Ishod_O1' -> 'O1'"""
    return node.split(":", 1)[-1].removeprefix(prefix)


def outcomes(kg) -> list:
    """Ishodi sa kompetencijom, nivoom i pokazateljem."""
    rows = kg.query("""
        SELECT ?i ?tekst ?nivo ?pokazatelj ?komp WHERE {
          ?i a :NastavniIshod ; rdfs:label ?tekst .
          OPTIONAL { ?i :nivo ?nivo }
          OPTIONAL { ?i :pokazatelj ?pokazatelj }
          OPTIONAL { ?komp :imaIshod ?i }
        } ORDER BY ?i""")
    return [{"id": _id(r["i"], "Ishod_"), "text": r["tekst"], "level": r["nivo"],
             "indicator": r["pokazatelj"], "competency": _id(r["komp"], "Komp_") if r["komp"] else None}
            for r in rows]


def lessons(kg) -> list:
    """Lekcije redom po jedinicama, sa temama i ishodima te jedinice."""
    rows = kg.query("""
        SELECT ?rb ?naslov ?tekst
               (GROUP_CONCAT(DISTINCT ?tema; separator="; ") AS ?teme)
               (GROUP_CONCAT(DISTINCT ?ishod; separator=" ") AS ?ishodi) WHERE {
          ?l a :Lekcija ; :zaJedinicu ?j ; rdfs:label ?naslov .
          OPTIONAL { ?l :tekst ?tekst }
          ?j :redniBroj ?rb .
          OPTIONAL { ?j :sadrziTemu/rdfs:label ?tema }
          OPTIONAL { ?j :pokrivaIshod ?ishod }
        } GROUP BY ?rb ?naslov ?tekst ORDER BY ?rb""")
    return [{"unit": r["rb"], "title": r["naslov"], "text": r["tekst"],
             "topics": [t for t in (r["teme"] or "").split("; ") if t],
             "outcomes": [_id(i, "http://example.org/kurikulum#Ishod_") for i in (r["ishodi"] or "").split()]}
            for r in rows]


def questions(kg) -> list:
    """Pitanja sa testa, sa ishodom koji proveravaju i ocekivanim odgovorom."""
    rows = kg.query("""
        SELECT ?p ?tekst ?ishod ?ocekivano WHERE {
          ?p a :Pitanje ; rdfs:label ?tekst .
          OPTIONAL { ?p :proveravaIshod ?ishod }
          OPTIONAL { ?p :ocekivaniOdgovor ?ocekivano }
        } ORDER BY ?p""")
    return [{"id": _id(r["p"], "Pitanje_"), "text": r["tekst"],
             "outcome": _id(r["ishod"], "Ishod_") if r["ishod"] else None,
             "expected_answer": r["ocekivano"]} for r in rows]


def test_answers(kg) -> dict:
    """Odgovori ucenika na testu: {'student_test_beginner': [{'question_id': 'T1', 'answer': '...'}]}"""
    rows = kg.query("""
        SELECT ?profil ?p ?tekst WHERE {
          ?o a :Odgovor ; :odUcenika ?u ; :naPitanje ?p ; :tekst ?tekst .
          ?u :profil ?profil .
        } ORDER BY ?profil ?p""")
    result = {}
    for r in rows:
        result.setdefault(f"student_test_{r['profil']}", []).append(
            {"question_id": _id(r["p"], "Pitanje_"), "answer": r["tekst"]})
    return result


def topics(kg) -> list:
    """Sve teme kursa redom po jedinicama."""
    rows = kg.query("""
        SELECT DISTINCT ?t ?naziv ?rb WHERE {
          ?j :sadrziTemu ?t ; :redniBroj ?rb . ?t rdfs:label ?naziv .
        } ORDER BY ?rb""")
    return [{"node": r["t"], "name": r["naziv"], "unit": r["rb"]} for r in rows]
