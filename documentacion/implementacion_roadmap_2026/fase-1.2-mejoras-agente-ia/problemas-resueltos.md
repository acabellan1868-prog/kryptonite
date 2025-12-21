# Problemas Resueltos Durante la Implementación

> Documentación de problemas encontrados y sus soluciones

---

## 🐛 Problema 1: Herramienta `obtener_analisis_portfolio` No Se Ejecutaba

### Síntomas
- El agente hacía "Llamada #1" con 13 tokens de salida
- Nunca aparecía el mensaje "Invoking: obtener_analisis_portfolio"
- No se veían los logs de debug dentro de `_run()`
- El agente se quedaba colgado sin responder

### Logs Observados
```
> Entering new AgentExecutor chain...
📊 Llamada #1 | Tokens: entrada=2726, salida=13, total=2739
✅ Respuesta generada correctamente
[NUNCA llega "Finished chain"]
```

### Causa Raíz
LangChain no invocaba correctamente herramientas con **schema de entrada vacío**.

**Código problemático:**
```python
class EntradaAnalisisPortfolio(BaseModel):
    """Input para obtener análisis del portfolio - no requiere parámetros"""
    pass  # ← LangChain no llamaba a _run()
```

### Solución
Añadir un campo dummy al schema de Pydantic:

```python
class EntradaAnalisisPortfolio(BaseModel):
    """Input para obtener análisis del portfolio"""
    # Campo dummy para compatibilidad con LangChain (no se usa)
    dummy: str = Field(default="", description="No se requieren parámetros para esta herramienta")
```

Y actualizar la firma del método:
```python
def _run(self, dummy: str = "") -> str:
    """Ejecuta la herramienta"""
    # ... código ...
```

### Resultado
✅ La herramienta ahora se ejecuta correctamente
✅ Los logs aparecen en Flask
✅ El agente recibe la respuesta y continúa

---

## 🐛 Problema 2: Max Iterations Alcanzado

### Síntomas
- Error: "Agent stopped due to max iterations."
- El agente hacía 5 llamadas y se detenía sin terminar
- Especialmente con consultas que combinan múltiples herramientas

### Logs Observados
```
💸 Tokens usados: 15702
   ↳ Entrada: 15390
   ↳ Salida:  312
   ↳ Llamadas:  5

Agent stopped due to max iterations.
```

### Causa Raíz
El límite de `max_iterations=5` era insuficiente para análisis complejos que requieren:
1. Llamada a herramienta #1
2. Procesamiento
3. Llamada a herramienta #2
4. Procesamiento
5. Generación de respuesta final

Con el límite en 5, se agotaba antes de completar.

### Solución
Aumentar `max_iterations` de 5 a 10:

```python
self.ejecutor_agente = AgentExecutor(
    agent=agente,
    tools=self.herramientas,
    memory=self.memoria,
    verbose=True,
    max_iterations=10,  # ← AUMENTADO de 5 a 10
    handle_parsing_errors=True,
    return_intermediate_steps=True
)
```

### Resultado
✅ Consultas complejas ahora completan correctamente
✅ El agente tiene margen suficiente para análisis combinados
✅ Sin impacto negativo en performance (termina cuando está listo, no usa siempre 10)

---

## 🐛 Problema 3: Circular Import Dependencies

### Síntomas
- Error: `ImportError: cannot import name 'analizar_portfolio_completo'`
- Al importar `analisis_tools.py` desde `grog_agente.py`

### Causa Raíz
Import circular entre módulos:
```
analisis_tools.py
    → imports portfolio_analyzer
        → imports analisis_rendimineto
            → imports modelos
                → imports database
                    → imports config
```

### Solución
**Opción A - Import Dinámico (Implementada):**
```python
def _run(self, dummy: str = "") -> str:
    try:
        # Importar aquí para evitar problemas de importación circular
        from analisis_rendimineto import calcular_rendimiento_portafolio_total

        portfolio_data = calcular_rendimiento_portafolio_total()
        # ...
```

**Opción B - Refactorización (No implementada):**
Reestructurar imports para evitar circularidad (más trabajo, no necesario por ahora)

### Resultado
✅ Imports dinámicos resuelven el problema
✅ Sin impacto en performance (import se ejecuta 1 vez por llamada)
✅ Código más modular y desacoplado

---

## 🐛 Problema 4: Timeout en `analizar_portfolio_completo()`

### Síntomas
- La herramienta `obtener_analisis_portfolio` tardaba >5 segundos
- Causaba timeouts del agente
- Usuario tenía que esperar mucho para respuestas simples

### Causa Raíz
`analizar_portfolio_completo()` ejecutaba demasiadas operaciones:
1. `calcular_rendimiento_portafolio_total()` (lento)
2. Cálculo de alertas
3. Cálculo de métricas de riesgo
4. Comparación con snapshots anteriores
5. Guardado de nuevo snapshot

### Solución Temporal
Implementar versión simplificada sin análisis completo:

