# src/backtesting.py

import pandas as pd
from datetime import datetime
from config import logger, DB_PATH
from database import get_data_from_db_in_range
import matplotlib.pyplot as plt
import io
import base64
import matplotlib.dates as mdates


def run_backtest(
    simbolo: str,
    fecha_inicio_str: str,
    fecha_fin_str: str,
    capital_inicial: float,
    funcion_estrategia,
    parametros_estrategia: dict
):
    """
    Ejecuta un backtest para una estrategia de trading sobre datos históricos.

    Args:
        simbolo (str): Símbolo de la criptomoneda (ej. 'BTC').
        fecha_inicio_str (str): Fecha de inicio en formato 'YYYY-MM-DD'.
        fecha_fin_str (str): Fecha de fin en formato 'YYYY-MM-DD'.
        capital_inicial (float): Capital inicial para la simulación.
        funcion_estrategia (function): La función de estrategia a probar (ej. obtener_senal_cambio_extremo).
        parametros_estrategia (dict): Parámetros para la función de estrategia.

    Returns:
        dict: Un diccionario con los resultados y métricas del backtest.
    """
    logger.info(f"Iniciando backtest para {simbolo} de {fecha_inicio_str} a {fecha_fin_str} con {capital_inicial}€")

    # 1. Cargar datos históricos
    # Convertir strings a objetos datetime
    fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
    fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')

    logger.info(f"Obteniendo datos para el backtest desde la base de datos...")
    todos_los_datos = get_data_from_db_in_range(simbolo, fecha_inicio, fecha_fin)

    if not todos_los_datos or not todos_los_datos['timestamps']:
        logger.error(f"No se pudieron obtener datos históricos para {simbolo}.")
        return {"error": "No se encontraron datos históricos suficientes para el backtest."}

    df = pd.DataFrame(todos_los_datos)
    # Renombrar la columna 'timestamps' a 'timestamp' para consistencia
    df.rename(columns={'timestamps': 'fecha_hora', 'prices': 'precio', 'volumes': 'volumen', 'volumen_eur': 'cap_mercado'}, inplace=True)

    df['fecha_hora'] = pd.to_datetime(df['fecha_hora'], unit='s')

    if df.empty:
        logger.error(f"No hay datos en el rango de fechas especificado: {fecha_inicio_str} a {fecha_fin_str}.")
        return {"error": "No hay datos en el rango de fechas especificado."}

    logger.info(f"Datos cargados para el backtest: {len(df)} filas desde {df['fecha_hora'].min()} hasta {df['fecha_hora'].max()}")

    # 2. Inicializar estado del portafolio
    efectivo = capital_inicial
    tenencias = 0.0
    operaciones = []
    historial_valor_portafolio = []

    # --- Nueva Máquina de Estados para la Lógica de Seguimiento ---
    # ESTADO_NEUTRAL: Buscando una señal de entrada (compra o venta inicial).
    # POSICION_ABIERTA_COMPRA: Se ha comprado, buscando vender (por Take Profit o Stop Loss).
    # POSICION_CERRADA_SHORT: Se ha vendido, buscando recomprar (por Take Profit o Stop Loss).
    estado_actual = "ESTADO_NEUTRAL"
    precio_entrada = 0.0
    cantidad_vendida_para_recompra = 0.0
    # --- Fin de la nueva lógica de estado ---


    # 3. Iterar a través de los datos y aplicar la estrategia
    # Para simular el comportamiento de las funciones de análisis que consultan la BD,
    # Esto es una simplificación. Una refactorización futura podría hacer que la estrategia acepte un DataFrame.
    for i in range(len(df)):
        # Para simular `get_data_from_db`, pasamos los datos hasta el punto actual `i`
        # a una función `mock_get_data_from_db` que la estrategia pueda usar.
        # Por simplicidad en este ejemplo, vamos a re-implementar la lógica de la señal aquí.
        
        # --- Lógica de la estrategia (simplificada para el ejemplo) ---
        # Creamos un DataFrame con los datos históricos hasta el punto actual
        # para que la función de estrategia pueda trabajar como si consultara la BD en ese instante.
        df_historico_actual = df.iloc[:i+1]
        
        precio_actual = df['precio'].iloc[i]
        timestamp_actual = df['fecha_hora'].iloc[i]

        # --- Lógica de la Máquina de Estados ---

        if estado_actual == "ESTADO_NEUTRAL":
            # 1. BUSCAR SEÑAL DE ENTRADA

            # --- Lógica de Filtro de Tendencia ---
            usar_filtro_tendencia = parametros_estrategia.get('usar_filtro_tendencia', False)
            if usar_filtro_tendencia:
                periodo_sma_tendencia = parametros_estrategia.get('periodo_sma_tendencia', 200)
                # Necesitamos suficientes datos para la SMA
                if len(df_historico_actual) > periodo_sma_tendencia:
                    sma_largo_plazo = df_historico_actual['precio'].rolling(window=periodo_sma_tendencia).mean().iloc[-1]
                    # En tendencia bajista (precio por debajo de la media larga), no permitimos compras.
                    if precio_actual < sma_largo_plazo:
                        valor_portafolio = efectivo + (tenencias * precio_actual)
                        historial_valor_portafolio.append({'fecha_hora': timestamp_actual, 'valor': valor_portafolio})
                        continue # Saltar a la siguiente iteración, no buscar señal de compra.

            # Pasamos todos los parámetros directamente. La función de estrategia se encargará de usar los que necesite.
            resultado_senal = funcion_estrategia(simbolo, df_historico=df_historico_actual, **parametros_estrategia)
            senal = resultado_senal['senal']

            if senal == "COMPRA" and efectivo > 0:
                # Entrar en posición LONG
                cantidad_a_comprar = efectivo / precio_actual
                tenencias = cantidad_a_comprar
                efectivo = 0
                estado_actual = "POSICION_ABIERTA_COMPRA"
                precio_entrada = precio_actual
                operaciones.append({'fecha_hora': timestamp_actual, 'tipo': 'COMPRA', 'precio': precio_actual, 'cantidad': cantidad_a_comprar, 'motivo': 'ENTRADA_ESTRATEGIA'})
                logger.info(f"Backtest: ENTRADA COMPRA. COMPRA de {cantidad_a_comprar:.6f} {simbolo} a {precio_actual:.2f}€")

            elif senal == "VENTA" and tenencias > 0:
                # Entrar en posición "SHORT" (vendemos para recomprar más barato)
                cantidad_vendida_para_recompra = tenencias
                efectivo += tenencias * precio_actual
                tenencias = 0.0
                estado_actual = "POSICION_CERRADA_VENTA"
                precio_entrada = precio_actual
                operaciones.append({'fecha_hora': timestamp_actual, 'tipo': 'VENTA', 'precio': precio_actual, 'cantidad': cantidad_vendida_para_recompra, 'motivo': 'ENTRADA_ESTRATEGIA'})
                logger.info(f"Backtest: ENTRADA VENTA. VENTA de {cantidad_vendida_para_recompra:.6f} {simbolo} a {precio_actual:.2f}€")

        elif estado_actual == "POSICION_ABIERTA_COMPRA":
            # 2. SEGUIMIENTO DE POSICIÓN LONG (buscamos vender)
            tp_pct = parametros_estrategia.get('toma_ganancias_pct_despues_compra', 3.0)
            sl_pct = parametros_estrategia.get('parada_perdidas_pct_despues_compra', 1.5)
            
            cambio_desde_compra = ((precio_actual - precio_entrada) / precio_entrada) * 100

            if cambio_desde_compra >= tp_pct:
                # Take Profit: Vender todo
                efectivo += tenencias * precio_actual
                cantidad_vendida = tenencias
                tenencias = 0
                estado_actual = "ESTADO_NEUTRAL"
                operaciones.append({'fecha_hora': timestamp_actual, 'tipo': 'VENTA', 'precio': precio_actual, 'cantidad': cantidad_vendida, 'motivo': 'TOMA_GANANCIAS'})
                logger.info(f"Backtest: TOMA GANANCIAS (COMPRA). VENTA de {cantidad_vendida:.6f} {simbolo} a {precio_actual:.2f}€. Ganancia: {cambio_desde_compra:.2f}%")
            
            elif cambio_desde_compra <= -sl_pct:
                # Stop Loss: Vender todo
                efectivo += tenencias * precio_actual
                cantidad_vendida = tenencias
                tenencias = 0
                estado_actual = "ESTADO_NEUTRAL"
                operaciones.append({'fecha_hora': timestamp_actual, 'tipo': 'VENTA', 'precio': precio_actual, 'cantidad': cantidad_vendida, 'motivo': 'PARADA_PERDIDAS'})
                logger.info(f"Backtest: PARADA PERDIDAS (COMPRA). VENTA de {cantidad_vendida:.6f} {simbolo} a {precio_actual:.2f}€. Pérdida: {cambio_desde_compra:.2f}%")

        elif estado_actual == "POSICION_CERRADA_VENTA":
            # 3. SEGUIMIENTO DE POSICIÓN "SHORT" (buscamos recomprar)
            tp_pct = parametros_estrategia.get('toma_ganancias_pct_despues_venta', 3.0)
            sl_pct = parametros_estrategia.get('parada_perdidas_pct_despues_venta', 1.5)

            cambio_desde_venta = ((precio_actual - precio_entrada) / precio_entrada) * 100

            if cambio_desde_venta <= -tp_pct:
                # Take Profit: Recomprar la misma cantidad que se vendió
                coste_recompra = cantidad_vendida_para_recompra * precio_actual
                if efectivo >= coste_recompra:
                    tenencias += cantidad_vendida_para_recompra
                    efectivo -= coste_recompra
                    estado_actual = "ESTADO_NEUTRAL"
                    operaciones.append({'fecha_hora': timestamp_actual, 'tipo': 'COMPRA', 'precio': precio_actual, 'cantidad': cantidad_vendida_para_recompra, 'motivo': 'TOMA_GANANCIAS'})
                    logger.info(f"Backtest: TOMA GANANCIAS (VENTA). RECOMPRA de {cantidad_vendida_para_recompra:.6f} {simbolo} a {precio_actual:.2f}€. Ganancia en precio: {-cambio_desde_venta:.2f}%")
                else:
                    logger.warning("Toma de ganancias (VENTA) no ejecutada por falta de efectivo.")

            elif cambio_desde_venta >= sl_pct:
                # Stop Loss: Recomprar para limitar la pérdida de oportunidad
                coste_recompra = cantidad_vendida_para_recompra * precio_actual
                if efectivo >= coste_recompra:
                    tenencias += cantidad_vendida_para_recompra
                    efectivo -= coste_recompra
                    estado_actual = "ESTADO_NEUTRAL"
                    operaciones.append({'fecha_hora': timestamp_actual, 'tipo': 'COMPRA', 'precio': precio_actual, 'cantidad': cantidad_vendida_para_recompra, 'motivo': 'PARADA_PERDIDAS'})
                    logger.info(f"Backtest: PARADA PERDIDAS (VENTA). RECOMPRA de {cantidad_vendida_para_recompra:.6f} {simbolo} a {precio_actual:.2f}€. Pérdida de oportunidad: {cambio_desde_venta:.2f}%")
                else:
                    logger.warning("Parada de pérdidas (VENTA) no ejecutada por falta de efectivo.")

        valor_portafolio = efectivo + (tenencias * precio_actual)
        historial_valor_portafolio.append({'fecha_hora': timestamp_actual, 'valor': valor_portafolio})

    # 4. Calcular métricas finales
    valor_final_portafolio = historial_valor_portafolio[-1]['valor']
    retorno_total_abs = valor_final_portafolio - capital_inicial
    retorno_total_pct = (retorno_total_abs / capital_inicial) * 100 if capital_inicial > 0 else 0
    
    retorno_compra_y_mantiene = (df['precio'].iloc[-1] / df['precio'].iloc[0] - 1) * 100

    resultados = {
        "periodo_analizado": f"{fecha_inicio_str} a {fecha_fin_str}",
        "simbolo": simbolo,
        "estrategia": funcion_estrategia.__name__,
        "parametros_estrategia": parametros_estrategia,
        "capital_inicial": capital_inicial,
        "valor_final_portafolio": round(valor_final_portafolio, 2),
        "retorno_total_abs": round(retorno_total_abs, 2),
        "retorno_total_pct": round(retorno_total_pct, 2),
        "retorno_buy_and_hold_pct": round(retorno_compra_y_mantiene, 2),
        "numero_operaciones": len(operaciones),
        "operaciones": operaciones,
    }

    # 5. Generar gráfica del valor del portafolio
    try:
        df_historial = pd.DataFrame(historial_valor_portafolio)
        if not df_historial.empty:
            plt.figure(figsize=(12, 6))
            plt.plot(df_historial['fecha_hora'], df_historial['valor'], label='Valor del Portafolio')
            plt.title(f"Evolución del Portafolio ({simbolo})")
            plt.xlabel("Fecha")
            plt.ylabel("Valor en €")
            plt.grid(True)
            plt.legend()
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
            plt.gcf().autofmt_xdate()

            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
            resultados['grafico_portafolio_base64'] = chart_base64
            logger.info("Gráfica de evolución del portafolio generada y añadida a los resultados.")
    except Exception as e:
        logger.error(f"No se pudo generar la gráfica del portafolio: {e}", exc_info=True)
        resultados['grafico_portafolio_base64'] = None

    logger.info(f"Backtest finalizado. Valor final: {resultados['valor_final_portafolio']}€. Retorno: {resultados['retorno_total_pct']}%")

    return resultados


