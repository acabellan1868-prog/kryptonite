# KRIPTONITE

# Kryptonite: Tu aliado en el mundo cripto

Kryptonite es una app hecha para simplificar las decisiones de inversión en criptomonedas. Sabemos que el mundo de las cripto puede ser un lío y todo parece un riesgo, pero nuestra idea es hacer que tomes decisiones con cabeza, sin andar a ciegas. Te damos las herramientas necesarias para que no te sientas perdido y puedas mover tu dinero de forma más segura. 💡

El nombre viene de algo simbólico. Si alguna vez has leído cómics, sabes que la kryptonita es la debilidad de Superman. Pues aquí, Kryptonite es lo contrario: nuestra app es tu punto fuerte en un mercado que a veces puede parecer una montaña rusa. Queremos que, con nuestra ayuda, tengas el control, sin que te tiemble el pulso. 💪

La idea es que sea fácil de usar, sin complicaciones. Nada de interfaces llenas de botones que no sabes qué hacen. Solo lo necesario para que puedas invertir de manera inteligente, tomar decisiones basadas en datos y no dejarte llevar por el pánico. 🚀


# Plan de Herramientas y Tecnologías para "Kryptonite"

## Lenguaje de Programación

El lenguaje principal que utilizaremos será **Python** 🐍. Es ideal para manejar grandes volúmenes de datos y realizar análisis complejos de manera eficiente. Además, su sintaxis clara y la enorme cantidad de librerías disponibles lo convierten en una opción perfecta para este proyecto.

## Entorno de Desarrollo

Se usará **Jupyter Lab** 💻 como entorno de desarrollo. Es excelente para trabajar con datos, visualizar resultados rápidamente y realizar experimentos. Su integración con Python y las herramientas de visualización lo hacen muy adecuado para este tipo de proyectos.

## API de Criptomonedas

Para interactuar con los mercados de criptomonedas, consideramos dos opciones principales: **Binance** y **Kraken**. Ambas tienen buenas APIs que permiten obtener datos de mercado en tiempo real, ejecutar operaciones y consultar balances. A la hora de elegir, es importante tener en cuenta lo siguiente:

- **Variedad de criptomonedas**: Binance ofrece una gama más amplia de criptomonedas, lo que puede ser útil si deseas diversificar las opciones de inversión en la app. 💎
- **Facilidad de uso**: Kraken es conocida por su seguridad y su interfaz amigable. Puede ser más adecuada si la prioridad es la seguridad sobre la variedad de criptos. 🔐
- **Tarifas**: Asegúrate de revisar las tarifas que cada plataforma cobra por operaciones y transacciones, ya que puede afectar la rentabilidad. 💸

## Librerías de Python

Las siguientes librerías nos serán de gran ayuda:

- **Pandas** 📊 y **NumPy** 🔢: Son esenciales para el manejo y procesamiento de datos. Nos ayudarán a analizar tendencias, patrones y tomar decisiones basadas en datos históricos y en tiempo real.
- **Matplotlib** 📈 / **Plotly** 📉: Para las visualizaciones. Queremos que el usuario pueda ver gráficos claros y fáciles de entender sobre el rendimiento de sus inversiones.
- **Requests** 🌐: Para hacer peticiones a las APIs y obtener datos de los mercados.
- **ccxt** 🔗: Nos permitirá interactuar con varias plataformas de criptomonedas de manera sencilla y estandarizada.

## Base de Datos

La base de datos elegida será **SQLite** 🗃️. Es una opción ligera, fácil de implementar y adecuada para proyectos que no requieren una infraestructura de base de datos compleja. Al ser un sistema de bases de datos relacional, facilita la organización de la información de manera estructurada, permitiendo almacenar transacciones, históricos de precios y otras métricas relevantes.

## Comunicación y Alertas

La integración con **Telegram** 📱 se usará para enviar alertas y actualizaciones a los usuarios sobre sus inversiones. Algunas ideas a tener en cuenta para esta parte del proyecto:

- **Notificaciones personalizadas** 🔔: Los usuarios deben poder elegir qué tipo de alertas quieren recibir (subidas o bajadas de precios, nuevas oportunidades de inversión, etc.).
- **Comandos fáciles de usar** 🖥️: Comandos simples como **/alertas**, **/inversiones**, **/estado** pueden ser útiles para que los usuarios interactúen con el bot de manera directa y fácil.
- **Frecuencia de notificaciones** 🕑: Es importante no abrumar al usuario con demasiadas notificaciones, por lo que el sistema debe ser flexible para permitir personalización en cuanto a la frecuencia de las alertas.

