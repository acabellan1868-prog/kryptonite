# Kryptonite - Roadmap 2026

> Plan de evolución y mejora del sistema de análisis de inversiones en criptomonedas

---

## 📋 Contexto

Este documento contiene ideas de mejora y evolución para **Kryptonite**, resultado de sesiones de brainstorming. Las ideas están priorizadas según:
- **Impacto:** Valor que aportan al usuario
- **Complejidad:** Esfuerzo de implementación
- **Sinergia:** Aprovechamiento de infraestructura existente

---

## 🏗️ Arquitectura Actual (Base)

```
Usuario (Telegram)
    ↓
Node-RED (Orquestador)
    ↓
Kryptonite API (Flask)
    ↓
Binance API + SQLite
```

**Fortalezas:**
- ✅ Interfaz de usuario ya resuelta (Telegram)
- ✅ Orquestación y automatización funcionando (Node-RED)
- ✅ Backend robusto con datos históricos (SQLite + Binance)
- ✅ Agente IA conversacional operativo (LangChain + Groq)
- ✅ Sistema de backtesting implementado

**Oportunidades de mejora:**
- Aprovechar más los datos de la tabla `operaciones`
- Hacer el agente IA más proactivo y útil
- Mejorar precisión de señales de trading
- Añadir capacidades predictivas

---

## 🎯 Ideas Propuestas

### 🔥 ALTA PRIORIDAD

Ideas que mejoran significativamente la funcionalidad existente aprovechando infraestructura ya disponible.

---

#### 1️⃣ Optimizador de Portfolio Inteligente

**Descripción:**
Sistema que analiza el portfolio actual (tabla `operaciones`) y sugiere acciones de rebalanceo para optimizar exposición al riesgo.

**Funcionalidades:**
- Calcular % de exposición por cripto
- Detectar sobreexposición a activos volátiles
- Sugerir rebalanceo basado en:
  - Capitalización de mercado
  - Volatilidad histórica
  - Correlación entre activos
  - Objetivos de riesgo del usuario
- Alertas automáticas cuando una cripto supera X% del portfolio

**Implementación Técnica:**
- **Endpoint:** `GET /portfolio/analisis`
- **Retorna:**
  ```json
  {
    "composicion_actual": [
      {"cripto": "BTC", "porcentaje": 45, "valor_eur": 450},
      {"cripto": "ETH", "porcentaje": 30, "valor_eur": 300},
      ...
    ],
    "alertas": [
      "⚠️ BTC representa el 45% del portfolio (recomendado: <40%)"
    ],
    "sugerencias_rebalanceo": [
      "Considerar reducir BTC en 50€ y aumentar ETH en 50€"
    ],
    "metricas_riesgo": {
      "volatilidad_portfolio": 0.18,
      "sharpe_ratio": 1.2,
      "diversificacion_score": 0.65
    }
  }
  ```

**Integración con Node-RED:**
- Trigger diario/semanal
- Envío de alertas a Telegram si hay sugerencias importantes

**Valor Añadido:**
- Aprovecha datos reales de `operaciones` (ya existentes)
- Ayuda a tomar decisiones de gestión de riesgo
- No requiere nuevas fuentes de datos

**Complejidad:** Media
**Tiempo estimado:** 2-3 sesiones de desarrollo

---

#### 2️⃣ Mejoras al Agente IA (grog_agente.py)

**Descripción:**
Ampliar las capacidades del agente LangChain existente para hacerlo más útil y proactivo.

**Mejoras Propuestas:**

##### A. Análisis Técnico Automático
- **Capacidad:** El agente puede ejecutar análisis técnicos al responder
- **Ejemplo de interacción:**
  ```
  Usuario: "¿Debería comprar más BTC ahora?"
  Agente:
    1. Consulta precio actual
    2. Ejecuta análisis de medias móviles
    3. Revisa cambios recientes de precio
    4. Consulta sentimiento de noticias
    5. Responde con recomendación fundamentada
  ```

