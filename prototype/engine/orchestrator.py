"""
ORKESTRATOR - automatski pravi LangGraph graf iz registra.

  Glavni graf:   faza1 -> faza2 -> faza3 -> faza4 -> povratna_sprega
                                     ^                      |
                                     |___ (ako treba dorada)|

  Svaka faza je PODGRAF:  korak1 (paralelno) -> korak2 -> korak3 ...
"""
from langgraph.graph import END, START, StateGraph

from engine.invoker import make_agent_node
from engine.registry import AgentRegistry
from engine.state import EducationState


# ----------------------------------------------------------------------
#  PODGRAF za jednu fazu
# ----------------------------------------------------------------------
def build_phase_graph(registry: AgentRegistry, phase_id: str, kg=None):
    phase_name = registry.phase_name(phase_id)
    builder = StateGraph(EducationState)

    # Ulazni čvor faze: samo javlja gde smo
    start_node = f"{phase_id}__start"

    def announce(state: dict) -> dict:
        it = state.get("iteration", 0)
        print(f"\n==== {phase_name}  (prolaz {it + 1}) ====")
        return {"current_phase": phase_id}

    builder.add_node(start_node, announce)
    builder.add_edge(START, start_node)

    previous = [start_node]
    for step in registry.steps_in_phase(phase_id):
        for agent in step:
            builder.add_node(agent.id, make_agent_node(agent, phase_name, kg))
            # svaki agent iz ovog koraka čeka SVE agente iz prethodnog koraka
            builder.add_edge(previous if len(previous) > 1 else previous[0], agent.id)
        previous = [a.id for a in step]

    builder.add_edge(previous if len(previous) > 1 else previous[0], END)
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
            return {"current_phase": "done"}
        decision = state.get("results", {}).get("feedback_manager") or {}
        it = state.get("iteration", 0)
        if decision.get("needs_rework") and it < max_iter:
            target = decision.get("return_to")
            print(f"\n<<< POVRATNA SPREGA: vracam se na fazu '{target}' "
                  f"(dorada {it + 1}/{max_iter})")
            return {"iteration": it + 1}
        if decision.get("needs_rework"):
            print(f"\n[!] Dostignut maksimalan broj dorada ({max_iter}) - zavrsavam.")
        else:
            print("\n>>> Evaluacija zadovoljena - zavrsavam.")
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
