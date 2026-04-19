"""
Herramientas de LangChain para ejecutar análisis técnicos sobre criptomonedas.
Estas herramientas permiten al agente usar las funciones de análisis ya existentes en Kryptonite.
"""
import sys
from pathlib import Path

# Añadir directorio padre al path para poder importar módulos de src/
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from typing import Optional, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

# Importar funciones de análisis existentes
from analysis import obtener_senal_cambio_extremo, obtener_senal_cruce_medias_moviles
from analisis_rendimineto import calcular_rendimiento_criptomoneda
# portfolio_analyzer y calcular_rendimiento_portafolio_total se importan en runtime para evitar circular imports
from database import get_data_from_db
import pandas as pd
from config import logger


# ============================================================================
# HERRAMIENTA 1: Analizar señal de compra/venta
# ============================================================================

class EntradaAnalizarSenal(BaseModel):
    """Input para analizar señales de trading"""
    cripto: str = Field(description="Símbolo de la criptomoneda a analizar (ej: 'BTC', 'ETH')")
    estrategia: str = Field(
        default="cambio_extremo",
        description="Estrategia de análisis: 'cambio_extremo', 'medias_moviles', o 'todas'"
    )


class HerramientaAnalizarSenal(BaseTool):
    name: str = "analizar_senal_compra_venta"
    description: str = """
    Ejecuta análisis técnico para generar señales de trading (COMPRA, VENTA, MANTENER).

    Estrategias disponibles:
    - 'cambio_extremo': Detecta cambios bruscos de precio (útil para movimientos rápidos)
    - 'medias_moviles': Analiza cruces de medias móviles (útil para tendencias)
    - 'todas': Ejecuta ambas estrategias y combina resultados

    Usa esta herramienta cuando el usuario pregunte:
    - "¿Debería comprar/vender X?"
    - "¿Es buen momento para entrar en X?"
    - "Dame una señal de trading para X"
    - "¿Qué dice el análisis técnico de X?"
    """
    args_schema: type[BaseModel] = EntradaAnalizarSenal

    def _run(self, cripto: str, estrategia: str = "cambio_extremo") -> str:
        """Ejecuta la herramienta"""
        try:
            cripto = cripto.upper().strip()
            estrategia = estrategia.lower().strip()

            resultados = {}

            # Estrategia 1: Cambio Extremo
            if estrategia in ["cambio_extremo", "todas"]:
                try:
                    senal_cambio = obtener_senal_cambio_extremo(
                        simbolo=cripto,
                        intervalo_minutos=15,
                        umbral_porcentual=1.0,
                        confirmar_con_volumen=True,
                        umbral_porcentual_volumen=20.0
                    )
                    resultados['cambio_extremo'] = senal_cambio
                except Exception as e:
                    logger.error(f"Error en análisis de cambio extremo: {e}")
                    resultados['cambio_extremo'] = {"error": str(e)}

            # Estrategia 2: Medias Móviles
            if estrategia in ["medias_moviles", "todas"]:
                try:
                    # Obtener datos históricos para medias móviles
                    datos = get_data_from_db(cripto, window=250)

                    if datos and datos['prices']:
                        df_historico = pd.DataFrame({
                            'timestamp': datos['timestamps'],
                            'precio': datos['prices']
                        })

                        senal_ma = obtener_senal_cruce_medias_moviles(
                            simbolo=cripto,
                            df_historico=df_historico,
                            periodo_sma_rapida=50,
                            periodo_sma_lenta=200
                        )
                        resultados['medias_moviles'] = senal_ma
                    else:
                        resultados['medias_moviles'] = {"error": "Datos insuficientes"}

                except Exception as e:
                    logger.error(f"Error en análisis de medias móviles: {e}")
                    resultados['medias_moviles'] = {"error": str(e)}

            # Formatear respuesta
            return self._formatear_respuesta(cripto, estrategia, resultados)

        except Exception as e:
            return f"Error al analizar señal para {cripto}: {str(e)}"

    def _formatear_respuesta(self, cripto: str, estrategia: str, resultados: dict) -> str:
        """Formatea la respuesta de forma legible para el agente"""
        respuesta = f"📊 ANÁLISIS TÉCNICO DE {cripto}\n\n"

        # Cambio Extremo
        if 'cambio_extremo' in resultados:
            datos = resultados['cambio_extremo']
            if 'error' not in datos:
                respuesta += "🔍 ESTRATEGIA: Cambio Extremo (15 min)\n"
                respuesta += f"   • Precio actual: {datos.get('precio_actual', 'N/A')}\n"
                respuesta += f"   • Cambio porcentual: {datos.get('cambio_porcentual', 0):.2f}%\n"
                respuesta += f"   • Tendencia previa: {datos.get('tendencia_previa', 'DESCONOCIDA')}\n"

                if datos.get('volumen_confirmado') is not None:
                    conf = "✅ SÍ" if datos['volumen_confirmado'] else "❌ NO"
                    respuesta += f"   • Volumen confirmado: {conf}\n"

                respuesta += f"   • 🎯 SEÑAL: {datos.get('senal', 'MANTENER')}\n\n"

        # Medias Móviles
        if 'medias_moviles' in resultados:
            datos = resultados['medias_moviles']
            if 'error' not in datos:
                respuesta += "📈 ESTRATEGIA: Medias Móviles (SMA 50/200)\n"
                respuesta += f"   • SMA 50: {datos.get('sma_rapida', 'N/A')}\n"
                respuesta += f"   • SMA 200: {datos.get('sma_lenta', 'N/A')}\n"
                respuesta += f"   • 🎯 SEÑAL: {datos.get('senal', 'MANTENER')}\n\n"

        # Señal combinada
        if estrategia == "todas" and len(resultados) > 1:
            senales = [r.get('senal') for r in resultados.values() if 'error' not in r]

            if senales:
                # Contar votos
                compras = senales.count('COMPRA')
                ventas = senales.count('VENTA')

                respuesta += "🎲 SEÑAL COMBINADA:\n"
                if compras > ventas:
                    respuesta += f"   • Recomendación: COMPRA ({compras}/{len(senales)} estrategias)\n"
                elif ventas > compras:
                    respuesta += f"   • Recomendación: VENTA ({ventas}/{len(senales)} estrategias)\n"
                else:
                    respuesta += f"   • Recomendación: MANTENER (señales mixtas)\n"

        return respuesta

    async def _arun(self, cripto: str, estrategia: str = "cambio_extremo") -> str:
        """Versión asíncrona"""
        return self._run(cripto, estrategia)


