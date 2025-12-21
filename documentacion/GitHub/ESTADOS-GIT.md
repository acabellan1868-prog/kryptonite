# 🔄 Estados de Archivos en Git - Guía Completa

> Entendiendo el flujo de trabajo de Git vs SVN

---

## 📊 Diferencia Fundamental: Git vs SVN

### SVN (Centralizado)
```
Working Copy ←──────────→ Servidor Central
      (tu código)           (repositorio remoto)
      
Estados: Modified → Committed al servidor
```

### Git (Distribuido)
```
Working Directory → Staging Area → Local Repository → Remote Repository
   (tu código)      (preparación)   (tu .git local)   (GitHub)
   
Estados: Modified → Staged → Committed → Pushed
```

**⚠️ Diferencia clave:** En Git tienes **DOS repositorios**:
- **Local** (en tu máquina: `.git/`)
- **Remoto** (en GitHub)

---

## 🎯 Los 4 Estados de un Archivo en Git

```
┌─────────────────────────────────────────────────────────────┐
│                    CICLO DE VIDA DE UN ARCHIVO              │
└─────────────────────────────────────────────────────────────┘

    1. UNTRACKED          2. UNMODIFIED         3. MODIFIED        4. STAGED
  (No versionado)      (Sin cambios)          (Modificado)      (Preparado)
        │                    │                     │                 │
        │                    │  ┌──────────────────┘                 │
        │                    │  │  Editas el archivo                 │
        │                    │  ↓                                    │
        │                    │  MODIFIED ──────────────────────────→ │
        │                    │     │                                 │
        │                    │     │  git add archivo.py             │
        │                    │     ↓                                 │
        │                    │  STAGED ←────────────────────────────┘
        │                    │     │
        │                    │     │  git commit -m "mensaje"
        │                    │     ↓
        │                    │  COMMITTED (guardado en .git local)
        │                    │     │
        │                    │     │  git push
        │                    │     ↓
        │                    │  PUSHED (subido a GitHub)
        │                    │     │
        │                    │     │  Ciclo completo
        │                    └─────┘
        │
        │  git add archivo_nuevo.py
        └────────────────────────────────────────────────────────────→ STAGED
```

---

## 📝 Explicación Detallada de Cada Estado

### ESTADO 1: UNTRACKED (No Rastreado)

**¿Qué es?**
- Archivo **nuevo** que Git detecta pero **NO está versionando**
- Git lo ve pero lo ignora
- Aparece en `git status` en **rojo** como "Untracked files"

**Ejemplo:**
```bash
# Creas un archivo nuevo
touch nuevo_archivo.py

# Git status lo muestra en rojo
$ git status
Untracked files:
  (use "git add <file>..." to include in what will be committed)
        nuevo_archivo.py
```

**Cómo pasa al siguiente estado:**
```bash
git add nuevo_archivo.py
```

---

### ESTADO 2: UNMODIFIED (Sin Modificar)

**¿Qué es?**
- Archivo **ya versionado** (en commits anteriores)
- El contenido **NO ha cambiado** desde el último commit
- Git lo rastrea pero no aparece en `git status` (porque no hay cambios)

**Ejemplo:**
```bash
# Después de hacer commit, el archivo está "limpio"
$ git status
nothing to commit, working tree clean
```

**Cómo pasa al siguiente estado:**
```bash
# Editas el archivo
nano archivo.py
# Ahora pasa a MODIFIED
```

---

### ESTADO 3: MODIFIED (Modificado)

**¿Qué es?**
- Archivo versionado que **HAS EDITADO**
- Los cambios están **solo en tu Working Directory**
- Git detecta diferencias vs el último commit
- Aparece en `git status` en **rojo** como "Changes not staged"

**Ejemplo:**
```bash
# Editas un archivo existente
echo "nueva línea" >> archivo.py

# Git status lo muestra en rojo
$ git status
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   archivo.py
```

**Importante:**
- ❌ **NO** está preparado para commit
- ❌ **NO** se subirá a GitHub si haces push ahora
- Los cambios pueden perderse fácilmente

**Cómo pasa al siguiente estado:**
```bash
git add archivo.py
```

**Cómo descartar cambios (PELIGROSO):**
```bash
git restore archivo.py  # Vuelve al estado del último commit
```

---

### ESTADO 4: STAGED (Preparado / En el Área de Stage)

**¿Qué es?**
- Archivo **preparado** para el próximo commit
- Los cambios están en el **Staging Area** (también llamado "Index")
- Aparece en `git status` en **VERDE** como "Changes to be committed"

**Ejemplo:**
```bash
# Añades el archivo al staging
git add archivo.py

# Git status lo muestra en VERDE
$ git status
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        modified:   archivo.py
```

**Importante:**
- ✅ Listo para hacer commit
- ❌ Todavía **NO** está guardado en el repositorio local
- ❌ Todavía **NO** está en GitHub

