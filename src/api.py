from flask import Flask, jsonify, request  # Importa 'request' aquí
import requests  # También necesitas importar 'requests' para hacer la solicitud a Binance
from main import fetch_and_insert_data_last_30min, get_crypto_data  # Importamos el método y get_crypto_data
import subprocess
from config import logger, FAVORITES_FILTER, PORTFOLIO_FILTER
from analisis_rendimineto import calcular_rendimiento_portafolio_total, obtener_portafolio # Importamos la nueva función
from database import get_data_from_db, obtener_precio_portafolio, limpiar_crypto_data, insertar_operacion
from charts import generate_chart, generar_grafica_comparativa
from analysis import obtener_senal_cambio_extremo, cambio_porcentual_precio, cambio_porcentual_volumen, obtener_senal_cruce_medias_moviles
import base64
import papermill as pm # Importar papermill
import matplotlib.pyplot as plt
import io

# IA

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Importar el nuevo módulo de backtesting
from backtesting import run_backtest, obtener_senal_cambio_extremo_backtest, obtener_senal_cruce_medias_moviles_backtest

# Importar el creador del agente desde el módulo correspondiente
from ia.grog_agente import crear_agente_kryptonite

'''
Endpoint que llama a fetch_and_insert_data_last_30min, y carga los datos de las criptomonedas favoritas de los últimos 30min. con intervalos de 5min.
'''
@app.route('/run', methods=['POST'])
def run_script():
    try:
        fetch_and_insert_data_last_30min(FAVORITES_FILTER)
        return jsonify({"message": "✅🪨 Carga de datos de FAVORITOS se ha ejecutado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/valor', methods=['GET'])
def obtener_valor():
    """
    Endpoint para obtener el precio actual de una criptomoneda desde Binance.
    
    Parámetros:
        - crypto (str): Símbolo de la criptomoneda (por ejemplo, BTC).
        - timeframe (str, opcional): El intervalo de tiempo para la vela (ej. '1m', '1h', '1d'). Por defecto es '1d'.

    Retorna:
        - JSON con el símbolo y el precio actual de la criptomoneda.
        - Mensaje de error si falta el parámetro o Binance no devuelve datos.
    """
    
    # Obtener el símbolo de la criptomoneda desde los parámetros de la URL
    crypto = request.args.get('crypto')  
    if not crypto:
        return jsonify({"error": "Falta el parámetro 'crypto' en la consulta"}), 400  # Error 400: Petición incorrecta

    # Obtener el timeframe desde los parámetros, con '1d' como valor por defecto
    timeframe = request.args.get('timeframe', '1d')

    # Formatear el símbolo para Binance (Ejemplo: BTC → BTCUSDT)
    symbol = f"{crypto.upper()}"

    try:
        # Llamamos a la función get_crypto_data para obtener los datos de la criptomoneda
        price, volume, market_cap, media_movil = get_crypto_data(symbol,'1d',1)
        price, volume, market_cap, media_movil = get_crypto_data(symbol, timeframe, 1)

        # Verificar si obtuvimos los datos correctamente
        if price is not None:
            return jsonify({
                "symbol": crypto.upper(),
                "price": price,
                "volume": volume,
                "market_cap": market_cap,
                "media_movil": media_movil
            }), 200  # Respuesta 200 OK
        else:
            return jsonify({"error": f"No se encontraron datos para {crypto} en Binance"}), 404  # Error 404: No encontrado

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Error 500: Problema interno del servidor



@app.route('/grafica24h', methods=['GET'])
def get_chart():

     # Obtener el símbolo de la criptomoneda desde los parámetros de la URL
    crypto = request.args.get('crypto')  
    if not crypto:
        #return jsonify({"error": "Falta el parámetro 'crypto' en la consulta"}), 400  # Error 400: Petición incorrecta
        monedas_a_comparar = obtener_portafolio() # Llama a la función para obtener el portafolio

        # Llamar a la función para generar la gráfica comparativa

        chart_image = generar_grafica_comparativa(monedas_a_comparar, title="Comparación de Precios de " + ", ".join(monedas_a_comparar) , returnBase64=True)
        return jsonify({"chart": chart_image})
    else:
        # Consultar los datos de la base de datos
        data = get_data_from_db(crypto, window=1440)

        if data is None:
            return jsonify({"error": "No se encontraron datos para la criptomoneda solicitada"}), 404
        else:

            # Generar la gráfica
            chart_image = generate_chart(data, "Gráfica de precios 24h de la 🪙 " + crypto.upper())
            #logger.info(f"Imagen recibida en Base64 exitosamente")
            #logger.info(f"Imagen recibida en Base64 exitosamente.{chart_image}")

            if chart_image is None:
                return jsonify({"error": "La imagen no está disponibles"}), 400

            # Convertir la gráfica en base64 para enviar por API
            #chart_image_base64 = base64.b64encode(chart_image).decode('utf-8')

            # Retornar la gráfica como una respuesta JSON con la imagen codificada
            return jsonify({"chart": chart_image})



@app.route('/portafolio', methods=['GET'])
def get_portafolio():
    """
    Endpoint para obtener el rendimiento del portafolio de criptomonedas.
    Calcula para cada activo la cantidad, coste, valor actual y rentabilidad.

    Parámetros opcionales (query):
        - analisis (str): Si es 'completo', incluye análisis enriquecido con alertas y métricas.
                         Si no se especifica o es 'basico', devuelve solo los datos base (compatibilidad).

    Respuesta:
    - Modo básico: Lista de diccionarios con datos de cada cripto (formato original).
    - Modo completo: Objeto con 'portfolio', 'totales' y 'analisis'.
    - Mensaje de error si ocurre algún problema.
    """
    try:
        # Obtener parámetro de query (por defecto: modo básico para retrocompatibilidad)
        modo_analisis = request.args.get('analisis', 'basico').lower()

        # Llamamos a la función que ya hace todo el cálculo base
        resultados_portafolio = calcular_rendimiento_portafolio_total()

        # Si se pide análisis completo, enriquecer con análisis avanzado
        if modo_analisis == 'completo':
            from portfolio_analyzer import analizar_portfolio_completo
            resultado_enriquecido = analizar_portfolio_completo(resultados_portafolio)
            return jsonify(resultado_enriquecido), 200
        else:
            # Modo básico: retrocompatible con Node-RED actual
            return jsonify(resultados_portafolio), 200

    except Exception as e:
        logger.error(f"Error en get_portafolio: {e}", exc_info=True)
        return jsonify({"error": "Ocurrió un error interno al calcular el rendimiento del portafolio."}), 500


@app.route('/limpiar', methods=['GET'])
def limpiar_tabla():
    """
    Endpoint para limpiar la tabla crypto_data eliminando datos duplicados.
    """
    try:
        limpiar_crypto_data()
        return jsonify({"message": "Tabla crypto_data limpiada correctamente."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/senal/cambio_extremo', methods=['GET'])
def obtener_senal_cambio_extremo_api():
    """
    Endpoint para obtener una señal de trading basada en un cambio porcentual extremo reciente.
    Estrategia de reversión a la media: detecta movimientos bruscos y asume que el precio volverá
    a su nivel normal (compra en caídas, vende en subidas).

    MEJORAS IMPLEMENTADAS:
    - Confirmación de volumen OPCIONAL (por defecto desactivada)
    - Análisis de tendencia previa para contexto (4x el intervalo de análisis)
    - Ventanas de precio y volumen sincronizadas
    - Umbral de volumen reducido a 20% (más realista)

    Parámetros obligatorios:
        - cripto (str): Símbolo de la criptomoneda (ej. BTC).

    Parámetros opcionales de precio:
        - intervalo_minutos (int): Período en minutos para analizar cambio de precio. Por defecto 15.
                                  Debe ser múltiplo de 5. La tendencia previa se analiza en 4x este valor.
        - umbral_porcentual (float): Umbral % para considerar cambio "extremo". Por defecto 1.0.
                                    Ejemplo: 1.0 = caída/subida del 1%.

    Parámetros opcionales de volumen:
        - confirmar_con_volumen (bool): Si true, requiere aumento de volumen para confirmar señal.
                                       Por defecto false (señal solo por precio).
        - umbral_porcentual_volumen (float): % mínimo de aumento de volumen para confirmar. Por defecto 20.0.
        - num_ventanas_historicas_volumen (int): Ventanas históricas para comparar volumen. Por defecto 3.

    Lógica de decisión:
        - COMPRA: Precio cae >= umbral_porcentual (ej. -1%)
        - VENTA: Precio sube >= umbral_porcentual (ej. +1%)
        - MANTENER: Cambio < umbral O volumen no confirma (si confirmar_con_volumen=true)

    Retorna JSON con:
        - simbolo, precio_actual, precio_anterior, cambio_porcentual
        - tendencia_previa: ALCISTA_FUERTE, ALCISTA, LATERAL, BAJISTA, BAJISTA_FUERTE, DESCONOCIDA
        - cambio_porcentual_previo: % de cambio en período 4x más largo (contexto)
        - volumen_total_actual, volumen_promedio_historico, cambio_porcentual_volumen (si se analiza volumen)
        - volumen_confirmado: true/false/null (si se requiere confirmación)
        - senal: COMPRA, VENTA, MANTENER o DATOS INSUFICIENTES

    Ejemplo de uso:
        /senal/cambio_extremo?cripto=BTC&intervalo_minutos=15&umbral_porcentual=1.0
        /senal/cambio_extremo?cripto=ETH&confirmar_con_volumen=true&umbral_porcentual_volumen=20

    ADVERTENCIA: Esta es una estrategia de reversión (contrarian). Funciona mejor en mercados laterales.
    En tendencias fuertes puede generar pérdidas. USA SIEMPRE CON STOP-LOSS y haz backtesting antes de operar.
    """
    cripto = request.args.get('cripto')
    if not cripto:
        return jsonify({"error": "Falta el parámetro 'cripto' en la consulta"}), 400

    try:
        # Parámetros de precio
        intervalo_minutos = int(request.args.get('intervalo_minutos', '15'))
        umbral_porcentual = float(request.args.get('umbral_porcentual', '1.0'))

        # Parámetros de volumen
        confirmar_con_volumen = request.args.get('confirmar_con_volumen', 'false').lower() == 'true'
        umbral_porcentual_volumen = float(request.args.get('umbral_porcentual_volumen', '20.0'))
        # intervalo_ventana_volumen_minutos ahora se sincroniza automáticamente con intervalo_minutos
        intervalo_ventana_volumen_minutos = intervalo_minutos  # Sincronizado con el análisis de precio
        num_ventanas_historicas_volumen = int(request.args.get('num_ventanas_historicas_volumen', '3'))

        # --- Validaciones ---
        if intervalo_minutos <= 0 or intervalo_minutos % 5 != 0:
            return jsonify({"error": "El parámetro 'intervalo_minutos' debe ser un entero positivo y múltiplo de 5."}), 400
        if umbral_porcentual <= 0:
            return jsonify({"error": "El parámetro 'umbral_porcentual' debe ser un número positivo."}), 400
        if confirmar_con_volumen and umbral_porcentual_volumen < 0:
            return jsonify({"error": "El parámetro 'umbral_porcentual_volumen' debe ser un número positivo o cero."}), 400
    except ValueError:
        return jsonify({"error": "Uno de los parámetros numéricos no es válido (ej. 'intervalo_minutos', 'umbral_porcentual', etc.)."}), 400

    try:
        datos_senal = obtener_senal_cambio_extremo(cripto.upper(), intervalo_minutos, umbral_porcentual, confirmar_con_volumen, umbral_porcentual_volumen, intervalo_ventana_volumen_minutos, num_ventanas_historicas_volumen)
        
        if datos_senal['senal'] == 'DATOS INSUFICIENTES':
            return jsonify({"error": datos_senal['senal'], "detalles": f"No hay suficientes datos para {cripto} en el período de {intervalo_minutos} minutos."}), 404
        return jsonify(datos_senal), 200
    except Exception as e:
        logger.error(f"Error al obtener la señal de cambio extremo para {cripto}: {e}", exc_info=True)
        return jsonify({"error": "Ocurrió un error interno al calcular la señal de cambio extremo."}), 500

@app.route('/backtest', methods=['POST'])
def backtest_strategy():
    """
    Endpoint para ejecutar un backtest de una estrategia de trading.
    Recibe los parámetros del backtest en el cuerpo de la solicitud JSON.
    """
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "Cuerpo de la solicitud JSON vacío o inválido."}), 400

    # Parámetros requeridos
    simbolo = datos.get('symbol')
    fecha_inicio = datos.get('start_date')
    fecha_fin = datos.get('end_date')
    capital_inicial = datos.get('initial_capital')

    # Parámetros de la estrategia
    nombre_estrategia = datos.get('strategy', 'obtener_senal_cambio_extremo')
    parametros_estrategia = datos.get('strategy_params', {})


    if not all([simbolo, fecha_inicio, fecha_fin, capital_inicial]):
        return jsonify({"error": "Faltan parámetros requeridos: symbol, start_date, end_date, initial_capital."}), 400

    # Mapeo de nombres de estrategia a funciones
    estrategias_disponibles = {
        "obtener_senal_cambio_extremo": obtener_senal_cambio_extremo_backtest,
        "cruce_medias_moviles": obtener_senal_cruce_medias_moviles_backtest
    }

    funcion_estrategia = estrategias_disponibles.get(nombre_estrategia)
    if not funcion_estrategia:
        return jsonify({"error": f"Estrategia '{nombre_estrategia}' no reconocida."}), 400

    try:
        resultados = run_backtest(
            simbolo=simbolo,
            fecha_inicio_str=fecha_inicio,
            fecha_fin_str=fecha_fin,
            capital_inicial=float(capital_inicial),
            funcion_estrategia=funcion_estrategia,
            parametros_estrategia=parametros_estrategia
        )
        return jsonify(resultados), 200
    except Exception as e:
        logger.error(f"Error durante la ejecución del backtest: {e}", exc_info=True)
        return jsonify({"error": f"Ocurrió un error interno durante el backtest: {str(e)}"}), 500

@app.route('/nuevaOperacion', methods=['POST'])
def nueva_operacion():
    """
    Endpoint para insertar una nueva operación en la tabla 'operaciones'.

    Cuerpo JSON requerido:
        - timestamp (int): Timestamp Unix en segundos.
        - cripto (str): Símbolo de la criptomoneda (ej. 'BTC').
        - moneda (str): Moneda fiat (ej. 'EUR').
        - tipo (str): Tipo de operación ('Compra', 'Venta', 'Recompensa', 'Recepción', 'Envío').
        - cantidad (float): Cantidad de criptomoneda.
        - precio (float): Precio unitario.
        - valor_total (float): Valor total de la operación.
        - comision (float): Comisión cobrada.
        - origen (str): Plataforma de origen (ej. 'Revolut', 'Binance').

    Retorna:
        - JSON con el id de la operación insertada y mensaje de confirmación.
    """
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "Cuerpo de la solicitud JSON vacío o inválido."}), 400

    # Campos obligatorios
    campos_obligatorios = ['timestamp', 'cripto', 'moneda', 'tipo', 'cantidad', 'precio', 'valor_total', 'comision', 'origen']
    campos_faltantes = [campo for campo in campos_obligatorios if campo not in datos]
    if campos_faltantes:
        return jsonify({"error": f"Faltan campos obligatorios: {', '.join(campos_faltantes)}"}), 400

    # Validar tipos permitidos
    tipos_permitidos = ['Compra', 'Venta', 'Recompensa', 'Recepción', 'Envío']
    if datos['tipo'] not in tipos_permitidos:
        return jsonify({"error": f"Tipo de operación no válido. Valores permitidos: {', '.join(tipos_permitidos)}"}), 400

    try:
        marca_temporal = int(datos['timestamp'])
        cantidad = float(datos['cantidad'])
        precio = float(datos['precio'])
        valor_total = float(datos['valor_total'])
        comision = float(datos['comision'])
    except (ValueError, TypeError):
        return jsonify({"error": "Los campos numéricos (timestamp, cantidad, precio, valor_total, comision) deben ser valores numéricos válidos."}), 400

    try:
        id_operacion = insertar_operacion(
            timestamp=marca_temporal,
            cripto=datos['cripto'],
            moneda=datos['moneda'],
            tipo=datos['tipo'],
            cantidad=cantidad,
            precio=precio,
            valor_total=valor_total,
            comision=comision,
            origen=datos['origen']
        )
        return jsonify({
            "mensaje": f"Operación insertada correctamente.",
            "id_operacion": id_operacion
        }), 201
    except Exception as e:
        logger.error(f"Error al insertar nueva operación: {e}", exc_info=True)
        return jsonify({"error": f"Error al insertar la operación: {str(e)}"}), 500