## Ideas Adicionales a Tener en Cuenta

1. **Simplicidad y accesibilidad** 🎯: El objetivo es hacer la aplicación lo más intuitiva posible, tanto para novatos como para usuarios con experiencia. Las interfaces deben ser limpias y fáciles de navegar.

2. **Seguridad** 🔒: Las criptomonedas son un campo propenso a fraudes y robos. Es importante asegurarse de que tanto las transacciones como el manejo de claves API se realicen de manera segura. Usar autenticación de dos factores (2FA) y encriptar las comunicaciones puede ser clave.

3. **Análisis y predicción** 🔮: A medida que avances en el proyecto, podrías integrar modelos de predicción utilizando machine learning para dar recomendaciones personalizadas a los usuarios basadas en el análisis de datos históricos.

4. **Escalabilidad** 📈: Aunque el proyecto empiece pequeño, asegúrate de que la arquitectura esté preparada para crecer en el futuro. Piensa en cómo agregar más criptomonedas, integrar nuevas APIs o implementar más funcionalidades a medida que el proyecto evolucione.

5. **Interfaz amigable para el usuario** 👨‍💻: Una parte importante del proyecto es ofrecer una experiencia de usuario agradable. Considera el diseño de la interfaz, la facilidad de navegación y la claridad de la información. Piensa en cómo puedes simplificar la toma de decisiones para los usuarios.

# PARTE TÉCNICA

# Conexión con Visual Studio

La conexión con visual estudio lo he hecho a través de SSH:

Ctrl+Shift+P
Remote-SSH: Connect to Host
antonio@192.168.31.131
Navegamos hasta donde están el directorio de Jupyter- >/mnt/datos/jupyter/kryptonite
Hay tengo toda la estructura del proyecto

# Estructura del Proyecto Kryptonite

La estructura del proyecto **Kryptonite** está organizada de la siguiente manera:

```plaintext
Kryptonite/
│
├── data/                   # Carpeta para datos y archivos generados
│   ├── kryptonite.db       # Base de datos SQLite con los datos de las criptomonedas
│   └── ...                 # Otros archivos de datos
|
├── documentacion/                   # Carpeta de documentación
│   ├── kryptoniteDoc.md       # MD con datos del proyecto, apuntes, notas, ...
│   └── ...                 # Otros archivos de datos
|
├── logs/                   # Carpeta para datos y archivos generados
│   ├── kryptonite.log       # Base de datos SQLite con los datos de las criptomonedas
│   └── ...                  # Otros archivos de datos
|
├── notebooks/               # Notebooks de Jupyter para pruebas y experimentación
│   ├── 01_testing_db.ipynb # Primer cuaderno de pruebas (por ejemplo, para la base de datos)
│   ├── kriptonite.ipynb    # Cuaderno principal del proyecto
│   └── ...                 # Otros cuadernos Jupyter
│
├── src/                    # Código fuente del proyecto
│   ├── __init__.py         # Archivo de inicialización de la carpeta
│   ├── database.py         # Funciones relacionadas con la base de datos
│   ├── analysis.py         # Funciones de análisis técnico
│   ├── alerts.py           # Funciones para gestionar alertas y notificaciones
│   └── ...                 # Otros archivos Python a medida que se añadan más funcionalidades
│
├── requirements.txt        # Archivo con las dependencias del proyecto
├── README.md               # Información general sobre el proyecto
└── .gitignore              # Archivo para ignorar archivos innecesarios en Git
```

## **SQLite en Jupyter Lab para Kryptonite**

### **1️⃣ Conceptos clave de SQLite**
- **No necesita servidor**: Es solo un archivo `.db` que almacena toda la información.
- **Fácil integración**: Puedes usarlo con Python sin configuraciones complicadas.
- **Consultas SQL estándar**: Se usa con lenguaje SQL como cualquier otra base de datos relacional.

---

### **2️⃣ Instalación (opcional)**
SQLite viene integrado con Python, pero si necesitas herramientas para gestionarlo visualmente, puedes instalar **DB Browser for SQLite** (opcional pero útil):

