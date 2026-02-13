# Prompts Agenticos v2.0 - White-Label Implementation

> **Fecha**: 2026-02-12
> **Path Legal**: A (< 50 usuarios) - CONFIRMADO
> **Total Prompts**: 14 (7 etapas x 2 prompts cada una)

---

## Instrucciones de Uso

Cada etapa tiene dos prompts:
1. **Prompt de Ejecucion (X.1)**: Realiza las tareas de la etapa
2. **Prompt de Validacion (X.2)**: Verifica que la etapa se completo correctamente

**Flujo recomendado**:
```
Ejecutar Prompt X.1 → Revisar cambios → Ejecutar Prompt X.2 → Si falla, corregir y repetir
```

---

## ETAPA 0: GATE LEGAL

### Prompt 0.1 - Ejecucion: Registrar Decision Legal

```text
**Rol**: Arquitecto de Compliance
**Contexto**: Fork de Open WebUI para marca blanca
**Decision Legal**: Path A confirmado - deployment limitado a < 50 usuarios

**Tarea**: Documentar la decision legal del proyecto

**Pasos**:
1. Leer el archivo `planning/legal_compliance.md` para entender los paths disponibles
2. Crear o actualizar el archivo `planning/LEGAL_DECISION.md` con el siguiente contenido:
   - Fecha de decision
   - Path seleccionado: A
   - Justificacion: Deployment interno/privado con menos de 50 usuarios
   - Implicaciones: Permitido remover branding visible de Open WebUI
   - Responsable: [Nombre del responsable]
3. Agregar un comentario al inicio de `planning/agentic_master_plan.md` indicando que Path A fue confirmado

**Output esperado**:
- Archivo `planning/LEGAL_DECISION.md` creado
- Plan maestro actualizado con confirmacion de Path A

**Archivos a modificar**:
- planning/LEGAL_DECISION.md (crear)
- planning/agentic_master_plan.md (actualizar header)
```

### Prompt 0.2 - Validacion: Verificar Gate Legal

```text
**Rol**: Auditor de Compliance
**Contexto**: Validar que la decision legal esta documentada correctamente

**Tarea**: Verificar documentacion del gate legal

**Pasos**:
1. Verificar que existe el archivo `planning/LEGAL_DECISION.md`
2. Confirmar que contiene:
   - [ ] Fecha de decision
   - [ ] Path seleccionado (debe ser A o B)
   - [ ] Justificacion clara
   - [ ] Implicaciones documentadas
3. Verificar que `planning/agentic_master_plan.md` tiene la confirmacion del path
4. Si Path A: Confirmar que el proyecto califica (< 50 usuarios)
5. Si Path B: Advertir que NO se puede remover branding visible

**Criterios de exito**:
- Archivo LEGAL_DECISION.md existe y esta completo
- Path documentado coincide con la realidad del proyecto
- Si Path A: Proceder con etapas siguientes
- Si Path B: Detener y ajustar plan para retener branding

**Comando de verificacion**:
cat planning/LEGAL_DECISION.md
grep -i "path" planning/agentic_master_plan.md | head -5
```

---

## ETAPA 1: IDENTIDAD VISUAL - ASSETS

### Prompt 1.1 - Ejecucion: Crear y Reemplazar Assets

```text
**Rol**: Disenador de Identidad Visual / Desarrollador Frontend
**Contexto**: Reemplazar todos los assets visuales de Open WebUI con nueva identidad

**Tarea**: Crear assets de marca y reemplazar los existentes

**Paleta de colores a usar**:
- Primary: #3b82f6 (blue-500)
- Primary Dark: #1e40af (blue-800)
- Surface: #0f172a (slate-900)
- Surface Elevated: #1e293b (slate-800)
- Text: #f8fafc (slate-50)

**Pasos**:

1. **Crear directorio de branding**:
   mkdir -p branding/source

2. **Generar favicon.svg** (logo minimalista geometrico):
   - Crear un SVG simple con forma geometrica (hexagono, cubo, o similar)
   - Usar color primary #3b82f6 sobre fondo transparente
   - Guardar en: branding/source/favicon.svg

3. **Generar versiones PNG del favicon**:
   - favicon.png (192x192)
   - favicon-dark.png (192x192) - version para modo oscuro
   - favicon-96x96.png (96x96)
   - apple-touch-icon.png (180x180)
   - web-app-manifest-192x192.png (192x192)
   - web-app-manifest-512x512.png (512x512)

4. **Generar splash screens**:
   - splash.png (512x512) - fondo claro con logo
   - splash-dark.png (512x512) - fondo #0f172a con logo

5. **Generar favicon.ico** (multi-resolucion: 16x16, 32x32, 48x48)

6. **Copiar assets a ubicaciones finales**:
   cp branding/source/favicon.png static/static/favicon.png
   cp branding/source/favicon-dark.png static/static/favicon-dark.png
   cp branding/source/favicon-96x96.png static/static/favicon-96x96.png
   cp branding/source/favicon.ico static/static/favicon.ico
   cp branding/source/favicon.svg static/static/favicon.svg
   cp branding/source/splash.png static/static/splash.png
   cp branding/source/splash-dark.png static/static/splash-dark.png
   cp branding/source/apple-touch-icon.png static/static/apple-touch-icon.png
   cp branding/source/web-app-manifest-192x192.png static/static/web-app-manifest-192x192.png
   cp branding/source/web-app-manifest-512x512.png static/static/web-app-manifest-512x512.png

7. **Actualizar favicon.svg** para que contenga SVG real (no base64 PNG):
   - Editar static/static/favicon.svg con contenido SVG vectorial

**Archivos a crear/modificar**:
- branding/source/* (nuevos assets)
- static/static/favicon.png
- static/static/favicon-dark.png
- static/static/favicon-96x96.png
- static/static/favicon.ico
- static/static/favicon.svg
- static/static/splash.png
- static/static/splash-dark.png
- static/static/apple-touch-icon.png
- static/static/web-app-manifest-192x192.png
- static/static/web-app-manifest-512x512.png
- static/static/logo.png

**Nota**: Si no puedes generar imagenes, crear placeholders y documentar especificaciones para disenador.
```

