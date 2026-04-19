# Kryptonite - Analisis de Dockerizacion

> Analisis para integrar Kryptonite en el ecosistema hogarOS con la misma
> estructura que ReDo, FiDo y MediDo.

Fecha: 2026-03-31

---

## 1. Estado actual

Kryptonite es la unica app satelite que **no** sigue el estandar del ecosistema:

| Aspecto | Estandar (ReDo/FiDo/MediDo) | Kryptonite actual |
|---------|-----------------------------|--------------------|
| Framework | FastAPI + uvicorn | Flask (`api.py`, debug=True) |
| Estructura | `app/principal.py`, `app/rutas/`, `app/bd.py` | `src/api.py` monolitico (711 lineas) |
| Dockerfile | Si, Python 3.12-slim | No existe |
| docker-compose | Si, en hogarOS + local | No existe |
| Config | Env vars con prefijo (`REDO_`, `FIDO_`) | Env vars sin prefijo + paths hardcoded a `/home/jovyan/` |
| Base de datos | `app/bd.py` + `app/esquema.sql` | `src/database.py` (funcional pero distinta convencion) |
| Frontend | SPA vanilla + Living Sanctuary | No tiene (usa Telegram + Node-RED) |
| Deploy | `actualizar.sh` (pull + build + up) | Manual dentro de JupyterLab |
| Puerto | Gestionado por docker-compose | 5000 hardcoded en `api.py` |
| Proxy nginx | Contenedor en red Docker | `host.docker.internal:5000` |

---

## 2. Problemas concretos a resolver

### 2.1 Paths hardcoded (`src/config.py`)

```python
# Linea 18 — default apunta a JupyterLab
DB_PATH = os.getenv("DB_PATH", "/home/jovyan/work/kryptonite/data/kryptonite.db")

# Linea 19
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "/home/jovyan/work/kryptonite/logs/kryptonite.log")

# Linea 50 — cambio de directorio forzado
os.chdir("/home/jovyan/work/kryptonite")
```

**Solucion:** Usar rutas relativas al proyecto (`data/kryptonite.db`, `logs/kryptonite.log`) y eliminar el `os.chdir()`. El `WORKDIR /app` del Dockerfile se encarga de posicionar el contexto.

### 2.2 Flask con debug=True

```python
# src/api.py linea 711
app.run(host='0.0.0.0', port=5000, debug=True)
```

**Solucion:** En Docker se arranca con uvicorn (si se migra a FastAPI) o con gunicorn/waitress (si se mantiene Flask). El `if __name__` solo se usa en desarrollo local.

### 2.3 API monolitica

`src/api.py` concentra ~20 endpoints en un solo fichero. El estandar usa routers separados:

```
app/rutas/
  portfolio.py      # /api/portafolio, /api/nuevaOperacion
  analisis.py       # /api/senal/*, /api/backtest
  datos.py          # /api/run, /api/valor
  ia.py             # /api/prompt, /api/analisis_ia
  resumen.py        # /api/resumen (para tarjeta del portal)
```

### 2.4 Dependencias del sistema

`requirements.txt` tiene ~25 dependencias. Algunas requieren compilacion nativa:
- `pandas`, `numpy`, `scikit-learn` — wheels pesados pero disponibles para linux/amd64
- `kaleido` — renderizado de graficos Plotly, puede dar problemas en slim
- `matplotlib` — necesita `libfreetype6` y `libpng`

