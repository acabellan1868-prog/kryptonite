# CEMENTERIO DE CÓDIGO

Ir almacenando partes de código que voy a dejar de usar, pero quiero conservarlo por si lo retomo en el futuro.

## Método de creación de tablas en kriptonite.db

Tenia un método para la creación de las tablas, pero las tablas las voy a crear a través de script o directamente con algún cliente de sqlite

```python

def create_tables():
    
    """
    Crea las tablas necesarias en la base de datos si no existen.

    Tablas creadas:
    - crypto_data: Almacena datos de precios y volúmenes de criptomonedas.
    - cryptos: Guarda información básica sobre las criptomonedas.
    - alerts: Contiene alertas configuradas para precios.
    - users: Tabla para almacenar información de usuarios.
    - inversiones: Guarda registros de inversiones realizadas.

    Esta función solo necesita ejecutarse una vez al inicio del programa.
    """
    try:
        logger.info("Conectando a la base de datos en %s", DB_PATH)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
    
        logger.info("Creando tablas si no existen...")
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS crypto_data (
            timestamp INTEGER,
            symbol TEXT,
            price REAL,
            volume REAL,
            market_cap REAL
        );
    
        CREATE TABLE IF NOT EXISTS cryptos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE,
            name TEXT,
            slug TEXT
        );
    
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crypto_id INTEGER,
            trigger_price REAL,
            alert_type TEXT,
            enabled INTEGER
        );
    
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT
        );
    
        CREATE TABLE IF NOT EXISTS inversiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_compra DATETIME,
            simbolo TEXT,
            cantidad REAL,
            precio_compra REAL,
            comision REAL,
            valor_usd REAL,
            fecha_venta DATETIME,
            precio_venta REAL,
            ganancia_perdida REAL,
            tipo_inversion TEXT
        );
        """)
    
        conn.commit()
        conn.close()
        logger.info("✅ Tablas creadas correctamente.")
    except Exception as e:
        logger.error("❌ Error al crear las tablas: %s", e)

```


## Primera versión de get_crypto_data

```python
def get_crypto_data(symbol):
    try:
        logger.info(f"get_crypto_data: Obteniendo datos de {symbol}.")
        ticker = binance_client.fetch_ticker(symbol + '/EUR')  # Usamos EUR como referencia
        price = ticker['last']  # Último precio
        volume = ticker['baseVolume']  # Volumen de la base
        market_cap = ticker['quoteVolume'] * price  # Market Cap aproximado
        return price, volume, market_cap
    except Exception as e:
        print(f"Error obteniendo datos para {symbol}: {e}")
        logger.error(f"Error obteniendo datos para {symbol}: {e}")
        return None, None, None
```

## get_data_from_binance

```python
def get_data_from_binance(symbol):
    """
    Obtiene los datos en tiempo real de Binance.

    Args:
        symbol (str): Símbolo de la criptomoneda (ej. BTC).

    Returns:
        tuple: Último precio, volumen y capitalización de mercado.
    """
    try:
        ticker = binance_client.fetch_ticker(f"{symbol}/{DEFAULT_CURRENCY}")
        last_price = ticker['last']
        last_volume = ticker['baseVolume']
        last_market_cap =  ticker['quoteVolume'] * last_price  # Market Cap aproximado

        logger.info(f"Binance {symbol} - Precio: {last_price}, Volumen: {last_volume}")
        return last_price, last_volume, last_market_cap

    except Exception as e:
        logger.error(f"Error obteniendo datos de Binance para {symbol}: {e}")
        return None, None, None
```

### fetch_and_insert_data_last_30min

