# Roadmap — Kryptonite

## Estado actual

**Fecha:** 2026-06-01

**Fases 1-3 y 7.1-7.3 completadas.** La autenticación Ed25519 con Revolut X está resuelta. La integración de recompensas de staking se ha descartado por limitaciones de la API.

- ✅ Autenticación Ed25519 funcionando correctamente
- ✅ Endpoint `/balances` de Revolut X accesible (saldos por moneda)
- ❌ **Descartado:** Revolut X no expone historial de recompensas de staking por API ni permite exportar CSV desde la app

**Situación:** Las recompensas de staking (DOT y ADA) no se registran en Kryptonite. Diferencia actual: ~1.10 DOT y ~2.47 ADA sin contabilizar.

**Próximo paso:** Sin acción planificada en la fase 7. Continuar con fase 2, 3 o 4 según prioridad.

### Fases 1, 2 y 3 completadas ✅
- ✅ `src/` renombrado a `app/` via `git mv`
- ✅ `app/config.py` limpiado: sin `os.chdir`, rutas relativas, prefijo `KRYPTO_`
- ✅ `Dockerfile` creado (python:3.12-slim, PYTHONPATH=/app/app, entry Flask)
- ✅ `docker-compose.yml` creado
- ✅ `kryptonite-build` clonado en VM 101 (`/mnt/datos/kryptonite-build/`)
- ✅ Build Docker exitoso en el servidor
- ✅ Contenedor arranca correctamente (puerto 5001)
- ✅ BD copiada de JupyterLab a `/mnt/datos/kryptonite/data/kryptonite.db` (292 MB)
- ✅ Endpoints verificados: `/portafolio`, `/portafolio?analisis=completo`, `/valor`, `/senal/cambio_extremo`

---

## Fases

### Fase 1 — Optimización de lo existente ✅

- [x] 🤖 Optimizador de portfolio (composición %, alertas de concentración, métricas de riesgo)
- [x] 🤖 Endpoint `/portafolio?analisis=completo` — 100% retrocompatible
- [x] 🤖 Mejoras al agente IA (Fase 1.2.1) — 3 nuevas herramientas MCP, señales automáticas, rendimiento histórico
- [x] 🤖 Detección de cambios desde última consulta (Fase 1.3) — snapshots automáticos, comparación con estado anterior

### Fase 2 — Mejoras al agente (pendiente)

- [ ] 🤖 Historial persistente de conversaciones (Fase 1.2.2)
- [ ] 🤖 Modo Experto / Principiante (Fase 1.2.3)
- [ ] 🤖 Recomendaciones proactivas (Fase 1.2.4)

### Fase 3 — Alertas avanzadas (pendiente)

Sistema de alertas con condiciones complejas (precio + volumen + sentimiento + indicadores técnicos).

- [ ] 🤖 Endpoint `POST /alertas/crear` con condiciones combinables
- [ ] 🤖 Motor de evaluación periódica (Node-RED trigger)
- [ ] 🤖 Historial de alertas disparadas
- [ ] 👤 Configurar flujo en Node-RED para enviar alertas por Telegram

### Fase 4 — Capacidades predictivas (pendiente)

- [ ] 🤖 Integrar modelo Random Forest existente en endpoints
- [ ] 🤖 Re-entrenar y documentar qué predice el modelo
- [ ] 🤖 Análisis multi-timeframe (señales en varias temporalidades)

### Fase 5 — Experimentación (pendiente)

- [ ] 🤖 Paper trading (simulador sin riesgo)
- [ ] 🤖 Reportes PDF automáticos (diario/semanal/mensual)

### Fase 7 — Integración Revolut X API ✅ (Fases 7.1-7.3 completadas)

Automatizar la importación de recompensas de staking de DOT (Polkadot) y ADA (Cardano) desde Revolut X hacia la tabla `operaciones` de la BD.

#### 7.1 — Autenticación Ed25519 ✅
- [x] 👤 Generar par de claves Ed25519 con OpenSSL en local
- [x] 👤 Registrar la clave pública en el panel de Revolut X (`exchange.revolut.com`)
- [x] 👤 Añadir `REVOLUT_API_KEY` y `REVOLUT_PRIVATE_KEY` a `parametros.env`
- [x] 🤖 Añadir las variables a `parametros.env.example` (sin valores)
- [x] 🤖 Declarar las variables en `app/config.py` con prefijo `KRYPTO_`

#### 7.2 — Módulo de integración `app/revolut_x.py` ✅
- [x] 🤖 Función de firma Ed25519 (headers `X-Revx-API-Key`, `X-Revx-Timestamp`, `X-Revx-Signature`)
- [x] 🤖 Función `obtener_trades(simbolo, inicio, fin)` — ventana máx. 7 días
- [x] 🤖 Función `obtener_recompensas(moneda, desde, hasta)` — itera en ventanas de 7 días y filtra por tipo recompensa
- [x] 🤖 Lógica anti-duplicados basada en `transaction_id` de Revolut X

#### 7.3 — Endpoints de sincronización `app/rutas/revolut.py` ✅
- [x] 🤖 `GET /revolut/sincronizar?moneda=DOT&desde=YYYY-MM-DD` — descarga e inserta recompensas
- [x] 🤖 `GET /revolut/sincronizar` sin parámetros — sincroniza DOT y ADA del 1ro del mes a hoy
- [x] 🤖 `GET /revolut/estado` — devuelve estado de sincronizaciones
- [x] 🤖 Registrar el nuevo router en `app/principal.py`

#### 7.4 — Carga histórica inicial
- [ ] 👤 Determinar fecha de la primera recompensa en Revolut X para DOT y ADA
- [ ] 🤖 Ejecutar carga histórica completa desde esa fecha hasta hoy
- [ ] 👤 Verificar que los datos coinciden con lo que muestra la app de Revolut X

#### 7.5 — Automatización periódica con Node-RED
- [ ] 👤 Crear flujo en Node-RED que llame a `/revolut/sincronizar` semanalmente
- [ ] 👤 Verificar que las nuevas recompensas aparecen en `/portafolio`

---

### Fase 6 — Expansión (opcional, futuro)

- [ ] Multi-Exchange (Kraken, Coinbase...)
- [ ] Webhooks en lugar de polling desde Node-RED
- [ ] Dashboard web standalone
