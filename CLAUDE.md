# CLAUDE.md — Kryptonite

## Qué es
Sistema de análisis y gestión de inversiones en criptomonedas. Obtiene datos de Binance, analiza portfolio, detecta señales de trading y responde consultas en lenguaje natural mediante un agente IA (Inteligencia Artificial).

- **Repo:** acabellan1868-prog/kryptonite
- **Local:** `Desarrollo/Claude/kryptonite/`
- **Servidor:** VM 101 (`/mnt/datos/kryptonite-build/`), contenedor Docker
- **Puerto:** `5001` externo → Nginx proxy `/crypto/api/`

## Stack
- Python + **FastAPI** + Uvicorn
- SQLite (`data/kryptonite.db`, ~292 MB de datos históricos)
- LangChain + Groq (LLM: llama-3.3-70b-versatile)
- Node-RED (orquestador de tareas recurrentes y flujos Telegram)
- Telegram Bot (interfaz de usuario)
- Binance API (fuente de datos de mercado)

## Estructura

```
kryptonite/
├── app/
│   ├── principal.py            ← entrada FastAPI, lifespan (LLM + agente inicializados una vez)
│   ├── esquemas.py             ← modelos Pydantic para request bodies
│   ├── config.py               ← configuración global (prefijo KRYPTO_)
│   ├── database.py             ← acceso SQLite
│   ├── binance_data.py         ← integración Binance
│   ├── analysis.py             ← análisis técnico y señales
│   ├── backtesting.py          ← motor de backtesting
│   ├── charts.py               ← generación de gráficas
│   ├── modelo_ia.py            ← modelos ML (Random Forest, sin integrar)
│   ├── main.py                 ← carga de datos
│   ├── ia/
│   │   ├── grog_agente.py      ← agente LangChain principal
│   │   └── mcp_sqlite_tools.py ← herramientas MCP para SQLite
│   └── rutas/
│       ├── datos.py            ← /run
│       ├── portfolio.py        ← /valor, /grafica24h, /portafolio, /limpiar, /nuevaOperacion
│       ├── analisis.py         ← /senal/cambio_extremo, /backtest
│       └── ia.py               ← /analisis_ia, /sentimiento_noticias, /prompt, /prompt/status
├── data/
│   └── kryptonite.db           ← BD SQLite
├── documentacion/
│   ├── roadmap-2026.md         ← ideas y brainstorming detallado
│   └── roadmap-dockerizacion.md
├── Dockerfile
├── docker-compose.yml
├── parametros.env              ← API keys (no en git)
└── parametros.env.example
```

## API

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/run` | Carga datos de favoritos últimos 30 min (Node-RED cron) |
| GET | `/valor?crypto=BTC&timeframe=1d` | Precio actual, volumen, media móvil |
| GET | `/grafica24h?crypto=BTC` | Gráfica 24h en base64. Sin `crypto` → comparativa portfolio |
| GET | `/portafolio` | Rendimiento completo del portfolio |
| GET | `/portafolio?analisis=completo` | Portfolio + análisis de riesgo y alertas de concentración |
| GET | `/limpiar` | Elimina duplicados en `crypto_data` |
| POST | `/nuevaOperacion` | Registra una nueva operación de compra/venta |
| GET | `/senal/cambio_extremo` | Detecta cambios extremos de precio |
| POST | `/backtest` | Backtesting de estrategias |
| GET/POST | `/analisis_ia` | Análisis del portfolio por IA |
| GET | `/sentimiento_noticias?cripto=BTC` | Sentimiento de noticias (NewsAPI + Groq) |
| POST | `/prompt` | Agente LangChain — consultas en lenguaje natural |
| GET | `/prompt/status` | Estado del agente |

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `GROQ_API_KEY` | Clave API de Groq |
| `GROQ_MODELO` | Modelo LLM (defecto: `llama-3.3-70b-versatile`) |
| `NEWS_API_KEY` | Clave NewsAPI para sentimiento de noticias |

## Gotchas

- **Puerto 5001:** El 5000 está ocupado por JupyterLab en la VM. El contenedor expone el 5001 externamente.
- **BD de 292 MB:** No mover ni recrear sin backup previo — contiene años de datos históricos de precios.
- **Modelo ML sin usar:** `modelo_ia.py` con Random Forest existe pero no está integrado en ningún endpoint.
- **Agente stateless:** La memoria de LangChain se reinicia antes de cada pregunta — sin contexto entre consultas.
- **Despliegue:** El repo se clona en `/mnt/datos/kryptonite-build/` y el build Docker se hace en el servidor. Los volúmenes de datos están en `/mnt/datos/kryptonite/`.
