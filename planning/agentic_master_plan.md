# Plan Maestro Agentico: White-Label Open WebUI

> **Fecha**: 2026-02-12
> **Version**: 1.2
> **Arquitecto**: Claude (Opus 4.5)
> **Estado**: LISTO PARA EJECUCION
> **Path Legal**: A (< 50 usuarios) - CONFIRMADO 2026-02-12
> **Marca**: Cognitia

---

## Configuracion de Marca

| Variable | Valor |
|----------|-------|
| **BRAND_NAME** | Cognitia |
| **BRAND_SHORT** | Cognitia |
| **brand** | cognitia |
| **Dominio** | cognitia.ai |
| **Color Primary** | #3b82f6 |

---

## Gate Legal: COMPLETADO

| Item | Estado |
|------|--------|
| Path seleccionado | **A** |
| Usuarios maximos | < 50 |
| Branding removal | **AUTORIZADO** |
| Documento legal | `planning/LEGAL_DECISION.md` |

---

## Resumen Ejecutivo

Este documento presenta un plan agentico completo para transformar el fork de Open WebUI en una solucion de marca blanca con identidad visual propia (azules), Docker build personalizado, y capacidades extendidas de MCP para presentaciones.

---

## PARTE 1: ANALISIS AS-IS (Estado Actual)

### 1.1 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────────┐
│                        OPEN WEBUI FORK                              │
├─────────────────────────────────────────────────────────────────────┤
│  FRONTEND (SvelteKit + Tailwind)                                    │
│  ├── src/lib/constants/identity.ts  → APP_NAME: "Agentic WebUI"     │
│  ├── src/app.html                   → Title, Splash Screen          │
│  ├── src/app.css                    → Variables CSS                 │
│  ├── static/                        → Favicons, Splash images       │
│  └── src/lib/components/            → UI Components                 │
├─────────────────────────────────────────────────────────────────────┤
│  BACKEND (FastAPI + Python 3.11)                                    │
│  ├── backend/open_webui/config.py   → WEBUI_NAME config             │
│  ├── backend/open_webui/main.py     → FastAPI app                   │
│  └── backend/open_webui/static/     → Backend static files          │
├─────────────────────────────────────────────────────────────────────┤
│  DOCKER                                                             │
│  ├── Dockerfile                     → Multi-stage build             │
│  ├── docker-compose.yaml            → Orchestration                 │
│  └── docker-compose.*.yaml          → GPU/variants                  │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Inventario de Branding Actual

| Categoria | Ubicacion | Estado Actual | Prioridad |
|-----------|-----------|---------------|-----------|
| **Nombre App** | `src/lib/constants/identity.ts` | "Agentic WebUI" | CRITICA |
| **Tab Title** | `src/app.html:88` | "Agentic WebUI" | CRITICA |
| **Splash Screen** | `static/static/splash.png` | Logo Open WebUI | CRITICA |
| **Splash Dark** | `static/static/splash-dark.png` | Logo Open WebUI | CRITICA |
| **Favicon** | `static/static/favicon.png` | Icono Open WebUI | CRITICA |
| **Favicon Dark** | `static/static/favicon-dark.png` | Icono Open WebUI | CRITICA |
| **Favicon ICO** | `static/static/favicon.ico` | Icono Open WebUI | ALTA |
| **Favicon SVG** | `static/static/favicon.svg` | Base64 PNG | ALTA |
| **Apple Touch** | `static/static/apple-touch-icon.png` | Icono Open WebUI | ALTA |
| **PWA Icons** | `static/static/web-app-manifest-*.png` | Iconos Open WebUI | ALTA |
| **Manifest** | `static/manifest.json` | Nombres PWA | ALTA |
| **Backend Manifest** | `backend/open_webui/static/site.webmanifest` | "Open WebUI" | ALTA |
| **Colores** | `src/app.css` + `tailwind.config.js` | Stock colors | MEDIA |
| **Textos UI** | 13+ componentes Svelte | Referencias varias | MEDIA |

### 1.3 Componentes con Referencias de Marca

