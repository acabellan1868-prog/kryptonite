# 🔮 Kryptonite

> Sistema inteligente de análisis y gestión de inversiones en criptomonedas

[![Python](https://img.shields.io/badge/Python-3.11.2-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-Private-red.svg)]()
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()
[![GitHub](https://img.shields.io/badge/GitHub-Kryptonite-181717.svg?logo=github)](https://github.com/acabellan1868-prog/kryptonite)

---

## 📑 Tabla de Contenidos

- [Inicio Rápido](#-inicio-rápido)
- [Descripción](#-descripción)
- [Características Principales](#-características-principales)
- [Arquitectura](#-arquitectura)
- [Stack Tecnológico](#-stack-tecnológico)
- [Base de Datos](#-base-de-datos)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Agente IA Conversacional](#-agente-ia-conversacional)
- [Estrategias de Trading](#-estrategias-de-trading)
- [Backtesting](#-backtesting)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Seguridad](#-seguridad)
- [Roadmap 2025](#-roadmap-2025)
- [Referencias](#-referencias-y-documentación)
- [Autor](#-autor)

---

## 🚀 Inicio Rápido

```bash
# Clonar el repositorio
git clone https://github.com/acabellan1868-prog/kryptonite.git
cd kryptonite

# Crear entorno virtual e instalar dependencias
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configurar variables de entorno
cp parametros.env.example parametros.env
# Edita parametros.env con tus API keys

# Iniciar la API
python3 src/api.py
```

> La API estará disponible en `http://localhost:5000`

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
| **Lenguaje** | Python 3.11.2 |
| **Framework API** | Flask 3.0 |
| **Base de Datos** | SQLite 3 |
| **Orquestador** | Node-RED (opcional) |
| **Interfaz** | Telegram Bot + API REST |
| **Exchange** | Binance API |
| **IA/LLM** | Groq (llama-3.3-70b-versatile) |
| **Framework IA** | LangChain + LangGraph |
| **ML** | scikit-learn 1.3.0 |
| **Análisis Técnico** | pandas-ta 0.3.14b0 |
| **Visualización** | Matplotlib 3.7.2, Plotly 5.11.0 |
| **APIs Crypto** | ccxt 4.4.58, python-binance 1.0.18 |

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

- Python 3.11.2+
- SQLite 3
- Node-RED (opcional, para automatización vía Telegram)
- Cuenta en Binance (para datos de mercado en tiempo real)
- API Key de Groq (para agente IA conversacional)
- API Key de NewsAPI (opcional, para análisis de sentimiento de noticias)

### Configuración

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/acabellan1868-prog/kryptonite.git
   cd kryptonite
   ```

2. **Crear entorno virtual**
   ```bash
   python3 -m venv .venv
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
python3 src/api.py
```

La API estará disponible en: `http://localhost:5000`

> **Nota:** Por defecto, la API Flask no requiere autenticación ya que está diseñada para uso interno vía Node-RED en entorno local.

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

## 🤖 Agente IA Conversacional

El agente inteligente está construido con **LangChain** y **Groq** (modelo llama-3.3-70b-versatile) y permite:

- **Consultas en lenguaje natural** sobre tu portfolio y operaciones
- **Análisis automático** de datos históricos de criptomonedas
- **Acceso directo a la base de datos** mediante herramientas MCP (Model Context Protocol)
- **Tracking de uso de tokens** para control de costes
- **Respuestas contextuales** basadas en datos reales en tiempo real

### Herramientas MCP Disponibles

El agente tiene acceso a las siguientes herramientas para consultar la base de datos:

- `listar_tablas_base_de_datos` - Lista todas las tablas disponibles
- `obtener_esquema_tabla` - Obtiene la estructura de una tabla específica
- `consultar_base_de_datos` - Ejecuta consultas SQL personalizadas
- `obtener_datos_tabla` - Recupera datos completos de una tabla

### Ejemplos de Consultas

```
- "¿Cuánto he invertido en total en BTC?"
- "¿Cuál es mi criptomoneda más rentable?"
- "Muéstrame mis últimas 5 operaciones"
- "¿Qué porcentaje de mi portfolio es ETH?"
```

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
├── src/                        # Código fuente principal
│   ├── ia/                     # Módulos de Inteligencia Artificial
│   │   ├── grog_agente.py      # Agente conversacional LangChain
│   │   └── mcp_sqlite_tools.py # Herramientas MCP para consultar BD
│   ├── api.py                  # API Flask (endpoints REST)
│   ├── database.py             # Gestión de base de datos SQLite
│   ├── analysis.py             # Análisis técnico y señales de trading
│   ├── backtesting.py          # Motor de backtesting de estrategias
│   └── charts.py               # Generación de gráficas
│
├── data/                       # Datos persistentes (no versionado)
│   └── kryptonite.db           # Base de datos SQLite
│
├── documentacion/              # Documentación del proyecto
│   ├── project-overview.md     # Visión general del proyecto
│   └── roadmap-2025.md         # Roadmap y planes futuros
│
├── logs/                       # Archivos de log (no versionado)
│   └── kryptonite.log          # Log rotativo (max 5MB, 3 backups)
│
├── notebook/                   # Jupyter notebooks para análisis
├── scripts/                    # Scripts auxiliares
├── .venv/                      # Entorno virtual Python (no versionado)
│
├── parametros.env              # Variables de entorno (no versionado)
├── parametros.env.example      # Plantilla de configuración
├── requirements.txt            # Dependencias Python
├── .gitignore                  # Archivos excluidos de git
└── README.md                   # Este archivo
```

---

## 🔐 Seguridad

### Buenas Prácticas Implementadas

- ✅ **API keys** almacenadas en `parametros.env` (excluido de git)
- ✅ **Base de datos** con información personal en `data/` (no versionada)
- ✅ **Logs rotativos** automáticos (max 5 MB, 3 backups)
- ✅ **`.gitignore`** configurado para proteger datos sensibles
- ⚠️ **API Flask** sin autenticación (diseñada para uso interno vía Node-RED)

### Archivos Protegidos (.gitignore)

```
data/                    # Base de datos con operaciones reales
logs/                    # Archivos de log
parametros.env           # API keys y configuración
.venv/                   # Entorno virtual
__pycache__/            # Archivos compilados Python
*.pyc
*.db
*.log
```

> **Importante:** La API Flask está pensada para ejecutarse en un entorno local seguro. Si necesitas exponerla públicamente, implementa autenticación (JWT, OAuth, etc.).

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

## 🗺️ Roadmap 2025

Ver [documentacion/roadmap-2025.md](documentacion/roadmap-2025.md) para planes detallados.

### Próximas Funcionalidades

- ✨ **Optimizador de portfolio** con rebalanceo inteligente
- 🤖 **Mejoras al agente IA**: historial conversacional, proactividad
- 🔔 **Sistema de alertas avanzadas** con condiciones combinadas (precio + volumen + indicadores)
- 📈 **Análisis predictivo** mejorado con modelos de ML (LSTM, Random Forest)
- 💼 **Paper trading** completo para probar estrategias sin riesgo
- 📊 **Análisis multi-timeframe** (1m, 5m, 15m, 1h, 4h, 1d)
- 📄 **Reportes automáticos** en PDF (diarios, semanales, mensuales)
- 🌐 **Dashboard web** con React/Vue para visualización en tiempo real
- 🔄 **Integración con múltiples exchanges** (Kraken, Coinbase, etc.)

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

## 📚 Referencias y Documentación

### APIs y Servicios
- [Binance API Documentation](https://binance-docs.github.io/apidocs/) - Documentación oficial de Binance
- [Groq API](https://groq.com/) - LLM ultra-rápido para el agente IA
- [NewsAPI](https://newsapi.org/) - API de noticias para análisis de sentimiento

### Frameworks y Librerías
- [LangChain Documentation](https://python.langchain.com/) - Framework para aplicaciones LLM
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Framework para agentes stateful
- [pandas-ta](https://github.com/twopirllc/pandas-ta) - Indicadores técnicos para pandas
- [Flask Documentation](https://flask.palletsprojects.com/) - Framework web Python
- [ccxt](https://docs.ccxt.com/) - Biblioteca para conectar con exchanges

### Machine Learning
- [scikit-learn](https://scikit-learn.org/) - Machine Learning en Python

---

## 📝 Licencia

Este proyecto es de **uso personal y privado**. No está licenciado para uso comercial o distribución pública.

---

## 👤 Autor

**Antonio Cabello**
- GitHub: [@acabellan1868-prog](https://github.com/acabellan1868-prog)
- Proyecto: [Kryptonite](https://github.com/acabellan1868-prog/kryptonite)

---

## 🙏 Agradecimientos

Este proyecto ha sido desarrollado con la asistencia de **Claude Code** (Anthropic) para:
- Arquitectura del sistema
- Desarrollo del código
- Implementación del agente IA
- Documentación técnica
- Optimización y debugging

---

## 🤝 Contribuciones

Este es un proyecto personal y privado. No se aceptan contribuciones externas en este momento.

---

## 📞 Soporte

Para reportar problemas o sugerencias:
1. Abre un [Issue](https://github.com/acabellan1868-prog/kryptonite/issues) en GitHub
2. Describe el problema o sugerencia de forma clara
3. Incluye logs o capturas si es posible

---

## ⚠️ Disclaimer

**Kryptonite** es una herramienta de análisis y **no constituye asesoramiento financiero**.

- El trading de criptomonedas conlleva **riesgo de pérdida de capital**
- Las decisiones de inversión son **responsabilidad exclusiva del usuario**
- Los resultados de backtesting **no garantizan rendimientos futuros**
- Usa este software bajo tu propio riesgo

---

**Última actualización:** Diciembre 2025
