import json
from typing import Dict, Optional

from domain import Intent
from llm_client import LLMClient


def detectar_intencion_llm(mensaje: str, llm: LLMClient) -> Intent:
    """
    Usa reglas simples + LLM para detectar la intencion del usuario.
    Regla prioritaria: si menciona 'cita' o 'agendar', se considera AGENDAR_CITA.
    """
    texto = mensaje.lower()

    if "cita" in texto or "agendar" in texto or "agenda" in texto:
        return Intent.AGENDAR_CITA

    system_prompt = (
        "Eres un clasificador de intenciones. Devuelve un JSON con el campo 'intent' "
        "que sea uno de: ['agendar_cita', 'small_talk', 'desconocida']."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": mensaje},
    ]
    content = llm.chat(messages, response_format={"type": "json_object"})
    if not content:
        return Intent.DESCONOCIDA
    try:
        data = json.loads(content)
        intent_value = data.get("intent", "desconocida")
        for intent in Intent:
            if intent.value == intent_value:
                return intent
    except json.JSONDecodeError:
        return Intent.DESCONOCIDA
    return Intent.DESCONOCIDA


def extraer_entidades_llm(mensaje: str, llm: LLMClient) -> Dict[str, Optional[str]]:
    """
    Usa OpenAI para extraer entidades del mensaje.
    Devuelve un dict con: nombre, identificacion, especialidad, fecha, hora, medio.
    """
    system_prompt = (
        "Eres un extractor de entidades. Dado el mensaje del usuario, devuelve un JSON con los "
        "campos: nombre, identificacion, especialidad, fecha, hora, medio. Usa null cuando no se pueda extraer."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": mensaje},
    ]
    content = llm.chat(messages, response_format={"type": "json_object"})
    if not content:
        return {
            "nombre": None,
            "identificacion": None,
            "especialidad": None,
            "fecha": None,
            "hora": None,
            "medio": None,
        }
    try:
        data = json.loads(content)
        return {
            "nombre": data.get("nombre"),
            "identificacion": data.get("identificacion"),
            "especialidad": data.get("especialidad"),
            "fecha": data.get("fecha"),
            "hora": data.get("hora"),
            "medio": data.get("medio"),
        }
    except json.JSONDecodeError:
        return {
            "nombre": None,
            "identificacion": None,
            "especialidad": None,
            "fecha": None,
            "hora": None,
            "medio": None,
        }
