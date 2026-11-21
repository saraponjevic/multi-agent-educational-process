"""
AGENT REGISTRY - katalog agenata.

Čita config/agents.yaml, proverava da li je sve ispravno i pamti:
  - AGENTE      (ko je, u kojoj je fazi, u kom koraku i kako se poziva)
  - UCENIKE     (simulirani ucenici - "genericki interfejs", vidi agents/students/base.py)
  - AKTIVNOSTI  (nisu agenti: nesto sto POSTOJECI ucenici rade nad POSTOJECIM resursom,
                 npr. "polaganje testa" = ucenici + test koji je napravio test_generator)
  - FAZE        (i opciono PETLJU unutar faze, npr. nastavnik <-> ucenici dok se ne preda sve)
"""
import importlib
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class AgentSpec:
    """Jedan zapis iz registra (jedan agent)."""
    id: str
    name: str
    phase: str
    step: int
    type: str = "local"                  # "local" ili "remote_http"
    function: str | None = None          # npr. "agents.phase1_curriculum.needs_analysis:run"
    endpoint: str | None = None          # za eksterne agente
    timeout_seconds: float = 30
    capabilities: list = field(default_factory=list)
    requires: list = field(default_factory=list)       # ulazi koji MORAJU da postoje
    optional: list = field(default_factory=list)       # ulazi koji mogu, ali ne moraju da postoje
    params: dict = field(default_factory=dict)
    enabled: bool = True
    callable: object = None              # učitana Python funkcija (popunjava se automatski)
    kind: str = "agent"                  # da orkestrator zna da je ovo agent


@dataclass
class StudentSpec:
    """Simulirani ucenik. 'cls' je Python klasa koja ispunjava interfejs agents/students/base.py."""
    id: str
    name: str
    cls: str                             # npr. "agents.students.simple_student:SimpleStudent"
    params: dict = field(default_factory=dict)
    enabled: bool = True
    klass: object = None                 # ucitana klasa (popunjava se automatski)


@dataclass
class ActivitySpec:
    """
    AKTIVNOST = cvor u LangGraph grafu koji NIJE novi agent.
    Postojeci ucesnici (ucenici) izvode akciju (action) nad resursom (rezultat nekog agenta).
    """
    id: str
    name: str
    phase: str
    step: int
    action: str                          # "learn" | "take_test"  (vidi engine/activities.py)
    participants: list = field(default_factory=list)   # id-jevi ucenika
    resource: str | None = None          # id agenta ciji izlaz je resurs (npr. test_generator)
    enabled: bool = True
    kind: str = "activity"

    @property
    def requires(self) -> list:          # resurs je ulaz aktivnosti (isto kao requires kod agenta)
        return [self.resource] if self.resource else []


@dataclass
class PhaseSpec:
    id: str
    name: str
    # PETLJA unutar faze (opciono):
    #   loop: {from_step: 3, to_step: 4, until: "teacher.done", max_rounds: 30}
    #   -> koraci 3..4 se ponavljaju dok rezultat agenta 'teacher' nema done = true
    loop: dict | None = None


