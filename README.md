# Gabee.ai - Agente conversacional para agendar citas medicas

Proyecto de ejemplo para un rol LLM Agent Developer / Conversational AI Engineer. El agente agenda citas medicas por consola usando la API de OpenAI, guarda trazas en JSONL y ofrece un flujo multi-turno con NLU y analitica de logs lista para BI.

## Que hace
- Conversa con el usuario para agendar citas medicas (nombre, identificacion, especialidad, fecha, hora, medio).
- Usa OpenAI para deteccion de intencion y extraccion de entidades.
- Maneja estado de conversacion y slots requeridos.
- Registra cada turno en JSONL con session_id y numero de turno.
- Incluye un script de analisis que genera metricas y un CSV listo para Power BI/Excel.

## Arquitectura modular
- `src/domain.py`: modelos de dominio (Intent, FlowStep, Memory, ConversationState), slots requeridos.
- `src/llm_client.py`: cliente HTTP para OpenAI (requests) con manejo de errores y fallback.
- `src/nlu.py`: deteccion de intencion y extraccion de entidades via LLM.
- `src/dialog_manager.py`: flujo conversacional, manejo de slots y agente principal (`agente_citas`).
- `src/logging_utils.py`: persistencia JSONL con session_id y contador de turnos.
- `src/main.py`: punto de entrada en consola.
- `analisis_logs.py`: lectura de logs, metricas de BI y export a CSV.

### Diagrama de flujo (texto)
```
Usuario (consola)
     ↓
main.py  →  dialog_manager.py (agente_citas)
     ↓
nlu.py + llm_client.py (intencion + entidades via OpenAI)
     ↓
domain.py (estado y memoria)
     ↓
logging_utils.py (logs en JSONL con session_id/turno)
     ↓
analisis_logs.py (metricas y CSV para BI)
```

## Requisitos
- Python 3.9+
- Dependencias: `pip install -r requirements.txt`
- Variable de entorno `OPENAI_API_KEY` exportada con tu clave.

## Como ejecutar el agente
```bash
cd src
python main.py
```
Tambien puedes usar:
```bash
python -m src.main
```

## Como ejecutar el analisis de logs
```bash
python analisis_logs.py
```
Imprime:
- Primeras filas y columnas del log.
- Total de turnos, conversaciones y promedio de turnos por sesion.
- Conteo de turnos por intencion y por paso del flujo.
- Porcentaje de conversaciones que llegaron a COMPLETADO.
- Rango temporal de actividad.

Ademas genera `logs_export_powerbi.csv` con columnas planas (session_id, turno, timestamp, textos, intencion, paso, slots) lista para cargar en Power BI o Excel.

## Manejo de errores y fallback
- `LLMClient` retorna None en errores o respuestas inesperadas.
- NLU devuelve `Intent.DESCONOCIDA` o entidades en None si el LLM falla.
- El agente responde con un mensaje de cortesía si hay fallas repetidas del modelo.

## Ideas de mejora futura
- Integrar TTS/ASR para voz.
- Conectar a canales reales (WhatsApp, web, call center).
- Persistir en base de datos (SQL/NoSQL) en lugar de archivo.
- Añadir reintentos y monitoring (traces, dashboards en tiempo real).
