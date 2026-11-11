"""
AGENT REGISTRY - katalog agenata.

Čita config/agents.yaml, proverava da li je sve ispravno i pamti
sve agente: ko je, u kojoj je fazi, u kom koraku i kako se poziva.
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
    function: str | None = None          # npr. "agents.phase1_curriculum:needs_analysis"
    endpoint: str | None = None          # za eksterne agente
    timeout_seconds: float = 30
    capabilities: list = field(default_factory=list)
    requires: list = field(default_factory=list)
    params: dict = field(default_factory=dict)
    enabled: bool = True
    callable: object = None              # učitana Python funkcija (popunjava se automatski)


@dataclass
class PhaseSpec:
    id: str
    name: str


class AgentRegistry:
    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path)
        self.settings: dict = {}
        self.phases: list[PhaseSpec] = []
        self.agents: dict[str, AgentSpec] = {}
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
                spec.callable = self._import_function(spec)
            elif spec.type == "remote_http":
                if not spec.endpoint:
                    raise ValueError(f"Eksterni agent '{spec.id}' nema 'endpoint'.")
            else:
                raise ValueError(f"Agent '{spec.id}' ima nepoznat type '{spec.type}'")

            self.agents[spec.id] = spec

        # Upozori ako agent zavisi od nekog ko ne postoji / nije uključen
        for a in self.agents.values():
            for dep in a.requires:
                if dep not in self.agents:
                    self.warnings.append(
                        f"Agent '{a.id}' ocekuje rezultat od '{dep}', ali taj agent nije registrovan/ukljucen."
                    )

    @staticmethod
    def _import_function(spec: AgentSpec):
        """'agents.phase1_curriculum:needs_analysis' -> prava Python funkcija."""
        try:
            module_name, func_name = spec.function.split(":")
            module = importlib.import_module(module_name)
            return getattr(module, func_name)
        except Exception as e:
            raise ImportError(f"Ne mogu da ucitam funkciju za agenta '{spec.id}' ({spec.function}): {e}")

    # ------------------------------------------------------------------
    #  Pomoćne funkcije koje koristi orkestrator
    # ------------------------------------------------------------------
    def agents_in_phase(self, phase_id: str) -> list[AgentSpec]:
        return [a for a in self.agents.values() if a.phase == phase_id]

    def steps_in_phase(self, phase_id: str) -> list[list[AgentSpec]]:
        """Vraća listu koraka; svaki korak je lista agenata koji rade paralelno."""
        agents = self.agents_in_phase(phase_id)
        step_numbers = sorted({a.step for a in agents})
        return [[a for a in agents if a.step == s] for s in step_numbers]

    def find_by_capability(self, capability: str) -> list[AgentSpec]:
        """Pronalaženje agenta na osnovu sposobnosti (npr. 'generate_lesson')."""
        return [a for a in self.agents.values() if capability in a.capabilities]

    def phase_name(self, phase_id: str) -> str:
        return next(p.name for p in self.phases if p.id == phase_id)

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
                    where = a.function if a.type == "local" else a.endpoint
                    print(f"      - {a.id:<28} [{a.type}]  {where}")
        for w in self.warnings:
            print(f"\n[UPOZORENJE] {w}")
        print("=====================================================\n")
