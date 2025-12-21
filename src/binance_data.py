import ccxt
from config import logger, DB_PATH, DEFAULT_CURRENCY
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import time

# Conexión a Binance
binance_client = ccxt.binance()

def get_crypto_data(symbol, timeframe='30m', limit=30):
    """
    Obtiene el último precio, volumen y capitalización de mercado desde Binance,
    y calcula la media móvil desde la base de datos.

    Args:
        symbol (str): Símbolo de la criptomoneda (ej. BTC).
        timeframe (str): El intervalo de tiempo (ej. '1m', '5m', '1h', '1d', etc.).
        limit (int): El número de puntos de datos que deseas obtener.

    Returns:
        tuple: Último precio, volumen, capitalización de mercado y media móvil (o None si no hay datos suficientes).
    """
    try:
       # 🔹 Obtener datos históricos de Binance (último valor disponible)
        historical_data = get_data_from_binance(symbol, timeframe=timeframe, limit=limit)  # Solo el último minuto

        if not historical_data:
            return None, None, None, None  # Si no hay datos, devolvemos None

        # 🔹 Tomamos el último valor de los datos históricos
        last_entry = historical_data[-1]  # Último dato de la lista
        last_timestamp, last_price, last_volume, last_market_cap = last_entry

        # 🔹 Obtener datos históricos desde la base de datos para calcular la media móvil
        # Hay que revisar el tema de windows.
        moving_average = get_moving_average_from_db(symbol, window=12)

        return last_price, last_volume, last_market_cap, moving_average

    except Exception as e:
        logger.error(f"Error obteniendo datos para {symbol}: {e}")
        return None, None, None, None


def get_data_from_binance(symbol, timeframe='1d', limit=1):
    """
    Obtiene datos históricos de Binance con parámetros flexibles.

    Args:
        symbol (str): El símbolo de la criptomoneda (ej. BTC).
        timeframe (str): El intervalo de tiempo (ej. '1m', '5m', '1h', '1d', etc.).
        limit (int): El número de puntos de datos que deseas obtener.
    
    Returns:
        list: Una lista de tuplas con timestamp, precio, volumen y capitalización de mercado.
    """
    try:
        market_symbol = f"{symbol}/{DEFAULT_CURRENCY}"

        # 🔹 Realizar la consulta a Binance con el timeframe y rango de tiempo especificado
        # logger.info(f"Parametros para fetch_ohlcv: market_symbol: {market_symbol}, timeframe: {timeframe}, limit: {limit}")
        data = binance_client.fetch_ohlcv(market_symbol, timeframe, limit=limit)  # Ajusta el 'limit' según lo necesites

        historical_data = []
        for entry in data:
            timestamp = entry[0]  # Timestamp en milisegundos
            price = entry[4]       # Precio de cierre
            volume = entry[5]      # Volumen
            market_cap = price * volume  # Estimación de capitalización de mercado
            # logger.info(f"Datos de binance: Timestamp: {timestamp}, Price: {price}, Volume: {volume}, Market Cap: {market_cap}")
            historical_data.append((timestamp, price, volume, market_cap))

        return historical_data

    except Exception as e:
        logger.error(f"Error obteniendo datos de Binance para {symbol}: {e}")
        return []


def get_moving_average_from_db(symbol, window):
    """
    Calcula la media móvil usando los datos históricos de la base de datos.

    Args:
        symbol (str): Símbolo de la criptomoneda (ej. BTC).
        window (int): Número de períodos para la media móvil.

    Returns:
        float: Valor de la media móvil o None si no hay suficientes datos.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        query = """
            SELECT price
            FROM crypto_data
            WHERE symbol = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=(symbol, window))
        conn.close()

        if df.empty or len(df) < window:
            logger.warning(f"No hay suficientes datos para calcular la media móvil de {symbol}.")
            return None

        moving_average = df['price'].rolling(window=window).mean().iloc[-1]
        return moving_average

    except Exception as e:
        logger.error(f"Error calculando la media móvil para {symbol}: {e}")
        return None


def get_historical_data_in_range(symbol, start_datetime, end_datetime, timeframe='1m'):
    """
    Obtiene datos históricos de Binance para un rango de tiempo específico.

    Args:
        symbol (str): Símbolo de la criptomoneda (ej. BTC).
        start_datetime (datetime): Fecha y hora de inicio del rango.
        end_datetime (datetime): Fecha y hora de fin del rango.
        timeframe (str): Periodicidad de los datos (ej. '1m', '5m', '1h', '1d').

    Returns:
        list: Una lista de tuplas con timestamp, precio, volumen y capitalización de mercado.
              Retorna una lista vacia si no hay datos o hay un error.
    """
    try:
        market_symbol = f"{symbol}/{DEFAULT_CURRENCY}"
        
        # Convertir datetime a timestamp en milisegundos
        start_timestamp = int(time.mktime(start_datetime.timetuple()) * 1000)
        end_timestamp = int(time.mktime(end_datetime.timetuple()) * 1000)
        logger.info(f"Fecha de inicio: {start_datetime}, Fecha de fin: {end_datetime}")

        historical_data = []
        current_timestamp = start_timestamp

        while current_timestamp < end_timestamp:
            
            #Calculo del limite, ya que es de maximo 1000
            limit = 1000
            
            if binance_client.parse_timeframe(timeframe) * limit *1000 + current_timestamp > end_timestamp:
                limit = (end_timestamp - current_timestamp) //(binance_client.parse_timeframe(timeframe) *1000)

            if limit < 1:
                break
           
            
            try:
                data = binance_client.fetch_ohlcv(market_symbol, timeframe, since=current_timestamp, limit=limit)
            except ccxt.NetworkError as e:
                    logger.warning(f"Network error: {e}. Retrying in 5 seconds...")
                    time.sleep(5)
                    continue
            except ccxt.ExchangeError as e:
                    logger.error(f"Exchange error getting data for {symbol}: {e}")
                    return []
            
            if not data:
                logger.warning(f"No data returned from Binance for symbol {symbol} between timestamps {current_timestamp} and {current_timestamp+binance_client.parse_timeframe(timeframe) * limit * 1000}. Stoping")
                break

            for entry in data:
                timestamp = entry[0]
                price = entry[4]
                volume = entry[5]
                market_cap = price * volume
                historical_data.append((timestamp, price, volume, market_cap))

            # Avanzar al siguiente periodo
            current_timestamp += binance_client.parse_timeframe(timeframe) * limit * 1000

        return historical_data

    except Exception as e:
        logger.error(f"Error obteniendo datos históricos en rango para {symbol}: {e}")
        return []
