                                                                                                                                
                                                                                                                                
                                                                                                                                
                                                                                                                                # ANALISIS DE DATOS

## Tendencia en intervalos consecutivos

He definido una SQL que me devuelva para intervalo, si el precio sube o baja con relacion al intervalo anterior.

Despues partiendo de esa sql:

Ordenamos los intervalos cronológicamente para tener una secuencia clara de variaciones. Comparamos cada variación con la siguiente:

* Si ambas son positivas → Contamos como acierto.
* Si ambas son negativas → Contamos como acierto.
* Si cambian de signo → No es acierto.

Calculamos el porcentaje de acierto dividiendo los aciertos entre el total de intervalos evaluados.

### RESULTADOS

#### Para un intervalo de 3min y BTC

|total_intervalos|total_aciertos|porcentaje_acierto|
|----------------|--------------|------------------|
|1541|727|47.18|


#### Para un intervalo de 5min y BTC

|total_intervalos|total_aciertos|porcentaje_acierto|
|----------------|--------------|------------------|
|924|446|48.27|

#### 5min y ETH

|total_intervalos|total_aciertos|porcentaje_acierto|
|----------------|--------------|------------------|
|924|453|49.03|


#### 10min y BTC

|total_intervalos|total_aciertos|porcentaje_acierto|
|----------------|--------------|------------------|
|462|228|49.35|

## CONCLUSIONES

Todas las pruebas se mueven al rededor del 50%, no fiable para sacar una estrategía.

## Tendencia del tercer intervalos consecutivo

Vale, entiendo la idea. Queremos ver si, cuando dos intervalos consecutivos tienen la misma dirección (subida o bajada), hay una mayor probabilidad de que el tercero siga el mismo patrón.


|tendencia_1|tendencia_2|tendencia_3|frecuencia|probabilidad|
|-----------|-----------|-----------|----------|------------|
|BAJA|BAJA|SUBE|112|50.68|
|BAJA|BAJA|BAJA|109|49.32|
|BAJA|SUBE|BAJA|132|55.0|
|BAJA|SUBE|SUBE|108|45.0|
|SUBE|BAJA|SUBE|128|53.33|
|SUBE|BAJA|BAJA|112|46.67|
|SUBE|SUBE|SUBE|114|51.35|
|SUBE|SUBE|BAJA|108|48.65|

## strategia Propuesta: Cruce de Precio con Media Móvil Simple (SMA)

Una de las estrategias más fundamentales y ampliamente utilizadas en el análisis técnico es el cruce del precio con una Media Móvil Simple (SMA). Esta estrategia ayuda a identificar la dirección de la tendencia y posibles puntos de entrada o salida.

### Metodología:

**Recolección de Datos**: Asegúrate de que la tabla crypto_data en tu base de datos SQLite se actualice regularmente con los precios más recientes de las criptomonedas de interés. La función fetch_and_insert_data_last_30min() en main.py es clave para esto.

**Cálculo de la SMA**: Utilizaremos la función calculate_sma de analysis.py para obtener la Media Móvil Simple de una criptomoneda para un período determinado (ej. 20 períodos).

**Lógica de la Señal**:

* Señal de COMPRA: Se genera cuando el precio actual de la criptomoneda cruza por encima de su SMA. Esto sugiere que el impulso alcista está ganando fuerza y podría ser el inicio o la continuación de una tendencia ascendente.

* Señal de VENTA: Se genera cuando el precio actual de la criptomoneda cruza por debajo de su SMA. Esto indica que el impulso bajista está tomando el control y podría ser el inicio o la continuación de una tendencia descendente.

* Señal de MANTENER: Si no hay un cruce claro o si el precio ya está consolidado por encima o por debajo de la SMA sin un cruce reciente, la señal será "MANTENER".

### Interpretación de las Señales:

**COMPRA**: Podría ser un buen momento para abrir una posición larga (comprar) o aumentar una existente, esperando que el precio continúe subiendo.

**VENTA**: Podría ser un buen momento para cerrar una posición larga (vender) o evitar nuevas compras, esperando que el precio continúe bajando.

**MANTENER**: No hay una señal fuerte para tomar una acción inmediata; se recomienda mantener la posición actual y observar.
Implementación de la Estrategia

