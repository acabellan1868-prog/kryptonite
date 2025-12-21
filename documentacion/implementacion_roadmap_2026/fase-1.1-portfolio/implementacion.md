# ✅ Fase 1.1 del Optimizador de Portfolio - IMPLEMENTADA

**Fecha:** 2025-12-14
**Estado:** Completado
**Versión:** 1.0

---

## 📋 Resumen Ejecutivo

Se ha implementado exitosamente la **Fase 1.1** del Optimizador de Portfolio Inteligente, tal como se describe en el [roadmap-2026.md](../roadmap-2026.md).

Esta fase añade capacidades de análisis avanzado al portfolio sin romper la compatibilidad con el sistema actual de Node-RED y Telegram.

---

## 🎯 Objetivos Cumplidos

### ✅ 1. Refactorización de Configuración
- **Archivo:** [`parametros.env`](../parametros.env)
- **Mejora:** Centralización de todos los parámetros configurables
- **Beneficio:** Cambiar umbrales sin tocar código

**Parámetros añadidos:**
```bash
UMBRAL_SOBREEXPOSICION=40        # % máximo recomendado por cripto
UMBRAL_PERDIDA_SEVERA=-50        # % para considerar pérdida severa
UMBRAL_CONCENTRACION_ALTA=60     # % top 2 cryptos para alta concentración
```

### ✅ 2. Actualización de config.py
- **Archivo:** [`src/config.py`](../src/config.py)
- **Mejora:** Carga automática desde `parametros.env`
- **Beneficio:** Un solo punto de configuración, fácil de mantener

### ✅ 3. Nuevo Módulo de Análisis
- **Archivo:** [`src/portfolio_analyzer.py`](../src/portfolio_analyzer.py)
- **Funcionalidades:**
  - ✅ Cálculo de composición del portfolio (% de cada cripto)
  - ✅ Detección de alertas individuales (sobreexposición, pérdidas severas)
  - ✅ Alertas globales automáticas
  - ✅ Métricas de riesgo (diversificación, exposición)