**Cómo pasa al siguiente estado:**
```bash
git commit -m "Descripción de los cambios"
```

**Cómo quitar del staging (sin perder cambios):**
```bash
git restore --staged archivo.py  # Vuelve a MODIFIED
```

---

### ESTADO 5: COMMITTED (Confirmado en Repositorio Local)

**¿Qué es?**
- Cambios **guardados permanentemente** en tu repositorio local (`.git/`)
- Forma parte del historial de commits
- **Seguro**: no se pierden fácilmente

**Ejemplo:**
```bash
# Hacer commit
git commit -m "feat: añadir nueva funcionalidad"

# Output
[main 97ff5e7] feat: añadir nueva funcionalidad
 1 file changed, 10 insertions(+)

# Git status ahora está limpio
$ git status
On branch main
Your branch is ahead of 'origin/main' by 1 commit.
  (use "git push" to publish your local commits)

nothing to commit, working tree clean
```

**Importante:**
- ✅ Guardado en tu máquina
- ❌ Todavía **NO** está en GitHub
- Solo tú lo tienes

**Cómo pasa al siguiente estado:**
```bash
git push
```

---

### ESTADO 6: PUSHED (Subido a Repositorio Remoto)

**¿Qué es?**
- Cambios **subidos a GitHub** (o GitLab, Bitbucket, etc.)
- Disponible para otros colaboradores
- Respaldado en la nube

**Ejemplo:**
```bash
# Subir a GitHub
git push

# Output
Enumerando objetos: 5, listo.
Contando objetos: 100% (5/5), listo.
Escribiendo objetos: 100% (3/3), 312 bytes | 312.00 KiB/s, listo.
Total 3 (delta 1), reusados 0 (delta 0)
To https://github.com/usuario/kryptonite.git
   97ff5e7..a1b2c3d  main -> main

# Git status
$ git status
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

**Importante:**
- ✅ Respaldado en GitHub
- ✅ Visible para otros
- ✅ Seguro y permanente

---

## 🔍 Comparación Visual: SVN vs Git

### SVN (2 pasos)
```
Working Copy          →          Server
(modificado)         svn commit   (committed)
    ROJO                              ✅

Comandos:
1. svn commit -m "mensaje"  → Sube directamente al servidor
```

### Git (4 pasos)
```
Working Directory  →  Staging Area  →  Local Repo  →  Remote Repo
  (modified)        git add (staged)  git commit     git push
     ROJO              VERDE          (committed)      (pushed)
                                          ✅              ✅✅

Comandos:
1. git add archivo.py           → Prepara para commit (staging)
2. git commit -m "mensaje"      → Guarda en repositorio local
3. git push                     → Sube a GitHub
```

**⚠️ Diferencia clave:**
- **SVN:** 1 comando (`svn commit`) → cambios en el servidor
- **Git:** 3 comandos (`add` → `commit` → `push`) → cambios en GitHub

---

## 🎨 Visualización con `git status`

### Ejemplo Completo con Múltiples Archivos

```bash
$ git status

On branch main
Your branch is ahead of 'origin/main' by 2 commits.
  (use "git push" to publish your local commits)

Changes to be committed:                           ← STAGED (VERDE)
  (use "git restore --staged <file>..." to unstage)
        new file:   nuevo.py
        modified:   api.py

Changes not staged for commit:                     ← MODIFIED (ROJO)
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   database.py
        deleted:    viejo.py

Untracked files:                                   ← UNTRACKED (ROJO)
  (use "git add <file>..." to include in what will be committed)
        temporal.py
```

**Interpretación:**
- `nuevo.py` y `api.py` → **STAGED** (verde) → Listos para commit
- `database.py` y `viejo.py` → **MODIFIED** (rojo) → Editados pero NO añadidos
- `temporal.py` → **UNTRACKED** (rojo) → Nuevo pero no añadido

---

## 📋 Tabla Resumen de Estados

| Estado | Color en `git status` | ¿Qué significa? | ¿Está guardado? | Comando siguiente |
|--------|----------------------|-----------------|-----------------|-------------------|
| **UNTRACKED** | 🔴 Rojo | Archivo nuevo no versionado | ❌ No | `git add` |
| **UNMODIFIED** | (no aparece) | Sin cambios desde último commit | ✅ Sí (en repo) | Editar archivo |
| **MODIFIED** | 🔴 Rojo | Editado pero no preparado | ❌ No | `git add` |
| **STAGED** | 🟢 Verde | Preparado para commit | ⚠️ En staging | `git commit` |
| **COMMITTED** | (no aparece) | Guardado en repo local | ✅ Sí (local) | `git push` |
| **PUSHED** | (no aparece) | Subido a GitHub | ✅✅ Sí (remoto) | - |

---

## 🔄 Flujo Completo Paso a Paso

### Escenario: Crear un nuevo archivo y subirlo a GitHub

```bash
# PASO 0: Estado inicial
$ git status
On branch main
nothing to commit, working tree clean

