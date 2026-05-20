# Bitácora — Kryptonite

## 2026-04-25

### AGENTS.md local para Codex

Creado `AGENTS.md` en el repo de Kryptonite a partir de `CLAUDE.md`, con stack,
estructura, API, variables de entorno y gotchas operativos.

Añadidos dos matices:
- Kryptonite ya está migrado a FastAPI; Flask queda obsoleto para trabajo nuevo.
- La siguiente integración técnica prevista es Revolut X, pero el estado y fases
  siguen viviendo en `roadmap.md`.

---

## 2026-04-22

### Planificación Fase 7 — Integración Revolut X API

Sesión de análisis y diseño para automatizar la importación de recompensas de staking de DOT (Polkadot) y ADA (Cardano) desde la API de Revolut X.

Decisiones tomadas:
- Las recompensas se guardarán en la tabla `operaciones` existente (tipo=`Recompensa`, origen=`Revolut`), sin nueva tabla.
- La autenticación usa firma Ed25519 — cada petición lleva tres headers firmados.
- El API tiene un límite de ventana de 7 días por petición; la carga histórica iterará en ventanas semanales.
- Se creará el módulo `app/revolut_x.py` y la ruta `app/rutas/revolut.py` con el endpoint `/revolut/sincronizar`.
- La automatización periódica se hará desde Node-RED (llamada semanal).

Roadmap actualizado con la Fase 7 completa (tareas 7.1 a 7.5). Implementación pendiente para la siguiente sesión.

---

## 2026-04-21

### Nuevo endpoint POST /nuevaOperacion

Añadido en la migración a FastAPI. Permite insertar operaciones (compra, venta, recompensa…) en la BD desde fuera de la aplicación — por ejemplo desde Node-RED o Telegram — sin acceder directamente a SQLite. Recibe cripto, cantidad, precio, comisión, tipo y origen. Devuelve el ID de la operación insertada.

### Fases 2 y 3 completadas — FastAPI + integración en hogarOS

Migración Flask → FastAPI:
- `app/principal.py`: FastAPI con lifespan (LLM + agente inicializados una vez)
- `app/esquemas.py`: modelos Pydantic para request bodies
- `app/rutas/`: 4 routers (datos, portfolio, analisis, ia)
- Dockerfile actualizado a uvicorn; flask/papermill eliminados de requirements.txt

Integración en hogarOS:
- `docker-compose.yml`: nuevo servicio kryptonite (build desde `/mnt/datos/kryptonite-build`, puerto 5001 externo por conflicto con JupyterLab)
- `nginx.conf`: upstream kryptonite como contenedor (ya no `host.docker.internal:5000`)
- `actualizar.sh`: añadido `kryptonite-build` al git pull
- Remote de kryptonite-build cambiado a SSH para evitar prompt de credenciales

API verificada en producción: `http://192.168.31.131/crypto/api/portafolio` ✅

### Fase 1 completada — verificación de endpoints

La BD original estaba vacía (0 bytes) en `/mnt/datos/kryptonite/data/`. Se localizó la BD real en `/mnt/datos/jupyter/kryptonite/data/kryptonite.db` (292 MB) y se copió al volumen correcto.

Endpoints verificados desde el navegador en `http://192.168.31.131:5001`:
- `/portafolio` — portfolio completo con 6 criptos y datos reales
- `/portafolio?analisis=completo` — portfolio + análisis de riesgo
- `/valor?crypto=BTC` — precio actual
- `/senal/cambio_extremo` — señales de trading

**Fase 1 cerrada.** Próximo paso: Fase 2 (migración Flask → FastAPI).

---

## 2026-04-19

### Fase 1 dockerización — sesión de trabajo

**Objetivo:** Kryptonite corriendo en Docker en el servidor.

Cambios en el repo:
- `git mv src/ app/` — renombrado para seguir el estándar del ecosistema
- `app/config.py` reescrito: eliminado `os.chdir()`, rutas relativas por defecto, variables con prefijo `KRYPTO_`, alias de compatibilidad para no romper imports
- `Dockerfile` creado: `python:3.12-slim`, `PYTHONPATH=/app/app` para que los imports de Flask funcionen sin tocar ningún fichero
- `docker-compose.yml` creado: volúmenes `data/` y `logs/`, env_file
- `requirements.txt`: actualizadas versiones incompatibles con Python 3.12 (`pandas`, `numpy`, `matplotlib`, `scikit-learn`), eliminado `pandas-ta` (solo lo usaba `modelo_ia.py`, modelo sin integrar)
- `documentacion/roadmap-dockerizacion.md` actualizado con pasos reales del despliegue (`actualizar.sh`, `kryptonite-build`, nginx, n8n)

Acciones en el servidor (VM 101, `/mnt/datos/`):
- Clonado repo en `kryptonite-build/`
- Creado `kryptonite/data/` y `kryptonite/logs/` para volúmenes
- Copiado `parametros.env` de JupyterLab a `kryptonite/`
- Copiado `kryptonite.db` a `kryptonite/data/`
- Build Docker exitoso
- Contenedor arrancado en puerto 5001 (5000 ocupado por JupyterLab)
- `/portafolio` responde `[]` — pendiente verificar si la BD se lee correctamente

---

## 2026-04-18

### Estandarización de documentación al esquema del ecosistema

Creados `CLAUDE.md`, `roadmap.md` y `bitacora.md` en la raíz del proyecto para
seguir el mismo esquema que hogarOS, FiDo, ReDo y MediDo.

La documentación anterior se conserva íntegra en `documentacion/` — especialmente
`roadmap-2026.md` con el análisis detallado de mejoras futuras y brainstorming.
El nuevo `roadmap.md` es el resumen operativo de estado y próximos pasos.
