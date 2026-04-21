"""Rutas de carga de datos de mercado desde Binance."""

from fastapi import APIRouter, HTTPException
from config import FAVORITES_FILTER
from main import fetch_and_insert_data_last_30min

router = APIRouter()


@router.post("/run")
def run_script():
    """Carga datos de las criptomonedas favoritas de los últimos 30 min (trigger de Node-RED)."""
    try:
        fetch_and_insert_data_last_30min(FAVORITES_FILTER)
        return {"message": "✅🪨 Carga de datos de FAVORITOS se ha ejecutado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
