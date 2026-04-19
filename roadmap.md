# Roadmap — Kryptonite

## Estado actual

**Fecha:** 2026-04-18

Fase 1 completada. Sistema en producción con portfolio analyzer, agente IA mejorado
y detección de cambios desde última consulta. Sin fase activa en curso.

**Próximo paso:** Elegir entre alertas avanzadas (Fase 1.2.2/Sistema Alertas) o
historial persistente del agente IA (Fase 1.2.2). Ver `documentacion/roadmap-2026.md`
para el análisis detallado de cada opción.

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

### Fase 6 — Expansión (opcional, futuro)

- [ ] Multi-Exchange (Kraken, Coinbase...)
- [ ] Webhooks en lugar de polling desde Node-RED
- [ ] Dashboard web standalone
