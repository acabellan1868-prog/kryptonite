# ✅ Fase 1.3 - Detección de Cambios desde Última Consulta - IMPLEMENTADA

**Fecha:** 2025-12-15
**Estado:** Completado
**Versión:** 1.0

---

## 📋 Resumen Ejecutivo

Se ha implementado exitosamente la **Fase 1.3** del Optimizador de Portfolio Inteligente, que añade capacidades de detección automática de cambios entre consultas consecutivas del endpoint `/portafolio?analisis=completo`.

Esta fase permite ver automáticamente qué ha cambiado en el portfolio desde la última vez que se consultó, sin necesidad de comparar manualmente entre llamadas.

---

## 🎯 Objetivos Cumplidos

### ✅ 1. Sistema de Snapshots Automáticos
- **Funcionalidad:** Guarda automáticamente el estado del portfolio en cada consulta
- **Tabla:** Nueva tabla `portfolio_snapshots` en la base de datos
- **Beneficio:** Histórico automático sin intervención manual

### ✅ 2. Comparación Automática
- **Funcionalidad:** Compara el estado actual con el snapshot anterior
- **Módulo:** Nuevo `portfolio_diff.py` con lógica de comparación
- **Beneficio:** Detecta cambios en valor, precio, rentabilidad y peso

### ✅ 3. Detección de Nuevas Posiciones y Cierres
- **Funcionalidad:** Identifica cryptos añadidas o eliminadas del portfolio
- **Beneficio:** Visibilidad clara de cambios en la composición

### ✅ 4. Formato de Tiempo Legible
- **Funcionalidad:** Muestra tiempo transcurrido en formato humano
- **Ejemplo:** "2 horas 15 minutos" en lugar de "8115 segundos"
- **Beneficio:** Información más comprensible

---

## 🔧 Arquitectura Implementada

```
┌────────────────────────────────────────────────────────┐
│                  GET /portafolio?analisis=completo      │
└───────────────────┬────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│          portfolio_analyzer.py                          │
│  - analizar_portfolio_completo()                       │
│  - incluir_cambios=True (default)                      │
└───┬────────────────────┬───────────────────────────────┘
    │                    │
    │ Guarda snapshot    │ Obtiene snapshot anterior
    │                    │
    ▼                    ▼
┌──────────────────────────────────────────────────────┐
│                database.py                            │
│  - crear_tabla_portfolio_snapshots()                 │
│  - guardar_snapshot_portfolio()                      │
│  - obtener_ultimo_snapshot()                         │
│  - limpiar_snapshots_antiguos()                      │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
         ┌──────────────────────┐
         │ portfolio_snapshots  │
         │      (SQLite)        │
         └──────────────────────┘

    Si existe snapshot anterior:
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│              portfolio_diff.py                          │
│  - comparar_snapshots()                                │
│  - formatear_tiempo_transcurrido()                     │
└────────────────────────────────────────────────────────┘
                   │
                   ▼
        Añade sección "cambios_desde_ultima_consulta"
```

---

## 📊 Nuevas Funcionalidades

### Primera Llamada (Sin Snapshot Previo)
```bash
GET /portafolio?analisis=completo
```

**Respuesta:**
```json
{
  "portfolio": [...],
  "totales": {...},
  "analisis": {...}
  // ❌ No hay sección 'cambios_desde_ultima_consulta'
}
```

### Llamadas Subsiguientes (Con Snapshot Previo)
```bash
GET /portafolio?analisis=completo
```

**Respuesta:**
```json
{
  "portfolio": [...],
  "totales": {...},
  "analisis": {...},
  "cambios_desde_ultima_consulta": {
    "timestamp_anterior": 1734287650,
    "timestamp_actual": 1734290115,
    "tiempo_transcurrido": "41 minutos",
    "valor_total": {
      "anterior": 862.70,
      "actual": 875.42,
      "cambio_eur": 12.72,
      "cambio_porcentaje": 1.47
    },
    "por_cripto": [...],
    "nuevas_posiciones": [],
    "posiciones_cerradas": []
  }
}
```

---

## 📈 Estructura de Datos de Cambios

### Información de Tiempos
```json
{
  "timestamp_anterior": 1734287650,           // Unix timestamp del snapshot anterior
  "timestamp_actual": 1734290115,             // Unix timestamp actual
  "tiempo_transcurrido": "2 horas 15 minutos" // Formato legible y comprensible
}
```

