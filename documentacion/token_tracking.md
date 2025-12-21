# Guía: Rastreo de Tokens en Agentes de LangChain con Groq

## Introducción

Cuando trabajas con agentes de LangChain que usan modelos LLM (como Groq), es fundamental rastrear el uso de tokens para:

- 💰 **Controlar costes**: Cada token tiene un coste asociado
- 📊 **Optimizar prompts**: Identificar cuántos tokens consumen tus prompts
- 🔍 **Debugging**: Entender cuántas llamadas hace tu agente al LLM

## El Problema

Por defecto, LangChain **no devuelve automáticamente** información sobre tokens cuando usas agentes. Necesitas implementar un **Callback** personalizado para capturar esta información.

## Estructura de Respuestas en LangChain

### Anatomía de `LLMResult`

Cuando un LLM completa una llamada, LangChain crea un objeto `LLMResult` con la siguiente estructura:

```
LLMResult
├── generations: List[List[ChatGeneration]]  ← Lista de listas (importante!)
│   └── [0]: List[ChatGeneration]
│       └── [0]: ChatGeneration
│           └── message: AIMessage
│               ├── content: str
│               ├── response_metadata: Dict  ← AQUÍ ESTÁN LOS TOKENS (Groq)
│               │   └── token_usage: Dict
│               │       ├── prompt_tokens: int
│               │       ├── completion_tokens: int
│               │       └── total_tokens: int
│               └── usage_metadata: Dict  ← Alternativa en algunos proveedores
└── llm_output: Dict | None  ← Forma legacy (puede ser None)
```

### ⚠️ Punto Clave: Lista de Listas

**La trampa más común**: `response.generations` NO es una lista de `ChatGeneration`, sino una **lista de listas**.

```python
# ❌ INCORRECTO - Esto no funciona
for generation in response.generations:
    message = generation.message  # Error: list no tiene atributo 'message'

# ✅ CORRECTO - Necesitas iterar sobre dos niveles
for generation_list in response.generations:
    for generation in generation_list:
        message = generation.message
```

## Solución: Callback Personalizado

### Implementación Completa

```python
from langchain_core.callbacks import BaseCallbackHandler
from typing import Any, Dict

class TokenCounterCallback(BaseCallbackHandler):
    """Callback que cuenta tokens de todas las llamadas al LLM"""

    def __init__(self):
        super().__init__()
        self.total_tokens_entrada = 0
        self.total_tokens_salida = 0
        self.total_tokens_totales = 0

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """Captura los tokens cada vez que el LLM termina una llamada"""
        if response is None:
            return

        try:
            # Para ChatGroq, buscar en generations[0].message.response_metadata
            # NOTA: response.generations es una lista de listas de ChatGeneration
            if hasattr(response, 'generations') and response.generations:
                for generation_list in response.generations:
                    if isinstance(generation_list, list):
                        for generation in generation_list:
                            if hasattr(generation, 'message') and generation.message:
                                message = generation.message

                                # Buscar en response_metadata (forma principal en ChatGroq)
                                if hasattr(message, 'response_metadata') and message.response_metadata:
                                    metadata = message.response_metadata

                                    # Groq usa 'token_usage' en response_metadata
                                    if 'token_usage' in metadata:
                                        token_usage = metadata['token_usage']
                                        entrada = token_usage.get('prompt_tokens', 0)
                                        salida = token_usage.get('completion_tokens', 0)
                                        total = token_usage.get('total_tokens', entrada + salida)

                                        self.total_tokens_entrada += entrada
                                        self.total_tokens_salida += salida
                                        self.total_tokens_totales += total

                                        print(f"📊 Tokens: entrada={entrada}, salida={salida}, total={total}")
                                        return

                                # Backup: buscar en usage_metadata
                                if hasattr(message, 'usage_metadata') and message.usage_metadata:
                                    usage = message.usage_metadata
                                    entrada = usage.get('input_tokens', 0)
                                    salida = usage.get('output_tokens', 0)
                                    total = usage.get('total_tokens', entrada + salida)

                                    self.total_tokens_entrada += entrada
                                    self.total_tokens_salida += salida
                                    self.total_tokens_totales += total

                                    print(f"📊 Tokens: entrada={entrada}, salida={salida}, total={total}")
                                    return

            # Backup: buscar en llm_output (forma antigua)
            if hasattr(response, 'llm_output') and response.llm_output:
                if isinstance(response.llm_output, dict) and 'token_usage' in response.llm_output:
                    token_usage = response.llm_output['token_usage']
                    entrada = token_usage.get('prompt_tokens', 0)
                    salida = token_usage.get('completion_tokens', 0)
                    total = token_usage.get('total_tokens', entrada + salida)

                    self.total_tokens_entrada += entrada
                    self.total_tokens_salida += salida
                    self.total_tokens_totales += total

                    print(f"📊 Tokens: entrada={entrada}, salida={salida}, total={total}")
                    return

        except Exception as e:
            print(f"⚠️  Error capturando tokens: {str(e)}")

    def get_totals(self) -> Dict[str, int]:
        """Devuelve el total de tokens usados"""
        return {
            "tokens_entrada": self.total_tokens_entrada,
            "tokens_salida": self.total_tokens_salida,
            "tokens_total": self.total_tokens_totales if self.total_tokens_totales > 0
                           else self.total_tokens_entrada + self.total_tokens_salida
        }
```

