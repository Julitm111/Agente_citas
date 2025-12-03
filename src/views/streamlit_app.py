# src/views/streamlit_app.py

from __future__ import annotations

import os
import sys

import streamlit as st

# --- Hack para que Python encuentre el paquete `src` cuando se ejecuta con streamlit ---
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# --------------------------------------------------------------------------------------


from src.controllers.dialog_manager import agente_citas
from src.models.domain import ConversationState, FlowStep
from src.controllers.llm_client import LLMClient, OPENAI_API_URL, OPENAI_MODEL
from src.controllers.logging_utils import log_turno


def get_llm_client() -> LLMClient:
    """Crea el cliente de OpenAI usando la API key del entorno."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        st.error(
            "La variable de entorno OPENAI_API_KEY no esta configurada. "
            "Configúrala antes de usar la app."
        )
        st.stop()
    return LLMClient(api_key=api_key, model=OPENAI_MODEL, api_url=OPENAI_API_URL)


def init_state() -> None:
    """Inicializa el estado de Streamlit (conversacion, agente, etc.)."""
    if "conversation_state" not in st.session_state:
        st.session_state.conversation_state = ConversationState()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "llm_client" not in st.session_state:
        st.session_state.llm_client = get_llm_client()


def render_sidebar() -> None:
    """Muestra en el sidebar el estado interno del agente (debugging/entrevista)."""
    state: ConversationState = st.session_state.conversation_state

    st.sidebar.header("🧠 Estado del agente")
    st.sidebar.write(f"**Session ID:** `{state.session_id}`")
    st.sidebar.write(f"**Turno actual:** {state.turn_counter}")
    st.sidebar.write(f"**Intencion:** {state.intent.name if state.intent else 'Ninguna'}")
    st.sidebar.write(f"**Paso del flujo:** {state.step.name}")
    st.sidebar.write(f"**Fallos LLM:** {state.llm_failures}")

    st.sidebar.subheader("📌 Memoria (slots)")
    mem = state.memory
    st.sidebar.write(f"- Nombre: {mem.nombre}")
    st.sidebar.write(f"- Identificacion: {mem.identificacion}")
    st.sidebar.write(f"- Especialidad: {mem.especialidad}")
    st.sidebar.write(f"- Fecha: {mem.fecha}")
    st.sidebar.write(f"- Hora: {mem.hora}")
    st.sidebar.write(f"- Medio: {mem.medio}")

    if st.sidebar.button("🔁 Reiniciar conversacion"):
        state.reset()
        st.session_state.messages = []
        st.rerun()


def render_chat() -> None:
    """Renderiza el historial de conversacion."""
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"**Tu:** {msg['text']}")
        else:
            st.markdown(f"**Bot:** {msg['text']}")


def main() -> None:
    st.set_page_config(page_title="Agente de citas medicas", page_icon="🩺")
    st.title("🩺 Agente de citas medicas con OpenAI")
    st.write(
        "Este agente agenda citas medicas usando un LLM, maneja memoria de conversacion "
        "y registra logs para analisis en BI."
    )

    init_state()
    render_sidebar()

    st.subheader("💬 Conversacion")
    render_chat()

    # No vamos a manipular este valor en session_state para evitar errores
    user_input = st.text_input("Escribe tu mensaje:", key="chat_input")

    col1, col2 = st.columns([1, 1])
    with col1:
        enviar = st.button("Enviar")
    with col2:
        reset_local = st.button("Limpiar historial")

    # Este boton solo limpia el historial (y opcionalmente resetea el estado)
    if reset_local:
        st.session_state.messages = []
        st.session_state.conversation_state.reset()
        st.rerun()

    if enviar and user_input.strip():
        state: ConversationState = st.session_state.conversation_state
        llm_client: LLMClient = st.session_state.llm_client

        # Guardamos mensaje del usuario
        st.session_state.messages.append({"role": "user", "text": user_input})

        # Llamamos al agente
        respuesta_bot = agente_citas(user_input, state, llm_client)

        # Guardamos respuesta del bot
        st.session_state.messages.append({"role": "bot", "text": respuesta_bot})

        # Log en JSONL
        log_turno(usuario_texto=user_input, bot_texto=respuesta_bot, state=state)

        # Si el flujo termina, reseteamos para una nueva cita
        if state.step == FlowStep.COMPLETADO:
            st.success("✅ Flujo completado. El estado se reiniciara para una nueva cita.")
            state.reset()

        # Forzamos rerender para ver inmediatamente la nueva conversacion
        st.rerun()


if __name__ == "__main__":
    main()
