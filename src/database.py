# GESTIONA LOS DATOS DE LA BASE DE DATOS

# CREACIÓN DE LA BASE DE DATOS
from config import DB_PATH, logger
from binance_data import get_crypto_data, get_historical_data_in_range
import pandas as pd


# database.py
import sqlite3

def insert_crypto_data(df):
    """
    Inserta datos en la tabla `crypto_data`.

    @param df: DataFrame de Pandas con las siguientes columnas:
               - timestamp (int): Momento de la lectura en formato Unix.
               - symbol (str): Código de la criptomoneda (BTC, ETH, etc.).
               - close (float): Precio de cierre en el período analizado.
               - volume (float): Volumen de transacciones.
               - volumen_eur (float): Volumen valorizado (precio × volumen).

    Cada fila del DataFrame se inserta en la base de datos.
    """
    logger.info(f"Entranto en [insert_crypto_data]");
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Convertimos el DataFrame en una lista de tuplas para ejecutemany()
    data_tuples = list(df.itertuples(index=False, name=None))

    # Obtén el primer elemento de data_tuples
    primer_elemento = data_tuples[0]
    logger.info(f"Primer elemento a la lista {primer_elemento}");
    cursor.executemany("""
        INSERT INTO crypto_data (timestamp, symbol, price, volume, volumen_eur)
        VALUES (?, ?, ?, ?, ?)
    """, data_tuples)

    # for _, row in df.iterrows():
    #     conn.execute("""
    #         INSERT INTO crypto_data (timestamp, symbol, price, volume, # market_cap)
    #         VALUES (?, ?, ?, ?, ?)
    #     """, (row['timestamp'], row['symbol'], row['close'], row['volume'], row['market_cap']))
    
    conn.commit()
    conn.close()
    # print(f"{len(df)} filas insertadas en 'crypto_data'.")
    logger.info(f"✅ {len(df)} filas insertadas en 'crypto_data'.")


def insert_cryptos(df):
    """
    Inserta datos en la tabla `cryptos`, evitando duplicados.

    @param df: DataFrame de Pandas con las siguientes columnas:
               - symbol (str): Código de la criptomoneda (BTC, ETH, etc.).
               - name (str): Nombre completo de la criptomoneda.
               - slug (str): Identificador en minúsculas (bitcoin, ethereum, etc.).
               - is_favorite (int, opcional): Indica si es favorita (0 o 1).
               - is_portfolio (int, opcional): Indica si está en cartera (0 o 1).
               - nota (str, opcional): Notas sobre la criptomoneda.

    Usa `INSERT OR IGNORE` con `executemany` para evitar insertar símbolos ya existentes de forma eficiente.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Preparar los datos para executemany
    data_tuples = [
        (
            row['symbol'],
            row['name'],
            row['slug'],
            row.get('is_favorite', 0),  # Si no existe, por defecto 0
            row.get('is_portfolio', 0),  # Si no existe, por defecto 0
            row.get('nota', '')  # Si no existe, por defecto vacío
        ) for _, row in df.iterrows()
    ]

    if not data_tuples:
        logger.info("No hay datos de criptomonedas para insertar.")
        conn.close()
        return

    cursor.executemany("""
        INSERT OR IGNORE INTO cryptos (symbol, name, slug, is_favorite, is_portfolio, nota)
        VALUES (?, ?, ?, ?, ?, ?)
    """, data_tuples)

    conn.commit()
    conn.close()
    logger.info(f"✅ {len(data_tuples)} filas procesadas para 'cryptos' (ignorando duplicados).")

def get_cryptos_from_db(filter_by=None):
    """
    Obtiene criptomonedas desde la tabla `cryptos` con filtros opcionales.

    @param filter_by: Opcional, puede ser:
                      - "favorites" -> Solo criptos marcadas como favoritas.
                      - "portfolio" -> Solo criptos en portfolio (que también son favoritas).
                      - None -> Todas las criptos.

    @return: Lista de diccionarios con los campos de cada cripto.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = "SELECT * FROM cryptos"
    params = []

    if filter_by == "favorites":
        query += " WHERE is_favorite = 1"
    elif filter_by == "portfolio":
        query += " WHERE is_portfolio = 1"  # No hace falta comprobar is_favorite

    cursor.execute(query, params)
    cryptos = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    conn.close()
    return cryptos