### Prompt 1.2 - Validacion: Verificar Assets

```text
**Rol**: QA Visual
**Contexto**: Validar que todos los assets fueron reemplazados correctamente

**Tarea**: Verificar integridad de assets visuales

**Pasos**:

1. **Verificar existencia de archivos**:
   ls -la static/static/favicon.png
   ls -la static/static/favicon-dark.png
   ls -la static/static/favicon-96x96.png
   ls -la static/static/favicon.ico
   ls -la static/static/favicon.svg
   ls -la static/static/splash.png
   ls -la static/static/splash-dark.png
   ls -la static/static/apple-touch-icon.png
   ls -la static/static/web-app-manifest-192x192.png
   ls -la static/static/web-app-manifest-512x512.png

2. **Verificar dimensiones de imagenes** (requiere ImageMagick o similar):
   file static/static/favicon.png  # Debe ser PNG 192x192
   file static/static/splash.png   # Debe ser PNG 512x512

3. **Verificar que favicon.svg es SVG real** (no base64):
   head -5 static/static/favicon.svg
   # Debe comenzar con <?xml o <svg, NO con data:image

4. **Verificar que las imagenes NO contienen logo de Open WebUI**:
   - Abrir cada imagen manualmente
   - Confirmar que tienen el nuevo diseno (geometrico, azul)
   - Confirmar que NO aparece el logo original de Open WebUI

5. **Test visual rapido** (opcional):
   npm run dev
   # Abrir http://localhost:5173
   # Verificar favicon en tab del navegador
   # Verificar splash screen al cargar

**Criterios de exito**:
- [ ] Todos los 12 archivos de assets existen
- [ ] Dimensiones correctas
- [ ] favicon.svg es SVG vectorial real
- [ ] Ningun asset contiene branding de Open WebUI
- [ ] Colores coinciden con paleta definida (#3b82f6)

**Si falla**: Volver a Prompt 1.1 y regenerar assets faltantes o incorrectos
```

---

## ETAPA 2: CONFIGURACION - CONSTANTES Y MANIFESTS

### Prompt 2.1 - Ejecucion: Actualizar Configuraciones

```text
**Rol**: Desarrollador de Configuracion
**Contexto**: Actualizar todas las configuraciones textuales de identidad

**Tarea**: Modificar archivos de configuracion con nueva marca

**Datos de marca a usar**:
- Nombre completo: "MiBrand AI" (o el nombre que defina el cliente)
- Nombre corto: "MiBrand"
- Descripcion: "Plataforma de Inteligencia Artificial Empresarial"
- Color primario: #3b82f6
- Color fondo: #0f172a

**Pasos**:

1. **Actualizar src/lib/constants/identity.ts**:

export const APP_NAME = 'MiBrand AI';

export const BRANDING = {
  name: 'MiBrand AI',
  shortName: 'MiBrand',
  description: 'Plataforma de Inteligencia Artificial Empresarial',
  colors: {
    primary: '#3b82f6',
    primaryDark: '#1e40af',
    primaryLight: '#60a5fa',
    surface: '#0f172a',
    surfaceElevated: '#1e293b',
    surfaceOverlay: '#334155',
    text: '#f8fafc',
    textSecondary: '#94a3b8',
    textMuted: '#64748b',
    success: '#22c55e',
    warning: '#f59e0b',
    error: '#ef4444'
  },
  urls: {
    website: 'https://mibrand.ai',
    docs: 'https://docs.mibrand.ai',
    support: 'https://support.mibrand.ai',
    community: 'https://community.mibrand.ai'
  }
};

2. **Actualizar static/manifest.json**:

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
      "type": "image/png",
      "purpose": "maskable"
    },
    {
      "src": "/static/web-app-manifest-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable"
    }
  ]
}

3. **Actualizar backend/open_webui/static/site.webmanifest**:

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

4. **Actualizar src/app.html** - titulo en <title> tag:
   Buscar: <title>Agentic WebUI</title>
   Reemplazar con: <title>MiBrand AI</title>

**Archivos a modificar**:
- src/lib/constants/identity.ts
- static/manifest.json
- backend/open_webui/static/site.webmanifest
- src/app.html
```

### Prompt 2.2 - Validacion: Verificar Configuraciones

