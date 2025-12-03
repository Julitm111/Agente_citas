from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import chat

app = FastAPI(
    title="Agente de Citas Medicas API",
    version="1.0.0"
)

# CORS si usas frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Aquí SÍ montamos el prefijo
app.include_router(chat.router, prefix="/api/v1")
