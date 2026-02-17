# Etapa 6: Sincronizacion con Upstream Open WebUI

## Objetivo

Integrar cambios del repositorio oficial `open-webui/open-webui` en nuestro fork de Cognitia, preservando todas las customizaciones de branding y features propias.

**Referencia:** `planning/upstream_sync_playbook.md`

---

## Pre-requisitos

### Verificar Estado Limpio

```bash
# Verificar que no hay cambios sin commitear
git status

# Si hay cambios, commitear o stashear
git stash  # o
git add . && git commit -m "WIP: guardar cambios antes de sync"
```

### Verificar Remote Upstream

```bash
# Ver remotes configurados
git remote -v

# Si no existe upstream, agregarlo
git remote add upstream https://github.com/open-webui/open-webui.git
```

---

## Proceso de Sync (Paso a Paso)

### Paso 1: Crear Branch de Sync

```bash
# Obtener ultima version de upstream
git fetch upstream

# Crear branch de sync con fecha
git checkout main
git pull origin main
git checkout -b sync/upstream-20260214
```

### Paso 2: Merge de Upstream

```bash
# Mergear upstream/main
git merge upstream/main
```

### Paso 3: Resolver Conflictos

**Prioridad de Resolucion:**

| Archivo                         | Accion            | Notas                     |
| ------------------------------- | ----------------- | ------------------------- |
| `src/lib/constants/identity.ts` | **KEEP OURS**     | Branding Cognitia         |
| `static/favicon*`               | **KEEP OURS**     | Assets Cognitia           |
| `static/logo*`                  | **KEEP OURS**     | Assets Cognitia           |
| `backend/open_webui/static/*`   | **KEEP OURS**     | Assets backend            |
| `src/app.css`                   | **MERGE CAREFUL** | Preservar brand colors    |
| `tailwind.config.js`            | **MERGE CAREFUL** | Preservar brand tokens    |
| `package.json`                  | **USE UPSTREAM**  | Dependencias actualizadas |
| `backend/requirements.txt`      | **USE UPSTREAM**  | Dependencias Python       |
| `backend/open_webui/*.py`       | **MERGE CAREFUL** | Revisar caso por caso     |
| `.env.example`                  | **MERGE**         | Agregar nuevas vars       |

**Archivos Criticos a Preservar (NO usar upstream):**

```
src/lib/constants/identity.ts
src/routes/auth/+page.svelte (si tiene branding)
static/favicon.ico
static/favicon.png
static/favicon.svg
static/logo.png
static/splash.png
static/apple-touch-icon.png
backend/open_webui/static/*
planning/*
CLAUDE.md
```

### Paso 4: Verificar Compilacion

```bash
# Frontend
npm install
npm run build
npm run check

# Backend
cd backend
pip install -r requirements.txt
python -c "from open_webui.main import app; print('OK')"
```

### Paso 5: Verificar Compliance

```bash
# Buscar referencias a "Open WebUI" que no deberian existir
./scripts/verify_compliance.sh

# Si hay violaciones, corregir
grep -r "Open WebUI" src/ --include="*.svelte" --include="*.ts"
```

### Paso 6: Test Local

```bash
# Iniciar backend
cd backend && ./dev.sh &

# Iniciar frontend
npm run dev

# Verificar:
# - Login funciona
# - Chat funciona
# - Branding Cognitia visible
# - Presentations tool funciona
```

### Paso 7: Merge a Main

```bash
# Si todo funciona, merge via PR o local
git checkout main
git merge sync/upstream-20260214

# Opcional: tag de sync
git tag sync-20260214
git push origin main --tags
```

---

## Resolucion de Conflictos Comunes

### Conflicto en `package.json`

```bash
# Usar version de upstream pero mantener nombre
git checkout --theirs package.json

# Editar manualmente para restaurar:
# - "name": "cognitia" (no "open-webui")
# - Dependencias custom si hay
```

### Conflicto en `app.css`

```bash
# Ver diferencias
git diff HEAD MERGE_HEAD -- src/app.css

# Merge manual:
# 1. Mantener brand-* variables
# 2. Aceptar nuevos estilos de upstream
# 3. Resolver conflictos de selectores
```

### Conflicto en Componentes Svelte

```bash
# Para cada archivo:
git diff HEAD MERGE_HEAD -- src/lib/components/XYZ.svelte

# Reglas:
# - Si tiene APP_NAME o branding -> preservar nuestro codigo
# - Si es logica/funcionalidad -> usar upstream
# - Si es mixto -> merge manual cuidadoso
```

---

## Checklist Post-Sync

```
BUILD
[ ] npm install exitoso
[ ] npm run build exitoso
[ ] npm run check sin errores de tipos
[ ] Backend inicia sin errores

BRANDING
[ ] Logo Cognitia en navbar
[ ] Favicon Cognitia
[ ] Titulo "Cognitia" en tab
[ ] Sin referencias a "Open WebUI"

FUNCIONALIDAD
[ ] Login funciona
[ ] Chat funciona
[ ] Models se cargan
[ ] Presentations tool funciona
[ ] Settings funcionan

COMPLIANCE
[ ] verify_compliance.sh pasa
[ ] No hay assets de Open WebUI
```

---

## Rollback si Algo Sale Mal

```bash
# Si el merge fue un desastre
git merge --abort

# Si ya commiteaste pero no pusheaste
git reset --hard HEAD~1

# Si ya pusheaste (PELIGROSO)
git revert <merge-commit>
# o
git reset --hard <commit-antes-de-merge>
git push --force  # SOLO si nadie mas trabaja en el repo
```

---

## Frecuencia Recomendada

- **Sync mensual:** Para features y fixes no criticos
- **Sync inmediato:** Si hay CVE o security fix en upstream
- **Antes de major release:** Asegurar estar actualizado

---

## Prompts Relacionados

| Prompt                               | Usar cuando                  |
| ------------------------------------ | ---------------------------- |
| Este documento                       | Sync programado              |
| `planning/compliance_checklist.md`   | Verificar branding post-sync |
| `planning/upstream_sync_playbook.md` | Referencia rapida            |

---

## Notas Importantes

1. **NUNCA hacer push directo a main sin testing**
2. **SIEMPRE crear branch de sync primero**
3. **SIEMPRE verificar compliance despues del merge**
4. **Preferir merge sobre rebase** (historial mas claro)
5. **Documentar conflictos importantes** en este archivo

---

## Historial de Syncs

| Fecha      | Commit Upstream | Conflictos | Notas                   |
| ---------- | --------------- | ---------- | ----------------------- |
| 2026-02-14 | (pendiente)     | -          | Primer sync documentado |

---

## Recursos

- [Open WebUI Releases](https://github.com/open-webui/open-webui/releases)
- [Open WebUI Changelog](https://github.com/open-webui/open-webui/blob/main/CHANGELOG.md)
- [Git Merge vs Rebase](https://www.atlassian.com/git/tutorials/merging-vs-rebasing)
