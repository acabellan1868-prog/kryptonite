"""
Agente de LangChain que usa Groq y las herramientas MCP SQLite
"""
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_core.callbacks import BaseCallbackHandler
from typing import Optional, Any, Dict
import os

from .mcp_sqlite_tools import obtener_herramientas_mcp
from .analisis_tools import obtener_herramientas_analisis


class TokenCounterCallback(BaseCallbackHandler):
    """Callback que cuenta tokens de todas las llamadas al LLM"""

    def __init__(self):
        super().__init__()
        self.total_tokens_entrada = 0
        self.total_tokens_salida = 0
        self.total_tokens_totales = 0
        self.num_llamadas_llm = 0  # Contador de iteraciones/llamadas al LLM

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """Captura los tokens cada vez que el LLM termina una llamada"""
        if response is None:
            return

        # Incrementar contador de llamadas al LLM
        self.num_llamadas_llm += 1

        try:
            # Para ChatGroq, buscar en generations[0].message.response_metadata
            # NOTA: response.generations es una lista de listas de ChatGeneration
            if hasattr(response, 'generations') and response.generations:
                for generation_list in response.generations:
                    if isinstance(generation_list, list):
                        for generation in generation_list:
                            if hasattr(generation, 'message') and generation.message:
                                message = generation.message

                                # Buscar en response_metadata (forma principal en ChatGroq)
                                if hasattr(message, 'response_metadata') and message.response_metadata:
                                    metadata = message.response_metadata

                                    # Groq usa 'token_usage' en response_metadata
                                    if 'token_usage' in metadata:
                                        token_usage = metadata['token_usage']
                                        entrada = token_usage.get('prompt_tokens', 0)
                                        salida = token_usage.get('completion_tokens', 0)
                                        total = token_usage.get('total_tokens', entrada + salida)

                                        self.total_tokens_entrada += entrada
                                        self.total_tokens_salida += salida
                                        self.total_tokens_totales += total

                                        print(f"📊 Llamada #{self.num_llamadas_llm} | Tokens: entrada={entrada}, salida={salida}, total={total}")
                                        return

                                # Backup: buscar en usage_metadata
                                if hasattr(message, 'usage_metadata') and message.usage_metadata:
                                    usage = message.usage_metadata
                                    entrada = usage.get('input_tokens', 0)
                                    salida = usage.get('output_tokens', 0)
                                    total = usage.get('total_tokens', entrada + salida)

                                    self.total_tokens_entrada += entrada
                                    self.total_tokens_salida += salida
                                    self.total_tokens_totales += total

                                    print(f"📊 Llamada #{self.num_llamadas_llm} | Tokens: entrada={entrada}, salida={salida}, total={total}")
                                    return

            # Backup: buscar en llm_output (forma antigua)
            if hasattr(response, 'llm_output') and response.llm_output:
                if isinstance(response.llm_output, dict) and 'token_usage' in response.llm_output:
                    token_usage = response.llm_output['token_usage']
                    entrada = token_usage.get('prompt_tokens', 0)
                    salida = token_usage.get('completion_tokens', 0)
                    total = token_usage.get('total_tokens', entrada + salida)

                    self.total_tokens_entrada += entrada
                    self.total_tokens_salida += salida
                    self.total_tokens_totales += total

                    print(f"📊 Llamada #{self.num_llamadas_llm} | Tokens: entrada={entrada}, salida={salida}, total={total}")
                    return

        except Exception as e:
            print(f"⚠️  Error capturando tokens: {str(e)}")

    def get_totals(self) -> Dict[str, int]:
        """Devuelve el total de tokens usados y número de llamadas"""
        return {
            "tokens_entrada": self.total_tokens_entrada,
            "tokens_salida": self.total_tokens_salida,
            "tokens_total": self.total_tokens_totales if self.total_tokens_totales > 0
                           else self.total_tokens_entrada + self.total_tokens_salida,
            "num_llamadas_llm": self.num_llamadas_llm
        }


