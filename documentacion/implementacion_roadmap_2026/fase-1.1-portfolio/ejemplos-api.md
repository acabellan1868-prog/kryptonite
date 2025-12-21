# API Portfolio - Ejemplos de Uso

## Endpoint: `/portafolio`

### Modo Básico (Retrocompatible)

**Request:**
```
GET http://localhost:5000/portafolio
```

O explícitamente:
```
GET http://localhost:5000/portafolio?analisis=basico
```

**Response:** (Igual que antes, compatible con Node-RED actual)
```json
[
  {
    "simbolo": "BTC",
    "cantidad_actual": 0.00423910,
    "precio_medio_compra": 88080.02,
    "coste_total_inversion": 373.38,
    "precio_actual": 76456.91,
    "valor_actual_inversion": 324.11,
    "ganancia_perdida_abs": -49.27,
    "rentabilidad_porcentaje": -13.20
  },
  {
    "simbolo": "ETH",
    "cantidad_actual": 0.03649996,
    "precio_medio_compra": 1791.23,
    "coste_total_inversion": 65.38,
    "precio_actual": 2638.84,
    "valor_actual_inversion": 96.32,
    "ganancia_perdida_abs": 30.94,
    "rentabilidad_porcentaje": 47.32
  }
]
```

---

### Modo Completo (Análisis Enriquecido - Fase 1.1)

**Request:**
```
GET http://localhost:5000/portafolio?analisis=completo
```

**Response:** (Estructura enriquecida)
```json
{
  "portfolio": [
    {
      "simbolo": "BTC",
      "cantidad_actual": 0.00423910,
      "precio_medio_compra": 88080.02,
      "coste_total_inversion": 373.38,
      "precio_actual": 76456.91,
      "valor_actual_inversion": 324.11,
      "ganancia_perdida_abs": -49.27,
      "rentabilidad_porcentaje": -13.20,

      // ⬇️ CAMPOS NUEVOS
      "peso_portfolio_pct": 42.6,
      "alertas": ["sobreexpuesto"]
    },
    {
      "simbolo": "ETH",
      "cantidad_actual": 0.03649996,
      "precio_medio_compra": 1791.23,
      "coste_total_inversion": 65.38,
      "precio_actual": 2638.84,
      "valor_actual_inversion": 96.32,
      "ganancia_perdida_abs": 30.94,
      "rentabilidad_porcentaje": 47.32,

      "peso_portfolio_pct": 12.7,
      "alertas": []
    },
    {
      "simbolo": "ADA",
      "cantidad_actual": 185.340000,
      "precio_medio_compra": 0.754937,
      "coste_total_inversion": 139.92,
      "precio_actual": 0.343600,
      "valor_actual_inversion": 63.68,
      "ganancia_perdida_abs": -76.24,
      "rentabilidad_porcentaje": -54.49,

      "peso_portfolio_pct": 8.4,
      "alertas": ["perdida_severa"]
    },
    {
      "simbolo": "SHIB",
      "cantidad_actual": 12359786.991500,
      "precio_medio_compra": 0.000021,
      "coste_total_inversion": 260.07,
      "precio_actual": 0.000007,
      "valor_actual_inversion": 86.64,
      "ganancia_perdida_abs": -173.43,
      "rentabilidad_porcentaje": -66.69,

      "peso_portfolio_pct": 11.4,
      "alertas": ["perdida_severa"]
    }
  ],

  // ⬇️ BLOQUE NUEVO: TOTALES CONSOLIDADOS
  "totales": {
    "total_invertido": 1166.16,
    "valor_actual": 760.73,
    "rentabilidad_total_pct": -34.77,
    "rentabilidad_total_abs": -405.43
  },

  // ⬇️ BLOQUE NUEVO: ANÁLISIS AVANZADO
  "analisis": {
    "alertas_globales": [
      "BTC representa el 42.6% del portfolio (recomendado: <40%)",
      "5 de 6 activos están en pérdidas",
      "Pérdidas severas en: SHIB (-67%), DOT (-59%), ADA (-54%)"
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

## Alertas Individuales (campo `alertas`)

Cada cripto puede tener las siguientes alertas:

| Alerta | Descripción |
|--------|-------------|
| `"sobreexpuesto"` | La cripto representa más del umbral configurado (default: 40%) del portfolio total |
| `"perdida_severa"` | La rentabilidad es inferior al umbral configurado (default: -50%) |

---

## Alertas Globales

El sistema detecta automáticamente:

1. **Sobreexposición individual**: Cuando una cripto supera el umbral
2. **Mayoría en pérdidas**: Cuando más de la mitad de los activos tienen rentabilidad negativa
3. **Pérdidas severas**: Lista las top 3 criptos con peores rentabilidades (<-50%)

---

## Métricas de Análisis

### `diversificacion_score`
- **"Alta"**: ≥8 activos + top 2 < 50%
- **"Media"**: ≥5 activos + top 2 < 60%
- **"Baja"**: Resto de casos

### `exposicion_riesgo`
- **"Alta"**: ≥50% de los activos con pérdidas severas (<-50%)
- **"Media"**: 25-50% de activos con pérdidas severas
- **"Baja"**: <25% de activos con pérdidas severas

### `concentracion_top2_pct`
Suma del % de las 2 criptos con mayor peso en el portfolio.

---

## Configuración de Umbrales

Los umbrales se configuran en `parametros.env`:

```bash
# Porcentaje máximo recomendado que una sola cripto debería representar
UMBRAL_SOBREEXPOSICION=40

