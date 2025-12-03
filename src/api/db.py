import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "appointments.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            identificacion TEXT,
            especialidad TEXT,
            fecha TEXT,
            hora TEXT,
            medio TEXT,
            session_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            identificacion TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def registrar_cita(
    nombre: Optional[str],
    identificacion: Optional[str],
    especialidad: Optional[str],
    fecha: Optional[str],
    hora: Optional[str],
    medio: Optional[str],
    session_id: Optional[str] = None,
) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO appointments (nombre, identificacion, especialidad, fecha, hora, medio, session_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (nombre, identificacion, especialidad, fecha, hora, medio, session_id),
    )
    conn.commit()
    conn.close()


# Inicializa la base al importar
init_db()
