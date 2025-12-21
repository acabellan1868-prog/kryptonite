# 🔮 Kryptonite

> Sistema inteligente de análisis y gestión de inversiones en criptomonedas

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-Private-red.svg)]()
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

---

## 📖 Descripción

**Kryptonite** es una aplicación diseñada para simplificar las decisiones de inversión en criptomonedas mediante análisis técnico, inteligencia artificial y automatización. El objetivo es proporcionar herramientas para tomar decisiones basadas en datos en un mercado volátil.

El nombre es simbólico: mientras que la kryptonita es la debilidad de Superman, **Kryptonite** es tu punto fuerte en el mercado cripto.

### ✨ Características Principales

- 📊 **Análisis técnico automatizado** con múltiples indicadores
- 🤖 **Agente IA conversacional** para consultas en lenguaje natural
- 📈 **Backtesting de estrategias** con datos históricos
- 💰 **Seguimiento de portfolio** en tiempo real
- 🔔 **Sistema de alertas** personalizables
- 📱 **Interfaz vía Telegram** para control remoto
- 🔄 **Actualización continua** de datos (granularidad 1 minuto)
- 📉 **Visualización de datos** con gráficas interactivas

---

## 🏗️ Arquitectura

```
┌─────────────────┐
│    TELEGRAM     │ ← Interfaz de usuario
│   (Usuario)     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│    NODE-RED     │ ← Orquestador de flujos
│  (Middleware)   │    - Tareas programadas
└────────┬────────┘    - Integración Telegram ↔ Kryptonite
         │
         ↓
┌─────────────────┐
│   KRYPTONITE    │ ← Backend de análisis
│  (Flask API)    │    - Datos históricos
└────────┬────────┘    - Análisis técnico
         │             - Agente IA
         ↓             - Backtesting
┌─────────────────┐
│   BINANCE API   │ ← Fuente de datos
└─────────────────┘
```

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| **Lenguaje** | Python 3.11 |
| **Framework API** | Flask |
| **Base de Datos** | SQLite |
| **Orquestador** | Node-RED |
| **Interfaz** | Telegram Bot |
| **Exchange** | Binance |
| **IA/LLM** | Groq (LangChain) |
| **ML** | scikit-learn |
| **Análisis Técnico** | pandas-ta |
| **Visualización** | Matplotlib, Plotly |

---

## 📊 Base de Datos

### Tablas Principales

- **`cryptos`**: Catálogo de criptomonedas monitoreadas
- **`crypto_data`**: Datos históricos (precio, volumen, market cap) - granularidad 1 minuto
- **`operaciones`**: Registro de transacciones reales (compras/ventas)
- **`uso_ia`**: Tracking de uso de tokens de IA (control de costes)
- **`alerts`**: Sistema de alertas configurables
- **`users`**: Gestión de usuarios

---

## 🚀 Instalación

### Requisitos Previos

- Python 3.11+
- SQLite 3
- Node-RED (para automatización)
- Cuenta en Binance (para datos de mercado)
- API Key de Groq (para agente IA)
- API Key de NewsAPI (para análisis de sentimiento)

### Configuración

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/acabellan1868-prog/kryptonite.git
   cd kryptonite
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # .venv\Scripts\activate   # Windows
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   
   Crea un archivo `parametros.env` basándote en el ejemplo:
   ```bash
   cp parametros.env.example parametros.env
   ```
   
   Edita `parametros.env` con tus API keys:
   ```env
   GROQ_API_KEY=gsk_your_key_here
   GROQ_MODELO=llama-3.3-70b-versatile
   NEWS_API_KEY=your_news_api_key_here
   ```

5. **Inicializar base de datos**
   
   La base de datos se crea automáticamente al ejecutar la aplicación por primera vez.

---

## 💻 Uso

### Iniciar la API

```bash
python src/api.py
```

La API estará disponible en: `http://localhost:5000`

### Endpoints Principales

#### 📥 Gestión de Datos
- `POST /run` - Cargar datos de favoritos (últimos 30 min)

#### 💰 Precios y Valores
- `GET /valor?crypto=BTC&timeframe=1d` - Precio actual y métricas

#### 📈 Gráficas
- `GET /grafica24h?crypto=BTC` - Gráfica de 24h en base64

#### 💼 Portfolio
- `GET /portafolio` - Rendimiento completo del portfolio

#### 🚦 Señales de Trading
- `GET /senal/cambio_extremo?cripto=BTC` - Señales basadas en cambios extremos

#### 📊 Backtesting
- `POST /backtest` - Probar estrategias con datos históricos