### Cambios en Valor Total
```json
{
  "valor_total": {
    "anterior": 1000.00,      // Valor total anterior (€)
    "actual": 1050.00,        // Valor total actual (€)
    "cambio_eur": 50.00,      // Diferencia absoluta en €
    "cambio_porcentaje": 5.0  // Diferencia porcentual
  }
}
```

### Cambios por Criptomoneda
```json
{
  "por_cripto": [
    {
      "cripto": "BTC",
      "valor_anterior": 450.00,
      "valor_actual": 480.00,
      "cambio_valor_eur": 30.00,
      "cambio_valor_pct": 6.67,
      "precio_anterior": 76000.00,
      "precio_actual": 78000.00,
      "cambio_precio_eur": 2000.00,
      "cambio_precio_pct": 2.63,
      "cambio_rentabilidad_pct": 1.75,    // Cambio en rentabilidad
      "cambio_peso_pct": 1.5               // Cambio en peso del portfolio
    }
  ]
}
```

### Nuevas Posiciones y Cierres
```json
{
  "nuevas_posiciones": [
    {
      "cripto": "SOL",
      "valor_actual": 100.00,
      "precio_actual": 95.50,
      "peso_portfolio_pct": 9.5
    }
  ],
  "posiciones_cerradas": [
    {
      "cripto": "DOGE",
      "valor_anterior": 25.00,
      "precio_anterior": 0.08
    }
  ]
}
```

---

## 🛠️ Implementación Técnica

### Archivos Modificados

#### 1. `src/database.py`
**Funciones añadidas:**
- `crear_tabla_portfolio_snapshots()` - Crea la tabla si no existe
- `guardar_snapshot_portfolio(datos_portfolio, timestamp)` - Guarda un snapshot
- `obtener_ultimo_snapshot()` - Recupera el snapshot más reciente
- `limpiar_snapshots_antiguos(dias_a_mantener=30)` - Limpia snapshots antiguos

**Nueva tabla:**
```sql
CREATE TABLE portfolio_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    cripto TEXT NOT NULL,
    cantidad_actual REAL NOT NULL,
    precio_actual REAL NOT NULL,
    valor_actual REAL NOT NULL,
    coste_total REAL NOT NULL,
    rentabilidad_pct REAL NOT NULL,
    rentabilidad_abs REAL NOT NULL,
    peso_portfolio_pct REAL NOT NULL
);

CREATE INDEX idx_snapshots_timestamp
ON portfolio_snapshots(timestamp DESC);
```

### Archivos Creados

#### 2. `src/portfolio_diff.py`
**Nuevo módulo completo** que contiene:
- `comparar_snapshots(portfolio_actual, snapshot_anterior, timestamp_actual)` - Lógica principal de comparación
- `formatear_tiempo_transcurrido(timestamp_anterior, timestamp_actual)` - Formato legible del tiempo
- Detecta cambios en: valor total, valores individuales, precios, rentabilidades, pesos
- Identifica nuevas posiciones y posiciones cerradas

#### 3. `src/portfolio_analyzer.py` (Modificado)
**Función modificada:**
- `analizar_portfolio_completo(datos_portfolio, incluir_cambios=True)`
  - Nuevo parámetro `incluir_cambios` (por defecto `True`)
  - Crea tabla automáticamente si no existe
  - Obtiene snapshot anterior
  - Llama a `portfolio_diff.comparar_snapshots()` si hay snapshot previo
  - Guarda snapshot actual después de procesar

---

## 🧪 Testing y Verificación

### Test Manual con curl

**Primera llamada:**
```bash
curl -s "http://localhost:5000/portafolio?analisis=completo" | python3 -m json.tool > snapshot1.json
```

**Esperar unos segundos y segunda llamada:**
```bash
sleep 15
curl -s "http://localhost:5000/portafolio?analisis=completo" | python3 -m json.tool > snapshot2.json
```

**Ver solo la sección de cambios:**
```bash
curl -s "http://localhost:5000/portafolio?analisis=completo" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'cambios_desde_ultima_consulta' in data:
    cambios = data['cambios_desde_ultima_consulta']
    print(f\"Tiempo transcurrido: {cambios['tiempo_transcurrido']}\")
    print(f\"Cambio en valor total: {cambios['valor_total']['cambio_eur']}€ ({cambios['valor_total']['cambio_porcentaje']}%)\")
    print(f\"Número de cryptos con cambios: {len(cambios['por_cripto'])}\")
else:
    print('Primera consulta: no hay cambios previos')
"
```

### Verificar Tabla en SQLite

