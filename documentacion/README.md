# 📚 Documentación de Kryptonite

Bienvenido a la documentación del proyecto **Kryptonite** - Sistema de análisis de inversiones en criptomonedas.

---

## 📋 Índice de Documentación

### 🎯 Planificación y Roadmap
- **[roadmap-2026.md](roadmap-2026.md)** - Plan de evolución y mejora del sistema (2026)
- **[implementacion_roadmap_2026/](implementacion_roadmap_2026/)** - Documentación detallada de cada fase implementada

### 📖 Documentación Técnica General
- **[kryptoniteDoc.md](kryptoniteDoc.md)** - Documentación principal del proyecto
- **[analisis.md](analisis.md)** - Documentación de análisis técnico y estrategias
- **[diagrama.md](diagrama.md)** - Diagramas de arquitectura del sistema

### 🤖 Inteligencia Artificial
- **[agenteLangChange.md](agenteLangChange.md)** - Documentación del agente LangChain
- **[token_tracking.md](token_tracking.md)** - Sistema de seguimiento de tokens de IA

### 📊 Visualizaciones
- **[kryptonite_graph.html](kryptonite_graph.html)** - Gráfico básico de arquitectura
- **[kryptonite_graph_advanced.html](kryptonite_graph_advanced.html)** - Gráfico avanzado de arquitectura
- **[kryptonite_diagrama_2025_06_20.html](kryptonite_diagrama_2025_06_20.html)** - Diagrama histórico

### 🗂️ Otros
- **[cementerioCode.md](cementerioCode.md)** - Código deprecado o ideas descartadas
- **[conversacionClaude1.md](conversacionClaude1.md)** - Conversaciones de diseño
- **[promp.md](promp.md)** - Prompts utilizados

---

## 🚀 Inicio Rápido

### Para Desarrolladores
1. Lee primero: [kryptoniteDoc.md](kryptoniteDoc.md)
2. Revisa la arquitectura: [diagrama.md](diagrama.md)
3. Consulta el roadmap: [roadmap-2026.md](roadmap-2026.md)

### Para Implementaciones Nuevas
1. Consulta: [roadmap-2026.md](roadmap-2026.md)
2. Revisa fases completadas: [implementacion_roadmap_2026/](implementacion_roadmap_2026/)
3. Sigue las convenciones establecidas

---

## 📁 Estructura de Carpetas

```
documentacion/
├── README.md                          # Este archivo (índice general)
├── roadmap-2026.md                    # Roadmap principal
├── implementacion_roadmap_2026/       # Implementaciones del roadmap
│   ├── README.md                      # Índice de implementaciones
│   └── fase-1.1-portfolio/           # Fase 1.1 completada
│       ├── README.md                  # Índice de la fase
│       ├── implementacion.md          # Resumen ejecutivo
│       └── ejemplos-api.md           # Ejemplos de uso
├── kryptoniteDoc.md                   # Doc principal técnica
├── analisis.md                        # Análisis y estrategias
├── agenteLangChange.md                # Agente IA
└── ... (otros archivos)
```

---

## 🔄 Convenciones

### Para Nuevas Implementaciones del Roadmap
1. Crear carpeta en `implementacion_roadmap_2026/fase-{numero}.{subfase}-{nombre}/`
2. Dentro de la carpeta crear:
   - `README.md` - Índice de la fase
   - `implementacion.md` - Detalles técnicos completos
   - `ejemplos-*.md` - Ejemplos de uso específicos
3. Actualizar el README de `implementacion_roadmap_2026/`
4. Actualizar el `roadmap-2026.md` con el estado y enlace

### Para Documentación General
- Usar Markdown con formato claro
- Incluir ejemplos de código cuando sea relevante
- Mantener un índice al inicio de documentos largos
- Fechar las actualizaciones importantes

---

## 📊 Estado del Proyecto

| Componente | Estado | Documentación |
|------------|--------|---------------|
| API Flask | ✅ Operativo | [kryptoniteDoc.md](kryptoniteDoc.md) |
| Análisis Técnico | ✅ Operativo | [analisis.md](analisis.md) |
| Agente IA (LangChain) | ✅ Operativo | [agenteLangChange.md](agenteLangChange.md) |
| Optimizador Portfolio | ✅ Implementado | [Fase 1.1](implementacion_roadmap_2026/fase-1.1-portfolio/) |
| Alertas Avanzadas | ⏸️ Pendiente | [roadmap-2026.md](roadmap-2026.md) |
| Paper Trading | ⏸️ Pendiente | [roadmap-2026.md](roadmap-2026.md) |

---

## 🔗 Enlaces Útiles

- [Código Fuente](../src/)
- [Datos](../data/)
- [Logs](../logs/)
- [Configuración](../parametros.env)

---

**Última actualización:** 2025-12-14
**Mantenido por:** Equipo Kryptonite
