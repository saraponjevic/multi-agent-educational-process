"""
AKTIVNOSTI - cvorovi LangGraph grafa koji NISU agenti.

Profesorova ideja: "polaganje testa" nije novi agent, nego AKTIVNOST koju sprovode
POSTOJECI agenti ucenici nad POSTOJECIM resursom (testom). Isto vazi za "slusanje casa".

Aktivnost se opisuje u config/agents.yaml:
    - id: test_taking
      action: take_test                  # STA se radi        (funkcija iz ACTIONS ispod)
      participants: [student_beginner]   # KO to radi         (ucenici iz sekcije students)
      resource: test_generator           # NAD CIM se radi    (izlaz agenta test_generator)

Engine za svakog ucesnika:
    1. ucita ucenika iz zajednickog stanja (njegovu MEMORIJU),
    2. pozove odgovarajucu funkciju interfejsa (receive / take_test),
    3. sacuva memoriju nazad u stanje,
    4. rezultat aktivnosti upise u results[<id aktivnosti>] - kao da je agent
       (zato ga sledeci agent, npr. answer_grader, dobija kao obican ulaz).
"""
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from engine.events import emit
from engine.invoker import say


# ----------------------------------------------------------------------
#  AKCIJE: sta ucenik radi u aktivnosti
# ----------------------------------------------------------------------
def act_learn(student, resource: dict, ctx: dict) -> dict | None:
    """Ucenik prima deo lekcije koji je nastavnik upravo isporucio (resource = izlaz nastavnika)."""
    piece = (resource or {}).get("segment")
    if not piece:
        return None
    res = student.receive(piece)
    summary = student.summary()
    emit("student_learned", student=student.id, piece=piece.get("id"), concept=piece.get("concept"),
         absorbed=res["absorbed"], reason=res.get("reason"), learned=summary["learned"],
         heard=summary["heard"], phase=ctx["phase"], round=ctx["round"])
    return {"piece": piece.get("id"), "concept": piece.get("concept"), **res, **summary}


def act_take_test(student, resource: dict, ctx: dict) -> dict:
    """Ucenik radi test (resource = izlaz test_generator-a) koristeci samo svoju memoriju."""
    questions = (resource or {}).get("questions", [])
    result = student.take_test(questions)
    emit("student_answered", student=student.id, answers=result.get("answers", []),
         plan=result.get("answer_plan"), phase=ctx["phase"])
    return result


ACTIONS = {"learn": act_learn, "take_test": act_take_test}


# ----------------------------------------------------------------------
#  UPIS U GRAF ZNANJA (isto kao write_graph kod agenata)
# ----------------------------------------------------------------------
def graph_learn(result: dict, g, registry):
    """:Ucenik_student_beginner a :Ucenik ; :profil "beginner" ."""
    for sid in result["participants"]:
        level = registry.students[sid].params.get("level", sid)
        u = g.node("Ucenik", f"Ucenik_{sid}", label=registry.students[sid].name)
        g.value(u, "profil", level)


def graph_take_test(result: dict, g, registry):
    """:Odgovor_student_beginner_T1 a :Odgovor ; :odUcenika :Ucenik_student_beginner ; :naPitanje :Pitanje_T1 ."""
    for sid, out in result["participants"].items():
        for a in (out or {}).get("answers", []):
            o = g.node("Odgovor", f"Odgovor_{sid}_{a.get('question_id')}")
            g.link(o, "odUcenika", g.ref(f"Ucenik_{sid}"))
            g.link(o, "naPitanje", g.ref(f"Pitanje_{a.get('question_id')}"))
            g.value(o, "tekst", a.get("answer"))


GRAPH_WRITERS = {"learn": graph_learn, "take_test": graph_take_test}