```
src/lib/components/
├── OnBoarding.svelte           → Logo display
├── NotificationToast.svelte    → Favicon reference
├── app/AppSidebar.svelte       → Splash/favicon logos
├── layout/Sidebar.svelte       → Logo en navegacion
├── chat/
│   ├── Placeholder.svelte      → "Agentic WebUI" text
│   ├── ChatPlaceholder.svelte  → Brand text
│   ├── ShareChatModal.svelte   → Community reference
│   ├── ToolServersModal.svelte → "Agentic WebUI can use..."
│   ├── Messages/ProfileImage.svelte → Default favicon
│   └── Settings/
│       ├── General.svelte      → Translation link
│       ├── About.svelte        → Team link
│       ├── Connections.svelte  → CORS text
│       ├── Tools.svelte        → Config text
│       └── Audio.svelte        → Feature description
├── admin/
│   ├── Functions.svelte        → "Made by Community"
│   ├── Users/UserList.svelte   → Free software message
│   └── Settings/Audio.svelte   → "uses" references
└── channel/Channel.svelte      → Title format
```

### 1.4 Docker Build Actual

```dockerfile
# Stage 1: Frontend (Node.js 22 Alpine)
FROM node:22-alpine3.20 AS build
→ npm ci && npm run build
→ Output: /app/build

# Stage 2: Runtime (Python 3.11)
FROM python:3.11.14-slim-bookworm AS base
→ System deps (ffmpeg, pandoc, etc.)
→ Python deps via uv
→ PyTorch (CPU/CUDA)
→ Embedding models download
→ Port 8080
```

**Build Args Disponibles:**
- `USE_CUDA` / `USE_CUDA_VER` - Soporte GPU NVIDIA
- `USE_OLLAMA` - Bundle Ollama
- `USE_SLIM` - Sin modelos preinstalados
- `USE_EMBEDDING_MODEL` - Modelo RAG
- `BUILD_HASH` - Version identifier

---

## PARTE 2: ANALISIS TO-BE (Estado Objetivo)

### 2.1 Nueva Identidad Visual

**Paleta de Colores (Azules Corporativos):**

```css
/* Primary Blues */
--brand-primary-50:  #eff6ff;   /* Lightest */
--brand-primary-100: #dbeafe;
--brand-primary-200: #bfdbfe;
--brand-primary-300: #93c5fd;
--brand-primary-400: #60a5fa;
--brand-primary-500: #3b82f6;   /* Primary */
--brand-primary-600: #2563eb;   /* Primary Dark */
--brand-primary-700: #1d4ed8;
--brand-primary-800: #1e40af;
--brand-primary-900: #1e3a8a;   /* Darkest */

/* Surface Colors (Dark Mode Default) */
--surface-base:      #0f172a;   /* Slate 900 */
--surface-elevated:  #1e293b;   /* Slate 800 */
--surface-overlay:   #334155;   /* Slate 700 */

/* Accent */
--accent-success:    #22c55e;
--accent-warning:    #f59e0b;
--accent-error:      #ef4444;
```

### 2.2 Nuevos Assets Requeridos

| Asset | Dimensiones | Formato | Descripcion |
|-------|-------------|---------|-------------|
| `logo.svg` | Vector | SVG | Logo principal vectorial |
| `logo-dark.svg` | Vector | SVG | Logo modo oscuro |
| `favicon.png` | 192x192 | PNG | Favicon principal |
| `favicon-dark.png` | 192x192 | PNG | Favicon modo oscuro |
| `favicon-96x96.png` | 96x96 | PNG | Favicon pequeno |
| `favicon.ico` | Multi | ICO | Favicon legacy |
| `favicon.svg` | Vector | SVG | Favicon vectorial |
| `splash.png` | 512x512 | PNG | Splash screen light |
| `splash-dark.png` | 512x512 | PNG | Splash screen dark |
| `apple-touch-icon.png` | 180x180 | PNG | iOS icon |
| `web-app-manifest-192x192.png` | 192x192 | PNG | PWA icon |
| `web-app-manifest-512x512.png` | 512x512 | PNG | PWA icon large |

### 2.3 Docker Build Personalizado