##### B. Historial de Conversaciones
- **Tabla nueva:** `conversaciones_ia`
  ```sql
  CREATE TABLE conversaciones_ia (
    id INTEGER PRIMARY KEY,
    timestamp INTEGER,
    usuario TEXT,
    pregunta TEXT,
    respuesta TEXT,
    contexto_usado TEXT
  );
  ```
- **Beneficio:** El agente puede recordar preguntas anteriores y dar respuestas más contextuales

##### C. Recomendaciones Proactivas
- **Nueva herramienta MCP:** `calcular_punto_entrada_salida`
- **Funcionalidad:**
  - Analiza datos históricos
  - Identifica niveles de soporte/resistencia
  - Sugiere puntos de entrada/salida óptimos

##### D. Modo Experto vs Principiante
- Ajustar verbosidad según nivel de usuario
- Explicaciones detalladas para principiantes
- Datos técnicos directos para expertos

**Implementación Técnica:**
- Ampliar `herramientas_mcp` con nuevas funciones de análisis
- Mejorar prompt del sistema con instrucciones más específicas
- Modificar memoria para persistir contexto entre sesiones

**Integración con Node-RED:**
- Endpoint `/prompt` ya existe, solo mejorar capacidades internas

**Valor Añadido:**
- Convierte al agente de "consultor pasivo" a "asesor activo"
- Reduce necesidad de múltiples consultas manuales
- Aprovecha infraestructura LangChain ya montada

**Complejidad:** Media-Alta
**Tiempo estimado:** 3-4 sesiones de desarrollo

---

#### 3️⃣ Sistema de Alertas Avanzadas con Condiciones Complejas

**Descripción:**
Sistema que permite definir alertas personalizadas combinando múltiples condiciones (precio, volumen, sentimiento, indicadores técnicos).

**Funcionalidades:**

##### A. Creación de Alertas
- **Endpoint:** `POST /alertas/crear`
- **Body:**
  ```json
  {
    "nombre": "BTC - Oportunidad de compra",
    "cripto": "BTC",
    "condiciones": [
      {
        "tipo": "precio",
        "operador": "menor_que",
        "valor": 85000,
        "moneda": "USD"
      },
      {
        "tipo": "volumen",
        "operador": "mayor_que_promedio",
        "porcentaje": 30
      },
      {
        "tipo": "sentimiento_noticias",
        "operador": "igual",
        "valor": "Positivo"
      }
    ],
    "logica": "AND",  // O "OR"
    "activa": true,
    "frecuencia_chequeo": "5m"
  }
  ```

##### B. Gestión de Alertas
- `GET /alertas` - Listar todas las alertas
- `PUT /alertas/{id}` - Modificar alerta
- `DELETE /alertas/{id}` - Eliminar alerta
- `GET /alertas/{id}/estado` - Ver si está activa

##### C. Motor de Evaluación
- **Tabla nueva:** `alertas`, `alertas_historial`
- **Proceso:**
  1. Node-RED llama a `GET /alertas/evaluar` cada X minutos
  2. Kryptonite evalúa cada alerta activa
  3. Si condiciones se cumplen → registra en `alertas_historial`
  4. Retorna alertas disparadas
  5. Node-RED envía notificación a Telegram

##### D. Tipos de Condiciones Soportadas
- **Precio:** mayor/menor/igual/entre/cambio_porcentual
- **Volumen:** mayor/menor/mayor_que_promedio
- **Indicadores técnicos:** RSI, MACD, Bollinger Bands
- **Sentimiento:** positivo/negativo/neutral
- **Medias móviles:** cruce_alcista/cruce_bajista
- **Tiempo:** horario (ej: solo entre 9h-18h)

**Implementación Técnica:**