import sqlite3
from datetime import datetime, timedelta


def get_data_from_db(symbol, window=12):
    """
    Obtiene datos históricos de una criptomoneda desde la base de datos para un período de tiempo específico.

    Args:
        symbol (str): El símbolo de la criptomoneda (por ejemplo, 'BTC').
        window (int):  Número máximo de registros a recuperar. Representa el número de elementos que va a devolver el método.

    Returns:
        dict or None: Un diccionario con los datos de timestamps, precios, volúmenes y capitalizaciones de mercado.
                      Devuelve None si no se encuentran datos para el símbolo dado en la última hora.
    """
    # Conectar a la base de datos
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Obtener la hora actual y calcular la hora de hace una hora
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)

    # Consulta SQL
    query = """
        SELECT timestamp, price, volume, volumen_eur
        FROM crypto_data
        WHERE symbol = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """
    # Parámetros para la consulta
    params = (symbol, window)

    # Registrar la consulta SQL en el log
    logger.info(f"Ejecutando consulta SQL: {query} con parámetros: {params}")

    # Ejecutar la consulta
    cursor.execute(query, params)
    rows = cursor.fetchall()

    # Organizar los datos para la gráfica
    if not rows:
        logger.info(f"No se encontraron datos para el símbolo {symbol} en la última hora.")
        conn.close()  # Cerrar la conexión antes de devolver None
        return None

    # Organizar los datos para la gráfica
    data = {
        'timestamps': [row[0] for row in rows],
        'prices': [row[1] for row in rows],
        'volumes': [row[2] for row in rows],
        'volumen_eur': [row[3] for row in rows],
    }

    # Cerrar la conexión a la base de datos después de organizar los datos
    conn.close()
    return data

def get_data_from_db_in_range(simbolo: str, fecha_inicio: datetime, fecha_fin: datetime):
    """
    Obtiene datos históricos de una criptomoneda desde la base de datos para un rango de fechas específico.

    Args:
        simbolo (str): El símbolo de la criptomoneda (ej. 'BTC').
        fecha_inicio (datetime): Fecha y hora de inicio del rango.
        fecha_fin (datetime): Fecha y hora de fin del rango.

    Returns:
        dict or None: Un diccionario con los datos de timestamps, precios, volúmenes y capitalizaciones de mercado.
                      Devuelve None si no se encuentran datos.
    """
    conexion = None
    try:
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()

        # Convertir datetime a timestamp Unix en segundos
        timestamp_inicio = int(fecha_inicio.timestamp())
        timestamp_fin = int(fecha_fin.timestamp())

        consulta = """
            SELECT timestamp, price, volume, volumen_eur
            FROM crypto_data
            WHERE symbol = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        """
        parametros = (simbolo, timestamp_inicio, timestamp_fin)
        logger.info(f"Ejecutando consulta por rango: {consulta} con parámetros: {parametros}")

        cursor.execute(consulta, parametros)
        filas = cursor.fetchall()

        if not filas:
            return None

        return {
            'timestamps': [fila[0] for fila in filas],
            'prices': [fila[1] for fila in filas],
            'volumes': [fila[2] for fila in filas], # volume
            'volumen_eur': [fila[3] for fila in filas], # volumen_euras],
        }
    finally:
        if conexion:
            conexion.close()

