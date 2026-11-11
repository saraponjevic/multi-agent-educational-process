# Kako pokrenuti prototip

## Prvi put (instalacija)
```powershell
python -m venv .venv
.venv\Scripts\activate            # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Svaki sledeći put
```powershell
.venv\Scripts\activate
python main.py                    # pokreni ceo nastavni proces
python main.py --list             # samo prikaži registrovane agente
python main.py --graph            # sačuvaj dijagram grafa u docs/graph.md
python main.py --course "Uvod u baze podataka"
```

## Eksterni agent (HTTP)
1. U drugom terminalu: `python external_agent/server.py`
2. U `config/agents.yaml` kod `answer_grader` promeni `type: local` u `type: remote_http`
3. U prvom terminalu: `python main.py`

## Struktura
| Folder / fajl | Šta je to (iz arhitekture) |
|---|---|
| `config/agents.yaml` | Agent Registry – spisak agenata, faza, korak, kako se pozivaju |
| `engine/registry.py` | učitava i proverava registar, traženje po sposobnosti |
| `engine/invoker.py` | Agent Invoker / Adapter – poziva lokalnog ili HTTP agenta, meri vreme, hvata greške |
| `engine/state.py` | zajedničko stanje (State) |
| `engine/orchestrator.py` | glavni orkestrator (LangGraph): faze sekvencijalno, korak paralelno, povratna sprega |
| `agents/` | svih 36 "hello world" agenata po fazama (9 + 9 + 8 + 10) |
| `external_agent/server.py` | primer eksternog agenta preko HTTP API-ja |
| `output/` | evidencija svakog pokretanja (JSON) |

## Pravila redosleda
- Faze idu redom kako su navedene u `phases`.
- Unutar faze agenti idu po broju `step`.
- Isti `step` u istoj fazi = rade **paralelno**.
- Korak N+1 čeka da se završe **svi** agenti iz koraka N.
- Ako `feedback_manager` vrati `needs_rework: true`, tok se vraća na fazu `return_to`
  (najviše `max_feedback_iterations` puta).

## Iskljucivanje agenta
Dodaj `enabled: false` u blok agenta - engine ga preskace, a ostali rade dalje.