# ==================== IA CON GROQ - AÑADIDO AL FINAL DEL ARCHIVO ====================

# Cargar variables de entorno desde parametros.env
load_dotenv("parametros.env")   # <--- ¡¡ESTO SÍ!!
modeloIA = os.getenv("GROQ_MODELO")


# LLM ultra rápido
llm = ChatGroq(
    model=modeloIA,   # Modelo actualizado recomendado por Groq
    temperature=0.7,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# Importamos la función que YA usas en /portafolio
from analisis_rendimineto import calcular_rendimiento_portafolio_total

@app.route("/analisis_ia", methods=["GET", "POST"])
def analisis_ia():
    try:
        # Reutilizamos exactamente la misma función que ya tienes funcionando
        datos_portafolio = calcular_rendimiento_portafolio_total()

        # Si por algún motivo viene vacío
        if not datos_portafolio:
            return jsonify({"error": "La función calcular_rendimiento_portafolio_total() devolvió vacío"}), 500

        # Convertimos a JSON bonito (sin importar la estructura exacta)
        import json
        datos_json = json.dumps(datos_portafolio, indent=2, ensure_ascii=False)

        # Pasamos el JSON limpio a la IA
        import json
        datos_json = json.dumps(datos_portafolio, indent=2, ensure_ascii=False)

        prompt = f"""
Eres un analista crypto español, directo. Analiza este portafolio y ten en cuenta:
Que cantidad invertida es poca cantidad y no importa perderla. 
Dame un análisis de cada moneda, máximo tres líneas y un resumen global.
Datos del portafolio:
{datos_json}
"""

        mensajes = [
            SystemMessage(content="Eres un trader español sin filtro, sincero y que va al grano."),
            HumanMessage(content=prompt)
        ]

        respuesta = llm.invoke(mensajes)
        opinion = respuesta.content

        # ←←←←←←←←←←←← CONTROL DE TOKEN'S ←←←←←←←←←←←←
        tokens_entrada = respuesta.usage_metadata["input_tokens"]
        tokens_salida  = respuesta.usage_metadata["output_tokens"]
        tokens_total   = tokens_entrada + tokens_salida
        # ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←


        # ←←←←← AQUÍ LO GUARDAMOS ←←←←←
        from database import guardar_tokens_ia
        guardar_tokens_ia(
            proveedor="groq",
            modelo=modeloIA,
            tokens_entrada=tokens_entrada,
            tokens_salida=tokens_salida
        )

        return jsonify({
            "analisis_ia": opinion,
            "datos_portafolio": datos_portafolio,
            "tokens_entrada": tokens_entrada,
            "tokens_salida": tokens_salida,
            "tokens_total": tokens_total,
            "coste_aprox_euros": round(tokens_total * 0.00000008, 7)  # opcional, pa' flipar
})

    except Exception as e:
        logger.error(f"Error en analisis_ia: {e}", exc_info=True)
        return jsonify({"error": f"IA ha petado: {str(e)}"}), 500
    

# ==================== IA: ANÁLISIS DE SENTIMIENTO DE NOTICIAS ====================

# Importamos el cliente de la API de noticias
from newsapi import NewsApiClient

@app.route("/sentimiento_noticias", methods=["GET"])
def sentimiento_noticias():
    """
    Endpoint para obtener el sentimiento de las noticias recientes sobre una criptomoneda.
    Usa NewsAPI para buscar titulares y Groq para clasificarlos.

    Parámetros:
        - cripto (str): Símbolo de la criptomoneda (ej. BTC).
    """
    cripto = request.args.get('cripto')
    if not cripto:
        return jsonify({"error": "Falta el parámetro 'cripto' en la consulta"}), 400

    # Mapeo simple para mejorar la búsqueda de noticias
    nombres_cripto = {
        "BTC": "Bitcoin",
        "ETH": "Ethereum",
        "ADA": "Cardano",
        "DOT": "Polkadot",
        "SHIB": "Shiba Inu"
    }
    nombre_completo = nombres_cripto.get(cripto.upper(), cripto.upper())

    try:
        # 1. Inicializar el cliente de NewsAPI
        newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

        # 2. Buscar noticias recientes en español
        # Buscamos por el nombre completo y la palabra "criptomoneda" para filtrar
        all_articles = newsapi.get_everything(
            q=f'"{nombre_completo}" AND (criptomoneda OR crypto)',
            language='es',
            sort_by='publishedAt', # Artículos más recientes primero
            page_size=10 # Pedimos los 10 titulares más recientes
        )

        if not all_articles or not all_articles['articles']:
            return jsonify({"sentimiento": "NEUTRAL", "detalle": "No se encontraron noticias recientes."}), 200

        # 3. Extraer solo las descripciones para tener más contexto
        descripciones = [article['description'] for article in all_articles['articles'] if article['description']]
        texto_descripciones = "\n".join(descripciones)

        # 4. Crear el prompt para la IA
        prompt = f""" 
Analiza los siguientes resúmenes de noticias sobre {nombre_completo} y justifica tu respuesta.
Tu respuesta DEBE ser un objeto JSON válido con dos claves:
1. "sentimiento": una de estas tres palabras: "Positivo", "Negativo" o "Neutral".
2. "explicacion": un párrafo breve en español explicando el porqué de esa clasificación.

Resúmenes:
{texto_descripciones}
"""
        import json

        mensajes = [
            SystemMessage(content="Eres un experto en análisis de sentimiento en las noticias de criptomonedas y prever movimientos del mercado."),
            HumanMessage(content=prompt)
        ]
        # Reutilizamos el LLM que ya tenemos configurado
        respuesta = llm.invoke(
            mensajes,
            response_format={"type": "json_object"}
            )
        
        try:
            # La IA ahora devuelve un JSON
            resultado_ia = json.loads(respuesta.content)
            sentimiento = resultado_ia.get("sentimiento", "Neutral")
            explicacion = resultado_ia.get("explicacion", "No se pudo obtener una explicación.")
        except (json.JSONDecodeError, AttributeError):
            # Fallback si la IA no devuelve un JSON válido
            sentimiento = "Sin Respuesta"
            explicacion = f"La respuesta de la IA no tuvo el formato esperado, por lo que no se pudo extraer la explicación. Respuesta cruda: {respuesta.content}"




        # Opcional: Guardar el uso de tokens
        # (Esta llamada consume muy pocos tokens, pero es buena práctica registrarlo)
         # ←←←←←←←←←←←← CONTROL DE TOKEN'S ←←←←←←←←←←←←
        tokens_entrada = respuesta.usage_metadata["input_tokens"]
        tokens_salida  = respuesta.usage_metadata["output_tokens"]
        tokens_total   = tokens_entrada + tokens_salida
        # ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←


        # ←←←←← AQUÍ LO GUARDAMOS ←←←←←
        from database import guardar_tokens_ia
        guardar_tokens_ia(
            proveedor="groq",
            modelo=modeloIA,
            tokens_entrada=tokens_entrada,
            tokens_salida=tokens_salida
        )

        return jsonify({
            "simbolo": cripto.upper(),
            "sentimiento": sentimiento,
            "explicacion": explicacion,
            "resumen_noticias": descripciones,
            "tokens_entrada":tokens_entrada,
            "tokens_salida": tokens_salida, # Añadido para ver los tokens de salida
            "tokens_total": tokens_total,   # Añadido para ver el total de tokens
            "coste_aprox_euros": round(tokens_total * 0.00000008, 7) # Añadido para ver el coste
        }), 200

    except Exception as e:
        logger.error(f"Error en sentimiento_noticias para {cripto}: {e}", exc_info=True)
        return jsonify({"error": f"El análisis de sentimiento ha fallado: {str(e)}"}), 500

# ==================== AGENTE LANGCHAIN (INICIALIZACIÓN CON DEBUGGING) ====================

# Cargar variables de entorno ANTES de importar el agente
load_dotenv("parametros.env")

# Importar el creador del agente desde el módulo correspondiente
from ia.grog_agente import crear_agente_kryptonite

# Inicializar el agente una sola vez al arrancar la aplicación
print("\n" + "="*60)
print("⚙️  INICIALIZANDO AGENTE LANGCHAIN...")
print("="*60)

agente_kryptonite = None
error_inicializacion = None

try:
    # 1. Verificar variables de entorno
    clave_api_groq = os.getenv("GROQ_API_KEY")
    modelo = os.getenv("GROQ_MODELO")
    
    print(f"🔑 API Key detectada: {'✅ Sí' if clave_api_groq else '❌ No'}")
    print(f"🤖 Modelo configurado: {modelo}")
    
    if not clave_api_groq:
        error_inicializacion = "Variable de entorno GROQ_API_KEY no está configurada"
        print(f"❌ ERROR: {error_inicializacion}")
    else:
        # 2. Intentar crear el agente
        print("📦 Creando instancia del agente...")
        agente_kryptonite = crear_agente_kryptonite(clave_api_groq)
        print("✅ Agente LangChain inicializado correctamente")
        print("🔧 Herramientas disponibles:")
        for tool in agente_kryptonite.herramientas:
            print(f"   - {tool.name}")
        
except Exception as e:
    error_inicializacion = str(e)
    print(f"❌ ERROR FATAL al inicializar el agente:")
    print(f"   {error_inicializacion}")
    import traceback
    traceback.print_exc()

print("="*60 + "\n")


@app.route('/prompt', methods=['POST'])
def langchain_ask():
    """
    Endpoint para hacer preguntas al agente LangChain
    """
    # Verificación mejorada con información de debug
    if agente_kryptonite is None:
        mensaje_error = "Agente LangChain no está disponible"
        if error_inicializacion:
            mensaje_error += f". Razón: {error_inicializacion}"

        return jsonify({
            "success": False,
            "error": mensaje_error,
            "debug": {
                "groq_api_key_present": bool(os.getenv("GROQ_API_KEY")),
                "modelo_configurado": os.getenv("GROQ_MODELO"),
                "error_inicializacion": error_inicializacion
            }
        }), 500

    try:
        datos = request.get_json()

        if not datos or 'question' not in datos:
            return jsonify({
                "success": False,
                "error": "Se requiere el campo 'question' en el body"
            }), 400

        pregunta = datos['question']
        print(f"\n💬 Pregunta recibida: {pregunta}")

        # Limpiar memoria antes de cada pregunta (conversación sin contexto)
        agente_kryptonite.reiniciar_memoria()
        # Procesar la pregunta con el agente (ahora devuelve dict con tokens)
        resultado = agente_kryptonite.preguntar(pregunta)
        print(f"✅ Respuesta generada correctamente")

        # Extraer información de tokens
        tokens_entrada = resultado.get("tokens_entrada", 0)
        tokens_salida = resultado.get("tokens_salida", 0)
        tokens_total = resultado.get("tokens_total", 0)
        num_llamadas_llm = resultado.get("num_llamadas_llm", 0)


        # Guardar los tokens en la base de datos si se usaron
        if tokens_total > 0:
            from database import guardar_tokens_ia
            guardar_tokens_ia(
                proveedor="groq",
                modelo=modeloIA,
                tokens_entrada=tokens_entrada,
                tokens_salida=tokens_salida
            )
            print(f"📊 Tokens guardados: entrada={tokens_entrada}, salida={tokens_salida}, total={tokens_total}")

        return jsonify({
            "success": True,
            "question": pregunta,
            "answer": resultado["output"],
            "tokens_entrada": tokens_entrada,
            "tokens_salida": tokens_salida,
            "tokens_total": tokens_total,
            "num_llamadas_llm": num_llamadas_llm,
            "coste_aprox_euros": round(tokens_total * 0.00000008, 7) if tokens_total > 0 else 0
        })

    except Exception as e:
        print(f"❌ Error procesando pregunta: {str(e)}")
        import traceback
        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# Endpoint adicional para verificar el estado del agente
@app.route('/prompt/status', methods=['GET'])
def agent_status():
    """
    Endpoint para verificar el estado del agente
    """
    return jsonify({
        "agente_disponible": agente_kryptonite is not None,
        "error_inicializacion": error_inicializacion,
        "groq_api_key_present": bool(os.getenv("GROQ_API_KEY")),
        "modelo_configurado": os.getenv("GROQ_MODELO"),
        "herramientas_disponibles": [
            tool.name for tool in agente_kryptonite.herramientas
        ] if agente_kryptonite else []
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