# ============================================================================
# HERRAMIENTA 2: Obtener análisis de portfolio
# ============================================================================

class EntradaAnalisisPortfolio(BaseModel):
    """Input para obtener análisis del portfolio"""
    # Campo dummy para compatibilidad con LangChain (no se usa)
    dummy: str = Field(default="", description="No se requieren parámetros para esta herramienta")


class HerramientaAnalisisPortfolio(BaseTool):
    name: str = "obtener_analisis_portfolio"
    description: str = """
    Obtiene un análisis completo del portfolio del usuario con:
    - Composición actual (% de cada cripto)
    - Valor total y rentabilidad
    - Alertas de riesgo (sobreexposición, pérdidas severas)
    - Métricas de diversificación y exposición al riesgo

    Usa esta herramienta cuando el usuario pregunte:
    - "¿Cómo está mi portfolio?"
    - "Dame un resumen de mis inversiones"
    - "¿Cuánto he ganado/perdido en total?"
    - "¿Mi portfolio está bien diversificado?"
    - "¿Tengo alguna alerta?"
    """
    args_schema: type[BaseModel] = EntradaAnalisisPortfolio

    def _run(self, dummy: str = "") -> str:
        """Ejecuta la herramienta"""
        try:
            # Importar aquí para evitar problemas de importación circular
            from analisis_rendimineto import calcular_rendimiento_portafolio_total

            logger.info("🔍 [HERRAMIENTA] Iniciando obtener_analisis_portfolio...")

            # Obtener datos del portfolio
            logger.info("📊 [HERRAMIENTA] Llamando a calcular_rendimiento_portafolio_total()...")
            portfolio_data = calcular_rendimiento_portafolio_total()
            logger.info(f"✅ [HERRAMIENTA] Portfolio data obtenido: {len(portfolio_data) if portfolio_data else 0} cryptos")

            if not portfolio_data:
                return "No hay datos de portfolio disponibles. El usuario no tiene criptomonedas registradas."

            # SIMPLIFICADO: Solo devolver resumen básico sin análisis completo
            total_valor = sum(c.get('valor_actual_inversion', 0) for c in portfolio_data)
            total_invertido = sum(c.get('coste_total_inversion', 0) for c in portfolio_data)
            rentabilidad = ((total_valor - total_invertido) / total_invertido * 100) if total_invertido > 0 else 0

            respuesta = f"""💼 RESUMEN DEL PORTFOLIO

📊 Totales:
   • Valor actual: {total_valor:.2f}€
   • Inversión total: {total_invertido:.2f}€
   • Rentabilidad: {rentabilidad:+.2f}%

🪙 Activos ({len(portfolio_data)}):
"""
            for cripto in portfolio_data[:5]:
                respuesta += f"   • {cripto.get('simbolo')}: {cripto.get('valor_actual_inversion', 0):.2f}€ ({cripto.get('rentabilidad_porcentaje', 0):+.2f}%)\n"

            if len(portfolio_data) > 5:
                respuesta += f"   • ... y {len(portfolio_data) - 5} más\n"

            logger.info(f"✅ [HERRAMIENTA] Respuesta generada ({len(respuesta)} chars)")
            return respuesta

        except Exception as e:
            logger.error(f"❌ [HERRAMIENTA] Error al obtener análisis de portfolio: {e}", exc_info=True)
            return f"Error al analizar portfolio: {str(e)}"

    def _formatear_respuesta(self, analisis: dict) -> str:
        """Formatea el análisis del portfolio de forma legible"""
        respuesta = "💼 ANÁLISIS DEL PORTFOLIO\n\n"

        # Totales
        if 'totales' in analisis:
            totales = analisis['totales']
            respuesta += "📊 RESUMEN GENERAL:\n"
            respuesta += f"   • Valor total actual: {totales.get('valor_actual', 0):.2f}€\n"
            respuesta += f"   • Inversión total: {totales.get('total_invertido', 0):.2f}€\n"
            respuesta += f"   • Rentabilidad: {totales.get('rentabilidad_total_pct', 0):.2f}% "
            respuesta += f"({totales.get('rentabilidad_total_abs', 0):+.2f}€)\n\n"

        # Composición
        if 'portfolio' in analisis and analisis['portfolio']:
            respuesta += "🪙 COMPOSICIÓN:\n"
            for cripto_data in analisis['portfolio'][:5]:  # Top 5
                simbolo = cripto_data.get('simbolo', 'N/A')
                peso = cripto_data.get('peso_portfolio_pct', 0)
                rent = cripto_data.get('rentabilidad_pct', 0)
                respuesta += f"   • {simbolo}: {peso:.1f}% del portfolio "
                respuesta += f"(rentabilidad: {rent:+.1f}%)\n"

            if len(analisis['portfolio']) > 5:
                respuesta += f"   • ... y {len(analisis['portfolio']) - 5} más\n"
            respuesta += "\n"

        # Alertas
        if 'analisis' in analisis:
            analisis_info = analisis['analisis']

            if 'alertas_globales' in analisis_info and analisis_info['alertas_globales']:
                respuesta += "⚠️ ALERTAS:\n"
                for alerta in analisis_info['alertas_globales']:
                    respuesta += f"   • {alerta}\n"
                respuesta += "\n"

            # Métricas
            if 'metricas' in analisis_info:
                metricas = analisis_info['metricas']
                respuesta += "📈 MÉTRICAS DE RIESGO:\n"
                respuesta += f"   • Diversificación: {metricas.get('diversificacion_score', 'N/A')}\n"
                respuesta += f"   • Exposición al riesgo: {metricas.get('exposicion_riesgo', 'N/A')}\n"
                respuesta += f"   • Activos rentables: {metricas.get('activos_rentables', 0)}/{metricas.get('num_activos', 0)}\n"

        return respuesta

    async def _arun(self, dummy: str = "") -> str:
        """Versión asíncrona"""
        return self._run(dummy)


