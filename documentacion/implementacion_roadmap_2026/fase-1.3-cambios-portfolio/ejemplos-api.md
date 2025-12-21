# API Portfolio - Ejemplos de Uso (Fase 1.3)

## Endpoint: `/portafolio?analisis=completo`

Esta documentación muestra ejemplos específicos del uso de la **Fase 1.3** que añade detección automática de cambios desde la última consulta.

---

## 🎯 Detección de Cambios desde Última Consulta

### Primera Llamada (Sin Snapshot Previo)

**Request:**
```bash
GET http://localhost:5000/portafolio?analisis=completo
```

**Response:** (Primera vez - sin sección de cambios)
```json
{
  "portfolio": [
    {
      "simbolo": "BTC",
      "cantidad_actual": 0.00490600,
      "precio_medio_compra": 88080.02,
      "coste_total_inversion": 373.38,
      "precio_actual": 76456.91,
      "valor_actual_inversion": 375.09,
      "ganancia_perdida_abs": 1.71,
      "rentabilidad_porcentaje": 0.46,
      "peso_portfolio_pct": 43.47,
      "alertas": ["sobreexpuesto"]
    },
    {
      "simbolo": "ETH",
      "cantidad_actual": 0.04350400,
      "precio_medio_compra": 1791.23,
      "coste_total_inversion": 65.38,
      "precio_actual": 2638.84,
      "valor_actual_inversion": 114.81,
      "ganancia_perdida_abs": 49.43,
      "rentabilidad_porcentaje": 75.60,
      "peso_portfolio_pct": 13.31,
      "alertas": []
    }
  ],
  "totales": {
    "total_invertido": 1166.16,
    "valor_actual": 862.70,
    "rentabilidad_total_pct": -26.02,
    "rentabilidad_total_abs": -303.46
  },
  "analisis": {
    "alertas_globales": [
      "BTC representa el 43.5% del portfolio (recomendado: <40%)"
    ],
    "metricas": {
      "num_activos": 6,
      "activos_rentables": 2,
      "activos_perdidas": 4,
      "concentracion_top2_pct": 56.8,
      "diversificacion_score": "Media",
      "exposicion_riesgo": "Alta"
    }
  }
  // ❌ No hay 'cambios_desde_ultima_consulta' (primera consulta)
}
```

**Nota:** En la primera llamada NO aparece la sección `cambios_desde_ultima_consulta` porque no existe un snapshot anterior con el que comparar.

---

### Segunda Llamada (Con Snapshot Previo)

**Contexto:** Han pasado 12 segundos desde la primera llamada. Los precios han subido ligeramente.

**Request:**
```bash
GET http://localhost:5000/portafolio?analisis=completo
```