```text
**Rol**: QA de Configuracion
**Contexto**: Validar que todas las configuraciones fueron actualizadas

**Tarea**: Verificar archivos de configuracion

**Pasos**:

1. **Verificar identity.ts**:
   cat src/lib/constants/identity.ts
   # Confirmar:
   # - APP_NAME NO contiene "Open WebUI" ni "Agentic WebUI"
   # - BRANDING.colors.primary es #3b82f6
   # - BRANDING.name coincide con APP_NAME

2. **Verificar manifest.json**:
   cat static/manifest.json
   # Confirmar:
   # - "name" NO contiene "Open WebUI"
   # - "theme_color" es #3b82f6
   # - "background_color" es #0f172a

3. **Verificar site.webmanifest**:
   cat backend/open_webui/static/site.webmanifest
   # Confirmar:
   # - "name" NO contiene "Open WebUI"

4. **Verificar app.html**:
   grep -i "<title>" src/app.html
   # Confirmar que NO contiene "Open WebUI" ni "Agentic WebUI"

5. **Busqueda exhaustiva de branding residual**:
   grep -ri "Open WebUI" src/lib/constants/
   grep -ri "Open WebUI" static/manifest.json
   grep -ri "Open WebUI" backend/open_webui/static/
   # Todos deben retornar vacio

6. **Validar JSON syntax**:
   python3 -m json.tool static/manifest.json > /dev/null && echo "manifest.json: OK"
   python3 -m json.tool backend/open_webui/static/site.webmanifest > /dev/null && echo "site.webmanifest: OK"

**Criterios de exito**:
- [ ] APP_NAME actualizado correctamente
- [ ] BRANDING object completo con colores
- [ ] manifest.json sin referencias a Open WebUI
- [ ] site.webmanifest sin referencias a Open WebUI
- [ ] app.html <title> actualizado
- [ ] Todos los JSON son validos sintacticamente

**Si falla**: Volver a Prompt 2.1 y corregir archivos con errores
```

---

## ETAPA 3: ESTILOS - CSS Y TAILWIND

### Prompt 3.1 - Ejecucion: Implementar Sistema de Colores

```text
**Rol**: Desarrollador Frontend / CSS
**Contexto**: Implementar paleta de colores corporativa en el sistema de estilos

**Tarea**: Actualizar variables CSS y configuracion de Tailwind

**Paleta completa**:
- brand-50:  #eff6ff (mas claro)
- brand-100: #dbeafe
- brand-200: #bfdbfe
- brand-300: #93c5fd
- brand-400: #60a5fa
- brand-500: #3b82f6 (PRIMARY)
- brand-600: #2563eb
- brand-700: #1d4ed8
- brand-800: #1e40af
- brand-900: #1e3a8a (mas oscuro)

**Pasos**:

1. **Actualizar src/app.css** - Agregar/modificar variables CSS:

:root {
  /* Brand Colors - Blue Corporate */
  --color-brand-50: 239 246 255;
  --color-brand-100: 219 234 254;
  --color-brand-200: 191 219 254;
  --color-brand-300: 147 197 253;
  --color-brand-400: 96 165 250;
  --color-brand-500: 59 130 246;
  --color-brand-600: 37 99 235;
  --color-brand-700: 29 78 216;
  --color-brand-800: 30 64 175;
  --color-brand-900: 30 58 138;

  /* Surface Colors - Dark Theme */
  --color-surface-base: 15 23 42;
  --color-surface-elevated: 30 41 59;
  --color-surface-overlay: 51 65 85;

  /* Text Colors */
  --color-text-primary: 248 250 252;
  --color-text-secondary: 148 163 184;
  --color-text-muted: 100 116 139;

  /* Semantic Colors */
  --color-success: 34 197 94;
  --color-warning: 245 158 11;
  --color-error: 239 68 68;
  --color-info: 59 130 246;
}

2. **Actualizar tailwind.config.js** - Extender tema:

Buscar la seccion `theme.extend` y agregar:

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
  },
  surface: {
    base: '#0f172a',
    elevated: '#1e293b',
    overlay: '#334155',
  }
}

3. **Buscar y reemplazar colores hardcodeados** en componentes:
   - Buscar: bg-gray-900, bg-slate-900 (en contextos de marca)
   - Considerar: bg-surface-base o bg-brand-900
   - Buscar: text-blue-500, text-blue-600 (colores de acento)
   - Considerar: text-brand-500, text-brand-600

4. **Verificar que el build funciona**:
   npm run build

**Archivos a modificar**:
- src/app.css
- tailwind.config.js
- Componentes con colores hardcodeados (opcional, low priority)
```

### Prompt 3.2 - Validacion: Verificar Estilos

