# 📚 Guía Completa de Git y GitHub para Kryptonite

> Documentación paso a paso de la configuración de Git/GitHub y comandos esenciales

**Fecha de configuración:** 21 de Diciembre de 2024  
**Usuario GitHub:** acabellan1868-prog  
**Repositorio:** https://github.com/acabellan1868-prog/kryptonite

---

## 📋 Tabla de Contenidos

1. [Configuración Inicial](#configuración-inicial)
2. [Proceso Completo Realizado](#proceso-completo-realizado)
3. [Comandos Git Esenciales](#comandos-git-esenciales)
4. [Workflow Diario](#workflow-diario)
5. [Resolución de Problemas Comunes](#resolución-de-problemas-comunes)
6. [Mejoras Futuras y Automatización](#mejoras-futuras-y-automatización)
7. [Buenas Prácticas](#buenas-prácticas)
8. [Recursos y Referencias](#recursos-y-referencias)

---

## 🚀 Configuración Inicial

### Arquitectura del Sistema

```
Tu PC
  ↓
Visual Studio Code
  ↓ [SSH]
Debian 12 (host)
  ↓
Docker
  ↓
Contenedor Jupyter Lab
  ↓
Volumen externo → /mnt/datos/jupyter/kryptonite/
```

### Software Instalado

- **Git:** v2.39.5 (instalado en Debian 12)
- **VS Code:** Conectado por SSH a Debian 12
- **Python:** 3.11 (en contenedor Jupyter Lab)

---

## 📝 Proceso Completo Realizado

### PASO 1: Verificar instalación de Git

```bash
git --version
# Output: git version 2.39.5
```

### PASO 2: Configurar Git (primera vez)

```bash
git config --global user.name "Buenos Días"
git config --global user.email "tu_email@example.com"

# Verificar configuración
git config --list | grep user
```

### PASO 3: Crear archivo .gitignore

**Ubicación:** `/mnt/datos/jupyter/kryptonite/.gitignore`

```bash
cat > .gitignore << 'EOF'
# Entorno virtual
.venv/
venv/
__pycache__/
*.pyc

# Variables de entorno (CRÍTICO - API KEYS)
parametros.env
.env

# Base de datos (185 MB - demasiado grande)
data/kryptonite.db
*.db

# Logs
logs/
*.log

# Modelos entrenados
*.joblib
*.pkl

# Jupyter
.ipynb_checkpoints/
*.ipynb

# Temporales
*.tmp
*.bak
.DS_Store
EOF
```

**⚠️ Crítico:** Este archivo protege secretos y archivos grandes.

### PASO 4: Hacer backup antes de inicializar

```bash
cd /mnt/datos/jupyter
tar -czf kryptonite_backup_$(date +%Y%m%d_%H%M%S).tar.gz kryptonite/
```

### PASO 5: Inicializar repositorio Git

```bash
cd /mnt/datos/jupyter/kryptonite
git init
```

**Output esperado:**
```
Inicializado repositorio Git vacío en /mnt/datos/jupyter/kryptonite/.git/
```

### PASO 6: Renombrar rama a 'main'

```bash
git branch -m main
```

### PASO 7: Resolver problema de permisos (si aparece)

Si aparece error de "posesión dudosa":

```bash
git config --global --add safe.directory /mnt/datos/jupyter/kryptonite
```

### PASO 8: Verificar archivos a versionar

```bash
git status

# Verificar que archivos sensibles están ignorados
git check-ignore data/kryptonite.db
# Debe devolver: data/kryptonite.db
```

### PASO 9: Añadir archivos al staging

```bash
# Añadir todos los archivos (respetando .gitignore)
git add .

# Verificar archivos en staging (verde)
git status
```

### PASO 10: Primer commit

```bash
git commit -m "Initial commit: Kryptonite cryptocurrency analysis system"
```

**Output esperado:**
```
[main (commit-raíz) 97ff5e7] Initial commit: Kryptonite cryptocurrency analysis system
 62 files changed, 14475 insertions(+)
```

### PASO 11: Crear repositorio en GitHub

1. Ir a: https://github.com/new
2. **Repository name:** `kryptonite`
3. **Description:** "Sistema inteligente de análisis y gestión de inversiones en criptomonedas"
4. **Visibility:** Private ✅
5. **NO** marcar "Initialize with README"
6. Click en "Create repository"

### PASO 12: Conectar repositorio local con GitHub

```bash
git remote add origin https://github.com/acabellan1868-prog/kryptonite.git

# Verificar conexión
git remote -v
```

**Output esperado:**
```
origin  https://github.com/acabellan1868-prog/kryptonite.git (fetch)
origin  https://github.com/acabellan1868-prog/kryptonite.git (push)
```

### PASO 13: Obtener Personal Access Token

1. GitHub → Settings → Developer settings
2. Personal access tokens → Tokens (classic)
3. Generate new token (classic)
4. **Note:** "Kryptonite Git Access"
5. **Expiration:** 90 days
6. **Permisos:** Marcar `repo` (completo)
7. Generate token
8. **Copiar el token** (empieza con `ghp_...`)

### PASO 14: Primer push a GitHub

```bash
git push -u origin main
```

**Autenticación:**
- **Username:** acabellan1868-prog
- **Password:** [Personal Access Token]

**Output esperado:**
```
Enumerando objetos: 77, listo.
Contando objetos: 100% (77/77), listo.
Escribiendo objetos: 100% (77/77), 368.45 KiB | 7.37 MiB/s, listo.
To https://github.com/acabellan1868-prog/kryptonite.git
 * [new branch]      main -> main
rama 'main' configurada para rastrear 'origin/main'.
```

### PASO 15: Guardar credenciales (opcional)

```bash
git config --global credential.helper store
```

⚠️ **Nota:** Guarda en texto plano en `~/.git-credentials`

### PASO 16: Añadir documentación

```bash
# Crear README.md profesional
# Crear parametros.env.example

# Pull de cambios si modificaste algo en GitHub
git pull origin main

# Añadir archivos
git add README.md parametros.env.example

# Commit
git commit -m "docs: add comprehensive README and env example"

# Push
git push
```

### PASO 17: Resolver problemas de permisos (si necesario)

```bash
# Cambiar propietario de archivos creados como root
chown -R antonio:antonio /mnt/datos/jupyter/kryptonite/
```

---

## 🎯 Comandos Git Esenciales

### Comandos de Información

```bash
# Ver estado del repositorio
git status

# Ver historial de commits
git log
git log --oneline
git log --graph --oneline --all

# Ver diferencias
git diff                    # Cambios no staged
git diff --staged          # Cambios staged
git diff HEAD              # Todos los cambios
git diff archivo.py        # Cambios en archivo específico

# Ver información de un commit
git show 97ff5e7

# Ver archivos ignorados
git status --ignored

# Ver qué archivos están trackeados
git ls-files
```

### Comandos de Staging

```bash
# Añadir archivos
git add archivo.py          # Archivo específico
git add .                   # Todo en el directorio actual
git add -A                  # Todo en el repo
git add src/                # Carpeta completa
git add *.py                # Por patrón

# Quitar del staging (unstage)
git restore --staged archivo.py
git reset HEAD archivo.py

# Descartar cambios locales (PELIGROSO)
git restore archivo.py
git checkout -- archivo.py
```

### Comandos de Commit

```bash
# Commit básico
git commit -m "Mensaje del commit"

# Commit con descripción extendida
git commit -m "Título" -m "Descripción más larga"

# Añadir y commit en un paso (solo archivos ya trackeados)
git commit -am "Mensaje"

# Modificar el último commit (antes de push)
git commit --amend -m "Nuevo mensaje"

# Modificar último commit añadiendo archivos
git add archivo_olvidado.py
git commit --amend --no-edit
```

### Comandos de Sincronización

```bash
# Descargar cambios de GitHub (sin fusionar)
git fetch origin

# Descargar y fusionar cambios
git pull origin main
git pull  # Si ya está configurado el upstream

# Subir cambios a GitHub
git push origin main
git push  # Si ya está configurado el upstream

# Forzar push (PELIGROSO - solo si sabes lo que haces)
git push --force
```

### Comandos de Branches

```bash
# Ver branches
git branch
git branch -a              # Incluye remotos
git branch -v              # Con último commit

# Crear branch
git branch nombre-branch

# Cambiar de branch
git checkout nombre-branch
git switch nombre-branch   # Comando moderno

# Crear y cambiar en un paso
git checkout -b nombre-branch
git switch -c nombre-branch

# Renombrar branch
git branch -m nuevo-nombre

# Eliminar branch
git branch -d nombre-branch
git branch -D nombre-branch  # Forzar eliminación

# Fusionar branch
git checkout main
git merge nombre-branch
```

### Comandos de Remotos

```bash
# Ver remotos
git remote -v

# Añadir remoto
git remote add origin URL

# Cambiar URL del remoto
git remote set-url origin NUEVA_URL

# Eliminar remoto
git remote remove origin

# Ver información del remoto
git remote show origin
```

### Comandos de Limpieza

```bash
# Limpiar archivos no trackeados (PELIGROSO)
git clean -n               # Ver qué se eliminaría
git clean -f               # Eliminar archivos
git clean -fd              # Eliminar archivos y directorios

# Descartar TODOS los cambios locales (PELIGROSO)
git reset --hard HEAD
git reset --hard origin/main
```

### Comandos de Historial

```bash
# Ver quién modificó cada línea
git blame archivo.py

# Buscar en el historial
git log --grep="palabra"
git log -S "código específico"

# Ver archivos en un commit específico
git show 97ff5e7:src/api.py

# Volver a un commit anterior
git checkout 97ff5e7        # Ver estado anterior
git checkout main           # Volver a main
```

---

## 🔄 Workflow Diario

### Workflow Básico

```bash
# 1. Actualizar desde GitHub (al empezar el día)
git pull

# 2. Hacer cambios en archivos...

# 3. Ver qué cambió
git status
git diff

# 4. Añadir cambios
git add .

# 5. Commit
git commit -m "feat: añadir nueva funcionalidad"

# 6. Subir a GitHub
git push
```

### Workflow con VS Code

1. **Ver cambios:** Panel "Source Control" (Ctrl+Shift+G)
2. **Stage archivos:** Click en "+" junto a cada archivo
3. **Commit:** Escribir mensaje arriba y click en "✓"
4. **Push:** Click en "..." → Push
5. **Pull:** Click en "..." → Pull

### Convención de Mensajes de Commit

Seguir el estándar **Conventional Commits**:

```bash
feat: nueva funcionalidad
fix: corrección de bug
docs: cambios en documentación
style: formato, punto y coma faltante, etc
refactor: refactorización de código
test: añadir tests
chore: tareas de mantenimiento
perf: mejoras de rendimiento
```

**Ejemplos:**
```bash
git commit -m "feat: añadir endpoint de optimización de portfolio"
git commit -m "fix: corregir cálculo de rendimiento en operaciones"
git commit -m "docs: actualizar README con nuevos endpoints"
git commit -m "refactor: reorganizar estructura de carpetas"
```

---

## 🐛 Resolución de Problemas Comunes

### Problema 1: Error de autenticación al hacer push

**Síntoma:**
```
remote: Support for password authentication was removed...
```

**Solución:**
Usar Personal Access Token en lugar de contraseña.

### Problema 2: Conflictos al hacer pull

**Síntoma:**
```
CONFLICT (content): Merge conflict in archivo.py
```

**Solución:**
```bash
# 1. Ver archivos en conflicto
git status

# 2. Abrir archivo y resolver manualmente
#    Buscar marcadores: <<<<<<< HEAD

# 3. Añadir archivo resuelto
git add archivo.py

# 4. Commit
git commit -m "fix: resolver conflicto en archivo.py"

# 5. Push
git push
```

### Problema 3: Archivo grande rechazado

**Síntoma:**
```
remote: error: File archivo.db is 185.00 MB; this exceeds GitHub's file size limit
```

**Solución:**
```bash
# 1. Añadir a .gitignore
echo "archivo.db" >> .gitignore

# 2. Quitar del repositorio
git rm --cached archivo.db

# 3. Commit
git commit -m "chore: remove large database file"

# 4. Push
git push
```

### Problema 4: Subí un secreto por error

**Solución URGENTE:**

```bash
# 1. REVOCA la API key inmediatamente en el servicio

# 2. Eliminar del historial (PELIGROSO)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch parametros.env" \
  --prune-empty --tag-name-filter cat -- --all

# 3. Force push
git push origin --force --all

# 4. Generar nueva API key
```

### Problema 5: Token expirado

**Síntoma:**
```
remote: Invalid username or password.
```

**Solución:**
1. Generar nuevo Personal Access Token en GitHub
2. Al hacer push, usar el nuevo token como password
3. Si usas credential.helper store, edita `~/.git-credentials`

### Problema 6: "Posesión dudosa" del repositorio

**Síntoma:**
```
fatal: posesión dudosa detectada en el repositorio
```

**Solución:**
```bash
git config --global --add safe.directory /ruta/al/repositorio
```

### Problema 7: Permisos incorrectos (root vs usuario)

**Solución:**
```bash
# Cambiar propietario recursivamente
chown -R antonio:antonio /mnt/datos/jupyter/kryptonite/
```

---

## 🚀 Mejoras Futuras y Automatización

### 1. Pre-commit Hooks

**Descripción:** Ejecutar validaciones antes de cada commit.

**Instalación:**
```bash
pip install pre-commit

# Crear .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=10000']
      - id: check-merge-conflict
      
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11
        
  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100']
EOF

# Instalar hooks
pre-commit install
```

**Uso:**
Ahora cada vez que hagas `git commit`, se ejecutarán automáticamente:
- Validación de formato
- Black (formateo de código)
- Flake8 (linting)
- Verificación de archivos grandes

### 2. GitHub Actions (CI/CD)

**Descripción:** Automatizar tests, linting, deployment.

**Crear:** `.github/workflows/python-app.yml`

```yaml
name: Python Application

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 src/ --count --max-line-length=100
        
    - name: Run tests
      run: |
        pip install pytest
        pytest tests/
```

### 3. Commits Automáticos Programados

**Descripción:** Backup automático diario.

**Crear script:** `scripts/auto_commit.sh`

```bash
#!/bin/bash
cd /mnt/datos/jupyter/kryptonite

# Verificar si hay cambios
if [[ -n $(git status -s) ]]; then
    git add .
    git commit -m "chore: backup automático $(date '+%Y-%m-%d %H:%M')"
    git push
    echo "✅ Backup completado: $(date)"
else
    echo "ℹ️ No hay cambios para commitear: $(date)"
fi
```

**Hacer ejecutable:**
```bash
chmod +x scripts/auto_commit.sh
```

**Añadir a cron:**
```bash
# Editar crontab
crontab -e

# Añadir línea (backup diario a las 23:00)
0 23 * * * /mnt/datos/jupyter/kryptonite/scripts/auto_commit.sh >> /var/log/kryptonite_backup.log 2>&1
```

### 4. Git Aliases (Atajos)

**Configurar:**
```bash
# Comandos más cortos
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual 'log --graph --oneline --all'

# Ver configuración
cat ~/.gitconfig
```

**Uso:**
```bash
git st              # En lugar de git status
git co main         # En lugar de git checkout main
git ci -m "msg"     # En lugar de git commit -m "msg"
git visual          # Log bonito
```

### 5. GitLens en VS Code

**Instalar extensión:**
1. VS Code → Extensions (Ctrl+Shift+X)
2. Buscar "GitLens"
3. Instalar

**Funcionalidades:**
- Ver quién modificó cada línea (blame inline)
- Historial de archivo
- Comparar branches
- Navegación de commits visual

### 6. Proteger la Rama Main

**En GitHub:**
1. Settings → Branches → Add rule
2. Branch name pattern: `main`
3. Marcar:
   - ✅ Require pull request before merging
   - ✅ Require status checks to pass
   - ✅ Require branches to be up to date

**Flujo de trabajo:**
- Trabajar en branches `feature/nombre`
- Hacer Pull Request a `main`
- Revisar y fusionar

### 7. Semantic Versioning + Tags

**Crear tags para releases:**
```bash
# Tag anotado (recomendado)
git tag -a v1.0.0 -m "Release 1.0.0: Initial stable version"

# Push tag a GitHub
git push origin v1.0.0

# Push todos los tags
git push --tags

# Ver tags
git tag

# Ver detalles de un tag
git show v1.0.0
```

### 8. Backup Automático del Repositorio

**Script:** `scripts/backup_repo.sh`

```bash
#!/bin/bash
BACKUP_DIR="/mnt/backups/kryptonite"
DATE=$(date +%Y%m%d_%H%M%S)

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Backup completo (incluyendo .git)
tar -czf $BACKUP_DIR/kryptonite_full_$DATE.tar.gz \
  -C /mnt/datos/jupyter kryptonite/

# Mantener solo últimos 7 backups
cd $BACKUP_DIR
ls -t kryptonite_full_*.tar.gz | tail -n +8 | xargs -r rm

echo "✅ Backup completado: kryptonite_full_$DATE.tar.gz"
```

**Cron semanal:**
```bash
# Todos los domingos a las 2:00 AM
0 2 * * 0 /mnt/datos/jupyter/kryptonite/scripts/backup_repo.sh
```

### 9. Git Hooks Personalizados

**Pre-push hook:** Prevenir push de archivos grandes

**Crear:** `.git/hooks/pre-push`

```bash
#!/bin/bash

# Verificar archivos grandes antes de push
large_files=$(git diff --cached --name-only --diff-filter=ACMR | \
  xargs -I {} du -k {} | awk '$1 > 10000 {print $2}')

if [ -n "$large_files" ]; then
    echo "❌ Error: Archivos demasiado grandes para subir:"
    echo "$large_files"
    echo "Añádelos a .gitignore o usa Git LFS"
    exit 1
fi

echo "✅ Verificación de tamaño completada"
exit 0
```

**Hacer ejecutable:**
```bash
chmod +x .git/hooks/pre-push
```

### 10. Integración con Notion/Obsidian

**Sincronizar documentación:**

```bash
# Script para exportar docs a Notion
#!/bin/bash
# Requiere: notion-py

python << EOF
from notion.client import NotionClient

client = NotionClient(token_v2="tu_token")
page = client.get_block("url_de_tu_pagina")

# Leer README.md
with open('README.md', 'r') as f:
    content = f.read()
    
# Actualizar página de Notion
page.children.add_new(MarkdownBlock, title=content)
EOF
```

---

## ✅ Buenas Prácticas

### Commits

✅ **Hacer commits pequeños y frecuentes**
- Cada commit = una funcionalidad o fix
- No mezclar cambios no relacionados

✅ **Mensajes descriptivos**
```bash
# ❌ Mal
git commit -m "cambios"
git commit -m "fix"

# ✅ Bien
git commit -m "feat: añadir validación de email en formulario"
git commit -m "fix: corregir cálculo de IVA en facturas"
```

✅ **Commitear código funcional**
- El código debe compilar/ejecutar
- Tests deben pasar
- No commitear código roto

### Branches

✅ **Usar branches para features**
```bash
git checkout -b feature/nuevo-endpoint
# Hacer cambios...
git push origin feature/nuevo-endpoint
# Pull Request en GitHub
```

✅ **Mantener main limpio**
- Solo código estable en `main`
- Desarrollar en branches
- Fusionar con Pull Requests

### .gitignore

✅ **Añadir antes del primer commit**
✅ **Nunca versionar:**
- Secretos (API keys, passwords)
- Archivos grandes (>10 MB)
- Archivos generados (`__pycache__`, `.pyc`)
- Configuración local específica de tu máquina

### Seguridad

✅ **Usar Personal Access Tokens**
- No usar contraseñas
- Tokens con permisos mínimos
- Renovar periódicamente

✅ **Revisar antes de push**
```bash
git diff origin/main
```

✅ **Nunca force push sin razón**
```bash
# ❌ Peligroso
git push --force

# ✅ Solo si sabes lo que haces y es necesario
git push --force-with-lease
```

### Colaboración

✅ **Pull antes de empezar a trabajar**
```bash
git pull origin main
```

✅ **Push frecuentemente**
- Al final del día
- Después de cada funcionalidad completa

✅ **Comunicar cambios grandes**
- Usar Pull Requests
- Describir cambios en el PR
- Pedir revisión de código

---

## 📚 Recursos y Referencias

### Documentación Oficial

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Docs](https://docs.github.com/)
- [Pro Git Book (Español)](https://git-scm.com/book/es/v2)

### Guías Interactivas

- [Learn Git Branching](https://learngitbranching.js.org/) - Tutorial interactivo
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [Conventional Commits](https://www.conventionalcommits.org/)

### Herramientas Útiles

- [GitKraken](https://www.gitkraken.com/) - Cliente Git visual
- [Sourcetree](https://www.sourcetreeapp.com/) - GUI de Git
- [GitLens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens) - Extensión VS Code
- [Oh My Zsh](https://ohmyz.sh/) - Shell con plugins Git

### Tutoriales en Español

- [Curso Git - Platzi](https://platzi.com/cursos/git-github/)
- [Git y GitHub - FreeCodeCamp](https://www.freecodecamp.org/espanol/news/git-y-github-guia-completa/)
- [Atlassian Git Tutorial](https://www.atlassian.com/es/git/tutorials)

---

## 🎓 Comandos de Emergencia

### Deshacer cambios (sin perder trabajo)

```bash
# Guardar cambios temporalmente
git stash
git stash list
git stash pop

# Descartar cambios en archivo específico
git restore archivo.py

# Volver al último commit (pero mantener cambios)
git reset --soft HEAD~1

# Volver al último commit (PERDER cambios)
git reset --hard HEAD~1
```

### Recuperar commits eliminados

```bash
# Ver historial completo (incluso commits "perdidos")
git reflog

# Recuperar commit
git checkout 97ff5e7
git cherry-pick 97ff5e7
```

### Limpiar repositorio

```bash
# Ver qué se limpiaría
git clean -n

# Limpiar archivos no trackeados
git clean -f

# Limpiar incluyendo directorios
git clean -fd

# Eliminar archivos ignorados
git clean -fX
```

---

## 📝 Notas Finales

### Configuración Actual del Proyecto

- **Repositorio:** https://github.com/acabellan1868-prog/kryptonite
- **Rama principal:** main
- **Token expira:** 90 días (renovar en Marzo 2025)
- **Archivos ignorados:** Ver `.gitignore`
- **Backup local:** `/mnt/datos/jupyter/kryptonite_backup_*.tar.gz`

### Contactos y Soporte

- **Documentación del proyecto:** `documentacion/project-overview.md`
- **Roadmap:** `documentacion/roadmap-2025.md`
- **Issues GitHub:** https://github.com/acabellan1868-prog/kryptonite/issues

---

**Última actualización:** 21 de Diciembre de 2024  
**Versión del documento:** 1.0  
**Autor:** Buenos Días con asistencia de Claude (Anthropic)