**Response:** (Con sección de cambios)
```json
{
  "portfolio": [
    {
      "simbolo": "BTC",
      "cantidad_actual": 0.00490600,
      "precio_medio_compra": 88080.02,
      "coste_total_inversion": 373.38,
      "precio_actual": 76498.66,
      "valor_actual_inversion": 375.28,
      "ganancia_perdida_abs": 1.90,
      "rentabilidad_porcentaje": 0.51,
      "peso_portfolio_pct": 43.48,
      "alertas": ["sobreexpuesto"]
    },
    {
      "simbolo": "ETH",
      "cantidad_actual": 0.04350400,
      "precio_medio_compra": 1791.23,
      "coste_total_inversion": 65.38,
      "precio_actual": 2639.45,
      "valor_actual_inversion": 114.84,
      "ganancia_perdida_abs": 49.46,
      "rentabilidad_porcentaje": 75.65,
      "peso_portfolio_pct": 13.31,
      "alertas": []
    }
  ],
  "totales": {
    "total_invertido": 1166.16,
    "valor_actual": 862.71,
    "rentabilidad_total_pct": -26.02,
    "rentabilidad_total_abs": -303.45
  },
  "analisis": {
    "alertas_globales": [
      "BTC representa el 43.5% del portfolio (recomendado: <40%)"
    ],
    "metricas": {
      "num_activos": 6,
      "activos_rentables": 2,
      "activos_perdidas": 4,
      "concentracion_top2_pct": 56.8,
      "diversificacion_score": "Media",
      "exposicion_riesgo": "Alta"
    }
  },

  // ✅ NUEVA SECCIÓN: Cambios desde la última consulta
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
        "precio_anterior": 76456.99,
        "precio_actual": 76498.66,
        "cambio_precio_eur": 41.67,
        "cambio_precio_pct": 0.05,
        "cambio_rentabilidad_pct": 0.05,
        "cambio_peso_pct": 0.01
      },
      {
        "cripto": "ETH",
        "valor_anterior": 114.81,
        "valor_actual": 114.84,
        "cambio_valor_eur": 0.03,
        "cambio_valor_pct": 0.03,
        "precio_anterior": 2638.84,
        "precio_actual": 2639.45,
        "cambio_precio_eur": 0.61,
        "cambio_precio_pct": 0.02,
        "cambio_rentabilidad_pct": 0.05,
        "cambio_peso_pct": 0.00
      }
    ],

    "nuevas_posiciones": [],
    "posiciones_cerradas": []
  }
}
```

---

## 📊 Ejemplos de Diferentes Escenarios

### Escenario 1: Cambios Significativos en 1 Hora

**Contexto:** Ha pasado 1 hora. Bitcoin subió 3%, Ethereum bajó 2%.

```json
{
  "cambios_desde_ultima_consulta": {
    "timestamp_anterior": 1734287662,
    "timestamp_actual": 1734291262,
    "tiempo_transcurrido": "1 hora",

    "valor_total": {
      "anterior": 862.71,
      "actual": 871.15,
      "cambio_eur": 8.44,
      "cambio_porcentaje": 0.98
    },

    "por_cripto": [
      {
        "cripto": "BTC",
        "cambio_valor_eur": 11.29,
        "cambio_valor_pct": 3.01,
        "cambio_precio_eur": 2294.96,
        "cambio_precio_pct": 3.00,
        "cambio_rentabilidad_pct": 3.03
      },
      {
        "cripto": "ETH",
        "cambio_valor_eur": -2.30,
        "cambio_valor_pct": -2.00,
        "cambio_precio_eur": -52.79,
        "cambio_precio_pct": -2.00,
        "cambio_rentabilidad_pct": -3.51
      }
    ],

    "nuevas_posiciones": [],
    "posiciones_cerradas": []
  }
}
```

---

### Escenario 2: Nueva Posición Añadida

**Contexto:** Has comprado SOL por primera vez.

```json
{
  "cambios_desde_ultima_consulta": {
    "tiempo_transcurrido": "3 horas 25 minutos",

    "valor_total": {
      "anterior": 862.71,
      "actual": 962.71,
      "cambio_eur": 100.00,
      "cambio_porcentaje": 11.59
    },

    "por_cripto": [
      {
        "cripto": "BTC",
        "cambio_valor_eur": 1.50,
        "cambio_valor_pct": 0.40
      },
      {
        "cripto": "ETH",
        "cambio_valor_eur": 0.80,
        "cambio_valor_pct": 0.70
      },
      {
        "cripto": "SOL",
        // SOL no tiene campos de cambio porque es nueva
        // Solo aparece en nuevas_posiciones
      }
    ],

    // ✅ Nueva cripto detectada
    "nuevas_posiciones": [
      {
        "cripto": "SOL",
        "valor_actual": 100.00,
        "precio_actual": 95.50,
        "peso_portfolio_pct": 10.39
      }
    ],

    "posiciones_cerradas": []
  }
}
```

---

### Escenario 3: Posición Cerrada (Vendida Completamente)

**Contexto:** Has vendido toda tu posición de DOGE.