```text
**Rol**: QA de Estilos
**Contexto**: Validar implementacion del sistema de colores

**Tarea**: Verificar que los estilos fueron aplicados correctamente

**Pasos**:

1. **Verificar variables CSS en app.css**:
   grep -E "brand-500|surface-base" src/app.css
   # Debe encontrar las definiciones de variables

2. **Verificar tailwind.config.js**:
   grep -A 15 "colors:" tailwind.config.js
   # Debe mostrar la configuracion de brand colors

3. **Ejecutar build de CSS**:
   npm run build
   # Debe completar sin errores

4. **Verificar CSS compilado** (si existe):
   ls -la build/_app/immutable/assets/
   # Archivos CSS deben existir

5. **Test visual** (recomendado):
   npm run dev
   # Abrir http://localhost:5173
   # Verificar:
   # - [ ] Colores azules aplicados en botones primarios
   # - [ ] Fondo oscuro (slate-900) en modo dark
   # - [ ] Contraste adecuado de texto
   # - [ ] Hover states funcionan correctamente

6. **Verificar contraste WCAG** (opcional):
   # Usar herramienta online como WebAIM Contrast Checker
   # Primary (#3b82f6) sobre Surface (#0f172a) = ratio > 4.5:1

**Criterios de exito**:
- [ ] Variables CSS definidas en :root
- [ ] Tailwind config extendido con brand colors
- [ ] Build completa sin errores
- [ ] Colores visibles en UI coinciden con paleta definida

**Si falla**:
- Error de build: Revisar sintaxis en app.css y tailwind.config.js
- Colores no visibles: Verificar que los componentes usan las nuevas clases
```

---

## ETAPA 4: COMPONENTES - TEXTOS Y REFERENCIAS

### Prompt 4.1 - Ejecucion: Actualizar Textos en Componentes

```text
**Rol**: Desarrollador Frontend
**Contexto**: Actualizar todos los textos visibles que hacen referencia a la marca anterior

**Tarea**: Modificar componentes Svelte con referencias de marca

**Regla general**:
- Reemplazar "Open WebUI" o "Agentic WebUI" con import de APP_NAME
- Reemplazar URLs de comunidad con URLs propias o genericas
- Mantener funcionalidad intacta

**Lista de componentes a modificar**:

1. **src/lib/components/OnBoarding.svelte**
   - Actualizar referencias a favicon URLs si estan hardcodeadas
   - Verificar que usa ${WEBUI_BASE_URL}/static/favicon.png

2. **src/lib/components/chat/Placeholder.svelte**
   - Buscar textos de bienvenida con nombre de marca
   - Reemplazar con ${APP_NAME} importado

3. **src/lib/components/chat/ChatPlaceholder.svelte**
   - Similar a Placeholder.svelte

4. **src/lib/components/chat/ShareChatModal.svelte**
   - Buscar referencias a "Open WebUI Community"
   - Reemplazar URL o remover funcionalidad de compartir a comunidad externa

5. **src/lib/components/chat/ToolServersModal.svelte**
   - Buscar "Agentic WebUI can use tools..."
   - Reemplazar con "${APP_NAME} can use tools..."

6. **src/lib/components/chat/Settings/General.svelte**
   - Buscar "Help us translate Agentic WebUI"
   - Actualizar texto o remover link

7. **src/lib/components/chat/Settings/About.svelte**
   - Buscar "Agentic WebUI Team"
   - Actualizar o remover

8. **src/lib/components/chat/Settings/Connections.svelte**
   - Buscar textos de configuracion CORS con marca
   - Generalizar texto

9. **src/lib/components/admin/Functions.svelte**
   - Buscar "Made by Agentic WebUI Community"
   - Actualizar o remover

10. **src/lib/components/admin/Users/UserList.svelte**
    - Buscar mensajes de licencia/free software
    - Actualizar texto

11. **src/lib/components/app/AppSidebar.svelte**
    - Verificar rutas de logos
    - Usar paths consistentes

12. **src/lib/components/layout/Sidebar.svelte**
    - Similar a AppSidebar

13. **src/lib/components/NotificationToast.svelte**
    - Verificar icono de notificacion

**Patron de importacion a usar en cada componente**:
import { APP_NAME } from '$lib/constants/identity';

**Patron de reemplazo**:
- Antes: "Agentic WebUI"
- Despues: {APP_NAME}

**Comando para encontrar todos los archivos**:
grep -rl "Agentic WebUI\|Open WebUI" src/lib/components/ | grep -v node_modules

**Archivos a modificar**: 13+ componentes listados arriba
```

### Prompt 4.2 - Validacion: Verificar Componentes

```text
**Rol**: QA de Componentes
**Contexto**: Validar que todos los componentes fueron actualizados

**Tarea**: Verificar ausencia de branding antiguo en componentes

**Pasos**:

1. **Ejecutar script de compliance**:
   chmod +x scripts/verify_compliance.sh
   ./scripts/verify_compliance.sh
   # Debe retornar exit 0

2. **Busqueda manual exhaustiva**:
   grep -ri "Open WebUI" src/lib/components/
   grep -ri "Agentic WebUI" src/lib/components/
   # Ambos deben retornar vacio

3. **Verificar imports de APP_NAME**:
   grep -r "APP_NAME" src/lib/components/ | head -20
   # Debe mostrar multiples componentes importando APP_NAME

4. **Verificar que no hay URLs hardcodeadas de Open WebUI**:
   grep -ri "openwebui.com" src/lib/components/
   grep -ri "open-webui" src/lib/components/ | grep -v "open_webui"
   # Debe retornar vacio (excepto referencias al backend)

5. **Build de verificacion**:
   npm run build
   # Debe completar sin errores de TypeScript/Svelte

6. **Test funcional** (recomendado):
   npm run dev
   # Navegar por la aplicacion:
   # - [ ] Pagina de login: sin marca antigua
   # - [ ] Chat principal: placeholder sin marca antigua
   # - [ ] Settings > About: sin referencia a Open WebUI team
   # - [ ] Settings > General: sin link de traduccion a Open WebUI
   # - [ ] Admin panel: sin referencias a comunidad Open WebUI

**Criterios de exito**:
- [ ] verify_compliance.sh retorna exit 0
- [ ] grep de "Open WebUI" en componentes retorna vacio
- [ ] grep de "Agentic WebUI" en componentes retorna vacio
- [ ] Build completa sin errores
- [ ] UI no muestra texto de marca antigua

**Si falla**:
- Compliance script falla: Revisar archivos reportados y actualizar
- Build falla: Revisar errores de import de APP_NAME
- UI muestra marca antigua: Buscar string especifico y ubicar componente
```

