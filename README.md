# Gabee.ai - Agente conversacional para agendar citas medicas

Proyecto de ejemplo para un rol LLM Agent Developer / Conversational AI Engineer. El agente agenda citas medicas usando la API de OpenAI, guarda trazas en JSONL y ofrece un flujo multi-turno con NLU y analitica de logs lista para BI.

## Que hace
- Conversa con el usuario para agendar citas medicas (nombre, identificacion, especialidad, fecha, hora, medio).
- Usa OpenAI para deteccion de intencion y extraccion de entidades.
- Maneja estado de conversacion y slots requeridos.
- Registra cada turno en JSONL con session_id y numero de turno.
- Incluye un script de analisis que genera metricas y un CSV listo para Power BI/Excel.

## Arquitectura (MVC liviano + API)
- `src/models/domain.py`: modelos de dominio (Intent, FlowStep, Memory, ConversationState), slots requeridos.
- `src/controllers/llm_client.py`: cliente HTTP para OpenAI (requests) con manejo de errores y fallback.
- `src/controllers/nlu.py`: deteccion de intencion y extraccion de entidades via LLM.
- `src/controllers/dialog_manager.py`: flujo conversacional y agente principal (`agente_citas`).
- `src/controllers/logging_utils.py`: persistencia JSONL con session_id y contador de turnos.
- `src/views/main.py`: punto de entrada en consola (vista CLI).
- `src/views/streamlit_app.py`: vista Streamlit para demo web.
- `src/api/api.py`: app FastAPI principal.
- `src/api/routers/chat.py`: endpoints REST (chat, reset, health) con manejo de sesiones y BD.
- `src/api/schemas.py`: modelos Pydantic para request/response.
- `src/api/db.py`: SQLite y registro de citas.
- `analisis_logs.py`: lectura de logs, metricas de BI y export a CSV.

### Diagrama de flujo (texto)
```
Usuario (CLI/Streamlit)
     |
views (main.py / streamlit_app.py)
     |
controllers (dialog_manager -> nlu + llm_client)
     |
models (domain: estado y memoria)
     |
controllers/logging_utils (logs JSONL con session_id/turno)
     |
analisis_logs.py (metricas y CSV para BI)
```

## Requisitos
- Python 3.9+
- Dependencias: `pip install -r requirements.txt`
- Variable de entorno `OPENAI_API_KEY` exportada con tu clave.

## Como ejecutar el agente (CLI)
Desde la raiz del repo:
```bash
python -m src.views.main
```
(asegura que `src` este en el PYTHONPATH; con `-m` se resuelve solo.)

## Como ejecutar la demo Streamlit
```bash
streamlit run src/views/streamlit_app.py
```
Si tienes problemas de imports, exporta `PYTHONPATH=src` antes de ejecutar.

## Como ejecutar la API FastAPI
```bash
uvicorn src.api.api:app --reload
```
Luego prueba:
```bash
POST http://localhost:8000/api/v1/chat
{
  "message": "Hola, quiero agendar una cita",
  "session_id": "123"
}
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
- El agente responde con un mensaje de cortesia si hay fallas repetidas del modelo.

## Ideas de mejora futura
- Integrar TTS/ASR para voz.
- Conectar a canales reales (WhatsApp, web, call center).
- Persistir en base de datos (SQL/NoSQL) en lugar de archivo.
- Añadir reintentos y monitoring (traces, dashboards en tiempo real).
