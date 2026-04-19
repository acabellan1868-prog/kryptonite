# -*- coding: utf-8 -*-
"""
Este archivo contiene la implementación de un modelo de Inteligencia Artificial (No es IA como la entendemos, pero bueno)
para predecir la dirección del precio de una criptomoneda.

Utiliza un modelo de clasificación llamado 'Random Forest' y una búsqueda automática
de hiperparámetros (GridSearchCV) para encontrar la mejor configuración posible.
"""

# --- Importaciones necesarias ---
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
import pandas_ta as ta
from database import get_data_from_db_in_range
from datetime import datetime, timedelta


# --- Constantes ---
NOMBRE_ARCHIVO_MODELO = 'random_forest_cripto.joblib'


def preparar_datos_para_entrenamiento(simbolo, dias=365):
    """
    Prepara los datos para el entrenamiento del modelo usando datos REALES de la BD local.
    """
    print(f"Obteniendo datos de la base de datos local para {simbolo}...")

    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=dias)
    datos_dict = get_data_from_db_in_range(simbolo, fecha_inicio, fecha_fin)

    if not datos_dict:
        print(f"Error: No se encontraron datos para {simbolo} en la base de datos.")
        return pd.DataFrame()

    datos = pd.DataFrame(datos_dict)
    datos['timestamp'] = pd.to_datetime(datos['timestamps'], unit='s')
    datos.set_index('timestamp', inplace=True)
    datos.rename(columns={'prices': 'close', 'volumes': 'volume'}, inplace=True)

    agregaciones = {'close': 'last', 'volume': 'sum'}
    datos_diarios = datos.resample('D').agg(agregaciones)
    datos = datos_diarios.dropna()

    print(f"Se han obtenido y procesado {len(datos)} registros diarios.")

    # Calcular características (Features)
    datos['sma_10'] = datos['close'].rolling(window=10).mean()
    datos['sma_30'] = datos['close'].rolling(window=30).mean()
    datos['momentum_5'] = datos['close'].diff(5)
    datos.ta.rsi(length=14, append=True)
    datos.ta.bbands(length=20, append=True)
    datos['bb_ancho'] = (datos['BBU_20_2.0'] - datos['BBL_20_2.0']) / datos['BBM_20_2.0']
    datos.ta.macd(append=True)

    # Crear la variable objetivo (Target)
    datos['precio_futuro'] = datos['close'].shift(-1)
    datos['objetivo'] = (datos['precio_futuro'] > datos['close']).astype(int)

    datos = datos.dropna()
    print("Datos reales de la BD preparados y listos para el entrenamiento.")
    return datos


def entrenar_y_guardar_modelo(datos):
    """
    Usa GridSearchCV para encontrar los mejores hiperparámetros para el modelo,
    lo entrena y lo guarda en un archivo.
    """
    if datos.empty:
        print("No hay datos para entrenar el modelo. Abortando.")
        return

    print("Iniciando la búsqueda automática de los mejores hiperparámetros...")
    print("Este proceso puede tardar varios minutos...")

    # 1. Separar las características (X) de la variable objetivo (y)
    caracteristicas = [
        'sma_10', 'sma_30', 'momentum_5', 'RSI_14', 'bb_ancho',
        'volume', 'MACD_12_26_9', 'MACDh_12_26_9'
    ]
    X = datos[caracteristicas]
    y = datos['objetivo']

    # 2. Definir la "parrilla" de parámetros a probar
    # Se probarán todas las combinaciones de estos valores.
    param_grid = {
        'n_estimators': [100, 200],      # Número de árboles
        'max_depth': [10, 20],           # Profundidad máxima de los árboles
        'min_samples_leaf': [2, 4]       # Mínimo de muestras para ser una hoja
    }

    # 3. Crear el modelo base
    modelo_base = RandomForestClassifier(random_state=42)

    # 4. Configurar el validador cruzado para series temporales
    # Esto es CRUCIAL para no usar datos del futuro para validar el pasado.
    tscv = TimeSeriesSplit(n_splits=5)

    # 5. Configurar GridSearchCV
    # n_jobs=-1 usa todos los procesadores para acelerar. verbose=2 muestra el progreso.
    grid_search = GridSearchCV(estimator=modelo_base, param_grid=param_grid, cv=tscv, n_jobs=-1, verbose=2)

    # 6. Ejecutar la búsqueda
    grid_search.fit(X, y)

    # 7. Mostrar y guardar los mejores resultados
    print("\n¡Búsqueda completada!")
    print(f"Mejores parámetros encontrados: {grid_search.best_params_}")
    print(f"Mejor puntuación de validación cruzada (precisión): {grid_search.best_score_:.3f}")

    # Guardar el mejor modelo encontrado
    mejor_modelo = grid_search.best_estimator_
    joblib.dump(mejor_modelo, NOMBRE_ARCHIVO_MODELO)
    print(f"El mejor modelo ha sido guardado en: '{NOMBRE_ARCHIVO_MODELO}'")
    
    # Opcional: Evaluar el mejor modelo en el conjunto de prueba final
    # (La puntuación de GridSearchCV es sobre los datos de validación, no de prueba)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)
    predicciones_finales = mejor_modelo.predict(X_test)
    precision_final = accuracy_score(y_test, predicciones_finales)
    print(f"Precisión del mejor modelo en el conjunto de prueba final: {precision_final:.3f}")


def hacer_prediccion(datos_nuevos):
    """
    Carga el modelo entrenado y hace una nueva predicción.
    """
    if datos_nuevos.empty:
        return "No se proporcionaron datos para la predicción."
        
    print("\nCargando modelo para hacer una nueva predicción...")
    try:
        modelo = joblib.load(NOMBRE_ARCHIVO_MODELO)
    except FileNotFoundError:
        return "Error: El archivo del modelo no ha sido encontrado. Por favor, entrena el modelo primero."

    caracteristicas = [
        'sma_10', 'sma_30', 'momentum_5', 'RSI_14', 'bb_ancho',
        'volume', 'MACD_12_26_9', 'MACDh_12_26_9'
    ]
    # Asegurarse de que los datos nuevos tengan todas las columnas necesarias
    datos_para_predecir = datos_nuevos[caracteristicas]

    prediccion_numerica = modelo.predict(datos_para_predecir)

    resultado = 'Sube' if prediccion_numerica[0] == 1 else 'Baja'
    print(f"Predicción del modelo: El precio {resultado}")
    return resultado


# --- Bloque de ejecución principal ---
if __name__ == '__main__':
    datos_historicos = preparar_datos_para_entrenamiento('BTC')
    
    if not datos_historicos.empty:
        entrenar_y_guardar_modelo(datos_historicos)
        
        ultimos_datos = datos_historicos.tail(1)
        hacer_prediccion(ultimos_datos)