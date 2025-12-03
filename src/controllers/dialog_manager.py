from typing import Dict, Optional

from src.models.domain import ConversationState, FlowStep, Intent, get_missing_slots
from src.controllers.llm_client import LLMClient
from src.controllers.nlu import detectar_intencion_llm, extraer_entidades_llm

FALLBACK_MESSAGE = (
    "Estoy teniendo problemas para procesar tu solicitud en este momento. "
    "Puedes reformular tu mensaje o intentarlo de nuevo mas tarde?"
)


def next_bot_action(state: ConversationState) -> str:
    """Determina el siguiente mensaje del bot basado en el flujo y slots faltantes."""
    if state.intent != Intent.AGENDAR_CITA:
        state.step = FlowStep.COMPLETADO
        return "Por ahora solo puedo ayudarte a agendar citas medicas."

    missing_slots = get_missing_slots(state)

    if "nombre" in missing_slots:
        state.step = FlowStep.PEDIR_NOMBRE
        return "Para comenzar, cual es tu nombre completo?"

    if "identificacion" in missing_slots:
        state.step = FlowStep.PEDIR_IDENTIFICACION
        return "Podrias indicarme tu numero de identificacion?"

    if "especialidad" in missing_slots:
        state.step = FlowStep.PEDIR_ESPECIALIDAD
        return (
            "Con que especialidad necesitas tu cita? "
            "(por ejemplo: pediatria, cardiologia, dermatologia)"
        )

    if "fecha" in missing_slots:
        state.step = FlowStep.PEDIR_FECHA
        return "Para que fecha deseas agendar la cita?"

    if not state.memory.hora:
        state.step = FlowStep.PEDIR_HORA
        return "Tienes alguna hora preferida para la cita?"

    if not state.memory.medio:
        state.step = FlowStep.PEDIR_MEDIO
        return "Prefieres que la cita sea presencial o virtual?"

    state.step = FlowStep.CONFIRMAR
    resumen = (
        f"Nombre: {state.memory.nombre}\n"
        f"Identificacion: {state.memory.identificacion}\n"
        f"Especialidad: {state.memory.especialidad}\n"
        f"Fecha: {state.memory.fecha}\n"
        f"Hora: {state.memory.hora or 'No especificada'}\n"
        f"Medio: {state.memory.medio or 'No especificado'}"
    )
    return (
        "Perfecto, con estos datos puedo agendar tu cita. Por favor confirma:\n"
        f"{resumen}\n"
        "Confirmas que son correctos? (si/no)"
    )


def agente_citas(
    mensaje_usuario: str, state: ConversationState, llm: LLMClient
) -> str:
    """Gestiona el ciclo conversacional, NLU y respuestas con manejo de fallback."""
    mensaje_usuario_lower = mensaje_usuario.strip().lower()

    if state.intent == Intent.SMALL_TALK:
        afirmativos = ["si", "claro", "obvio", "dale", "por supuesto", "ok", "vale"]
        if any(pal in mensaje_usuario_lower for pal in afirmativos):
            state.intent = Intent.AGENDAR_CITA
        else:
            return "Soy un asistente para agendar citas medicas, deseas programar una?"

    if state.intent == Intent.AGENDAR_CITA:
        if state.step == FlowStep.PEDIR_HORA and not state.memory.hora:
            state.memory.hora = mensaje_usuario.strip()
        elif state.step == FlowStep.PEDIR_MEDIO and not state.memory.medio:
            medio = mensaje_usuario_lower
            if "presencial" in medio:
                state.memory.medio = "presencial"
            elif "virtual" in medio or "online" in medio:
                state.memory.medio = "virtual"
            else:
                state.memory.medio = mensaje_usuario.strip()

    if state.intent is None or state.intent == Intent.DESCONOCIDA:
        intent_detectada = detectar_intencion_llm(mensaje_usuario, llm)
        state.intent = intent_detectada
        if intent_detectada == Intent.DESCONOCIDA:
            state.llm_failures += 1
        else:
            state.llm_failures = 0

    if state.intent == Intent.AGENDAR_CITA:
        entidades: Dict[str, Optional[str]] = extraer_entidades_llm(mensaje_usuario, llm)
        for key, value in entidades.items():
            if value and getattr(state.memory, key) in (None, ""):
                setattr(state.memory, key, value)
        state.llm_failures = 0

    if state.step == FlowStep.CONFIRMAR and "si" in mensaje_usuario_lower:
        respuesta = "Tu cita ha sido registrada."
        state.step = FlowStep.COMPLETADO
        state.intent = Intent.AGENDAR_CITA
        return respuesta

    if state.intent == Intent.DESCONOCIDA:
        if state.llm_failures >= 2:
            return FALLBACK_MESSAGE
        return (
            "No estoy seguro de como ayudarte con eso. "
            "Puedo agendar citas medicas si lo necesitas."
        )

    if state.llm_failures >= 2:
        return FALLBACK_MESSAGE

    return next_bot_action(state)