```python

def fetch_and_insert_data_last_30min(filter_by=None):
    """
    Obtiene los datos de las criptomonedas para los últimos 30 minutos (en intervalos de 5 minutos)
    y los inserta en la base de datos.

    @param filter_by: Opcional, puede ser:
                      - "favorites" -> Solo criptos marcadas como favoritas.
                      - "portfolio" -> Solo criptos en portfolio (que también son favoritas).
                      - None -> Todas las criptos.

    El flujo de trabajo es el siguiente:
    1. Obtener la hora actual.
    2. Calcular el rango de tiempo de los últimos 30 minutos.
    3. Consultar los datos de las criptomonedas para ese rango de tiempo.
    4. Insertar los datos obtenidos en la base de datos.

    Se asume que la función `get_crypto_data()` (definida en otro archivo) se usa para obtener los datos
    de cada criptomoneda en un intervalo de 5 minutos dentro del rango de los últimos 30 minutos.

    Pasos detallados:
    - Se calcula el rango de los últimos 30 minutos usando `datetime.now()` y `timedelta`.
    - Para cada criptomoneda, se obtiene el precio, volumen y capitalización de mercado en intervalos de 5 minutos.
    - Los datos obtenidos se insertan en la tabla `crypto_data` de la base de datos.
    """
    # Obtener la hora actual
    now = datetime.now()

    # Obtener el rango de los últimos 30 minutos
    end_time = now
    start_time = now - timedelta(minutes=30)

    # Lista de criptomonedas a consultar según el filtro
    cryptos = get_cryptos_from_db(filter_by)

    # Crear una lista para almacenar los datos
    data = []

    # Consultar los datos cada 5 minutos entre el rango de 30 minutos
    current_time = start_time
    while current_time <= end_time:
        for crypto in cryptos:
            price, volume, market_cap, moving_average = get_crypto_data(crypto['symbol'])  # Cambiar crypto a dict
            if price is not None and volume is not None and market_cap is not None:
                data.append({
                    'timestamp': int(current_time.timestamp()),
                    'symbol': crypto['symbol'],  # Usar 'symbol' del diccionario
                    'close': price,
                    'volume': volume,
                    'market_cap': market_cap
                })
        # Incrementar el tiempo en 5 minutos
        current_time += timedelta(minutes=5)

    # Si hay datos, insertar en la base de datos
    if data:
        df = pd.DataFrame(data)
        insert_crypto_data(df)
        logger.info(f"Datos de los últimos 30 minutos insertados en la base de datos.")
    else:
        logger.warning("No se encontraron datos para los últimos 30 minutos.")

```

### Recuperar datos perdidos de un periodo para una moneda

Esto se ha ejecutado en una celda de jupyter, paro es fácil de implementar en un script


```python
import sys
import os
sys.path.append(os.path.abspath('/home/jovyan/work/kryptonite/src')) #absolute path, replace with yours.
from database import insert_historico_crypto_data
from datetime import datetime

symbol = "SHIB"
start_datetime = datetime(2025, 3, 6, 3, 42, 0)
end_datetime = datetime(2025, 3, 6, 7, 25, 0) # año mes dia hora minuto segundo

print(f"Fecha de inicio: {start_datetime}.")
print(f"Fecha de fin {end_datetime}.")

success = insert_historico_crypto_data(symbol, start_datetime, end_datetime, timeframe='1m')

if success:
    print(f"Datos de {symbol} insertados exitosamente.")
else:
    print(f"Error al insertar datos de {symbol}.")
```

# SQL

Trozos de script que puede ser interesante tenerlos guardados para reutilizarlos

### **sqlite**: Elimina los registros que tienen el mismo timestamp y se quedan con el primero que aparezca

```sql
DELETE FROM crypto_data
WHERE ROWID NOT IN (
    SELECT MIN(ROWID) 
    FROM crypto_data 
    GROUP BY timestamp, symbol
);
```

### **sqlite**: Consulta donde se formatea el timestamp

```sql
SELECT datetime(timestamp, 'unixepoch') AS readable_timestamp,
symbol,
price,
volume,
market_cap
FROM crypto_data;
```

### SQL Elimina los milisegundos del campo timestampo de crypto_data

```sql
UPDATE crypto_data
SET timestamp = timestamp / 1000
WHERE timestamp > 9999999999;
```

### SQL Consulta que devuelve la varaiación entre carga de datos consecutivas

Es decir, devuelve la diferencia en %, entre una lectura y la consecutiva

```sql
SELECT 
    timestamp,
    datetime(timestamp, 'unixepoch', 'localtime') AS fecha_hora, 
    symbol, 
    price AS precio_actual, 
    LAG(price) OVER (PARTITION BY symbol ORDER BY timestamp) AS precio_anterior,
    CASE 
        WHEN LAG(price) OVER (PARTITION BY symbol ORDER BY timestamp) IS NOT NULL 
        THEN ROUND(
            ((price - LAG(price) OVER (PARTITION BY symbol ORDER BY timestamp)) 
            / LAG(price) OVER (PARTITION BY symbol ORDER BY timestamp)) * 100, 2)
        ELSE NULL 
    END AS variacion_porcentual
FROM crypto_data
ORDER BY symbol, variacion_porcentual;
```

Esta es más fina que la anterior y lo hace cada 5min. Pero se puede cambiar el tiempo del intervalo.