- 📥 [Descargar DB Browser](https://sqlitebrowser.org/) para visualizar la base de datos.

---

### **3️⃣ Creando y conectando SQLite en Jupyter Lab**
En Jupyter, puedes manejar SQLite con `sqlite3`. Aquí tienes el flujo básico:

```python
import sqlite3

# Conectar (o crear) la base de datos
conn = sqlite3.connect("kryptonite.db")

# Crear un cursor para ejecutar consultas SQL
cursor = conn.cursor()

# Crear una tabla de ejemplo (si no existe)
cursor.execute("""
CREATE TABLE IF NOT EXISTS transacciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    moneda TEXT,
    cantidad REAL,
    precio REAL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()
```

🔹 Esto crea la base de datos **kryptonite.db** y una tabla llamada **transacciones** para guardar operaciones de compra/venta.

---

### **4️⃣ Insertando datos**
Una vez que la tabla está lista, podemos insertar datos:

```python
conn = sqlite3.connect("kryptonite.db")
cursor = conn.cursor()

cursor.execute("""
INSERT INTO transacciones (moneda, cantidad, precio) 
VALUES ('BTC', 0.01, 45000)
""")

conn.commit()
conn.close()
```

---

### **5️⃣ Consultando datos**
Para leer los datos guardados:

```python
conn = sqlite3.connect("kryptonite.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM transacciones")
resultados = cursor.fetchall()  # Obtener todos los registros

for row in resultados:
    print(row)  # Muestra cada transacción

conn.close()
```

---

### **6️⃣ Integración con Pandas**
Como usarás **Pandas**, puedes cargar la base de datos en un DataFrame fácilmente:

```python
import pandas as pd

conn = sqlite3.connect("kryptonite.db")
df = pd.read_sql_query("SELECT * FROM transacciones", conn)
conn.close()

print(df)  # Muestra la tabla como un DataFrame
```

Esto te permitirá hacer análisis y gráficos directamente desde **Pandas**.

---

## **¿Qué sigue?**
Ahora que ya tienes lo básico, podemos definir:
✅ **Estructura de la base de datos** (qué tablas necesitas).  
✅ **Qué datos guardar** (transacciones, precios históricos, etc.).  
✅ **Cómo sincronizar SQLite con los datos de la API**.  

¿Quieres empezar por definir la estructura de la base de datos o necesitas más detalles de cómo integrarlo en Kryptonite? 🚀

## Estructura de la Base de Datos

La base de datos se estructura para almacenar los datos de las criptomonedas durante el último año. A continuación se detallan las tablas que forman la base de datos y sus campos.

### Tabla: `crypto_data`
| Campo       | Tipo de dato   | Descripción                                           |
|-------------|----------------|-------------------------------------------------------|
| `timestamp` | `INTEGER`      | Timestamp de la lectura (formato Unix, en segundos).  |
| `symbol`    | `TEXT`         | Símbolo de la criptomoneda (por ejemplo, BTC, ETH).   |
| `price`     | `REAL`         | Precio de la criptomoneda en el momento de la lectura.|
| `volume`    | `REAL`         | Volumen de transacciones en el momento de la lectura. |
| `market_cap`| `REAL`         | Capitalización de mercado de la criptomoneda.         |

### Tabla: `cryptos`
| Campo        | Tipo de dato   | Descripción                                               |
|--------------|----------------|-----------------------------------------------------------|
| `symbol`     | `TEXT`         | Símbolo de la criptomoneda (por ejemplo, BTC, ETH).       |
| `name`       | `TEXT`         | Nombre de la criptomoneda (por ejemplo, Bitcoin, Ethereum). |
| `slug`       | `TEXT`         | Slug o identificador en minúsculas (por ejemplo, bitcoin, ethereum). |
| `is_favorite`| `INT`          | 1 si es favorito y 0 si no lo es |
| `is_porfolio`| `INT`          | 1 si esta en mi porfolio y 0 si no lo está |
| `note`       | `TEXT`         | Poder incluir alguna nota sobre la criptomoneda |


### Tabla: `alerts`
| Campo         | Tipo de dato   | Descripción                                                 |
|---------------|----------------|-------------------------------------------------------------|
| `id`          | `INTEGER`      | Identificador único de la alerta.                           |
| `crypto_id`   | `INTEGER`      | Referencia al `id` de la tabla `cryptos`.                   |
| `trigger_price`| `REAL`         | Precio al que se activa la alerta.                          |
| `alert_type`  | `TEXT`         | Tipo de alerta (por ejemplo, "precio supera" o "precio baja"). |
| `enabled`     | `INTEGER`      | Estado de la alerta (0 = deshabilitada, 1 = habilitada).     |

### Tabla: `users`
| Campo         | Tipo de dato   | Descripción                                                 |
|---------------|----------------|-------------------------------------------------------------|
| `id`          | `INTEGER`      | Identificador único del usuario.                            |
| `username`    | `TEXT`         | Nombre de usuario del cliente.                              |
| `email`       | `TEXT`         | Correo electrónico del usuario.                             |
| `password`    | `TEXT`         | Contraseña del usuario (almacenada de manera segura).      |

### Tabla: inversiones

Esta tabla almacenará las inversiones realizadas, tanto reales como simuladas, permitiendo analizar estrategias y evaluar la lógica de las decisiones basadas en el análisis de datos.

| Campo            | Tipo de dato  | Descripción |
|-----------------|--------------|-------------|
| `id`            | INTEGER (PK)  | Identificador único de la inversión |
| `fecha_compra`  | DATETIME      | Fecha y hora de la compra |
| `simbolo`       | TEXT          | Código de la criptomoneda (BTC, ETH, etc.) |
| `cantidad`      | REAL          | Cantidad comprada |
| `precio_compra` | REAL          | Precio unitario de compra |
| `comision`      | REAL          | Comisión pagada en la compra (opcional) |
| `valor_usd`     | REAL          | Valor total en USD/EUR en el momento de compra |
| `fecha_venta`   | DATETIME      | Fecha de venta (si se ha vendido) |
| `precio_venta`  | REAL          | Precio unitario de venta (si aplica) |
| `ganancia_perdida` | REAL      | Se puede calcular posteriormente |
| `tipo_inversion` | TEXT         | Indica si la inversión es "real" o "simulada" |

### Detalles adicionales:
- **`timestamp`**: El campo `timestamp` en la tabla `crypto_data` se usará para ordenar y gestionar los datos por antigüedad. Los registros más antiguos de un año serán eliminados.
- **Eliminación de datos**: Un proceso automatizado se encargará de borrar los registros de la tabla `crypto_data` que tengan más de un año de antigüedad.
- **Índices**: Es recomendable crear un índice en el campo `timestamp` para optimizar las consultas de las lecturas de criptomonedas.
- **Relaciones**:
  - La tabla `alerts` tiene una relación con la tabla `cryptos` a través de `crypto_id`, lo que permite asociar alertas a criptomonedas específicas.
  - La tabla `users` puede integrarse si se decide permitir a los usuarios personalizar alertas o seguir criptomonedas.
 
### Tabla: `operaciones`

Hasta ahora, el proyecto Kryptonite contaba con una tabla llamada inversiones donde se registraban las compras y ventas de criptomonedas, junto con datos como el precio de entrada, salida, comisiones y beneficio/pérdida.

Sin embargo, este enfoque plantea varios problemas:

* La tabla inversiones mezcla conceptos: operaciones individuales y resultados agregados.

* Las inversiones no siempre son compras únicas; pueden construirse con varias operaciones.

* Operaciones como ventas anticipadas o recompras (shorting manual) no encajan bien en ese esquema.

Por eso, se ha decidido eliminar la tabla inversiones y trabajar exclusivamente con una nueva tabla llamada operaciones, que es más flexible y precisa.

La tabla operaciones recoge cada movimiento real realizado en el mercado (compra o venta), con todos los detalles necesarios para reconstruir después cualquier inversión, calcular posiciones abiertas, ganancias, pérdidas, etc.

A partir de esta tabla, se podrán generar:

* Posiciones actuales por cripto (cantidad y precio medio).

* Ganancias y pérdidas realizadas (por cada venta).

* Estadísticas de rentabilidad, rendimiento histórico, etc.

Toda esta información se calculará a partir de las operaciones, usando lógica en Python, sin necesidad de almacenar redundancias.

| Campo         | Tipo      | Descripción                                                  |
|---------------|-----------|--------------------------------------------------------------|
| `id`          | INTEGER   | Identificador único de la operación                          |
| `timestamp`   | INTEGER   | Fecha/hora de la operación (en formato UNIX timestamp)       |
| `cripto`      | TEXT      | Criptomoneda operada (ej: `BTC`, `ETH`, `ADA`)               |
| `moneda`      | TEXT      | Moneda fiat usada (ej: `EUR`, `USD`, `USDT`)                 |
| `tipo`        | TEXT      | Tipo de operación: `'compra'` o `'venta'`                    |
| `cantidad`    | REAL      | Cantidad de criptomoneda operada                             |
| `precio`      | REAL      | Precio unitario en moneda fiat                               |
| `valor_total` | REAL      | Valor total de la operación (sin contar comisión)            |
| `comision`    | REAL      | Comisión pagada en moneda fiat                               |
| `origen`      | TEXT      | Fuente de la operación: `'manual'`, `'binance'`, etc.        |
| `nota`        | TEXT      | Notas o comentarios opcionales sobre la operación            |


## Fichero de log

Se ha configurado un manejador para usa ritaciones de fichero de log en /work/kryptonite/logs/kryptonite.log.
En prinicpio es fichero plano, pero me aputna ChatGPT la posibilidad de configurarlo para que el fichero de log sea en formato JSON, lo que facilitaría el procesa del mismo con herramientas.
De momento se ha dejado el clásico fichero de log con texto plano, pero la idea de usar JSON me parece interesante, quizas lo implantemos más adelante.

# API

Se ha montado un API para que se pueda llamar desde Node-Red. api.py

> python src/api.py (Se ejecuta desde el directorio principal del proyecto)
>
> 

# Telegram

Con el API, desde telegram se puede llamar a la kriptonite, a través del método del API que se quiera. Si no esta implementado, solo hay que implementarlo.
Métodos disponibles:

/run -> Ejecuta fetch_and_insert_data_last_30min(), que lees datos del binance de las criptomonedas favoritas, lee el valor de los ultimos 30mi. en intervalos de 5min. y los carga en sqlite.

/valor [criptomoneda] -> devuelve el valor de una criptomoneda.

# 📦 Estructura de datos: CriptoEnCartera

Con el objetivo de estandarizar la representación de cada criptomoneda en cartera, se ha creado una clase llamada `CriptoEnCartera` definida con `@dataclass`. Esta clase actúa como estructura central para almacenar y procesar todos los datos relacionados con una posición individual en el portafolio.

La clase se encuentra en el archivo:

📁 `src/modelos.py`

### 🧩 Atributos incluidos:

- `simbolo` (`str`): símbolo de la criptomoneda (por ejemplo, BTC, ETH).
- `cantidad_total` (`float`): cantidad total actual en posesión.
- `coste_total_inversion` (`float`): coste total invertido en esa criptomoneda.
- `precio_actual` (`float`): precio actual de mercado.

### ⚙️ Atributos calculados automáticamente:

Se implementan como propiedades (`@property`), y se calculan de forma automática según los valores actuales:

- `precio_medio_compra` (`float`): coste medio por unidad.
- `valor_actual_inversion` (`float`): valor actual de la inversión.
- `rentabilidad` (`float`): rentabilidad de la inversión en porcentaje respecto al coste total.

### 🔄 Conversión a diccionario

Se incluye el método `a_dict()` que devuelve todos los datos en un `dict`, útil para:

- Exportar a JSON.
- Enviar por API o integraciones (por ejemplo, Node-RED o Telegram).
- Mostrar en reportes o interfaces.

### ✅ Ejemplo de uso:

```python
from modelos import CriptoEnCartera

cripto = CriptoEnCartera(
    simbolo="BTC",
    cantidad_total=0.5,
    coste_total_inversion=12000,
    precio_actual=25000
)

print(cripto.precio_medio_compra)      # 24000.0
print(cripto.valor_actual_inversion)   # 12500.0
print(cripto.rentabilidad)             # 4.17
print(cripto.a_dict())                 # Diccionario con todos los campos
```

# SCRIPT DE SQL

Insertar las operaciones en la tabla operaciones de la base de datos.

Procedente de Revolut   

```sql
INSERT INTO operaciones (timestamp, cripto, moneda, tipo, cantidad, precio, valor_total, comision, origen) VALUES
(1721318523, 'SHIB', 'EUR', 'Compra', 2265632.3079, 0.00, 55.00, 1.49, 'Revolut'),
(1723755986, 'XLM', 'EUR', 'Compra', 206.8521406, 0.48, 100.00, 1.49, 'Revolut'),
(1723842233, 'XLM', 'EUR', 'Venta', 103.7700437, 0.50, 51.99, 1.49, 'Revolut'),
(1724103109, 'XLM', 'EUR', 'Compra', 108.0999396, 0.48, 51.50, 1.49, 'Revolut'),
(1724753174, 'SHIB', 'EUR', 'Compra', 2107423.8981, 0.00, 50.00, 1.49, 'Revolut'),
(1726611458, 'DOT', 'EUR', 'Compra', 7.69469341, 6.69, 51.50, 1.49, 'Revolut'),
(1726724475, 'XLM', 'EUR', 'Envío', 204.9723879, 0.39, 79.75, 0.00, 'Revolut'),
(1726986085, 'BTC', 'EUR', 'Compra', 0.00001835, 91508.53, 1.68, 0.00, 'Revolut'),
(1727072085, 'BTC', 'EUR', 'Compra', 0.00000376, 95628.14, 0.36, 0.00, 'Revolut'),
(1727082924, 'BTC', 'EUR', 'Compra', 0.00002549, 94138.14, 2.40, 0.00, 'Revolut'),
(1727178478, 'BTC', 'EUR', 'Compra', 0.00001725, 95048.64, 1.64, 0.00, 'Revolut'),
(1727263064, 'BTC', 'EUR', 'Compra', 0.00001833, 98171.90, 1.80, 0.00, 'Revolut'),
(1727307927, 'BTC', 'EUR', 'Compra', 0.00001116, 98559.25, 1.10, 0.00, 'Revolut'),
(1727754323, 'SHIB', 'EUR', 'Recepción', 4878000.0, 0.00, 101.70, 0.00, 'Revolut'),
(1727938096, 'SHIB', 'EUR', 'Compra', 106897.8162, 0.00, 2.10, 0.00, 'Revolut'),
(1729315940, 'BTC', 'EUR', 'Compra', 0.00001146, 96781.24, 1.11, 0.00, 'Revolut');
```

Procedente de revolut X

```sql
INSERT INTO operaciones (timestamp, cripto, moneda, tipo, cantidad, precio, valor_total, comision, origen) VALUES
(1736226101, 'EUR', 'EUR', 'Recepción', 50, 1.00, 50.00, 0.00, 'Revolut X'),
(1736242740, 'ADA', 'EUR', 'Compra', 49.01, 1.02, 49.99, 0.00, 'Revolut X'),
(1736300480, 'EUR', 'EUR', 'Recepción', 50, 1.00, 50.00, 0.00, 'Revolut X'),
(1736377786, 'ADA', 'EUR', 'Compra', 51.58, 0.97, 50.01, 0.04, 'Revolut X'),
(1736553675, 'XLM', 'EUR', 'Recepción', 204.9723879, 0.40, 81.01, 0.00, 'Revolut X'),
(1736557348, 'XLM', 'EUR', 'Venta', 204.9, 0.39, 80.24, 0.08, 'Revolut X'),
(1736557485, 'BTC', 'EUR', 'Compra', 0.000855, 92093.56, 78.74, 0.07, 'Revolut X'),
(1736557567, 'EUR', 'EUR', 'Recepción', 20, 1.00, 20.00, 0.00, 'Revolut X'),
(1736557568, 'BTC', 'EUR', 'Compra', 0.000215, 92139.53, 19.81, 0.01, 'Revolut X'),
(1736648394, 'BTC', 'EUR', 'Compra', 0.000017, 91764.71, 1.56, 0.00, 'Revolut X'),
(1737163205, 'EUR', 'EUR', 'Recepción', 100, 1.00, 100.00, 0.00, 'Revolut X'),
(1737163279, 'SHIB', 'EUR', 'Compra', 4878000, 0.00, 99.99, 0.00, 'Revolut X'),
(1737163523, 'SHIB', 'EUR', 'Envio', 4878000, 0.00, 99.88, 0.00, 'Revolut X'),
(1737163661, 'EUR', 'EUR', 'Recepción', 50, 1.00, 50.00, 0.00, 'Revolut X'),
(1737163662, 'DOT', 'EUR', 'Compra', 7.6923, 6.42, 49.39, 0.04, 'Revolut X'),
(1737763930, 'EUR', 'EUR', 'Recepción', 25, 1.00, 25.00, 0.00, 'Revolut X'),
(1737764162, 'EUR', 'EUR', 'Recepción', 50, 1.00, 50.00, 0.00, 'Revolut X'),
(1737766367, 'BTC', 'EUR', 'Compra', 0.0005, 100000.00, 50.00, 0.00, 'Revolut X'),
(1737844150, 'EUR', 'EUR', 'Recepción', 50, 1.00, 50.00, 0.00, 'Revolut X'),
(1737859598, 'DOT', 'EUR', 'Compra', 4.5454, 5.50, 24.99, 0.00, 'Revolut X'),
(1737865054, 'EUR', 'EUR', 'Recepción', 50, 1.00, 50.00, 0.00, 'Revolut X'),
(1737945997, 'SHIB', 'EUR', 'Compra', 3125000, 0.00, 50.00, 0.00, 'Revolut X'),
(1737979502, 'ETH', 'EUR', 'Compra', 0.0181, 2800.00, 50.68, 0.00, 'Revolut X'),
(1738386684, 'EUR', 'EUR', 'Recepción', 51.92, 1.00, 51.92, 0.00, 'Revolut X'),
(1738386684, 'BTC', 'EUR', 'Compra', 0.000574, 90348.43, 51.86, 0.04, 'Revolut X'),
(1741819056, 'ETH', 'EUR', 'Venta', 0.0181, 1665.75, 30.15, 0.03, 'Revolut X'),
(1741908850, 'ETH', 'EUR', 'Compra', 0.0181, 1549.72, 28.05, 0.00, 'Revolut X'),
(1742991855, 'BTC', 'EUR', 'Venta', 0.00041487, 82845.23, 34.37, 0.04, 'Revolut X'),
(1743381105, 'ADA', 'EUR', 'Venta', 25.1358, 0.63, 15.71, 0.02, 'Revolut X'),
(1743643309, 'ADA', 'EUR', 'Compra', 25.1358, 0.59, 14.83, 0.00, 'Revolut X'),
(1745638331, 'ETH', 'EUR', 'Compra', 0.00077496, 2671.11, 2.07, 0.00, 'Revolut X');
```
---

# 🚀 Control de Estado de Inversiones en Kryptonite

---

## 🎯 Objetivo

Calcular para cada criptomoneda el estado actual de la inversión, considerando:

* 💰 **Cantidad invertida (€)**
* 📊 **Cantidad actual de monedas en cartera**
* ⚖️ **Coste medio por moneda (€)**
* 📈 **Valor actual en euros (precio de mercado)**
* 💹 **Rentabilidad (valor y porcentaje)**
* 🔄 **Estado de la posición (abierta o cerrada)**

---

## 🔍 Supuestos y Consideraciones

* 🛒 **Compras:** aumentan la cantidad de monedas y la inversión total (valor + comisiones).
* 💸 **Ventas:** disminuyen la cantidad de monedas.
* 🎁 **Recepciones:** aumentan la cantidad de monedas sin afectar la inversión (monedas gratuitas).
* 📤 **Envíos:** disminuyen la cantidad de monedas sin afectar la inversión (transferencias).
* 📊 La rentabilidad = valor actual - inversión total.
* 💵 Valor actual calculado con el precio de mercado actualizado.
* 🔓 Posición **abierta** si la cantidad actual > 0, **cerrada** si 0 o menor.

---

## 🗂 Modelo de Datos Simplificado

Suponemos que tienes:

* Clases o tablas con **Operaciones**:
  `symbol`, `type`, `quantity`, `price`, `value`, `fees`, `date`
* Función para obtener el precio actual de mercado (API o base de datos).

---

## 🧑‍💻 Código Python de ejemplo

```python
from datetime import datetime
from typing import List

class Operation:
    def __init__(self, symbol: str, op_type: str, quantity: float, price: float, value: float, fees: float, date: datetime):
        self.symbol = symbol
        self.op_type = op_type
        self.quantity = quantity
        self.price = price
        self.value = value
        self.fees = fees
        self.date = date

class InvestmentStatus:
    def __init__(self, symbol: str, quantity_invested: float, quantity_holdings: float, cost_avg: float, market_value: float, profit_loss: float, profit_loss_pct: float, status: str):
        self.symbol = symbol
        self.quantity_invested = quantity_invested
        self.quantity_holdings = quantity_holdings
        self.cost_avg = cost_avg
        self.market_value = market_value
        self.profit_loss = profit_loss
        self.profit_loss_pct = profit_loss_pct
        self.status = status

def get_market_price(symbol: str) -> float:
    """
    Función simulada para obtener el precio actual de mercado.
    En Kryptonite, esta función consulta API o base de datos.
    """
    market_prices = {
        "BTC": 95000,
        "ETH": 2800,
        "SHIB": 0.00002,
        "XLM": 0.4,
        "DOT": 6.5,
    }
    return market_prices.get(symbol.upper(), 0)

def calculate_investment_status(operations: List[Operation], symbol: str) -> InvestmentStatus:
    # Filtrar operaciones para la moneda
    ops = sorted([op for op in operations if op.symbol.upper() == symbol.upper()], key=lambda x: x.date)

    quantity_bought = 0.0
    invested_amount = 0.0
    quantity_sold = 0.0
    quantity_received = 0.0
    quantity_sent = 0.0

    for op in ops:
        t = op.op_type.lower()
        if t == "compra" or t == "buy":
            quantity_bought += op.quantity
            invested_amount += op.value + op.fees
        elif t == "venta" or t == "sell":
            quantity_sold += op.quantity
        elif t == "recepción" or t == "receive":
            quantity_received += op.quantity
        elif t == "envío" or t == "send":
            quantity_sent += op.quantity

    quantity_holdings = quantity_bought + quantity_received - quantity_sold - quantity_sent

    cost_avg = invested_amount / quantity_bought if quantity_bought > 0 else 0
    market_price = get_market_price(symbol)
    market_value = quantity_holdings * market_price
    profit_loss = market_value - invested_amount
    profit_loss_pct = (profit_loss / invested_amount) * 100 if invested_amount > 0 else 0
    status = "Abierta" if quantity_holdings > 0 else "Cerrada"

    return InvestmentStatus(symbol, invested_amount, quantity_holdings, cost_avg, market_value, profit_loss, profit_loss_pct, status)

# --- EJEMPLO DE USO ---

if __name__ == "__main__":
    operations = [
        Operation("BTC", "Compra", 0.001, 90000, 90, 0.5, datetime(2025, 1, 10, 12, 0)),
        Operation("BTC", "Compra", 0.002, 95000, 190, 0.7, datetime(2025, 2, 5, 14, 0)),
        Operation("BTC", "Venta", 0.0015, 98000, 147, 0.4, datetime(2025, 3, 10, 10, 0)),
        Operation("BTC", "Recepción", 0.0003, 0, 0, 0, datetime(2025, 4, 1, 9, 0)),
    ]

    status_btc = calculate_investment_status(operations, "BTC")

    print(f"💎 Moneda: {status_btc.symbol}")
    print(f"💰 Inversión (€): {status_btc.quantity_invested:.2f}")
    print(f"📦 Cantidad en cartera: {status_btc.quantity_holdings:.6f}")
    print(f"⚖️ Coste medio (€): {status_btc.cost_avg:.2f}")
    print(f"📈 Valor mercado (€): {status_btc.market_value:.2f}")
    print(f"💹 Rentabilidad (€): {status_btc.profit_loss:.2f}")
    print(f"📊 Rentabilidad (%): {status_btc.profit_loss_pct:.2f}%")
    print(f"🔄 Estado: {status_btc.status}")
```

---

## 🔗 Integración en Kryptonite

* 📥 Las operaciones se obtienen desde la base de datos.
* 💻 El precio actual se obtiene mediante tus funciones API o base de datos.
* 🔄 El cálculo se realiza para cada moneda y se actualiza el estado.
* 📊 Resultados se pueden mostrar en informes, alertas o interfaz.

---

Si quieres, te ayudo a hacer un script que lea directamente de la base de datos SQLite o que se adapte a las clases y estructura exacta de tu proyecto Kryptonite.

¿Quieres que siga con eso? 🚀