def obtener_portafolio():
    """
    Obtiene los símbolos de las criptomonedas que forman parte del portafolio.

    Returns:
        list: Una lista de símbolos de criptomonedas (ej. ['BTC', 'ETH', 'ADA']).
              Retorna una lista vacía si no hay criptomonedas en el portafolio.
              Retorna None si ocurre un error en la base de datos.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Consultar la tabla de portafolio
        cursor.execute("SELECT symbol FROM cryptos WHERE is_portfolio = 1")
        rows = cursor.fetchall()

        if not rows:
            logger.info("No hay criptomonedas en el portafolio.")
            return []  # Retorna una lista vacía si no hay datos

        # Extraer los símbolos de las filas y retornarlos en una lista
        symbols = [row[0] for row in rows]
        return symbols
    except sqlite3.Error as e:
        logger.error(f"Error al obtener el portafolio de la base de datos: {e}")
        return None  # Retorna None si ocurre un error
    finally:
        if conn:
            conn.close()


def obtener_precio_portafolio():
    """
    Obtiene el precio actual en EUR de las criptos en las que hay inversión activa.

    Returns:
        dict: Un diccionario con los precios de las criptomonedas.
        ejemplo:
          {
            "BTC": 42500,
            "ETH": 2350,
            "ADA": 0.55
          }
           Retorna un diccionario vacio si no hay criptos.
           Retorna None si hay un error con la BD
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Obtener los símbolos del portafolio
        symbols = obtener_portafolio()
        if symbols is None:
          return None
        elif not symbols:
          return {}

        prices = {}
        for symbol in symbols:
            # Obtener el precio actual desde Binance
            price, _, _, _ = get_crypto_data(symbol,'1d',1)
            if price is not None:
                prices[symbol] = price
            else:
                logger.warning(f"No se pudo obtener el precio para {symbol} desde Binance.")
        return prices
    except sqlite3.Error as e:
        logger.error(f"Error al obtener precio de portafolio: {e}")
        return None
    finally:
        if conn:
            conn.close()

def limpiar_crypto_data():
    """
    Limpia la tabla crypto_data eliminando registros duplicados para la misma moneda y timestamp,
    manteniendo solo el registro con el ROWID más pequeño (el primero insertado).
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM crypto_data
            WHERE ROWID NOT IN (
                SELECT MIN(ROWID)
                FROM crypto_data
                GROUP BY timestamp, symbol
            );
        """)
        # Obtener el número de filas afectadas (eliminadas)
        deleted_count = cursor.rowcount
        # Confirmar los cambios en la base de datos
        conn.commit()
        
        logger.info(f"Tabla crypto_data limpiada correctamente. Se eliminaron {deleted_count} registros duplicados.")
    except sqlite3.Error as e:
        logger.error(f"Error al limpiar la tabla crypto_data: {e}")
    finally:
        if conn:
            conn.close()