```python
# Tabla de alertas
CREATE TABLE alertas (
  id INTEGER PRIMARY KEY,
  nombre TEXT,
  cripto TEXT,
  condiciones JSON,  -- Almacenar como JSON
  logica TEXT,       -- "AND" o "OR"
  activa INTEGER,
  frecuencia_chequeo TEXT,
  fecha_creacion INTEGER,
  ultima_evaluacion INTEGER,
  veces_disparada INTEGER DEFAULT 0
);

CREATE TABLE alertas_historial (
  id INTEGER PRIMARY KEY,
  alerta_id INTEGER,
  timestamp INTEGER,
  valores_evaluados JSON,
  FOREIGN KEY(alerta_id) REFERENCES alertas(id)
);
```

**Integración con Node-RED:**
- Flujo que evalúa alertas periódicamente
- Envío condicional a Telegram solo cuando se disparan

**Valor Añadido:**
- Personalización total para cada usuario
- Reduce "ruido" de notificaciones irrelevantes
- Combina múltiples señales para mayor precisión
- Historial de alertas para análisis posterior

**Complejidad:** Alta
**Tiempo estimado:** 4-5 sesiones de desarrollo

---

### 🟡 MEDIA PRIORIDAD

Funcionalidad nueva que añade valor pero requiere más infraestructura.

---

#### 4️⃣ Análisis Predictivo Mejorado (ML)

**Descripción:**
Ampliar el modelo Random Forest existente para generar predicciones utilizables.

**Estado Actual:**
- Modelo `random_forest_cripto.joblib` entrenado
- ❌ NO hay endpoints que lo usen
- ❌ NO está claro qué predice ni con qué features

**Mejoras Propuestas:**

##### A. Re-entrenar y Documentar Modelo
- Definir claramente objetivo de predicción:
  - ¿Precio en 1h/24h/7d?
  - ¿Dirección (sube/baja)?
  - ¿Volatilidad esperada?
- Features propuestos:
  - Precio actual
  - Medias móviles (7, 14, 30 períodos)
  - RSI
  - Volumen vs promedio
  - Cambio porcentual 1h, 24h
  - Sentimiento de noticias (si disponible)

##### B. Modelos por Cripto
- Entrenar modelo específico para BTC, ETH, etc.
- Mejor precisión que modelo único

##### C. Endpoints de Predicción
- `GET /prediccion/precio?cripto=BTC&horizonte=24h`
  ```json
  {
    "cripto": "BTC",
    "precio_actual": 85234,
    "prediccion_24h": 86100,
    "confianza": 0.73,
    "tendencia": "alcista",
    "features_importantes": {
      "media_movil_7d": 0.35,
      "rsi": 0.22,
      "volumen_ratio": 0.18
    }
  }
  ```

##### D. Re-entrenamiento Automático
- Script que re-entrena modelos semanalmente con datos nuevos
- Evaluación de métricas (MAE, RMSE) antes de reemplazar modelo

**Implementación Técnica:**
- Archivo: `src/modelo_ia.py` (ya existe, ampliar)
- Notebook de experimentación para optimizar hiperparámetros
- Guardar métricas de rendimiento en BD

**Valor Añadido:**
- Predicciones cuantitativas (no solo señales binarias)
- Complementa análisis técnico tradicional
- Aprovecha modelo ya entrenado

**Complejidad:** Media-Alta
**Tiempo estimado:** 4-6 sesiones de desarrollo

---

#### 5️⃣ Sistema de Paper Trading

**Descripción:**
Simulador de trading en tiempo real para probar estrategias sin riesgo.

**Funcionalidades:**

##### A. Gestión de Portfolio Virtual
- **Tabla nueva:** `paper_portfolio`, `paper_trades`
- Capital inicial configurable
- Track de operaciones simuladas

##### B. Endpoints
- `POST /paper/comprar` - Simular compra
  ```json
  {
    "cripto": "BTC",
    "cantidad_eur": 100
  }
  ```
- `POST /paper/vender` - Simular venta
- `GET /paper/portfolio` - Estado actual
- `GET /paper/rendimiento` - Performance vs portfolio real

##### C. Ejecución Automática de Estrategias
- Activar backtesting en modo "live paper trading"
- Ejecutar operaciones simuladas según señales

