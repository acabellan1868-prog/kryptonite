# Bitácora — Kryptonite

## 2026-05-29 (tarde) — Generación de claves Ed25519 y debug de autenticación Revolut X

### Estado actual
**Bloqueador activo:** Revolut X devuelve HTTP 401 "Signature verification rejected" en todos los intentos de sincronización de recompensas.

### Acciones realizadas ✅

**1. Generación de claves Ed25519**
Se generó un nuevo par de claves Ed25519 con OpenSSL:
- Clave privada (guardada en `parametros.env`): `MC4CAQAwBQYDK2VwBCIEIOZsHSKyikN35/SbTuuDiHOXFHXQqMrxBkBLiOFHo04v`
- Clave pública (registrada en Revolut X): `MCowBQYDK2VwAyEA5Fy1bZW5ZlKnvVUbP//uvl2MpAgFeJZ+3A9ZLo2NlUc=`

Nota: El usuario registró la clave pública EN EL PANEL DE REVOLUT X con los bloques BEGIN/END, como se verifica en la documentación oficial.

**2. Actualización de `parametros.env`**
Se actualizó `/mnt/datos/kryptonite-build/parametros.env` con:
```
KRYPTO_REVOLUT_API_KEY="iOtOzRpf2tu17xUt7QiqLJb51ZCkPbepDrB6JwCXipswc4s0i0YL8dx0ELMcZ2oA"
KRYPTO_REVOLUT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIOZsHSKyikN35/SbTuuDiHOXFHXQqMrxBkBLiOFHo04v
-----END PRIVATE KEY-----"
```

Importante: Usar comillas en `.env` para variables multilínea.

**3. Reconstrucción del contenedor**
El usuario reconstruyó el contenedor con `docker-compose build --no-cache && docker-compose up -d`.

### Problema detectado ❌

**Endpoint:** `GET http://192.168.31.131:5001/revolut/sincronizar?moneda=DOT&desde=2025-12-28&hasta=2026-05-29`

**Error:** HTTP 401 - "Signature verification rejected"
```json
{
  "message": "Signature verification rejected",
  "error_id": "23df56cb-8b45-4818-9e1a-3aa2291e6b27",
  "timestamp": 1780076325138
}
```

**Síntomas:**
- Clave privada carga correctamente (118 chars, ✅)
- Headers se generan sin error (✅)
- Petición HTTP se envía correctamente (✅)
- Pero Revolut X rechaza la firma

**Posibles causas:**
1. El formato del mensaje a firmar es incorrecto
2. El algoritmo de firma no coincide con lo que Revolut X espera
3. La documentación de Revolut X especifica un formato diferente al que estamos usando

### Debug añadido 🔧

Se añadieron prints en `app/revolut_x.py` línea ~97 para mostrar:
- Mensaje exacto que se está firmando
- Firma generada (primeros 50 chars)
- API Key (primeros 20 chars)

### Próximos pasos para la siguiente sesión

**CRÍTICO: Revisar documentación de Revolut X**
1. Acceder a: https://developer.revolut.com/docs/x-api/revolut-x-crypto-exchange-rest-api
2. Buscar la sección de autenticación Ed25519
3. Verificar:
   - Formato exacto del mensaje a firmar (¿es `METODO|RUTA|TIMESTAMP`?)
   - Dónde va la ruta (¿incluye query params?)
   - Qué unidades usa el timestamp (¿milisegundos o segundos?)
   - Si hay un prefijo especial en el header `X-Revx-Signature`

**Si los logs muestran que el mensaje es incorrecto:**
1. Corregir el formato en `_generar_headers_autenticados()`
2. Reconstruir contenedor
3. Probar nuevamente

**Si el formato es correcto pero sigue fallando:**
1. Verificar que la clave privada se carga correctamente (load_pem_private_key)
2. Probar con una firma manual generada desde OpenSSL para comparar
3. Revisar si Revolut X espera un encoding diferente (¿base64url en lugar de base64?)

---

## 2026-05-29 (continuación) — Debug Fase 7.4 y fixes de integración Revolut X