### Uso del Callback con un Agente

```python
from langchain.agents import AgentExecutor
from langchain_groq import ChatGroq

# Crear el agente (ejemplo simplificado)
llm = ChatGroq(api_key="tu_api_key", model="llama-3.3-70b-versatile")
agente_executor = AgentExecutor(agent=agente, tools=herramientas)

# Crear el callback
token_counter = TokenCounterCallback()

# Ejecutar el agente con el callback
resultado = agente_executor.invoke(
    {"input": "¿Cuánto he invertido en Bitcoin?"},
    config={"callbacks": [token_counter]}
)

# Obtener totales
totales = token_counter.get_totals()
print(f"Total tokens entrada: {totales['tokens_entrada']}")
print(f"Total tokens salida: {totales['tokens_salida']}")
print(f"Total tokens: {totales['tokens_total']}")
```

## Ubicación de Tokens por Proveedor

Diferentes proveedores de LLM colocan los tokens en diferentes lugares:

| Proveedor | Ubicación Principal | Ubicación Alternativa |
|-----------|--------------------|-----------------------|
| **Groq** (ChatGroq) | `message.response_metadata['token_usage']` | `message.usage_metadata` |
| **OpenAI** | `llm_output['token_usage']` | `message.usage_metadata` |
| **Anthropic** | `message.usage_metadata` | `llm_output['usage']` |
| **Google** | `message.usage_metadata` | - |

### Estrategia de Fallback

El callback implementa una **estrategia de 3 niveles** para máxima compatibilidad:

1. **Nivel 1**: `response_metadata['token_usage']` (ChatGroq, algunos OpenAI)
2. **Nivel 2**: `usage_metadata` (Standard moderno)
3. **Nivel 3**: `llm_output['token_usage']` (Legacy, puede ser `None`)

## Cálculo de Costes

Una vez que tienes los tokens, puedes calcular el coste:

```python
# Tarifas de Groq (ejemplo para llama-3.3-70b-versatile, enero 2025)
COSTE_POR_MILLON_TOKENS_ENTRADA = 0.59  # USD
COSTE_POR_MILLON_TOKENS_SALIDA = 0.79   # USD
TASA_CAMBIO_USD_EUR = 0.92  # Ejemplo

def calcular_coste_euros(tokens_entrada: int, tokens_salida: int) -> float:
    """Calcula el coste aproximado en euros"""
    coste_entrada_usd = (tokens_entrada / 1_000_000) * COSTE_POR_MILLON_TOKENS_ENTRADA
    coste_salida_usd = (tokens_salida / 1_000_000) * COSTE_POR_MILLON_TOKENS_SALIDA
    coste_total_usd = coste_entrada_usd + coste_salida_usd
    return coste_total_usd * TASA_CAMBIO_USD_EUR

# Ejemplo
tokens_info = token_counter.get_totals()
coste = calcular_coste_euros(
    tokens_info['tokens_entrada'],
    tokens_info['tokens_salida']
)
print(f"Coste aproximado: €{coste:.6f}")
```

## Debugging: Encontrar Dónde Están los Tokens

