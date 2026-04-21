"""Rutas de inteligencia artificial: análisis, sentimiento y agente LangChain."""

import json
import os

from fastapi import APIRouter, HTTPException, Request
from newsapi import NewsApiClient
from langchain_core.messages import HumanMessage, SystemMessage

from config import logger
from analisis_rendimineto import calcular_rendimiento_portafolio_total
from database import guardar_tokens_ia
from esquemas import PromptRequest

router = APIRouter()


def _guardar_tokens(modelo: str, tokens_entrada: int, tokens_salida: int) -> None:
    guardar_tokens_ia(
        proveedor="groq",
        modelo=modelo,
        tokens_entrada=tokens_entrada,
        tokens_salida=tokens_salida,
    )


@router.get("/analisis_ia")
@router.post("/analisis_ia")
def analisis_ia(request: Request):
    """Análisis del portfolio con IA (Groq). Devuelve opinión por cripto y resumen global."""
    llm = request.app.state.llm
    modelo = request.app.state.modelo_ia

    try:
        datos_portafolio = calcular_rendimiento_portafolio_total()
        if not datos_portafolio:
            raise HTTPException(status_code=500, detail="calcular_rendimiento_portafolio_total() devolvió vacío")

        datos_json = json.dumps(datos_portafolio, indent=2, ensure_ascii=False)
        prompt = (
            "Eres un analista crypto español, directo. Analiza este portafolio y ten en cuenta: "
            "que la cantidad invertida es poca y no importa perderla. "
            "Dame un análisis de cada moneda, máximo tres líneas y un resumen global.\n"
            f"Datos del portafolio:\n{datos_json}"
        )
        mensajes = [
            SystemMessage(content="Eres un trader español sin filtro, sincero y que va al grano."),
            HumanMessage(content=prompt),
        ]
        respuesta = llm.invoke(mensajes)

        tokens_entrada = respuesta.usage_metadata["input_tokens"]
        tokens_salida = respuesta.usage_metadata["output_tokens"]
        tokens_total = tokens_entrada + tokens_salida
        _guardar_tokens(modelo, tokens_entrada, tokens_salida)

        return {
            "analisis_ia": respuesta.content,
            "datos_portafolio": datos_portafolio,
            "tokens_entrada": tokens_entrada,
            "tokens_salida": tokens_salida,
            "tokens_total": tokens_total,
            "coste_aprox_euros": round(tokens_total * 0.00000008, 7),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en analisis_ia: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"IA ha petado: {str(e)}")


@router.get("/sentimiento_noticias")
def sentimiento_noticias(request: Request, cripto: str = None):
    """Sentimiento de noticias recientes sobre una criptomoneda usando NewsAPI + Groq."""
    if not cripto:
        raise HTTPException(status_code=400, detail="Falta el parámetro 'cripto' en la consulta")

    llm = request.app.state.llm
    modelo = request.app.state.modelo_ia

    nombres_cripto = {"BTC": "Bitcoin", "ETH": "Ethereum", "ADA": "Cardano", "DOT": "Polkadot", "SHIB": "Shiba Inu"}
    nombre_completo = nombres_cripto.get(cripto.upper(), cripto.upper())

    try:
        newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))
        articulos = newsapi.get_everything(
            q=f'"{nombre_completo}" AND (criptomoneda OR crypto)',
            language="es",
            sort_by="publishedAt",
            page_size=10,
        )

        if not articulos or not articulos["articles"]:
            return {"sentimiento": "NEUTRAL", "detalle": "No se encontraron noticias recientes."}

        descripciones = [a["description"] for a in articulos["articles"] if a["description"]]
        texto = "\n".join(descripciones)

        prompt = (
            f"Analiza los siguientes resúmenes de noticias sobre {nombre_completo} y justifica tu respuesta. "
            "Tu respuesta DEBE ser un objeto JSON válido con dos claves:\n"
            '1. "sentimiento": una de estas tres palabras: "Positivo", "Negativo" o "Neutral".\n'
            '2. "explicacion": un párrafo breve en español explicando el porqué de esa clasificación.\n\n'
            f"Resúmenes:\n{texto}"
        )
        mensajes = [
            SystemMessage(content="Eres un experto en análisis de sentimiento en noticias de criptomonedas."),
            HumanMessage(content=prompt),
        ]
        respuesta = llm.invoke(mensajes, response_format={"type": "json_object"})

        try:
            resultado = json.loads(respuesta.content)
            sentimiento = resultado.get("sentimiento", "Neutral")
            explicacion = resultado.get("explicacion", "No se pudo obtener una explicación.")
        except (json.JSONDecodeError, AttributeError):
            sentimiento = "Sin Respuesta"
            explicacion = f"La respuesta de la IA no tuvo el formato esperado: {respuesta.content}"

        tokens_entrada = respuesta.usage_metadata["input_tokens"]
        tokens_salida = respuesta.usage_metadata["output_tokens"]
        tokens_total = tokens_entrada + tokens_salida
        _guardar_tokens(modelo, tokens_entrada, tokens_salida)

        return {
            "simbolo": cripto.upper(),
            "sentimiento": sentimiento,
            "explicacion": explicacion,
            "resumen_noticias": descripciones,
            "tokens_entrada": tokens_entrada,
            "tokens_salida": tokens_salida,
            "tokens_total": tokens_total,
            "coste_aprox_euros": round(tokens_total * 0.00000008, 7),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en sentimiento_noticias para {cripto}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"El análisis de sentimiento ha fallado: {str(e)}")


@router.post("/prompt")
def langchain_ask(datos: PromptRequest, request: Request):
    """Consulta en lenguaje natural al agente LangChain con herramientas MCP."""
    agente = request.app.state.agente
    modelo = request.app.state.modelo_ia

    if agente is None:
        error = request.app.state.error_agente or "Agente LangChain no disponible"
        raise HTTPException(status_code=500, detail={
            "error": error,
            "groq_api_key_present": bool(os.getenv("GROQ_API_KEY")),
            "modelo_configurado": os.getenv("GROQ_MODELO"),
        })

    try:
        agente.reiniciar_memoria()
        resultado = agente.preguntar(datos.question)

        tokens_entrada = resultado.get("tokens_entrada", 0)
        tokens_salida = resultado.get("tokens_salida", 0)
        tokens_total = resultado.get("tokens_total", 0)

        if tokens_total > 0:
            _guardar_tokens(modelo, tokens_entrada, tokens_salida)

        return {
            "success": True,
            "question": datos.question,
            "answer": resultado["output"],
            "tokens_entrada": tokens_entrada,
            "tokens_salida": tokens_salida,
            "tokens_total": tokens_total,
            "num_llamadas_llm": resultado.get("num_llamadas_llm", 0),
            "coste_aprox_euros": round(tokens_total * 0.00000008, 7) if tokens_total > 0 else 0,
        }
    except Exception as e:
        logger.error(f"Error procesando pregunta: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prompt/status")
def agent_status(request: Request):
    """Estado del agente LangChain: disponibilidad y herramientas cargadas."""
    agente = request.app.state.agente
    return {
        "agente_disponible": agente is not None,
        "error_inicializacion": request.app.state.error_agente,
        "groq_api_key_present": bool(os.getenv("GROQ_API_KEY")),
        "modelo_configurado": os.getenv("GROQ_MODELO"),
        "herramientas_disponibles": [t.name for t in agente.herramientas] if agente else [],
    }
