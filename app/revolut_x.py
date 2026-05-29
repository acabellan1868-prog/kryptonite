"""
Integración con Revolut X API — Importación de recompensas de staking.

Automatiza la captura de recompensas de DOT (Polkadot) y ADA (Cardano)
desde Revolut X hacia la tabla `operaciones` de Kryptonite.

Autenticación: Ed25519 con headers firmados en cada petición.
Límite de API: 7 días máximo por ventana (itera en semanas para histórico).
"""

import httpx
import logging
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from config import KRYPTO_REVOLUT_API_KEY, KRYPTO_REVOLUT_PRIVATE_KEY
import bd

logger = logging.getLogger("kryptonite.revolut_x")

# ── Constantes ─────────────────────────────────────────────────────────────
REVOLUT_X_API_BASE = "https://api.revolut.com/trading/api"
REVOLUT_X_TIMEOUT = 30
VENTANA_MAXIMA_DIAS = 7  # Límite de API: máx 7 días por petición
MONEDAS_STAKING = {"DOT", "ADA"}  # Monedas con recompensas de staking


# ── Firma Ed25519 ─────────────────────────────────────────────────────────

def _cargar_clave_privada() -> Optional[ed25519.Ed25519PrivateKey]:
    """Carga la clave privada Ed25519 desde config."""
    if not KRYPTO_REVOLUT_PRIVATE_KEY:
        logger.error("KRYPTO_REVOLUT_PRIVATE_KEY no configurada")
        return None

    try:
        clave_privada = serialization.load_pem_private_key(
            KRYPTO_REVOLUT_PRIVATE_KEY.encode(),
            password=None
        )
        if not isinstance(clave_privada, ed25519.Ed25519PrivateKey):
            logger.error("Clave privada no es Ed25519")
            return None
        return clave_privada
    except Exception as e:
        logger.error(f"Error al cargar clave privada: {e}")
        return None


def _generar_firma(mensaje: bytes, clave_privada: ed25519.Ed25519PrivateKey) -> str:
    """Genera firma Ed25519 en base64."""
    firma_bytes = clave_privada.sign(mensaje)
    return base64.b64encode(firma_bytes).decode("utf-8")


def _generar_headers_autenticados(metodo: str, ruta: str) -> Optional[Dict[str, str]]:
    """
    Genera headers autenticados con firma Ed25519 para Revolut X.

    Headers requeridos por Revolut X:
    - X-Revx-API-Key: clave pública
    - X-Revx-Timestamp: timestamp actual en ms
    - X-Revx-Signature: firma Ed25519 del mensaje
    """
    clave_privada = _cargar_clave_privada()
    if not clave_privada:
        print(f"❌ [REVOLUT_X] No se pudo cargar clave privada")
        return None
    if not KRYPTO_REVOLUT_API_KEY:
        print(f"❌ [REVOLUT_X] KRYPTO_REVOLUT_API_KEY no configurada")
        return None

    try:
        ahora_ms = int(datetime.utcnow().timestamp() * 1000)

        # Mensaje a firmar: METODO|RUTA|TIMESTAMP
        mensaje = f"{metodo}|{ruta}|{ahora_ms}".encode("utf-8")
        firma = _generar_firma(mensaje, clave_privada)

        headers = {
            "X-Revx-API-Key": KRYPTO_REVOLUT_API_KEY.strip(),
            "X-Revx-Timestamp": str(ahora_ms),
            "X-Revx-Signature": firma,
            "Content-Type": "application/json",
        }
        print(f"🔑 [REVOLUT_X] Headers generados para {metodo} {ruta}")
        return headers
    except Exception as e:
        print(f"❌ [REVOLUT_X] Error al generar headers: {e}")
        return None


# ── Cliente HTTP ───────────────────────────────────────────────────────────