### Para implementar esta estrategia, te propongo los siguientes cambios en tu código:

1. Añadir una nueva función get_trading_signal en src/analysis.py: Esta función encapsulará la lógica de la estrategia de cruce de SMA.

2. Crear un nuevo endpoint /signal en src/api.py: Este endpoint permitirá consultar la señal de trading para una criptomoneda específica y un período de SMA.

## Estrategia Propuesta: "Reversión por Cambio Extremo Reciente"

Concepto: Las criptomonedas son conocidas por su alta volatilidad. Esta estrategia busca identificar movimientos de precio inusualmente grandes en un corto intervalo y apostar por una reversión inmediata. No se basa en tendencias a largo plazo, sino en la idea de que los movimientos extremos a menudo son seguidos por una corrección.

### Lógica de la Señal:

**Señal de COMPRA**: Si el precio de una criptomoneda cae drásticamente (por ejemplo, un 1% o más) en un período muy corto (ej. los últimos 5 o 15 minutos), podría estar "sobrevendida" momentáneamente. Esto generaría una señal de compra, esperando un rebote al alza.
**Señal de VENTA**: Si el precio de una criptomoneda sube drásticamente (por ejemplo, un 1% o más) en un período muy corto, podría estar "sobrecomprada" momentáneamente. Esto generaría una señal de venta, esperando un retroceso a la baja.
**Señal de MANTENER**: Si el cambio porcentual no supera el umbral establecido, no hay una señal clara para actuar.

### Parámetros Clave:

**timeframe_minutes**: El intervalo de tiempo sobre el cual se calcula el cambio porcentual (ej. 5, 10, 15 minutos).

**percentage_threshold**: El porcentaje de cambio que se considera "extremo" y que activa una señal (ej. 1.0 para 1%, 2.0 para 2%).

### ¿Por qué es "no tradicional"?

Esta estrategia se aleja de los indicadores técnicos clásicos (SMA, RSI, MACD) y se centra únicamente en la magnitud y velocidad del cambio de precio. Es una forma de trading de "contratendencia" muy a corto plazo, buscando capitalizar la inercia de los movimientos extremos.

## Combinar la estrategia de reversión por cambio extremo con Analisis de Volumen

Para combinar los cambios extremos recientes (como los que ya tienes implementados en tu estrategia) con el análisis de volumen, la idea es usar el volumen como un filtro de confirmación. Es decir, solo operar cuando ambos factores (el cambio de precio y el volumen) se alineen de manera que aumente la probabilidad de que el movimiento sea relevante y no un simple "fake out" o un movimiento sin mucha fuerza detrás.

Aquí te explico cómo podrías combinar ambas estrategias:

#### Cambio Extremo de Precio + Volumen Alto
Señal de COMPRA: Si el precio cae drásticamente (por ejemplo, un 1% o más en los últimos 5 o 15 minutos) y el volumen es considerablemente mayor que el volumen promedio de las últimas X horas (puedes definir el periodo de comparación, por ejemplo, las últimas 24 horas), esto podría ser una señal más fuerte de que el precio está "sobrevendido" momentáneamente y que hay un interés real de compra.

Ejemplo de Condición:

El precio cae un 1% o más en los últimos 5 minutos.

El volumen actual es al menos un 30% mayor que el volumen promedio de los últimos 30 minutos.

Si ambas condiciones se cumplen, podría ser una señal de compra.

Señal de VENTA: Si el precio sube drásticamente (por ejemplo, un 1% o más en los últimos 5 o 15 minutos) y el volumen es significativamente mayor que el promedio (lo que indica que el movimiento está respaldado por una gran cantidad de operaciones), puede ser una señal más confiable de que el precio está "sobrecomprado" y que podría haber un retroceso.

Ejemplo de Condición:

El precio sube un 1% o más en los últimos 5 minutos.

El volumen actual es al menos un 30% mayor que el volumen promedio de los últimos 30 minutos.

Si ambas condiciones se cumplen, podría ser una señal de venta.

#### Volumen Bajo + Cambio Extremo
Si tienes un cambio de precio significativo pero el volumen es bajo o igual al promedio, este movimiento podría no tener la fuerza suficiente para mantenerse. En este caso, podrías optar por no operar o esperar a una confirmación adicional.

Ejemplo de Condición:

