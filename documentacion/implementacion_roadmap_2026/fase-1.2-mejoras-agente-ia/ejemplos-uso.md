# Ejemplos de Uso - Fase 1.2.1

> Ejemplos prácticos de cómo usar las nuevas herramientas del agente IA

---

## 📋 Índice

1. [Análisis Técnico (Señales de Trading)](#1-análisis-técnico-señales-de-trading)
2. [Rendimiento Individual de Criptomoneda](#2-rendimiento-individual-de-criptomoneda)
3. [Análisis de Portfolio](#3-análisis-de-portfolio)
4. [Consultas Combinadas](#4-consultas-combinadas)
5. [Comparativa Antes vs Ahora](#5-comparativa-antes-vs-ahora)

---

## 1. Análisis Técnico (Señales de Trading)

### 📝 Prompts de Ejemplo

```
¿Debería comprar BTC ahora?
```

```
Dame una señal de trading para ETH
```

```
¿Es buen momento para invertir en SOL?
```

```
Dame un párrafo sobre la situación actual del mercado cripto
```

---

### 💬 Ejemplo de Interacción

**Usuario:**
```
¿Debería comprar BTC ahora?
```

**Agente IA:**
```
Según el análisis técnico actual, la situación de BTC es de MANTENER.

📊 Análisis realizado:

🔍 ESTRATEGIA: Cambio Extremo (15 min)
   • Precio actual: 75,250.52€
   • Cambio porcentual: 0.00%
   • Tendencia previa: LATERAL
   • 🎯 SEÑAL: MANTENER

📈 ESTRATEGIA: Medias Móviles (SMA 50/200)
   • SMA 50: 75,273.26€
   • SMA 200: 75,263.21€
   • 🎯 SEÑAL: MANTENER

El mercado se encuentra en un momento de estabilidad sin señales claras
de compra o venta. Las medias móviles están muy cercanas entre sí,
indicando consolidación. Recomiendo esperar a que se defina una tendencia
más clara antes de tomar posición.
```

**Tokens usados:** ~5,867
**Llamadas al LLM:** 2
**Herramienta ejecutada:** `analizar_senal_compra_venta("BTC", "todas")`

---

## 2. Rendimiento Individual de Criptomoneda

### 📝 Prompts de Ejemplo

```
¿Cuánto he ganado con BTC?
```

```
¿Cómo va mi inversión en ETH?
```

```
Dame el rendimiento de SOL
```

```
¿A qué precio compré ADA?
```

---

### 💬 Ejemplo de Interacción

**Usuario:**
```
¿Cuánto he ganado con BTC?
```

**Agente IA:**
```
Has perdido 55.84€ con BTC, lo que representa una pérdida del 13.13%
respecto a tu inversión inicial.

💰 DETALLES DEL RENDIMIENTO:

📊 POSICIÓN ACTUAL:
   • Cantidad: 0.00490576 BTC
   • Precio actual: 75,277.37€
   • Valor actual: 369.29€

📈 INVERSIÓN:
   • Precio medio de compra: 86,659.36€
   • Total invertido: 425.13€

❌ RESULTADO:
   • PÉRDIDA: -55.84€ (-13.13%)

Tu precio medio de compra (86,659€) está por encima del precio actual
(75,277€), por lo que estás en pérdidas. Si crees en el potencial a
largo plazo de BTC, podrías considerar esta caída como oportunidad de
promediar tu precio de compra.
```

**Tokens usados:** ~5,657
**Llamadas al LLM:** 2
**Herramienta ejecutada:** `calcular_rendimiento_historico("BTC")`

---

## 3. Análisis de Portfolio

### 📝 Prompts de Ejemplo

```
¿Cómo está mi portfolio?
```

```
Dame un resumen de mis inversiones
```

```
¿Cuánto he ganado/perdido en total?
```

```
Dame un resumen completo de mi portfolio
```

---

### 💬 Ejemplo de Interacción

**Usuario:**
```
Dame un resumen completo de mi portfolio
```

**Agente IA:**
```
Aquí tienes el análisis completo de tu portfolio:

💼 RESUMEN DEL PORTFOLIO

📊 Totales:
   • Valor actual: 862.71€
   • Inversión total: 1,166.16€
   • Rentabilidad: -26.01%

🪙 Activos (6):
   • BTC: 369.29€ (-13.13%)
   • ETH: 246.27€ (-38.46%)
   • SOL: 148.81€ (-26.06%)
   • ADA: 53.58€ (-36.22%)
   • AVAX: 29.90€ (-24.68%)
   • ... y 1 más

📉 ANÁLISIS:
Tu portfolio actualmente está en pérdidas con una rentabilidad del -26%.
Los activos con peor rendimiento son ETH (-38%) y ADA (-36%). BTC es el
que mejor se está comportando con solo -13% de pérdida.

Recomendaría revisar si quieres mantener los activos con mayores pérdidas
o rebalancear hacia los que están mostrando mejor resistencia.
```

**Tokens usados:** ~15,702
**Llamadas al LLM:** 5
**Herramienta ejecutada:** `obtener_analisis_portfolio()`

---

## 4. Consultas Combinadas

### 📝 Prompts de Ejemplo

```
¿Cómo está mi portfolio y debería comprar más BTC?
```

```
Analiza mi inversión en ETH y dime si vender ahora
```

```
Dame análisis completo: portfolio, rendimiento de BTC y señal de ETH
```

---

### 💬 Ejemplo de Interacción

**Usuario:**
```
¿Cómo está mi portfolio y debería comprar más BTC?
```

**Agente IA:**
```
Déjame analizar tu situación completa:

💼 ESTADO DE TU PORTFOLIO:

📊 Totales:
   • Valor actual: 862.71€
   • Inversión total: 1,166.16€
   • Rentabilidad: -26.01%

Tu portfolio actual:
   • BTC: 369.29€ (42.8% del portfolio, -13.13%)
   • ETH: 246.27€ (28.5% del portfolio, -38.46%)
   • Otros 4 activos: 247.15€

📊 SEÑAL DE BTC:

Análisis técnico actual:
   • Cambio extremo: MANTENER (tendencia lateral)
   • Medias móviles: MANTENER (SMA 50/200 muy cercanas)

💡 RECOMENDACIÓN:

1. BTC representa el 42.8% de tu portfolio (bastante concentrado)
2. BTC es tu activo con mejor rendimiento (-13% vs -26% promedio)
3. El análisis técnico sugiere esperar (mercado lateral sin dirección clara)

Mi recomendación: ESPERAR antes de comprar más BTC por dos razones:
   • Ya tienes exposición significativa (43% del portfolio)
   • El mercado no muestra señales claras de entrada

Considera primero:
   - Rebalancear reduciendo posiciones con -38% pérdidas
   - Esperar a que BTC muestre señal clara de compra
   - Diversificar si decides invertir más capital
```

**Tokens usados:** ~18,000+
**Llamadas al LLM:** 6-8
**Herramientas ejecutadas:**
1. `obtener_analisis_portfolio()`
2. `analizar_senal_compra_venta("BTC", "todas")`

---

## 5. Comparativa Antes vs Ahora

### Antes (Sin Herramientas de Análisis)

**Prompt:** `¿Debería comprar BTC?`

**Respuesta antigua:**
```
Para responder esa pregunta, déjame consultar los datos...

[Ejecuta query SQL para obtener precio actual]

El precio actual de BTC es 75,250€. No tengo suficiente información
para darte una recomendación de compra. Podrías consultar el precio
histórico o hacer un análisis más detallado.
```

❌ No daba señales de trading
❌ No ejecutaba análisis técnico
❌ Respuesta poco útil

---

### Ahora (Con Herramientas de Análisis)

**Prompt:** `¿Debería comprar BTC?`

**Respuesta nueva:**
```
Según el análisis técnico actual, la situación de BTC es de MANTENER.

📊 Análisis realizado:

🔍 Cambio Extremo: Tendencia LATERAL (0% cambio)
📈 Medias Móviles: SMA 50/200 muy cercanas → MANTENER

Recomendación: Esperar a señales más claras antes de comprar.
```

✅ Señal de trading clara
✅ Análisis técnico automático
✅ Recomendación fundamentada

---

## 📊 Tabla de Prompts por Herramienta

| Herramienta | Prompts que la Activan |
|-------------|------------------------|
| `analizar_senal_compra_venta` | "¿Debería comprar X?", "Dame señal de X", "¿Es buen momento para X?", "Análisis técnico de X" |
| `calcular_rendimiento_historico` | "¿Cuánto he ganado con X?", "Rendimiento de X", "¿Cómo va mi inversión en X?" |
| `obtener_analisis_portfolio` | "¿Cómo está mi portfolio?", "Resumen de inversiones", "Análisis de portfolio" |

---

## 🎯 Tips para Mejores Resultados

1. **Sé específico:** "Dame señal de BTC" es mejor que "Ayúdame con trading"

2. **Combina preguntas:** "Analiza mi portfolio y dime si comprar más ETH" ejecuta múltiples herramientas

3. **Usa lenguaje natural:** El agente entiende variaciones como:
   - "¿Compro BTC?" = "¿Debería comprar BTC ahora?"
   - "¿Cómo voy con ETH?" = "¿Cuánto he ganado con ETH?"

4. **Pide explicaciones:** "¿Por qué recomiendas mantener?" hará que el agente profundice en el análisis

---

**Última actualización:** 2025-12-20