```json
{
  "cambios_desde_ultima_consulta": {
    "tiempo_transcurrido": "2 días 5 horas",

    "valor_total": {
      "anterior": 862.71,
      "actual": 837.71,
      "cambio_eur": -25.00,
      "cambio_porcentaje": -2.90
    },

    "por_cripto": [
      {
        "cripto": "BTC",
        "cambio_valor_eur": 5.20,
        "cambio_valor_pct": 1.39
      }
      // DOGE ya NO aparece aquí porque fue vendido
    ],

    "nuevas_posiciones": [],

    // ✅ Posición cerrada detectada
    "posiciones_cerradas": [
      {
        "cripto": "DOGE",
        "valor_anterior": 25.00,
        "precio_anterior": 0.080500
      }
    ]
  }
}
```

---

### Escenario 4: Cambios Mixtos (Compra y Venta)

**Contexto:** Vendiste SHIB y compraste MATIC.

```json
{
  "cambios_desde_ultima_consulta": {
    "tiempo_transcurrido": "15 horas 30 minutos",

    "valor_total": {
      "anterior": 862.71,
      "actual": 865.45,
      "cambio_eur": 2.74,
      "cambio_porcentaje": 0.32
    },

    "por_cripto": [
      {
        "cripto": "BTC",
        "cambio_valor_eur": 3.15,
        "cambio_valor_pct": 0.84
      },
      {
        "cripto": "ETH",
        "cambio_valor_eur": 1.20,
        "cambio_valor_pct": 1.05
      }
      // SHIB desapareció, MATIC apareció
    ],

    "nuevas_posiciones": [
      {
        "cripto": "MATIC",
        "valor_actual": 85.00,
        "precio_actual": 0.520000,
        "peso_portfolio_pct": 9.82
      }
    ],

    "posiciones_cerradas": [
      {
        "cripto": "SHIB",
        "valor_anterior": 86.64,
        "precio_anterior": 0.000007
      }
    ]
  }
}
```

---

## 🕐 Formatos de Tiempo Transcurrido

El sistema muestra el tiempo en formato legible:

| Tiempo real | Formato mostrado |
|-------------|------------------|
| 5 segundos | "5 segundos" |
| 45 segundos | "45 segundos" |
| 90 segundos | "1 minuto" |
| 5 minutos | "5 minutos" |
| 65 minutos | "1 hora 5 minutos" |
| 2 horas 30 min | "2 horas 30 minutos" |
| 1 día 2 horas | "1 día 2 horas" |
| 3 días 0 horas | "3 días" |
| 7 días 12 horas | "7 días 12 horas" |

**Lógica:**
- Solo muestra componentes relevantes (no muestra "0 minutos" si hay días)
- Se adapta automáticamente al tamaño del intervalo
- Siempre en formato singular/plural correcto

---

## 💻 Uso desde Node-RED

### Procesamiento de Cambios en JavaScript