```python
# Versión SIMPLIFICADA sin analizar_portfolio_completo()
total_valor = sum(c.get('valor_actual_inversion', 0) for c in portfolio_data)
total_invertido = sum(c.get('coste_total_inversion', 0) for c in portfolio_data)
rentabilidad = ((total_valor - total_invertido) / total_invertido * 100) if total_invertido > 0 else 0

respuesta = f"""💼 RESUMEN DEL PORTFOLIO

📊 Totales:
   • Valor actual: {total_valor:.2f}€
   • Inversión total: {total_invertido:.2f}€
   • Rentabilidad: {rentabilidad:+.2f}%

🪙 Activos ({len(portfolio_data)}):
"""
```

### Resultado Actual
✅ Respuesta en <1 segundo
✅ Datos esenciales disponibles (totales + top 5)
❌ Sin alertas de riesgo (pendiente)
❌ Sin métricas de diversificación (pendiente)

### Mejora Futura
Optimizar `analizar_portfolio_completo()` para ejecutar en <2 segundos y retornar a la versión completa.

---

## 🐛 Problema 5: Funciones Existentes No Usadas Correctamente

### Síntomas
- Error: `argument of type 'NoneType' is not iterable`
- Al intentar usar `obtener_portafolio()`

### Causa Raíz
Confusión entre funciones similares:
- `obtener_portafolio()` → Devuelve lista de símbolos: `['BTC', 'ETH', ...]`
- `calcular_rendimiento_portafolio_total()` → Devuelve datos completos: `[{simbolo: 'BTC', ...}, ...]`

**Código incorrecto:**
```python
portfolio_data = obtener_portafolio()  # Devuelve ['BTC', 'ETH']
analizar_portfolio_completo(portfolio_data)  # Espera [{...}, {...}] → ERROR
```

### Solución
Usar la función correcta:

```python
portfolio_data = calcular_rendimiento_portafolio_total()  # ✅ Devuelve datos completos
```

### Resultado
✅ La herramienta recibe los datos en el formato esperado
✅ Sin errores de tipo `NoneType`

---

## 📊 Resumen de Problemas y Soluciones

| # | Problema | Solución | Tiempo Invertido |
|---|----------|----------|------------------|
| 1 | Schema vacío | Campo dummy | ~1 hora |
| 2 | Max iterations | Aumentar de 5 a 10 | ~15 min |
| 3 | Circular imports | Import dinámico | ~30 min |
| 4 | Timeout análisis | Versión simplificada | ~45 min |
| 5 | Función incorrecta | Usar `calcular_rendimiento_portafolio_total()` | ~20 min |

**Tiempo total de debugging:** ~3 horas

---

## 🎓 Lecciones Aprendidas

### 1. LangChain Tools Requieren Schema Válido
Incluso si una herramienta no necesita parámetros, el schema de Pydantic debe tener al menos un campo.

### 2. Max Iterations Debe Ser Generoso
Para agentes que combinan múltiples herramientas, `max_iterations` debe ser al menos 2x el número de herramientas esperadas.

### 3. Imports Dinámicos Son Útiles
Cuando hay riesgo de circular dependencies, importar dentro de funciones es una solución rápida y efectiva.

### 4. Performance Importa en Herramientas
Si una herramienta tarda >2 segundos, causará problemas de UX. Optimizar o simplificar.

### 5. Documentar las Firmas de Funciones
Tener claro qué devuelve cada función (tipos, estructura) evita errores de integración.

---

## 🔧 Debugging Tips para Futuros Desarrolladores

### Problema: Herramienta No Se Ejecuta

**Checklist:**
- [ ] ¿El schema de Pydantic tiene al menos un campo?
- [ ] ¿La firma de `_run()` coincide con el schema?
- [ ] ¿Hay imports circulares? → Usar imports dinámicos
- [ ] ¿Aparece el nombre de la herramienta en logs de inicialización?

### Problema: Agent Stopped Due to Max Iterations

**Solución rápida:**
1. Contar cuántas herramientas se necesitan
2. Multiplicar por 2
3. Aumentar `max_iterations` a ese valor

### Problema: Timeout o Respuesta Lenta

**Checklist:**
- [ ] ¿Cuánto tarda cada herramienta? (añadir `logger.info` con timestamps)
- [ ] ¿Se puede cachear algún resultado?
- [ ] ¿Se puede simplificar la lógica?
- [ ] ¿Es necesario todo el cálculo o solo parte?

---

## 📝 Notas para Versiones Futuras

### Mejora Pendiente: Versión Completa de Portfolio

**Objetivo:** Volver a incluir alertas y métricas de `analizar_portfolio_completo()`

**Requisitos:**
1. Optimizar `calcular_rendimiento_portafolio_total()` (actualmente el cuello de botella)
2. Cachear precios actuales (se consultan múltiples veces)
3. Paralelizar cálculos independientes
4. Target: <2 segundos de ejecución total

---

**Última actualización:** 2025-12-20
**Autor:** Claude Code
