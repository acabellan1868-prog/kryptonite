# config.py

import logging
import os
import time
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv("parametros.env")

# ── Rutas ──────────────────────────────────────────────────────────────────
KRYPTO_DB_PATH      = os.getenv("KRYPTO_DB_PATH",  "data/kryptonite.db")
KRYPTO_LOG_PATH     = os.getenv("KRYPTO_LOG_PATH",  "logs/kryptonite.log")

# Alias sin prefijo para no romper imports existentes en esta fase
DB_PATH      = KRYPTO_DB_PATH
LOG_FILE_PATH = KRYPTO_LOG_PATH

# ── Constantes ─────────────────────────────────────────────────────────────
FAVORITES_FILTER = "favorites"
PORTFOLIO_FILTER = "portfolio"

EURO_CURRENCY   = "EUR"
DOLLAR_CURRENCY = "USD"

# ── Configuración de moneda ────────────────────────────────────────────────
DEFAULT_CURRENCY = os.getenv("KRYPTO_DEFAULT_CURRENCY", os.getenv("DEFAULT_CURRENCY", EURO_CURRENCY))

# ── Umbrales de análisis de portfolio ──────────────────────────────────────
UMBRAL_SOBREEXPOSICION    = float(os.getenv("KRYPTO_UMBRAL_SOBREEXPOSICION",    os.getenv("UMBRAL_SOBREEXPOSICION",    "40")))
UMBRAL_PERDIDA_SEVERA     = float(os.getenv("KRYPTO_UMBRAL_PERDIDA_SEVERA",     os.getenv("UMBRAL_PERDIDA_SEVERA",     "-50")))
UMBRAL_CONCENTRACION_ALTA = float(os.getenv("KRYPTO_UMBRAL_CONCENTRACION_ALTA", os.getenv("UMBRAL_CONCENTRACION_ALTA", "60")))

# ── Directorios de datos y logs (se crean si no existen) ───────────────────
os.makedirs(os.path.dirname(KRYPTO_DB_PATH),  exist_ok=True)
os.makedirs(os.path.dirname(KRYPTO_LOG_PATH), exist_ok=True)

# ── Logger ─────────────────────────────────────────────────────────────────
logger = logging.getLogger("kryptonite")
logger.setLevel(logging.INFO)

if logger.hasHandlers():
    logger.handlers.clear()

file_handler = RotatingFileHandler(KRYPTO_LOG_PATH, maxBytes=5_000_000, backupCount=3)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

logging.Formatter.converter = time.gmtime
logger.propagate = False
logging.getLogger().handlers = []

logging.getLogger("ccxt").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger.info("Sistema de logs inicializado.")