### Problemas resueltos ✅

**1. Endpoint `/operaciones/contar`**
- Creado endpoint que devuelve el total de operaciones en BD con filtros opcionales
- Permite verificar si portfolio crece por nuevas recompensas (cantidad) o cambios de precio

**2. Módulo `app/bd.py`**
- Creado módulo con funciones `consultar_uno()`, `consultar_todos()`, `ejecutar()`
- Proporciona API de alto nivel para acceso a BD SQLite

**3. Fixes de imports**
- Corregido orden de `load_dotenv()` en `principal.py` (antes de imports)
- Cambio de imports relativos a directos en `revolut.py` y `revolut_x.py`
- Resuelto problema de PYTHONPATH con estructura de carpetas

**4. Configuración de credenciales**
- Arreglado nombre de variables en `config.py`: `REVOLUT_API_KEY` → `KRYPTO_REVOLUT_API_KEY`
- Credenciales Ed25519 registradas en Revolut X (clave pública)
- Variables de entorno cargadas correctamente en contenedor

**5. Debugging y logging**
- Agregados prints detallados en `revolut_x.py` para diagnosticar problemas
- Headers Ed25519 se generan correctamente ✅
- Autenticación funciona ✅

### Problema pendiente ❌

**Endpoint incorrecto en Revolut X API**
- API devuelve 404 en `GET https://api.revolut.com/trading/api/transactions`
- El endpoint `/transactions` no existe o es incorrecto
- Necesaria revisión de documentación oficial de Revolut X para encontrar endpoint correcto

### Conclusión
Fases 7.1-7.3 están correctamente implementadas (autenticación, módulo, endpoints). 
La Fase 7.4 (carga histórica) está **bloqueada** porque el endpoint de la API de Revolut X es incorrecto.
Próximo paso: investigar documentación de Revolut X para determinar endpoint correcto.

---

## 2026-05-29 — Nuevo endpoint para verificar crecimiento del portfolio

### Endpoint `/operaciones/contar` ✅
Creado nuevo endpoint `GET /operaciones/contar` que devuelve el número total de operaciones en la BD con filtros opcionales:
- Sin parámetros: total de todas las operaciones
- Con filtros: `?moneda=DOT&origen=Revolut&tipo=Recompensa`

Respuesta incluye:
- `total`: número total
- `desglose_por_moneda`: operaciones por cada cripto
- `desglose_por_tipo`: operaciones por cada tipo (Recompensa, Compra, etc.)

**Propósito:** Verificar si el portfolio crece por nuevas recompensas (cantidad) o solo por cambios de precio. El usuario notó que su portfolio pasó de 0.741682 a 0.742393 sin haber cargado recompensas manualmente — este endpoint permite detectar si hay un sistema automático cargando datos.

---

## 2026-05-28 — Implementación Fase 7.1-7.3 (Integración Revolut X)

### Fases completadas 🤖

**Fase 7.1 ✅ — Autenticación Ed25519**
- Generadas claves Ed25519 (pública + privada)
- Creado `parametros.env` con claves (no en git)
- Actualizado `parametros.env.example` con plantilla
- Actualizado `app/config.py` para leer `KRYPTO_REVOLUT_API_KEY` y `KRYPTO_REVOLUT_PRIVATE_KEY`

**Fase 7.2 ✅ — Módulo `app/revolut_x.py`**
- Carga de clave privada Ed25519
- Firma de peticiones HTTP con Ed25519
- Generación de headers autenticados (`X-Revx-API-Key`, `X-Revx-Timestamp`, `X-Revx-Signature`)
- Función `obtener_recompensas(moneda, desde, hasta)` — itera en ventanas de 7 días
- Función `obtener_trades(simbolo, desde, hasta)` — para futuras ampliaciones
- Función `sincronizar_recompensas()` — descarga e inserta en BD
- Lógica anti-duplicados basada en `transaction_id`