---

## ETAPA 5: DOCKER BUILD PERSONALIZADO

### Prompt 5.1 - Ejecucion: Crear Sistema Docker White-Label

```text
**Rol**: DevOps / Ingeniero de Infraestructura
**Contexto**: Crear sistema de build Docker personalizado para marca blanca

**Tarea**: Crear Dockerfile y docker-compose para builds personalizados

**Pasos**:

1. **Crear Dockerfile.whitelabel**:

# Crear archivo: Dockerfile.whitelabel

```dockerfile
# ==============================================================================
# Dockerfile.whitelabel - Build de marca blanca
# ==============================================================================
ARG NODE_VERSION=22
ARG PYTHON_VERSION=3.11.14

# ============================================
# STAGE 1: Frontend Build
# ============================================
FROM node:${NODE_VERSION}-alpine3.20 AS frontend

WORKDIR /app

# Build arguments
ARG BRAND_NAME="MiBrand AI"
ENV BRAND_NAME=${BRAND_NAME}

# Install dependencies
COPY package*.json ./
RUN npm ci --ignore-scripts

# Copy source and build
COPY . .
RUN npm run build

# ============================================
# STAGE 2: Python Runtime
# ============================================
FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime

# Build arguments
ARG USE_CUDA=false
ARG USE_CUDA_VER=cu128
ARG BUILD_HASH=dev
ARG BRAND_NAME="MiBrand AI"

# Environment
ENV PYTHONUNBUFFERED=1 \
    PORT=8080 \
    ENV=prod \
    WEBUI_NAME="${BRAND_NAME}" \
    BUILD_HASH=${BUILD_HASH} \
    SCARF_NO_ANALYTICS=true \
    DO_NOT_TRACK=true \
    ANONYMIZED_TELEMETRY=false

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential pandoc gcc netcat-openbsd curl jq \
    ffmpeg libsm6 libxext6 python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install uv for fast Python package management
RUN pip install --no-cache-dir uv

# Copy and install Python dependencies
COPY backend/requirements.txt /app/backend/
WORKDIR /app/backend
RUN uv pip install --system --no-cache -r requirements.txt

# Copy backend source
COPY backend/ /app/backend/

# Copy built frontend from stage 1
COPY --from=frontend /app/build /app/build
COPY --from=frontend /app/static /app/static

# Create data directory
RUN mkdir -p /app/backend/data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -sf http://localhost:${PORT}/health | jq -e '.status == true' || exit 1

EXPOSE ${PORT}

# Start command
CMD ["python", "-m", "uvicorn", "open_webui.main:app", "--host", "0.0.0.0", "--port", "8080", "--forwarded-allow-ips", "*"]
```

2. **Crear docker-compose.whitelabel.yaml**:

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
        BUILD_HASH: ${BUILD_HASH:-dev}
    image: ${REGISTRY:-local}/mibrand-ai:${VERSION:-latest}
    container_name: mibrand-ai
    restart: unless-stopped
    environment:
      - WEBUI_NAME=${BRAND_NAME:-MiBrand AI}
      - WEBUI_SECRET_KEY=${SECRET_KEY:-}
      - OLLAMA_BASE_URL=${OLLAMA_URL:-http://ollama:11434}
      - OPENAI_API_BASE_URL=${OPENAI_API_BASE_URL:-}
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - ENABLE_SIGNUP=${ENABLE_SIGNUP:-true}
      - DEFAULT_USER_ROLE=${DEFAULT_USER_ROLE:-pending}
    ports:
      - "${PORT:-3000}:8080"
    volumes:
      - mibrand-data:/app/backend/data
    networks:
      - mibrand-network
    depends_on:
      - ollama

  ollama:
    image: ollama/ollama:latest
    container_name: mibrand-ollama
    restart: unless-stopped
    volumes:
      - ollama-models:/root/.ollama
    networks:
      - mibrand-network
    # Uncomment for GPU support:
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: 1
    #           capabilities: [gpu]

volumes:
  mibrand-data:
    name: mibrand-data
  ollama-models:
    name: mibrand-ollama-models

networks:
  mibrand-network:
    name: mibrand-network
    driver: bridge
```

3. **Crear scripts/build-whitelabel.sh**:

