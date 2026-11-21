"""
GENERICKI INTERFEJS UCENIKA  (StudentInterface)

Ovo je "ugovor": SVAKI simulirani ucenik u sistemu mora da ume ove 3 stvari:

    1. knowledge()          -> sta trenutno ZNA (njegova memorija / baza znanja)
    2. receive(piece)       -> PRIMI novo znanje ("e, sad imas i ovu vestinu")
                               i odluci da li ga je usvojio
    3. take_test(questions) -> pokaze sta zna (odgovori na pitanja)

Engine (aktivnosti "learn" i "take_test" u engine/activities.py) razgovara sa ucenikom
SAMO preko ove 3 funkcije. Zato se implementacija moze zameniti, a da se nista drugo ne menja:

    - agents/students/simple_student.py  -> nas GRUBO simulirani ucenik (random usvajanje)
    - neki drugi simulirani ucenik       -> nova klasa koja nasledjuje StudentInterface
                                            i u config/agents.yaml (sekcija students) promeni 'class'

DEO ZNANJA (piece) koji nastavnik isporucuje izgleda ovako:
    {"id": "S3", "unit": 1, "concept": "trening i test skup",
     "content": "Podatke delimo na ...", "outcomes": ["O2"]}

MEMORIJA ucenika je obican recnik (JSON), da bi mogla da putuje kroz LangGraph stanje
iz faze u fazu (ucenik u fazi 4 je ISTI onaj koji je slusao cas u fazi 3).
"""
from abc import ABC, abstractmethod


class StudentInterface(ABC):

    def __init__(self, student_id: str, params: dict, course: dict, memory: dict | None = None):
        self.id = student_id
        self.params = params or {}
        self.course = course or {}
        self.memory = memory if memory is not None else self.initial_memory()

    # ------------------------------------------------------------------
    #  MEMORIJA
    # ------------------------------------------------------------------
    def initial_memory(self) -> dict:
        """Sta ucenik zna PRE casa. Podrazumevano: predznanje iz profila (config/course.yaml)."""
        return {
            "prior_knowledge": list(self.params.get("prior_knowledge", [])),
            "learned": [],      # delovi lekcije koje je USVOJIO
            "missed": [],       # delovi lekcije koje je cuo, ali NIJE usvojio
        }

    def knowledge(self) -> dict:
        """1) Sta trenutno zna."""
        return {"prior_knowledge": self.memory["prior_knowledge"], "learned": self.memory["learned"]}

    # ------------------------------------------------------------------
    #  OBAVEZNE FUNKCIJE (svaka implementacija ih pravi na svoj nacin)
    # ------------------------------------------------------------------
    @abstractmethod
    def receive(self, piece: dict) -> dict:
        """
        2) Primi deo lekcije. Vrati {"absorbed": True/False, "reason": "..."}.
        Ako je usvojen, deo treba da zavrsi u self.memory["learned"].
        """

    @abstractmethod
    def take_test(self, questions: list[dict]) -> dict:
        """
        3) Uradi test KORISTECI SAMO svoju memoriju.
        questions: [{"id": "T1", "text": "...", "outcome": "O1"}]
        Vrati: {"answers": [{"question_id": "T1", "answer": "..."}], ...dodatno po zelji}
        """

    # ------------------------------------------------------------------
    #  Cuvanje u stanju (engine ovo poziva sam)
    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        return self.memory

    def summary(self) -> dict:
        """Kratak pregled za izvestaje i vizualizaciju."""
        learned, missed = self.memory["learned"], self.memory["missed"]
        heard = len(learned) + len(missed)
        return {
            "learned": len(learned),
            "heard": heard,
            "ratio": round(len(learned) / heard, 2) if heard else 0.0,
            "learned_ids": [p.get("id") for p in learned],
            "learned_concepts": [p.get("concept") for p in learned],
            "missed_concepts": [p.get("concept") for p in missed],
        }
