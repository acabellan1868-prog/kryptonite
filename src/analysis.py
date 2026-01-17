import sqlite3
import pandas as pd
from config import DB_PATH, logger
from database import get_data_from_db


####################################################################
# calculate_moving_average 
####################################################################

def calculate_moving_average(symbol, minutes):
    """
    Calcula la media móvil de una criptomoneda en los últimos x minutos.

    Args:
        symbol (str): Símbolo de la criptomoneda (ej. 'BTC').
        minutes (int): Número de minutos para calcular la media móvil.

    Returns:
        float: Valor de la media móvil.
        None: Si no hay suficientes datos o hay un error.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Obtener el timestamp actual
            cursor.execute("SELECT strftime('%s', 'now')")
            current_timestamp = int(cursor.fetchone()[0])

            # Calcular el timestamp de hace x minutos
            past_timestamp = current_timestamp - (minutes * 60)

            # Consulta para obtener los precios de la criptomoneda en los últimos x minutos
            query = """
                SELECT price
                FROM crypto_data
                WHERE symbol = ? AND timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            cursor.execute(query, (symbol, past_timestamp, minutes // 5))  # Suponiendo que se recopilan cada 5 minutos
            prices = [row[0] for row in cursor.fetchall()]

        if not prices:
            logger.warning(f"No se encontraron datos para {symbol} en los últimos {minutes} minutos.")
            return None

        # Calcular la media móvil
        moving_average = sum(prices) / len(prices)
        return moving_average

    except sqlite3.Error as e:
        logger.error(f"Error de SQLite: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return None

####################################################################
# calculate_sma 
####################################################################

def calculate_sma(symbol: str, period: int = 10, window: int = 100):
    """
    Calcula la Media Móvil Simple (SMA) para una criptomoneda dada.

    Args:
        symbol (str): Símbolo de la criptomoneda (ej. 'BTCUSDT').
        period (int): Número de períodos para calcular la SMA (por defecto 10).
        window (int): Número de registros recientes a obtener de la base de datos.

    Returns:
        pd.DataFrame: DataFrame con timestamps, precios y valores de la SMA.
    """
    
    # Obtener datos históricos desde la base de datos
    data = get_data_from_db(symbol, window)
    if data is None:
        return None  # Si no se encuentran datos, devolvemos None
    
    # Convertir los datos en un DataFrame de pandas
    df = pd.DataFrame({
        'timestamp': data['timestamps'],
        'price': data['prices'],
        'volume': data['volumes'],
        'volumen_eur': data['volumen_eur']
    })
    
    # Convertir timestamps a formato legible
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    
    # Calcular la media móvil
    df['sma'] = df['price'].rolling(window=period).mean()
    
    return df

####################################################################
#  cambio_porcentual_precio
####################################################################

def cambio_porcentual_precio(simbolo: str, intervalo_minutos: int = 15):
    """
    Devuelve el cambio en porciento que ha experimentado el precio de una moneda en un intervalo de tiempo.

    Args:
        simbolo (str): Símbolo de la criptomoneda (ej. 'BTC').
        intervalo_minutos (int): Período en minutos sobre el cual calcular el cambio porcentual.

     Returns:
        dict: Un diccionario con el símbolo, precio actual, precio anterior y cambio porcentual.
              Ej: {'simbolo': 'BTC', 'precio_actual': 70000, 'precio_anterior': 70700,
                   'cambio_porcentual': -1.0}

    """
    # puntos_datos_necesarios = int(intervalo_minutos / 5) + 2
    puntos_datos_necesarios = intervalo_minutos + 5  # 5 de margen de seguridad

    datos = get_data_from_db(simbolo, window=puntos_datos_necesarios)

    if datos is None or not datos['prices'] or len(datos['prices']) < 2:
        logger.warning(f"No hay suficientes datos para generar un valor porcentual para {simbolo} en {intervalo_minutos} minutos.")
        return {'simbolo': simbolo, 'precio_actual': None, 'precio_anterior': None, 'cambio_porcentual': None}

    df_precios = pd.DataFrame({'timestamp': datos['timestamps'], 'price': datos['prices']}).sort_values(by='timestamp', ascending=True)
    #logger.info(f"Timestamps disponibles: {df_precios['timestamp'].tolist()}")
    precio_actual = df_precios['price'].iloc[-1]
    timestamp_actual = df_precios['timestamp'].iloc[-1]

    # Excluimos el punto actual para la búsqueda del punto anterior.
    df_sin_actual = df_precios.iloc[:-1]

    # Si no hay más puntos después de quitar el actual, no podemos comparar.
    if df_sin_actual.empty:
        logger.warning(f"No hay puntos de datos anteriores para comparar para {simbolo}.")
        return {'simbolo': simbolo, 'precio_actual': precio_actual, 'precio_anterior': None, 'cambio_porcentual': None}

    # Calculamos el timestamp objetivo (hace 'intervalo_minutos' minutos)
    timestamp_objetivo = timestamp_actual - (intervalo_minutos * 60)

    # Encontramos el índice del punto de datos cuyo timestamp es más cercano al timestamp objetivo.
    # Esto es más robusto frente a pequeños huecos en los datos.
    idx_mas_cercano = (df_sin_actual['timestamp'] - timestamp_objetivo).abs().idxmin()
    punto_dato_anterior = df_precios.loc[idx_mas_cercano]

    if punto_dato_anterior['price'] == 0:
        logger.warning(f"El precio del punto de datos encontrado {intervalo_minutos} minutos atrás es cero para {simbolo}.")
        return {'simbolo': simbolo, 'precio_actual': precio_actual, 'precio_anterior': None, 'cambio_porcentual': None}

    precio_anterior = punto_dato_anterior['price']
    cambio_porcentual = ((precio_actual - precio_anterior) / precio_anterior) * 100
    return {
        'simbolo': simbolo,
        'precio_actual': precio_actual,
        'precio_anterior': precio_anterior,
        'cambio_porcentual': cambio_porcentual,
    }
                

####################################################################
#  cambio_porcentual_volumen
####################################################################

def cambio_porcentual_volumen(simbolo: str, intervalo_ventana_minutos: int = 30, num_ventanas_historicas: int = 5) -> dict:
    """
    Calcula el cambio porcentual del volumen total de la ventana más reciente
    con respecto al volumen promedio de ventanas históricas de la misma duración.

    Args:
        simbolo (str): Símbolo de la criptomoneda (ej. 'BTC').
        intervalo_ventana_minutos (int): Duración en minutos de cada ventana de análisis.
        num_ventanas_historicas (int): Número de ventanas pasadas para calcular el promedio histórico.

    Returns:
        dict: Un diccionario con el volumen total actual, el promedio histórico y el cambio porcentual.
              Ej: {'simbolo': 'BTC', 'volumen_total_actual': 15000, 'volumen_promedio_historico': 10000,
                   'cambio_porcentual_volumen': 50.0}
    """
    # Calcular tiempo total necesario en segundos
    tiempo_total_segundos = (num_ventanas_historicas + 1) * intervalo_ventana_minutos * 60
    # Pedir más registros para asegurar cobertura completa (asumiendo frecuencia de 1 min o más)
    puntos_datos_necesarios = int(tiempo_total_segundos / 60) + 30  # +30 de margen

    datos = get_data_from_db(simbolo, window=puntos_datos_necesarios)

    # Validar que tenemos datos
    if datos is None or not datos['volumes'] or len(datos['volumes']) < 2:
        logger.warning(f"No hay suficientes datos de volumen para {simbolo}.")
        return {'simbolo': simbolo, 'volumen_total_actual': None, 'volumen_promedio_historico': None, 'cambio_porcentual_volumen': None}

    # Crear DataFrame y eliminar duplicados por timestamp
    df = pd.DataFrame({
        'timestamp': datos['timestamps'],
        'volume': datos['volumes']
    }).sort_values(by='timestamp', ascending=True).drop_duplicates(subset=['timestamp'], keep='last')

    # Verificar que tenemos datos suficientes después de limpiar
    if len(df) < 2:
        logger.warning(f"Datos insuficientes después de eliminar duplicados para {simbolo}.")
        return {'simbolo': simbolo, 'volumen_total_actual': None, 'volumen_promedio_historico': None, 'cambio_porcentual_volumen': None}

    # Convertir timestamp a datetime y ordenar
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
    df = df.sort_values('timestamp', ascending=True)

    # Verificar que el rango temporal sea suficiente
    tiempo_disponible_segundos = df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]
    tiempo_minimo_requerido = (num_ventanas_historicas + 1) * intervalo_ventana_minutos * 60 * 0.5  # Al menos 50% del tiempo requerido

    if tiempo_disponible_segundos < tiempo_minimo_requerido:
        logger.warning(f"Rango temporal muy insuficiente para {simbolo}: {tiempo_disponible_segundos/60:.0f} min disponibles vs mínimo {tiempo_minimo_requerido/60:.0f} min requeridos.")
        return {'simbolo': simbolo, 'volumen_total_actual': None, 'volumen_promedio_historico': None, 'cambio_porcentual_volumen': None}

    # Si tenemos menos tiempo del ideal, ajustar expectativas pero continuar
    if tiempo_disponible_segundos < tiempo_total_segundos:
        logger.info(f"ADVERTENCIA: Datos parciales para {simbolo}. Disponible: {tiempo_disponible_segundos/60:.0f} min, ideal: {tiempo_total_segundos/60:.0f} min. Continuando con datos disponibles...")

    # Calcular ventanas móviles consecutivas (NO solapadas) desde el final
    # Ventana 0: últimos N minutos
    # Ventana 1: N minutos anteriores
    # Ventana 2: N minutos anteriores a esos, etc.
    timestamp_mas_reciente = df['timestamp'].iloc[-1]
    ventanas_volumen = []

    for i in range(num_ventanas_historicas + 1):
        # Calcular límites de ventanas CONSECUTIVAS (no solapadas)
        # Ventana 0: [now - 60min, now]
        # Ventana 1: [now - 120min, now - 60min]
        # Ventana 2: [now - 180min, now - 120min]
        fin_ventana = timestamp_mas_reciente - (i * intervalo_ventana_minutos * 60)
        inicio_ventana = timestamp_mas_reciente - ((i + 1) * intervalo_ventana_minutos * 60)

        # Filtrar datos en esta ventana
        datos_ventana = df[(df['timestamp'] > inicio_ventana) & (df['timestamp'] <= fin_ventana)]

        # Sumar volumen
        volumen_ventana = datos_ventana['volume'].sum()
        ventanas_volumen.append(volumen_ventana)

        logger.debug(f"Ventana {i}: {inicio_ventana} - {fin_ventana}, volumen: {volumen_ventana:.4f}, registros: {len(datos_ventana)}")

    # Verificar que tenemos ventanas válidas
    if len(ventanas_volumen) < num_ventanas_historicas + 1:
        logger.warning(f"Ventanas insuficientes para {simbolo}: {len(ventanas_volumen)} ventanas vs {num_ventanas_historicas + 1} necesarias.")
        return {'simbolo': simbolo, 'volumen_total_actual': None, 'volumen_promedio_historico': None, 'cambio_porcentual_volumen': None}

    # La ventana actual es la primera (i=0)
    volumen_total_actual = ventanas_volumen[0]

    # Las ventanas históricas son las siguientes
    ventanas_historicas = ventanas_volumen[1:]

    if len(ventanas_historicas) == 0:
        logger.warning(f"No hay ventanas históricas de volumen para calcular el promedio para {simbolo}.")
        return {'simbolo': simbolo, 'volumen_total_actual': volumen_total_actual, 'volumen_promedio_historico': None, 'cambio_porcentual_volumen': None}

    # Calcular promedio de las ventanas históricas (es una lista, no un Series de pandas)
    volumen_promedio_historico = sum(ventanas_historicas) / len(ventanas_historicas)

    if volumen_promedio_historico == 0 or pd.isna(volumen_promedio_historico):
        cambio_porcentual = float('inf') if volumen_total_actual > 0 else 0.0
    else:
        cambio_porcentual = ((volumen_total_actual - volumen_promedio_historico) / volumen_promedio_historico) * 100

    return {
        'simbolo': simbolo,
        'volumen_total_actual': float(volumen_total_actual),
        'volumen_promedio_historico': float(volumen_promedio_historico),
        'cambio_porcentual_volumen': float(cambio_porcentual)
    }

####################################################################
#  calcular_presion_compradora (OBV Simplificado)
####################################################################

def calcular_presion_compradora(simbolo: str, ventana_minutos: int = 60) -> dict:
    """
    Calcula la presión compradora vs vendedora usando OBV simplificado.

    Lógica:
    - Si precio sube respecto al minuto anterior → volumen se suma a "compradores"
    - Si precio baja respecto al minuto anterior → volumen se suma a "vendedores"

    Args:
        simbolo (str): Símbolo de la criptomoneda (ej. 'BTC').
        ventana_minutos (int): Período en minutos para analizar (default: 60).

    Returns:
        dict: {
            'simbolo': 'BTC',
            'volumen_compra': 5.2,
            'volumen_venta': 3.8,
            'presion_compradora_pct': 57.8,
            'presion_vendedora_pct': 42.2,
            'interpretacion': 'LIGERA_PRESION_COMPRADORA'
        }
    """
    # Obtener datos suficientes para el análisis
    # Pedimos el doble de registros para asegurar cobertura completa
    datos = get_data_from_db(simbolo, window=ventana_minutos * 2)

    # Validar datos
    if datos is None or not datos['prices'] or len(datos['prices']) < 2:
        logger.warning(f"Datos insuficientes para calcular presión compradora de {simbolo}.")
        return {
            'simbolo': simbolo,
            'volumen_compra': None,
            'volumen_venta': None,
            'presion_compradora_pct': None,
            'presion_vendedora_pct': None,
            'interpretacion': 'DATOS_INSUFICIENTES'
        }

    # Crear DataFrame
    df = pd.DataFrame({
        'timestamp': datos['timestamps'],
        'price': datos['prices'],
        'volume': datos['volumes']
    }).sort_values(by='timestamp', ascending=True).drop_duplicates(subset=['timestamp'], keep='last')

    if len(df) < 2:
        logger.warning(f"Datos insuficientes después de limpiar duplicados para {simbolo}.")
        return {
            'simbolo': simbolo,
            'volumen_compra': None,
            'volumen_venta': None,
            'presion_compradora_pct': None,
            'presion_vendedora_pct': None,
            'interpretacion': 'DATOS_INSUFICIENTES'
        }

    # Filtrar solo los últimos N minutos
    timestamp_mas_reciente = df['timestamp'].iloc[-1]
    timestamp_inicio = timestamp_mas_reciente - (ventana_minutos * 60)
    df = df[df['timestamp'] > timestamp_inicio]

    if len(df) < 2:
        logger.warning(f"Datos insuficientes en la ventana de {ventana_minutos} min para {simbolo}.")
        return {
            'simbolo': simbolo,
            'volumen_compra': None,
            'volumen_venta': None,
            'presion_compradora_pct': None,
            'presion_vendedora_pct': None,
            'interpretacion': 'DATOS_INSUFICIENTES'
        }

    # Calcular presión compradora/vendedora
    volumen_compra = 0.0
    volumen_venta = 0.0
    volumen_sin_cambio = 0.0
    minutos_subida = 0
    minutos_bajada = 0
    minutos_sin_cambio = 0

    prices = df['price'].tolist()
    volumes = df['volume'].tolist()

    for i in range(1, len(prices)):
        if prices[i] > prices[i-1]:
            # Precio subió → presión compradora
            volumen_compra += volumes[i]
            minutos_subida += 1
        elif prices[i] < prices[i-1]:
            # Precio bajó → presión vendedora
            volumen_venta += volumes[i]
            minutos_bajada += 1
        else:
            # Precio igual → sin cambio
            volumen_sin_cambio += volumes[i]
            minutos_sin_cambio += 1

    total = volumen_compra + volumen_venta

    if total == 0:
        presion_compradora_pct = 50.0
        presion_vendedora_pct = 50.0
    else:
        presion_compradora_pct = (volumen_compra / total) * 100
        presion_vendedora_pct = (volumen_venta / total) * 100

    # Determinar interpretación
    if presion_compradora_pct >= 70:
        interpretacion = 'DOMINIO_COMPRADOR_FUERTE'
    elif presion_compradora_pct >= 50:
        interpretacion = 'LIGERA_PRESION_COMPRADORA'
    elif presion_compradora_pct >= 30:
        interpretacion = 'LIGERA_PRESION_VENDEDORA'
    else:
        interpretacion = 'DOMINIO_VENDEDOR_FUERTE'

    logger.info(f"Presión compradora {simbolo} ({ventana_minutos}min): {presion_compradora_pct:.1f}% compra, {presion_vendedora_pct:.1f}% venta → {interpretacion}")
    logger.info(f"Desglose minutos: {minutos_subida} subida, {minutos_bajada} bajada, {minutos_sin_cambio} sin cambio")

    return {
        'simbolo': simbolo,
        'volumen_compra': round(volumen_compra, 5),
        'volumen_venta': round(volumen_venta, 5),
        'volumen_sin_cambio': round(volumen_sin_cambio, 5),
        'minutos_subida': minutos_subida,
        'minutos_bajada': minutos_bajada,
        'minutos_sin_cambio': minutos_sin_cambio,
        'presion_compradora_pct': round(presion_compradora_pct, 1),
        'presion_vendedora_pct': round(presion_vendedora_pct, 1),
        'interpretacion': interpretacion
    }


def generar_conclusion_senal(senal: str, presion_compradora_pct: float) -> str:
    """
    Genera una conclusión automática basada en la señal y la presión compradora.

    Args:
        senal (str): COMPRA, VENTA o MANTENER
        presion_compradora_pct (float): Porcentaje de presión compradora (0-100)

    Returns:
        str: Conclusión descriptiva para mostrar al usuario
    """
    if presion_compradora_pct is None:
        return "Sin datos de presión para analizar."

    if senal == 'COMPRA':
        if presion_compradora_pct >= 70:
            return "COMPRA CONFIRMADA. Caída con fuerte presión compradora. Rebote muy probable."
        elif presion_compradora_pct >= 50:
            return "COMPRA con cautela. Ligera presión compradora. Rebote posible."
        elif presion_compradora_pct >= 30:
            return "ESPERAR. Señal de compra débil con presión vendedora."
        else:
            return "NO COMPRAR. Fuerte presión vendedora. Puede seguir cayendo."

    elif senal == 'VENTA':
        if presion_compradora_pct <= 30:
            return "VENTA CONFIRMADA. Subida con fuerte presión vendedora. Corrección probable."
        elif presion_compradora_pct <= 50:
            return "VENTA con cautela. Ligera presión vendedora. Corrección posible."
        elif presion_compradora_pct <= 70:
            return "ESPERAR. Señal de venta débil con presión compradora."
        else:
            return "NO VENDER. Rally genuino con fuerte presión compradora."

    else:  # MANTENER
        if presion_compradora_pct >= 60:
            return "Mercado lateral con presión compradora. Posible subida próxima."
        elif presion_compradora_pct <= 40:
            return "Mercado lateral con presión vendedora. Posible bajada próxima."
        else:
            return "Mercado lateral equilibrado. Sin señales claras."


####################################################################
#  analizar_tendencia_previa
####################################################################

def analizar_tendencia_previa(simbolo: str, intervalo_minutos: int = 60) -> dict:
    """
    Analiza la tendencia del precio en un período anterior para dar contexto a la señal.

    Args:
        simbolo (str): Símbolo de la criptomoneda (ej. 'BTC').
        intervalo_minutos (int): Período en minutos para analizar la tendencia previa.

    Returns:
        dict: Diccionario con información de la tendencia previa.
              Ej: {'tendencia': 'ALCISTA', 'cambio_porcentual_previo': 2.5,
                   'precio_inicio': 70000, 'precio_fin': 71750}
    """
    cambio_previo = cambio_porcentual_precio(simbolo, intervalo_minutos)

    if cambio_previo['cambio_porcentual'] is None:
        return {
            'tendencia': 'DESCONOCIDA',
            'cambio_porcentual_previo': None,
            'precio_inicio': None,
            'precio_fin': None
        }

    cambio_pct = cambio_previo['cambio_porcentual']

    # Determinar tendencia
    if cambio_pct > 2.0:
        tendencia = 'ALCISTA_FUERTE'
    elif cambio_pct > 0.5:
        tendencia = 'ALCISTA'
    elif cambio_pct < -2.0:
        tendencia = 'BAJISTA_FUERTE'
    elif cambio_pct < -0.5:
        tendencia = 'BAJISTA'
    else:
        tendencia = 'LATERAL'

    return {
        'tendencia': tendencia,
        'cambio_porcentual_previo': cambio_pct,
        'precio_inicio': cambio_previo['precio_anterior'],
        'precio_fin': cambio_previo['precio_actual']
    }

####################################################################
#  obtener_senal_cambio_extremo
####################################################################

def obtener_senal_cambio_extremo(
    simbolo: str,
    intervalo_minutos: int = 15,
    umbral_porcentual: float = 1.0,
    confirmar_con_volumen: bool = False,
    umbral_porcentual_volumen: float = 20.0,
    intervalo_ventana_volumen_minutos: int = 30,
    num_ventanas_historicas_volumen: int = 5
) -> dict:
    """
    Genera una señal de trading (COMPRA, VENTA, MANTENER) basada en un cambio porcentual extremo reciente,
    con confirmación opcional por volumen.

    Args:
        simbolo (str): Símbolo de la criptomoneda (ej. 'BTC').
        intervalo_minutos (int): Período en minutos sobre el cual calcular el cambio porcentual.
        umbral_porcentual (float): Umbral porcentual para considerar un cambio como "extremo".
        confirmar_con_volumen (bool): Si es True, la señal de precio se debe confirmar con un aumento de volumen.
        umbral_porcentual_volumen (float): Umbral porcentual para considerar el cambio de volumen como "significativo".
        intervalo_ventana_volumen_minutos (int): Duración de la ventana de análisis de volumen.
        num_ventanas_historicas_volumen (int): Ventanas históricas para el promedio de volumen.

    Returns:
        dict: Un diccionario con el símbolo, precio actual, precio anterior, cambio porcentual y la señal.
              Ej: {'simbolo': 'BTC', 'precio_actual': 70000, 'precio_anterior': 70700,
                   'cambio_porcentual': -1.0, 'cambio_porcentual_volumen': 50.0, 'volumen_confirmado': True, 'senal': 'COMPRA'}
              Ej: {'simbolo': 'BTC', 'precio_actual': 70000, 'precio_anterior': 70700, 'cambio_porcentual': -1.0,
                   'volumen_actual': 1500, 'volumen_anterior': 1000, 'cambio_porcentual_volumen': 50.0,
                   'volumen_confirmado': True, 'senal': 'COMPRA'}
    """
    cambio = cambio_porcentual_precio(simbolo, intervalo_minutos)

    # Analizar tendencia previa (período más largo para contexto)
    tendencia_info = analizar_tendencia_previa(simbolo, intervalo_minutos * 4)  # 4x el intervalo actual

    # Inicializar el diccionario de retorno
    resultado = {
        'simbolo': simbolo,
        'precio_actual': cambio['precio_actual'],
        'precio_anterior': cambio['precio_anterior'],
        'cambio_porcentual': cambio['cambio_porcentual'],
        'tendencia_previa': tendencia_info['tendencia'],
        'cambio_porcentual_previo': tendencia_info['cambio_porcentual_previo'],
        'volumen_total_actual': None,
        'volumen_promedio_historico': None,
        'cambio_porcentual_volumen': None,
        'volumen_confirmado': None,
        'volumen_compra': None,
        'volumen_venta': None,
        'volumen_sin_cambio': None,
        'minutos_subida': None,
        'minutos_bajada': None,
        'minutos_sin_cambio': None,
        'presion_compradora_pct': None,
        'presion_vendedora_pct': None,
        'interpretacion_presion': None,
        'conclusion': None,
        'senal': 'MANTENER'
    }
    cambio_porcentual = resultado['cambio_porcentual']

    if cambio_porcentual is None:
        # El warning ya se ha logueado en cambio_porcentual_precio si los datos son insuficientes
        resultado['senal'] = 'DATOS INSUFICIENTES'
        return resultado

    senal_precio = "MANTENER"
    if cambio_porcentual <= -umbral_porcentual:
        senal_precio = "COMPRA"
    elif cambio_porcentual >= umbral_porcentual:
        senal_precio = "VENTA"

    # SIEMPRE calculamos el volumen (para mostrarlo), independientemente de la señal de precio
    logger.info(f"Analizando volumen para {simbolo}...")
    analisis_volumen = cambio_porcentual_volumen(simbolo, intervalo_minutos, num_ventanas_historicas_volumen)
    cambio_volumen = analisis_volumen.get('cambio_porcentual_volumen')
    resultado['volumen_total_actual'] = analisis_volumen.get('volumen_total_actual')
    resultado['volumen_promedio_historico'] = analisis_volumen.get('volumen_promedio_historico')
    resultado['cambio_porcentual_volumen'] = cambio_volumen

    # SIEMPRE calculamos la presión compradora (para mostrarlo)
    logger.info(f"Analizando presión compradora para {simbolo}...")
    presion = calcular_presion_compradora(simbolo, intervalo_minutos)
    resultado['volumen_compra'] = presion.get('volumen_compra')
    resultado['volumen_venta'] = presion.get('volumen_venta')
    resultado['volumen_sin_cambio'] = presion.get('volumen_sin_cambio')
    resultado['minutos_subida'] = presion.get('minutos_subida')
    resultado['minutos_bajada'] = presion.get('minutos_bajada')
    resultado['minutos_sin_cambio'] = presion.get('minutos_sin_cambio')
    resultado['presion_compradora_pct'] = presion.get('presion_compradora_pct')
    resultado['presion_vendedora_pct'] = presion.get('presion_vendedora_pct')
    resultado['interpretacion_presion'] = presion.get('interpretacion')

    # Si no se requiere confirmación de volumen, devolvemos la señal de precio directamente
    if not confirmar_con_volumen:
        resultado['senal'] = senal_precio
        resultado['volumen_confirmado'] = None
        # Generar conclusión basada en señal + presión
        resultado['conclusion'] = generar_conclusion_senal(senal_precio, resultado['presion_compradora_pct'])
        logger.info(f"Señal para {simbolo}: Precio actual={resultado['precio_actual']:.2f}, Precio anterior={resultado['precio_anterior']:.2f}, Cambio={cambio_porcentual:.2f}%, Señal={resultado['senal']} (sin confirmación de volumen)")
        return resultado

    # Si la señal de precio es MANTENER, no hay nada que confirmar con volumen
    if senal_precio == "MANTENER":
        resultado['senal'] = senal_precio
        resultado['volumen_confirmado'] = None
        resultado['conclusion'] = generar_conclusion_senal(senal_precio, resultado['presion_compradora_pct'])
        logger.info(f"Señal para {simbolo}: MANTENER (cambio {cambio_porcentual:.2f}% no supera umbral {umbral_porcentual}%)")
        return resultado

    # Si hay señal de precio (COMPRA/VENTA) y se requiere confirmación, validamos con volumen
    logger.info(f"Señal de precio '{senal_precio}' detectada para {simbolo}. Verificando confirmación de volumen...")

    # Si no hay datos de volumen disponibles, proceder con la señal de precio pero avisar
    if cambio_volumen is None:
        resultado['volumen_confirmado'] = None
        resultado['senal'] = senal_precio
        logger.warning(f"Datos de volumen insuficientes para {simbolo}. Señal basada solo en precio: {senal_precio}")
    elif cambio_volumen >= umbral_porcentual_volumen:
        resultado['volumen_confirmado'] = True
        resultado['senal'] = senal_precio # Confirmamos la señal de precio
        logger.info(f"Volumen CONFIRMADO para {simbolo}. Cambio vol: {cambio_volumen:.2f}% >= {umbral_porcentual_volumen}%. Señal final: {resultado['senal']}.")
    else:
        resultado['volumen_confirmado'] = False
        resultado['senal'] = 'MANTENER' # No hay confirmación, revertimos a MANTENER
        logger.info(f"Volumen NO confirmado para {simbolo}. Cambio vol: {cambio_volumen:.2f}% < {umbral_porcentual_volumen}%. Señal revertida a MANTENER.")

    # Generar conclusión basada en señal final + presión
    resultado['conclusion'] = generar_conclusion_senal(resultado['senal'], resultado['presion_compradora_pct'])

    return resultado

####################################################################
#  obtener_senal_cruce_medias_moviles
####################################################################

def obtener_senal_cruce_medias_moviles(
    simbolo: str,
    df_historico: pd.DataFrame,
    periodo_sma_rapida: int = 50,
    periodo_sma_lenta: int = 200
) -> dict:
    """
    Genera una señal de trading basada en el cruce de dos medias móviles simples (SMA).

    Args:
        simbolo (str): Símbolo de la criptomoneda.
        df_historico (pd.DataFrame): DataFrame con los datos históricos.
        periodo_sma_rapida (int): Período para la SMA rápida.
        periodo_sma_lenta (int): Período para la SMA lenta.

    Returns:
        dict: Un diccionario con la señal y datos relevantes.
    """
    if df_historico.empty or len(df_historico) < periodo_sma_lenta:
        return {'senal': 'DATOS INSUFICIENTES'}

    # Calcular ambas SMAs
    sma_rapida = df_historico['precio'].rolling(window=periodo_sma_rapida).mean()
    sma_lenta = df_historico['precio'].rolling(window=periodo_sma_lenta).mean()

    # Tomar los dos últimos valores para detectar el cruce
    sma_rapida_anterior = sma_rapida.iloc[-2]
    sma_rapida_actual = sma_rapida.iloc[-1]
    sma_lenta_anterior = sma_lenta.iloc[-2]
    sma_lenta_actual = sma_lenta.iloc[-1]

    senal = "MANTENER"
    # Cruce alcista: la rápida estaba por debajo y ahora está por encima de la lenta.
    if sma_rapida_anterior < sma_lenta_anterior and sma_rapida_actual > sma_lenta_actual:
        senal = "COMPRA"
    # Cruce bajista: la rápida estaba por encima y ahora está por debajo de la lenta.
    elif sma_rapida_anterior > sma_lenta_anterior and sma_rapida_actual < sma_lenta_actual:
        senal = "VENTA"

    return {'senal': senal, 'sma_rapida': sma_rapida_actual, 'sma_lenta': sma_lenta_actual}