async def _hacer_request(
    metodo: str,
    ruta: str,
    params: Optional[Dict[str, str]] = None
) -> Optional[Dict[str, Any]]:
    """
    Realiza petición HTTP autenticada a Revolut X.
    """
    headers = _generar_headers_autenticados(metodo, ruta)
    if not headers:
        print(f"❌ [REVOLUT_X] No se pudo generar headers autenticados")
        return None

    url = REVOLUT_X_API_BASE + ruta
    print(f"🌐 [REVOLUT_X] {metodo} {url} con params: {params}")

    try:
        async with httpx.AsyncClient(timeout=REVOLUT_X_TIMEOUT) as cliente:
            if metodo == "GET":
                respuesta = await cliente.get(url, headers=headers, params=params)
            elif metodo == "POST":
                respuesta = await cliente.post(url, headers=headers, json=params)
            else:
                print(f"❌ [REVOLUT_X] Método HTTP no soportado: {metodo}")
                return None

            print(f"📨 [REVOLUT_X] Status {respuesta.status_code} en {metodo} {url}")
            respuesta.raise_for_status()
            resultado = respuesta.json()
            print(f"✅ [REVOLUT_X] Respuesta OK: {resultado}")
            return resultado
    except httpx.HTTPStatusError as e:
        print(f"❌ [REVOLUT_X] Error HTTP {e.response.status_code} en {metodo} {url}")
        print(f"   Respuesta: {e.response.text}")
        return None
    except httpx.HTTPError as e:
        print(f"❌ [REVOLUT_X] Error de conexión en {metodo} {url}: {e}")
        return None
    except Exception as e:
        print(f"❌ [REVOLUT_X] Error inesperado: {type(e).__name__}: {e}")
        return None


# ── Obtención de datos ─────────────────────────────────────────────────────

async def obtener_recompensas(
    moneda: str,
    desde: str,  # YYYY-MM-DD
    hasta: str   # YYYY-MM-DD
) -> List[Dict[str, Any]]:
    """
    Obtiene recompensas de staking de una moneda en un rango de fechas.

    Itera en ventanas de 7 días (límite del API) y filtra por tipo "Reward".

    Args:
        moneda: "DOT" o "ADA"
        desde: fecha inicio (YYYY-MM-DD)
        hasta: fecha fin (YYYY-MM-DD)

    Returns:
        Lista de transacciones de tipo recompensa
    """
    if moneda not in MONEDAS_STAKING:
        logger.warning(f"Moneda {moneda} no soportada para staking")
        return []

    recompensas = []

    try:
        fecha_inicio = datetime.strptime(desde, "%Y-%m-%d")
        fecha_fin = datetime.strptime(hasta, "%Y-%m-%d")
    except ValueError as e:
        logger.error(f"Formato de fecha inválido: {e}")
        return []

    # Iterar en ventanas de 7 días
    ventana_actual = fecha_inicio
    while ventana_actual < fecha_fin:
        ventana_fin = min(ventana_actual + timedelta(days=VENTANA_MAXIMA_DIAS), fecha_fin)

        desde_str = ventana_actual.strftime("%Y-%m-%d")
        hasta_str = ventana_fin.strftime("%Y-%m-%d")

        print(f"📅 [REVOLUT_X] Obteniendo {moneda} recompensas: {desde_str} a {hasta_str}")

        # Consultar transacciones de esta ventana
        params = {
            "symbol": moneda,
            "type": "Reward",  # Solo recompensas
            "startDate": desde_str,
            "endDate": hasta_str,
        }

        resultado = await _hacer_request("GET", f"/trading/transactions", params)

        print(f"📡 [REVOLUT_X] Respuesta recibida: {resultado}")

        if resultado and "transactions" in resultado:
            recompensas.extend(resultado["transactions"])
            print(f"✅ [REVOLUT_X] {len(resultado['transactions'])} transacciones encontradas en ventana {desde_str}-{hasta_str}")
        elif resultado:
            print(f"⚠️  [REVOLUT_X] Respuesta sin 'transactions': {resultado}")
        else:
            print(f"❌ [REVOLUT_X] Sin respuesta o respuesta vacía")

        ventana_actual = ventana_fin + timedelta(days=1)

    return recompensas


