# Presentations V2 - Mejora Visual de Presentaciones

## Objetivo
Transformar el generador de presentaciones de Cognitia de un output "plano" (solo texto y colores) a presentaciones visualmente atractivas con imágenes, gradientes y diseno moderno tipo Gamma.

## Estado Actual (2026-02-14)

**Implementacion actual:** Reveal.js HTML (migrado desde PPTX)

Ver [ESTADO_2026-02-14.md](./ESTADO_2026-02-14.md) para detalles completos.

## Criterios de Exito
1. Presentaciones generadas incluyen imagenes relevantes automaticamente
2. Diseno visual mejorado (gradientes, shapes, mejor tipografia)
3. Enlaces de descarga funcionan correctamente
4. Multiples temas con backgrounds apropiados (dark/light/corporate)
5. UI completamente responsive, sin superposiciones
6. Costo operativo: $0 (usando APIs gratuitas)
7. Tiempo de generacion: <10 segundos

## Estructura de Etapas

| Etapa | Documento | Estado | Descripcion |
|-------|-----------|--------|-------------|
| 0 | [0-asis-tobe.md](./0-asis-tobe.md) | Completado | Analisis AS-IS / TO-BE |
| 1 | [1-unsplash-integration.md](./1-unsplash-integration.md) | Pausado | Integracion Unsplash API |
| 2 | [2-design-improvements.md](./2-design-improvements.md) | Completado | Migracion a Reveal.js |
| 3 | [3-download-fix.md](./3-download-fix.md) | Completado | Fix enlaces de descarga |
| 4 | [4-validation.md](./4-validation.md) | En Progreso | Validacion y QA |
| 5 | [5-model-selector-ux.md](./5-model-selector-ux.md) | Pendiente | Selector de modelos agrupados |
| 6 | [6-upstream-sync.md](./6-upstream-sync.md) | **NUEVO** | Sync con upstream Open WebUI |
| 7 | [7-ollama-local-deployment.md](./7-ollama-local-deployment.md) | **NUEVO** | Ollama + Phi3 para pruebas locales |

## Prompts de Ejecucion

Ver carpeta [`prompts/`](./prompts/) para prompts detallados por etapa:

### Etapas Originales

| Etapa | Ejecutar | Validar |
|-------|----------|---------|
| 1. Imagenes | [1.1](./prompts/1.1-imagenes-ejecutar.md) | [1.2](./prompts/1.2-imagenes-validar.md) |
| 2. Diseno | [2.1](./prompts/2.1-diseno-ejecutar.md) | [2.2](./prompts/2.2-diseno-validar.md) |
| 3. Download | [3.1](./prompts/3.1-download-ejecutar.md) | [3.2](./prompts/3.2-download-validar.md) |
| 4. QA Final | [4.1](./prompts/4.1-qa-final-ejecutar.md) | [4.2](./prompts/4.2-qa-final-validar.md) |
| 5. Model Selector | [5.1](./prompts/5.1-model-selector-ejecutar.md) | [5.2](./prompts/5.2-model-selector-validar.md) |

### Etapa 4 Extendida (Nuevos Issues)

| Prompt | Descripcion | Estado |
|--------|-------------|--------|
| [4.3-themes-ejecutar.md](./prompts/4.3-themes-ejecutar.md) | **Temas con backgrounds apropiados** | NUEVO |
| [4.4-responsiveness-ejecutar.md](./prompts/4.4-responsiveness-ejecutar.md) | **Responsividad del chat (sidebar)** | NUEVO |

## Issues Actuales (Prioritarios)

### Issue 1: Selector de Temas sin Backgrounds
- El cambio de tema solo modifica texto, no el fondo
- Resultado: texto ilegible
- Solucion: Prompt 4.3

### Issue 2: Sidebar Se Sobrepone al Chat
- En mobile/tablet el sidebar cubre el contenido
- No hay backdrop ni patron drawer
- Solucion: Prompt 4.4

### Issue 3: Sync con Upstream
- Necesitamos features y fixes de Open WebUI
- Preservar branding Cognitia
- Solucion: Documento 6-upstream-sync.md

## Archivos Clave

### Backend (Reveal.js Generator)
- `backend/open_webui/tools/presentations.py` - Generador principal
- `backend/open_webui/routers/files.py` - Endpoint de descarga

### Frontend (Responsividad)
- `src/lib/components/layout/Sidebar.svelte` - Sidebar
- `src/routes/(app)/+layout.svelte` - Layout principal
- `src/app.css` - Estilos globales

### Configuracion
- `planning/upstream_sync_playbook.md` - Guia de sync

## Orden de Ejecucion Recomendado

```
1. [ ] 4.5 - Desplegar Ollama + Phi3 (entorno de pruebas local)
2. [ ] 4.3 - Temas con backgrounds apropiados (fix Reveal.js)
3. [ ] 4.4 - Responsividad del chat (fix sidebar)
4. [ ] 4.6 - Sync con upstream Open WebUI (actualizar codigo)
5. [ ] 4.1/4.2 - QA FINAL (validar TODO al final)
6. [ ] 5.x - Model selector (opcional, futuro)
```

## Timeline Estimado

| Orden | Tarea | Estimacion |
|-------|-------|------------|
| 1 | 4.5 Ollama + Phi3 | 30 min - 1 hora |
| 2 | 4.3 Temas | 1-2 horas |
| 3 | 4.4 Responsividad | 2-3 horas |
| 4 | 4.6 Upstream Sync | 2-4 horas (depende de conflictos) |
| 5 | 4.1/4.2 QA Final | 1-2 horas |
| | **Total** | **7-12 horas** |

## Dependencias

### Actuales
- Reveal.js 5.0.4 (CDN)
- Google Fonts (Inter)

### Pendientes
- Unsplash API (para integracion de imagenes, Etapa 1)

## Riesgos

| Riesgo | Probabilidad | Mitigacion |
|--------|--------------|------------|
| Conflictos en sync upstream | Alta | Seguir playbook, preservar branding |
| Breakpoints incorrectos | Media | Testing en multiples dispositivos |
| Temas con bajo contraste | Baja | Validar WCAG AA |
