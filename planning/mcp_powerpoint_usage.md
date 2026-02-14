# Presentations Tool - Guia Operativa

> Estado real del proyecto: presentaciones se ejecuta como **builtin tool** de Open WebUI, no via endpoint MCP dedicado.

## 1) Como se habilita realmente

Para que la generacion de presentaciones funcione, deben cumplirse estas condiciones:

1. `ENABLE_PRESENTATIONS=true` en backend.
2. En el request de chat, `features.presentations=true`.
3. El modo de function calling debe ser `native` (chat o default global).

Si el modo esta en `default`, la tool de presentaciones no se inyecta como builtin y parece que "no ejecuta".

## 2) Tools disponibles

Desde `backend/open_webui/tools/presentations.py`:

- `get_available_templates`
- `get_available_icons`
- `get_story_spec_template` (nuevo)
- `generate_presentation`

## 3) Flujo recomendado (Gamma-like base)

1. Llamar `get_story_spec_template` para obtener esquema narrativo.
2. Construir `story_spec` con bloques (`cover`, `insight`, `metrics`, `comparison`, `timeline`, `cta`).
3. Llamar `generate_presentation(title, story_spec=...)`.
4. Descargar PPTX por `download_url`.

## 4) Descarga de archivos

Las presentaciones se guardan en:

- Runtime: `DATA_DIR/presentations/`
- Local tipico: `backend/data/presentations/`

Y se descargan por:

- `GET /api/v1/files/presentations/{filename}`

## 5) Troubleshooting rapido

- **No aparece o no ejecuta la tool**:
  - Validar `features.presentations=true` en payload.
  - Validar `function_calling=native`.
  - Validar `ENABLE_PRESENTATIONS=true`.
- **Genera error por contenido vacio**:
  - Enviar `slides` o `story_spec` (al menos un bloque).

## 6) Nota MCP

El archivo `backend/open_webui/config/mcp_servers.json` puede usarse para MCP externo, pero no es requisito para la tool builtin de presentaciones actual.

## 7) Nota Operativa Para Entornos Existentes

Si vienes de despliegues previos con `DEFAULT_FUNCTION_CALLING_MODE=default`, aplica esta guia:

1. Mantener `DEFAULT_FUNCTION_CALLING_MODE=default` si el modelo principal no soporta function calling nativo.
2. Cambiar a `DEFAULT_FUNCTION_CALLING_MODE=native` cuando el modelo si soporte native tools y se quiera usar Presentations builtin por defecto.
3. Verificar fallback automatico: si el modelo declara `capabilities.function_calling=false`, el backend cae a `default` sin crash.

Smoke check recomendado:

- `DEFAULT_FUNCTION_CALLING_MODE=native` -> el backend debe iniciar.
- `DEFAULT_FUNCTION_CALLING_MODE=default` -> el backend debe iniciar.
- En ambos casos, el valor debe verse en runtime como `app.state.config.DEFAULT_FUNCTION_CALLING_MODE`.