**Ver estructura de la tabla:**
```bash
sqlite3 data/kryptonite.db ".schema portfolio_snapshots"
```

**Ver últimos snapshots guardados:**
```bash
sqlite3 data/kryptonite.db "
SELECT datetime(timestamp, 'unixepoch', 'localtime') as fecha,
       COUNT(*) as num_cryptos
FROM portfolio_snapshots
GROUP BY timestamp
ORDER BY timestamp DESC
LIMIT 5;
"
```

**Contar total de snapshots únicos:**
```bash
sqlite3 data/kryptonite.db "
SELECT COUNT(DISTINCT timestamp) as total_snapshots
FROM portfolio_snapshots;
"
```

**Ver detalles de un snapshot específico:**
```bash
sqlite3 data/kryptonite.db "
SELECT cripto,
       valor_actual,
       precio_actual,
       rentabilidad_pct,
       peso_portfolio_pct
FROM portfolio_snapshots
WHERE timestamp = (SELECT MAX(timestamp) FROM portfolio_snapshots)
ORDER BY valor_actual DESC;
"
```

---

## ⚙️ Configuración y Mantenimiento

### Retrocompatibilidad
El sistema es completamente retrocompatible:
- `GET /portafolio` → Modo básico (sin análisis, sin snapshots)
- `GET /portafolio?analisis=basico` → Modo básico (sin snapshots)
- `GET /portafolio?analisis=completo` → Modo completo (CON snapshots y comparación)

### Limpieza de Snapshots Antiguos

Para evitar crecimiento ilimitado de la tabla, existe una función de limpieza:

```python
from database import limpiar_snapshots_antiguos

# Eliminar snapshots de más de 30 días (por defecto)
eliminados = limpiar_snapshots_antiguos()
print(f"Eliminados {eliminados} registros antiguos")

# O especificar días personalizados
eliminados = limpiar_snapshots_antiguos(dias_a_mantener=7)
```

**Recomendación:** Ejecutar esta función periódicamente mediante un cron job semanal o mensual.

**Ejemplo de cron job (semanal):**
```bash
# Añadir al crontab: crontab -e
0 2 * * 0 cd /ruta/a/kryptonite && python3 -c "from src.database import limpiar_snapshots_antiguos; limpiar_snapshots_antiguos(30)"
```

---

## 📝 Decisiones de Diseño

### 1. Snapshot Automático
**Decisión:** Guardar automáticamente en cada llamada a `analisis=completo`

✅ **Ventajas:**
- Sencillo de usar (no requiere llamada manual adicional)
- Siempre actualizado y sincronizado
- Transparente para el usuario

⚠️ **Consideraciones:**
- Genera un snapshot por cada llamada al endpoint
- Requiere limpieza periódica para evitar crecimiento indefinido

### 2. Tabla Separada
**Decisión:** Los snapshots se guardan en tabla `portfolio_snapshots` independiente

✅ **Ventajas:**
- No interfiere con datos existentes
- Fácil de limpiar/purgar sin afectar otros datos
- Índice optimizado para consultas rápidas por timestamp
- Permite futuras expansiones (ej: consultas históricas)

### 3. Formato de Tiempo Legible
**Decisión:** "2 horas 15 minutos" en lugar de "8115 segundos"

✅ **Ventajas:**
- Más amigable y comprensible para el usuario
- Se adapta al contexto (segundos, minutos, horas, días)
- Solo muestra componentes relevantes

**Ejemplos:**
- "15 segundos" (< 1 minuto)
- "5 minutos" (< 1 hora)
- "2 horas 30 minutos" (< 1 día)
- "1 día 3 horas" (>= 1 día)

### 4. Comparación Solo con Snapshot Anterior
**Decisión:** Comparar únicamente con el snapshot inmediatamente anterior

✅ **Ventajas:**
- Lógica simple y predecible
- Rendimiento óptimo (solo una consulta a BD)
- Información más relevante (cambio desde última consulta)

📌 **Nota:** Los snapshots antiguos permanecen en la BD y pueden usarse para análisis histórico mediante consultas SQL directas.

---

## 🎯 Casos de Uso

### 1. Monitoreo Diario
Ver cómo cambió el portfolio desde ayer a la misma hora.

**Ejemplo:** Consulta a las 09:00 cada día para ver cambio en 24h.

### 2. Análisis Intradiario
Comparar cambios cada hora durante el día de trading.

**Ejemplo:** Consultas a las 09:00, 12:00, 15:00, 18:00 para seguir evolución.

