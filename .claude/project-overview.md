# Kryptonite - Visión General del Proyecto

> Sistema inteligente de análisis y gestión de inversiones en criptomonedas

---

## 🎯 Descripción del Proyecto

**Kryptonite** es una aplicación diseñada para simplificar las decisiones de inversión en criptomonedas. El objetivo es proporcionar herramientas para tomar decisiones basadas en datos, sin andar a ciegas en un mercado volátil.

El nombre es simbólico: mientras que la kryptonita es la debilidad de Superman, **Kryptonite** es tu punto fuerte en un mercado que puede parecer una montaña rusa.

---

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```
┌─────────────────┐
│    TELEGRAM     │ ← Interfaz de usuario (panel de control)
│   (Usuario)     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│    NODE-RED     │ ← Orquestador de flujos y tareas recurrentes
│  (Middleware)   │    - Programación de tareas (cron jobs)
└────────┬────────┘    - Integración Telegram ↔ Kryptonite
         │
         ↓
┌─────────────────┐
│   KRYPTONITE    │ ← Backend de datos y análisis
│  (Flask API)    │    - Gestión de datos
└────────┬────────┘    - Análisis técnico
         │             - Agente IA
         ↓             - Backtesting
┌─────────────────┐
│   BINANCE API   │ ← Fuente de datos de mercado
└─────────────────┘
```

### Stack Tecnológico

| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| **Lenguaje** | Python 3.11 | Backend principal |
| **Framework API** | Flask | Endpoints REST |
| **Base de Datos** | SQLite | Almacenamiento de datos históricos y operaciones |
| **Orquestador** | Node-RED | Automatización y flujos de trabajo |
| **Interfaz** | Telegram Bot | Panel de control de usuario |
| **Exchange** | Binance | Datos de mercado en tiempo real |
| **IA/LLM** | Groq (LangChain) | Agente conversacional y análisis |
| **ML** | scikit-learn | Modelos predictivos (Random Forest) |
| **Visualización** | Matplotlib, Plotly | Generación de gráficas |
| **Análisis Técnico** | pandas-ta | Indicadores técnicos |
| **Noticias** | NewsAPI | Análisis de sentimiento |

---

## 📊 Estructura de la Base de Datos

### Tabla: `cryptos`
Catálogo de criptomonedas monitoreadas.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `symbol` | TEXT (PK) | Código de la criptomoneda (BTC, ETH, etc.) |
| `name` | TEXT | Nombre completo (Bitcoin, Ethereum, etc.) |
| `slug` | TEXT | Identificador en minúsculas (bitcoin, ethereum) |
| `is_favorite` | INTEGER | 1 si es favorita, 0 si no (para filtrado) |
| `is_portfolio` | INTEGER | 1 si está en cartera, 0 si no |
| `nota` | TEXT | Notas personalizadas sobre la cripto |

### Tabla: `crypto_data`
Datos históricos de precios y volúmenes (granularidad: 1 minuto).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `timestamp` | INTEGER | Fecha/hora en formato UNIX |
| `symbol` | TEXT | Símbolo de la criptomoneda |
| `price` | REAL | Precio en USD/EUR |
| `volume` | REAL | Volumen de transacciones |
| `market_cap` | REAL | Capitalización de mercado |

**Índices:**
- `(symbol, timestamp)` - Para consultas rápidas por cripto y rango temporal

### Tabla: `operaciones`
Registro de operaciones reales de compra/venta.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER (PK) | ID autoincremental |
| `timestamp` | INTEGER | Fecha de la operación en formato UNIX (segundos desde epoch) |
| `cripto` | TEXT | Símbolo de la criptomoneda |
| `moneda` | TEXT | Moneda fiat usada (EUR, USD) |
| `tipo` | TEXT | Tipo: 'Compra', 'Venta', 'Envío', 'Recepción' |
| `cantidad` | REAL | Cantidad de criptomoneda operada |
| `precio` | REAL | Precio unitario en moneda fiat |
| `valor_total` | REAL | Cantidad × Precio (sin comisiones) |
| `comision` | REAL | Comisión pagada en moneda fiat |
| `origen` | TEXT | Fuente del dato (ej: 'Revolut', 'Binance') |

**Formato de timestamp:**
- Tipo: INTEGER (UNIX timestamp - segundos desde 1970-01-01 00:00:00 UTC)
- Para convertir a fecha legible: `datetime(timestamp, 'unixepoch')` en SQLite
- Ejemplo: `1736798485` → `2025-01-13 21:01:25`

**Cálculos importantes:**
- **Inversión total en Compra:** `valor_total + comision`
- **Ajuste en Venta:** Restar `valor_total` y sumar `comision`