##### D. Comparación Real vs Paper
- Dashboard que muestra:
  - Rendimiento portfolio real
  - Rendimiento paper trading
  - Diferencias y aprendizajes

**Implementación Técnica:**

```sql
CREATE TABLE paper_portfolio (
  cripto TEXT PRIMARY KEY,
  cantidad REAL,
  coste_promedio REAL,
  fecha_primera_compra INTEGER
);

CREATE TABLE paper_trades (
  id INTEGER PRIMARY KEY,
  timestamp INTEGER,
  cripto TEXT,
  tipo TEXT,  -- 'compra' o 'venta'
  cantidad REAL,
  precio REAL,
  comision REAL,
  estrategia TEXT  -- Qué estrategia disparó la orden
);
```

**Valor Añadido:**
- Probar estrategias sin riesgo financiero
- Ajustar parámetros antes de operar en real
- Comparar rendimiento de diferentes estrategias

**Complejidad:** Media
**Tiempo estimado:** 3-4 sesiones de desarrollo

---

#### 6️⃣ Análisis Multi-Timeframe

**Descripción:**
Analizar señales en múltiples temporalidades simultáneamente para detectar confluencias.

**Funcionalidades:**

##### A. Análisis Paralelo
- Evaluar misma estrategia en: 1m, 5m, 15m, 1h, 4h, 1d
- Detectar cuando múltiples timeframes dan la misma señal (confluencia)

##### B. Endpoint
- `GET /senal/multi_timeframe?cripto=BTC&estrategia=cambio_extremo`
  ```json
  {
    "cripto": "BTC",
    "timeframes": {
      "1m": {"senal": "NEUTRAL", "confianza": 0.5},
      "5m": {"senal": "COMPRA", "confianza": 0.7},
      "15m": {"senal": "COMPRA", "confianza": 0.8},
      "1h": {"senal": "COMPRA", "confianza": 0.9},
      "4h": {"senal": "NEUTRAL", "confianza": 0.6},
      "1d": {"senal": "COMPRA", "confianza": 0.75}
    },
    "confluencia": {
      "senal_mayoritaria": "COMPRA",
      "timeframes_alineados": ["5m", "15m", "1h", "1d"],
      "fuerza_senal": 0.78
    }
  }
  ```

##### C. Visualización
- Gráfica que muestra señales en cada timeframe
- Highlighting cuando hay confluencia fuerte

**Valor Añadido:**
- Mayor precisión en señales (reduce falsos positivos)
- Confirmación multi-temporal antes de operar
- Identificar tendencias vs ruido de corto plazo

**Complejidad:** Media
**Tiempo estimado:** 2-3 sesiones de desarrollo

---

#### 7️⃣ Exportación de Reportes Automáticos

**Descripción:**
Generar informes PDF con análisis completo del portfolio y rendimiento.

**Funcionalidades:**

##### A. Tipos de Reportes
- **Diario:** Resumen de cambios del día
- **Semanal:** Performance semanal + top movers
- **Mensual:** Análisis completo + recomendaciones

##### B. Contenido del Reporte
- Resumen ejecutivo
- Gráficas de rendimiento
- Tabla de operaciones realizadas
- Comparación con benchmarks (BTC, ETH)
- Análisis de riesgo
- Recomendaciones del agente IA
- Sentimiento de mercado

##### C. Endpoint
- `GET /reportes/generar?periodo=semanal&formato=pdf`
- Retorna PDF en base64 o guarda en disco

**Implementación Técnica:**
- Librería: `reportlab` o `weasyprint`
- Templates HTML → PDF
- Uso de gráficas ya generadas por `charts.py`

**Valor Añadido:**
- Documentación histórica de decisiones
- Análisis retrospectivo de estrategias
- Compartible con asesores/terceros

**Complejidad:** Media
**Tiempo estimado:** 3-4 sesiones de desarrollo

---

### 🟢 BAJA PRIORIDAD

Ideas interesantes pero menos críticas o con ROI menor.

---

#### 8️⃣ Integración Multi-Exchange