class AgentRegistry:
    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path)
        self.settings: dict = {}
        self.phases: list[PhaseSpec] = []
        self.agents: dict[str, AgentSpec] = {}
        self.students: dict[str, StudentSpec] = {}
        self.activities: dict[str, ActivitySpec] = {}
        self.warnings: list[str] = []
        self._load()

    # ------------------------------------------------------------------
    def _load(self):
        with open(self.config_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        self.settings = cfg.get("settings", {})
        self.phases = [PhaseSpec(**p) for p in cfg["phases"]]
        phase_ids = [p.id for p in self.phases]

        for raw in cfg.get("agents", []):
            spec = AgentSpec(**raw)

            if not spec.enabled:
                self.warnings.append(f"Agent '{spec.id}' je iskljucen (enabled: false) - preskacem ga.")
                continue
            if spec.id in self.agents:
                raise ValueError(f"Dva agenta imaju isti id: '{spec.id}'")
            if spec.phase not in phase_ids:
                raise ValueError(f"Agent '{spec.id}' ima nepoznatu fazu '{spec.phase}'. Dozvoljene: {phase_ids}")

            if spec.type == "local":
                spec.callable = self._import(spec.id, spec.function, default="run")
            elif spec.type == "remote_http":
                if not spec.endpoint:
                    raise ValueError(f"Eksterni agent '{spec.id}' nema 'endpoint'.")
            else:
                raise ValueError(f"Agent '{spec.id}' ima nepoznat type '{spec.type}'")

            self.agents[spec.id] = spec

        # --- simulirani ucenici ---
        for raw in cfg.get("students", []):
            raw = dict(raw)
            spec = StudentSpec(cls=raw.pop("class"), **raw)
            if not spec.enabled:
                continue
            spec.klass = self._import(spec.id, spec.cls)
            self.students[spec.id] = spec

        # --- aktivnosti ---
        for raw in cfg.get("activities", []):
            spec = ActivitySpec(**raw)
            if not spec.enabled:
                self.warnings.append(f"Aktivnost '{spec.id}' je iskljucena - preskacem je.")
                continue
            if spec.id in self.agents or spec.id in self.activities:
                raise ValueError(f"Aktivnost '{spec.id}' ima id koji vec postoji")
            if spec.phase not in phase_ids:
                raise ValueError(f"Aktivnost '{spec.id}' ima nepoznatu fazu '{spec.phase}'")
            unknown = [p for p in spec.participants if p not in self.students]
            if unknown:
                raise ValueError(f"Aktivnost '{spec.id}': ucesnici {unknown} nisu u listi 'students'")
            self.activities[spec.id] = spec

        # Upozori ako agent zavisi od nekog ko ne postoji / nije uključen
        for a in self.nodes():
            deps = a.requires + (a.optional if a.kind == "agent" else [])
            for dep in deps:
                if dep not in self.agents and dep not in self.activities:
                    self.warnings.append(
                        f"'{a.id}' ocekuje rezultat od '{dep}', ali taj agent/aktivnost nije registrovan/ukljucen."
                    )

        for p in self.phases:
            if p.loop and "." not in str(p.loop.get("until", "")):
                raise ValueError(f"Faza '{p.id}': loop.until mora biti oblika 'agent.polje' (npr. teacher.done)")

    @staticmethod
    def _import(owner: str, path: str, default: str | None = None):
        """'agents.phase1_curriculum.needs_analysis:run' -> prava Python funkcija (ili klasa)."""
        try:
            module_name, _, name = path.partition(":")
            name = name or default
            module = importlib.import_module(module_name)
            return getattr(module, name)
        except Exception as e:
            raise ImportError(f"Ne mogu da ucitam '{path}' za '{owner}': {e}")

    # ------------------------------------------------------------------
    #  Pomoćne funkcije koje koristi orkestrator
    # ------------------------------------------------------------------
    def nodes(self) -> list:
        """Svi cvorovi grafa: agenti + aktivnosti."""
        return list(self.agents.values()) + list(self.activities.values())

    def agents_in_phase(self, phase_id: str) -> list:
        return [a for a in self.nodes() if a.phase == phase_id]

    def steps_in_phase(self, phase_id: str) -> list[list]:
        """Vraća listu koraka; svaki korak je lista agenata/aktivnosti koji rade paralelno."""
        agents = self.agents_in_phase(phase_id)
        step_numbers = sorted({a.step for a in agents})
        return [[a for a in agents if a.step == s] for s in step_numbers]

    def find_by_capability(self, capability: str) -> list[AgentSpec]:
        """Pronalaženje agenta na osnovu sposobnosti (npr. 'generate_lesson')."""
        return [a for a in self.agents.values() if capability in a.capabilities]

    def phase(self, phase_id: str) -> PhaseSpec:
        return next(p for p in self.phases if p.id == phase_id)

    def phase_name(self, phase_id: str) -> str:
        return self.phase(phase_id).name

    def describe(self) -> dict:
        """Opis celog sistema (za vizuelnu platformu): faze, koraci, agenti, aktivnosti, ucenici."""
        return {
            "phases": [{
                "id": p.id, "name": p.name, "loop": p.loop,
                "steps": [[{"id": a.id, "name": a.name, "kind": a.kind, "step": a.step,
                            "participants": getattr(a, "participants", []),
                            "resource": getattr(a, "resource", None)} for a in step]
                          for step in self.steps_in_phase(p.id)],
            } for p in self.phases],
            "students": [{"id": s.id, "name": s.name, "params": s.params} for s in self.students.values()],
        }

    def print_summary(self):
        print("\n================ REGISTROVANI AGENTI ================")
        for phase in self.phases:
            print(f"\n{phase.name}")
            steps = self.steps_in_phase(phase.id)
            if not steps:
                print("   (nema agenata)")
            for step in steps:
                paralel = "  <- paralelno" if len(step) > 1 else ""
                print(f"   korak {step[0].step}:{paralel}")
                for a in step:
                    if a.kind == "activity":
                        print(f"      * {a.id:<28} [AKTIVNOST] {a.action}: {', '.join(a.participants)}"
                              f"  nad '{a.resource}'")
                    else:
                        where = a.function if a.type == "local" else a.endpoint
                        print(f"      - {a.id:<28} [{a.type}]  {where}")
            if phase.loop:
                lp = phase.loop
                print(f"   PETLJA: koraci {lp['from_step']}-{lp['to_step']} se ponavljaju dok ne vazi "
                      f"'{lp['until']}' (najvise {lp.get('max_rounds', 30)} krugova)")
        if self.students:
            print("\nSimulirani ucenici:")
            for s in self.students.values():
                print(f"      o {s.id:<28} {s.cls}  {s.params}")
        for w in self.warnings:
            print(f"\n[UPOZORENJE] {w}")
        print("=====================================================\n")