#### 🤖 Inteligencia Artificial
- `GET /analisis_ia` - Análisis del portfolio por IA
- `GET /sentimiento_noticias?cripto=BTC` - Análisis de sentimiento
- `POST /prompt` - Consultas en lenguaje natural

### Ejemplos de Uso

#### Consultar precio actual
```bash
curl http://localhost:5000/valor?crypto=BTC
```

#### Obtener señal de trading
```bash
curl "http://localhost:5000/senal/cambio_extremo?cripto=BTC&intervalo_minutos=15&umbral_porcentual=1.0"
```

#### Consulta al agente IA
```bash
curl -X POST http://localhost:5000/prompt \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Cuánto he invertido en BTC?"}'
```

---

## 🤖 Agente IA

El agente conversacional basado en LangChain permite:

- Consultas en lenguaje natural sobre tu portfolio
- Análisis automático de datos históricos
- Acceso a herramientas MCP para consultar la base de datos
- Tracking de uso de tokens

**Herramientas disponibles:**
- `listar_tablas_base_de_datos`
- `obtener_esquema_tabla`
- `consultar_base_de_datos`
- `obtener_datos_tabla`

---

## 📈 Estrategias de Trading

### 1. Cambio Extremo (Reversión a la Media)

Detecta cambios porcentuales significativos:
- Precio sube rápido → Señal de VENTA (espera corrección)
- Precio baja rápido → Señal de COMPRA (espera rebote)

**Parámetros configurables:**
- `intervalo_minutos`: Ventana temporal (default: 15 min)
- `umbral_porcentual`: % de cambio mínimo (default: 1.0%)
- `confirmar_con_volumen`: Validar con volumen anómalo (default: true)

### 2. Cruce de Medias Móviles

Señales basadas en cruces de medias móviles:
- Cruce alcista → COMPRAR
- Cruce bajista → VENDER

---

## 🧪 Backtesting

Prueba estrategias con datos históricos antes de operar:

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

---

## 📁 Estructura del Proyecto

```
kryptonite/
├── src/                    # Código fuente
│   ├── ia/                 # Módulos de IA
│   │   ├── grog_agente.py  # Agente LangChain
│   │   └── mcp_sqlite_tools.py
│   ├── api.py              # API Flask
│   ├── database.py         # Gestión BD
│   ├── analysis.py         # Análisis técnico
│   ├── backtesting.py      # Motor de backtesting
│   └── charts.py           # Gráficas
│
├── data/                   # Datos (no versionado)
│   └── kryptonite.db       # Base de datos SQLite
│
├── documentacion/          # Documentación
│   ├── project-overview.md
│   └── roadmap-2025.md
│
├── logs/                   # Logs (no versionado)
├── requirements.txt        # Dependencias Python
└── README.md              # Este archivo
```

---

## 🔐 Seguridad

- ✅ API keys en archivo `.env` (no versionado)
- ✅ Base de datos con información personal (no versionada)
- ✅ Logs rotativos (max 5 MB, 3 backups)
- ⚠️ API Flask sin autenticación (uso interno via Node-RED)

---

## 📊 Monitoreo

### Control de Costes IA

Todos los usos de Groq se registran en la tabla `uso_ia`:

```sql
SELECT
  proveedor,
  modelo,
  SUM(tokens_entrada) as total_entrada,
  SUM(tokens_salida) as total_salida,
  COUNT(*) as num_llamadas
FROM uso_ia
GROUP BY proveedor, modelo;
```

---

## 🗺️ Roadmap

Ver [`documentacion/roadmap-2025.md`](documentacion/roadmap-2025.md) para planes futuros:

- ✨ Optimizador de portfolio inteligente
- 🤖 Mejoras al agente IA (proactividad, historial)
- 🔔 Sistema de alertas avanzadas con condiciones complejas
- 📈 Análisis predictivo mejorado (ML)
- 💼 Sistema de paper trading
- 📊 Análisis multi-timeframe
- 📄 Reportes automáticos en PDF

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

### Probar Endpoint
```bash
curl http://localhost:5000/prompt/status
```

---

## 📚 Referencias

- [Binance API Docs](https://binance-docs.github.io/apidocs/)
- [LangChain Docs](https://python.langchain.com/)
- [Groq API](https://groq.com/)
- [NewsAPI](https://newsapi.org/)
- [pandas-ta](https://github.com/twopirllc/pandas-ta)

---

## 📝 Licencia

Este proyecto es de uso personal y privado.

---

## 👤 Autor

**Buenos Días**

---

## 🙏 Agradecimientos

Desarrollado con la asistencia de Claude (Anthropic) para arquitectura, desarrollo y documentación.

---

**Última actualización:** Diciembre 2024