**Descripción:**
Expandir más allá de Binance (Kraken, Coinbase, etc.).

**Utilidad:**
- Comparar precios entre exchanges (arbitraje)
- Diversificar fuentes de datos
- Operar en el exchange con mejor precio

**Consideraciones:**
- ¿Operas actualmente en múltiples exchanges?
- Si no, el esfuerzo no justifica el beneficio

**Complejidad:** Alta
**Tiempo estimado:** 5-7 sesiones de desarrollo

---

#### 9️⃣ Webhooks para Eventos

**Descripción:**
Sistema de webhooks para recibir notificaciones push en lugar de polling.

**Ventajas:**
- Más eficiente que Node-RED haciendo polling constante
- Respuesta más rápida a eventos

**Desventajas:**
- Node-RED ya funciona bien
- Requiere infraestructura adicional (servidor expuesto)

**Complejidad:** Media
**Tiempo estimado:** 2-3 sesiones de desarrollo

---

#### 🔟 Dashboard Web Standalone

**Descripción:**
Interfaz web con Plotly Dash o Streamlit.

**Consideración:**
- Telegram ya funciona como interfaz
- Redundante a menos que necesites visualización en pantalla grande

**Complejidad:** Alta
**Tiempo estimado:** 6-8 sesiones de desarrollo

---

## 🎯 Recomendación de Roadmap

### Fase 1: Optimización de lo Existente (1-2 meses) ✅ **FASES 1.1, 1.2.1 Y 1.3 COMPLETADAS**
1. **✅ Optimizador de Portfolio** ← **IMPLEMENTADO** (ver [fase-1.1-portfolio](implementacion_roadmap_2026/fase-1.1-portfolio/))
   - ✅ Cálculo de composición del portfolio (%)
   - ✅ Detección de alertas (sobreexposición, pérdidas severas)
   - ✅ Métricas de riesgo (diversificación, exposición)
   - ✅ Endpoint `/portafolio?analisis=completo`
   - ✅ Parámetros configurables en `parametros.env`
   - ✅ 100% retrocompatible
   - ✅ **NUEVO:** Detección de cambios desde última consulta (Fase 1.3) - [ver docs](implementacion_roadmap_2026/fase-1.3-cambios-portfolio/)
2. **✅ Mejoras al Agente IA (Fase 1.2.1)** ← **IMPLEMENTADO** (ver [fase-1.2-mejoras-agente-ia](implementacion_roadmap_2026/fase-1.2-mejoras-agente-ia/))
   - ✅ Herramientas de análisis técnico (3 nuevas)
   - ✅ Análisis de señales de trading automático
   - ✅ Análisis de portfolio integrado
   - ✅ Cálculo de rendimientos históricos
   - ⏸️ Historial persistente (Fase 1.2.2 - Pendiente)
   - ⏸️ Modo Experto/Principiante (Fase 1.2.3 - Pendiente)
   - ⏸️ Recomendaciones Proactivas (Fase 1.2.4 - Pendiente)
3. **Sistema de Alertas Avanzadas** ← Complementa Node-RED (PENDIENTE)

### Fase 2: Capacidades Predictivas (2-3 meses)
4. **Análisis Predictivo Mejorado** ← Usar modelo existente
5. **Análisis Multi-Timeframe** ← Mejora precisión de señales

### Fase 3: Experimentación y Refinamiento (3-4 meses)
6. **Paper Trading** ← Probar nuevas estrategias
7. **Reportes Automáticos** ← Documentación y análisis

### Fase 4: Expansión (Opcional, futuro)
8. Multi-Exchange
9. Webhooks
10. Dashboard Web

---

## 📊 Matriz de Priorización

