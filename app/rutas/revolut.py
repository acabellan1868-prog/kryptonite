"""
API REST para sincronización de recompensas de staking desde Revolut X.

Endpoints:
- GET /revolut/sincronizar — Sincroniza DOT y ADA del último mes
- GET /revolut/sincronizar?moneda=DOT&desde=YYYY-MM-DD — Sincroniza con parámetros custom
"""

import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException

import revolut_x

logger = logging.getLogger("kryptonite.rutas.revolut")
ruta = APIRouter()


@ruta.get("/revolut/sincronizar")
async def sincronizar_recompensas(
    moneda: str = None,
    desde: str = None,
    hasta: str = None
):
    """
    Sincroniza recompensas de staking desde Revolut X.

    Query params:
    - moneda: "DOT" o "ADA" (defecto: ambas)
    - desde: YYYY-MM-DD (defecto: 1ro del mes actual)
    - hasta: YYYY-MM-DD (defecto: hoy)

    Ejemplo:
    - GET /revolut/sincronizar
      → Sincroniza DOT y ADA del 1ro a hoy del mes actual

    - GET /revolut/sincronizar?moneda=DOT&desde=2026-05-01
      → Sincroniza DOT desde 2026-05-01 hasta hoy
    """

    # Parámetros por defecto
    if not desde:
        hoy = datetime.now()
        desde = hoy.replace(day=1).strftime("%Y-%m-%d")

    if not hasta:
        hasta = datetime.now().strftime("%Y-%m-%d")

    # Validar fechas
    try:
        fecha_desde = datetime.strptime(desde, "%Y-%m-%d")
        fecha_hasta = datetime.strptime(hasta, "%Y-%m-%d")
        if fecha_desde > fecha_hasta:
            raise ValueError("'desde' debe ser menor o igual a 'hasta'")
    except ValueError as e:
        raise HTTPException(400, f"Fechas inválidas: {e}")

    # Validar moneda
    monedas_a_sincronizar = []
    if moneda:
        if moneda.upper() not in ["DOT", "ADA"]:
            raise HTTPException(400, "Moneda debe ser 'DOT' o 'ADA'")
        monedas_a_sincronizar = [moneda.upper()]
    else:
        monedas_a_sincronizar = ["DOT", "ADA"]

    # Sincronizar
    resultados = {}
    try:
        for m in monedas_a_sincronizar:
            logger.info(f"Sincronizando {m} recompensas ({desde} a {hasta})")
            resultado = await revolut_x.sincronizar_recompensas(m, desde, hasta)
            resultados[m] = resultado
    except Exception as e:
        logger.error(f"Error durante sincronización: {e}")
        raise HTTPException(500, f"Error en sincronización: {e}")

    return {
        "status": "ok",
        "periodo": {
            "desde": desde,
            "hasta": hasta,
        },
        "resultados": resultados,
        "timestamp": datetime.now().isoformat(),
    }