def obtener_senal_cambio_extremo_backtest(
    simbolo: str,
    df_historico: pd.DataFrame,
    intervalo_minutos: int = 15,
    umbral_porcentual: float = 1.0,
    confirmar_con_volumen: bool = False,
    umbral_porcentual_volumen: float = 30.0,
    intervalo_ventana_volumen_minutos: int = 30,
    num_ventanas_historicas_volumen: int = 5,
    **kwargs # Captura argumentos extra para no dar error
) -> dict:
    """
    Versión de `obtener_senal_cambio_extremo` adaptada para el backtesting.
    Recibe un DataFrame con los datos históricos en lugar de consultar la base de datos.
    """
    # El punto de datos actual es el último en el DataFrame histórico
    if df_historico.empty:
        return {'senal': 'DATOS INSUFICIENTES'}

    punto_actual = df_historico.iloc[-1]
    precio_actual = punto_actual['precio']
    timestamp_actual = punto_actual['fecha_hora']

    # --- Lógica de cambio de precio ---
    limite_timestamp_pasado = timestamp_actual - pd.Timedelta(minutes=intervalo_minutos)
    df_periodo_precio = df_historico[(df_historico['fecha_hora'] < timestamp_actual) & (df_historico['fecha_hora'] >= limite_timestamp_pasado)]

    if df_periodo_precio.empty:
        return {'senal': 'MANTENER', 'cambio_porcentual': 0, 'volumen_total_actual': None, 'volumen_promedio_historico': None}

    precio_anterior = df_periodo_precio['precio'].iloc[0]
    cambio_porcentual = ((precio_actual - precio_anterior) / precio_anterior) * 100 if precio_anterior != 0 else 0

    senal_precio = "MANTENER"
    if cambio_porcentual <= -umbral_porcentual:
        senal_precio = "COMPRA"
    elif cambio_porcentual >= umbral_porcentual:
        senal_precio = "VENTA"

    if senal_precio == "MANTENER" or not confirmar_con_volumen:
        return {'senal': senal_precio, 'cambio_porcentual': cambio_porcentual, 'volumen_total_actual': None, 'volumen_promedio_historico': None}

    # --- Lógica de confirmación de volumen ---
    # Calcular el volumen actual en el intervalo especificado
    limite_timestamp_volumen = timestamp_actual - pd.Timedelta(minutes=intervalo_ventana_volumen_minutos)
    df_volumen_actual = df_historico[(df_historico['fecha_hora'] < timestamp_actual) & (df_historico['fecha_hora'] >= limite_timestamp_volumen)]
    volumen_actual = df_volumen_actual['volumen'].sum()

    # Calcular el volumen promedio histórico
    volumenes_historicos = []
    for j in range(1, num_ventanas_historicas_volumen + 1):
        limite_inferior = timestamp_actual - pd.Timedelta(minutes=intervalo_ventana_volumen_minutos * (j + 1))
        limite_superior = timestamp_actual - pd.Timedelta(minutes=intervalo_ventana_volumen_minutos * j)
        df_volumen_historico = df_historico[(df_historico['fecha_hora'] >= limite_inferior) & (df_historico['fecha_hora'] < limite_superior)]
        volumenes_historicos.append(df_volumen_historico['volumen'].sum())

    if not volumenes_historicos:
        return {'senal': 'MANTENER', 'cambio_porcentual': cambio_porcentual, 'volumen_total_actual': volumen_actual, 'volumen_promedio_historico': 0}

    volumen_promedio_historico = sum(volumenes_historicos) / len(volumenes_historicos)

    senal_final = "MANTENER"
    if volumen_promedio_historico > 0:
        cambio_porcentual_volumen = ((volumen_actual - volumen_promedio_historico) / volumen_promedio_historico) * 100
        if cambio_porcentual_volumen >= umbral_porcentual_volumen:
            senal_final = senal_precio  # Confirmado

    return {
        'senal': senal_final,
        'cambio_porcentual': cambio_porcentual,
        'volumen_total_actual': volumen_actual,
        'volumen_promedio_historico': volumen_promedio_historico
    }

def obtener_senal_cruce_medias_moviles_backtest(
    simbolo: str,
    df_historico: pd.DataFrame,
    periodo_sma_rapida: int = 50,
    periodo_sma_lenta: int = 200,
    **kwargs # Captura argumentos extra para no dar error
) -> dict:
    """
    Versión de `obtener_senal_cruce_medias_moviles` adaptada para el backtesting.
    """
    # Necesitamos al menos datos para la SMA lenta + 1 para comparar el cruce
    if df_historico.empty or len(df_historico) < periodo_sma_lenta + 1:
        return {'senal': 'DATOS INSUFICIENTES', 'cambio_porcentual': 0, 'volumen_total_actual': None, 'volumen_promedio_historico': None}

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

    # Devolvemos un diccionario compatible con el motor de backtesting
    return {'senal': senal, 'cambio_porcentual': 0, 'volumen_total_actual': None, 'volumen_promedio_historico': None}
