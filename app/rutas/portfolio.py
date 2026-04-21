"""Rutas de portfolio: valor, posiciones, operaciones y limpieza de datos."""

from fastapi import APIRouter, HTTPException, Query
from config import logger
from main import get_crypto_data
from analisis_rendimineto import calcular_rendimiento_portafolio_total, obtener_portafolio
from database import get_data_from_db, limpiar_crypto_data, insertar_operacion
from charts import generate_chart, generar_grafica_comparativa
from esquemas import NuevaOperacionRequest

router = APIRouter()


@router.get("/valor")
def obtener_valor(
    crypto: str = Query(..., description="Símbolo de la criptomoneda, ej. BTC"),
    timeframe: str = Query("1d", description="Intervalo de tiempo, ej. 1m, 1h, 1d"),
):
    """Precio actual, volumen y media móvil de una criptomoneda desde Binance."""
    symbol = crypto.upper()
    try:
        price, volume, market_cap, media_movil = get_crypto_data(symbol, timeframe, 1)
        if price is None:
            raise HTTPException(status_code=404, detail=f"No se encontraron datos para {crypto} en Binance")
        return {
            "symbol": symbol,
            "price": price,
            "volume": volume,
            "market_cap": market_cap,
            "media_movil": media_movil,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/grafica24h")
def get_chart(crypto: str = Query(None, description="Símbolo de la criptomoneda. Sin valor → comparativa del portfolio")):
    """Gráfica de precios 24h en base64. Sin parámetro devuelve comparativa del portfolio."""
    try:
        if not crypto:
            monedas = obtener_portafolio()
            chart_image = generar_grafica_comparativa(
                monedas,
                title="Comparación de Precios de " + ", ".join(monedas),
                returnBase64=True,
            )
            return {"chart": chart_image}

        data = get_data_from_db(crypto.upper(), window=1440)
        if data is None:
            raise HTTPException(status_code=404, detail="No se encontraron datos para la criptomoneda solicitada")

        chart_image = generate_chart(data, f"Gráfica de precios 24h de la 🪙 {crypto.upper()}")
        if chart_image is None:
            raise HTTPException(status_code=400, detail="La imagen no está disponible")
        return {"chart": chart_image}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portafolio")
def get_portafolio(analisis: str = Query("basico", description="'basico' o 'completo'")):
    """
    Rendimiento del portfolio.
    - basico: lista de criptos con rentabilidad (retrocompatible con Node-RED).
    - completo: añade análisis de riesgo, alertas de concentración y totales.
    """
    try:
        resultados = calcular_rendimiento_portafolio_total()
        if analisis.lower() == "completo":
            from portfolio_analyzer import analizar_portfolio_completo
            return analizar_portfolio_completo(resultados)
        return resultados
    except Exception as e:
        logger.error(f"Error en get_portafolio: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno al calcular el rendimiento del portfolio.")


@router.get("/limpiar")
def limpiar_tabla():
    """Elimina registros duplicados de la tabla crypto_data."""
    try:
        limpiar_crypto_data()
        return {"message": "Tabla crypto_data limpiada correctamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/nuevaOperacion", status_code=201)
def nueva_operacion(datos: NuevaOperacionRequest):
    """Inserta una nueva operación (compra, venta, recompensa…) en la BD."""
    try:
        id_operacion = insertar_operacion(
            timestamp=datos.timestamp,
            cripto=datos.cripto,
            moneda=datos.moneda,
            tipo=datos.tipo,
            cantidad=datos.cantidad,
            precio=datos.precio,
            valor_total=datos.valor_total,
            comision=datos.comision,
            origen=datos.origen,
        )
        return {"mensaje": "Operación insertada correctamente.", "id_operacion": id_operacion}
    except Exception as e:
        logger.error(f"Error al insertar nueva operación: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error al insertar la operación: {str(e)}")