**Fase 7.3 ✅ — Endpoints de sincronización `app/rutas/revolut.py`**
- `GET /revolut/sincronizar` — Sincroniza DOT y ADA del 1ro del mes a hoy
- `GET /revolut/sincronizar?moneda=DOT&desde=YYYY-MM-DD&hasta=YYYY-MM-DD` — Custom
- `GET /revolut/estado` — Estado de sincronizaciones realizadas
- Registrados en `app/principal.py` con tag `["Revolut X"]`

### Próximas tareas 👤 + 🤖

**Fase 7.4 — Carga histórica inicial**
- [ ] 👤 Determinar fecha de primera recompensa en Revolut X (app de Revolut)
- [ ] 🤖 Ejecutar: `GET /revolut/sincronizar?moneda=DOT&desde=<PRIMERA_FECHA>`
- [ ] 👤 Verificar: los datos coinciden con la app de Revolut X

**Fase 7.5 — Automatización Node-RED**
- [ ] 👤 Crear flujo en Node-RED que llame a `/revolut/sincronizar` semanalmente (ej: lunes 8:00)
- [ ] 👤 Verificar: nuevas recompensas aparecen automáticamente en `/portafolio`

### Testing
Los endpoints están listos para probar:
```
curl http://192.168.31.131:5001/crypto/api/revolut/sincronizar
curl http://192.168.31.131:5001/crypto/api/revolut/estado
```

Requisito: `.env` con claves válidas de Revolut X registradas.

---

## 2026-05-28 — Auditoría Fase 7 (Integración Revolut X)

### Situación actual
Revisión del estado de la Fase 7 — Integración Revolut X API para automatizar importación de recompensas de staking (DOT, ADA).

**Resultado:** Fase **completamente pendiente**. Roadmap documentado, sin código implementado.

### Análisis
La Fase 7 está desglosada en 5 sub-tareas:

1. **7.1 — Autenticación Ed25519** (2 manuales + 2 código)
   - [ ] 👤 Generar par de claves Ed25519 con OpenSSL en local
   - [ ] 👤 Registrar clave pública en `exchange.revolut.com`
   - [ ] 👤 Añadir variables a `parametros.env` (`REVOLUT_API_KEY`, `REVOLUT_PRIVATE_KEY`)
   - [ ] 🤖 Declarar en `app/config.py` con prefijo `KRYPTO_`

2. **7.2 — Módulo de integración** `app/revolut_x.py`
   - [ ] 🤖 Firma Ed25519 (headers para autenticación)
   - [ ] 🤖 Función `obtener_trades()` y `obtener_recompensas()` (ventanas máx. 7 días)
   - [ ] 🤖 Lógica anti-duplicados por `transaction_id`

3. **7.3 — Endpoints de sincronización** `app/rutas/revolut.py`
   - [ ] 🤖 `GET /revolut/sincronizar?moneda=DOT&desde=YYYY-MM-DD`
   - [ ] 🤖 `GET /revolut/sincronizar` (ambas monedas, último mes por defecto)
   - [ ] 🤖 Registrar router en `app/principal.py`

4. **7.4 — Carga histórica inicial**
   - [ ] 👤 Determinar fecha de primera recompensa en Revolut X
   - [ ] 🤖 Ejecutar carga histórica completa
   - [ ] 👤 Verificar coincidencia con app de Revolut X

5. **7.5 — Automatización con Node-RED**
   - [ ] 👤 Crear flujo que llame a `/revolut/sincronizar` semanalmente
   - [ ] 👤 Verificar que aparecen nuevas recompensas en `/portafolio`

### Decisiones de diseño (ya tomadas en sesión anterior)
- Guardar recompensas en tabla `operaciones` existente (tipo=`Recompensa`, origen=`Revolut`)
- Autenticación Ed25519 con headers firmados por cada petición
- API limit: 7 días por ventana (iterar en semanas para carga histórica)
- Automatización semanal desde Node-RED

### Esfuerzo estimado
- Total: Medio (~3-4 sesiones de desarrollo)
- Prerequisito crítico: Generar claves Ed25519 (tarea 7.1 manual)

---

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
