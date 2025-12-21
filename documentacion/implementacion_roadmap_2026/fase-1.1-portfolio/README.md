# Fase 1.1 - Optimizador de Portfolio Inteligente

**Estado:** ✅ Completado
**Fecha:** 2025-12-14
**Versión:** 1.0

---

## 📋 Descripción

Implementación del análisis avanzado de portfolio con detección de alertas, métricas de riesgo y composición porcentual de cada criptomoneda.

---

## 📁 Documentación de esta Fase

- **[implementacion.md](implementacion.md)** - Resumen ejecutivo completo de la implementación
- **[ejemplos-api.md](ejemplos-api.md)** - Ejemplos de uso del endpoint `/portafolio`

---

## 🎯 Funcionalidades Implementadas

### ✅ Análisis de Composición
- Cálculo del % que representa cada cripto del portfolio total
- Campo `peso_portfolio_pct` en cada cripto

### ✅ Detección de Alertas Individuales
- `sobreexpuesto`: Cuando una cripto supera el umbral configurado (default: 40%)
- `perdida_severa`: Cuando la rentabilidad < umbral configurado (default: -50%)

### ✅ Análisis Global
- Alertas automáticas de concentración
- Alertas de mayoría en pérdidas
- Top 3 pérdidas severas

### ✅ Métricas de Riesgo
- **Score de diversificación**: Baja/Media/Alta
- **Exposición al riesgo**: Baja/Media/Alta
- **Concentración top 2**: % acumulado de las 2 cryptos más grandes
- **Contadores**: Activos rentables vs. en pérdidas

---

## 🔧 Archivos de Código

### Creados
- [`src/portfolio_analyzer.py`](../../../src/portfolio_analyzer.py) - Módulo principal de análisis

### Modificados
- [`src/api.py`](../../../src/api.py) - Endpoint `/portafolio` con modo completo
- [`src/config.py`](../../../src/config.py) - Carga de parámetros desde ENV
- [`parametros.env`](../../../parametros.env) - Nuevos umbrales configurables

---

## 🚀 Uso Rápido

### Modo Básico (Retrocompatible)
```bash
GET /portafolio
```
Devuelve el formato original, compatible con Node-RED actual.

### Modo Completo (Nuevo)
```bash
GET /portafolio?analisis=completo
```
Devuelve estructura enriquecida con análisis avanzado.

---

## ⚙️ Configuración

Parámetros configurables en [`parametros.env`](../../../parametros.env):

```bash
UMBRAL_SOBREEXPOSICION=40        # % máximo por cripto
UMBRAL_PERDIDA_SEVERA=-50        # % para pérdida severa
UMBRAL_CONCENTRACION_ALTA=60     # % top 2 para alta concentración
```

---

## 📊 Ejemplo de Respuesta (Modo Completo)

```json
{
  "portfolio": [
    {
      "simbolo": "BTC",
      "peso_portfolio_pct": 42.6,
      "alertas": ["sobreexpuesto"],
      ...
    }
  ],
  "totales": {
    "total_invertido": 1166.16,
    "valor_actual": 760.73,
    "rentabilidad_total_pct": -34.77
  },
  "analisis": {
    "alertas_globales": [...],
    "metricas": {
      "diversificacion_score": "Media",
      "exposicion_riesgo": "Alta"
    }
  }
}
```

---

## ✅ Compatibilidad

| Componente | Estado |
|------------|--------|
| API `/portafolio` | ✅ 100% compatible |
| Node-RED actual | ✅ Sin cambios necesarios |
| Telegram | ✅ Funciona igual |

---

## 📖 Más Información

- [Implementación completa](implementacion.md)
- [Ejemplos de API](ejemplos-api.md)
- [Roadmap general](../../roadmap-2026.md)

---

**Desarrollado:** 2025-12-14
**Próxima fase:** 1.2 - Mejoras al Agente IA
