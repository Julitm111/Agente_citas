# src/api/schemas.py
from typing import Optional, Dict
from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Lo que recibe la API cuando el cliente habla con el bot."""
    session_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    """Lo que devuelve la API al cliente."""
    session_id: str        # id de la conversación (para seguir el mismo contexto)
    reply: str             # texto del bot
    completed: bool        # True si el flujo de la cita terminó
    memory: Dict[str, Optional[str]]  # estado de los slots (nombre, fecha, etc.)


class AppointmentRecord(BaseModel):
    """Estructura de una cita registrada en la BD (para documentación)."""
    session_id: str
    nombre: str
    identificacion: str
    especialidad: str
    fecha: str
    hora: Optional[str] = None
    medio: Optional[str] = None
