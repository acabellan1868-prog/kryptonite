"""
Módulo de acceso a la base de datos SQLite.

Proporciona funciones de alto nivel para consultas, inserciones y actualizaciones.
"""

import sqlite3
import logging
from typing import List, Dict, Any, Optional, Tuple
from app.config import KRYPTO_DB_PATH

logger = logging.getLogger("kryptonite.bd")


def _obtener_conexion() -> sqlite3.Connection:
    """Obtiene una conexión a la BD SQLite."""
    conexion = sqlite3.connect(KRYPTO_DB_PATH)
    conexion.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
    return conexion


def consultar_uno(sql: str, parametros: Tuple = ()) -> Optional[Dict[str, Any]]:
    """
    Ejecuta una consulta SELECT y devuelve un único registro.

    Args:
        sql: Consulta SQL
        parametros: Tupla de parámetros para la consulta

    Returns:
        Diccionario con el registro, o None si no hay resultados
    """
    try:
        conexion = _obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(sql, parametros)
        fila = cursor.fetchone()
        conexion.close()

        if fila:
            return dict(fila)
        return None
    except Exception as e:
        logger.error(f"Error en consultar_uno: {e}")
        return None


def consultar_todos(sql: str, parametros: Tuple = ()) -> List[Dict[str, Any]]:
    """
    Ejecuta una consulta SELECT y devuelve todos los registros.

    Args:
        sql: Consulta SQL
        parametros: Tupla de parámetros para la consulta

    Returns:
        Lista de diccionarios con los registros
    """
    try:
        conexion = _obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(sql, parametros)
        filas = cursor.fetchall()
        conexion.close()

        return [dict(fila) for fila in filas]
    except Exception as e:
        logger.error(f"Error en consultar_todos: {e}")
        return []


def ejecutar(sql: str, parametros: Tuple = ()) -> bool:
    """
    Ejecuta una sentencia SQL (INSERT, UPDATE, DELETE).

    Args:
        sql: Consulta SQL
        parametros: Tupla de parámetros para la consulta

    Returns:
        True si la operación fue exitosa, False en caso contrario
    """
    try:
        conexion = _obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(sql, parametros)
        conexion.commit()
        conexion.close()
        return True
    except Exception as e:
        logger.error(f"Error en ejecutar: {e}")
        return False
