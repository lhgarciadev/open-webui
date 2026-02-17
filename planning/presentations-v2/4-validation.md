# Etapa 4: Validación y QA

## Objetivo

Verificar que todas las mejoras implementadas funcionan correctamente en producción antes del release final.

**Documento previo:** [3-download-fix.md](./3-download-fix.md)

---

## Plan de Validación

### Fase 1: Testing Unitario

#### Tests de Unsplash Client

```python
# tests/test_unsplash.py

import pytest
import os

@pytest.fixture
def skip_without_api_key():
    if not os.environ.get("UNSPLASH_ACCESS_KEY"):
        pytest.skip("UNSPLASH_ACCESS_KEY not configured")

class TestKeywordExtraction:
    def test_removes_stopwords_spanish(self):
        from open_webui.utils.unsplash import extract_keywords
        result = extract_keywords("Introducción a la Inteligencia Artificial")
        assert "introducción" not in result.lower()
        assert "inteligencia" in result.lower() or "artificial" in result.lower()

    def test_removes_stopwords_english(self):
        from open_webui.utils.unsplash import extract_keywords
        result = extract_keywords("The future of artificial intelligence")
        assert "the" not in result.lower()
        assert "future" in result.lower() or "artificial" in result.lower()

    def test_limits_keywords(self):
        from open_webui.utils.unsplash import extract_keywords
        result = extract_keywords("palabra1 palabra2 palabra3 palabra4 palabra5")
        words = result.split()
        assert len(words) <= 3

class TestUnsplashAPI:
    @pytest.mark.asyncio
    async def test_search_returns_image_data(self, skip_without_api_key):
        from open_webui.utils.unsplash import search_image
        result = await search_image("technology")
        assert result is not None
        assert "url" in result
        assert "photographer_name" in result

    @pytest.mark.asyncio
    async def test_search_handles_no_results(self, skip_without_api_key):
        from open_webui.utils.unsplash import search_image
        result = await search_image("xyznonexistentkeyword123456")
        # Puede retornar None o resultado parcial
        # No debe lanzar excepción

    @pytest.mark.asyncio
    async def test_download_image(self, skip_without_api_key):
        from open_webui.utils.unsplash import search_image, download_image
        search_result = await search_image("office")
        if search_result:
            image_bytes = await download_image(search_result["url"])
            assert image_bytes is not None
            assert len(image_bytes) > 1000  # Al menos 1KB
```

#### Tests de Generación PPTX

```python
# tests/test_presentations.py

import pytest
from pptx import Presentation
from pptx.util import Inches
import io

class TestGradientBackground:
    def test_gradient_applied(self):
        from open_webui.tools.presentations import _apply_gradient_background
        # Test implementation

class TestModernLayouts:
    def test_title_slide_modern(self):
        from open_webui.tools.presentations import _add_title_slide_modern
        # Test implementation

    def test_content_slide_modern(self):
        from open_webui.tools.presentations import _add_content_slide_modern
        # Test implementation

class TestURLGeneration:
    def test_absolute_url_with_base(self):
        # Verificar que se genera URL absoluta
        pass

    def test_fallback_to_relative(self):
        # Verificar fallback cuando no hay base URL
        pass
```

### Fase 2: Testing de Integración

#### Checklist de Integración

| Test              | Comando/Acción           | Resultado Esperado        |
| ----------------- | ------------------------ | ------------------------- |
| Backend inicia    | `cd backend && ./dev.sh` | Sin errores de import     |
| Unsplash conecta  | Generar presentación     | Imágenes se descargan     |
| PPTX válido       | Abrir en PowerPoint      | Sin errores de corrupción |
| URL absoluta      | Verificar JSON response  | URL completa con dominio  |
| Descarga funciona | Click en enlace          | Archivo se descarga       |

#### Script de Test de Integración

