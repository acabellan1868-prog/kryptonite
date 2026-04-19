# Bitácora — Kryptonite

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