# Porcentaje de pérdida para considerar "pérdida severa"
UMBRAL_PERDIDA_SEVERA=-50

# Porcentaje acumulado de las top 2 cryptos para alta concentración
UMBRAL_CONCENTRACION_ALTA=60
```

Puedes modificar estos valores sin tocar código y reiniciar la API.

---

## Uso desde Node-RED

### Opción 1: Mantener comportamiento actual
No cambies nada en Node-RED. El endpoint sin parámetros devuelve el formato original.

### Opción 2: Usar análisis completo
Cambia la URL en Node-RED de:
```
http://localhost:5000/portafolio
```

A:
```
http://localhost:5000/portafolio?analisis=completo
```

Y adapta el código JavaScript para procesar la nueva estructura:
- Accede a `payload.portfolio` en lugar de `payload` directamente
- Usa `payload.totales` para los totales (ya calculados)
- Usa `payload.analisis.alertas_globales` para mostrar alertas
- Usa `payload.analisis.metricas` para métricas adicionales

---

## Ejemplo de Procesamiento en Node-RED (Modo Completo)

```javascript
// Recibir respuesta del API
var respuesta = JSON.parse(msg.payload);

// Verificar errores
if (respuesta.error) {
    msg.payload = {
        "content": "⚠️ Error: " + respuesta.error,
        "type": "message",
        "chatId": 458079309
    };
    return msg;
}

// Función helper
function formatValue(value) {
    return value >= 1 ? value.toFixed(2) : value.toFixed(6);
}

// Construir mensaje básico con cada cripto
let content = "📊 **Estado de tus inversiones**\n\n";
content += "*******************************\n";

respuesta.portfolio.forEach(crypto => {
    content += `💰 **${crypto.simbolo}**\n`;
    content += `   * Precio actual:\t\t${formatValue(crypto.precio_actual)} €\n`;
    content += `   * Precio medio compra:\t${formatValue(crypto.precio_medio_compra)} €\n`;

    let rentabilidadEmoji = crypto.ganancia_perdida_abs >= 0 ? "✅" : "🚨";
    content += `   * ${rentabilidadEmoji} Rentabilidad:\t\t ${crypto.rentabilidad_porcentaje.toFixed(2)}% (${crypto.ganancia_perdida_abs.toFixed(2)} €)\n`;
    content += `   * Total invertido:\t\t${formatValue(crypto.coste_total_inversion)} €\n`;
    content += `   * Valor actual inversión:\t${formatValue(crypto.valor_actual_inversion)} €\n`;

    // ⬇️ NUEVO: Mostrar peso en portfolio
    content += `   * 📊 Peso en portfolio:\t${crypto.peso_portfolio_pct}%`;

    // ⬇️ NUEVO: Mostrar alertas individuales
    if (crypto.alertas && crypto.alertas.length > 0) {
        if (crypto.alertas.includes('sobreexpuesto')) {
            content += " ⚠️ Sobreexpuesto";
        }
        if (crypto.alertas.includes('perdida_severa')) {
            content += " 🚨 Pérdida severa";
        }
    }
    content += "\n\n";
});

// Totales (ya vienen calculados)
let totales = respuesta.totales;
let rentabilidadEmoji = totales.rentabilidad_total_abs >= 0 ? "✅" : "🚨";

content += "📌 **Totales de la cartera:**\n";
content += "**************************\n";
content += `   * Total invertido:\t\t${formatValue(totales.total_invertido)} €\n`;
content += `   * Valor actual:\t\t${formatValue(totales.valor_actual)} €\n`;
content += `   * ${rentabilidadEmoji} Rentabilidad:\t\t${totales.rentabilidad_total_pct.toFixed(2)}% (${totales.rentabilidad_total_abs.toFixed(2)} €)\n`;

// ⬇️ NUEVO: Mostrar alertas globales
if (respuesta.analisis.alertas_globales && respuesta.analisis.alertas_globales.length > 0) {
    content += "\n⚠️ **Alertas:**\n";
    respuesta.analisis.alertas_globales.forEach(alerta => {
        content += `   * ${alerta}\n`;
    });
}

// ⬇️ NUEVO: Mostrar métricas
let metricas = respuesta.analisis.metricas;
content += "\n💡 **Análisis:**\n";
content += `   * Diversificación: ${metricas.diversificacion_score} (${metricas.num_activos} activos)\n`;
content += `   * Activos rentables: ${metricas.activos_rentables}/${metricas.num_activos}\n`;
content += `   * Exposición a riesgo: ${metricas.exposicion_riesgo}\n`;
content += `   * Concentración top 2: ${metricas.concentracion_top2_pct}%\n`;

// Enviar mensaje
msg.payload = {
    "content": content,
    "type": "message",
    "chatId": 458079309
};

return msg;
```

---

## Testing Manual

### Usando curl:

```bash
# Modo básico (retrocompatible)
curl http://localhost:5000/portafolio

# Modo completo (con análisis)
curl http://localhost:5000/portafolio?analisis=completo
```

### Usando el navegador:
```
http://localhost:5000/portafolio?analisis=completo
```

---

**Última actualización:** 2025-12-14
**Versión:** Fase 1.1 - Optimizador de Portfolio Inteligente