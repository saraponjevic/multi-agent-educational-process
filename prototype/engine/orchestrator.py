"""
ORKESTRATOR - automatski pravi LangGraph graf iz registra.

  Glavni graf:   faza1 -> faza2 -> faza3 -> faza4 -> povratna_sprega
                                     ^                      |
                                     |___ (ako treba dorada)|

  Svaka faza je PODGRAF i ima svoj TOK (sekvencioniranje unutar faze):
     - korak 1 -> korak 2 -> korak 3 ...        (redom, po broju 'step')
     - isti 'step' = paralelno
     - PETLJA (opciono, 'loop' kod faze u config/agents.yaml):
           korak 3 -> korak 4 -> provera --(nije gotovo)--> korak 3
                                         --(gotovo)-------> korak 5
       Primer: nastavnik preda deo lekcije -> ucenici ga usvajaju -> sledeci deo ...

  Cvor u fazi moze biti AGENT ili AKTIVNOST (vidi engine/activities.py).
"""
from langgraph.graph import END, START, StateGraph

from engine.activities import make_activity_node
from engine.events import emit
from engine.invoker import make_agent_node, say
from engine.registry import AgentRegistry
from engine.state import EducationState


def _make_node(registry, spec, phase_name, kg):
    if spec.kind == "activity":
        return make_activity_node(spec, registry, phase_name, kg)
    return make_agent_node(spec, phase_name, kg)


def _source(ids: list):
    """LangGraph: jedan cvor -> 'ime', vise cvorova -> lista (ceka SVE njih)."""
    return ids if len(ids) > 1 else ids[0]


def _check_until(state: dict, until: str) -> bool:
    """'teacher.done' -> results['teacher']['done'] je True?"""
    node_id, _, field = until.partition(".")
    return bool(((state.get("results") or {}).get(node_id) or {}).get(field))


# ----------------------------------------------------------------------
#  PODGRAF za jednu fazu
# ----------------------------------------------------------------------
def build_phase_graph(registry: AgentRegistry, phase_id: str, kg=None):
    phase = registry.phase(phase_id)
    phase_name = phase.name
    builder = StateGraph(EducationState)

    # Ulazni čvor faze: javlja gde smo i resetuje brojac krugova petlje
    start_node = f"{phase_id}__start"

    def announce(state: dict) -> dict:
        it = state.get("iteration", 0)
        print(f"\n==== {phase_name}  (prolaz {it + 1}) ====")
        emit("phase_start", phase=phase_id, name=phase_name, iteration=it)
        return {"current_phase": phase_id, "rounds": {phase_id: 0, f"{phase_id}__gotovo": False}}

    builder.add_node(start_node, announce)
    builder.add_edge(START, start_node)

    steps = registry.steps_in_phase(phase_id)
    for step in steps:
        for spec in step:
            builder.add_node(spec.id, _make_node(registry, spec, phase_name, kg))

    loop = phase.loop or {}
    max_rounds = int(loop.get("max_rounds", 30))
    step_ids = [[s.id for s in step] for step in steps]
    step_nums = [step[0].step for step in steps]
    done_key = f"{phase_id}__gotovo"

    previous = [start_node]
    reached_by_loop = False          # korak posle petlje dobija ulaz iz petlje, ne obicnu ivicu
    for i, (ids, num) in enumerate(zip(step_ids, step_nums)):
        if not reached_by_loop:
            for node_id in ids:
                builder.add_edge(_source(previous), node_id)
        reached_by_loop = False
        previous = ids

        if not (loop and num == loop["to_step"]):
            continue

        # ---------- PETLJA: posle koraka 'to_step' odluci da li se ponavlja ----------
        loop_node = f"{phase_id}__petlja"
        first_ids = step_ids[step_nums.index(loop["from_step"])]
        next_ids = step_ids[i + 1] if i + 1 < len(steps) else [END]
        until = loop["until"]

        def loop_check(state: dict, _until=until) -> dict:
            rnd = (state.get("rounds") or {}).get(phase_id, 0)
            done = bool(_check_until(state, _until) or state.get("abort"))
            if not done and rnd + 1 >= max_rounds:
                say(f"   [!] petlja: dostignut max_rounds={max_rounds} - nastavljam dalje")
                done = True
            emit("loop_round", phase=phase_id, round=rnd, done=done)
            if done:
                return {"rounds": {done_key: True}}
            say(f"   ... petlja: krug {rnd + 2}")
            return {"rounds": {phase_id: rnd + 1, done_key: False}}

        def route(state: dict, _first=first_ids, _next=next_ids):
            return _next if (state.get("rounds") or {}).get(done_key) else _first

        builder.add_node(loop_node, loop_check)
        builder.add_edge(_source(ids), loop_node)
        builder.add_conditional_edges(loop_node, route, list(dict.fromkeys(first_ids + next_ids)))
        if next_ids == [END]:
            return builder.compile()
        reached_by_loop = True

    builder.add_edge(_source(previous), END)
    return builder.compile()


# ----------------------------------------------------------------------
#  GLAVNI GRAF
# ----------------------------------------------------------------------
def build_main_graph(registry: AgentRegistry, kg=None):
    """kg = graf znanja (engine/knowledge_graph.py) koji dele svi agenti; moze i None."""
    builder = StateGraph(EducationState)
    phase_ids = [p.id for p in registry.phases]

    # 1) svaka faza je jedan čvor (podgraf), faze idu SEKVENCIJALNO
    for pid in phase_ids:
        builder.add_node(pid, build_phase_graph(registry, pid, kg))

    builder.add_edge(START, phase_ids[0])
    for a, b in zip(phase_ids, phase_ids[1:]):
        builder.add_edge(a, b)

    # 2) povratna sprega posle poslednje faze
    max_iter = registry.settings.get("max_feedback_iterations", 2)

    def feedback_control(state: dict) -> dict:
        if state.get("abort"):
            print("\n!!! Rad je prekinut zbog greske - nema povratne sprege.")
            emit("feedback", rework=False, reason="prekid zbog greske")
            return {"current_phase": "done"}
        decision = state.get("results", {}).get("feedback_manager") or {}
        it = state.get("iteration", 0)
        if decision.get("needs_rework") and it < max_iter:
            target = decision.get("return_to")
            print(f"\n<<< POVRATNA SPREGA: vracam se na fazu '{target}' "
                  f"(dorada {it + 1}/{max_iter})")
            emit("feedback", rework=True, return_to=target, iteration=it + 1, reason=decision.get("reason"))
            return {"iteration": it + 1}
        if decision.get("needs_rework"):
            print(f"\n[!] Dostignut maksimalan broj dorada ({max_iter}) - zavrsavam.")
        else:
            print("\n>>> Evaluacija zadovoljena - zavrsavam.")
        emit("feedback", rework=False, reason=decision.get("reason"))
        return {"current_phase": "done"}

    def route_after_feedback(state: dict) -> str:
        if state.get("current_phase") == "done":
            return END
        target = (state.get("results", {}).get("feedback_manager") or {}).get("return_to")
        return target if target in phase_ids else END

    builder.add_node("feedback_control", feedback_control)
    builder.add_edge(phase_ids[-1], "feedback_control")
    builder.add_conditional_edges(
        "feedback_control", route_after_feedback, {**{p: p for p in phase_ids}, END: END}
    )

    return builder.compile()
