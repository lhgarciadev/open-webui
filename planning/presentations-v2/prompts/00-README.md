# Prompts - Presentations V2 (Mejora Visual Premium)

> Estructura: 6 etapas, 2 prompts por etapa (ejecutar/validar).
> Objetivo: Transformar presentaciones "planas" a diseno premium tipo Gamma.
> Costo objetivo: $0 (APIs gratuitas + modelos locales)

## Flujo de Ejecucion

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Ejecutar   │ ──► │  Revisar    │ ──► │  Validar    │
│  X.Y-*.md   │     │  cambios    │     │  X.Y-*.md   │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                          ┌───────────────────┴───────────────────┐
                          ▼                                       ▼
                    [PASS] ──► Siguiente etapa            [FAIL] ──► Corregir y repetir
```

## Indice de Etapas

### Etapas Originales (1-3)

| Etapa | Descripcion                              | Ejecutar                          | Validar                          | Estado     |
| ----- | ---------------------------------------- | --------------------------------- | -------------------------------- | ---------- |
| 1     | Integracion Imagenes (Unsplash + Pexels) | [1.1](./1.1-imagenes-ejecutar.md) | [1.2](./1.2-imagenes-validar.md) | Pausado    |
| 2     | Mejoras de Diseno (gradientes, shapes)   | [2.1](./2.1-diseno-ejecutar.md)   | [2.2](./2.2-diseno-validar.md)   | Completado |
| 3     | Fix de Descarga (URLs absolutas)         | [3.1](./3.1-download-ejecutar.md) | [3.2](./3.2-download-validar.md) | Completado |

### Etapa 4 - Mejoras y QA (Actual)

| Orden | Sub-etapa | Descripcion                | Ejecutar                                | Validar                                  | Estado    |
| ----- | --------- | -------------------------- | --------------------------------------- | ---------------------------------------- | --------- |
| 1     | 4.5       | **Ollama + Phi3 local**    | [4.5](./4.5-ollama-ejecutar.md)         | [4.5-v](./4.5-ollama-validar.md)         | **NUEVO** |
| 2     | 4.3       | **Temas con backgrounds**  | [4.3](./4.3-themes-ejecutar.md)         | [4.3-v](./4.3-themes-validar.md)         | **NUEVO** |
| 3     | 4.4       | **Responsividad del chat** | [4.4](./4.4-responsiveness-ejecutar.md) | [4.4-v](./4.4-responsiveness-validar.md) | **NUEVO** |
| 4     | 4.6       | **Sync con upstream**      | [4.6](./4.6-upstream-sync-ejecutar.md)  | [4.6-v](./4.6-upstream-sync-validar.md)  | **NUEVO** |
| 5     | 4.1/4.2   | **QA FINAL (ultimo)**      | [4.1](./4.1-qa-final-ejecutar.md)       | [4.2](./4.2-qa-final-validar.md)         | Pendiente |

### Etapa 5 - Model Selector (Futuro)

| Etapa | Descripcion                   | Ejecutar                                | Validar                                | Estado    |
| ----- | ----------------------------- | --------------------------------------- | -------------------------------------- | --------- |
| 5     | Selector de modelos agrupados | [5.1](./5.1-model-selector-ejecutar.md) | [5.2](./5.2-model-selector-validar.md) | Pendiente |

## Orden de Ejecucion Recomendado

```
1. [ ] 4.5 - Desplegar Ollama + Phi3 (entorno de pruebas local)
2. [ ] 4.3 - Temas con backgrounds apropiados (fix Reveal.js)
3. [ ] 4.4 - Responsividad del chat (fix sidebar)
4. [ ] 4.6 - Sync con upstream Open WebUI (actualizar codigo)
5. [ ] 4.1/4.2 - QA FINAL (validar TODO al final)
6. [ ] 5.1/5.2 - Model selector (opcional, futuro)
```

## Resumen de Issues Actuales

| Issue             | Prompt | Descripcion                                  |
| ----------------- | ------ | -------------------------------------------- |
| Temas ilegibles   | 4.3    | Selector de tema no cambia background        |
| Sidebar sobrepone | 4.4    | En mobile el sidebar cubre el chat           |
| Pruebas locales   | 4.5    | Necesitamos Ollama para pruebas de seguridad |
| Desactualizado    | 4.6    | Necesitamos features de upstream             |

## Dependencias entre Etapas

```
4.5 (Ollama) ──────► Permite probar todo localmente
       │
       ▼
4.3 (Temas) ──────► Reveal.js genera temas correctos
       │
       ▼
4.4 (Responsive) ──► UI funciona en todas las resoluciones
       │
       ▼
4.6 (Sync) ───────► Actualizar con upstream (nuevas features)
       │
       ▼
4.1/4.2 (QA) ─────► VALIDACION FINAL DE TODO
       │
       ▼
5.x (Model Selector) ► Mejora UX de seleccion de modelos (futuro)
```

## Archivos de Referencia

- **Plan completo:** [`../README.md`](../README.md)
- **Estado actual:** [`../ESTADO_2026-02-14.md`](../ESTADO_2026-02-14.md)
- **AS-IS/TO-BE:** [`../0-asis-tobe.md`](../0-asis-tobe.md)
- **Ollama deployment:** [`../7-ollama-local-deployment.md`](../7-ollama-local-deployment.md)
- **Upstream sync:** [`../6-upstream-sync.md`](../6-upstream-sync.md)

## Codigo Principal

| Archivo                                     | Descripcion          |
| ------------------------------------------- | -------------------- |
| `backend/open_webui/tools/presentations.py` | Generador Reveal.js  |
| `backend/open_webui/routers/files.py`       | Endpoint de descarga |
| `src/lib/components/layout/Sidebar.svelte`  | Sidebar del chat     |
| `src/routes/(app)/+layout.svelte`           | Layout principal     |
| `src/app.css`                               | Estilos globales     |

## Variables de Entorno

```bash
# Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434

# APIs de imagenes (opcional)
UNSPLASH_ACCESS_KEY=xxx
PEXELS_API_KEY=xxx

# Ya configurados
WEBUI_URL=https://cognitia-production.up.railway.app
```

## Criterios de Exito Global

### Presentaciones (Reveal.js)

- [ ] Temas dark/light/corporate con backgrounds correctos
- [ ] Texto legible en todos los temas (WCAG AA)
- [ ] Footer con branding "Powered by Cognitia"
- [ ] Descargas funcionan al 100%

### UI/UX

- [ ] Sidebar no sobrepone contenido en ninguna resolucion
- [ ] Drawer pattern en mobile con backdrop
- [ ] Transiciones suaves
- [ ] Responsive en 375px - 1920px

### Infraestructura

- [ ] Ollama + Phi3 funcionando localmente
- [ ] Pruebas de seguridad pasan (sin trafico externo)
- [ ] Sync con upstream sin regresiones
- [ ] Branding Cognitia preservado

### Performance

- [ ] Tiempo de generacion < 30 segundos
- [ ] Respuesta de modelo local < 30 segundos
- [ ] Build sin errores de tipos
