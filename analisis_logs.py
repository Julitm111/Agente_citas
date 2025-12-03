import json
from typing import Any, Dict

import pandas as pd

LOG_PATH = "logs.jsonl"
EXPORT_CSV = "logs_export_powerbi.csv"


def cargar_logs(path: str = LOG_PATH) -> pd.DataFrame:
    registros = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                registros.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return pd.DataFrame(registros)


def calcular_metricas(df: pd.DataFrame) -> None:
    if df.empty:
        print("No hay datos en logs.jsonl todavia.")
        return

    print("== Metricas de conversacion ==")
    total_turnos = len(df)
    total_conversaciones = df["session_id"].nunique() if "session_id" in df else 0
    promedio_turnos = total_turnos / total_conversaciones if total_conversaciones else 0
    print(f"Total de turnos: {total_turnos}")
    print(f"Total de conversaciones: {total_conversaciones}")
    print(f"Promedio de turnos por conversacion: {promedio_turnos:.2f}")

    if "intencion" in df:
        print("\nTurnos por intencion:")
        print(df["intencion"].value_counts(dropna=False))

    if "paso" in df:
        print("\nTurnos por paso del flujo:")
        print(df["paso"].value_counts(dropna=False))

    if "paso" in df and "session_id" in df:
        completadas = df[df["paso"] == "COMPLETADO"].groupby("session_id").size()
        porcentaje_completadas = (len(completadas) / total_conversaciones * 100) if total_conversaciones else 0
        print(f"\nPorcentaje de conversaciones que llegaron a COMPLETADO: {porcentaje_completadas:.2f}%")

    if "timestamp" in df:
        fechas = pd.to_datetime(df["timestamp"], errors="coerce")
        if fechas.notna().any():
            print("\nRango temporal de actividad:")
            print(f"Desde: {fechas.min()} | Hasta: {fechas.max()}")


def exportar_powerbi(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    df_export = df.copy()
    memoria_cols = pd.json_normalize(df_export["memoria"]).rename(columns=lambda c: c.lower()) if "memoria" in df_export else pd.DataFrame()
    for col in ["nombre", "identificacion", "especialidad", "fecha", "hora", "medio"]:
        if col not in memoria_cols:
            memoria_cols[col] = None
    df_export = pd.concat([df_export.drop(columns=["memoria"], errors="ignore"), memoria_cols], axis=1)

    columnas_finales = [
        "session_id",
        "turno",
        "timestamp",
        "usuario_texto",
        "bot_texto",
        "intencion",
        "paso",
        "nombre",
        "identificacion",
        "especialidad",
        "fecha",
        "hora",
        "medio",
    ]
    for col in columnas_finales:
        if col not in df_export:
            df_export[col] = None
    df_export = df_export[columnas_finales]
    df_export.to_csv(EXPORT_CSV, index=False, encoding="utf-8")
    return df_export


def main() -> None:
    df = cargar_logs()

    if df.empty:
        print("No hay datos en logs.jsonl todavia.")
        return

    print("Primeras filas del log:")
    print(df.head())

    print("\nColumnas disponibles:")
    print(df.columns.tolist())

    print("\n")
    calcular_metricas(df)

    df_export = exportar_powerbi(df)
    if not df_export.empty:
        print(f"\nCSV exportado a {EXPORT_CSV} con {len(df_export)} filas.")


if __name__ == "__main__":
    main()