# ----------------------------------------------------------------------
def load_student(registry, sid: str, state: dict, iteration: int):
    """Napravi objekat ucenika i vrati mu memoriju iz stanja (ili mu da pocetnu memoriju)."""
    spec = registry.students[sid]
    course = state.get("course", {})
    profile = (course.get("student_profiles") or {}).get(spec.params.get("level"), {})
    if isinstance(profile, str):
        profile = {"description": profile}
    params = {**profile, **spec.params}           # config agenata moze da pregazi profil iz kursa

    memory = (state.get("students") or {}).get(sid)
    if memory is not None and memory.get("iteration") != iteration:
        memory = None   # nova dorada (povratna sprega) = nova generacija ucenika, krecu od nule
    student = spec.klass(sid, params, course, memory)
    student.memory.setdefault("iteration", iteration)
    return student


def make_activity_node(spec, registry, phase_name: str, kg=None):
    """Pravi LangGraph cvor za AKTIVNOST."""
    action = ACTIONS.get(spec.action)
    if action is None:
        raise ValueError(f"Aktivnost '{spec.id}': nepoznata akcija '{spec.action}' (postoje: {list(ACTIONS)})")

    def node(state: dict) -> dict:
        iteration = state.get("iteration", 0)
        rnd = (state.get("rounds") or {}).get(spec.phase, 0)
        log_key = f"iter{iteration}|{spec.phase}|{spec.step}|{spec.id}|r{rnd}"
        base_log = {"agent": spec.id, "kind": "activity", "phase": phase_name, "step": spec.step,
                    "iteration": iteration, "round": rnd}

        if state.get("abort"):
            say(f"   - preskacem {spec.id:<28} (rad je prekinut zbog ranije greske)")
            return {"log": {log_key: {**base_log, "status": "skipped", "error": None, "duration_s": 0}}}

        resource = (state.get("results") or {}).get(spec.resource) if spec.resource else None
        say(f"   * aktivnost {spec.id:<27} ({spec.action}: {', '.join(spec.participants)})")
        emit("activity_start", activity=spec.id, name=spec.name, action=spec.action, phase=spec.phase,
             participants=spec.participants, resource=spec.resource, iteration=iteration, round=rnd)
        start = time.perf_counter()
        ctx = {"phase": spec.phase, "round": rnd, "iteration": iteration}
        try:
            students = {sid: load_student(registry, sid, state, iteration) for sid in spec.participants}
            # ucenici rade paralelno (npr. svi istovremeno pisu test)
            with ThreadPoolExecutor(max_workers=len(students) or 1) as pool:
                futures = {sid: pool.submit(action, st, resource, ctx) for sid, st in students.items()}
                outputs = {sid: f.result() for sid, f in futures.items()}
            output = {"activity": spec.id, "action": spec.action, "resource": spec.resource,
                      "participants": outputs, "iteration": iteration, "round": rnd}
            memories = {sid: st.to_dict() for sid, st in students.items()}

            graph_report = None
            if kg is not None and spec.action in GRAPH_WRITERS:
                g = kg.writer(spec.id, iteration)
                GRAPH_WRITERS[spec.action](output, g, registry)
                graph_report = kg.commit(spec.id, g)
            status, error = "ok", None
        except Exception as e:
            output, memories, graph_report = {"error": str(e)}, {}, None
            status, error = "error", str(e)

        duration = round(time.perf_counter() - start, 3)
        say(f"   < {'OK ' if status == 'ok' else 'GRESKA':<6}    {spec.id:<28} {duration}s"
            + (f"  -> {error}" if error else ""))
        emit("activity_end", activity=spec.id, phase=spec.phase, status=status, error=error,
             duration_s=duration, output=output, round=rnd, iteration=iteration)

        update = {
            "results": {spec.id: output},
            "students": memories,
            "log": {log_key: {**base_log, "status": status, "error": error, "duration_s": duration,
                              "finished_at": datetime.now().isoformat(timespec="seconds"),
                              "graph": graph_report}},
        }
        if status == "error" and state.get("settings", {}).get("stop_on_error", True):
            say(f"   !!! PREKIDAM rad zbog greske u aktivnosti '{spec.id}' (stop_on_error: true)")
            update["abort"] = {spec.id: error}
        return update

    return node