@ruta.get("/revolut/recompensas")
async def obtener_recompensas_importadas(
    moneda: str = None,
    limite: int = 100,
    desde: str = None
):
    """
    Devuelve las recompensas importadas desde Revolut X.

    Query params:
    - moneda: "DOT", "ADA" o ambas (defecto: ambas)
    - limite: máximo de registros (defecto: 100)
    - desde: YYYY-MM-DD para filtrar por fecha mínima (defecto: sin filtro)

    Útil para verificación y comparación con la app de Revolut X.
    """
    try:
        import bd

        # Construir WHERE clause
        where = ["origen = 'Revolut' AND tipo = 'Recompensa'"]
        parametros = []

        if moneda:
            monedas = moneda.upper().split(",")
            placeholders = ",".join(["?" for _ in monedas])
            where.append(f"crypto IN ({placeholders})")
            parametros.extend(monedas)

        if desde:
            where.append("fecha >= ?")
            parametros.append(desde)

        where_clause = " WHERE " + " AND ".join(where)

        # Obtener recompensas ordenadas por fecha desc
        sql = f"""
            SELECT
                id, fecha, crypto, cantidad, descripcion, notas,
                precio_compra, precio_actual
            FROM operaciones
            {where_clause}
            ORDER BY fecha DESC
            LIMIT ?
        """
        parametros.append(limite)

        recompensas = bd.consultar_todos(sql, tuple(parametros))

        # Calcular totales por moneda
        sql_totales = f"""
            SELECT crypto, COUNT(*) as cantidad, SUM(cantidad) as importe
            FROM operaciones
            {where_clause.replace(' LIMIT ?', '')}
            GROUP BY crypto
            ORDER BY crypto
        """
        totales = bd.consultar_todos(sql_totales, tuple(parametros[:-1]))

        return {
            "status": "ok",
            "recompensas": [
                {
                    "id": r["id"],
                    "fecha": r["fecha"],
                    "moneda": r["crypto"],
                    "cantidad": float(r["cantidad"]),
                    "descripcion": r["descripcion"],
                    "notas": r["notas"],
                }
                for r in recompensas
            ],
            "resumen": {
                "total_registros": len(recompensas),
                "por_moneda": [
                    {
                        "moneda": t["crypto"],
                        "cantidad_transacciones": t["cantidad"],
                        "importe_total": float(t["importe"]) if t["importe"] else 0.0,
                    }
                    for t in totales
                ]
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error al obtener recompensas: {e}")
        raise HTTPException(500, f"Error: {e}")


@ruta.get("/revolut/estado")
async def estado_sincronizacion():
    """
    Devuelve el estado de las sincronizaciones realizadas.

    Información:
    - Última sincronización por moneda
    - Total de recompensas importadas
    - Próxima sincronización automática (si está configurada en Node-RED)
    """
    try:
        import bd

        # Contar recompensas por origen/moneda
        recompensas = bd.consultar_todos(
            """
            SELECT crypto, COUNT(*) as cantidad, SUM(cantidad) as importe
            FROM operaciones
            WHERE origen = 'Revolut' AND tipo = 'Recompensa'
            GROUP BY crypto
            ORDER BY crypto
            """
        )

        # Última sincronización
        ultima = bd.consultar_uno(
            """
            SELECT MAX(fecha) as ultima_sincronizacion
            FROM operaciones
            WHERE origen = 'Revolut' AND tipo = 'Recompensa'
            """
        )

        return {
            "status": "ok",
            "recompensas_por_moneda": [
                {
                    "moneda": r["crypto"],
                    "cantidad_transacciones": r["cantidad"],
                    "importe_total": float(r["importe"]) if r["importe"] else 0.0,
                }
                for r in recompensas
            ],
            "ultima_sincronizacion": ultima["ultima_sincronizacion"] if ultima else None,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error al obtener estado: {e}")
        raise HTTPException(500, f"Error al obtener estado: {e}")


@ruta.get("/revolut/diagnostico")
async def diagnostico_api():
    """
    Prueba varios endpoints de Revolut X y devuelve las respuestas crudas.

    Útil para explorar qué endpoints existen y qué datos devuelven.
    """
    import revolut_x

    candidatos = ["/balances", "/account/balances", "/account", "/accounts"]
    resultados = {}
    for path in candidatos:
        resultados[path] = await revolut_x._hacer_request("GET", path)

    return {
        "status": "ok",
        "respuestas": resultados,
        "timestamp": datetime.now().isoformat(),
    }


@ruta.get("/operaciones/contar")
async def contar_operaciones(
    moneda: str = None,
    origen: str = None,
    tipo: str = None
):
    """
    Devuelve el número total de operaciones en la BD con filtros opcionales.

    Query params:
    - moneda: filtrar por criptomoneda (ej: "DOT", "ADA")
    - origen: filtrar por origen (ej: "Revolut")
    - tipo: filtrar por tipo (ej: "Recompensa", "Compra", "Venta")

    Útil para verificar si el portfolio ha crecido por nuevas recompensas.

    Ejemplos:
    - GET /operaciones/contar
      → Total de operaciones en la BD

    - GET /operaciones/contar?origen=Revolut&tipo=Recompensa
      → Total de recompensas importadas desde Revolut

    - GET /operaciones/contar?moneda=DOT
      → Total de operaciones de DOT
    """
    try:
        import bd

        # Construir consulta SQL con filtros opcionales
        where = []
        parametros = []

        if moneda:
            where.append("crypto = ?")
            parametros.append(moneda.upper())

        if origen:
            where.append("origen = ?")
            parametros.append(origen)

        if tipo:
            where.append("tipo = ?")
            parametros.append(tipo)

        where_clause = ""
        if where:
            where_clause = " WHERE " + " AND ".join(where)

        # Contar total
        sql_total = f"SELECT COUNT(*) as total FROM operaciones{where_clause}"
        resultado_total = bd.consultar_uno(sql_total, tuple(parametros))
        total = resultado_total["total"] if resultado_total else 0

        # Contar por moneda si no hay filtro de moneda
        sql_por_moneda = f"""
            SELECT crypto, COUNT(*) as cantidad
            FROM operaciones{where_clause}
            GROUP BY crypto
            ORDER BY crypto
        """
        por_moneda = bd.consultar_todos(sql_por_moneda, tuple(parametros))

        # Contar por tipo si no hay filtro de tipo
        sql_por_tipo = f"""
            SELECT tipo, COUNT(*) as cantidad
            FROM operaciones{where_clause}
            GROUP BY tipo
            ORDER BY tipo
        """
        por_tipo = bd.consultar_todos(sql_por_tipo, tuple(parametros))

        return {
            "status": "ok",
            "total": total,
            "filtros_aplicados": {
                "moneda": moneda,
                "origen": origen,
                "tipo": tipo,
            },
            "desglose_por_moneda": [
                {
                    "moneda": m["crypto"],
                    "cantidad": m["cantidad"]
                }
                for m in por_moneda
            ],
            "desglose_por_tipo": [
                {
                    "tipo": t["tipo"],
                    "cantidad": t["cantidad"]
                }
                for t in por_tipo
            ],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error al contar operaciones: {e}")
        raise HTTPException(500, f"Error: {e}")
