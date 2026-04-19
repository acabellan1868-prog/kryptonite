"""
Módulo de comparación de snapshots del portfolio
Implementa la Fase 1.3: Detección de cambios desde última consulta

Funcionalidades:
- Comparar estado actual del portfolio con snapshot anterior
- Calcular diferencias por cripto (€ y %)
- Detectar nuevas posiciones y posiciones cerradas
- Formatear tiempo transcurrido de forma legible
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from config import logger


def formatear_tiempo_transcurrido(timestamp_anterior: int, timestamp_actual: int) -> str:
    """
    Formatea el tiempo transcurrido entre dos timestamps de forma legible.

    Args:
        timestamp_anterior: Timestamp Unix del snapshot anterior
        timestamp_actual: Timestamp Unix actual

    Returns:
        String formateado (ej: "2 horas 15 minutos", "3 días 4 horas")
    """
    diferencia_segundos = timestamp_actual - timestamp_anterior

    if diferencia_segundos < 0:
        return "0 segundos"

    # Calcular componentes de tiempo
    dias = diferencia_segundos // 86400
    horas = (diferencia_segundos % 86400) // 3600
    minutos = (diferencia_segundos % 3600) // 60
    segundos = diferencia_segundos % 60

    # Construir string
    partes = []
    if dias > 0:
        partes.append(f"{dias} día{'s' if dias != 1 else ''}")
    if horas > 0:
        partes.append(f"{horas} hora{'s' if horas != 1 else ''}")
    if minutos > 0 and dias == 0:  # Solo mostrar minutos si no hay días
        partes.append(f"{minutos} minuto{'s' if minutos != 1 else ''}")
    if not partes:  # Si todo es 0, mostrar segundos
        partes.append(f"{segundos} segundo{'s' if segundos != 1 else ''}")

    return " ".join(partes)


def comparar_snapshots(
    portfolio_actual: List[Dict[str, Any]],
    snapshot_anterior: Dict[str, Any],
    timestamp_actual: int
) -> Dict[str, Any]:
    """
    Compara el portfolio actual con el snapshot anterior y genera un reporte de cambios.

    Args:
        portfolio_actual: Lista de diccionarios con los datos actuales del portfolio
                         (incluyendo peso_portfolio_pct).
        snapshot_anterior: Diccionario con 'timestamp' y 'portfolio' del snapshot anterior
                          (como lo devuelve obtener_ultimo_snapshot).
        timestamp_actual: Timestamp Unix actual.

    Returns:
        Diccionario con:
        - timestamp_anterior: int
        - timestamp_actual: int
        - tiempo_transcurrido: str
        - valor_total: dict con anterior, actual, cambio_eur, cambio_porcentaje
        - por_cripto: lista de cambios por cada cripto
        - nuevas_posiciones: lista de cryptos nuevas
        - posiciones_cerradas: lista de cryptos que ya no están
    """
    if not snapshot_anterior:
        logger.info("No hay snapshot anterior para comparar.")
        return None

    timestamp_anterior = snapshot_anterior['timestamp']
    portfolio_anterior = snapshot_anterior['portfolio']

    # Crear diccionarios indexados por símbolo para acceso rápido
    anterior_dict = {c['simbolo']: c for c in portfolio_anterior}
    actual_dict = {c['simbolo']: c for c in portfolio_actual}

    # Calcular valores totales
    valor_total_anterior = sum(c['valor_actual_inversion'] for c in portfolio_anterior)
    valor_total_actual = sum(c['valor_actual_inversion'] for c in portfolio_actual)

    cambio_valor_total_eur = valor_total_actual - valor_total_anterior
    cambio_valor_total_pct = 0
    if valor_total_anterior > 0:
        cambio_valor_total_pct = (cambio_valor_total_eur / valor_total_anterior) * 100

    # Comparar cryptos existentes en ambos snapshots
    cambios_por_cripto = []

    for simbolo in actual_dict.keys():
        cripto_actual = actual_dict[simbolo]

        if simbolo in anterior_dict:
            cripto_anterior = anterior_dict[simbolo]

            # Calcular cambios
            cambio_valor_eur = cripto_actual['valor_actual_inversion'] - cripto_anterior['valor_actual_inversion']
            cambio_valor_pct = 0
            if cripto_anterior['valor_actual_inversion'] > 0:
                cambio_valor_pct = (cambio_valor_eur / cripto_anterior['valor_actual_inversion']) * 100

            cambio_precio_eur = cripto_actual['precio_actual'] - cripto_anterior['precio_actual']
            cambio_precio_pct = 0
            if cripto_anterior['precio_actual'] > 0:
                cambio_precio_pct = (cambio_precio_eur / cripto_anterior['precio_actual']) * 100

            cambio_rentabilidad_pct = cripto_actual['rentabilidad_porcentaje'] - cripto_anterior['rentabilidad_porcentaje']
            # Cambio en peso actual (exposición variable al mercado)
            cambio_peso_actual_pct = cripto_actual['peso_actual_pct'] - cripto_anterior['peso_actual_pct']

            cambios_por_cripto.append({
                'cripto': simbolo,
                'valor_anterior': round(cripto_anterior['valor_actual_inversion'], 2),
                'valor_actual': round(cripto_actual['valor_actual_inversion'], 2),
                'cambio_valor_eur': round(cambio_valor_eur, 2),
                'cambio_valor_pct': round(cambio_valor_pct, 2),
                'precio_anterior': round(cripto_anterior['precio_actual'], 2),
                'precio_actual': round(cripto_actual['precio_actual'], 2),
                'cambio_precio_eur': round(cambio_precio_eur, 2),
                'cambio_precio_pct': round(cambio_precio_pct, 2),
                'cambio_rentabilidad_pct': round(cambio_rentabilidad_pct, 2),
                'cambio_peso_pct': round(cambio_peso_actual_pct, 2)
            })

    # Detectar nuevas posiciones
    nuevas_posiciones = []
    for simbolo in actual_dict.keys():
        if simbolo not in anterior_dict:
            nuevas_posiciones.append({
                'cripto': simbolo,
                'valor_actual': round(actual_dict[simbolo]['valor_actual_inversion'], 2),
                'precio_actual': round(actual_dict[simbolo]['precio_actual'], 2),
                'peso_actual_pct': round(actual_dict[simbolo]['peso_actual_pct'], 2)
            })

    # Detectar posiciones cerradas
    posiciones_cerradas = []
    for simbolo in anterior_dict.keys():
        if simbolo not in actual_dict:
            posiciones_cerradas.append({
                'cripto': simbolo,
                'valor_anterior': round(anterior_dict[simbolo]['valor_actual_inversion'], 2),
                'precio_anterior': round(anterior_dict[simbolo]['precio_actual'], 2)
            })

    # Construir resultado
    resultado = {
        'timestamp_anterior': timestamp_anterior,
        'timestamp_actual': timestamp_actual,
        'tiempo_transcurrido': formatear_tiempo_transcurrido(timestamp_anterior, timestamp_actual),
        'valor_total': {
            'anterior': round(valor_total_anterior, 2),
            'actual': round(valor_total_actual, 2),
            'cambio_eur': round(cambio_valor_total_eur, 2),
            'cambio_porcentaje': round(cambio_valor_total_pct, 2)
        },
        'por_cripto': cambios_por_cripto,
        'nuevas_posiciones': nuevas_posiciones,
        'posiciones_cerradas': posiciones_cerradas
    }

    logger.info(f"Comparación de snapshots completada. Tiempo transcurrido: {resultado['tiempo_transcurrido']}, "
                f"Cambio total: {resultado['valor_total']['cambio_eur']}€ ({resultado['valor_total']['cambio_porcentaje']}%)")

    return resultado


# Función auxiliar para testing/debugging
if __name__ == "__main__":
    import time
    import json

    # Datos de ejemplo
    timestamp_anterior = int(time.time()) - 7200  # Hace 2 horas
    timestamp_actual = int(time.time())

    snapshot_anterior = {
        'timestamp': timestamp_anterior,
        'portfolio': [
            {
                'simbolo': 'BTC',
                'cantidad_actual': 0.00423910,
                'precio_actual': 76456.91,
                'valor_actual_inversion': 324.11,
                'coste_total_inversion': 373.38,
                'rentabilidad_porcentaje': -13.20,
                'ganancia_perdida_abs': -49.27,
                'peso_portfolio_pct': 45.0
            },
            {
                'simbolo': 'ETH',
                'cantidad_actual': 0.03649996,
                'precio_actual': 2638.84,
                'valor_actual_inversion': 96.32,
                'coste_total_inversion': 65.38,
                'rentabilidad_porcentaje': 47.32,
                'ganancia_perdida_abs': 30.94,
                'peso_portfolio_pct': 30.0
            }
        ]
    }

    portfolio_actual = [
        {
            'simbolo': 'BTC',
            'cantidad_actual': 0.00423910,
            'precio_actual': 78000.00,  # Precio subió
            'valor_actual_inversion': 330.65,
            'coste_total_inversion': 373.38,
            'rentabilidad_porcentaje': -11.45,
            'ganancia_perdida_abs': -42.73,
            'peso_portfolio_pct': 46.5
        },
        {
            'simbolo': 'ETH',
            'cantidad_actual': 0.03649996,
            'precio_actual': 2700.00,  # Precio subió
            'valor_actual_inversion': 98.55,
            'coste_total_inversion': 65.38,
            'rentabilidad_porcentaje': 50.73,
            'ganancia_perdida_abs': 33.17,
            'peso_portfolio_pct': 28.0
        },
        {
            'simbolo': 'ADA',  # Nueva posición
            'cantidad_actual': 100.0,
            'precio_actual': 0.50,
            'valor_actual_inversion': 50.00,
            'coste_total_inversion': 50.00,
            'rentabilidad_porcentaje': 0.0,
            'ganancia_perdida_abs': 0.0,
            'peso_portfolio_pct': 25.5
        }
    ]

    resultado = comparar_snapshots(portfolio_actual, snapshot_anterior, timestamp_actual)

    if resultado:
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