```bash
#!/bin/bash
# ==============================================================================
# build-whitelabel.sh - Script de build para marca blanca
# ==============================================================================

set -e

# Configuracion por defecto
BRAND_NAME="${BRAND_NAME:-MiBrand AI}"
VERSION="${VERSION:-$(git describe --tags --always 2>/dev/null || echo 'dev')}"
REGISTRY="${REGISTRY:-local}"
USE_CUDA="${USE_CUDA:-false}"

echo "=============================================="
echo "  Building: ${BRAND_NAME}"
echo "  Version:  ${VERSION}"
echo "  Registry: ${REGISTRY}"
echo "  CUDA:     ${USE_CUDA}"
echo "=============================================="

# Build image
docker build \
  --build-arg BRAND_NAME="${BRAND_NAME}" \
  --build-arg BUILD_HASH="$(git rev-parse --short HEAD 2>/dev/null || echo 'dev')" \
  --build-arg USE_CUDA="${USE_CUDA}" \
  -f Dockerfile.whitelabel \
  -t "${REGISTRY}/mibrand-ai:${VERSION}" \
  -t "${REGISTRY}/mibrand-ai:latest" \
  .

echo ""
echo "=============================================="
echo "  Build complete!"
echo "  Image: ${REGISTRY}/mibrand-ai:${VERSION}"
echo "=============================================="
echo ""
echo "To run:"
echo "  docker-compose -f docker-compose.whitelabel.yaml up -d"
```

4. **Hacer script ejecutable**:
   chmod +x scripts/build-whitelabel.sh

5. **Crear .env.whitelabel.example**:

```env
# Branding
BRAND_NAME=MiBrand AI

# Build
VERSION=1.0.0
REGISTRY=local
USE_CUDA=false

# Runtime
PORT=3000
SECRET_KEY=your-secret-key-here
ENABLE_SIGNUP=true
DEFAULT_USER_ROLE=pending

# LLM Providers
OLLAMA_URL=http://ollama:11434
OPENAI_API_BASE_URL=
OPENAI_API_KEY=
```

**Archivos a crear**:
- Dockerfile.whitelabel
- docker-compose.whitelabel.yaml
- scripts/build-whitelabel.sh
- .env.whitelabel.example
```

### Prompt 5.2 - Validacion: Verificar Docker Build

```text
**Rol**: QA de Infraestructura
**Contexto**: Validar que el sistema Docker funciona correctamente

**Tarea**: Verificar build y deployment de Docker

**Pasos**:

1. **Verificar archivos creados**:
   ls -la Dockerfile.whitelabel
   ls -la docker-compose.whitelabel.yaml
   ls -la scripts/build-whitelabel.sh
   ls -la .env.whitelabel.example
   # Todos deben existir

2. **Validar sintaxis de Dockerfile**:
   docker build -f Dockerfile.whitelabel --check .
   # O simplemente intentar build con --dry-run si disponible

3. **Validar docker-compose**:
   docker-compose -f docker-compose.whitelabel.yaml config
   # Debe mostrar configuracion sin errores

4. **Test de build** (puede tomar varios minutos):
   BRAND_NAME="Test Brand" ./scripts/build-whitelabel.sh
   # Debe completar sin errores

5. **Verificar imagen creada**:
   docker images | grep mibrand-ai
   # Debe mostrar la imagen recien creada

6. **Test de ejecucion** (opcional pero recomendado):
   docker-compose -f docker-compose.whitelabel.yaml up -d
   sleep 30
   curl -s http://localhost:3000/health | jq .
   # Debe retornar {"status": true}

   # Verificar branding
   curl -s http://localhost:3000 | grep -i "title"
   # Debe mostrar el nuevo nombre de marca

   # Cleanup
   docker-compose -f docker-compose.whitelabel.yaml down

7. **Verificar variables de entorno en container**:
   docker run --rm local/mibrand-ai:latest env | grep WEBUI_NAME
   # Debe mostrar WEBUI_NAME=MiBrand AI

**Criterios de exito**:
- [ ] Todos los archivos Docker existen
- [ ] docker-compose config no muestra errores
- [ ] Build completa exitosamente
- [ ] Imagen aparece en docker images
- [ ] Container inicia y responde en /health
- [ ] WEBUI_NAME configurado correctamente

**Si falla**:
- Error de sintaxis: Revisar Dockerfile y docker-compose
- Build falla: Verificar que npm y pip funcionan
- Container no inicia: Revisar logs con docker logs mibrand-ai
```

---

## ETAPA 6: MCP PRESENTACIONES (NICE TO HAVE)

### Prompt 6.1 - Ejecucion: Integrar MCP PowerPoint

```text
**Rol**: Desarrollador de Integraciones
**Contexto**: Agregar capacidad de generar presentaciones via MCP

**Tarea**: Integrar Office-PowerPoint-MCP-Server

**Opcion seleccionada**: Office-PowerPoint-MCP-Server (self-hosted)
**Repositorio**: https://github.com/GongRzhe/Office-PowerPoint-MCP-Server

**Pasos**:

1. **Agregar dependencia al backend**:

   Editar backend/requirements.txt y agregar:
   office-powerpoint-mcp-server>=1.0.0
   python-pptx>=0.6.21

2. **Crear configuracion MCP** para presentaciones:

   Crear archivo: backend/open_webui/config/mcp_servers.json

   {
     "mcpServers": {
       "powerpoint": {
         "command": "python",
         "args": ["-m", "office_powerpoint_mcp_server"],
         "env": {
           "OUTPUT_DIR": "/app/backend/data/presentations",
           "DEFAULT_TEMPLATE": "professional"
         }
       }
     }
   }

