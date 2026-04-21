"""Rutas de análisis técnico: señales de trading y backtesting."""

from fastapi import APIRouter, HTTPException, Query
from config import logger
from analysis import obtener_senal_cambio_extremo
from backtesting import (
    run_backtest,
    obtener_senal_cambio_extremo_backtest,
    obtener_senal_cruce_medias_moviles_backtest,
)
from esquemas import BacktestRequest

router = APIRouter()

ESTRATEGIAS = {
    "obtener_senal_cambio_extremo": obtener_senal_cambio_extremo_backtest,
    "cruce_medias_moviles": obtener_senal_cruce_medias_moviles_backtest,
}


@router.get("/senal/cambio_extremo")
def obtener_senal_cambio_extremo_api(
    cripto: str = Query(..., description="Símbolo de la criptomoneda, ej. BTC"),
    intervalo_minutos: int = Query(15, description="Período en minutos (múltiplo de 5)"),
    umbral_porcentual: float = Query(1.0, description="Umbral % para considerar cambio extremo"),
    confirmar_con_volumen: bool = Query(False, description="Si True, requiere confirmación de volumen"),
    umbral_porcentual_volumen: float = Query(20.0, description="% mínimo de aumento de volumen"),
    num_ventanas_historicas_volumen: int = Query(3, description="Ventanas históricas para comparar volumen"),
):
    """
    Señal de trading por cambio porcentual extremo (reversión a la media).
    Detecta movimientos bruscos de precio y asume retorno al nivel normal.
    """
    if intervalo_minutos <= 0 or intervalo_minutos % 5 != 0:
        raise HTTPException(status_code=400, detail="'intervalo_minutos' debe ser un entero positivo y múltiplo de 5.")
    if umbral_porcentual <= 0:
        raise HTTPException(status_code=400, detail="'umbral_porcentual' debe ser un número positivo.")
    if confirmar_con_volumen and umbral_porcentual_volumen < 0:
        raise HTTPException(status_code=400, detail="'umbral_porcentual_volumen' debe ser positivo o cero.")

    try:
        datos = obtener_senal_cambio_extremo(
            cripto.upper(),
            intervalo_minutos,
            umbral_porcentual,
            confirmar_con_volumen,
            umbral_porcentual_volumen,
            intervalo_minutos,
            num_ventanas_historicas_volumen,
        )
        if datos["senal"] == "DATOS INSUFICIENTES":
            raise HTTPException(
                status_code=404,
                detail=f"No hay suficientes datos para {cripto} en el período de {intervalo_minutos} minutos.",
            )
        return datos
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener señal de cambio extremo para {cripto}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al calcular la señal de cambio extremo.")


@router.post("/backtest")
def backtest_strategy(datos: BacktestRequest):
    """Ejecuta un backtest de estrategia de trading sobre datos históricos."""
    funcion = ESTRATEGIAS.get(datos.strategy)
    if not funcion:
        raise HTTPException(status_code=400, detail=f"Estrategia '{datos.strategy}' no reconocida.")

    try:
        resultados = run_backtest(
            simbolo=datos.symbol,
            fecha_inicio_str=datos.start_date,
            fecha_fin_str=datos.end_date,
            capital_inicial=float(datos.initial_capital),
            funcion_estrategia=funcion,
            parametros_estrategia=datos.strategy_params,
        )
        return resultados
    except Exception as e:
        logger.error(f"Error durante el backtest: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno durante el backtest: {str(e)}")
