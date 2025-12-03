import datetime
import json
from typing import Optional

from domain import ConversationState


def log_turno(
    usuario_texto: str,
    bot_texto: str,
    state: ConversationState,
    log_path: str = "logs.jsonl",
) -> None:
    """Persistencia JSONL de cada turno con session_id y contador de turno."""
    registro = {
        "session_id": state.session_id,
        "turno": state.next_turn(),
        "usuario_texto": usuario_texto,
        "bot_texto": bot_texto,
        "memoria": state.memory.to_dict(),
        "intencion": state.intent.value if state.intent else None,
        "paso": state.step.name,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")
