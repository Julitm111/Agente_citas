from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class Intent(Enum):
    AGENDAR_CITA = "agendar_cita"
    SMALL_TALK = "small_talk"
    DESCONOCIDA = "desconocida"


class FlowStep(Enum):
    INICIO = "inicio"
    PEDIR_NOMBRE = "pedir_nombre"
    PEDIR_IDENTIFICACION = "pedir_identificacion"
    PEDIR_ESPECIALIDAD = "pedir_especialidad"
    PEDIR_FECHA = "pedir_fecha"
    PEDIR_HORA = "pedir_hora"
    PEDIR_MEDIO = "pedir_medio"
    CONFIRMAR = "confirmar"
    COMPLETADO = "completado"


@dataclass
class Memory:
    nombre: Optional[str] = None
    identificacion: Optional[str] = None
    especialidad: Optional[str] = None
    fecha: Optional[str] = None
    hora: Optional[str] = None
    medio: Optional[str] = None

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "nombre": self.nombre,
            "identificacion": self.identificacion,
            "especialidad": self.especialidad,
            "fecha": self.fecha,
            "hora": self.hora,
            "medio": self.medio,
        }


@dataclass
class ConversationState:
    intent: Optional[Intent] = None
    step: FlowStep = FlowStep.INICIO
    memory: Memory = field(default_factory=Memory)
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    turn_counter: int = 0
    llm_failures: int = 0

    def reset(self) -> None:
        self.intent = None
        self.step = FlowStep.INICIO
        self.memory = Memory()
        self.session_id = str(uuid.uuid4())
        self.turn_counter = 0
        self.llm_failures = 0

    def next_turn(self) -> int:
        """Incrementa y devuelve el número de turno de la conversación."""
        self.turn_counter += 1
        return self.turn_counter


REQUIRED_SLOTS_BY_INTENT: Dict[Intent, List[str]] = {
    Intent.AGENDAR_CITA: ["nombre", "identificacion", "especialidad", "fecha"],
}


def get_missing_slots(state: ConversationState) -> List[str]:
    """Devuelve la lista de slots obligatorios faltantes para la intencion actual."""
    if state.intent is None:
        return []
    required_slots = REQUIRED_SLOTS_BY_INTENT.get(state.intent, [])
    memory_dict = state.memory.to_dict()
    return [slot for slot in required_slots if not memory_dict.get(slot)]
