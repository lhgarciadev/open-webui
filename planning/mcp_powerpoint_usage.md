# MCP PowerPoint - Guia de Uso

> Integracion de Office-PowerPoint-MCP-Server para generacion de presentaciones

## Capacidades

- Crear presentaciones nuevas
- Agregar slides con diferentes layouts
- Insertar texto, imagenes, tablas
- Aplicar temas profesionales
- Exportar a PPTX

## Configuracion

El servidor MCP esta configurado en:
```
backend/open_webui/config/mcp_servers.json
```

### Variables de Entorno

| Variable | Valor | Descripcion |
|----------|-------|-------------|
| `OUTPUT_DIR` | `/app/backend/data/presentations` | Directorio de salida |
| `DEFAULT_TEMPLATE` | `professional` | Plantilla por defecto |

## Ejemplo de Uso via API

```bash
POST /api/v1/tools/powerpoint/create
Content-Type: application/json

{
  "title": "Mi Presentacion",
  "slides": [
    {
      "type": "title",
      "title": "Bienvenidos",
      "subtitle": "Subtitulo de la presentacion"
    },
    {
      "type": "content",
      "title": "Agenda",
      "bullets": ["Item 1", "Item 2", "Item 3"]
    },
    {
      "type": "two_column",
      "title": "Comparacion",
      "left": ["Opcion A", "Caracteristica 1"],
      "right": ["Opcion B", "Caracteristica 2"]
    }
  ]
}
```

## Ubicacion de Archivos

Los archivos generados se guardan en:
```
/app/backend/data/presentations/
```

En desarrollo local:
```
backend/data/presentations/
```

## Tipos de Slides Soportados

| Tipo | Descripcion |
|------|-------------|
| `title` | Slide de titulo con subtitulo opcional |
| `content` | Slide con titulo y viñetas |
| `two_column` | Slide de dos columnas |
| `image` | Slide con imagen principal |
| `table` | Slide con tabla de datos |

## Dependencias

Instaladas automaticamente:
- `office-powerpoint-mcp-server>=1.0.0`
- `python-pptx>=1.0.2` (ya incluida)

## Alternativa SaaS

Si se prefiere usar un servicio externo en lugar de self-hosted:

### SlideSpeak MCP

```json
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
```

Requiere:
- Cuenta en slidespeak.co
- API key configurada en variables de entorno
- Costos por uso

## Notas

- Esta integracion es opcional (nice to have)
- Repositorio original: https://github.com/GongRzhe/Office-PowerPoint-MCP-Server
- Licencia: MIT
