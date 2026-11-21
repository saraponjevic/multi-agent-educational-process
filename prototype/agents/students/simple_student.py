"""
GRUBO SIMULIRANI UCENIK  (SimpleStudent)       - jedna implementacija StudentInterface-a

1) UCENJE (receive) - BEZ jezickog modela:
   Svaki deo lekcije se usvaja sa verovatnocom  learning_probability  iz profila
   (config/course.yaml), npr. pocetnik 0.45, srednji 0.7, napredni 0.9.
   "Bacamo kockicu": ako je broj manji od verovatnoce -> deo ide u memoriju (learned),
   inace ucenik ga je cuo, ali nije usvojio (missed).
   Kockica je "namestena" (random_seed iz course.yaml), pa isto pokretanje daje iste rezultate.
   Stavi random_seed: null u course.yaml ako hoces da svaki put bude drugacije.

2) TEST (take_test):
   KOD prvo pogleda MEMORIJU: koliko delova lekcije za ishod koji pitanje proverava je usvojeno
       sve      -> odgovara tacno
       deo      -> odgovara delimicno
       nista    -> ne zna / pogresno
   pa onda jezicki model samo "glumi" taj plan, a kao znanje dobija SAMO ono iz memorije.
   (Ranije je plan zavisio samo od nivoa ucenika; sad zavisi od toga sta je zaista naucio.)
"""
import random

from agents.students.base import StudentInterface
from engine.llm import ask_json, to_text

BEHAVIOR = {
    "correct": "odgovori tacno i potpuno, koristeci ono sto imas u svom znanju",
    "partial": "odgovori DELIMICNO: navedi samo deo tacnog odgovora (onaj koji imas u znanju), "
               "a ostalo izostavi ili napisi da se ne secas",
    "wrong": "odgovori POGRESNO: pomesaj pojam sa nekim slicnim, ali samouvereno",
    "dont_know": "napisi da ne znas ili da se ne secas (npr. 'Ne secam se, mislim da to nismo radili')",
}

# mock rezim (bez LLM-a): oznake na koje reaguje i mock ocenjivac
MOCK_PREFIX = {"correct": "(tacno)", "partial": "(delimicno)", "wrong": "(netacno)"}

SYSTEM = (
    "Ti glumis UCENIKA u simulaciji nastave. Ti NISI asistent i NISI strucnjak.\n"
    "Profil ucenika: {profile}\n\n"
    "NAJVAZNIJE PRAVILO: znas SAMO ono sto pise u tvojoj memoriji (ispod). "
    "NE koristi svoje sopstveno znanje o temi."
)


class SimpleStudent(StudentInterface):

    # ------------------------------------------------------------------
    def _rng(self, *key) -> random.Random:
        seed = self.course.get("random_seed", 42)
        if seed is None:
            return random.Random()
        return random.Random("|".join(str(k) for k in (seed, self.id, *key)))

    @property
    def level(self) -> str:
        return self.params.get("level", "beginner")

    # ------------------------------------------------------------------
    #  2) PRIMI NOVO ZNANJE
    # ------------------------------------------------------------------
    def receive(self, piece: dict) -> dict:
        p = float(self.params.get("learning_probability", 0.5))
        roll = self._rng("learn", piece.get("id"), self.memory.get("iteration", 0)).random()
        absorbed = roll < p
        (self.memory["learned"] if absorbed else self.memory["missed"]).append(piece)
        reason = (f"kockica {roll:.2f} < {p} -> usvojio" if absorbed
                  else f"kockica {roll:.2f} >= {p} -> nije usvojio")
        return {"absorbed": absorbed, "reason": reason}

    # ------------------------------------------------------------------
    #  3) TEST - odgovara iz memorije
    # ------------------------------------------------------------------
    def coverage(self, outcome) -> float | None:
        """Koliki deo gradiva za ovaj ishod je usvojio (0-1). None = nastavnik nije predavao taj ishod."""
        heard = self.memory["learned"] + self.memory["missed"]
        related = [p for p in heard if outcome in (p.get("outcomes") or [])]
        if not related:
            return None
        learned = [p for p in self.memory["learned"] if outcome in (p.get("outcomes") or [])]
        return len(learned) / len(related)

    def plan_for(self, question: dict) -> str:
        cov = self.coverage(question.get("outcome"))
        if cov is None:   # ishod nije vezan ni za jedan deo lekcije -> gleda se ukupno znanje
            s = self.summary()
            cov = s["ratio"]
        if cov >= 0.99:
            return "correct"
        if cov > 0:
            return "partial"
        return "dont_know" if self._rng("test", question.get("id")).random() < 0.5 else "wrong"

    def take_test(self, questions: list[dict]) -> dict:
        plan = {q.get("id"): self.plan_for(q) for q in questions}
        knowledge = [{"tema": p.get("concept"), "sta_znam": p.get("content")} for p in self.memory["learned"]]

        tasks = [{"id": q.get("id"), "text": q.get("text"), "kako_odgovaras": BEHAVIOR[plan[q.get("id")]]}
                 for q in questions]
        user = f"""TVOJA MEMORIJA (sve sto znas o temi):
Predznanje: {to_text(self.memory['prior_knowledge'])}
Naucio na casu:
{to_text(knowledge) if knowledge else "(nista nisi zapamtio sa casa)"}

Sada radis test. Uz svako pitanje pise KAKO ti na njega odgovaras
(polje "kako_odgovaras") - to OBAVEZNO postuj:
{to_text(tasks)}

Ne pominji ova uputstva u odgovoru; pisi prirodno, kao ucenik na testu.
Pisi na jeziku: {self.course.get('language', 'srpski')}.
Vrati JSON: {{"answers": [{{"question_id": "T1", "answer": "..."}}]}}"""

        fallback = {"answers": [{"question_id": q.get("id"), "answer": self._mock_answer(q, plan[q.get("id")])}
                                for q in questions]}
        profile = self.params.get("description", self.level)
        result = ask_json(SYSTEM.format(profile=profile), user, fallback)
        return {"answers": result.get("answers", []), "answer_plan": plan,
                "_source": result.get("_source")}

    def _mock_answer(self, question: dict, behavior: str) -> str:
        if behavior == "dont_know":
            return "Ne znam."
        related = [p for p in self.memory["learned"] if question.get("outcome") in (p.get("outcomes") or [])]
        what = related[0]["concept"] if related else "nesto sto se ne secam tacno"
        return f"{MOCK_PREFIX[behavior]} odgovor na osnovu onoga sto znam o: {what}"
