# src/modelos.py

from dataclasses import dataclass, field
import math
# Nuevas importaciones necesarias:
from binance_data import get_crypto_data
from config import logger
# Importar la función para calcular posición desde la base de datos
from database import calcular_posicion_actual

@dataclass
class CriptoEnCartera:
    simbolo: str
    # Cachés internas para los datos fundamentales
    _precio_actual_cache: float | None = field(default=None, init=False, repr=False)
    _cantidad_total_cache: float | None = field(default=None, init=False, repr=False)
    _cantidad_inversion_cache: float | None = field(default=None, init=False, repr=False)
    _cantidad_recompensas_cache: float | None = field(default=None, init=False, repr=False)
    _cantidad_recepciones_cache: float | None = field(default=None, init=False, repr=False)
    _coste_total_inversion_cache: float | None = field(default=None, init=False, repr=False)

    def _cargar_datos_operaciones_si_necesario(self):
        """
        Método interno para cargar cantidad y coste desde la BD si aún no están cacheados.
        Llama a calcular_posicion_actual y puebla las cachés correspondientes.
        """
        if self._cantidad_total_cache is None or self._coste_total_inversion_cache is None:
            logger.info(f"Cachés de operaciones vacías para {self.simbolo}. Obteniendo de BD...")
            try:
                datos_posicion = calcular_posicion_actual(self.simbolo)
                self._cantidad_inversion_cache = datos_posicion.get('cantidad_actual', 0.0)
                self._cantidad_recompensas_cache = datos_posicion.get('cantidad_recompensas', 0.0)
                self._cantidad_recepciones_cache = datos_posicion.get('cantidad_recepciones', 0.0)
                self._cantidad_total_cache = datos_posicion.get('cantidad_total', 0.0)
                self._coste_total_inversion_cache = datos_posicion.get('coste_total', 0.0)
                logger.info(
                    f"Datos de operaciones para {self.simbolo} obtenidos y cacheados: "
                    f"Inversión={self._cantidad_inversion_cache}, Recompensas={self._cantidad_recompensas_cache}, "
                    f"Recepciones={self._cantidad_recepciones_cache}, Total={self._cantidad_total_cache}, "
                    f"Coste={self._coste_total_inversion_cache}"
                )
            except Exception as e:
                self._cantidad_inversion_cache = 0.0
                self._cantidad_recompensas_cache = 0.0
                self._cantidad_recepciones_cache = 0.0
                self._cantidad_total_cache = 0.0
                self._coste_total_inversion_cache = 0.0
                logger.error(
                    f"Excepción al obtener datos de operaciones para {self.simbolo}: {e}. "
                    f"Usando 0.0 como fallback."
                )

    @property
    def cantidad_total(self) -> float:
        """
        Cantidad total actual de la criptomoneda (inversión + recompensas + recepciones).
        Obtenida de la base de datos (tabla operaciones).
        Se cachea después de la primera lectura.
        """
        self._cargar_datos_operaciones_si_necesario()
        return self._cantidad_total_cache if self._cantidad_total_cache is not None else 0.0

    @property
    def cantidad_inversion(self) -> float:
        """
        Cantidad de criptomoneda obtenida únicamente por compras (descontando ventas/envíos).
        No incluye recompensas ni recepciones.
        Se cachea después de la primera lectura.
        """
        self._cargar_datos_operaciones_si_necesario()
        return self._cantidad_inversion_cache if self._cantidad_inversion_cache is not None else 0.0

    @property
    def cantidad_recompensas(self) -> float:
        """
        Cantidad de criptomoneda obtenida por recompensas de staking, airdrops, etc.
        Se cachea después de la primera lectura.
        """
        self._cargar_datos_operaciones_si_necesario()
        return self._cantidad_recompensas_cache if self._cantidad_recompensas_cache is not None else 0.0

    @property
    def cantidad_recepciones(self) -> float:
        """
        Cantidad de criptomoneda obtenida por recepciones (transferencias entrantes).
        Se cachea después de la primera lectura.
        """
        self._cargar_datos_operaciones_si_necesario()
        return self._cantidad_recepciones_cache if self._cantidad_recepciones_cache is not None else 0.0

    @property
    def coste_total_inversion(self) -> float:
        """
        Coste total neto de la inversión en la criptomoneda, obtenido de la base de datos (tabla operaciones).
        Se cachea después de la primera lectura.
        """
        self._cargar_datos_operaciones_si_necesario()
        return self._coste_total_inversion_cache if self._coste_total_inversion_cache is not None else 0.0

    @property
    def precio_actual(self) -> float:
        """
        Precio actual de la criptomoneda.
        Se obtiene de la API (Binance) la primera vez que se accede y se guarda en caché.
        Si no se puede obtener, se devuelve 0.0 y se registra un aviso.
        Utiliza timeframe '1m' y limit 1 para obtener el precio más reciente.
        """
        if self._precio_actual_cache is None:
            logger.info(f"Caché de precio_actual vacía para {self.simbolo}. Obteniendo de API...")
            try:
                # get_crypto_data devuelve (price, volume, market_cap, moving_average)
                # Usamos '1m' y limit 1 para el precio más reciente.
                price, _, _, _ = get_crypto_data(self.simbolo, timeframe='1m', limit=1)
                if price is not None:
                    self._precio_actual_cache = price
                    logger.info(f"Precio actual para {self.simbolo} obtenido y cacheado: {self._precio_actual_cache}")
                else:
                    self._precio_actual_cache = 0.0
                    logger.warning(f"No se pudo obtener el precio actual para {self.simbolo} desde API. Usando 0.0.")
            except Exception as e:
                self._precio_actual_cache = 0.0
                logger.error(f"Excepción al obtener precio para {self.simbolo}: {e}. Usando 0.0.")
        return self._precio_actual_cache if self._precio_actual_cache is not None else 0.0

    def refrescar_precio_actual(self) -> None:
        """
        Fuerza la actualización del precio actual desde la API.
        """
        logger.info(f"Refrescando precio_actual para {self.simbolo} (invalidando caché).")
        self._precio_actual_cache = None

    def refrescar_datos_operaciones(self) -> None:
        """Fuerza la actualización de cantidad y coste desde la base de datos."""
        logger.info(f"Refrescando datos de operaciones para {self.simbolo} (invalidando cachés).")
        self._cantidad_total_cache = None
        self._cantidad_inversion_cache = None
        self._cantidad_recompensas_cache = None
        self._cantidad_recepciones_cache = None
        self._coste_total_inversion_cache = None
        # La próxima vez que se acceda a las propiedades, se recargarán.

    def refrescar_todo(self) -> None:
        """Fuerza la actualización de todos los datos cacheados (precio y operaciones)."""
        logger.info(f"Refrescando todos los datos cacheados para {self.simbolo}.")
        self.refrescar_precio_actual()
        self.refrescar_datos_operaciones()

    @property
    def precio_medio_compra(self) -> float:
        """
        Precio medio de compra por unidad.
        Se calcula SOLO sobre la cantidad de inversión (compras/ventas),
        NO incluye recompensas ni recepciones para mantener la integridad del precio medio.
        """
        # Usa cantidad_inversion en lugar de cantidad_total
        cantidad = self.cantidad_inversion
        coste = self.coste_total_inversion
        if cantidad > 0:
            return coste / cantidad
        return 0.0

    @property
    def valor_actual_inversion(self) -> float:
        """Valor actual total de la inversión para esta criptomoneda."""
        # Ahora usa la propiedad self.precio_actual, que gestiona la obtención y caché.
        return self.precio_actual * self.cantidad_total

    @property
    def rentabilidad(self) -> float:
        """
        Rentabilidad de la inversión en porcentaje.
        Devuelve math.inf si el coste fue cero y el valor actual es positivo.
        """
        cantidad = self.cantidad_total # Accede a la propiedad
        if cantidad <= 0:
            return 0.0

        # Usa self.valor_actual_inversion, que a su vez usa la propiedad self.precio_actual
        current_value = self.valor_actual_inversion # Usa propiedades
        coste_inversion = self.coste_total_inversion # Accede a la propiedad

        if coste_inversion > 0:
            return ((current_value - coste_inversion) / coste_inversion) * 100
        elif coste_inversion == 0:
            return math.inf if current_value > 0 else 0.0
        else: # Coste negativo
            return 0.0

    def a_dict(self) -> dict:
        """
        Devuelve una representación en diccionario del objeto, lista para enviar como JSON.
        Incluye campos base y derivados (calculados mediante propiedades).
        """
        return {
            "simbolo": self.simbolo,
            "cantidad_inversion": self.cantidad_inversion,
            "cantidad_recompensas": self.cantidad_recompensas,
            "cantidad_recepciones": self.cantidad_recepciones,
            "cantidad_total": self.cantidad_total,
            "coste_total_inversion": self.coste_total_inversion,
            "precio_actual": self.precio_actual,
            "precio_medio_compra": self.precio_medio_compra,
            "valor_actual_inversion": self.valor_actual_inversion,
            "rentabilidad": self.rentabilidad,
        }