# PASO 1: Crear archivo nuevo
$ touch nuevo_archivo.py
$ echo "print('Hola')" > nuevo_archivo.py

# Estado: UNTRACKED (rojo)
$ git status
Untracked files:
        nuevo_archivo.py

# PASO 2: Añadir al staging
$ git add nuevo_archivo.py

# Estado: STAGED (verde)
$ git status
Changes to be committed:
        new file:   nuevo_archivo.py

# PASO 3: Commit (guardar en repo local)
$ git commit -m "feat: añadir nuevo archivo"
[main a1b2c3d] feat: añadir nuevo archivo
 1 file changed, 1 insertion(+)

# Estado: COMMITTED (local, no aparece en status)
$ git status
On branch main
Your branch is ahead of 'origin/main' by 1 commit.
nothing to commit, working tree clean

# PASO 4: Push (subir a GitHub)
$ git push
To https://github.com/usuario/kryptonite.git
   97ff5e7..a1b2c3d  main -> main

# Estado: PUSHED (sincronizado)
$ git status
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

---

## 🛠️ Comandos para Moverse Entre Estados

### De MODIFIED a UNMODIFIED (descartar cambios)
```bash
git restore archivo.py          # ⚠️ PELIGROSO: Pierdes cambios
git checkout -- archivo.py      # Sintaxis antigua
```

### De STAGED a MODIFIED (quitar del staging)
```bash
git restore --staged archivo.py  # Mantiene cambios, quita de verde
git reset HEAD archivo.py        # Sintaxis antigua
```

### De MODIFIED a STAGED (preparar para commit)
```bash
git add archivo.py
git add .                        # Añadir TODO
```

### De STAGED a COMMITTED (guardar en repo local)
```bash
git commit -m "Mensaje descriptivo"
```

### De COMMITTED a PUSHED (subir a GitHub)
```bash
git push
git push origin main            # Explícito
```

### Deshacer último commit (mantener cambios como STAGED)
```bash
git reset --soft HEAD~1
```

### Deshacer último commit (volver a MODIFIED)
```bash
git reset HEAD~1
```

### Deshacer último commit (PERDER cambios)
```bash
git reset --hard HEAD~1         # ⚠️ PELIGROSO
```

---

## 🎓 Casos de Uso Comunes

### Caso 1: Añadir TODO de una vez

```bash
# Modificas varios archivos...

# Opción A: Añadir uno por uno
git add archivo1.py
git add archivo2.py
git add archivo3.py

# Opción B: Añadir TODO
git add .

# Commit
git commit -m "feat: múltiples cambios"

# Push
git push
```

### Caso 2: Añadir solo algunos archivos

```bash
# Modificaste 5 archivos pero solo quieres commitear 2

git add archivo1.py archivo2.py   # Solo estos dos
git commit -m "fix: corrección específica"
git push

# Los otros 3 siguen en MODIFIED (rojo)
```

### Caso 3: Revisar antes de commit

```bash
# Añadir archivos
git add .

# Ver qué se va a commitear
git status
git diff --staged

# Si algo no te gusta, quitarlo del staging
git restore --staged archivo_no_deseado.py

# Commit solo lo que quieres
git commit -m "feat: cambios revisados"
```

### Caso 4: Commit rápido de archivos ya trackeados

```bash
# Solo para archivos que YA están versionados (no nuevos)
git commit -am "fix: corrección rápida"

# Equivale a:
# git add -u  (solo archivos modificados, no nuevos)
# git commit -m "fix: corrección rápida"
```

### Caso 5: Descartar cambios que no quieres

```bash
# Editaste archivo.py pero no te gusta el cambio
git restore archivo.py          # Vuelve al último commit

# Añadiste archivos al staging pero te arrepentiste
git restore --staged .          # Quita TODO del staging

# Ya hiciste commit pero te arrepentiste (antes de push)
git reset --soft HEAD~1         # Deshace commit, mantiene cambios
```

---

## 🚨 Errores Comunes y Soluciones

### Error 1: "¿Por qué no se sube mi cambio?"

**Síntoma:**
```bash
# Editas archivo.py
# Haces push directamente
git push
# Pero GitHub no tiene tus cambios
```

**Problema:** Saltaste `git add` y `git commit`

**Solución:**
```bash
git add archivo.py
git commit -m "descripción"
git push
```

---

### Error 2: "Añadí archivos pero no se commitean"

**Síntoma:**
```bash
git add .
git push  # ❌ Error: nothing to commit
```

**Problema:** Saltaste `git commit`

**Solución:**
```bash
git add .
git commit -m "mensaje"  # ← Te faltaba esto
git push
```

