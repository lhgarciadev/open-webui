# Etapa 3: Fix de Enlaces de Descarga

## Objetivo

Solucionar el problema de URLs con prefijo `sandbox:` que causan que los enlaces de descarga muestren `about:blank`.

**Documento previo:** [2-design-improvements.md](./2-design-improvements.md)

**Estado:** En Progreso

---

## Problema Identificado

### Síntoma

Los enlaces de descarga generados aparecen como:

```
sandbox:/api/v1/files/presentations/Presentacion_20260214_044136.pptx
```

Al hacer clic, el navegador redirige a `about:blank` porque el protocolo `sandbox:` no es reconocido.

### Causa Raíz

El modelo GPT-4o interpreta URLs relativas como `/api/v1/files/...` y les agrega el prefijo `sandbox:` internamente, creyendo que está en un entorno sandboxed.

### Impacto

- Usuarios no pueden descargar presentaciones generadas
- Experiencia de usuario degradada
- Funcionalidad core rota en producción

---

## Solución Implementada

### Cambio Principal

Convertir URLs relativas a URLs absolutas usando la URL base de la aplicación.

### Código Antes (Problemático)

```python
# presentations.py - Retorno anterior
return json.dumps({
    "status": "success",
    "message": f"Presentación '{title}' generada exitosamente con {len(prs.slides)} slides.",
    "filename": filename,
    "download_url": f"/api/v1/files/presentations/{filename}",
    "slides_count": len(prs.slides)
}, ensure_ascii=False)
```

### Código Después (Solución)

```python
# presentations.py - Retorno corregido
from open_webui.config import WEBUI_URL

def generate_presentation(..., __request__: Request = None):
    # ... generación de presentación ...

    # Build absolute download URL to prevent model from adding sandbox: prefix
    download_path = f"/api/v1/files/presentations/{filename}"

    # Determinar URL base
    base_url = ""
    if __request__:
        try:
            # Intentar obtener de la request actual
            base_url = str(__request__.base_url).rstrip('/')
        except Exception:
            pass

        # Fallback a configuración si request no tiene URL válida
        if not base_url or base_url == "http://testserver":
            try:
                webui_url = __request__.app.state.config.WEBUI_URL
                if webui_url:
                    base_url = webui_url.rstrip('/')
            except Exception:
                pass

    # Construir URL absoluta
    full_download_url = f"{base_url}{download_path}" if base_url else download_path

    return json.dumps({
        "status": "success",
        "message": f"Presentación '{title}' generada exitosamente con {len(prs.slides)} slides.",
        "filename": filename,
        "download_url": full_download_url,  # URL absoluta
        "slides_count": len(prs.slides)
    }, ensure_ascii=False)
```

---

## Configuración Requerida

### Variable de Entorno

```bash
# Railway Dashboard > Variables
WEBUI_URL=https://cognitia-production.up.railway.app
```

### Verificación

```bash
# En la consola del servidor
echo $WEBUI_URL
# Debe mostrar: https://cognitia-production.up.railway.app
```

---

## Testing

### Test Local

```bash
# 1. Configurar variable
export WEBUI_URL=http://localhost:8080

# 2. Iniciar backend
cd backend && ./dev.sh

# 3. Generar presentación via API
curl -X POST http://localhost:8080/api/v1/tools/generate_presentation \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "slides": [{"type": "title", "title": "Test"}]}'

# 4. Verificar que download_url es absoluta
# Esperado: http://localhost:8080/api/v1/files/presentations/Test_XXXXX.pptx
```

### Test en Producción

1. Ir a https://cognitia-production.up.railway.app
2. Iniciar chat con modelo configurado
3. Pedir: "Genera una presentación sobre IA"
4. Verificar que el enlace de descarga funciona

### Resultado Esperado

```json
{
	"status": "success",
	"message": "Presentación 'IA en Colombia' generada exitosamente con 6 slides.",
	"filename": "IA_en_Colombia_20260214_120000.pptx",
	"download_url": "https://cognitia-production.up.railway.app/api/v1/files/presentations/IA_en_Colombia_20260214_120000.pptx",
	"slides_count": 6
}
```

---

## Alternativas Consideradas

### Opción A: Instrucciones al Modelo (No Funcionó)

```python
return json.dumps({
    "status": "success",
    "download_url": "/api/v1/files/...",
    "user_instructions": "IMPORTANT: Show the download URL exactly as provided..."
})
```

**Resultado:** GPT-4o ignoró las instrucciones y siguió agregando `sandbox:`.

### Opción B: URLs Absolutas (Implementada)

Construir URL completa con dominio.
**Resultado:** Funciona correctamente, el modelo no modifica URLs absolutas.

### Opción C: Render en Backend

Generar HTML con enlace directamente en el backend.
**Resultado:** No implementado, requiere más cambios en el frontend.

---

## Checklist

- [x] Identificar causa raíz del problema
- [x] Implementar solución con URLs absolutas
- [x] Agregar fallbacks para diferentes entornos
- [x] Configurar `WEBUI_URL` en Railway
- [ ] Desplegar y verificar en producción
- [ ] Confirmar que descargas funcionan correctamente

---

## Troubleshooting

### URL sigue siendo relativa

1. Verificar que `WEBUI_URL` está configurada en Railway
2. Verificar que el servidor se reinició después del cambio
3. Revisar logs: `railway logs`

### Error 404 al descargar

1. Verificar que el archivo existe en `/tmp/presentations/`
2. Verificar que el endpoint `/api/v1/files/presentations/{filename}` está configurado
3. Revisar permisos del directorio

### URL con dominio incorrecto

1. Verificar valor de `WEBUI_URL` en Railway
2. Asegurar que no hay trailing slash: `https://domain.com` no `https://domain.com/`

---

## Próximo Paso

→ [Etapa 4: Validación](./4-validation.md)