Si el callback no funciona, usa esta versión de debug:

```python
def on_llm_end(self, response: Any, **kwargs: Any) -> None:
    """Versión debug para encontrar tokens"""
    print(f"🔍 Tipo: {type(response)}")
    print(f"🔍 Atributos: {dir(response)}")

    if hasattr(response, 'generations'):
        print(f"🔍 Generations: {len(response.generations)}")
        for i, gen_list in enumerate(response.generations):
            print(f"🔍 Generation[{i}]: {type(gen_list)}")
            if isinstance(gen_list, list):
                for j, gen in enumerate(gen_list):
                    print(f"🔍   [{i}][{j}]: {type(gen)}")
                    if hasattr(gen, 'message'):
                        msg = gen.message
                        print(f"🔍   Message attrs: {dir(msg)}")
                        if hasattr(msg, 'response_metadata'):
                            print(f"🔍   response_metadata: {msg.response_metadata}")
                        if hasattr(msg, 'usage_metadata'):
                            print(f"🔍   usage_metadata: {msg.usage_metadata}")

    if hasattr(response, 'llm_output'):
        print(f"🔍 llm_output: {response.llm_output}")
```

## Mejores Prácticas

### ✅ Hacer

- **Acumular tokens**: El callback acumula tokens de TODAS las llamadas al LLM durante la ejecución del agente
- **Usar fallbacks**: Implementar múltiples estrategias para diferentes proveedores
- **Validar antes de acceder**: Siempre usar `hasattr()` antes de acceder a atributos
- **Manejar None**: Los valores pueden ser `None`, manejar con `.get()` y valores por defecto

### ❌ Evitar

- **Asumir estructura simple**: No asumir que `generations` es una lista plana
- **Ignorar la iteración doble**: Siempre iterar sobre dos niveles en `generations`
- **No manejar excepciones**: Siempre usar try/except para evitar que el callback rompa el agente
- **Confiar en `llm_output`**: En versiones modernas puede ser `None`

## Ejemplo Completo: API Flask con Tracking

```python
from flask import Flask, request, jsonify
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent

app = Flask(__name__)

@app.route('/prompt', methods=['POST'])
def procesar_pregunta():
    data = request.get_json()
    pregunta = data.get('question', '')

    # Crear callback
    token_counter = TokenCounterCallback()

    # Ejecutar agente
    resultado = agente_executor.invoke(
        {"input": pregunta},
        config={"callbacks": [token_counter]}
    )

    # Obtener tokens
    tokens_info = token_counter.get_totals()

    # Calcular coste
    coste = calcular_coste_euros(
        tokens_info['tokens_entrada'],
        tokens_info['tokens_salida']
    )

    return jsonify({
        "success": True,
        "question": pregunta,
        "answer": resultado["output"],
        "tokens_entrada": tokens_info['tokens_entrada'],
        "tokens_salida": tokens_info['tokens_salida'],
        "tokens_total": tokens_info['tokens_total'],
        "coste_aprox_euros": round(coste, 6)
    })
```

## Troubleshooting

### Problema: Tokens siempre son 0

**Causa**: El callback no se está pasando correctamente al agente.

**Solución**:
```python
# ❌ Incorrecto
resultado = agente_executor.invoke({"input": pregunta})

# ✅ Correcto
resultado = agente_executor.invoke(
    {"input": pregunta},
    config={"callbacks": [token_counter]}  # ← Importante!
)
```

### Problema: `llm_output` es `None`

**Causa**: Versiones modernas de LangChain no usan `llm_output`.

**Solución**: Tu callback debe buscar en `response_metadata` o `usage_metadata` primero (que es lo que hace nuestra implementación).

### Problema: Error `'list' object has no attribute 'message'`

**Causa**: Estás iterando sobre `generations` sin iterar sobre las listas internas.

**Solución**: Ver sección "Punto Clave: Lista de Listas" arriba.

## Referencias

- [LangChain Callbacks Documentation](https://python.langchain.com/docs/modules/callbacks/)
- [Groq Pricing](https://groq.com/pricing/)
- [LangChain Agent Documentation](https://python.langchain.com/docs/modules/agents/)

## Changelog

- **2025-01**: Versión inicial con soporte para ChatGroq y estructura de doble lista