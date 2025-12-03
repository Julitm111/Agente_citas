import os

from dialog_manager import agente_citas
from domain import ConversationState, FlowStep
from llm_client import LLMClient, OPENAI_API_URL, OPENAI_MODEL
from logging_utils import log_turno


def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("La variable de entorno OPENAI_API_KEY es requerida.")

    llm_client = LLMClient(
        api_key=api_key,
        model=OPENAI_MODEL,
        api_url=OPENAI_API_URL,
    )
    state = ConversationState()

    print("Agente de citas medicas iniciado. Escribe 'salir' para terminar.")
    while True:
        try:
            mensaje_usuario = input("Tu: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nCerrando conversacion.")
            break

        if mensaje_usuario.lower() in {"salir", "exit"}:
            print("Hasta luego.")
            break

        respuesta_bot = agente_citas(mensaje_usuario, state, llm_client)
        print(f"Bot: {respuesta_bot}")
        log_turno(mensaje_usuario, respuesta_bot, state)

        if state.step == FlowStep.COMPLETADO:
            state.reset()


if __name__ == "__main__":
    main()
