# src/streamlit_app.py

from __future__ import annotations

import os

import streamlit as st

from dialog_manager import agente_citas
from domain import ConversationState, FlowStep
from llm_client import LLMClient, OPENAI_API_URL, OPENAI_MODEL
from logging_utils import log_turno


def get_llm_client() -> LLMClient:
    """Crea el cliente de OpenAI usando la API key del entorno."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        st.error(
            "La variable de entorno OPENAI_API_KEY no está configurada. "
            "Configúrala antes de usar la app."
        )
        st.stop()
    return LLMClient(api_key=api_key, model=OPENAI_MODEL, api_url=OPENAI_API_URL)


def init_state() -> None:
    """Inicializa el estado de Streamlit (conversación, agente, etc.)."""
    if "conversation_state" not in st.session_state:
        st.session_state.conversation_state = ConversationState()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "llm_client" not in st.session_state:
        st.session_state.llm_client = get_llm_client()


def render_sidebar() -> None:
    """Muestra el estado interno del agente (sidebar)."""
    state: ConversationState = st.session_state.conversation_state

    st.sidebar.header("🧠 Estado del agente")
    st.sidebar.write(f"**Session ID:** `{state.session_id}`")
    st.sidebar.write(f"**Turno actual:** {state.turn_counter}")
    st.sidebar.write(f"**Intención:** {state.intent.name if state.intent else 'Ninguna'}")
    st.sidebar.write(f"**Paso del flujo:** {state.step.name}")
    st.sidebar.write(f"**Fallos LLM:** {state.llm_failures}")

    st.sidebar.subheader("📌 Memoria (slots)")
    mem = state.memory
    st.sidebar.write(f"- Nombre: {mem.nombre}")
    st.sidebar.write(f"- Identificación: {mem.identificacion}")
    st.sidebar.write(f"- Especialidad: {mem.especialidad}")
    st.sidebar.write(f"- Fecha: {mem.fecha}")
    st.sidebar.write(f"- Hora: {mem.hora}")
    st.sidebar.write(f"- Medio: {mem.medio}")

    if st.sidebar.button("🔁 Reiniciar conversación"):
        state.reset()
        st.session_state.messages = []
        st.rerun()


def render_chat() -> None:
    """Renderiza el historial de conversación."""
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"**Tú:** {msg['text']}")
        else:
            st.markdown(f"**Bot:** {msg['text']}")


def main() -> None:
    st.set_page_config(page_title="Agente de citas médicas", page_icon="🩺")
    st.title("🩺 Agente de citas médicas con OpenAI")
    st.write(
        "Este agente agenda citas médicas usando un LLM, maneja memoria de conversación "
        "y registra logs para análisis en BI."
    )

    init_state()
    render_sidebar()

    st.subheader("💬 Conversación")
    render_chat()

    user_input = st.text_input("Escribe tu mensaje:", key="chat_input")

    col1, col2 = st.columns([1, 1])
    with col1:
        enviar = st.button("Enviar")
    with col2:
        reset_local = st.button("Limpiar historial")

    if reset_local:
        st.session_state.messages = []
        st.rerun()

    if enviar and user_input.strip():
        state: ConversationState = st.session_state.conversation_state
        llm_client: LLMClient = st.session_state.llm_client

        st.session_state.messages.append({"role": "user", "text": user_input})

        respuesta_bot = agente_citas(user_input, state, llm_client)

        st.session_state.messages.append({"role": "bot", "text": respuesta_bot})

        log_turno(usuario_texto=user_input, bot_texto=respuesta_bot, state=state)

        if state.step == FlowStep.COMPLETADO:
            st.success("✅ Flujo completado. El estado se reiniciará para una nueva cita.")
            state.reset()

        st.rerun()


if __name__ == "__main__":
    main()