El precio sube un 1% en los últimos 5 minutos.

El volumen actual es bajo o igual al volumen promedio de los últimos 30 minutos.

En este caso, puedes evitar la señal o esperar una confirmación de un aumento en el volumen antes de tomar acción.

#### Volumen en la Dirección Contraria (Divergencia)
También puedes usar el volumen para detectar divergencias, lo que puede ser útil para identificar señales falsas. Por ejemplo:

Si el precio está subiendo rápidamente, pero el volumen está disminuyendo, esto podría ser una señal de que el movimiento alcista no tiene la fuerza suficiente, lo que sugiere que podría haber un retroceso pronto.

Si el precio está cayendo rápidamente, pero el volumen también cae, esto podría indicar que no hay suficientes compradores para que el precio siga cayendo, lo que sugiere que el movimiento es débil y podría ser un buen momento para comprar.

#### Establecer umbrales de volumen
El volumen puede no ser siempre un indicador obvio, por lo que es útil establecer umbrales específicos de volumen para tus operaciones. Algunas opciones son:

Volumen medio: Comparar el volumen actual con el volumen promedio de los últimos 5, 15, 30 minutos o incluso 1 día.

Rango del volumen: Establecer un porcentaje mínimo de aumento de volumen, como un 20-30% más alto que el promedio.

#### Filtrar señales con volumen
Una forma de aplicar el volumen de manera efectiva es filtrar tus señales de compra y venta solo cuando el volumen sea significativamente alto, como un indicador de que el movimiento es respaldado por una fuerte participación en el mercado.

Si el cambio porcentual en el precio es de más del 1%, pero el volumen es bajo, puedes optar por no operar o esperar una confirmación de volumen alto antes de realizar la operación.

Si el volumen es alto, esto refuerza la validez de la señal de compra o venta.

#### Ejemplo de la Estrategia Combinada

**Señal de COMPRA:**

El precio ha caído un 1% o más en los últimos 5 minutos.

El volumen actual es al menos un 30% mayor que el volumen promedio de los últimos 30 minutos.

Si ambas condiciones se cumplen, compra esperando un rebote.

**Señal de VENTA:**

El precio ha subido un 1% o más en los últimos 5 minutos.

El volumen actual es al menos un 30% mayor que el volumen promedio de los últimos 30 minutos.

Si ambas condiciones se cumplen, vende esperando una corrección.

**No actuar si el volumen es bajo:**

Si el volumen es bajo en un movimiento importante del precio (sube o baja un 1% o más), espera a que el volumen aumente antes de tomar una acción.

#### Resumen de la Lógica:

Precio: Cambios extremos en un corto periodo de tiempo.

Volumen: Confirmación de que el movimiento está respaldado por un aumento en las transacciones.

Sin volumen o bajo volumen: Filtrar señales o esperar una confirmación.

Este enfoque hace que tu estrategia sea más robusta, ya que el volumen agrega una capa adicional de validación a las señales generadas por los cambios extremos de precio.

## BackTesting. Cambios Extremo + Volumen Alto

Se ha creado un proceso para probar la técnica de cambio extremo + Volumen Alto

El test devuelve un JSON. Cuyos campos son:

Este JSON es el resumen de una simulación de trading (un "backtest") para ver cómo se habría comportado una estrategia específica con datos históricos.

### Resumen General

La simulación se ejecutó para el Bitcoin (BTC) durante el período del 1 al 10 de noviembre de 2025, comenzando con un capital de 10,000€.

El resultado principal es que la estrategia perdió un 1.17% de la inversión, terminando con 9,882.60€. Aunque es una pérdida, fue un resultado mejor que si simplemente hubieras comprado Bitcoin el primer día y lo hubieras mantenido, ya que en ese caso la pérdida habría sido del 4.62%.

### Desglose de los Campos del JSON

Aquí te detallo cada campo para que lo entiendas mejor:

**capital_inicial**: 10000

Es la cantidad de dinero con la que empezó la simulación.

**valor_final_portafolio**: 9882.6

Es el dinero que quedó al final del período de prueba.

**retorno_total_abs**: -117.4

La ganancia o pérdida neta en euros. En este caso, una pérdida de 117.40€.

**retorno_total_pct**: -1.17

La rentabilidad total como porcentaje sobre el capital inicial. Aquí, una pérdida del 1.17%.

