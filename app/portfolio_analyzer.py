"""
Módulo de análisis de portfolio
Implementa la Fase 1.1 y 1.3 del Optimizador de Portfolio Inteligente

Funcionalidades:
- Cálculo de composición del portfolio (% de cada cripto)
- Detección de alertas (sobreexposición, pérdidas severas)
- Métricas de riesgo básicas (diversificación, exposición)
- Comparación con snapshot anterior (Fase 1.3)
"""

from typing import List, Dict, Any, Optional
import time
from config import (
    logger,
    UMBRAL_SOBREEXPOSICION,
    UMBRAL_PERDIDA_SEVERA,
    UMBRAL_CONCENTRACION_ALTA
)
from database import (
    crear_tabla_portfolio_snapshots,
    guardar_snapshot_portfolio,
    obtener_ultimo_snapshot
)
from portfolio_diff import comparar_snapshots


def calcular_peso_portfolio(datos_portfolio: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Añade dos campos de peso a cada cripto del portfolio:
    - peso_inversion_pct: % basado en cuánto invertiste (estrategia de diversificación)
    - peso_actual_pct: % basado en valor actual (exposición actual al riesgo)

    Args:
        datos_portfolio: Lista de diccionarios con datos de cada cripto.
                        Debe incluir 'coste_total_inversion' y 'valor_actual_inversion'.

    Returns:
        La misma lista pero con los campos de peso añadidos.
    """
    # Calcular totales
    total_invertido = sum(cripto.get('coste_total_inversion', 0) for cripto in datos_portfolio)
    valor_total_actual = sum(cripto.get('valor_actual_inversion', 0) for cripto in datos_portfolio)

    if total_invertido == 0:
        logger.warning("El total invertido es 0. No se pueden calcular pesos de inversión.")
        for cripto in datos_portfolio:
            cripto['peso_inversion_pct'] = 0.0
            cripto['peso_actual_pct'] = 0.0
        return datos_portfolio

    # Calcular ambos pesos para cada cripto
    for cripto in datos_portfolio:
        # Peso por inversión (fijo, tu estrategia)
        coste = cripto.get('coste_total_inversion', 0)
        peso_inversion = (coste / total_invertido) * 100 if total_invertido > 0 else 0
        cripto['peso_inversion_pct'] = round(peso_inversion, 2)

        # Peso por valor actual (variable, cambia con el mercado)
        valor_actual = cripto.get('valor_actual_inversion', 0)
        peso_actual = (valor_actual / valor_total_actual) * 100 if valor_total_actual > 0 else 0
        cripto['peso_actual_pct'] = round(peso_actual, 2)

    return datos_portfolio


def detectar_alertas_cripto(cripto: Dict[str, Any]) -> List[str]:
    """
    Detecta alertas específicas para una criptomoneda.

    Args:
        cripto: Diccionario con datos de la cripto (debe incluir 'peso_inversion_pct'
                y 'rentabilidad_porcentaje').

    Returns:
        Lista de strings con las alertas detectadas.
    """
    alertas = []

    # Usar peso_inversion_pct (tu estrategia) para alertas de diversificación
    peso_inversion = cripto.get('peso_inversion_pct', 0)
    rentabilidad = cripto.get('rentabilidad_porcentaje', 0)

    # Alerta de sobreexposición (basado en cuánto invertiste, no en valor actual)
    if peso_inversion > UMBRAL_SOBREEXPOSICION:
        alertas.append("sobreexpuesto")

    # Alerta de pérdida severa
    if rentabilidad < UMBRAL_PERDIDA_SEVERA:
        alertas.append("perdida_severa")

    return alertas


def generar_analisis_global(datos_portfolio: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Genera un análisis global del portfolio con alertas y métricas.

    Args:
        datos_portfolio: Lista de diccionarios con datos completos de cada cripto.
                        Debe incluir 'peso_portfolio_pct', 'rentabilidad_porcentaje',
                        'simbolo'.

    Returns:
        Diccionario con:
        - alertas_globales: Lista de strings con alertas generales
        - metricas: Diccionario con métricas calculadas
    """
    if not datos_portfolio:
        return {
            "alertas_globales": ["No hay datos de portfolio para analizar"],
            "metricas": {
                "num_activos": 0,
                "activos_rentables": 0,
                "activos_perdidas": 0,
                "diversificacion_score": "N/A",
                "exposicion_riesgo": "N/A"
            }
        }

    alertas_globales = []

    # Contar activos rentables vs en pérdidas
    activos_rentables = sum(1 for c in datos_portfolio if c.get('rentabilidad_porcentaje', 0) >= 0)
    activos_perdidas = sum(1 for c in datos_portfolio if c.get('rentabilidad_porcentaje', 0) < 0)
    num_activos = len(datos_portfolio)

    # Detectar sobreexposición individual (basado en inversión, no en valor actual)
    cryptos_sobreexpuestas = [
        c for c in datos_portfolio
        if c.get('peso_inversion_pct', 0) > UMBRAL_SOBREEXPOSICION
    ]

    for cripto in cryptos_sobreexpuestas:
        simbolo = cripto.get('simbolo', 'Desconocida')
        peso_inv = cripto.get('peso_inversion_pct', 0)
        alertas_globales.append(
            f"{simbolo}: invertiste el {peso_inv}% del capital (recomendado: <{UMBRAL_SOBREEXPOSICION}%)"
        )

    # Alerta si la mayoría de activos están en pérdidas
    if activos_perdidas > activos_rentables and num_activos > 1:
        alertas_globales.append(
            f"{activos_perdidas} de {num_activos} activos están en pérdidas"
        )

    # Detectar pérdidas severas
    cryptos_perdida_severa = [
        c for c in datos_portfolio
        if c.get('rentabilidad_porcentaje', 0) < UMBRAL_PERDIDA_SEVERA
    ]

    if cryptos_perdida_severa:
        # Ordenar por rentabilidad (de menor a mayor, es decir, las peores primero)
        cryptos_perdida_severa.sort(key=lambda x: x.get('rentabilidad_porcentaje', 0))

        # Crear lista con símbolo y rentabilidad
        lista_perdidas = ", ".join([
            f"{c.get('simbolo', '?')} ({c.get('rentabilidad_porcentaje', 0):.0f}%)"
            for c in cryptos_perdida_severa[:3]  # Top 3 peores
        ])

        alertas_globales.append(f"Pérdidas severas en: {lista_perdidas}")

    # Calcular concentración (suma de top 2 cryptos por INVERSIÓN, no por valor actual)
    datos_ordenados = sorted(
        datos_portfolio,
        key=lambda x: x.get('peso_inversion_pct', 0),
        reverse=True
    )

    concentracion_top2 = 0
    if len(datos_ordenados) >= 2:
        concentracion_top2 = (
            datos_ordenados[0].get('peso_inversion_pct', 0) +
            datos_ordenados[1].get('peso_inversion_pct', 0)
        )
    elif len(datos_ordenados) == 1:
        concentracion_top2 = datos_ordenados[0].get('peso_inversion_pct', 0)

    # Determinar score de diversificación
    if num_activos >= 8 and concentracion_top2 < 50:
        diversificacion_score = "Alta"
    elif num_activos >= 5 and concentracion_top2 < UMBRAL_CONCENTRACION_ALTA:
        diversificacion_score = "Media"
    else:
        diversificacion_score = "Baja"

    # Determinar exposición al riesgo
    # Basado en % de activos con pérdidas severas
    pct_perdidas_severas = (len(cryptos_perdida_severa) / num_activos * 100) if num_activos > 0 else 0

    if pct_perdidas_severas >= 50:
        exposicion_riesgo = "Alta"
    elif pct_perdidas_severas >= 25:
        exposicion_riesgo = "Media"
    else:
        exposicion_riesgo = "Baja"

    # Construir resultado
    return {
        "alertas_globales": alertas_globales if alertas_globales else ["No hay alertas"],
        "metricas": {
            "num_activos": num_activos,
            "activos_rentables": activos_rentables,
            "activos_perdidas": activos_perdidas,
            "concentracion_top2_pct": round(concentracion_top2, 2),
            "diversificacion_score": diversificacion_score,
            "exposicion_riesgo": exposicion_riesgo
        }
    }


def analizar_portfolio_completo(datos_portfolio: List[Dict[str, Any]], incluir_cambios: bool = True) -> Dict[str, Any]:
    """
    Función principal que realiza el análisis completo del portfolio.

    Esta función orquesta todo el proceso:
    1. Calcula pesos de cada cripto
    2. Detecta alertas individuales
    3. Genera análisis global
    4. Compara con snapshot anterior (si incluir_cambios=True)
    5. Guarda snapshot actual

    Args:
        datos_portfolio: Lista de diccionarios con los datos base de cada cripto
                        (tal como vienen de calcular_rendimiento_portafolio_total).
        incluir_cambios: Si True, incluye comparación con snapshot anterior y guarda nuevo snapshot.

    Returns:
        Diccionario con la estructura completa:
        {
            "portfolio": [...],  # Lista con datos enriquecidos
            "totales": {...},
            "analisis": {...},
            "cambios_desde_ultima_consulta": {...}  # Solo si incluir_cambios=True
        }
    """
    logger.info("Iniciando análisis completo del portfolio...")

    # 0. Asegurar que la tabla de snapshots existe
    if incluir_cambios:
        crear_tabla_portfolio_snapshots()

    # 1. Calcular totales (antes de modificar los datos)
    total_invertido = sum(c.get('coste_total_inversion', 0) for c in datos_portfolio)
    total_valor_actual = sum(c.get('valor_actual_inversion', 0) for c in datos_portfolio)
    total_rentabilidad_abs = sum(c.get('ganancia_perdida_abs', 0) for c in datos_portfolio)

    rentabilidad_total_pct = 0
    if total_invertido > 0:
        rentabilidad_total_pct = (total_rentabilidad_abs / total_invertido) * 100

    # 2. Calcular pesos
    datos_con_pesos = calcular_peso_portfolio(datos_portfolio)

    # 3. Detectar alertas individuales
    for cripto in datos_con_pesos:
        cripto['alertas'] = detectar_alertas_cripto(cripto)

    # 4. Generar análisis global
    analisis_global = generar_analisis_global(datos_con_pesos)

    # 5. Construir respuesta base
    resultado = {
        "portfolio": datos_con_pesos,
        "totales": {
            "total_invertido": round(total_invertido, 2),
            "valor_actual": round(total_valor_actual, 2),
            "rentabilidad_total_pct": round(rentabilidad_total_pct, 2),
            "rentabilidad_total_abs": round(total_rentabilidad_abs, 2)
        },
        "analisis": analisis_global
    }

    # 6. Comparar con snapshot anterior (Fase 1.3)
    if incluir_cambios:
        timestamp_actual = int(time.time())

        # Obtener snapshot anterior
        snapshot_anterior = obtener_ultimo_snapshot()

        # Comparar si existe snapshot anterior
        if snapshot_anterior:
            cambios = comparar_snapshots(datos_con_pesos, snapshot_anterior, timestamp_actual)
            if cambios:
                resultado['cambios_desde_ultima_consulta'] = cambios

        # Guardar snapshot actual
        guardar_snapshot_portfolio(datos_con_pesos, timestamp_actual)

    logger.info(f"Análisis completado. Activos: {analisis_global['metricas']['num_activos']}, "
                f"Alertas: {len(analisis_global['alertas_globales'])}")

    return resultado


# Función auxiliar para testing/debugging
if __name__ == "__main__":
    # Datos de ejemplo (simulando la salida actual del endpoint /portafolio)
    ejemplo_portfolio = [
        {
            "simbolo": "BTC",
            "cantidad_actual": 0.00423910,
            "precio_medio_compra": 88080.02,
            "coste_total_inversion": 373.38,
            "precio_actual": 76456.91,
            "valor_actual_inversion": 324.11,
            "ganancia_perdida_abs": -49.27,
            "rentabilidad_porcentaje": -13.20
        },
        {
            "simbolo": "ETH",
            "cantidad_actual": 0.03649996,
            "precio_medio_compra": 1791.23,
            "coste_total_inversion": 65.38,
            "precio_actual": 2638.84,
            "valor_actual_inversion": 96.32,
            "ganancia_perdida_abs": 30.94,
            "rentabilidad_porcentaje": 47.32
        },
        {
            "simbolo": "ADA",
            "cantidad_actual": 185.340000,
            "precio_medio_compra": 0.754937,
            "coste_total_inversion": 139.92,
            "precio_actual": 0.343600,
            "valor_actual_inversion": 63.68,
            "ganancia_perdida_abs": -76.24,
            "rentabilidad_porcentaje": -54.49
        },
        {
            "simbolo": "SHIB",
            "cantidad_actual": 12359786.991500,
            "precio_medio_compra": 0.000021,
            "coste_total_inversion": 260.07,
            "precio_actual": 0.000007,
            "valor_actual_inversion": 86.64,
            "ganancia_perdida_abs": -173.43,
            "rentabilidad_porcentaje": -66.69
        }
    ]

    # Ejecutar análisis
    resultado = analizar_portfolio_completo(ejemplo_portfolio)

    # Mostrar resultado
    import json
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