async def obtener_trades(
    simbolo: str,
    desde: str,  # YYYY-MM-DD
    hasta: str   # YYYY-MM-DD
) -> List[Dict[str, Any]]:
    """
    Obtiene trades (operaciones de compra/venta) de un símbolo.

    Itera en ventanas de 7 días (límite del API).
    """
    trades = []

    try:
        fecha_inicio = datetime.strptime(desde, "%Y-%m-%d")
        fecha_fin = datetime.strptime(hasta, "%Y-%m-%d")
    except ValueError as e:
        logger.error(f"Formato de fecha inválido: {e}")
        return []

    ventana_actual = fecha_inicio
    while ventana_actual < fecha_fin:
        ventana_fin = min(ventana_actual + timedelta(days=VENTANA_MAXIMA_DIAS), fecha_fin)

        desde_str = ventana_actual.strftime("%Y-%m-%d")
        hasta_str = ventana_fin.strftime("%Y-%m-%d")

        logger.info(f"Obteniendo {simbolo} trades: {desde_str} a {hasta_str}")

        params = {
            "symbol": simbolo,
            "startDate": desde_str,
            "endDate": hasta_str,
        }

        resultado = await _hacer_request("GET", f"/trading/trades", params)

        if resultado and "trades" in resultado:
            trades.extend(resultado["trades"])
            logger.info(f"  → {len(resultado['trades'])} trades encontrados")

        ventana_actual = ventana_fin + timedelta(days=1)

    return trades


# ── Sincronización a BD ────────────────────────────────────────────────────

def _evitar_duplicados(transaction_id: str, origen: str = "Revolut") -> bool:
    """
    Verifica si una transacción ya existe en la BD.

    Busca por: origen='Revolut' + notas que contenga el transaction_id.
    """
    try:
        existe = bd.consultar_uno(
            """
            SELECT id FROM operaciones
            WHERE origen = ? AND notas LIKE ?
            LIMIT 1
            """,
            (origen, f"%{transaction_id}%")
        )
        return existe is not None
    except Exception as e:
        logger.error(f"Error al verificar duplicados: {e}")
        return False


async def sincronizar_recompensas(
    moneda: str,
    desde: str,  # YYYY-MM-DD
    hasta: Optional[str] = None  # Si es None, hasta hoy
) -> Dict[str, Any]:
    """
    Descarga recompensas de staking y las inserta en la tabla `operaciones`.

    Returns:
        {
            "moneda": "DOT",
            "desde": "2026-05-01",
            "hasta": "2026-05-28",
            "recompensas_encontradas": 15,
            "insertadas": 12,
            "duplicadas": 3,
            "errores": 0
        }
    """
    if not hasta:
        hasta = datetime.now().strftime("%Y-%m-%d")

    print(f"🔄 [REVOLUT_X] sincronizar_recompensas({moneda}, {desde}, {hasta})")
    recompensas = await obtener_recompensas(moneda, desde, hasta)
    print(f"📊 [REVOLUT_X] Encontradas {len(recompensas)} recompensas")

    resultado = {
        "moneda": moneda,
        "desde": desde,
        "hasta": hasta,
        "recompensas_encontradas": len(recompensas),
        "insertadas": 0,
        "duplicadas": 0,
        "errores": 0,
    }

    for recompensa in recompensas:
        try:
            transaction_id = recompensa.get("transactionId", "")

            # Verificar duplicados
            if _evitar_duplicados(transaction_id):
                resultado["duplicadas"] += 1
                logger.debug(f"Transacción duplicada ignorada: {transaction_id}")
                continue

            # Extraer datos
            importe = float(recompensa.get("amount", 0))
            fecha = recompensa.get("executedAt", "")
            nota = f"Recompensa {moneda} (Revolut) - TX:{transaction_id}"

            # Insertar en operaciones
            sql = """
                INSERT INTO operaciones (
                    fecha, tipo, crypto, cantidad, precio_compra,
                    precio_actual, descripcion, origen, notas
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            bd.ejecutar(sql, (
                fecha,                      # fecha
                "Recompensa",               # tipo
                moneda,                     # crypto
                importe,                    # cantidad
                1.0,                        # precio_compra (irrelevante para recompensas)
                1.0,                        # precio_actual
                f"Recompensa de staking",   # descripción
                "Revolut",                  # origen
                nota                        # notas (contiene transaction_id)
            ))

            resultado["insertadas"] += 1
            logger.info(f"Recompensa insertada: {moneda} {importe} ({transaction_id})")

        except Exception as e:
            resultado["errores"] += 1
            logger.error(f"Error al insertar recompensa: {e}")

    return resultado