```bash
#!/bin/bash
# scripts/test_presentations_integration.sh

echo "=== Testing Presentations V2 Integration ==="

# 1. Check dependencies
echo "1. Checking dependencies..."
pip show httpx python-pptx pillow || exit 1

# 2. Check environment
echo "2. Checking environment..."
if [ -z "$UNSPLASH_ACCESS_KEY" ]; then
    echo "WARNING: UNSPLASH_ACCESS_KEY not set, images will be skipped"
fi

# 3. Run unit tests
echo "3. Running unit tests..."
cd backend && pytest tests/test_presentations.py tests/test_unsplash.py -v

# 4. Generate test presentation
echo "4. Generating test presentation..."
python -c "
from open_webui.tools.presentations import generate_presentation
import json

result = generate_presentation(
    title='Test Presentation V2',
    slides=[
        {'type': 'title', 'title': 'Test', 'subtitle': 'Integration Test'},
        {'type': 'content', 'title': 'Content', 'bullets': ['Point 1', 'Point 2']},
        {'type': 'stats', 'title': 'Stats', 'stats': [{'value': '100%', 'label': 'Test'}]}
    ]
)
print(json.loads(result))
"

echo "=== Integration Test Complete ==="
```

### Fase 3: Testing Manual en Producción

#### Casos de Prueba

##### Caso 1: Presentación Simple

```
Prompt: "Genera una presentación de 3 slides sobre inteligencia artificial"

Verificar:
[ ] Presentación se genera sin errores
[ ] Enlace de descarga funciona
[ ] Archivo PPTX válido
[ ] Imágenes incluidas (si API key configurada)
[ ] Gradientes visibles
```

##### Caso 2: Presentación con Estadísticas

```
Prompt: "Crea una presentación con estadísticas del mercado colombiano de tecnología"

Verificar:
[ ] Slide de stats tiene formato de cards
[ ] Números grandes visibles
[ ] Diseño moderno aplicado
```

##### Caso 3: Presentación Larga

```
Prompt: "Genera una presentación completa de 10 slides sobre transformación digital"

Verificar:
[ ] Todas las slides se generan
[ ] Tiempo de generación < 30 segundos
[ ] Variedad de layouts
[ ] Archivo no excede 10MB
```

##### Caso 4: Edge Cases

```
Verificar:
[ ] Título con caracteres especiales (ñ, á, é, etc.)
[ ] Tema vacío (debe usar auto-generación)
[ ] Bullet points muy largos
[ ] Sin conexión a Unsplash (fallback a sin imágenes)
```

---

## Métricas de Éxito

### Métricas Cuantitativas

| Métrica                | Objetivo                                   | Método de Medición             |
| ---------------------- | ------------------------------------------ | ------------------------------ |
| Tiempo de generación   | < 10s (sin imágenes), < 30s (con imágenes) | Logs del servidor              |
| Tasa de éxito descarga | 100%                                       | Monitoreo de 404s              |
| Tamaño archivo         | < 5MB promedio                             | Análisis de archivos generados |
| Errores en producción  | 0                                          | Railway logs                   |

### Métricas Cualitativas

| Aspecto             | Evaluación               | Responsable       |
| ------------------- | ------------------------ | ----------------- |
| Atractivo visual    | Escala 1-5, objetivo > 4 | Feedback usuarios |
| Relevancia imágenes | Escala 1-5, objetivo > 3 | Feedback usuarios |
| Profesionalismo     | Comparación con Gamma    | Revisión interna  |

---

## Rollback Plan

### Si hay problemas críticos

1. **Revertir cambios en presentations.py**

   ```bash
   git revert HEAD~N  # N = número de commits
   ```

2. **Desactivar imágenes**

   ```bash
   # Railway > Variables
   UNSPLASH_ACCESS_KEY=  # Dejar vacío
   ```

3. **Volver a URLs relativas**
   ```python
   # En presentations.py, cambiar:
   "download_url": f"/api/v1/files/presentations/{filename}"
   ```

---

## Checklist Final de Release

### Pre-Deployment

- [ ] Todos los tests unitarios pasan
- [ ] Tests de integración pasan
- [ ] Code review completado
- [ ] Documentación actualizada

### Deployment

- [ ] Variables de entorno configuradas en Railway
- [ ] Deploy exitoso sin errores
- [ ] Health check pasa

### Post-Deployment

- [ ] Test manual de generación de presentación
- [ ] Test manual de descarga
- [ ] Verificar logs sin errores
- [ ] Confirmar imágenes se cargan (si API key presente)

### Comunicación

- [ ] Actualizar README si hay nuevas features
- [ ] Documentar nuevos parámetros de la tool
- [ ] Notificar a usuarios sobre mejoras

---

## Documentación Relacionada

- [README Principal](./README.md)
- [AS-IS / TO-BE](./0-asis-tobe.md)
- [System Prompt Recomendado](../presentations_system_prompt.md)
- [Archivo Principal](../../backend/open_webui/tools/presentations.py)