```javascript
// Recibir respuesta del API
var respuesta = JSON.parse(msg.payload);

// Verificar si hay cambios
if (respuesta.cambios_desde_ultima_consulta) {
    let cambios = respuesta.cambios_desde_ultima_consulta;

    // Construir mensaje con información de cambios
    let content = "📊 **Cambios en tu portfolio**\n\n";
    content += `⏱️ Tiempo transcurrido: ${cambios.tiempo_transcurrido}\n\n`;

    // Cambio en valor total
    let valorTotal = cambios.valor_total;
    let emojiValor = valorTotal.cambio_eur >= 0 ? "📈" : "📉";
    content += `${emojiValor} **Valor total:**\n`;
    content += `   Antes: ${valorTotal.anterior.toFixed(2)} €\n`;
    content += `   Ahora: ${valorTotal.actual.toFixed(2)} €\n`;
    content += `   Cambio: ${valorTotal.cambio_eur > 0 ? '+' : ''}${valorTotal.cambio_eur.toFixed(2)} € `;
    content += `(${valorTotal.cambio_porcentaje > 0 ? '+' : ''}${valorTotal.cambio_porcentaje.toFixed(2)}%)\n\n`;

    // Cambios por crypto (solo las más significativas)
    let cambiosSignificativos = cambios.por_cripto.filter(c =>
        Math.abs(c.cambio_valor_pct) >= 1.0  // Cambios >= 1%
    );

    if (cambiosSignificativos.length > 0) {
        content += "🔄 **Cambios significativos (>1%):**\n";
        cambiosSignificativos.forEach(c => {
            let emoji = c.cambio_valor_eur >= 0 ? "✅" : "⚠️";
            content += `   ${emoji} **${c.cripto}**: `;
            content += `${c.cambio_valor_eur > 0 ? '+' : ''}${c.cambio_valor_eur.toFixed(2)} € `;
            content += `(${c.cambio_valor_pct > 0 ? '+' : ''}${c.cambio_valor_pct.toFixed(2)}%)\n`;
        });
        content += "\n";
    }

    // Nuevas posiciones
    if (cambios.nuevas_posiciones.length > 0) {
        content += "🆕 **Nuevas posiciones:**\n";
        cambios.nuevas_posiciones.forEach(p => {
            content += `   ➕ ${p.cripto}: ${p.valor_actual.toFixed(2)} € (${p.peso_portfolio_pct.toFixed(1)}%)\n`;
        });
        content += "\n";
    }

    // Posiciones cerradas
    if (cambios.posiciones_cerradas.length > 0) {
        content += "❌ **Posiciones cerradas:**\n";
        cambios.posiciones_cerradas.forEach(p => {
            content += `   🔻 ${p.cripto}: ${p.valor_anterior.toFixed(2)} € (vendido)\n`;
        });
        content += "\n";
    }

    // Si no hay cambios significativos
    if (cambiosSignificativos.length === 0 &&
        cambios.nuevas_posiciones.length === 0 &&
        cambios.posiciones_cerradas.length === 0 &&
        Math.abs(valorTotal.cambio_porcentaje) < 0.1) {
        content += "ℹ️ No hay cambios significativos desde la última consulta.\n";
    }

    msg.payload = {
        "content": content,
        "type": "message",
        "chatId": 458079309
    };

} else {
    // Primera consulta: no hay cambios previos
    msg.payload = {
        "content": "ℹ️ Primera consulta registrada. Los cambios se mostrarán en la próxima consulta.",
        "type": "message",
        "chatId": 458079309
    };
}

return msg;
```

---

## 🧪 Testing Manual

### Test 1: Verificar Primera Consulta

```bash
# Primera llamada
curl -s "http://localhost:5000/portafolio?analisis=completo" | python3 -m json.tool > primera.json

# Verificar que NO tiene cambios
cat primera.json | grep "cambios_desde_ultima_consulta"
# Output: (vacío - no encontrado)
```

### Test 2: Verificar Segunda Consulta

```bash
# Segunda llamada (después de unos segundos)
sleep 10
curl -s "http://localhost:5000/portafolio?analisis=completo" | python3 -m json.tool > segunda.json

# Verificar que SÍ tiene cambios
cat segunda.json | grep "cambios_desde_ultima_consulta"
# Output: "cambios_desde_ultima_consulta": {
```

### Test 3: Ver Solo Cambios