class AgenteKryptonite:
    """
    Agente inteligente que puede consultar la base de datos de kryptonite
    usando lenguaje natural.
    """
    
    def __init__(self, clave_api_groq: str, modelo: Optional[str] = None):
        """
        Inicializa el agente

        Args:
            clave_api_groq: Clave API de Groq
            modelo: Modelo de Groq a usar (si es None, usa GROQ_MODELO del entorno)
        """
        # Si no se proporciona modelo, usar el del entorno
        if modelo is None:
            modelo = os.getenv("GROQ_MODELO", "llama-3.3-70b-versatile")

        # Configurar el LLM de Groq
        self.llm = ChatGroq(
            api_key=clave_api_groq,
            model=modelo,
            temperature=0,  # Para respuestas más deterministas
            max_tokens=4096
        )
        
        # Obtener herramientas MCP (consultas a base de datos)
        herramientas_mcp = obtener_herramientas_mcp()

        # Obtener herramientas de análisis técnico
        herramientas_analisis = obtener_herramientas_analisis()

        # Combinar todas las herramientas
        self.herramientas = herramientas_mcp + herramientas_analisis
        
        # Crear el prompt del agente
        self.plantilla = ChatPromptTemplate.from_messages([
            ("system", """Eres un asistente experto en análisis de inversiones en criptomonedas.
            Tienes acceso a:
            1. Base de datos SQLite con operaciones e inversiones
            2. Herramientas de análisis técnico para generar señales de trading
            3. Análisis de portfolio y rendimiento

            ### HERRAMIENTAS DISPONIBLES ###

            🔍 HERRAMIENTAS DE ANÁLISIS TÉCNICO (USA ESTAS PRIMERO):
            - 'analizar_senal_compra_venta': Genera señales de trading (COMPRA/VENTA/MANTENER)
              Usa cuando pregunten: "¿Debería comprar X?", "¿Es buen momento para X?", "Dame señal de X"

            - 'obtener_analisis_portfolio': Análisis completo del portfolio con alertas y métricas
              Usa cuando pregunten: "¿Cómo está mi portfolio?", "Dame resumen de inversiones"

            - 'calcular_rendimiento_historico': Rendimiento detallado de una cripto específica
              Usa cuando pregunten: "¿Cuánto he ganado con X?", "¿Cómo va mi inversión en X?"

            📊 HERRAMIENTAS DE BASE DE DATOS (USA SI NECESITAS DATOS CRUDOS):
            - 'listar_tablas_base_de_datos': Ver tablas disponibles
            - 'obtener_esquema_tabla': Ver estructura de una tabla
            - 'consultar_base_de_datos': Ejecutar queries SQL SELECT
            - 'obtener_datos_tabla': Obtener muestra de datos

            ### CONTEXTO DE LA BASE DE DATOS ###
            - Tabla 'operaciones': Compras/ventas de criptomonedas
            - Tabla 'crypto_data': Precios históricos

            ### CÓMO RESPONDER ###

            **Para preguntas de trading/señales:**
            1. USA directamente 'analizar_senal_compra_venta' (NO consultes la BD primero)
            2. Interpreta los resultados de forma clara
            3. Explica la recomendación y por qué

            **Para preguntas sobre portfolio:**
            1. USA directamente 'obtener_analisis_portfolio' (NO consultes la BD primero)
            2. Resalta las alertas importantes
            3. Explica las métricas de riesgo

            **Para preguntas sobre rendimiento de una cripto:**
            1. USA directamente 'calcular_rendimiento_historico' (NO consultes la BD primero)
            2. Explica si está ganando o perdiendo
            3. Contextualiza el rendimiento

            **Para preguntas complejas o de datos históricos:**
            Solo entonces usa las herramientas de base de datos.

            ### REGLAS IMPORTANTES ###
            - SIEMPRE usa las herramientas de análisis cuando estén disponibles
            - NO hagas queries SQL manualmente si hay una herramienta que lo haga
            - Sé claro, conciso y útil en tus respuestas
            - Si una herramienta falla, explica el problema claramente

            Tu objetivo es ser un ASESOR PROACTIVO, no solo un consultor de datos.
            """),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Crear el agente
        agente = create_tool_calling_agent(
            llm=self.llm,
            tools=self.herramientas,
            prompt=self.plantilla
        )
        
        # Crear el ejecutor del agente con memoria
        self.memoria = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
           
             # ← Añade esto para eliminar el warning
        )
        
        self.ejecutor_agente = AgentExecutor(
            agent=agente,
            tools=self.herramientas,
            memory=self.memoria,
            verbose=True,  # Para ver los pasos del agente
            max_iterations=10,  # Máximo de llamadas a herramientas (aumentado para análisis complejos)
            handle_parsing_errors=True,
            return_intermediate_steps=True  # Para capturar información adicional
        )

        # Variable para almacenar el uso de tokens de la última llamada
        self.ultimo_uso_tokens = {
            "tokens_entrada": 0,
            "tokens_salida": 0,
            "tokens_total": 0
        }
    
    def preguntar(self, pregunta: str) -> dict:
        """
        Hace una pregunta al agente

        Args:
            pregunta: Pregunta en lenguaje natural

        Returns:
            Diccionario con:
                - output: Respuesta del agente
                - tokens_entrada: Tokens de entrada utilizados
                - tokens_salida: Tokens de salida generados
                - tokens_total: Total de tokens
        """
        # Crear callback para contar tokens
        token_counter = TokenCounterCallback()

        try:
            # Ejecutar el agente con el callback
            resultado = self.ejecutor_agente.invoke(
                {"input": pregunta},
                config={"callbacks": [token_counter]}
            )

            # Obtener totales de tokens del callback
            tokens_info = token_counter.get_totals()

            # Actualizar el registro interno
            self.ultimo_uso_tokens = tokens_info

            return {
                "output": resultado["output"],
                "tokens_entrada": tokens_info["tokens_entrada"],
                "tokens_salida": tokens_info["tokens_salida"],
                "tokens_total": tokens_info["tokens_total"],
                "num_llamadas_llm": tokens_info["num_llamadas_llm"]
            }

        except Exception as e:
            return {
                "output": f"Error al procesar la pregunta: {str(e)}",
                "tokens_entrada": 0,
                "tokens_salida": 0,
                "tokens_total": 0,
                "num_llamadas_llm": 0
            }
    
    def reiniciar_memoria(self):
        """Limpia la memoria de conversación"""
        self.memoria.clear()


def crear_agente_kryptonite(clave_api_groq: Optional[str] = None) -> AgenteKryptonite:
    """
    Crea una instancia del agente de kryptonite
    """
    if clave_api_groq is None:
        clave_api_groq = os.getenv("GROQ_API_KEY")
        if not clave_api_groq:
            raise ValueError("Necesitas proporcionar GROQ_API_KEY como variable de entorno o como argumento.")
    
    return AgenteKryptonite(clave_api_groq=clave_api_groq)