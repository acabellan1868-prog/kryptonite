# Fase 1.3 - Detección de Cambios desde Última Consulta

> Implementación completada el 2025-12-15

## 📋 Descripción

Sistema que detecta y muestra automáticamente los cambios en el portfolio desde la última vez que se consultó el endpoint `/portafolio?analisis=completo`.

**Valor añadido:** Evita tener que comparar manualmente entre llamadas consecutivas al endpoint, mostrando automáticamente:
- Cambios en el valor total del portfolio
- Cambios por criptomoneda (precio, valor, rentabilidad)
- Tiempo transcurrido desde la última consulta
- Nuevas posiciones añadidas o posiciones cerradas

---

## 🎯 Funcionalidad Implementada

### Snapshot Automático
Cada vez que llamas a `/portafolio?analisis=completo`, el sistema:
1. Guarda un "snapshot" del estado actual del portfolio
2. Compara con el snapshot anterior (si existe)
3. Calcula y muestra los cambios

### Primera Llamada
```json
{
  "portfolio": [...],
  "totales": {...},
  "analisis": {...}
  // ❌ No hay 'cambios_desde_ultima_consulta' (primera vez)
}
```

### Llamadas Subsiguientes
```json
{
  "portfolio": [...],
  "totales": {...},
  "analisis": {...},
  "cambios_desde_ultima_consulta": {
    "timestamp_anterior": 1734287650,
    "timestamp_actual": 1734287662,
    "tiempo_transcurrido": "12 segundos",
    "valor_total": {
      "anterior": 862.70,
      "actual": 862.71,
      "cambio_eur": 0.01,
      "cambio_porcentaje": 0.00
    },
    "por_cripto": [
      {
        "cripto": "BTC",
        "valor_anterior": 375.09,
        "valor_actual": 375.28,
        "cambio_valor_eur": 0.19,
        "cambio_valor_pct": 0.05,
        "precio_anterior": 76458.99,
        "precio_actual": 76498.66,
        "cambio_precio_eur": 39.67,
        "cambio_precio_pct": 0.05,
        "cambio_rentabilidad_pct": 0.05,
        "cambio_peso_pct": 0.01
      },
      ...
    ],
    "nuevas_posiciones": [],
    "posiciones_cerradas": []
  }
}
```

---

## 🛠️ Implementación Técnica

### Archivos Modificados/Creados

#### 1. [database.py](../../../src/database.py) - Funciones de BD
**Nuevas funciones:**
- `crear_tabla_portfolio_snapshots()` - Crea la tabla si no existe
- `guardar_snapshot_portfolio(datos_portfolio, timestamp)` - Guarda un snapshot
- `obtener_ultimo_snapshot()` - Obtiene el snapshot más reciente
- `limpiar_snapshots_antiguos(dias_a_mantener)` - Limpia snapshots viejos

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

#### 2. [portfolio_diff.py](../../../src/portfolio_diff.py) - Módulo de Comparación
**Nuevo módulo** que contiene:
- `comparar_snapshots(portfolio_actual, snapshot_anterior, timestamp_actual)` - Lógica de comparación
- `formatear_tiempo_transcurrido(timestamp_anterior, timestamp_actual)` - Formateo legible del tiempo

#### 3. [portfolio_analyzer.py](../../../src/portfolio_analyzer.py) - Integración
**Función modificada:**
- `analizar_portfolio_completo(datos_portfolio, incluir_cambios=True)`
  - Nuevo parámetro `incluir_cambios` (por defecto `True`)
  - Crea tabla automáticamente en primera ejecución
  - Obtiene snapshot anterior
  - Compara si existe snapshot previo
  - Guarda snapshot actual

---

## 🚀 Uso

### Endpoint
```bash
GET /portafolio?analisis=completo
```

### Ejemplo de Uso

**Primera llamada (09:30:00):**
```bash
curl "http://localhost:5000/portafolio?analisis=completo"
```
Respuesta: Portfolio actual sin sección de cambios.

**Segunda llamada (11:45:15):**
```bash
curl "http://localhost:5000/portafolio?analisis=completo"
```
Respuesta: Portfolio actual + sección `cambios_desde_ultima_consulta` mostrando diferencias en 2 horas 15 minutos.

---

## 📊 Estructura de Datos de Cambios

```json
{
  "cambios_desde_ultima_consulta": {
    "timestamp_anterior": 1734287650,        // Unix timestamp del snapshot anterior
    "timestamp_actual": 1734290115,          // Unix timestamp actual
    "tiempo_transcurrido": "2 horas 15 minutos",  // Formato legible

    "valor_total": {
      "anterior": 1000.00,                   // Valor total anterior (€)
      "actual": 1050.00,                     // Valor total actual (€)
      "cambio_eur": 50.00,                   // Diferencia en €
      "cambio_porcentaje": 5.0               // Diferencia en %
    },

    "por_cripto": [                          // Array con cambios por cada cripto
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
        "cambio_rentabilidad_pct": 1.75,     // Cambio en la rentabilidad
        "cambio_peso_pct": 1.5               // Cambio en el peso del portfolio
      }
    ],

    "nuevas_posiciones": [                   // Cryptos que NO estaban en el snapshot anterior
      {
        "cripto": "SOL",
        "valor_actual": 100.00,
        "precio_actual": 95.50,
        "peso_portfolio_pct": 9.5
      }
    ],

    "posiciones_cerradas": [                 // Cryptos que ya NO están en el portfolio
      {
        "cripto": "DOGE",
        "valor_anterior": 25.00,
        "precio_anterior": 0.08
      }
    ]
  }
}
```

