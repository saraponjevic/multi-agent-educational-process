"""Pomocna funkcija za "hello world" agente."""


def hello(data: dict, who: str, **extra) -> dict:
    """Vraca standardan hello world odgovor + spisak od koga je agent dobio ulaz."""
    return {
        "message": f"Zdravo, ja sam {who}.",
        "received_from": list(data.get("inputs", {}).keys()),
        **extra,
    }