```bash
curl -s "http://localhost:5000/portafolio?analisis=completo" | python3 -c "
import sys, json

data = json.load(sys.stdin)

if 'cambios_desde_ultima_consulta' in data:
    cambios = data['cambios_desde_ultima_consulta']

    print('=' * 50)
    print('RESUMEN DE CAMBIOS')
    print('=' * 50)
    print(f'Tiempo transcurrido: {cambios[\"tiempo_transcurrido\"]}')
    print()

    vt = cambios['valor_total']
    print(f'Valor anterior: {vt[\"anterior\"]} €')
    print(f'Valor actual:   {vt[\"actual\"]} €')
    print(f'Cambio:         {vt[\"cambio_eur\"]:+.2f} € ({vt[\"cambio_porcentaje\"]:+.2f}%)')
    print()

    if cambios['nuevas_posiciones']:
        print('Nuevas posiciones:')
        for p in cambios['nuevas_posiciones']:
            print(f'  + {p[\"cripto\"]}: {p[\"valor_actual\"]} €')
        print()

    if cambios['posiciones_cerradas']:
        print('Posiciones cerradas:')
        for p in cambios['posiciones_cerradas']:
            print(f'  - {p[\"cripto\"]}: {p[\"valor_anterior\"]} € (vendido)')
        print()

    print(f'Cambios en {len(cambios[\"por_cripto\"])} cryptos')

else:
    print('Primera consulta: no hay cambios previos')
"
```

### Test 4: Comparar Dos Snapshots Guardados

```bash
# Consulta 1
curl -s "http://localhost:5000/portafolio?analisis=completo" > snap1.json
echo "Snapshot 1 guardado"

# Esperar
sleep 60

# Consulta 2
curl -s "http://localhost:5000/portafolio?analisis=completo" > snap2.json
echo "Snapshot 2 guardado"

# Comparar manualmente
diff <(cat snap1.json | jq '.totales.valor_actual') <(cat snap2.json | jq '.totales.valor_actual')
```

---

## 🔍 Consultas SQL Útiles

### Ver Todos los Snapshots Guardados

```sql
SELECT
    datetime(timestamp, 'unixepoch', 'localtime') as fecha,
    cripto,
    valor_actual,
    precio_actual,
    rentabilidad_pct,
    peso_portfolio_pct
FROM portfolio_snapshots
ORDER BY timestamp DESC, valor_actual DESC
LIMIT 20;
```

### Ver Evolución de una Crypto

```sql
SELECT
    datetime(timestamp, 'unixepoch', 'localtime') as fecha,
    precio_actual,
    valor_actual,
    rentabilidad_pct
FROM portfolio_snapshots
WHERE cripto = 'BTC'
ORDER BY timestamp DESC
LIMIT 10;
```

### Ver Cuántos Snapshots por Día

```sql
SELECT
    date(timestamp, 'unixepoch', 'localtime') as dia,
    COUNT(DISTINCT timestamp) as num_consultas,
    COUNT(*) as total_registros
FROM portfolio_snapshots
GROUP BY dia
ORDER BY dia DESC;
```

---

## 📋 Compatibilidad con Modos Anteriores

### Modo Básico (Sin Cambios)

```bash
GET /portafolio
# O
GET /portafolio?analisis=basico
```

**Comportamiento:** NO guarda snapshots, NO muestra cambios. Funciona exactamente como antes.

### Modo Completo (Con Cambios)

```bash
GET /portafolio?analisis=completo
```

**Comportamiento:** Guarda snapshot, compara con anterior, muestra cambios si existe snapshot previo.

---

## ⚙️ Configuración Avanzada

### Deshabilitar Detección de Cambios

Si por alguna razón quieres el análisis completo PERO SIN snapshots:

**No está implementado directamente**, pero puedes:
1. Llamar al endpoint con `analisis=completo`
2. Ignorar la sección `cambios_desde_ultima_consulta` en tu código

**O modificar el código:**
```python
# En portfolio_analyzer.py
resultado = analizar_portfolio_completo(datos, incluir_cambios=False)
```

### Limpiar Snapshots Manualmente

```bash
python3 -c "
from src.database import limpiar_snapshots_antiguos
eliminados = limpiar_snapshots_antiguos(dias_a_mantener=7)
print(f'Eliminados {eliminados} registros')
"
```

---

**Última actualización:** 2025-12-15
**Versión:** Fase 1.3 - Detección de Cambios desde Última Consulta