3. **Crear directorio de salida**:
   mkdir -p backend/data/presentations

4. **Actualizar Dockerfile.whitelabel** para incluir dependencia:

   Agregar despues de la instalacion de requirements:
   RUN mkdir -p /app/backend/data/presentations

5. **Documentar uso** en planning/:

   Crear: planning/mcp_powerpoint_usage.md

   # MCP PowerPoint - Guia de Uso

   ## Capacidades
   - Crear presentaciones nuevas
   - Agregar slides con diferentes layouts
   - Insertar texto, imagenes, tablas
   - Aplicar temas
   - Exportar a PPTX

   ## Ejemplo de uso via API

   POST /api/v1/tools/powerpoint/create
   {
     "title": "Mi Presentacion",
     "slides": [
       {"type": "title", "title": "Bienvenidos", "subtitle": "Subtitulo"},
       {"type": "content", "title": "Agenda", "bullets": ["Item 1", "Item 2"]}
     ]
   }

   ## Ubicacion de archivos
   Los archivos generados se guardan en:
   /app/backend/data/presentations/

6. **Alternativa SaaS** (si se prefiere no instalar localmente):

   Usar SlideSpeak MCP:
   {
     "mcpServers": {
       "slidespeak": {
         "url": "https://mcp.slidespeak.co/v1",
         "headers": {
           "Authorization": "Bearer ${SLIDESPEAK_API_KEY}"
         }
       }
     }
   }

**Archivos a crear/modificar**:
- backend/requirements.txt (agregar dependencia)
- backend/open_webui/config/mcp_servers.json (crear)
- planning/mcp_powerpoint_usage.md (documentacion)
- Dockerfile.whitelabel (crear directorio)

**Nota**: Esta etapa es opcional (nice to have). Si hay problemas, puede omitirse.
```

### Prompt 6.2 - Validacion: Verificar MCP PowerPoint

```text
**Rol**: QA de Integraciones
**Contexto**: Validar integracion de MCP para presentaciones

**Tarea**: Verificar que MCP PowerPoint funciona

**Pasos**:

1. **Verificar dependencias instaladas**:
   pip show office-powerpoint-mcp-server
   pip show python-pptx
   # Ambos deben mostrar informacion del paquete

2. **Verificar configuracion MCP**:
   cat backend/open_webui/config/mcp_servers.json
   # Debe ser JSON valido con configuracion de powerpoint
   python3 -m json.tool backend/open_webui/config/mcp_servers.json

3. **Verificar directorio de salida**:
   ls -la backend/data/presentations/
   # Directorio debe existir

4. **Test de MCP server** (local):
   python -m office_powerpoint_mcp_server --help
   # Debe mostrar opciones del servidor

5. **Test de creacion de presentacion** (opcional):
   # Script de prueba
   python3 << 'EOF'
   from pptx import Presentation
   prs = Presentation()
   slide = prs.slides.add_slide(prs.slide_layouts[0])
   title = slide.shapes.title
   title.text = "Test MiBrand AI"
   prs.save("backend/data/presentations/test.pptx")
   print("Presentacion creada exitosamente")
   EOF

   ls -la backend/data/presentations/test.pptx
   # Archivo debe existir

6. **Verificar documentacion**:
   cat planning/mcp_powerpoint_usage.md
   # Debe contener guia de uso

**Criterios de exito**:
- [ ] Dependencias instaladas
- [ ] Configuracion MCP valida
- [ ] Directorio de salida existe
- [ ] Test de creacion de PPTX funciona
- [ ] Documentacion existe

**Si falla**:
- Dependencia no instala: Verificar version de Python (3.11+)
- MCP no responde: Verificar configuracion JSON
- PPTX no se crea: Verificar permisos de directorio

**Nota**: Si esta etapa falla, puede marcarse como "deferred" y continuar con Etapa 7
```

---

## ETAPA 7: VALIDACION Y QA FINAL

### Prompt 7.1 - Ejecucion: Verificacion Completa del Sistema

```text
**Rol**: QA Lead / Release Manager
**Contexto**: Validacion final antes de release

**Tarea**: Ejecutar suite completa de verificacion

**Pasos**:

1. **Ejecutar script de compliance**:
   chmod +x scripts/verify_compliance.sh
   ./scripts/verify_compliance.sh
   # DEBE retornar exit 0

2. **Build completo de frontend**:
   npm ci
   npm run build
   # DEBE completar sin errores

3. **Verificacion de build output**:
   grep -ri "Open WebUI" build/ | grep -v ".map" | head -10
   # DEBE retornar vacio

4. **Lint y format check**:
   npm run lint
   npm run format:check
   # Idealmente sin errores (warnings aceptables)

5. **Build Docker**:
   ./scripts/build-whitelabel.sh
   # DEBE completar sin errores

6. **Deploy de prueba**:
   docker-compose -f docker-compose.whitelabel.yaml up -d
   sleep 60  # Esperar inicializacion

7. **Health check**:
   curl -sf http://localhost:3000/health | jq .
   # DEBE retornar {"status": true}