| Idea | Impacto | Complejidad | Aprovecha Existente | Prioridad | Estado |
|------|---------|-------------|---------------------|-----------|--------|
| Optimizador Portfolio (Fase 1.1) | 🔥🔥🔥 | Media | ✅ Tabla operaciones | **ALTA** | ✅ **COMPLETADO** |
| Detección Cambios Portfolio (Fase 1.3) | 🔥🔥 | Baja | ✅ Fase 1.1 | **ALTA** | ✅ **COMPLETADO** |
| Mejoras Agente IA (Fase 1.2.1) | 🔥🔥🔥 | Media-Alta | ✅ LangChain | **ALTA** | ✅ **COMPLETADO** |
| Alertas Avanzadas | 🔥🔥 | Alta | ✅ Node-RED | **ALTA** | ⏸️ Pendiente |
| Predictivo ML | 🔥🔥 | Media-Alta | ✅ Modelo RF | **MEDIA** | ⏸️ Pendiente |
| Paper Trading | 🔥🔥 | Media | ⚠️ Nueva infra | **MEDIA** | ⏸️ Pendiente |
| Multi-Timeframe | 🔥 | Media | ✅ Analysis.py | **MEDIA** | ⏸️ Pendiente |
| Reportes PDF | 🔥 | Media | ✅ Charts.py | **MEDIA** | ⏸️ Pendiente |
| Multi-Exchange | 🔥 | Alta | ❌ Nueva integración | **BAJA** | ⏸️ Pendiente |
| Webhooks | 🔥 | Media | ⚠️ Cambio arquitectura | **BAJA** | ⏸️ Pendiente |
| Dashboard Web | 🔥 | Alta | ❌ Nuevo frontend | **BAJA** | ⏸️ Pendiente |

---

## 🤔 Próximos Pasos

### ✅ Completado
1. ✅ **Fase 1.1 - Optimizador de Portfolio**
   - Cálculo de composición y métricas
   - Detección de alertas
   - Endpoint `/portafolio?analisis=completo`
   - Documentación completa

2. ✅ **Fase 1.2.1 - Mejoras al Agente IA: Herramientas de Análisis**
   - 3 nuevas herramientas MCP (análisis técnico)
   - Señales de trading automáticas (COMPRA/VENTA/MANTENER)
   - Análisis de portfolio integrado
   - Rendimiento histórico por cripto
   - Prompt del sistema mejorado
   - Agente transformado de "consultor" a "asesor"

3. ✅ **Fase 1.3 - Detección de Cambios desde Última Consulta**
   - Snapshots automáticos del portfolio
   - Comparación con estado anterior
   - Tiempo transcurrido formateado
   - Detección de nuevas/cerradas posiciones
   - 100% retrocompatible

### 🔄 En Progreso
- Ninguna (esperando selección de siguiente fase)

### 📋 Siguiente Fase Sugerida
**Opción 1:** Fase 1.2.2 - Historial Persistente del Agente IA
**Opción 2:** Sistema de Alertas Avanzadas (complementa análisis de portfolio)
**Opción 3:** Fase 1.2.3 - Modo Experto/Principiante para el Agente

---

## 📝 Notas de Brainstorming

### Preguntas Abiertas
- ¿Cuál es el objetivo principal? ¿Maximizar rentabilidad o minimizar riesgo?
- ¿Qué nivel de automatización quieres? ¿Sugerencias o ejecución automática?
- ¿Cuántas operaciones haces al mes? (para calibrar utilidad de paper trading)
- ¿Tienes acceso a otros exchanges además de Binance?

### Ideas Descartadas (por ahora)
- **Trading automático real:** Requiere mucha confianza en el sistema
- **Integración con exchanges DeFi:** Complejidad muy alta
- **Análisis on-chain:** Fuera del scope actual
- **Social trading:** No aplica (uso personal)

---

## 🎨 PROYECTO: Optimizador de Portfolio Inteligente

### Hoja de Ruta de Implementación

#### **FASE 1: Visualización Básica** 📊

**Item 1.1: Visor de Portfolio Simple**
- Input: Usuario ingresa sus cryptos y cantidades manualmente
- Output: Tabla mostrando: nombre, cantidad, precio actual, valor total
- Valor: Ya puedes ver todo tu portfolio en un solo sitio con valores actualizados

