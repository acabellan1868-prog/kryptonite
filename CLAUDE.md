# CLAUDE.md — Kryptonite

## Qué es
Sistema de análisis y gestión de inversiones en criptomonedas. Obtiene datos de Binance, analiza portfolio, detecta señales de trading y responde consultas en lenguaje natural mediante un agente IA (Inteligencia Artificial).

- **Repo:** acabellan1868-prog/kryptonite
- **Local:** `Desarrollo/kryptonite/`
- **Servidor:** JupyterLab en VM 101 (`/mnt/datos/jupyter/kryptonite/`)
- **Puerto:** `5000` → Nginx proxy `/crypto/api/`

## Stack
- Python + **Flask** (no FastAPI — proyecto anterior al estándar del ecosistema)
- SQLite (`data/kryptonite.db`, ~185 MB de datos históricos)
- LangChain + Groq (LLM: llama-3.3-70b-versatile)
- Node-RED (orquestador de tareas recurrentes y flujos Telegram)
- Telegram Bot (interfaz de usuario)
- Binance API (fuente de datos de mercado)

## Estructura

```
kryptonite/
├── src/
│   ├── api.py                  ← Flask API (endpoints)
│   ├── main.py                 ← carga de datos
│   ├── database.py             ← acceso SQLite
│   ├── binance_data.py         ← integración Binance
│   ├── analysis.py             ← análisis técnico y señales
│   ├── backtesting.py          ← motor de backtesting
│   ├── charts.py               ← generación de gráficas
│   ├── config.py               ← configuración global
│   ├── modelo_ia.py            ← modelos ML (Random Forest)
│   └── ia/
│       ├── grog_agente.py      ← agente LangChain principal
│       └── mcp_sqlite_tools.py ← herramientas MCP para SQLite
├── data/
│   └── kryptonite.db           ← BD SQLite
├── documentacion/
│   ├── analisis.md             ← análisis de datos históricos
│   ├── roadmap-2026.md         ← ideas y brainstorming detallado
│   └── roadmap-dockerizacion.md
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
| GET | `/senal/cambio_extremo` | Detecta cambios extremos de precio |
| POST | `/backtest` | Backtesting de estrategias |
| GET | `/analisis_ia` | Análisis del portfolio por IA |
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

- **Flask, no FastAPI:** Proyecto anterior al estándar del ecosistema. No migrar sin necesidad.
- **Sin Docker:** Corre directamente en JupyterLab, no en contenedor. Nginx hace proxy desde `/crypto/api/` a `host.docker.internal:5000`.
- **BD de 185 MB:** No mover ni recrear sin backup previo — contiene años de datos históricos de precios.
- **Modelo ML sin usar:** `random_forest_cripto.joblib` existe pero no está integrado en ningún endpoint.
- **Agente stateless:** La memoria de LangChain se reinicia antes de cada pregunta — sin contexto entre consultas.
