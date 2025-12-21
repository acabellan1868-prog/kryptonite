# config.py

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
import time
from dotenv import load_dotenv

# ============================================
# CARGA DE VARIABLES DE ENTORNO
# ============================================
load_dotenv("parametros.env")

# ============================================
# RUTAS DEL SISTEMA (desde ENV con fallbacks)
# ============================================
DB_PATH = os.getenv("DB_PATH", "/home/jovyan/work/kryptonite/data/kryptonite.db")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "/home/jovyan/work/kryptonite/logs/kryptonite.log")

# Si quieres usar rutas relativas, puedes hacerlo así
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# ============================================
# CONSTANTES DEL PROYECTO (no cambian)
# ============================================
FAVORITES_FILTER = "favorites"
PORTFOLIO_FILTER = "portfolio"

# Monedas disponibles
EURO_CURRENCY = "EUR"
DOLLAR_CURRENCY = "USD"

# ============================================
# CONFIGURACIÓN DE MONEDA (desde ENV)
# ============================================
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", EURO_CURRENCY)

# ============================================
# UMBRALES DE ANÁLISIS DE PORTFOLIO
# ============================================
UMBRAL_SOBREEXPOSICION = float(os.getenv("UMBRAL_SOBREEXPOSICION", "40"))
UMBRAL_PERDIDA_SEVERA = float(os.getenv("UMBRAL_PERDIDA_SEVERA", "-50"))
UMBRAL_CONCENTRACION_ALTA = float(os.getenv("UMBRAL_CONCENTRACION_ALTA", "60"))

# INICICIO DEFINICIÓN DEL FICHERO DE LOG'S

# Cambiar al directorio raíz del proyecto
os.chdir("/home/jovyan/work/kryptonite")

# Crear el directorio logs en la raíz del proyecto
log_dir = os.path.join(os.getcwd(), "logs")
os.makedirs(log_dir, exist_ok=True)

# Configurar el logging solo para Kryptonite
log_file = os.path.join(log_dir, "kryptonite.log")

# Crear un logger específico para Kryptonite
logger = logging.getLogger("kryptonite")
logger.setLevel(logging.INFO)

# 🔹 Eliminar manejadores previos para evitar duplicados
if logger.hasHandlers():
    logger.handlers.clear()

# Crear un manejador de archivo
file_handler = logging.FileHandler(log_file)
file_handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=3)
file_handler.setLevel(logging.INFO)

# Definir el formato del log
formatter = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Agregar el manejador al logger
logger.addHandler(file_handler)
logging.Formatter.converter = time.gmtime

# Evitar que este logger se propague a otros loggers globales
logger.propagate = False

# --- 🔹 PASO CLAVE: Desactivar el logger raíz de logging 🔹 ---
logging.getLogger().handlers = []  # Elimina cualquier manejador del logger raíz

# --- 🔹 PASO OPCIONAL: Silenciar logs de librerías 🔹 ---
logging.getLogger("ccxt").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Mensaje de prueba
logger.info("Sistema de logs inicializado en la raíz del proyecto.")

# FIN FICHERO DE LOG'S