### Tabla: `uso_ia`
Tracking de uso de tokens de modelos de IA (control de costes).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER (PK) | ID autoincremental |
| `proveedor` | TEXT | Proveedor del LLM (ej: 'groq'), default: 'groq' |
| `modelo` | TEXT | Modelo usado (ej: 'llama-3.3-70b-versatile') |
| `fecha` | DATETIME | Timestamp de la llamada (CURRENT_TIMESTAMP) |
| `tokens_entrada` | INTEGER | Tokens de entrada (prompt) |
| `tokens_salida` | INTEGER | Tokens de salida (respuesta) |

### Tabla: `alerts`
Sistema de alertas (posiblemente en desuso o poco usado).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER (PK) | ID autoincremental |
| `crypto_id` | INTEGER | ID de la criptomoneda |
| `trigger_price` | REAL | Precio que dispara la alerta |
| `alert_type` | TEXT | Tipo de alerta |
| `enabled` | INTEGER | 1 si está activa, 0 si no |

**Nota:** No hay evidencia de uso en el código actual de la API.

### Tabla: `users`
Gestión de usuarios (posiblemente para futuras funcionalidades).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | INTEGER (PK) | ID autoincremental |
| `username` | TEXT (UNIQUE) | Nombre de usuario |
| `email` | TEXT (UNIQUE) | Email del usuario |
| `password` | TEXT | Contraseña (presumiblemente hasheada) |

**Nota:** No hay evidencia de sistema de autenticación en uso actualmente.

---

## 🔌 API REST (Flask)

### Endpoints Disponibles

#### 📥 Carga de Datos
- **`POST /run`**
  - Carga datos de favoritos de los últimos 30 min (intervalos 1 min)
  - Usado por Node-RED en tareas recurrentes

#### 💰 Precios y Valores
- **`GET /valor?crypto=BTC&timeframe=1d`**
  - Obtiene precio actual, volumen, market cap y media móvil
  - Parámetros: `crypto` (requerido), `timeframe` (opcional, default: '1d')

#### 📈 Gráficas
- **`GET /grafica24h?crypto=BTC`**
  - Devuelve gráfica de 24h en base64
  - Si no se especifica `crypto`, devuelve gráfica comparativa del portfolio

#### 💼 Portfolio
- **`GET /portafolio`**
  - Rendimiento completo del portfolio
  - Retorna: cantidad, coste, valor actual, rentabilidad por cripto

#### 🧹 Mantenimiento
- **`GET /limpiar`**
  - Elimina duplicados de la tabla `crypto_data`

#### 🚦 Señales de Trading
- **`GET /senal/cambio_extremo?cripto=BTC&intervalo_minutos=15&umbral_porcentual=1.0`**
  - Detecta cambios extremos en precio (estrategia de reversión)
  - Parámetros:
    - `cripto` (requerido)
    - `intervalo_minutos` (default: 15, múltiplo de 5)
    - `umbral_porcentual` (default: 1.0)
    - `confirmar_con_volumen` (default: true)
    - `umbral_porcentual_volumen` (default: 30.0)

#### 📊 Backtesting
- **`POST /backtest`**
  - Body JSON:
    ```json
    {
      "symbol": "BTC",
      "start_date": "2025-01-01",
      "end_date": "2025-01-31",
      "initial_capital": 1000,
      "strategy": "obtener_senal_cambio_extremo",
      "strategy_params": {
        "intervalo_minutos": 15,
        "umbral_porcentual": 1.0
      }
    }
    ```
  - Estrategias disponibles:
    - `obtener_senal_cambio_extremo`
    - `cruce_medias_moviles`

#### 🤖 Inteligencia Artificial

- **`GET /analisis_ia`**
  - Análisis del portfolio completo por IA
  - Retorna opinión del agente + datos + uso de tokens

- **`GET /sentimiento_noticias?cripto=BTC`**
  - Análisis de sentimiento de noticias recientes (NewsAPI + Groq)
  - Retorna: sentimiento (Positivo/Negativo/Neutral), explicación, resúmenes

- **`POST /prompt`**
  - Agente LangChain conversacional (consultas en lenguaje natural)
  - Body: `{"question": "¿Cuánto he invertido en BTC?"}`
  - Tiene acceso a herramientas MCP SQLite para consultar la BD

- **`GET /prompt/status`**
  - Estado del agente (disponibilidad, herramientas, configuración)

---

## 🧠 Agente IA (LangChain + Groq)

### Ubicación
[src/ia/grog_agente.py](src/ia/grog_agente.py)

### Características
- **Modelo:** Configurable vía env (default: `llama-3.3-70b-versatile`)
- **Herramientas MCP SQLite:**
  - `listar_tablas_base_de_datos`
  - `obtener_esquema_tabla`
  - `consultar_base_de_datos`
  - `obtener_datos_tabla`

