# Kryptonite - Roadmap de Dockerizacion

> Plan por fases para integrar Kryptonite en el ecosistema hogarOS
> con la misma estructura que ReDo, FiDo y MediDo.

Fecha: 2026-03-31
Actualizado: 2026-04-19
Documento de analisis: [analisis-dockerizacion.md](analisis-dockerizacion.md)

---

## Estado actual

- [x] 1.1 `src/` renombrado a `app/` via `git mv`
- [x] 1.2 `app/config.py` limpiado: sin `os.chdir()`, rutas relativas, prefijo `KRYPTO_`, alias de compatibilidad

---

## Fase 1 — Dockerizar sin migrar Flask

**Objetivo:** Kryptonite corre en Docker con la estructura minima viable.
**Esfuerzo estimado:** 1 sesion de trabajo.
**Resultado:** Contenedor funcional, desplegable con docker-compose.

### Tareas

- [x] 1.1 Reorganizar estructura de directorios (`src/` → `app/`)
  - `git mv src app`
  - Imports no cambian — resueltos via `PYTHONPATH=/app/app` en el Dockerfile

- [x] 1.2 Limpiar configuracion (`app/config.py`)
  - Eliminado `os.chdir("/home/jovyan/work/kryptonite")`
  - Defaults de `DB_PATH` y `LOG_FILE_PATH` cambiados a rutas relativas
  - Variables con prefijo `KRYPTO_` como estandar; alias sin prefijo para compatibilidad
  - `data/` y `logs/` se crean solos al arrancar

- [x] 1.3 Crear Dockerfile
  - Base: `python:3.12-slim`
  - Instalar dependencias de sistema (`libfreetype6-dev`, `libpng-dev`)
  - `pip install` de `requirements.txt`
  - `ENV PYTHONPATH=/app/app` para que los imports de Flask sigan funcionando sin cambios
  - Entry point: `python -m flask --app api run --host 0.0.0.0 --port 5000`
  - Probar build local: `docker build -t kryptonite .`

- [x] 1.4 Crear docker-compose.yml local
  - Servicio `kryptonite` con build, puertos, volumenes, env_file
  - Probar: `docker compose up` y verificar endpoints con curl

- [ ] 1.5 Verificar que todo funciona
  - `GET /portafolio` devuelve datos
  - `POST /prompt` responde (requiere GROQ_API_KEY)
  - Logs se escriben en `./logs/`

### Entregables
- `Dockerfile`
- `docker-compose.yml`
- `app/config.py` limpio ✅
- Estructura `app/` funcional ✅

---

## Fase 2 — Migrar Flask a FastAPI

**Objetivo:** Consistencia de stack con el resto del ecosistema.
**Esfuerzo estimado:** 2-3 sesiones de trabajo.
**Resultado:** API identica pero sobre FastAPI + uvicorn.

### Tareas

- [ ] 2.1 Crear `app/principal.py` con estructura estandar
  - FastAPI app con `lifespan` (init BD, scheduler si aplica)
  - Montar routers
  - Montar `static/` (preparado para fase 4)

- [ ] 2.2 Crear modelos Pydantic (`app/modelos.py`)
  - Schemas de request/response para cada grupo de endpoints
  - Tipos estrictos, Optional donde corresponda

- [ ] 2.3 Migrar endpoints a routers FastAPI
  - `app/rutas/portfolio.py` — `/portafolio`, `/nuevaOperacion`, `/valor`
  - `app/rutas/analisis.py` — `/senal/*`, `/backtest`, `/grafica24h`
  - `app/rutas/datos.py` — `/run`
  - `app/rutas/ia.py` — `/prompt`, `/prompt/status`, `/analisis_ia`, `/sentimiento_noticias`
  - Cada router: migrar, probar, siguiente

- [ ] 2.4 Estandarizar capa de base de datos (`app/bd.py`)
  - Funciones: `obtener_conexion()`, `consultar_todos()`, `consultar_uno()`, `ejecutar()`
  - PRAGMA WAL + foreign_keys
  - Crear `app/esquema.sql` con las tablas actuales

- [ ] 2.5 Actualizar Dockerfile
  - Cambiar entry point a `uvicorn app.principal:app`
  - Actualizar `requirements.txt` (anadir fastapi, uvicorn; quitar flask)

- [ ] 2.6 Actualizar `requirements.txt`
  - Eliminar `flask`
  - Anadir `fastapi`, `uvicorn[standard]`
  - Verificar compatibilidad de versiones

- [ ] 2.7 Test completo de todos los endpoints
  - Verificar con curl o httpie cada endpoint
  - Comprobar docs automaticas en `/docs` (Swagger)

### Entregables
- `app/principal.py`, `app/modelos.py`, `app/bd.py`, `app/esquema.sql`
- `app/rutas/` con 4 routers
- `requirements.txt` actualizado
- Dockerfile con uvicorn

---

## Fase 3 — Integrar en hogarOS

**Objetivo:** Kryptonite es un servicio mas del docker-compose de hogarOS.
**Esfuerzo estimado:** 1 sesion de trabajo.
**Resultado:** Despliegue unificado con `actualizar.sh`.

### Tareas