**retorno_buy_and_hold_pct**: -4.62

Este es un dato muy importante para comparar. Indica la rentabilidad que habrías tenido si simplemente hubieras comprado BTC el primer día y vendido el último, sin hacer más operaciones. En este caso, habrías perdido un 4.62%.
Conclusión clave: Tu estrategia, aunque perdió dinero, fue más efectiva que no hacer nada, ya que limitó las pérdidas.

**estrategia**: "obtener_senal_cambio_extremo"

El nombre de la función de Python que contiene la lógica de trading que se probó.

**parametros_estrategia**:

Estos son los "ajustes" con los que funcionó tu estrategia:

* **intervalo_minutos**: 15: La estrategia analizaba cambios de precio en ventanas de 15 minutos.

* **intervalo_ventana_volumen_minutos**: 30: 
Qué es: Define la duración de las "ventanas" de tiempo que se usan para medir el volumen.
En tu caso: La estrategia mide el volumen en bloques de 30 minutos.

* **num_ventanas_historicas_volumen**: 5: 
Qué es: El número de bloques de 30 minutos que se usarán para calcular un "volumen promedio histórico".
En tu caso: Se toman 5 bloques de 30 minutos del pasado (un total de 2.5 horas) para establecer una media de volumen normal.

* **umbral_porcentual**: 1: Se activaba una señal si el precio cambiaba más de un 1% en esos 15 minutos.

* **confirmar_con_volumen**: true: La señal de precio no era suficiente; necesitaba ser confirmada por un aumento en el volumen de operaciones.

* **umbral_porcentual_volumen**: 30: El volumen debía aumentar al menos un 30% por encima de su media reciente para confirmar la señal.

**numero_operaciones**: 8

La estrategia realizó un total de 8 operaciones (4 de compra y 4 de venta) durante los 10 días.

**operaciones: [...]**

Es el listado detallado de cada una de las 8 operaciones que se ejecutaron, con la fecha, el tipo (compra/venta), el precio y la cantidad. Se puede ver que la estrategia compraba y vendía de forma activa, probablemente intentando aprovechar pequeñas fluctuaciones.
En Resumen
La estrategia obtener_senal_cambio_extremo, con los parámetros que usaste, fue capaz de reducir las pérdidas en un mercado bajista para BTC en ese período. Perdió solo un 1.17% frente al 4.62% que habría perdido el mercado. Esto sugiere que la lógica de la estrategia tiene potencial para gestionar el riesgo, aunque en este caso concreto no llegó a generar beneficios.

NOTAS

Podrías experimentar cambiando los parametros_estrategia (por ejemplo, un umbral_porcentual más alto o más bajo) para ver si puedes mejorar el resultado y conseguir una rentabilidad positiva en el mismo período.

---

## Presión Compradora vs Vendedora (OBV Simplificado)

### Concepto

El volumen total nos dice **cuánto** se ha operado, pero no **quién domina** el mercado. La presión compradora/vendedora nos ayuda a entender si el volumen está impulsando el precio hacia arriba o hacia abajo.

### Fundamento Técnico

#### OHLC (Open, High, Low, Close)

Las velas de trading tienen 4 componentes:
- **Open**: Precio de apertura
- **High**: Precio máximo
- **Low**: Precio mínimo
- **Close**: Precio de cierre

Actualmente solo guardamos el precio de **cierre** de cada vela de 1 minuto.

#### OBV (On-Balance Volume)

El OBV es un indicador clásico que acumula volumen según la dirección del precio:
- Si el precio **sube** → el volumen se considera "comprador"
- Si el precio **baja** → el volumen se considera "vendedor"

### Implementación Simplificada

Al no tener OHLC completo, usamos una versión simplificada basada en el precio de cierre:

```
Para cada minuto del período analizado:
    Si precio_actual > precio_anterior:
        → volumen_compra += volumen_minuto
    Si precio_actual < precio_anterior:
        → volumen_venta += volumen_minuto

presión_compradora = volumen_compra / (volumen_compra + volumen_venta) × 100
```

### Ejemplo Práctico