---

## ⚙️ Configuración

### Retrocompatibilidad
El endpoint `/portafolio` sigue funcionando exactamente igual:
- `GET /portafolio` → Modo básico (sin análisis, sin snapshots)
- `GET /portafolio?analisis=basico` → Modo básico (sin snapshots)
- `GET /portafolio?analisis=completo` → Modo completo (CON snapshots y comparación)

### Limpieza de Snapshots Antiguos
Para evitar que la tabla crezca indefinidamente, se puede ejecutar:

```python
from database import limpiar_snapshots_antiguos

# Eliminar snapshots de más de 30 días (por defecto)
eliminados = limpiar_snapshots_antiguos()

# O especificar días personalizados
eliminados = limpiar_snapshots_antiguos(dias_a_mantener=7)
```

**Recomendación:** Ejecutar esta función periódicamente (ej: mediante un cron job semanal).

---

## 🧪 Testing

### Test Manual con curl

```bash
# Primera llamada
curl -s "http://localhost:5000/portafolio?analisis=completo" | python3 -m json.tool > snapshot1.json

# Esperar unos segundos
sleep 10

# Segunda llamada
curl -s "http://localhost:5000/portafolio?analisis=completo" | python3 -m json.tool > snapshot2.json

# Ver solo los cambios
curl -s "http://localhost:5000/portafolio?analisis=completo" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'cambios_desde_ultima_consulta' in data:
    cambios = data['cambios_desde_ultima_consulta']
    print(f\"Tiempo: {cambios['tiempo_transcurrido']}\")
    print(f\"Cambio total: {cambios['valor_total']['cambio_eur']}€\")
"
```

### Verificar Tabla en SQLite

```bash
# Ver estructura de la tabla
sqlite3 data/kryptonite.db ".schema portfolio_snapshots"

# Ver últimos snapshots
sqlite3 data/kryptonite.db "
SELECT datetime(timestamp, 'unixepoch') as fecha,
       COUNT(*) as num_cryptos
FROM portfolio_snapshots
GROUP BY timestamp
ORDER BY timestamp DESC
LIMIT 5;
"

# Contar total de snapshots
sqlite3 data/kryptonite.db "
SELECT COUNT(DISTINCT timestamp) as total_snapshots
FROM portfolio_snapshots;
"
```

---

## 📝 Notas de Implementación

### Decisiones de Diseño

1. **Snapshot automático:** Se guarda automáticamente en cada llamada a `analisis=completo`
   - ✅ Sencillo de usar (no requiere llamada manual)
   - ✅ Siempre actualizado
   - ⚠️ Genera un snapshot por cada llamada (usar limpieza periódica)

2. **Tabla separada:** Los snapshots se guardan en tabla `portfolio_snapshots`
   - ✅ No interfiere con datos existentes
   - ✅ Fácil de limpiar/purgar
   - ✅ Índice optimizado para consultas rápidas

3. **Formato de tiempo legible:** "2 horas 15 minutos" en lugar de segundos
   - ✅ Más amigable para el usuario
   - ✅ Muestra solo componentes relevantes (no muestra minutos si hay días)

### Casos de Uso

1. **Monitoreo diario:** Ver cómo cambió el portfolio desde ayer
2. **Análisis intradiario:** Comparar cambios cada hora durante el día de trading
3. **Detección de eventos:** Identificar cuándo se añadieron/quitaron posiciones
4. **Seguimiento de tendencias:** Ver si el portfolio mejora o empeora entre consultas

### Limitaciones Conocidas

1. **Solo guarda el último snapshot:** Cada llamada sobrescribe (en términos de "último")
   - Los snapshots antiguos siguen en la BD pero no se usan para comparación
   - Solo se compara con el inmediatamente anterior

2. **Sin historial de comparaciones:** No se guarda un registro de comparaciones pasadas
   - Cada comparación es "en tiempo real"
   - Para análisis histórico habría que consultar directamente la tabla

3. **Requiere análisis completo:** Solo funciona con `analisis=completo`
   - El modo básico no genera snapshots

---

## ✅ Checklist de Implementación

- [x] Crear tabla `portfolio_snapshots` en la base de datos
- [x] Implementar función `guardar_snapshot_portfolio()`
- [x] Implementar función `obtener_ultimo_snapshot()`
- [x] Implementar módulo `portfolio_diff.py` con lógica de comparación
- [x] Modificar `analizar_portfolio_completo()` para integrar snapshots
- [x] Probar endpoint con llamadas múltiples
- [x] Verificar retrocompatibilidad (modos básico y sin parámetro)
- [x] Documentar funcionalidad
- [x] Crear función de limpieza de snapshots antiguos

---

## 🎉 Resumen

**Estado:** ✅ **COMPLETADO**

La Fase 1.3 añade detección automática de cambios en el portfolio, eliminando la necesidad de comparar manualmente entre llamadas sucesivas. El sistema es:
- **Automático:** Se activa solo en modo `analisis=completo`
- **Retrocompatible:** No afecta el funcionamiento existente
- **Eficiente:** Índices optimizados, limpieza automática disponible
- **Informativo:** Muestra cambios en valor, precio, rentabilidad y peso

**Próximos pasos sugeridos:**
- Añadir limpieza automática de snapshots en un cron job
- Considerar implementar historial de comparaciones (opcional)
- Integrar visualización gráfica de cambios (Fase 1.2 retomada)