### 3. Detección de Eventos
Identificar cuándo se añadieron o quitaron posiciones.

**Ejemplo:** Ver qué cryptos nuevas aparecieron o cuáles se vendieron completamente.

### 4. Seguimiento de Tendencias
Ver si el portfolio mejora o empeora entre consultas.

**Ejemplo:** Detectar patrones de mejora continua o deterioro progresivo.

---

## ⚠️ Limitaciones Conocidas

### 1. Solo el Último Snapshot
- Cada llamada compara con el snapshot inmediatamente anterior
- Los snapshots antiguos permanecen en BD pero no se usan para comparación automática
- Para análisis histórico profundo, se requiere consulta SQL directa

### 2. Sin Historial de Comparaciones
- No se guarda un registro de comparaciones pasadas
- Cada comparación es "en tiempo real" y no se almacena
- Los cambios solo están disponibles en la respuesta JSON actual

### 3. Requiere Modo Completo
- Solo funciona con `analisis=completo`
- El modo básico (`analisis=basico` o sin parámetro) no genera snapshots
- No hay impacto en rendimiento para usuarios que no usan el modo completo

### 4. Primera Consulta Sin Cambios
- La primera llamada no muestra cambios (no hay snapshot previo)
- Es necesario hacer al menos dos llamadas para ver la sección de cambios

---

## 📊 Impacto en el Rendimiento

### Base de Datos
- **Escritura:** +1 INSERT por crypto por llamada (~10-20ms total)
- **Lectura:** +1 SELECT por llamada (~5-10ms)
- **Índice:** Optimizado para consultas rápidas por timestamp

### API Response
- **Tamaño adicional:** ~2-5 KB por respuesta (sección de cambios)
- **Tiempo de procesamiento:** +20-50ms adicionales
- **Impacto total:** Insignificante para uso normal

### Almacenamiento
- **Por snapshot:** ~200-500 bytes por crypto
- **Ejemplo:** Portfolio de 10 cryptos = ~5 KB por snapshot
- **Proyección:** 100 snapshots = ~500 KB (muy liviano)

**Recomendación:** Limpiar snapshots >30 días mensualmente es suficiente para la mayoría de casos de uso.

---

## ✅ Checklist de Implementación

- [x] Crear tabla `portfolio_snapshots` en la base de datos
- [x] Implementar función `crear_tabla_portfolio_snapshots()`
- [x] Implementar función `guardar_snapshot_portfolio()`
- [x] Implementar función `obtener_ultimo_snapshot()`
- [x] Implementar función `limpiar_snapshots_antiguos()`
- [x] Crear módulo `portfolio_diff.py` con lógica de comparación
- [x] Implementar `comparar_snapshots()`
- [x] Implementar `formatear_tiempo_transcurrido()`
- [x] Modificar `analizar_portfolio_completo()` para integrar snapshots
- [x] Añadir parámetro `incluir_cambios` con valor por defecto `True`
- [x] Probar endpoint con llamadas múltiples
- [x] Verificar primera llamada (sin cambios)
- [x] Verificar segunda llamada (con cambios)
- [x] Verificar retrocompatibilidad (modos básico y sin parámetro)
- [x] Probar detección de nuevas posiciones
- [x] Probar detección de posiciones cerradas
- [x] Verificar formato de tiempo legible
- [x] Documentar funcionalidad completa
- [x] Crear script de limpieza de snapshots antiguos
- [x] Probar limpieza de snapshots

---

## 🎉 Resumen

**Estado:** ✅ **COMPLETADO**

La Fase 1.3 añade detección automática de cambios en el portfolio, eliminando la necesidad de comparar manualmente entre llamadas sucesivas. El sistema es:

✅ **Automático:** Se activa solo en modo `analisis=completo`
✅ **Retrocompatible:** No afecta el funcionamiento existente
✅ **Eficiente:** Índices optimizados, bajo impacto en rendimiento
✅ **Informativo:** Muestra cambios en valor, precio, rentabilidad y peso
✅ **Mantenible:** Función de limpieza incluida para gestión de histórico

**Próximos pasos sugeridos:**
- Configurar cron job para limpieza automática de snapshots (recomendado: mensual)
- Considerar implementar historial de comparaciones extendido (opcional)
- Integrar visualización gráfica de cambios (podría retomarse Fase 1.2)
- Añadir alertas basadas en cambios significativos (futura funcionalidad)

---

**Desarrollado por:** Claude Code
**Fecha de implementación:** 2025-12-15
**Versión:** 1.0 - Fase 1.3 Completa
