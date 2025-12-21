                           ┌────────────────────────────┐
                           │         api.py             │
                           │   (tu servidor Flask)      │
                           └─────────────┬──────────────┘
                                         │
                                         │ POST /prompt
                                         ▼
                   ┌──────────────────────────────────────────┐
                   │   agente_kryptonite.preguntar(pregunta)  │
                   └───────────────────┬──────────────────────┘
                                       │
                                       │ Llama a .invoke()
                                       ▼
              ┌──────────────────────────────────────────────┐
              │        AgentExecutor.invoke()                │
              │  (mientras el agente piensa y actúa)         │
              └──────────────────────┬───────────────────────┘
                                     │
                          Construye contexto inicial:
                                     │
                                     ▼
                    ┌────────────────────────────────┐
                    │   PROMPT del agente            │
                    │  + memoria (historial)         │
                    │  + pregunta del usuario        │
                    │  + agent_scratchpad vacío     │
                    └──────────────────┬─────────────┘
                                       │
                                       │
                                       ▼
                             LLM (Groq ChatGroq)
                       decide el siguiente paso
                                       │
                                       │
                                       ▼
           ┌─────────────────────────────────────────────────┐
           │ ¿El LLM pide usar una herramienta?              │
           └──────┬──────────────────────────────────────────┘
                  │ SÍ
                  ▼
    ┌─────────────────────────────────────┐
    │  mcp_sqlite_tools.py               │
    │  (lista de herramientas MCP)       │
    ├──────────────────────┬─────────────┤
    │ listar_tablas        │             │
    │ obtener_esquema      │  -> AgentExecutor ejecuta
    │ consultar_base_sql   │             │
    │ obtener_datos_tabla  │             │
    └───────────────┬──────┴────────────┘
                    │ (resultado)
                    ▼
         Añadir resultado al agent_scratchpad
                    │
                    ▼
          Volver a llamar al LLM con:
          - pregunta
          - memoria
          - scratchpad actualizado
                    │
                    ▼
          Ciclo se repite (hasta 5 veces)
                    │
                    ▼
      ┌────────────────────────────────────────────┐
      │ El LLM decide que ya tiene la respuesta    │
      │ y NO llama herramientas                    │
      └──────────────────────────┬─────────────────┘
                                 │
                                 ▼
                   AgentExecutor genera OUTPUT final
                                 │
                                 ▼
                 agente_kryptonite.preguntar() devuelve texto
                                 │
                                 ▼
                        api.py responde JSON


Vale, vamos a dejar de lado explicaciones “de manual” y te lo cuento **con tus propios archivos**, como si estuviéramos mirando el motor de tu coche pieza por pieza.

Aquí tienes **el enfoque que te falta** para que lo veas claro, sin teoría abstracta.

---

# 🔥 **Tu agente LangChain funciona así: pieza por pieza**

En tu proyecto intervienen **3 archivos**:

1. **`grog_agente.py`** → construye el agente y lo deja preparado.
2. **`mcp_sqlite_tools.py`** → define las herramientas que el agente puede usar.
3. **`api.py`** → crea *una sola instancia* del agente y la usa cuando llega una pregunta.

Vamos paso a paso.

---

# 🧩 1. `mcp_sqlite_tools.py`: las herramientas

Este archivo define **las capacidades reales del agente**.

Cada clase es una herramienta:

* `listar_tablas_base_de_datos`
* `obtener_esquema_tabla`
* `consultar_base_de_datos`
* `obtener_datos_tabla`

Cada herramienta NO piensa.
SOLO ejecuta el código Python que le toca: llamar a tu servidor MCP SQLite.

👉 Esto es importante: **las herramientas NO deciden cuándo se usan**.
Eso lo decide el LLM dentro del agente.

---

# 🧩 2. `grog_agente.py`: construcción del agente

Aquí está el núcleo de todo.

Cuando llamas a:

```python
crear_agente_kryptonite(...)
```

ocurre esto:

### ✔️ 1. Se crea un LLM Groq

Tu agente usa este LLM para generar cada paso de razonamiento.

### ✔️ 2. Se cargan tus herramientas MCP

```python
self.herramientas = obtener_herramientas_mcp()
```

Son las mismas cuatro herramientas de antes.

### ✔️ 3. Se crea la plantilla del prompt