### Prompt del Sistema
El agente está configurado como experto en análisis de inversiones cripto con conocimiento profundo de:
- Estructura de tablas `operaciones` y `crypto_data`
- Cálculos de inversión (valor_total + comisión)
- Consultas SQL contextuales

### Uso de Tokens
- Callback personalizado (`TokenCounterCallback`) que registra:
  - Tokens de entrada/salida por llamada
  - Número de iteraciones del agente
- Todos los usos se guardan en tabla `uso_ia` mediante la función `guardar_tokens_ia()`

### Memoria
- `ConversationBufferMemory` que se reinicia antes de cada pregunta nueva
- Actualmente sin contexto entre consultas (stateless)

---

## 📂 Estructura del Proyecto

```
kryptonite/
├── .claude/                    # Contexto para Claude AI
│   └── project-overview.md     # Este archivo
│
├── data/                       # Datos persistentes
│   └── kryptonite.db           # Base de datos SQLite (185 MB)
│
├── documentacion/              # Documentación del proyecto
│   ├── kryptoniteDoc.md        # Documentación original
│   ├── roadmap-2025.md         # Roadmap y planificación
│   ├── agenteLangChange.md     # Notas sobre el agente IA
│   ├── token_tracking.md       # Control de uso de tokens
│   └── ...
│
├── logs/                       # Logs de aplicación
│   └── kryptonite.log          # Log principal (rotativo, 5MB max)
│
├── notebook/                   # Jupyter notebooks
│   └── kryptonite.ipynb        # Notebook principal de pruebas
│
├── src/                        # Código fuente
│   ├── ia/                     # Módulo de IA
│   │   ├── grog_agente.py      # Agente LangChain principal
│   │   └── mcp_sqlite_tools.py # Herramientas MCP para SQLite
│   │
│   ├── api.py                  # API Flask (endpoints)
│   ├── main.py                 # Scripts de carga de datos
│   ├── database.py             # Gestión de base de datos
│   ├── binance_data.py         # Integración con Binance
│   ├── analysis.py             # Análisis técnico y señales
│   ├── backtesting.py          # Motor de backtesting
│   ├── charts.py               # Generación de gráficas
│   ├── config.py               # Configuración global
│   ├── modelo_ia.py            # Modelos de ML
│   ├── modelos.py              # Definiciones de modelos
│   └── analisis_rendimineto.py # Cálculos de rendimiento
│
├── .venv/                      # Entorno virtual Python
├── parametros.env              # Variables de entorno (API keys)
├── requirements.txt            # Dependencias Python
└── random_forest_cripto.joblib # Modelo ML entrenado
```

---

## 🔧 Configuración

### Variables de Entorno (parametros.env)

```env
GROQ_API_KEY=gsk_...
GROQ_MODELO=llama-3.3-70b-versatile
NEWS_API_KEY=...
```

### Constantes Principales (config.py)

```python
DB_PATH = '/home/jovyan/work/kryptonite/data/kryptonite.db'
LOG_FILE_PATH = '/home/jovyan/work/kryptonite/logs/kryptonite.log'
FAVORITES_FILTER = "favorites"
PORTFOLIO_FILTER = "portfolio"
DEFAULT_CURRENCY = "EUR"
```

---

## 🔄 Flujo de Trabajo Típico

### 1. Carga de Datos (Node-RED → Kryptonite)
```
Node-RED (cada X minutos)
  → POST /run
    → fetch_and_insert_data_last_30min(FAVORITES_FILTER)
      → Consulta Binance para cada favorita
        → Inserta en crypto_data (tabla histórica)
```

### 2. Detección de Señales (Node-RED → Kryptonite)
```
Node-RED (cada Y minutos)
  → GET /senal/cambio_extremo?cripto=BTC
    → Analiza cambio porcentual reciente
    → Confirma con volumen (opcional)
      → Devuelve señal: COMPRA / VENTA / NEUTRAL
        → Node-RED → Telegram (notificación al usuario)
```

### 3. Consulta por Usuario (Telegram → Node-RED → Kryptonite)
```
Usuario escribe en Telegram
  → Node-RED recibe mensaje
    → Identifica comando (/portafolio, /grafica, etc.)
      → GET/POST al endpoint correspondiente
        → Kryptonite procesa y responde
          → Node-RED formatea respuesta
            → Telegram envía al usuario
```