def insert_historico_crypto_data(symbols, start_datetime, end_datetime, timeframe='1m'):
    """
    Recupera datos históricos de criptomonedas de Binance y los inserta en la base de datos.

    Args:
        symbols (list): Lista de símbolos de criptomonedas (ej., ['BTC', 'ETH']).
        start_datetime (datetime): Fecha y hora de inicio del rango.
        end_datetime (datetime): Fecha y hora de fin del rango.
        timeframe (str): Intervalo de tiempo (ej., '1m', '5m', '1h', '1d').

    Returns:
        bool: True si la inserción fue exitosa para todas las criptomonedas, False en caso contrario.
    """
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for symbol in symbols:
            # Obtener datos históricos de Binance
            historical_data = get_historical_data_in_range(symbol, start_datetime, end_datetime, timeframe)
            if not historical_data:
                logger.warning(f"No se encontraron datos para {symbol} en el rango especificado.")
                continue  # Si no se encuentran datos, pasamos al siguiente símbolo

            logger.info(f"Se han obtenido {len(historical_data)} datos históricos de {symbol}")
            logger.info(f"Primer dato: {historical_data[0]}")
            logger.info(f"Último dato: {historical_data[-1]}")

            # Preparar datos para inserción en la base de datos
            data_tuples = [(ts // 1000, symbol, p, v, mc) for ts, p, v, mc in historical_data]

            # Insertar los datos usando executemany para mayor eficiencia
            cursor.executemany("""
                INSERT INTO crypto_data (timestamp, symbol, price, volume, volumen_eur)
                VALUES (?, ?, ?, ?, ?)
            """, data_tuples)
            logger.info(f"Datos históricos de {symbol} insertados correctamente.")

        # Confirmar los cambios en la base de datos
        conn.commit()
        conn.close()
        return True

    except sqlite3.IntegrityError:
        logger.warning("Error: Algunos datos ya existen en la base de datos. Se omitieron los duplicados.")
        return False  # Manejar la integridad de la base de datos
    except Exception as e:
        logger.error(f"Error al obtener o insertar datos históricos: {e}")
        return False  # Manejar errores generales


def datos_comparados(monedas):
    """
    Obtiene datos de precio y timestamp de las criptomonedas indicadas. De las ultimas 24 horas.

    :param monedas: Lista de símbolos de criptomonedas (ej. ['BTC', 'ETH']).
    :return: DataFrame con los datos filtrados.
    """
    conn = sqlite3.connect(DB_PATH)
    limite = len(monedas)*1440
    
    # Construir la consulta dinámica
    placeholders = ', '.join(['?'] * len(monedas))
    query = f"""
    SELECT timestamp, symbol, price
    FROM crypto_data
    WHERE symbol IN ({placeholders})
    ORDER BY timestamp DESC
    LIMIT {limite};
    """

    cursor = conn.cursor()
    cursor.execute(query, monedas)
    data = cursor.fetchall()
    
    conn.close()
    
    # Convertir los resultados a una lista de diccionarios
    result = [{"timestamp": timestamp, "symbol": symbol, "price": price} for timestamp, symbol, price in data]
    
    return result

####################################################################
# calcular_posicion_actual
#######################################################

def calcular_posicion_actual(simbolo: str):
    """
    Calcula la posición actual de una criptomoneda basándose en la tabla 'operaciones'.
    Devuelve cantidad de inversión, cantidad de recompensas, coste total neto y coste medio.

    La cantidad de inversión solo incluye compras/ventas/envíos.
    Las recompensas (staking, airdrops, etc.) se trackean por separado para mantener
    la integridad del precio medio de compra.
    """
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    # Cargar todas las operaciones de esa cripto
    cursor.execute("""
        SELECT tipo, cantidad, valor_total, comision
        FROM operaciones
        WHERE cripto = ?
        ORDER BY timestamp ASC
    """, (simbolo.upper(),))

    operaciones = cursor.fetchall()
    conexion.close()

    cantidad_inversion = 0.0  # Solo compras/ventas/envíos
    cantidad_recompensas = 0.0  # Recompensas de staking, airdrops, etc.
    cantidad_recepciones = 0.0  # Recepciones (transferencias entrantes)
    coste_total = 0.0

    for tipo, cantidad, valor_total, comision in operaciones:
        tipo_lower = tipo.lower()
        comision_actual = comision if comision is not None else 0.0

        if tipo_lower == "compra":
            cantidad_inversion += cantidad
            coste_total += valor_total + comision_actual
        elif tipo_lower in ["venta", "envío", "envio"]:
            # Para ventas o envíos, reducimos el coste total proporcionalmente a la cantidad vendida/enviada (método del coste medio).
            coste_medio_unitario = 0
            if cantidad_inversion > 0:
                coste_medio_unitario = coste_total / cantidad_inversion

            coste_a_reducir = cantidad * coste_medio_unitario
            coste_total -= coste_a_reducir
            cantidad_inversion -= cantidad
        elif tipo_lower == "recepción":
            cantidad_recepciones += cantidad
            # El coste total no se modifica para recepciones "gratuitas"
        elif tipo_lower == "recompensa":
            cantidad_recompensas += cantidad
            # El coste total no se modifica para recompensas (staking, etc.)

    # Calcular coste medio solo basado en la inversión real
    if cantidad_inversion > 0:
        coste_medio = coste_total / cantidad_inversion
    else:
        coste_medio = 0.0

    # Cantidad total es la suma de todas las fuentes
    cantidad_total = cantidad_inversion + cantidad_recompensas + cantidad_recepciones

    return {
        "cripto": simbolo.upper(),
        "cantidad_actual": round(cantidad_inversion, 8),  # Solo inversión (compras/ventas)
        "cantidad_recompensas": round(cantidad_recompensas, 8),  # Recompensas de staking
        "cantidad_recepciones": round(cantidad_recepciones, 8),  # Recepciones/transferencias
        "cantidad_total": round(cantidad_total, 8),  # Suma total
        "coste_total": round(coste_total, 2),
        "coste_medio": round(coste_medio, 2)
    }




####################################################################
# obtener_operaciones_por_criptomoned
#######################################################


def obtener_operaciones_por_criptomoneda(simbolo: str):
    """
    Obtiene todas las operaciones para una criptomoneda específica desde la tabla 'operaciones'.

    Args:
        simbolo: El ticker de la criptomoneda (ej. 'BTC', 'ETH').

    Returns:
        Una lista de tuplas representando las operaciones.
        Cada tupla corresponde a una fila de la tabla 'operaciones'.
        Retorna una lista vacía si no hay operaciones o si ocurre un error.
    """
    conexion = None
    try:
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        # Asegúrate de que el nombre de la columna para el ticker en tu tabla 'operaciones' sea 'cripto'
        cursor.execute("SELECT * FROM operaciones WHERE cripto = ?", (simbolo.upper(),))
        lista_operaciones = cursor.fetchall()
        return lista_operaciones
    except sqlite3.Error as e:
        logger.error(f"Error al obtener operaciones para {simbolo} desde la base de datos: {e}")
        return []
    finally:
        if conexion:
            conexion.close()


####################################################################
# guardar_uso_ia
#######################################################

def guardar_tokens_ia(
    proveedor: str = "groq",
    modelo: str = "llama-3.1-70b-instant",
    tokens_entrada: int = 0,
    tokens_salida: int = 0
):
    """Guarda solo los tokens de entrada y salida. El total se calcula cuando haga falta."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO uso_ia
        (proveedor, modelo, tokens_entrada, tokens_salida)
        VALUES (?, ?, ?, ?)
    """, (proveedor, modelo, tokens_entrada, tokens_salida))

    conn.commit()
    conn.close()


####################################################################
# FUNCIONES PARA SNAPSHOTS DEL PORTFOLIO (Fase 1.3)
####################################################################

def crear_tabla_portfolio_snapshots():
    """
    Crea la tabla portfolio_snapshots si no existe.

    Esta tabla almacena snapshots del estado del portfolio en cada consulta,
    permitiendo comparar cambios entre llamadas al endpoint.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                cripto TEXT NOT NULL,
                cantidad_actual REAL NOT NULL,
                precio_actual REAL NOT NULL,
                valor_actual REAL NOT NULL,
                coste_total REAL NOT NULL,
                rentabilidad_pct REAL NOT NULL,
                rentabilidad_abs REAL NOT NULL,
                peso_inversion_pct REAL NOT NULL,
                peso_actual_pct REAL NOT NULL
            )
        """)

        # Crear índice para mejorar performance de consultas
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp
            ON portfolio_snapshots(timestamp DESC)
        """)

        conn.commit()
        logger.info("Tabla portfolio_snapshots creada/verificada correctamente.")
        return True
    except sqlite3.Error as e:
        logger.error(f"Error al crear tabla portfolio_snapshots: {e}")
        return False
    finally:
        if conn:
            conn.close()


def guardar_snapshot_portfolio(datos_portfolio: list, timestamp: int = None):
    """
    Guarda un snapshot del estado actual del portfolio.

    Args:
        datos_portfolio: Lista de diccionarios con los datos de cada cripto del portfolio
                        (como los devuelve analizar_portfolio_completo).
        timestamp: Timestamp Unix en segundos. Si no se proporciona, usa el momento actual.

    Returns:
        int: El timestamp del snapshot guardado, o None si hubo error.
    """
    import time

    if not datos_portfolio:
        logger.warning("No hay datos de portfolio para guardar snapshot.")
        return None

    if timestamp is None:
        timestamp = int(time.time())

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Preparar datos para inserción
        data_tuples = []
        for cripto in datos_portfolio:
            data_tuples.append((
                timestamp,
                cripto.get('simbolo', ''),
                cripto.get('cantidad_actual', 0),
                cripto.get('precio_actual', 0),
                cripto.get('valor_actual_inversion', 0),
                cripto.get('coste_total_inversion', 0),
                cripto.get('rentabilidad_porcentaje', 0),
                cripto.get('ganancia_perdida_abs', 0),
                cripto.get('peso_inversion_pct', 0),
                cripto.get('peso_actual_pct', 0)
            ))

        # Insertar todos los datos del snapshot
        cursor.executemany("""
            INSERT INTO portfolio_snapshots
            (timestamp, cripto, cantidad_actual, precio_actual, valor_actual,
             coste_total, rentabilidad_pct, rentabilidad_abs, peso_inversion_pct, peso_actual_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data_tuples)

        conn.commit()
        logger.info(f"Snapshot del portfolio guardado correctamente. Timestamp: {timestamp}, Cryptos: {len(data_tuples)}")
        return timestamp
    except sqlite3.Error as e:
        logger.error(f"Error al guardar snapshot del portfolio: {e}")
        return None
    finally:
        if conn:
            conn.close()