- [ ] 3.1 Preparar VM 101 (una sola vez, manual)
  ```bash
  cd /mnt/datos
  git clone https://github.com/acabellan1868-prog/kryptonite kryptonite-build
  mkdir -p kryptonite/data kryptonite/logs
  cp /ruta/actual/kryptonite.db kryptonite/data/
  cp kryptonite-build/parametros.env.example kryptonite/parametros.env
  # editar parametros.env con las API keys reales
  ```

- [ ] 3.2 Anadir `kryptonite-build` a `actualizar.sh` de hogarOS
  ```bash
  # Linea actual:
  PROYECTOS=("hogarOS" "redo-build" "fido-build" "medido-build")
  # Cambia a:
  PROYECTOS=("hogarOS" "redo-build" "fido-build" "medido-build" "kryptonite-build")
  ```

- [ ] 3.3 Anadir servicio al docker-compose de hogarOS
  ```yaml
  kryptonite:
    build: /mnt/datos/kryptonite-build/
    container_name: kryptonite
    ports:
      - "5000:5000"
    volumes:
      - /mnt/datos/kryptonite/data:/app/data
      - /mnt/datos/kryptonite/logs:/app/logs
    env_file:
      - /mnt/datos/kryptonite/parametros.env
    environment:
      - TZ=Europe/Madrid
    restart: unless-stopped
  ```

- [ ] 3.4 Actualizar nginx.conf de hogarOS
  ```nginx
  # Antes (app externa al ecosistema Docker):
  location /crypto/api/ {
      proxy_pass http://host.docker.internal:5000/;
  }
  # Despues (contenedor en la misma red Docker):
  location /crypto/api/ {
      proxy_pass http://kryptonite:5000/;
  }
  ```

- [ ] 3.5 Crear endpoint `/api/resumen`
  - Devuelve: valor total portfolio, cambio 24h, numero de criptos, estado
  - MediDo puede consultarlo para health checks
  - El portal puede mostrar tarjeta de Kryptonite

- [ ] 3.6 Actualizar MediDo
  - Cambiar URL de health check de Kryptonite
  - Apuntar al nuevo endpoint `/api/resumen`

- [ ] 3.7 Actualizar n8n
  - Cambiar URLs de la API en los flujos que llaman a Kryptonite
  - Las rutas no cambian (`/portafolio`, `/run`, `/prompt`, etc.)
  - Solo cambia el host: de `localhost:5000` o `IP:5000` al nuevo endpoint via proxy

- [ ] 3.8 Probar despliegue completo
  - `cd /mnt/datos/hogarOS && bash actualizar.sh`
  - Verificar que todos los servicios arrancan
  - Verificar proxy desde el portal
  - Verificar health check desde MediDo

### Entregables
- `kryptonite-build/` clonado en VM 101
- `actualizar.sh` actualizado con `kryptonite-build`
- Servicio `kryptonite` en docker-compose de hogarOS
- nginx.conf actualizado
- `/api/resumen` funcional
- n8n actualizado
- `actualizar.sh` despliega todo junto

---

## Fase 4 — Frontend con Living Sanctuary (opcional)

**Objetivo:** Dashboard web para Kryptonite integrado en el portal.
**Esfuerzo estimado:** 2-3 sesiones de trabajo.
**Resultado:** SPA accesible desde el portal en `/crypto/`.

### Tareas

- [ ] 4.1 Crear `static/index.html` con estructura estandar
  - Header con lumina + hogar-header__barra
  - Drawer de navegacion (otras apps + portal)
  - Link a `/static/hogar.css`

- [ ] 4.2 Tab "Portfolio"
  - Tabla con criptos, cantidad, valor actual, PnL (beneficio/perdida)
  - Grafico de distribucion

- [ ] 4.3 Tab "Analisis"
  - Graficas de precio 24h
  - Senales de trading activas
  - Formulario de backtesting

- [ ] 4.4 Tab "Agente IA"
  - Chat con el agente (consume `/api/prompt`)
  - Historial de conversacion

- [ ] 4.5 Actualizar nginx.conf
  - Cambiar ruta de `/crypto/api/` a `/crypto/`
  - Anadir sub_filters para reescritura de paths del frontend

- [ ] 4.6 Anadir tarjeta en el portal de hogarOS
  - Tarjeta con resumen del portfolio (consume `/api/resumen`)

### Entregables
- SPA funcional en `static/index.html`
- Integrado en el portal con Living Sanctuary
- Navegacion bidireccional portal <-> kryptonite

---

## Resumen de esfuerzo

| Fase | Descripcion | Sesiones | Dependencias |
|------|-------------|----------|--------------|
| 1 | Dockerizar (Flask) | 1 | Ninguna |
| 2 | Migrar a FastAPI | 2-3 | Fase 1 |
| 3 | Integrar en hogarOS | 1 | Fase 2 |
| 4 | Frontend (opcional) | 2-3 | Fase 3 |
| **Total** | | **6-8** | |

---

## Orden recomendado

```
Fase 1 ──→ Fase 2 ──→ Fase 3 ──→ Fase 4
  │                       │
  │                       └─ Kryptonite ya es "ciudadano de primera" en hogarOS
  │
  └─ Aqui ya tienes Kryptonite en Docker (rapido, valor inmediato)
```