8. **Captura de evidencia visual**:
   # Abrir en navegador y tomar screenshots de:
   # - Pagina de login
   # - Dashboard principal
   # - Chat con placeholder
   # - Settings > About
   # - Favicon en tab
   # Guardar en: evidence/screenshots/

9. **Verificacion visual manual**:
   # En cada screenshot verificar:
   # - [ ] NO aparece "Open WebUI" en ningun texto
   # - [ ] NO aparece logo original de Open WebUI
   # - [ ] Colores son azules (#3b82f6)
   # - [ ] Favicon es el nuevo icono
   # - [ ] Titulo del tab es correcto

10. **Cleanup**:
    docker-compose -f docker-compose.whitelabel.yaml down

11. **Documentar resultados**:
    Crear: planning/qa_report_YYYYMMDD.md

    # QA Report - [FECHA]

    ## Compliance
    - Script: PASS/FAIL
    - Build: PASS/FAIL

    ## Visual
    - Login page: PASS/FAIL
    - Dashboard: PASS/FAIL
    - Settings: PASS/FAIL

    ## Docker
    - Build: PASS/FAIL
    - Deploy: PASS/FAIL
    - Health: PASS/FAIL

    ## Issues Found
    [Lista de issues si los hay]

    ## Approval
    - [ ] Ready for release

**Archivos a crear**:
- evidence/screenshots/ (directorio con capturas)
- planning/qa_report_YYYYMMDD.md
```

### Prompt 7.2 - Validacion: Certificacion de Release

```text
**Rol**: Release Manager
**Contexto**: Certificacion final para release

**Tarea**: Validar que todos los criterios de release se cumplen

**Checklist de Release** (todos deben ser PASS):

## 1. Legal Compliance
- [ ] LEGAL_DECISION.md existe con Path A documentado
- [ ] Licencia BSD mantenida en backend
- [ ] Deployment limitado a < 50 usuarios confirmado

## 2. Branding Compliance
- [ ] verify_compliance.sh retorna exit 0
- [ ] Cero menciones de "Open WebUI" en UI
- [ ] Cero menciones de "Agentic WebUI" en UI
- [ ] Todos los assets reemplazados

## 3. Visual Identity
- [ ] Favicon muestra nuevo icono
- [ ] Splash screen muestra nuevo logo
- [ ] Colores azules (#3b82f6) aplicados
- [ ] Tab title muestra nombre correcto

## 4. Technical Quality
- [ ] npm run build: SUCCESS
- [ ] npm run lint: No critical errors
- [ ] Docker build: SUCCESS
- [ ] Docker deploy: SUCCESS
- [ ] Health endpoint: 200 OK

## 5. Documentation
- [ ] planning/agentic_master_plan.md actualizado
- [ ] planning/LEGAL_DECISION.md completo
- [ ] planning/qa_report_YYYYMMDD.md completo

## 6. MCP Integration (Optional)
- [ ] PowerPoint MCP configurado (o marcado como deferred)

**Comandos de verificacion final**:

# 1. Compliance
./scripts/verify_compliance.sh && echo "COMPLIANCE: PASS"

# 2. Build
npm run build && echo "BUILD: PASS"

# 3. Docker
docker-compose -f docker-compose.whitelabel.yaml config > /dev/null && echo "DOCKER CONFIG: PASS"

# 4. Version tag (si aplica)
git tag -a v1.0.0-whitelabel -m "White-label release"

**Criterios de certificacion**:
- TODOS los items del checklist deben ser PASS
- QA report debe indicar "Ready for release"
- Cero issues bloqueantes abiertos

**Si PASS**:
- Aprobar release
- Crear tag de version
- Documentar en CHANGELOG

**Si FAIL**:
- Documentar issues encontrados
- Regresar a etapa correspondiente
- Re-ejecutar validacion
```

---

## Resumen de Prompts

| Etapa | Prompt Ejecucion | Prompt Validacion |
|-------|------------------|-------------------|
| 0. Legal | 0.1 Registrar Decision | 0.2 Verificar Gate |
| 1. Assets | 1.1 Crear/Reemplazar | 1.2 Verificar Assets |
| 2. Config | 2.1 Actualizar Configs | 2.2 Verificar Configs |
| 3. Estilos | 3.1 Implementar Colores | 3.2 Verificar Estilos |
| 4. Componentes | 4.1 Actualizar Textos | 4.2 Verificar Componentes |
| 5. Docker | 5.1 Crear Sistema | 5.2 Verificar Build |
| 6. MCP | 6.1 Integrar PowerPoint | 6.2 Verificar MCP |
| 7. QA | 7.1 Verificacion Completa | 7.2 Certificacion |

**Total: 14 prompts**

---

## Notas de Uso

1. **Orden de ejecucion**: Siempre ejecutar en orden (0 → 7)
2. **No saltar validacion**: Cada prompt de validacion debe pasar antes de continuar
3. **Documentar fallos**: Si un prompt falla, documentar el error antes de reintentar
4. **Etapa 6 opcional**: Puede omitirse si MCP no es prioritario
5. **Path A confirmado**: Todas las etapas asumen que Path A (< 50 usuarios) esta activo

---

> Documento generado: 2026-02-12
> Version: 2.0
> Aprobado para ejecucion
