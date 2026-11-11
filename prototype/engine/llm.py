"""
LLM SLOJ - jedno mesto preko kog SVI agenti pricaju sa jezickim modelom.

Radi u dva rezima (podesava se u fajlu .env):
  LLM_ENABLED=false -> "mock" rezim: agenti vracaju unapred zadate (hello world) podatke.
                       Ne treba internet ni API kljuc. Dobro za testiranje toka.
  LLM_ENABLED=true  -> pravi pozivi ka modelu preko OpenAI-kompatibilnog API-ja
                       (Gemini, Groq, OpenAI, lokalni Ollama... samo promenis adresu i model).

Agent koristi samo jednu funkciju:
    ask_json(system, user, fallback)  -> dict
"""
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_env_file():
    """Ucitava .env fajl (KLJUC=vrednost) u os.environ, bez dodatnih biblioteka."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.split(" #")[0]          # ukloni komentar sa kraja reda
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file()

ENABLED = os.getenv("LLM_ENABLED", "false").lower() == "true"
BASE_URL = os.getenv("LLM_BASE_URL", "").rstrip("/")
API_KEY = os.getenv("LLM_API_KEY", "")
MODEL = os.getenv("LLM_MODEL", "")
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "2"))
TIMEOUT = int(os.getenv("LLM_TIMEOUT", "300"))                  # sekundi cekanja na odgovor
REASONING_EFFORT = os.getenv("LLM_REASONING_EFFORT", "").strip()  # npr. "low" = manje "razmisljanja", brzi odgovor

# Besplatni nalozi imaju ogranicenje broja zahteva u minuti,
# pa ne saljemo previse zahteva istovremeno.
_parallel_limit = threading.Semaphore(int(os.getenv("LLM_MAX_PARALLEL", "2")))


def describe() -> str:
    if not ENABLED:
        return "LLM: ISKLJUCEN (mock rezim - agenti vracaju hello world podatke)"
    return f"LLM: UKLJUCEN  model={MODEL}  adresa={BASE_URL}"


def _extract_json(text: str) -> dict:
    """Model ponekad doda ```json ... ``` ili tekst oko JSON-a - ovo to cisti."""
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"Model nije vratio JSON. Odgovor: {text[:200]}")
    return json.loads(text[start:end + 1])


def _chat(messages: list) -> str:
    payload = {"model": MODEL, "messages": messages, "temperature": TEMPERATURE}
    if REASONING_EFFORT:
        payload["reasoning_effort"] = REASONING_EFFORT
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
            "User-Agent": "sotis-multiagent/1.0",
        },
        method="POST",
    )
    for attempt in range(MAX_RETRIES + 1):
        try:
            with _parallel_limit, urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            details = e.read().decode("utf-8", errors="ignore")[:300]
            if "quota" in details.lower() and "perday" in details.lower().replace(" ", "").replace("_", ""):
                raise RuntimeError("LLM: potrosena DNEVNA kvota besplatnog naloga - probaj sutra ili promeni servis/model")
            if e.code in (429, 500, 502, 503) and attempt < MAX_RETRIES:
                wait = 10 * (attempt + 1)      # 10s, 20s, 30s...
                print(f"      (LLM: greska {e.code}, cekam {wait}s pa pokusavam ponovo)", flush=True)
                time.sleep(wait)
                continue
            raise RuntimeError(f"LLM HTTP greska {e.code}: {details}")


def test_connection():
    """Jedan mali probni poziv - provera kljuca, modela i brzine (python main.py --test-llm)."""
    print(describe())
    if not ENABLED:
        print("LLM je iskljucen (LLM_ENABLED=false u .env) - nema sta da se testira.")
        return
    start = time.perf_counter()
    try:
        answer = _chat([{"role": "user", "content": "Odgovori samo jednom recju: zdravo"}])
        print(f"OK - model je odgovorio za {time.perf_counter() - start:.1f}s: {answer.strip()[:100]}")
    except Exception as e:
        print(f"GRESKA posle {time.perf_counter() - start:.1f}s: {e}")


def ask_json(system: str, user: str, fallback: dict) -> dict:
    """
    Posalje pitanje modelu i vrati odgovor kao Python dict.
    U mock rezimu odmah vraca `fallback` (hello world podatke).
    """
    if not ENABLED:
        return {**fallback, "_source": "mock"}
    if not (BASE_URL and API_KEY and MODEL):
        raise RuntimeError("LLM je ukljucen, ali u .env fali LLM_BASE_URL, LLM_API_KEY ili LLM_MODEL")

    messages = [
        {"role": "system", "content": system + "\n\nOdgovori ISKLJUCIVO validnim JSON objektom, bez dodatnog teksta."},
        {"role": "user", "content": user},
    ]
    text = _chat(messages)
    try:
        result = _extract_json(text)
    except Exception:
        # jedan pokusaj popravke: zamolimo model da vrati samo JSON
        messages += [{"role": "assistant", "content": text},
                     {"role": "user", "content": "To nije bio validan JSON. Vrati ISKLJUCIVO JSON objekat."}]
        result = _extract_json(_chat(messages))
    return {**result, "_source": f"llm:{MODEL}"}


def to_text(obj) -> str:
    """Pomocna: pretvara podatke u citljiv JSON tekst za ubacivanje u prompt."""
    return json.dumps(obj, ensure_ascii=False, indent=2)