Tu prompt explica al modelo:

* Qué puede hacer.
* Qué herramientas existen.
* Cómo debe usarlas.
* Qué pasos seguir.

Y muy importante:

```python
MessagesPlaceholder("chat_history")  
MessagesPlaceholder("agent_scratchpad")
```

* **chat_history** → memoria de la conversación.
* **agent_scratchpad** → donde se acumulan los *pensamientos intermedios* y las llamadas a herramientas.

### ✔️ 4. Se construye el agente con `create_tool_calling_agent()`

Este es el cerebro:

* Interpreta la pregunta.
* Decide si necesita herramientas.
* Decide qué herramienta usar.
* Decide qué parámetros pasarle.
* Recoge el resultado.
* Vuelve a razonar.
* Repite hasta que ya tiene respuesta final.

**Aquí no ejecuta nada**, solo crea la lógica del agente.

### ✔️ 5. Se crea el `AgentExecutor`

```python
self.ejecutor_agente = AgentExecutor(...)
```

Este sí **ejecuta** todo el ciclo cada vez que llamas a `.invoke()`.

Tiene:

* las herramientas
* la memoria
* el prompt
* el LLM
* el límite de iteraciones

---

# 🧩 3. El detalle clave: `AgentExecutor.invoke()`

Aquí es donde “corre el motor”.

Cuando en la API haces:

```python
respuesta = agente_kryptonite.preguntar("¿Cuánto invertí en BTC?")
```

tu método hace:

```python
self.ejecutor_agente.invoke({"input": pregunta})
```

Y aquí empieza **el ciclo completo**:

---

# 🚀 **Cómo funciona el ciclo REAL dentro de `AgentExecutor`**

Imagínate que pregunta:

**"¿Cuánto invertí en BTC?"**

### 1) El ejecutor construye el mensaje inicial:

Combina:

* tu prompt del sistema
* la memoria (si la hay)
* la pregunta del usuario
* el agent_scratchpad vacío

### 2) El LLM genera un pensamiento tipo:

«Necesito mirar los datos en la tabla de inversiones»

Y produce algo así (internamente):

```json
{
  "tool": "listar_tablas_base_de_datos",
  "args": {}
}
```

### 3) AgentExecutor detecta que el LLM quiere usar una herramienta

→ Llama a esa herramienta Python

```python
resultado = HerramientaListarTablas()._run()
```

### 4) Añade el resultado al `agent_scratchpad`

(esto es lo que hace posible el siguiente paso)

### 5) Vuelve a llamar al LLLM

Ahora el modelo ve:

* pregunta inicial
* el resultado de la herramienta
* y el scratchpad actualizado

Y decide la siguiente acción.

### 6) Hace más llamadas a herramientas

Por ejemplo:

1. obtener_esquema_tabla("inversiones")
2. consultar_base_de_datos("SELECT * FROM inversiones WHERE simbolo = 'BTC'")

Siempre en bucle.

### 7) Cuando el LLM decide que ya tiene toda la info

Devuelve un mensaje final sin herramienta:

```json
{
  "final_answer": "Invertiste 250€ en BTC..."
}
```

---

# ⭐ **La clave que te faltaba:**

👉 **El agente NO sabe nada de tu base de datos.**
👉 **Solo sabe que existen herramientas** que *puede usar cuando quiera*.
👉 **AgentExecutor es quien mira cada mensaje y ejecuta las herramientas.**

Tú sólo inicias el agente una vez.
Pero **cada pregunta dispara un nuevo ciclo de razonamiento y ejecución**.

---

# 👀 Resumen simple estilo “mecánico”:

### **mcp_sqlite_tools.py**

➡️ Son los martillos, destornilladores y llaves.

### **grog_agente.py**

➡️ Construye el robot mecánico y lo programa para que USE esas herramientas.

### **AgentExecutor**

➡️ Es el motor que hace que el robot trabaje paso a paso.

### **.invoke()**

➡️ Es darle al botón: *¡haz tu trabajo!*.

### **api.py**

➡️ Es el sitio donde arrancas el robot una vez y luego le pasas las órdenes (preguntas).

---

# Si quieres, te hago ahora un **diagrama visual paso a paso** o un **ejemplo de ejecución real** con logs simulados.

¿Quieres un esquema visual o un ejemplo?