**Solucion:** Instalar dependencias de sistema en el Dockerfile:
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    libfreetype6-dev libpng-dev && rm -rf /var/lib/apt/lists/*
```

### 2.5 Endpoint `/api/resumen` inexistente

Las apps satelite exponen un `/api/resumen` que MediDo consulta para health checks y que el portal muestra como tarjeta. Kryptonite no lo tiene.

**Solucion:** Crear un endpoint ligero que devuelva estado basico del portfolio (valor total, cambio 24h, numero de criptos activas).

---

## 3. Estructura objetivo

```
kryptonite/
  app/
    __init__.py
    principal.py          # FastAPI + lifespan + scheduler
    config.py             # Env vars con prefijo KRYPTO_
    bd.py                 # Capa SQLite estandarizada
    esquema.sql           # CREATE TABLE IF NOT EXISTS
    modelos.py            # Pydantic schemas
    rutas/
      portfolio.py        # Operaciones y valor del portfolio
      analisis.py         # Senales, backtesting
      datos.py            # Fetch de datos Binance
      ia.py               # Agente LangChain, prompts
      resumen.py          # Tarjeta para portal + health check
    ia/
      grog_agente.py      # Agente conversacional (sin cambios)
      analisis_tools.py   # Tools del agente (sin cambios)
      mcp_sqlite_tools.py # MCP tools (sin cambios)
    servicios/
      binance.py          # Logica de Binance API
      charts.py           # Generacion de graficos
      alertas.py          # Sistema de alertas
      noticias.py         # Sentimiento de noticias
  static/
    index.html            # SPA con Living Sanctuary (opcional, fase 4)
  data/                   # SQLite (volumen montado)
  logs/                   # Logs (volumen montado)
  Dockerfile
  docker-compose.yml
  requirements.txt
  parametros.env.example
  README.md
  CLAUDE.md
  .gitignore
  documentacion/          # Se mantiene tal cual
```

---

## 4. Ficheros nuevos clave

### 4.1 Dockerfile

```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libfreetype6-dev libpng-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY static/ static/

ENV KRYPTO_PORT=5000
EXPOSE 5000

CMD uvicorn app.principal:app --host 0.0.0.0 --port $KRYPTO_PORT
```

### 4.2 docker-compose.yml (local, para desarrollo)

```yaml
services:
  kryptonite:
    build: .
    container_name: kryptonite
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    env_file:
      - parametros.env
    environment:
      - TZ=Europe/Madrid
    restart: unless-stopped
```

### 4.3 Integracion en hogarOS docker-compose.yml

```yaml
  kryptonite:
    build: /mnt/datos/kryptonite-build/
    container_name: kryptonite
    ports:
      - "5000:5000"
    volumes:
      - /mnt/datos/kryptonite/data:/app/data
      - /mnt/datos/kryptonite/logs:/app/logs
    env_file:
      - /mnt/datos/kryptonite/parametros.env
    environment:
      - TZ=Europe/Madrid
    restart: unless-stopped
```

### 4.4 Cambio en nginx.conf de hogarOS

```nginx
# Antes (app externa):
location /crypto/api/ {
    proxy_pass http://host.docker.internal:5000/;
}

# Despues (contenedor en la misma red):
location /crypto/api/ {
    proxy_pass http://kryptonite:5000/;
    sub_filter_once off;
    # sub_filters si se anade frontend
}
```

### 4.5 Config estandarizada (`app/config.py`)

```python
import os
from dotenv import load_dotenv

load_dotenv("parametros.env")

# Rutas — defaults relativos al WORKDIR del contenedor
KRYPTO_DB_PATH = os.getenv("KRYPTO_DB_PATH", "data/kryptonite.db")
KRYPTO_LOG_PATH = os.getenv("KRYPTO_LOG_PATH", "logs/kryptonite.log")
KRYPTO_PORT = int(os.getenv("KRYPTO_PORT", "5000"))

# APIs externas
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODELO = os.getenv("GROQ_MODELO", "llama-3.3-70b-versatile")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

# Moneda
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "EUR")

# Umbrales
UMBRAL_SOBREEXPOSICION = float(os.getenv("UMBRAL_SOBREEXPOSICION", "40"))
UMBRAL_PERDIDA_SEVERA = float(os.getenv("UMBRAL_PERDIDA_SEVERA", "-50"))
UMBRAL_CONCENTRACION_ALTA = float(os.getenv("UMBRAL_CONCENTRACION_ALTA", "60"))
```

---

## 5. Lo que NO cambia

- **Logica de negocio**: analisis tecnico, backtesting, agente IA, charts — se mueven de sitio pero no se reescriben
- **Base de datos**: mismas tablas, mismos datos. Se migra el fichero `.db` tal cual
- **Node-RED + Telegram**: siguen funcionando, solo cambia la URL de la API (de `localhost:5000` a `kryptonite:5000` o la IP del host)
- **API keys**: mismas variables de entorno, solo se renombran con prefijo `KRYPTO_`

---

## 6. Riesgos y mitigaciones

| Riesgo | Probabilidad | Mitigacion |
|--------|-------------|------------|
| `kaleido` no funciona en python:3.12-slim | Media | Probar en build; alternativa: generar charts solo con matplotlib |
| Node-RED pierde conexion con la API | Baja | Actualizar URL en flujos de Node-RED al nuevo endpoint |
| Migracion Flask→FastAPI introduce bugs | Media | Migrar endpoint por endpoint, testear cada uno antes de pasar al siguiente |
| Imagen Docker muy pesada (pandas, sklearn) | Alta | Aceptable (~800MB); se puede optimizar despues con multi-stage build |
| Perdida de datos SQLite en migracion | Baja | Copiar `kryptonite.db` al volumen antes de arrancar el contenedor |

---

## 7. Prerequisitos

1. Crear directorio en VM 101: `/mnt/datos/kryptonite-build/` (codigo) y `/mnt/datos/kryptonite/` (datos)
2. Configurar repo en GitHub (`acabellan1868-prog/kryptonite` — ya existe)
3. Copiar `kryptonite.db` actual al directorio de datos
4. Crear `parametros.env` con las API keys reales
5. Actualizar flujos de Node-RED para apuntar al nuevo endpoint
