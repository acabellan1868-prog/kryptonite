"""
Punto de entrada de la API Kryptonite con FastAPI.
Inicializa el LLM y el agente LangChain en el lifespan para compartirlos entre rutas.
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_groq import ChatGroq

from rutas import datos, portfolio, analisis, ia

load_dotenv("parametros.env")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialización y limpieza de recursos compartidos."""
    clave_api = os.getenv("GROQ_API_KEY")
    modelo_ia = os.getenv("GROQ_MODELO", "llama-3.3-70b-versatile")

    app.state.modelo_ia = modelo_ia
    app.state.agente = None
    app.state.error_agente = None

    if clave_api:
        app.state.llm = ChatGroq(model=modelo_ia, temperature=0.7, groq_api_key=clave_api)
        try:
            from ia.grog_agente import crear_agente_kryptonite
            app.state.agente = crear_agente_kryptonite(clave_api)
            herramientas = [t.name for t in app.state.agente.herramientas]
            print(f"✅ Agente LangChain inicializado. Herramientas: {herramientas}")
        except Exception as e:
            app.state.error_agente = str(e)
            print(f"❌ Error al inicializar el agente: {e}")
    else:
        app.state.llm = None
        app.state.error_agente = "Variable de entorno GROQ_API_KEY no configurada"
        print("⚠️  GROQ_API_KEY no encontrada. Los endpoints de IA no estarán disponibles.")

    yield


app = FastAPI(
    title="Kryptonite API",
    description="Sistema de análisis y gestión de inversiones en criptomonedas.",
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(datos.router, tags=["Datos"])
app.include_router(portfolio.router, tags=["Portfolio"])
app.include_router(analisis.router, tags=["Análisis"])
app.include_router(ia.router, tags=["IA"])
