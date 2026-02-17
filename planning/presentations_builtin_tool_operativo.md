# Presentations Builtin Tool - Operativa Real

## Estado actual

La generación de presentaciones funciona como **builtin tool** del backend (`backend/open_webui/tools/presentations.py`).
No requiere endpoint MCP dedicado para crear PPTX.

## Entradas soportadas por `generate_presentation`

- `title` (requerido)
- `slides` (opcional)
- `story_spec` (opcional)

`slides` y `story_spec` aceptan estos formatos:

- `list[dict]`
- `dict` (se normaliza a lista de un elemento)
- `string` JSON (se parsea y normaliza)

Si `slides` no trae contenido válido y `story_spec` sí, se construyen slides desde `story_spec`.

## Validación de contenido

La tool devuelve error cuando no hay contenido renderizable:

- sin `slides` y sin `story_spec`
- estructuras vacías
- slides sin texto útil (por ejemplo, títulos/bullets/quote/stats vacíos)

Respuesta de error esperada:

```json
{
	"success": false,
	"error": "No slide content provided. Send non-empty 'slides' or 'story_spec'."
}
```

## Descarga de archivo

La salida exitosa mantiene:

- `download_url`: `/api/v1/files/presentations/{filename}`
- escritura en `DATA_DIR/presentations`

Endpoint de descarga:

- `GET /api/v1/files/presentations/{filename}`

## Flujo recomendado

1. Activar `features.presentations=true` en chat.
2. Usar `function_calling=native`.
3. Llamar `generate_presentation` con `slides` o `story_spec`.
4. Descargar el archivo usando `download_url`.