| Minuto | Precio Cierre | Volumen | Movimiento | Acumulado |
|:------:|:-------------:|:-------:|:----------:|:---------:|
| 1 | 81,900 | 2.5 BTC | - | - |
| 2 | 81,920 | 1.8 BTC | SUBIÓ | compra += 1.8 |
| 3 | 81,915 | 3.2 BTC | BAJÓ | venta += 3.2 |
| 4 | 81,930 | 2.1 BTC | SUBIÓ | compra += 2.1 |
| 5 | 81,925 | 1.5 BTC | BAJÓ | venta += 1.5 |

**Resultado:**
- Volumen compra: 3.9 BTC (45%)
- Volumen venta: 4.7 BTC (55%)
- **Presión compradora: 45%** (dominio vendedor)

### Interpretación

| Presión Compradora | Significado |
|:------------------:|-------------|
| 70-100% | Dominio comprador fuerte |
| 50-70% | Ligera presión compradora |
| 30-50% | Ligera presión vendedora |
| 0-30% | Dominio vendedor fuerte |

### Tabla de Decisiones: Señal + Presión

| Señal Precio | Presión Compradora | Presión Vendedora | Interpretación | Acción |
|:------------:|:------------------:|:-----------------:|----------------|:------:|
| **COMPRA** | 70-100% | 0-30% | Caída con fuerte volumen comprador. Rebote muy probable. | COMPRAR |
| **COMPRA** | 50-70% | 30-50% | Caída con ligera presión compradora. Rebote posible. | COMPRAR (cautela) |
| **COMPRA** | 30-50% | 50-70% | Caída con ligera presión vendedora. Señal débil. | ESPERAR |
| **COMPRA** | 0-30% | 70-100% | Caída con fuerte volumen vendedor. Puede seguir cayendo. | NO COMPRAR |
| **VENTA** | 0-30% | 70-100% | Subida con fuerte volumen vendedor. Corrección probable. | VENDER |
| **VENTA** | 30-50% | 50-70% | Subida con ligera presión vendedora. Corrección posible. | VENDER (cautela) |
| **VENTA** | 50-70% | 30-50% | Subida con ligera presión compradora. Rally puede continuar. | ESPERAR |
| **VENTA** | 70-100% | 0-30% | Subida con fuerte volumen comprador. Rally genuino. | NO VENDER |
| **MANTENER** | 50-70% | 30-50% | Mercado lateral con ligera presión compradora. | Posible subida |
| **MANTENER** | 30-50% | 50-70% | Mercado lateral con ligera presión vendedora. | Posible bajada |

### Tabla Resumen Simplificada

| Señal | Presión Compradora | Resultado |
|:-----:|:------------------:|:---------:|
| COMPRA | Alta (>50%) | Confirma COMPRA |
| COMPRA | Baja (<50%) | Rechaza COMPRA |
| VENTA | Alta (>50%) | Rechaza VENTA |
| VENTA | Baja (<50%) | Confirma VENTA |

### Regla de Oro

> **"La señal de precio te dice QUÉ pasó. La presión te dice QUIÉN lo hizo."**

- Precio bajó + más compradores → **Rebote probable**
- Precio bajó + más vendedores → **Sigue cayendo**
- Precio subió + más compradores → **Rally genuino**
- Precio subió + más vendedores → **Corrección probable**

### Casos de Uso: Trampas de Mercado

Este indicador ayuda a detectar **trampas (traps)**:

**Bull Trap (Trampa alcista):**
- Precio sube bruscamente
- Pero presión compradora baja (<40%)
- Muchos vendedores aprovechando para salir
- **Acción:** No comprar, posible corrección

**Bear Trap (Trampa bajista):**
- Precio cae bruscamente
- Pero presión vendedora baja (<40%)
- Muchos compradores acumulando
- **Acción:** Comprar, posible rebote

### Limitaciones

- Es una **estimación**, no datos reales de órdenes de compra/venta
- Menos preciso que usar `takerBuyBaseAssetVolume` de Binance
- Puede dar falsos positivos en mercados muy laterales
- Funciona mejor con ventanas de tiempo más largas (30-60 min)

### Mejora Futura: OHLC Completo

Para un análisis más preciso, se podría:
1. Guardar OHLC completo en la BD (open, high, low, close)
2. Analizar velas: alcistas (close > open) vs bajistas (close < open)
3. Usar el cuerpo de la vela para ponderar la fuerza del movimiento