def obtener_ultimo_snapshot():
    """
    Obtiene el snapshot más reciente del portfolio.

    Returns:
        dict: Diccionario con:
            - 'timestamp': timestamp del snapshot
            - 'portfolio': lista de diccionarios con los datos de cada cripto
        None si no hay snapshots guardados o hay error.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Obtener el timestamp más reciente
        cursor.execute("""
            SELECT MAX(timestamp) FROM portfolio_snapshots
        """)

        result = cursor.fetchone()
        if not result or result[0] is None:
            logger.info("No hay snapshots previos del portfolio.")
            return None

        timestamp_anterior = result[0]

        # Obtener todos los datos de ese snapshot
        # Intentar primero con el nuevo esquema (ambos pesos)
        try:
            cursor.execute("""
                SELECT cripto, cantidad_actual, precio_actual, valor_actual,
                       coste_total, rentabilidad_pct, rentabilidad_abs, peso_inversion_pct, peso_actual_pct
                FROM portfolio_snapshots
                WHERE timestamp = ?
                ORDER BY cripto ASC
            """, (timestamp_anterior,))

            rows = cursor.fetchall()

            if not rows:
                return None

            # Convertir a lista de diccionarios (nuevo esquema con ambos pesos)
            portfolio_data = []
            for row in rows:
                portfolio_data.append({
                    'simbolo': row[0],
                    'cantidad_actual': row[1],
                    'precio_actual': row[2],
                    'valor_actual_inversion': row[3],
                    'coste_total_inversion': row[4],
                    'rentabilidad_porcentaje': row[5],
                    'ganancia_perdida_abs': row[6],
                    'peso_inversion_pct': row[7],
                    'peso_actual_pct': row[8]
                })
        except sqlite3.OperationalError:
            # Si falla, probablemente es la tabla vieja con solo peso_portfolio_pct
            logger.warning("Usando esquema antiguo de snapshots (solo peso_portfolio_pct)")
            cursor.execute("""
                SELECT cripto, cantidad_actual, precio_actual, valor_actual,
                       coste_total, rentabilidad_pct, rentabilidad_abs, peso_portfolio_pct
                FROM portfolio_snapshots
                WHERE timestamp = ?
                ORDER BY cripto ASC
            """, (timestamp_anterior,))

            rows = cursor.fetchall()

            if not rows:
                return None

            # Convertir a lista de diccionarios (esquema antiguo)
            # Usamos peso_portfolio_pct para ambos campos por compatibilidad
            portfolio_data = []
            for row in rows:
                portfolio_data.append({
                    'simbolo': row[0],
                    'cantidad_actual': row[1],
                    'precio_actual': row[2],
                    'valor_actual_inversion': row[3],
                    'coste_total_inversion': row[4],
                    'rentabilidad_porcentaje': row[5],
                    'ganancia_perdida_abs': row[6],
                    'peso_portfolio_pct': row[7],  # Mantener para compatibilidad
                    'peso_inversion_pct': row[7],  # Usar el mismo valor temporalmente
                    'peso_actual_pct': row[7]      # Usar el mismo valor temporalmente
                })

        return {
            'timestamp': timestamp_anterior,
            'portfolio': portfolio_data
        }
    except sqlite3.Error as e:
        logger.error(f"Error al obtener último snapshot: {e}")
        return None
    finally:
        if conn:
            conn.close()


def limpiar_snapshots_antiguos(dias_a_mantener: int = 30):
    """
    Elimina snapshots más antiguos que X días para evitar que la tabla crezca indefinidamente.

    Args:
        dias_a_mantener: Número de días de snapshots a mantener. Por defecto 30.

    Returns:
        int: Número de registros eliminados, o -1 si hay error.
    """
    import time

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Calcular timestamp límite
        timestamp_limite = int(time.time()) - (dias_a_mantener * 24 * 60 * 60)

        cursor.execute("""
            DELETE FROM portfolio_snapshots
            WHERE timestamp < ?
        """, (timestamp_limite,))

        deleted_count = cursor.rowcount
        conn.commit()

        if deleted_count > 0:
            logger.info(f"Eliminados {deleted_count} snapshots antiguos (más de {dias_a_mantener} días).")

        return deleted_count
    except sqlite3.Error as e:
        logger.error(f"Error al limpiar snapshots antiguos: {e}")
        return -1
    finally:
        if conn:
            conn.close()