```yaml
# Nuevo: docker-compose.whitelabel.yaml
version: "3.8"
services:
  whitelabel-webui:
    build:
      context: .
      dockerfile: Dockerfile.whitelabel
      args:
        - USE_CUDA=false
        - USE_SLIM=false
        - BUILD_HASH=${GIT_COMMIT:-dev}
        - BRAND_NAME=MiBrand
    image: mibrand/ai-webui:${VERSION:-latest}
    environment:
      - WEBUI_NAME=MiBrand AI
      - WEBUI_FAVICON_URL=/static/favicon.png
    ports:
      - "${PORT:-3000}:8080"
    volumes:
      - whitelabel-data:/app/backend/data
```

### 2.4 MCP para Presentaciones (Nice to Have)

**Opciones Investigadas:**

1. **Office-PowerPoint-MCP-Server** (Recomendado)
   - GitHub: [GongRzhe/Office-PowerPoint-MCP-Server](https://github.com/GongRzhe/Office-PowerPoint-MCP-Server)
   - 34 herramientas especializadas
   - MIT License
   - Python-pptx backend

2. **SlideSpeak MCP**
   - URL: [slidespeak.co](https://slidespeak.co/blog/2025/04/02/introducing-slidespeak-mcp-for-presentations)
   - Servicio remoto (SaaS)
   - Integra con Claude Desktop

3. **FlashDocs MCP**
   - URL: [flashdocs.com](https://www.flashdocs.com/post/flashdocs-model-context-protocol-mcp)
   - Generacion automatica de decks
   - Multi-formato (PPTX, Google Slides, PDF)

---

## PARTE 3: GAP ANALYSIS

### 3.1 Brechas Identificadas

| # | Area | Gap | Impacto | Esfuerzo |
|---|------|-----|---------|----------|
| G1 | **Splash/Loading** | Logo OpenWebUI visible al cargar | ALTO | BAJO |
| G2 | **Favicon Tab** | Icono identifica como OpenWebUI | ALTO | BAJO |
| G3 | **Colores** | Paleta generica sin identidad | MEDIO | MEDIO |
| G4 | **PWA Manifest** | Nombres "Open WebUI" | MEDIO | BAJO |
| G5 | **Textos UI** | 13+ referencias en componentes | MEDIO | MEDIO |
| G6 | **Docker Build** | Sin personalizacion de marca | ALTO | MEDIO |
| G7 | **MCP Presentations** | No existe capacidad | BAJO | ALTO |
| G8 | **Backend Manifest** | site.webmanifest con branding | BAJO | BAJO |

### 3.2 Matriz de Riesgos

```
         IMPACTO
    Alto  │ G1,G2,G6 │         │
          ├──────────┼─────────┤
   Medio  │   G4,G8  │ G3,G5   │
          ├──────────┼─────────┤
    Bajo  │          │   G7    │
          └──────────┴─────────┘
              Bajo     Medio   Alto
                  ESFUERZO
```

---

## PARTE 4: PLAN AGENTICO POR ETAPAS

### ETAPA 0: VALIDACION LEGAL (Gate Obligatorio)

**Objetivo**: Confirmar Path A de licencia antes de proceder.

**Verificacion Requerida:**
- [ ] Confirmar < 50 usuarios finales en periodo de 30 dias
- [ ] O confirmar acuerdo Enterprise existente
- [ ] Documentar decision en PR/planning

**Resultado**: Path A confirmado → Proceder con eliminacion de branding

---

### ETAPA 1: IDENTIDAD VISUAL - ASSETS (Dia 1-2) ✅ COMPLETADO

> **Validado**: 2026-02-12 17:50 GMT-5
> **Documentacion**: `planning/prompts/1.2-assets-validar.md`

**Objetivo**: Crear y reemplazar todos los assets visuales.

#### Tarea 1.1: Generacion de Assets

```bash
# Directorio de trabajo
mkdir -p branding/assets/{png,svg,ico}

# Assets a crear:
# 1. Logo principal (azul sobre fondo oscuro)
# 2. Variante clara
# 3. Iconos en todas las dimensiones
```

**Especificaciones de Diseno:**
- Estilo: Minimalista, geometrico
- Color primario: #3b82f6 (blue-500)
- Color secundario: #1e40af (blue-800)
- Background: #0f172a (slate-900)

#### Tarea 1.2: Reemplazo de Archivos

| Archivo Original | Nuevo Archivo | Accion |
|------------------|---------------|--------|
| `static/static/splash.png` | `branding/splash.png` | REPLACE |
| `static/static/splash-dark.png` | `branding/splash-dark.png` | REPLACE |
| `static/static/favicon.png` | `branding/favicon-192.png` | REPLACE |
| `static/static/favicon-dark.png` | `branding/favicon-dark-192.png` | REPLACE |
| `static/static/favicon-96x96.png` | `branding/favicon-96.png` | REPLACE |
| `static/static/favicon.ico` | `branding/favicon.ico` | REPLACE |
| `static/static/favicon.svg` | `branding/favicon.svg` | REPLACE |
| `static/static/apple-touch-icon.png` | `branding/apple-touch-180.png` | REPLACE |
| `static/static/web-app-manifest-192x192.png` | `branding/pwa-192.png` | REPLACE |
| `static/static/web-app-manifest-512x512.png` | `branding/pwa-512.png` | REPLACE |
| `static/static/logo.png` | `branding/logo.png` | REPLACE |

#### Prompt Agentico 1.1:

```text
**Task**: Crear assets de marca para white-label
**Context**: Paleta azul corporativa, estilo minimalista
**Steps**:
1. Generar SVG de logo geometrico usando colores definidos
2. Exportar a PNG en todas las dimensiones requeridas
3. Crear favicon.ico multi-resolucion
4. Verificar contraste WCAG AA
**Output**: Archivos en branding/assets/
```

---

### ETAPA 2: CONFIGURACION - CONSTANTES Y MANIFESTS (Dia 2)

**Objetivo**: Actualizar todas las configuraciones textuales.

#### Tarea 2.1: identity.ts

```typescript
// src/lib/constants/identity.ts
export const APP_NAME = 'MiBrand AI';

export const BRANDING = {
  name: 'MiBrand AI',
  shortName: 'MiBrand',
  description: 'Plataforma de Inteligencia Artificial Empresarial',
  colors: {
    primary: '#3b82f6',
    primaryDark: '#1e40af',
    surface: '#0f172a',
    surfaceElevated: '#1e293b'
  },
  urls: {
    website: 'https://mibrand.ai',
    docs: 'https://docs.mibrand.ai',
    support: 'https://support.mibrand.ai'
  }
};
```

#### Tarea 2.2: manifest.json

```json
{
  "name": "MiBrand AI",
  "short_name": "MiBrand",
  "description": "Plataforma de Inteligencia Artificial Empresarial",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0f172a",
  "theme_color": "#3b82f6",
  "icons": [
    {
      "src": "/static/web-app-manifest-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/static/web-app-manifest-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

#### Tarea 2.3: Backend site.webmanifest

```json
{
  "name": "MiBrand AI",
  "short_name": "MiBrand",
  "icons": [
    {"src": "/android-chrome-192x192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "/android-chrome-512x512.png", "sizes": "512x512", "type": "image/png"}
  ],
  "theme_color": "#3b82f6",
  "background_color": "#0f172a",
  "display": "standalone"
}
```

#### Prompt Agentico 2.1:

```text
**Task**: Actualizar configuraciones de identidad
**Files**:
- src/lib/constants/identity.ts
- static/manifest.json
- backend/open_webui/static/site.webmanifest
**Action**: Reemplazar todos los valores de marca con nuevos valores
**Validation**: grep -ri "open webui" src/ static/ | grep -v planning | grep -v LICENSE
```

---

### ETAPA 3: ESTILOS - CSS Y TAILWIND (Dia 2-3)

**Objetivo**: Implementar nueva paleta de colores.

#### Tarea 3.1: Variables CSS (src/app.css)

```css
:root {
  /* Brand Colors */
  --color-brand-primary: 59 130 246;      /* blue-500 */
  --color-brand-primary-hover: 37 99 235; /* blue-600 */
  --color-brand-accent: 30 64 175;        /* blue-800 */

  /* Surface Colors */
  --color-surface-base: 15 23 42;         /* slate-900 */
  --color-surface-elevated: 30 41 59;     /* slate-800 */
  --color-surface-overlay: 51 65 85;      /* slate-700 */

  /* Text Colors */
  --color-text-primary: 248 250 252;      /* slate-50 */
  --color-text-secondary: 148 163 184;    /* slate-400 */
  --color-text-muted: 100 116 139;        /* slate-500 */
}
```

#### Tarea 3.2: tailwind.config.js

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        }
      }
    }
  }
}
```

#### Prompt Agentico 3.1:

```text
**Task**: Implementar sistema de colores de marca
**Files**: src/app.css, tailwind.config.js
**Style Guide**:
- Primary: Blue-500 (#3b82f6)
- Dark surfaces: Slate-900 (#0f172a)
- High contrast text
**Validation**: npm run build (sin errores)
```

---

### ETAPA 4: COMPONENTES - TEXTOS Y REFERENCIAS (Dia 3-4)

**Objetivo**: Actualizar todos los textos visibles en componentes.

#### Lista de Componentes a Modificar:

| Componente | Linea | Cambio |
|------------|-------|--------|
| `OnBoarding.svelte` | 22,49 | URL favicon |
| `NotificationToast.svelte` | - | Icon path |
| `AppSidebar.svelte` | 29,53 | Logo paths |
| `Sidebar.svelte` | - | Logo paths |
| `Placeholder.svelte` | - | Textos de bienvenida |
| `ChatPlaceholder.svelte` | - | Brand text |
| `ShareChatModal.svelte` | - | Community URL |
| `ToolServersModal.svelte` | - | Description text |
| `Settings/General.svelte` | - | Translation link |
| `Settings/About.svelte` | - | Team link |
| `Settings/Connections.svelte` | - | CORS text |
| `admin/Functions.svelte` | - | Community text |
| `admin/Users/UserList.svelte` | - | License text |

#### Prompt Agentico 4.1:

```text
**Task**: Actualizar referencias de marca en componentes Svelte
**Search Pattern**: grep -ri "agentic webui\|open webui" src/lib/components/
**Action**: Reemplazar con APP_NAME importado o texto generico
**Validation**: ./scripts/verify_compliance.sh
```

---

### ETAPA 5: DOCKER BUILD PERSONALIZADO (Dia 4-5)

**Objetivo**: Crear sistema de build Docker con marca blanca.

#### Tarea 5.1: Dockerfile.whitelabel

```dockerfile
# Dockerfile.whitelabel
# Build con marca personalizada

ARG NODE_VERSION=22
ARG PYTHON_VERSION=3.11.14

# ============================================
# STAGE 1: Frontend Build
# ============================================
FROM node:${NODE_VERSION}-alpine3.20 AS frontend

ARG BRAND_NAME="MiBrand AI"
ENV BRAND_NAME=${BRAND_NAME}

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias
RUN npm ci --ignore-scripts

# Copiar codigo fuente
COPY . .

# Build frontend
RUN npm run build

# ============================================
# STAGE 2: Python Runtime
# ============================================
FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime

ARG USE_CUDA=false
ARG USE_CUDA_VER=cu128
ARG USE_SLIM=false
ARG BUILD_HASH=dev
ARG BRAND_NAME="MiBrand AI"

# Environment
ENV PYTHONUNBUFFERED=1 \
    PORT=8080 \
    ENV=prod \
    WEBUI_NAME="${BRAND_NAME}" \
    BUILD_HASH=${BUILD_HASH}

WORKDIR /app/backend

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential pandoc gcc netcat-openbsd curl jq \
    ffmpeg libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY backend/ .

# Copy built frontend
COPY --from=frontend /app/build /app/build

# Health check
HEALTHCHECK CMD curl -sf http://localhost:${PORT}/health | jq -e '.status == true'

EXPOSE ${PORT}

CMD ["python", "-m", "uvicorn", "open_webui.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### Tarea 5.2: docker-compose.whitelabel.yaml

```yaml
version: "3.8"

services:
  whitelabel-ai:
    build:
      context: .
      dockerfile: Dockerfile.whitelabel
      args:
        BRAND_NAME: ${BRAND_NAME:-MiBrand AI}
        USE_CUDA: ${USE_CUDA:-false}
        USE_SLIM: ${USE_SLIM:-false}
        BUILD_HASH: ${BUILD_HASH:-dev}
    image: ${REGISTRY:-local}/mibrand-ai:${VERSION:-latest}
    container_name: mibrand-ai
    restart: unless-stopped
    environment:
      - WEBUI_NAME=${BRAND_NAME:-MiBrand AI}
      - WEBUI_SECRET_KEY=${SECRET_KEY:-changeme}
      - OLLAMA_BASE_URL=${OLLAMA_URL:-http://ollama:11434}
    ports:
      - "${PORT:-3000}:8080"
    volumes:
      - mibrand-data:/app/backend/data
    networks:
      - mibrand-network

  ollama:
    image: ollama/ollama:latest
    container_name: mibrand-ollama
    restart: unless-stopped
    volumes:
      - ollama-models:/root/.ollama
    networks:
      - mibrand-network

volumes:
  mibrand-data:
  ollama-models:

networks:
  mibrand-network:
    driver: bridge
```

#### Tarea 5.3: Scripts de Build

```bash
#!/bin/bash
# scripts/build-whitelabel.sh

set -e

# Configuracion
BRAND_NAME="${BRAND_NAME:-MiBrand AI}"
VERSION="${VERSION:-$(git describe --tags --always)}"
REGISTRY="${REGISTRY:-local}"

echo "Building ${BRAND_NAME} v${VERSION}..."

# Build
docker build \
  --build-arg BRAND_NAME="${BRAND_NAME}" \
  --build-arg BUILD_HASH="$(git rev-parse --short HEAD)" \
  --build-arg USE_CUDA="${USE_CUDA:-false}" \
  -f Dockerfile.whitelabel \
  -t "${REGISTRY}/mibrand-ai:${VERSION}" \
  -t "${REGISTRY}/mibrand-ai:latest" \
  .

echo "Build complete: ${REGISTRY}/mibrand-ai:${VERSION}"
```

#### Prompt Agentico 5.1:

```text
**Task**: Crear sistema Docker de marca blanca
**Files**:
- Dockerfile.whitelabel
- docker-compose.whitelabel.yaml
- scripts/build-whitelabel.sh
**Validation**:
- docker build -f Dockerfile.whitelabel -t test .
- docker-compose -f docker-compose.whitelabel.yaml config
```

---

### ETAPA 6: MCP PRESENTACIONES (Nice to Have) (Dia 5+)

**Objetivo**: Integrar capacidad de generacion de presentaciones via MCP.

#### Opcion Recomendada: Office-PowerPoint-MCP-Server

**Instalacion:**
```bash
pip install office-powerpoint-mcp-server
```

**Configuracion MCP:**
```json
{
  "mcpServers": {
    "powerpoint": {
      "command": "python",
      "args": ["-m", "office_powerpoint_mcp_server"],
      "env": {
        "OUTPUT_DIR": "/app/backend/data/presentations"
      }
    }
  }
}
```

**Capacidades:**
- Crear presentaciones nuevas
- Agregar slides con diferentes layouts
- Insertar texto, imagenes, tablas
- Aplicar temas y estilos
- Exportar a PPTX

#### Alternativa SaaS: SlideSpeak MCP

**Para integracion sin instalacion local:**
```json
{
  "mcpServers": {
    "slidespeak": {
      "url": "https://mcp.slidespeak.co/v1",
      "apiKey": "${SLIDESPEAK_API_KEY}"
    }
  }
}
```

#### Prompt Agentico 6.1:

```text
**Task**: Integrar MCP para presentaciones
**Options**:
1. Office-PowerPoint-MCP-Server (self-hosted)
2. SlideSpeak MCP (SaaS)
**Action**: Configurar en backend/open_webui/config.py
**Validation**: Crear presentacion de prueba via API
```

---

### ETAPA 7: VALIDACION Y QA (Dia 5-6)

**Objetivo**: Verificar cumplimiento completo.

#### Checklist de Validacion:

```bash
# 1. Verificacion de branding
./scripts/verify_compliance.sh
# Expected: exit 0, no matches

# 2. Build frontend
npm run build
# Expected: success, no errors

# 3. Build Docker
docker build -f Dockerfile.whitelabel -t test .
# Expected: success

# 4. Test visual
npm run dev &
# Verificar:
# - [ ] Tab title correcto
# - [ ] Favicon correcto
# - [ ] Splash screen sin logo OpenWebUI
# - [ ] Colores azules aplicados
# - [ ] Ningun texto "Open WebUI" visible

# 5. Test funcional
# - [ ] Login funciona
# - [ ] Chat funciona
# - [ ] Streaming funciona
```

#### Prompt Agentico 7.1:

```text
**Task**: Validacion final de compliance
**Steps**:
1. Ejecutar verify_compliance.sh
2. Build frontend y backend
3. Deploy temporal y screenshot
4. Busqueda exhaustiva de strings
**Report**: Documentar cualquier hallazgo en planning/
```

---

## PARTE 5: CRONOGRAMA RESUMIDO

```
ETAPA 0: Legal Gate          ████ (Prereq) ✅
ETAPA 1: Assets             ████████ (1-2 dias) ✅
ETAPA 2: Configuracion       ████ (0.5 dia) ✅
ETAPA 3: Estilos            ████████ (1 dia) ✅
ETAPA 4: Componentes        ████████████ (1-2 dias) ✅
ETAPA 5: Docker             ████████████ (1-2 dias) ✅
ETAPA 6: MCP (Optional)     ████████████████ (2+ dias) ⏸️ DEFERRED
ETAPA 7: QA                 ████████ (1 dia)
```

---

## PARTE 6: ARCHIVOS A CREAR/MODIFICAR

### Nuevos Archivos:
- `Dockerfile.whitelabel`
- `docker-compose.whitelabel.yaml`
- `scripts/build-whitelabel.sh`
- `branding/` (directorio con assets)

### Archivos a Modificar:
- `src/lib/constants/identity.ts`
- `src/app.html`
- `src/app.css`
- `static/manifest.json`
- `backend/open_webui/static/site.webmanifest`
- `tailwind.config.js`
- 13+ componentes Svelte

### Assets a Reemplazar:
- 12 archivos de imagen en `static/static/`

---

## PARTE 7: FUENTES Y REFERENCIAS

### MCP para Presentaciones:
- [Office-PowerPoint-MCP-Server](https://github.com/GongRzhe/Office-PowerPoint-MCP-Server)
- [SlideSpeak MCP](https://slidespeak.co/blog/2025/04/02/introducing-slidespeak-mcp-for-presentations)
- [FlashDocs MCP](https://www.flashdocs.com/post/flashdocs-model-context-protocol-mcp)
- [PowerPoint MCP Server Guide](https://skywork.ai/skypage/en/powerpoint-mcp-server-guide/1978636141368823808)

### Documentacion Tecnica:
- Open WebUI License: `LICENSE` (BSD 3-Clause + Branding Clauses)
- SvelteKit: https://kit.svelte.dev
- FastAPI: https://fastapi.tiangolo.com
- Tailwind CSS: https://tailwindcss.com

---

## Aprobacion

| Rol | Nombre | Fecha | Firma |
|-----|--------|-------|-------|
| Arquitecto | Claude (Opus 4.5) | 2026-02-12 | [AUTO] |
| Product Owner | | | |
| Tech Lead | | | |

---

> **Estado Final**: ✅ RELEASE READY - Todas las etapas completadas. Proyecto listo para despliegue.

---

## Historial de Ejecución

| Etapa | Fecha | Estado | Notas |
|-------|-------|--------|-------|
| 0 - Legal Gate | 2026-02-12 | ✅ PASS | Path A confirmado |
| 1 - Assets | 2026-02-12 | ✅ PASS | Todos los assets reemplazados |
| 2 - Config | 2026-02-12 | ✅ PASS | identity.ts, manifests actualizados |
| 3 - Estilos | 2026-02-12 | ✅ PASS | CSS/Tailwind colors implementados |
| 4 - Componentes | 2026-02-12 | ✅ PASS | 13+ componentes actualizados |
| 5 - Docker | 2026-02-13 | ✅ PASS | Build exitoso, health check pasó |
| 6 - MCP | 2026-02-12 | ⏸️ DEFERRED | python-pptx OK, MCP server no instalado |
| 7 - QA Final | 2026-02-13 | ✅ PASS | Compliance verified, build OK, Docker OK |