---

### Error 3: "Hice commit pero no aparece en GitHub"

**Síntoma:**
```bash
git add .
git commit -m "mensaje"
# Miras GitHub y no hay cambios
```

**Problema:** Te falta el `git push`

**Solución:**
```bash
git push  # ← Faltaba este paso
```

---

### Error 4: "Git no detecta mis cambios"

**Síntoma:**
```bash
# Editas archivo.py
git status
# Output: nothing to commit, working tree clean
```

**Posibles causas:**
1. **El archivo está en `.gitignore`**
   ```bash
   git check-ignore archivo.py
   # Si devuelve algo, está ignorado
   ```

2. **No guardaste el archivo en el editor**
   - Guarda con Ctrl+S en VS Code

3. **Estás en el directorio equivocado**
   ```bash
   pwd  # Verificar dónde estás
   cd /mnt/datos/jupyter/kryptonite
   ```

---

### Error 5: "Your branch is ahead of origin/main"

**Síntoma:**
```bash
git status
# Your branch is ahead of 'origin/main' by 3 commits.
```

**Significado:**
- Tienes 3 commits en tu repo LOCAL
- Que NO están en GitHub

**Solución:**
```bash
git push  # Subir esos 3 commits
```

---

## 🎯 Mnemotecnia para Recordar el Flujo

### Regla de las 3 A's + P

```
Add → Commit → Push
(Añadir → Confirmar → Publicar)

1. ADD (git add)      → Preparar 🎒
2. COMMIT (git commit) → Empacar 📦
3. PUSH (git push)     → Enviar 🚚
```

### Analogía del Correo

```
1. MODIFIED (rojo)     = Escribes una carta
2. STAGED (verde)      = Metes la carta en sobre
3. COMMITTED           = Cierras el sobre
4. PUSHED              = Envías por correo
```

### Pregunta clave antes de cada comando

**Antes de `git add`:**
- "¿Están completos mis cambios?"

**Antes de `git commit`:**
- "¿Qué archivos he añadido al staging?"
- "¿El mensaje describe bien los cambios?"

**Antes de `git push`:**
- "¿Estoy en la rama correcta?"
- "¿Quiero que esto esté en GitHub ya?"

---

## 📊 Diagrama de Flujo Completo

```
┌──────────────────────────────────────────────────────────────┐
│                    FLUJO COMPLETO DE GIT                     │
└──────────────────────────────────────────────────────────────┘

     Editas          git add        git commit       git push
      archivo           .              -m ""
        │               │                │              │
        ↓               ↓                ↓              ↓
┌─────────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────┐
│  MODIFIED   │→ │   STAGED    │→ │COMMITTED │→ │ PUSHED   │
│   (rojo)    │  │   (verde)   │  │ (local)  │  │ (GitHub) │
└─────────────┘  └─────────────┘  └──────────┘  └──────────┘
      ↑                ↑                ↑              ↑
      │                │                │              │
  git restore    git restore      git reset      git pull
   archivo        --staged         HEAD~1
                  archivo
```

---

## ✅ Checklist para Cada Cambio

```
☐ 1. Editar archivos
☐ 2. Guardar en editor (Ctrl+S)
☐ 3. git status (verificar qué cambió)
☐ 4. git diff (ver cambios específicos)
☐ 5. git add . (o archivos específicos)
☐ 6. git status (verificar en verde)
☐ 7. git commit -m "mensaje descriptivo"
☐ 8. git status (verificar "ahead of origin")
☐ 9. git push
☐ 10. Verificar en GitHub que está actualizado
```

---

## 🎓 Ejercicio Práctico

Prueba este flujo para entender los estados:

```bash
# 1. Crear archivo
echo "Versión 1" > test.txt
git status                    # UNTRACKED (rojo)

# 2. Añadir
git add test.txt
git status                    # STAGED (verde)

# 3. Commit
git commit -m "test: versión 1"
git status                    # COMMITTED (limpio)

# 4. Editar
echo "Versión 2" >> test.txt
git status                    # MODIFIED (rojo)

# 5. Ver diferencias
git diff test.txt             # Ver cambios

# 6. Añadir
git add test.txt
git status                    # STAGED (verde)

# 7. Quitar del staging
git restore --staged test.txt
git status                    # MODIFIED (rojo) otra vez

# 8. Añadir y commit
git add test.txt
git commit -m "test: versión 2"
git status                    # COMMITTED (limpio)

# 9. Push
git push
git status                    # PUSHED (actualizado con origin)

# 10. Limpiar
git rm test.txt
git commit -m "test: eliminar archivo de prueba"
git push
```

---

**Última actualización:** 21 de Diciembre de 2024  
**Autor:** Buenos Días con asistencia de Claude (Anthropic)  
**Versión:** 1.0
