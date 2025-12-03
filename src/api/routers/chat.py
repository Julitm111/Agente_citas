# src/api/routers/chat.py

from __future__ import annotations

from typing import Dict, Optional

from fastapi import APIRouter, HTTPException

from src.controllers.dialog_manager import agente_citas
from src.controllers.llm_client import LLMClient, OPENAI_API_URL, OPENAI_MODEL
from src.controllers.logging_utils import log_turno
from src.models.domain import ConversationState, FlowStep
from src.api.db import registrar_cita
from src.api.schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["default"])

# Almacena estados de conversación en memoria: session_id -> ConversationState
SESSION_STORE: Dict[str, ConversationState] = {}

# Cliente LLM singleton (se crea una sola vez)
_LLM_CLIENT: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Devuelve un cliente LLM único para toda la API."""
    global _LLM_CLIENT
    if _LLM_CLIENT is None:
        import os

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY no está configurada en el entorno.")
        _LLM_CLIENT = LLMClient(api_key=api_key, model=OPENAI_MODEL, api_url=OPENAI_API_URL)
    return _LLM_CLIENT


@router.get("/health")
def health() -> dict:
    """Ping sencillo para saber si la API está viva."""
    return {"status": "ok"}


@router.post("/reset")
def reset_session(session_id: Optional[str] = None) -> dict:
    """
    Resetea una sesión específica o todas si no se envía session_id.
    Útil para pruebas.
    """
    global SESSION_STORE
    if session_id:
        SESSION_STORE.pop(session_id, None)
    else:
        SESSION_STORE = {}
    return {"status": "reset", "session_id": session_id}


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    """
    Endpoint principal de chat.
    - Recibe session_id (opcional) y message.
    - Mantiene el estado de la conversación en SESSION_STORE.
    - Llama al dialog_manager (agente_citas).
    - Registra logs.
    - Si el flujo se completa, guarda la cita en SQLite.
    """
    try:
        # 1. Recuperar o crear estado de conversación
        if payload.session_id and payload.session_id in SESSION_STORE:
            state = SESSION_STORE[payload.session_id]
        else:
            state = ConversationState()
            SESSION_STORE[state.session_id] = state

        llm_client = get_llm_client()

        # 2. Ejecutar turno del agente
        respuesta_bot = agente_citas(payload.message, state, llm_client)

        # 3. Log de turno
        log_turno(
            usuario_texto=payload.message,
            bot_texto=respuesta_bot,
            state=state,
        )

        # 4. ¿El flujo llegó a COMPLETADO?
        completed = state.step == FlowStep.COMPLETADO

        if completed:
            # Registrar cita en la BD
            registrar_cita(
                session_id=state.session_id,
                nombre=state.memory.nombre or "",
                identificacion=state.memory.identificacion or "",
                especialidad=state.memory.especialidad or "",
                fecha=state.memory.fecha or "",
                hora=state.memory.hora,
                medio=state.memory.medio,
            )
            # IMPORTANTE: NO resetear state.session_id, solo vaciar memoria de slots
            state.reset()

        # 5. Construir respuesta que cumpla exactamente con ChatResponse
        memory_dict = state.memory.to_dict()
        return ChatResponse(
            session_id=state.session_id,
            reply=respuesta_bot,
            completed=completed,
            memory=memory_dict,
        )

    except RuntimeError as e:
        # Errores de configuración (por ejemplo OPENAI_API_KEY)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Cualquier otro error inesperado
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {e}")
