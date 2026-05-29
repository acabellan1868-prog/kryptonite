# Continuación Fase 7.4 — Debugging autenticación Revolut X

## Estado del bloqueador

**Error:** HTTP 401 "Signature verification rejected" en todas las peticiones a Revolut X API

**Última prueba:**
```
GET /revolut/sincronizar?moneda=DOT&desde=2025-12-28&hasta=2026-05-29
→ 200 OK pero sin datos (firma rechazada por Revolut X)
```

## Qué está configurado ✅

| Componente | Estado | Ubicación |
|-----------|--------|-----------|
| Clave privada Ed25519 | ✅ Generada | `/mnt/datos/kryptonite-build/parametros.env` |
| Clave pública Ed25519 | ✅ Registrada en panel Revolut X | (con bloques BEGIN/END) |
| API Key | ✅ Obtenido | `iOtOzRpf2tu17xUt7QiqLJb51ZCkPbepDrB6JwCXipswc4s0i0YL8dx0ELMcZ2oA` |
| Contenedor Docker | ✅ Reconstruido | `/mnt/datos/kryptonite-build/` |
| Módulo `revolut_x.py` | ✅ Con debugging | `app/revolut_x.py` línea ~97 |

## Qué necesita investigarse 🔍

### 1. Formato de firma Ed25519 en Revolut X

**Documentación oficial:** https://developer.revolut.com/docs/x-api/revolut-x-crypto-exchange-rest-api

**Preguntas a responder:**
- ¿Es el mensaje a firmar `METODO|RUTA|TIMESTAMP` o algo diferente?
- ¿La ruta incluye query parameters? (ej: `/trades/DOT?start_date=...`)
- ¿El timestamp es en milisegundos o segundos?
- ¿Hay un prefijo en `X-Revx-Signature`? (ej: "Ed25519 " o "Signature: ")
- ¿La firma debe estar en base64 o base64url?

### 2. Función a revisar

Archivo: `app/revolut_x.py` (líneas 66-101)

```python
def _generar_headers_autenticados(metodo: str, ruta: str) -> Optional[Dict[str, str]]:
    # AQUÍ ESTÁ EL PROBLEMA
    # Línea 88: mensaje = f"{metodo}|{ruta}|{ahora_ms}".encode("utf-8")
    # ¿Es este el formato correcto según Revolut X?
```

## Cómo continuar

### Paso 1: Revisar documentación (5 min)
1. Accede a https://developer.revolut.com/docs/x-api/revolut-x-crypto-exchange-rest-api
2. Busca la sección "Authentication" o "Ed25519 Signature"
3. Copia el ejemplo exacto de cómo debe verse la firma

### Paso 2: Comparar con nuestro código
Si el formato es diferente:
1. Edita `app/revolut_x.py` línea 88
2. Cambia el formato del mensaje a firmar
3. Reconstruye: `cd /mnt/datos/kryptonite-build && docker-compose build --no-cache && docker-compose up -d`

### Paso 3: Probar con debugging
```bash
# Ver logs con debugging
docker logs kryptonite | tail -50 | grep "REVOLUT"

# Ver el mensaje exacto que se está firmando
curl "http://192.168.31.131:5001/revolut/sincronizar?moneda=DOT&desde=2026-05-21&hasta=2026-05-28" 2>&1
```

### Paso 4: Si sigue fallando
Opciones:
- Probar firma con OpenSSL directamente para comparar
- Revisar si hay un `secret` adicional para mezclar con la firma
- Contactar con Revolut X support

## Variables útiles

```bash
# API Key registrado
iOtOzRpf2tu17xUt7QiqLJb51ZCkPbepDrB6JwCXipswc4s0i0YL8dx0ELMcZ2oA

# Clave pública registrada
MCowBQYDK2VwAyEA5Fy1bZW5ZlKnvVUbP//uvl2MpAgFeJZ+3A9ZLo2NlUc=

# Clave privada (EN PARAMETROS.ENV)
MC4CAQAwBQYDK2VwBCIEIOZsHSKyikN35/SbTuuDiHOXFHXQqMrxBkBLiOFHo04v
```

## Archivos modificados en esta sesión

- ✏️ `app/revolut_x.py` — Añadido debugging en líneas ~97-100
- ✏️ `/mnt/datos/kryptonite-build/parametros.env` — Actualizado con claves y API Key correctos
- 📝 `bitacora.md` — Documentado estado y acciones
- 📝 `roadmap.md` — Actualizado estado actual

## Tips de debugging

**Ver si la clave privada se carga:**
```bash
docker logs kryptonite | grep "Clave privada cargada"
```

**Ver el mensaje exacto a firmar:**
```bash
docker logs kryptonite | grep "Mensaje a firmar"
```

**Ver la firma generada:**
```bash
docker logs kryptonite | grep "Firma (base64)"
```

---

**Última actualización:** 2026-05-29 22:35
**Sesión anterior:** https://github.com/acabellan1868-prog/kryptonite