### 4. Análisis con IA (Telegram → Kryptonite)
```
Usuario pregunta: "¿Cuánto he ganado con BTC?"
  → Node-RED
    → POST /prompt {"question": "..."}
      → AgenteKryptonite.preguntar()
        → LangChain ejecuta ciclo:
          1. Analiza pregunta
          2. Decide qué herramienta usar
          3. Ejecuta consulta SQL
          4. Interpreta resultados
          5. Genera respuesta en lenguaje natural
        → Retorna respuesta + tokens usados
      → Guarda tokens en BD
    → Telegram envía respuesta al usuario
```

---

## 🧪 Análisis Técnico Implementado

### Estrategias de Trading

#### 1. Cambio Extremo (Reversión a la Media)
- **Función:** `obtener_senal_cambio_extremo()`
- **Lógica:**
  - Detecta cambios porcentuales mayores al umbral en intervalo corto
  - Si precio sube rápido → VENDER (se espera corrección)
  - Si precio baja rápido → COMPRAR (se espera rebote)
  - Confirmación opcional con volumen anómalo
- **Parámetros configurables:**
  - `intervalo_minutos` (default: 15)
  - `umbral_porcentual` (default: 1.0%)
  - `confirmar_con_volumen` (default: true)

#### 2. Cruce de Medias Móviles
- **Función:** `obtener_senal_cruce_medias_moviles()`
- **Lógica:**
  - Compara media móvil corta vs larga
  - Cruce alcista → COMPRAR
  - Cruce bajista → VENDER

### Indicadores Calculados
- Media móvil simple (SMA)
- Cambio porcentual de precio
- Cambio porcentual de volumen
- Volumen promedio histórico

---

## 🎓 Machine Learning

### Modelo Actual
- **Archivo:** `random_forest_cripto.joblib`
- **Algoritmo:** Random Forest (scikit-learn)
- **Estado:** Entrenado pero NO integrado en endpoints actuales
- **Uso potencial:** Predicción de tendencias a corto plazo

---

## 📝 Logging

### Configuración
- **Archivo:** `logs/kryptonite.log`
- **Rotación:** 5 MB, 3 backups
- **Formato:** `%(asctime)s - %(filename)s - %(levelname)s - %(message)s`
- **Nivel:** INFO

### Loggers silenciados
- `ccxt` → WARNING
- `requests` → WARNING
- `urllib3` → WARNING

---

## 🚀 Ejecución

### Iniciar API Flask
```bash
cd /mnt/datos/jupyter/kryptonite
source .venv/bin/activate
python src/api.py
```

La API escucha en: `http://0.0.0.0:5000`

### Verificar Estado del Agente
```bash
curl http://localhost:5000/prompt/status
```

---

## 📊 Métricas y Monitoreo

### Control de Costes IA
Todos los usos de Groq se registran en `uso_ia`:
```sql
SELECT
  proveedor,
  modelo,
  SUM(tokens_entrada) as total_entrada,
  SUM(tokens_salida) as total_salida,
  SUM(tokens_entrada + tokens_salida) as total,
  COUNT(*) as num_llamadas
FROM uso_ia
GROUP BY proveedor, modelo;
```

### Análisis de Operaciones
```sql
-- Inversión total por cripto
SELECT
  cripto,
  SUM(CASE WHEN tipo = 'Compra' THEN valor_total + comision ELSE 0 END) as invertido,
  SUM(CASE WHEN tipo = 'Venta' THEN valor_total - comision ELSE 0 END) as recuperado
FROM operaciones
GROUP BY cripto;
```

---

## 🔐 Seguridad

### Consideraciones Actuales
- ✅ API keys en archivo `.env` (no versionado)
- ✅ Logs rotativos para evitar llenado de disco
- ⚠️ API Flask sin autenticación (uso interno Node-RED)
- ⚠️ No hay rate limiting en endpoints

### Mejoras Recomendadas
- Añadir autenticación por token en endpoints sensibles
- Implementar rate limiting (Flask-Limiter)
- Cifrar `parametros.env` con herramientas como `sops`
- Usar HTTPS si se expone públicamente

---

## 🐛 Debugging

### Verificar Base de Datos
```bash
sqlite3 data/kryptonite.db "SELECT COUNT(*) FROM crypto_data;"
```

### Ver Logs en Tiempo Real
```bash
tail -f logs/kryptonite.log
```

### Probar Endpoint Manual
```bash
curl -X POST http://localhost:5000/prompt \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Cuántas criptos tengo en portfolio?"}'
```

---

## 📚 Referencias Técnicas

- **Binance API Docs:** https://binance-docs.github.io/apidocs/
- **LangChain Docs:** https://python.langchain.com/
- **Groq API:** https://groq.com/
- **NewsAPI:** https://newsapi.org/
- **pandas-ta:** https://github.com/twopirllc/pandas-ta

---

**Última actualización:** 2025-12-13
