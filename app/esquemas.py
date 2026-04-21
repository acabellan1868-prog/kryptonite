"""Esquemas Pydantic para validación de requests de la API."""

from pydantic import BaseModel, field_validator


TIPOS_OPERACION = {"Compra", "Venta", "Recompensa", "Recepción", "Envío"}


class BacktestRequest(BaseModel):
    """Parámetros para ejecutar un backtest de estrategia."""
    symbol: str
    start_date: str
    end_date: str
    initial_capital: float
    strategy: str = "obtener_senal_cambio_extremo"
    strategy_params: dict = {}


class NuevaOperacionRequest(BaseModel):
    """Datos de una nueva operación para insertar en la BD."""
    timestamp: int
    cripto: str
    moneda: str
    tipo: str
    cantidad: float
    precio: float
    valor_total: float
    comision: float
    origen: str

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, v: str) -> str:
        if v not in TIPOS_OPERACION:
            raise ValueError(f"Tipo no válido. Permitidos: {', '.join(TIPOS_OPERACION)}")
        return v


class PromptRequest(BaseModel):
    """Pregunta en lenguaje natural para el agente LangChain."""
    question: str