### ✅ 4. Endpoint Mejorado
- **Archivo:** [`src/api.py`](../src/api.py#L126)
- **Endpoint:** `GET /portafolio`
- **Mejora:** Soporte de 2 modos (básico y completo)
- **Beneficio:** Retrocompatibilidad total + nuevas funcionalidades

---

## 🔧 Arquitectura Implementada

```
┌─────────────────────────────────────────────────────────┐
│                     parametros.env                       │
│  (Configuración: umbrales, rutas, API keys)             │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│                     config.py                            │
│  (Carga ENV + constantes + logger)                      │
└──────────┬──────────────────────────────────────────────┘
           │
           ├──────────────┬────────────────┬───────────────┐
           ▼              ▼                ▼               ▼
    analisis_      portfolio_       database.py      api.py
 rendimineto.py   analyzer.py                        (Flask)
                                                         │
                                                         ▼
                                                   Node-RED
                                                         │
                                                         ▼
                                                    Telegram
```

---

## 📊 Nuevas Funcionalidades

### Modo Básico (Retrocompatible)
```
GET /portafolio
```
- Devuelve la lista de cryptos tal como antes
- Node-RED actual sigue funcionando sin cambios
- **0% riesgo de romper lo existente**

### Modo Completo (Nuevo)
```
GET /portafolio?analisis=completo
```
- Devuelve estructura enriquecida con 3 bloques:
  - `portfolio`: Datos de cada cripto + peso_portfolio_pct + alertas
  - `totales`: Valores consolidados del portfolio
  - `analisis`: Alertas globales + métricas de riesgo

---

## 📈 Nuevos Datos Disponibles

### Por Cripto (campo `peso_portfolio_pct`)
```json
{
  "simbolo": "BTC",
  "peso_portfolio_pct": 42.6,  // % del portfolio total
  "alertas": ["sobreexpuesto"]  // Alertas individuales
}
```

### Totales Consolidados
```json
{
  "totales": {
    "total_invertido": 1166.16,
    "valor_actual": 760.73,
    "rentabilidad_total_pct": -34.77,
    "rentabilidad_total_abs": -405.43
  }
}
```

### Análisis Global
```json
{
  "analisis": {
    "alertas_globales": [
      "BTC representa el 42.6% del portfolio (recomendado: <40%)",
      "5 de 6 activos están en pérdidas"
    ],
    "metricas": {
      "num_activos": 6,
      "activos_rentables": 1,
      "activos_perdidas": 5,
      "concentracion_top2_pct": 55.3,
      "diversificacion_score": "Media",
      "exposicion_riesgo": "Alta"
    }
  }
}
```

---

## 🎨 Tipos de Alertas

### Alertas Individuales
| Código | Descripción | Umbral |
|--------|-------------|--------|
| `sobreexpuesto` | Cripto representa >40% del portfolio | Configurable en ENV |
| `perdida_severa` | Rentabilidad < -50% | Configurable en ENV |

### Alertas Globales (Automáticas)
1. **Sobreexposición**: Detecta cryptos que superan el umbral
2. **Mayoría en pérdidas**: Cuando >50% de activos están en negativo
3. **Pérdidas severas**: Lista top 3 cryptos con peor rentabilidad

---

## 📐 Métricas de Riesgo

### Score de Diversificación
- **Alta**: ≥8 activos + top 2 < 50%
- **Media**: ≥5 activos + top 2 < 60%
- **Baja**: Resto de casos

### Exposición al Riesgo
- **Alta**: ≥50% activos con pérdidas severas
- **Media**: 25-50% activos con pérdidas severas
- **Baja**: <25% activos con pérdidas severas

### Concentración Top 2
Suma del % de las 2 cryptos más grandes del portfolio.

---

## 🧪 Testing

### Prueba Rápida del Módulo
```bash
cd /mnt/datos/jupyter/kryptonite
python3 src/portfolio_analyzer.py
```

Esto ejecutará un ejemplo con datos simulados y mostrará el JSON de salida.

### Prueba del Endpoint

**Opción 1: Modo básico (debe seguir funcionando igual)**
```bash
curl http://localhost:5000/portafolio
```

**Opción 2: Modo completo (nuevo)**
```bash
curl http://localhost:5000/portafolio?analisis=completo
```

---

## 📚 Documentación Creada

1. **[api-portfolio-ejemplos.md](api-portfolio-ejemplos.md)**
   - Ejemplos de uso del endpoint
   - Código JavaScript para Node-RED
   - Testing manual

2. **[test_config.py](../test_config.py)**
   - Script de verificación de configuración
   - Útil para debugging

---

## 🔄 Próximos Pasos (Opcionales)

### Opción A: Mantener como está
- Node-RED sigue usando el modo básico
- Cuando quieras, cambias a modo completo

### Opción B: Actualizar Node-RED gradualmente
1. Crear un nuevo flujo de prueba
2. Llamar a `/portafolio?analisis=completo`
3. Adaptar el JavaScript para mostrar las alertas
4. Probar en un chat de prueba
5. Cuando funcione, reemplazar el flujo original

### Opción C: Dos comandos diferentes
- `/portafolio` → Modo básico (como ahora)
- `/analisis` → Modo completo (nuevo comando)
- Así tienes ambos disponibles

---

## 🎯 Compatibilidad

| Componente | Estado | Notas |
|------------|--------|-------|
| API `/portafolio` | ✅ Compatible | Sin parámetros = modo básico |
| Node-RED actual | ✅ Compatible | Sigue funcionando sin cambios |
| Telegram | ✅ Compatible | Muestra lo mismo que antes |
| Base de datos | ✅ Compatible | No requiere cambios |
| Nuevas features | ✅ Disponibles | Con `?analisis=completo` |

---

## ⚙️ Configuración Flexible

Todos los umbrales son configurables en [`parametros.env`](../parametros.env):

```bash
# Cambiar estos valores sin tocar código
UMBRAL_SOBREEXPOSICION=40        # Default: 40%
UMBRAL_PERDIDA_SEVERA=-50        # Default: -50%
UMBRAL_CONCENTRACION_ALTA=60     # Default: 60%
```

**Para aplicar cambios:**
1. Editar `parametros.env`
2. Reiniciar la API Flask
3. Los nuevos valores se aplican inmediatamente

---

## 📝 Archivos Modificados/Creados

### Modificados
- ✏️ [`parametros.env`](../parametros.env) - Añadidos 3 parámetros nuevos
- ✏️ [`src/config.py`](../src/config.py) - Refactorizado para cargar desde ENV
- ✏️ [`src/api.py`](../src/api.py) - Endpoint `/portafolio` con soporte de 2 modos

### Creados
- ✨ [`src/portfolio_analyzer.py`](../src/portfolio_analyzer.py) - Módulo de análisis
- ✨ [`test_config.py`](../test_config.py) - Script de verificación
- ✨ [`documentacion/api-portfolio-ejemplos.md`](api-portfolio-ejemplos.md) - Documentación
- ✨ [`documentacion/FASE-1.1-IMPLEMENTADA.md`](FASE-1.1-IMPLEMENTADA.md) - Este archivo

---

## ✅ Checklist de Validación

- [x] Configuración refactorizada a `parametros.env`
- [x] `config.py` carga variables desde ENV
- [x] Módulo `portfolio_analyzer.py` implementado
- [x] Endpoint `/portafolio` con modo básico (retrocompatible)
- [x] Endpoint `/portafolio?analisis=completo` funcional
- [x] Cálculo de pesos de portfolio
- [x] Detección de alertas individuales
- [x] Generación de alertas globales
- [x] Cálculo de métricas de riesgo
- [x] Documentación completa
- [x] Script de testing
- [x] 100% retrocompatible con sistema actual

---

## 🚀 Conclusión

La Fase 1.1 está **completamente funcional** y lista para usar. El sistema actual sigue funcionando exactamente igual, pero ahora tienes acceso a análisis avanzado cuando lo necesites.

**Recomendación:** Probar primero con `curl` o navegador el endpoint con `?analisis=completo` para ver los datos enriquecidos antes de modificar Node-RED.

---

**Desarrollado por:** Claude Code
**Fecha de implementación:** 2025-12-14
**Versión:** 1.0 - Fase 1.1 Completa
