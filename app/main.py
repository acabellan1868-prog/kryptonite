# main.py
import pandas as pd
import time
from database import get_cryptos_from_db, insert_crypto_data
from config import logger
from binance_data import get_crypto_data, get_data_from_binance
from datetime import datetime, timedelta



def fetch_and_insert_data(filter_by=None):
    """
    Obtiene los datos de las criptomonedas desde la base de datos y los inserta.

    @param filter_by: Opcional, puede ser:
                      - "favorites" -> Solo criptos marcadas como favoritas.
                      - "portfolio" -> Solo criptos en portfolio (que también son favoritas).
                      - None -> Todas las criptos.
    """
    # Obtener las criptos de la base de datos según el filtro
    cryptos = get_cryptos_from_db(filter_by)

    # Obtener datos y crear un DataFrame
    data = []
    timestamp = int(time.time())  # Usamos el timestamp actual

    for crypto in cryptos:
        price, volume, market_cap = get_crypto_data(crypto['symbol'])  # Cambiar crypto a dict
        if price is not None and volume is not None and market_cap is not None:
            data.append({
                'timestamp': timestamp,
                'symbol': crypto['symbol'],  # Usar 'symbol' del diccionario
                'close': price,
                'volume': volume,
                'market_cap': market_cap
            })

    # Crear DataFrame
    df = pd.DataFrame(data)

    # Insertar los datos en la base de datos
    if not df.empty:
        insert_crypto_data(df)  # Inserta los datos en la tabla `crypto_data`
        logger.info(f"Datos de {len(df)} criptomonedas insertados en la base de datos.")
    else:
        logger.error("No se encontraron datos para insertar.")



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

    Se asume que la función `get_data_from_binance()` (definida en otro archivo) se usa para obtener los datos
    de cada criptomoneda en el rango de los últimos 30 minutos, con granularidad de 1 minuto.
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

    # Consultar los datos cada 1 minuto entre el rango de 30 minutos
    for crypto in cryptos:
        # Usar la nueva versión de get_data_from_binance
        historical_data = get_data_from_binance(crypto['symbol'], '1m', 30)

        if historical_data:
            # Puedes optar por usar solo el último dato o todos, dependiendo de lo que necesites
            logger.info(f"Cargando datso de {crypto['symbol']}")
            for entry in historical_data:
                timestamp, price, volume, market_cap = entry
                timestamp = int(timestamp / 1000)  # Convertir a segundos
                # logger.info(f" ... Timestamp: {timestamp}, Price: {price}")
                data.append((
                    timestamp,
                    crypto['symbol'],
                    price,
                    volume,
                    market_cap
                ))

    # Si hay datos, insertar en la base de datos
    if data:
        df = pd.DataFrame(data)
        insert_crypto_data(df)
        logger.info(f"✅-{len(df)} filas de datos de {len(cryptos)}-🪙 insertadas en la base de datos para los últimos 30 minutos.")
    else:
        logger.warning("No se encontraron datos para los últimos 30 minutos.")