# ============================================================================
# HERRAMIENTA 3: Calcular rendimiento histórico de una cripto
# ============================================================================

class EntradaRendimientoHistorico(BaseModel):
    """Input para calcular rendimiento de una criptomoneda"""
    cripto: str = Field(description="Símbolo de la criptomoneda (ej: 'BTC', 'ETH')")


class HerramientaRendimientoHistorico(BaseTool):
    name: str = "calcular_rendimiento_historico"
    description: str = """
    Calcula el rendimiento histórico detallado de una criptomoneda específica del portfolio.
    Muestra:
    - Cantidad total actual
    - Precio medio de compra vs precio actual
    - Inversión total realizada
    - Valor actual de la inversión
    - Ganancia/pérdida absoluta y porcentual

    Usa esta herramienta cuando el usuario pregunte:
    - "¿Cuánto he ganado/perdido con X?"
    - "¿Cómo va mi inversión en X?"
    - "¿A qué precio compré X?"
    - "Dame el rendimiento de X"
    """
    args_schema: type[BaseModel] = EntradaRendimientoHistorico

    def _run(self, cripto: str) -> str:
        """Ejecuta la herramienta"""
        try:
            cripto = cripto.upper().strip()

            # Calcular rendimiento usando función existente
            rendimiento = calcular_rendimiento_criptomoneda(cripto)

            if not rendimiento or rendimiento.get('cantidad_actual', 0) == 0:
                return f"No hay datos de inversión para {cripto}. El usuario no tiene esta criptomoneda o no hay operaciones registradas."

            # Formatear respuesta
            return self._formatear_respuesta(rendimiento)

        except Exception as e:
            logger.error(f"Error al calcular rendimiento de {cripto}: {e}")
            return f"Error al calcular rendimiento de {cripto}: {str(e)}"

    def _formatear_respuesta(self, rendimiento: dict) -> str:
        """Formatea el rendimiento de forma legible"""
        simbolo = rendimiento.get('simbolo', 'N/A')

        respuesta = f"💰 RENDIMIENTO DE {simbolo}\n\n"

        respuesta += "📊 POSICIÓN ACTUAL:\n"
        respuesta += f"   • Cantidad: {rendimiento.get('cantidad_actual', 0):.8f} {simbolo}\n"
        respuesta += f"   • Precio actual: {rendimiento.get('precio_actual', 0):.2f}€\n"
        respuesta += f"   • Valor actual: {rendimiento.get('valor_actual_inversion', 0):.2f}€\n\n"

        respuesta += "📈 INVERSIÓN:\n"
        respuesta += f"   • Precio medio de compra: {rendimiento.get('precio_medio_compra', 0):.2f}€\n"
        respuesta += f"   • Total invertido: {rendimiento.get('coste_total_inversion', 0):.2f}€\n\n"

        ganancia = rendimiento.get('ganancia_perdida_abs', 0)
        rentabilidad = rendimiento.get('rentabilidad_porcentaje', 0)

        if ganancia >= 0:
            emoji = "✅"
            estado = "GANANCIA"
        else:
            emoji = "❌"
            estado = "PÉRDIDA"

        respuesta += f"{emoji} RESULTADO:\n"
        respuesta += f"   • {estado}: {ganancia:+.2f}€ ({rentabilidad:+.2f}%)\n"

        return respuesta

    async def _arun(self, cripto: str) -> str:
        """Versión asíncrona"""
        return self._run(cripto)


# ============================================================================
# Función para obtener todas las herramientas de análisis
# ============================================================================

def obtener_herramientas_analisis() -> List[BaseTool]:
    """Devuelve todas las herramientas de análisis disponibles"""
    return [
        HerramientaAnalizarSenal(),
        HerramientaAnalisisPortfolio(),
        HerramientaRendimientoHistorico()
    ]
