# charts.py
import matplotlib.pyplot as plt
import io
import base64
from config import logger
from datetime import datetime, timezone  # Importar timezone
import matplotlib.dates as mdates  # Importar mdates
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.io as pio
from config import logger, DB_PATH
from database import datos_comparados
import plotly.graph_objects as go
from analysis import calculate_sma



def generate_chart(data, title="Gráfica de precios"):
    """
    Genera una gráfica de precios con el eje X formateado en hh:mm y la convierte en una imagen para enviar por API.

    Args:
        data (list): Lista de precios u otros datos a graficar.
        title (str, optional): Título de la gráfica. Defaults to "Gráfica de precios".

    Returns:
        str: Imagen codificada en base64.
    """

    if data is None:
        logger.error("No se han recibido datos para generar la gráfica.")
        return None

    try:
        logger.info("Generando gráfica...")

        # Asegurarse de que 'data' contiene las claves necesarias
        if not all(key in data for key in ['timestamps', 'prices']):
            raise ValueError("El diccionario debe contener las claves 'timestamps' y 'prices'")

        timestamps = data['timestamps']
        prices = data['prices']

        # logger.info(f"Timestamps recibidos: {timestamps}")
        # logger.info(f"Precios recibidos: {prices}")

        # Convertir los timestamps Unix a objetos datetime (forma recomendada)
        # datetimes = [datetime.utcfromtimestamp(ts) for ts in timestamps]  # Deprecated
        datetimes = [datetime.fromtimestamp(ts, tz=timezone.utc) for ts in timestamps]

        # Crear la gráfica
        plt.figure(figsize=(10, 5))
        plt.plot(datetimes, prices)
        plt.title(title)
        plt.xlabel("Tiempo")
        plt.ylabel("Precio")
        plt.grid(True)

        # Formatear el eje X para mostrar hh:mm
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gcf().autofmt_xdate()  # Rota las etiquetas si son muy largas para que no se solapen

        # Guardar la gráfica en un buffer en memoria
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png')
        img_buf.seek(0)
        logger.info("Gráfica generada exitosamente.")

        # Convertir la imagen a base64
        img_base64 = base64.b64encode(img_buf.getvalue()).decode('utf-8')
        logger.info(f"Imagen codificada en Base64 exitosamente.")

        plt.close()

        return img_base64

    except Exception as e:
        print(f"Error generando la gráfica: {e}")
        logger.info(f"Error generando la gráfica: {e}")
        return None

def generar_grafica_comparativa(monedas, title="Comparación de precios", returnBase64=False):
    """
    Función para generar una gráfica comparativa de los precios normalizados de varias criptomonedas.

    Parámetros:
    monedas (list): Lista de símbolos de criptomonedas (por ejemplo, ['BTC', 'ETH', 'DOT']).
    title (str): Título de la gráfica. El valor por defecto es "Comparación de precios".

    Esta función:
    1. Obtiene los datos de las criptomonedas especificadas en la lista 'monedas'.
    2. Convierte los datos en un DataFrame de pandas.
    3. Normaliza los precios entre 0 y 1 para facilitar la comparación visual.
    4. Genera una gráfica de líneas con Plotly, mostrando la evolución de los precios normalizados de las criptomonedas.
    """

    # Obtener los datos
    data = datos_comparados(monedas)

    # Convertir la lista de diccionarios a un DataFrame solo cuando sea necesario
    df = pd.DataFrame(data)

    # Ahora puedes usar df para crear gráficos o hacer análisis
    print(df)

    # Convertir timestamp a datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

    # Normalizar los precios entre 0 y 1
    df['price_normalized'] = df.groupby('symbol')['price'].transform(lambda x: (x - x.min()) / (x.max() - x.min()))

    # Graficar con los valores normalizados, pero mostrar el precio original en el hover
    fig = px.line(df, x='timestamp', y='price_normalized', color='symbol',
                labels={'price_normalized': 'Precio (Normalizado)', 'timestamp': 'Fecha'},
                title=title,
                hover_data={'price_normalized': False, 'price': ':.2f'}) #aquí esta el cambio
    
    fig.update_traces(hovertemplate="<b>%{fullData.name}</b><br>Fecha: %{x}<br>Precio: %{customdata[0]:.2f}<br>Precio Normalizado: %{y:.2f}")

    if returnBase64:
        # Convertir la gráfica a base64
        img_buf = io.BytesIO()
        pio.write_image(fig, img_buf, format="png") #Use pio.write_image
        img_buf.seek(0)
        img_base64 = base64.b64encode(img_buf.getvalue()).decode('utf-8')
        return img_base64
    else: 
        # Mostrar la gráfica
        fig.show()





def generar_grafica_precio_y_sma(symbol: str, period: int = 10, limit: int = 1000):
    # Calcular los datos y la SMA
    df = calculate_sma(symbol, period, limit)
    
    if df is None or df.empty:
        print("No hay datos para mostrar.")
        return
    
    # Crear la figura
    fig = go.Figure()

    # Añadir la serie de precios
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['price'], mode='lines', name='Precio', line=dict(color='blue')))

    # Añadir la serie de la SMA
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['sma'], mode='lines', name=f'SMA {period}', line=dict(color='red', dash='dash')))
    
    # Títulos y etiquetas
    fig.update_layout(
        title=f'Precio y Media Móvil Simple (SMA) de {symbol}',
        xaxis_title='Timestamp',
        yaxis_title='Precio (USD)',
        xaxis=dict(tickangle=45)
    )
    
    # Mostrar la gráfica
    fig.show()