**Item 1.2: Gráfico de Distribución**
- Input: El portfolio del item anterior
- Output: Gráfico de torta/donut mostrando % de cada crypto
- Valor: Ves visualmente dónde está concentrado tu dinero

**Item 1.3: Totales y Estadísticas Básicas**
- Output: Valor total del portfolio, % de cambio 24h, mayor/menor posición
- Valor: Overview rápido de tu situación

---

#### **FASE 2: Análisis de Riesgo Simple** ⚠️

**Item 2.1: Categorización por Capitalización**
- Output: Clasificación de cada crypto (Large cap, Mid cap, Small cap)
- Visualización: Gráfico mostrando distribución por categoría
- Valor: Entiendes si estás muy expuesto a cryptos pequeñas y arriesgadas

**Item 2.2: Alertas de Concentración**
- Output: Avisos tipo "El 70% de tu portfolio está en una sola moneda"
- Valor: Te previene de riesgos evidentes sin cálculos complejos

---

#### **FASE 3: Comparación con Perfiles de Referencia** 🎯

**Item 3.1: Perfiles Pre-definidos**
- Defines 3 perfiles de referencia (Conservador, Moderado, Agresivo)
- Cada uno con % recomendados (ej: Conservador = 40% BTC, 30% ETH, 20% Stablecoins, 10% Altcoins)
- Valor: Tienes benchmarks claros

**Item 3.2: Comparador Visual**
- Input: Seleccionas un perfil de referencia
- Output: Gráfico comparando tu portfolio vs el perfil ideal
- Valor: Ves de un vistazo en qué te desvías

**Item 3.3: Sugerencias de Rebalanceo Simples**
- Output: "Para acercarte al perfil Moderado: aumenta BTC en un 15%, reduce Altcoins en 10%"
- Valor: Recomendaciones concretas y accionables

---

#### **FASE 4: Historial y Tendencias** 📈

**Item 4.1: Guardar Snapshots del Portfolio**
- Guardas el estado de tu portfolio en fechas específicas
- Valor: Empiezas a construir tu historial

**Item 4.2: Evolución Temporal**
- Output: Gráfico mostrando cómo ha cambiado el valor total en el tiempo
- Valor: Ves si estás ganando o perdiendo

**Item 4.3: Performance por Activo**
- Output: Ranking de qué cryptos te han dado mejor/peor rendimiento
- Valor: Identificas ganadores y perdedores

---

#### **FASE 5: Simulador "What-if"** 🔮

**Item 5.1: Simulador de Cambios**
- Input: "¿Qué pasa si vendo X cantidad de crypto A y compro crypto B?"
- Output: Cómo quedaría tu nuevo portfolio y distribución
- Valor: Puedes probar ideas antes de ejecutarlas

**Item 5.2: Simulador de Precio**
- Input: "¿Qué pasa si BTC sube/baja un 20%?"
- Output: Impacto en tu portfolio total
- Valor: Evalúas escenarios de mercado

---

#### **FASE 6: Optimización Avanzada** 🧮

**Item 6.1: Cálculo de Correlaciones**
- Análisis de cómo se mueven tus cryptos juntas
- Valor: Entiendes si realmente estás diversificado

**Item 6.2: Optimización Matemática Básica**
- Algoritmo que sugiere distribución óptima según riesgo/retorno
- Valor: Recomendaciones basadas en datos históricos reales

---

### Orden de Implementación Propuesto

1. Item 1.1 → Base de todo
2. Item 1.2 → Visualización que da valor inmediato
3. Item 1.3 → Estadísticas básicas útiles
4. Item 2.1 → Primera capa de análisis
5. Item 2.2 → Primeras recomendaciones (simples)
6. Item 3.1 → Estableces referencias
7. Item 3.2 → Comparación visual potente
8. Item 3.3 → Sugerencias más elaboradas
9. Los demás según prioridad...

---

**Última actualización:** 2025-12-15
**Estado:** ✅ Fases 1.1 y 1.3 COMPLETADAS - En producción (100% retrocompatible)