```sql
WITH Intervalos5Min AS (
    SELECT
        symbol,
        price,
        timestamp,
        -- Redondeamos el timestamp al inicio de cada intervalo de 5 minutos
        (timestamp / 300) * 300 AS timestamp_5min,
        ROW_NUMBER() OVER (PARTITION BY symbol, (timestamp / 300) ORDER BY timestamp) AS rn
    FROM crypto_data
    WHERE symbol = 'BTC'
)
SELECT 
    c1.timestamp_5min, 
    -- Hora de inicio del intervalo de 5 minutos
    datetime(c1.timestamp_5min, 'unixepoch', 'localtime') AS inicio_intervalo, 
    -- Hora de fin del intervalo de 5 minutos (sumamos 5 minutos)
    datetime(c1.timestamp_5min + 300, 'unixepoch', 'localtime') AS fin_intervalo, 
    c1.symbol, 
    c1.price AS precio_actual, 
    c2.price AS precio_anterior, 
    ROUND(((c1.price - c2.price) / c2.price) * 100, 2) AS variacion_porcentual
FROM Intervalos5Min c1
JOIN Intervalos5Min c2 
    ON c1.symbol = c2.symbol 
    AND c1.timestamp_5min = c2.timestamp_5min + 300  -- Comparamos bloques de 5 minutos
    AND c1.rn = 1  -- Solo tomamos el primer registro de cada intervalo de 5 minutos
    AND c2.rn = 1  -- Solo tomamos el primer registro de cada intervalo de 5 minutos
ORDER BY variacion_porcentual DESC;
```


### SQL Borra entradas anteriores a una fecha y consulta numero de registros anteriores a una fecha

CONSULTA

```sql
SELECT COUNT(*) 
FROM crypto_data 
WHERE timestamp < strftime('%s', '2025-03-01 00:00:00');
```


BORRA 

```sql
DELETE FROM crypto_data
WHERE timestamp < strftime('%s', '2025-03-01 00:00:00');
```

### SQL Devuelve primera y ultima fecha para una moneda

```sql
SELECT 
    symbol, 
    COUNT(*) AS total_registros,
    MIN(timestamp) AS min_timestamp, 
    datetime(MIN(timestamp), 'unixepoch', 'localtime') AS min_fecha,
    MAX(timestamp) AS max_timestamp, 
    datetime(MAX(timestamp), 'unixepoch', 'localtime') AS max_fecha
FROM crypto_data
WHERE symbol = 'BTC';
```


### CLASE CriptoEnCartera

Clase CriptoEnCartera, pero calculando el precio actual


```python

# src/modelos.py

from dataclasses import dataclass, field
import math
# Nuevas importaciones necesarias:
from binance_data import get_crypto_data
from config import logger

@dataclass
class CriptoEnCartera:
    simbolo: str
    cantidad_total: float
    coste_total_inversion: float
    # Este campo ya no es un parámetro de __init__ y no se muestra en repr por defecto.
    # Almacenará el precio actual una vez obtenido.
    _precio_actual_cache: float | None = field(default=None, init=False, repr=False)

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
                    logger.warning(f"No se pudo obtener el precio actual para {self.simbolo} desde la API. Usando 0.0 como fallback.")
            except Exception as e:
                self._precio_actual_cache = 0.0
                logger.error(f"Excepción al obtener precio para {self.simbolo}: {e}. Usando 0.0 como fallback.")
        return self._precio_actual_cache

    def refrescar_precio_actual(self) -> None:
        """
        Fuerza la actualización del precio actual desde la API, invalidando la caché.
        La próxima vez que se acceda a `self.precio_actual`, se volverá a consultar la API.
        """
        logger.info(f"Refrescando precio_actual para {self.simbolo} (invalidando caché).")
        self._precio_actual_cache = None
        # Opcionalmente, podrías forzar la carga aquí mismo:
        # _ = self.precio_actual

    @property
    def precio_medio_compra(self) -> float:
        """Precio medio de compra por unidad."""
        if self.cantidad_total > 0:
            return self.coste_total_inversion / self.cantidad_total
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
        if self.cantidad_total <= 0:
            return 0.0

        # Usa self.valor_actual_inversion, que a su vez usa la propiedad self.precio_actual
        current_value = self.valor_actual_inversion

        if self.coste_total_inversion > 0:
            return ((current_value - self.coste_total_inversion) / self.coste_total_inversion) * 100
        elif self.coste_total_inversion == 0:
            if current_value > 0:
                return math.inf
            else:
                return 0.0
        else:
            return 0.0

    def a_dict(self) -> dict:
        """
        Devuelve una representación en diccionario del objeto, lista para enviar como JSON.
        Incluye campos base y derivados (calculados mediante propiedades).
        """
        return {
            "simbolo": self.simbolo,
            "cantidad_total": self.cantidad_total,
            "coste_total_inversion": self.coste_total_inversion,
            "precio_actual": self.precio_actual, # Llamará a la propiedad
            "precio_medio_compra": self.precio_medio_compra,
            "valor_actual_inversion": self.valor_actual_inversion,
            "rentabilidad": self.rentabilidad,
        }


```