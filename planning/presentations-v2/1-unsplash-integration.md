# Etapa 1: Integración de Imágenes (Unsplash + Pexels)

## Objetivo

Integrar APIs de imágenes gratuitas (Unsplash principal, Pexels backup) para agregar imágenes relevantes automáticamente a las presentaciones.

**Documento previo:** [0-asis-tobe.md](./0-asis-tobe.md)

---

## Análisis de APIs

### Comparación de APIs de Imágenes Gratuitas

| API          | Rate Limit                   | Ventajas                      | Desventajas                     |
| ------------ | ---------------------------- | ----------------------------- | ------------------------------- |
| **Unsplash** | 50/hr (demo), 5000/hr (prod) | Mejor calidad, más artísticas | Proceso de aprobación para prod |
| **Pexels**   | 200/hr                       | Sin aprobación, fácil setup   | Calidad variable                |
| **Pixabay**  | 100/min                      | Alto rate limit               | Requiere atribución visible     |

**Decisión:** Unsplash como principal (mejor calidad), Pexels como backup.

---

### Unsplash API - Características

| Característica          | Detalle                                               |
| ----------------------- | ----------------------------------------------------- |
| **Costo**               | Gratis (Demo: 50 req/hora, Producción: 5000 req/hora) |
| **Registro**            | https://unsplash.com/developers                       |
| **Endpoint principal**  | `GET /search/photos`                                  |
| **Tamaños disponibles** | raw, full, regular (1080px), small (400px), thumb     |
| **Atribución**          | Requerida (link a foto + fotógrafo)                   |

### Ejemplo de Request

```bash
curl "https://api.unsplash.com/search/photos?query=technology&per_page=1" \
  -H "Authorization: Client-ID YOUR_ACCESS_KEY"
```

### Ejemplo de Response

```json
{
	"results": [
		{
			"id": "abc123",
			"urls": {
				"raw": "https://images.unsplash.com/...",
				"regular": "https://images.unsplash.com/...?w=1080",
				"small": "https://images.unsplash.com/...?w=400"
			},
			"user": {
				"name": "John Doe",
				"links": {
					"html": "https://unsplash.com/@johndoe"
				}
			},
			"links": {
				"html": "https://unsplash.com/photos/abc123"
			}
		}
	]
}
```

### Pexels API - Características

| Característica          | Detalle                                                            |
| ----------------------- | ------------------------------------------------------------------ |
| **Costo**               | Gratis (200 req/hora)                                              |
| **Registro**            | https://www.pexels.com/api/                                        |
| **Endpoint principal**  | `GET /v1/search`                                                   |
| **Tamaños disponibles** | original, large2x, large, medium, small, portrait, landscape, tiny |
| **Atribución**          | Recomendada pero no requerida                                      |

### Ejemplo Pexels Request

```bash
curl "https://api.pexels.com/v1/search?query=technology&per_page=1" \
  -H "Authorization: YOUR_API_KEY"
```

---

## Plan de Implementación

### Paso 1: Configuración

#### 1.1 Variables de Entorno

```python
# backend/open_webui/config.py

# Agregar después de otras configuraciones de APIs
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")  # Backup
```

#### 1.2 Dependencias

```bash
# Ya tenemos httpx instalado, verificar:
pip show httpx
```

### Paso 2: Cliente Unsplash

#### 2.1 Crear módulo de cliente

```python
# backend/open_webui/utils/unsplash.py

import httpx
import logging
from typing import Optional, Dict, Any
from functools import lru_cache
from open_webui.config import UNSPLASH_ACCESS_KEY

log = logging.getLogger(__name__)

UNSPLASH_API_URL = "https://api.unsplash.com"

# Cache simple en memoria
_image_cache: Dict[str, bytes] = {}

async def search_image(query: str, size: str = "regular") -> Optional[Dict[str, Any]]:
    """
    Busca una imagen en Unsplash basada en keywords.

    Args:
        query: Términos de búsqueda
        size: Tamaño deseado (raw, full, regular, small, thumb)

    Returns:
        Dict con url, photographer_name, photographer_url, photo_url
        None si no hay resultados o API key no configurada
    """
    if not UNSPLASH_ACCESS_KEY:
        log.warning("UNSPLASH_ACCESS_KEY not configured, skipping image search")
        return None

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{UNSPLASH_API_URL}/search/photos",
                params={
                    "query": query,
                    "per_page": 1,
                    "orientation": "landscape"  # Mejor para slides
                },
                headers={
                    "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
                }
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("results"):
                return None

            photo = data["results"][0]
            return {
                "url": photo["urls"].get(size, photo["urls"]["regular"]),
                "photographer_name": photo["user"]["name"],
                "photographer_url": photo["user"]["links"]["html"],
                "photo_url": photo["links"]["html"]
            }

    except Exception as e:
        log.error(f"Error searching Unsplash: {e}")
        return None


async def download_image(url: str) -> Optional[bytes]:
    """
    Descarga una imagen desde URL.
    Usa cache en memoria para evitar descargas repetidas.
    """
    # Check cache
    if url in _image_cache:
        return _image_cache[url]

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            image_bytes = response.content

            # Cache (limitar a 50 imágenes)
            if len(_image_cache) > 50:
                # Eliminar la más antigua
                _image_cache.pop(next(iter(_image_cache)))
            _image_cache[url] = image_bytes

            return image_bytes

    except Exception as e:
        log.error(f"Error downloading image: {e}")
        return None


def extract_keywords(text: str, max_words: int = 3) -> str:
    """
    Extrae keywords relevantes de un texto para búsqueda de imágenes.

    Estrategia:
    1. Eliminar stopwords comunes (español e inglés)
    2. Priorizar sustantivos y términos técnicos
    3. Limitar a max_words palabras
    """
    # Stopwords básicos español/inglés
    stopwords = {
        # Español
        'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del',
        'en', 'con', 'por', 'para', 'como', 'que', 'qué', 'es', 'son', 'y',
        'o', 'a', 'al', 'se', 'su', 'sus', 'este', 'esta', 'estos', 'estas',
        'muy', 'más', 'menos', 'sobre', 'entre', 'sin', 'cada', 'todo', 'toda',
        # Inglés
        'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'and',
        'or', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
        'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
        'might', 'can', 'this', 'that', 'these', 'those', 'it', 'its',
        # Presentaciones
        'presentación', 'slide', 'diapositiva', 'contenido', 'introducción',
        'conclusión', 'resumen', 'puntos', 'clave', 'principales'
    }

    # Limpiar y tokenizar
    words = text.lower().split()
    words = [w.strip('.,;:!?()[]{}"\'-') for w in words]
    words = [w for w in words if w and len(w) > 2 and w not in stopwords]

    # Tomar las primeras max_words palabras únicas
    seen = set()
    keywords = []
    for w in words:
        if w not in seen:
            seen.add(w)
            keywords.append(w)
            if len(keywords) >= max_words:
                break

    return ' '.join(keywords)
```

### Paso 3: Integración en presentations.py

#### 3.1 Importar cliente

```python
# Al inicio de presentations.py
from open_webui.utils.unsplash import search_image, download_image, extract_keywords
```

#### 3.2 Modificar generación de slides

```python
async def _add_content_slide_with_image(prs, slide_def: dict):
    """
    Slide de contenido con imagen opcional.
    Layout: Texto a la izquierda (60%), Imagen a la derecha (40%)
    """
    from pptx.util import Inches, Pt
    from pptx.enum.text import PP_ALIGN
    import io

    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout

    title_text = slide_def.get("title", "")
    bullets = slide_def.get("bullets", [])

    # Área de texto (izquierda 60%)
    text_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(1), Inches(5.5), Inches(5)
    )
    tf = text_box.text_frame
    tf.word_wrap = True

    # Título
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = RGBColor(30, 64, 175)  # brand-800

    # Bullets
    for bullet in bullets:
        p = tf.add_paragraph()
        p.text = f"• {bullet}"
        p.font.size = Pt(16)
        p.level = 0

    # Buscar e insertar imagen (derecha 40%)
    keywords = extract_keywords(title_text + ' ' + ' '.join(bullets))
    if keywords:
        image_data = await search_image(keywords, size="small")
        if image_data:
            image_bytes = await download_image(image_data["url"])
            if image_bytes:
                # Insertar imagen
                image_stream = io.BytesIO(image_bytes)
                slide.shapes.add_picture(
                    image_stream,
                    Inches(6.2), Inches(1.5),
                    width=Inches(3.3), height=Inches(2.5)
                )

                # Agregar atribución pequeña
                attr_box = slide.shapes.add_textbox(
                    Inches(6.2), Inches(4.1), Inches(3.3), Inches(0.3)
                )
                attr_tf = attr_box.text_frame
                attr_p = attr_tf.paragraphs[0]
                attr_p.text = f"Photo: {image_data['photographer_name']}"
                attr_p.font.size = Pt(8)
                attr_p.font.color.rgb = RGBColor(156, 163, 175)  # gray-400
```

---

## Configuración Railway

### Variables de Entorno

```bash
# En Railway Dashboard > Variables
UNSPLASH_ACCESS_KEY=your_access_key_here
```

### Obtener API Key

1. Ir a https://unsplash.com/developers
2. Crear aplicación nueva
3. Copiar "Access Key"
4. Configurar en Railway

---

## Testing

### Test Local

```python
# tests/test_unsplash.py
import pytest
import asyncio
from open_webui.utils.unsplash import search_image, extract_keywords

def test_extract_keywords():
    text = "Introducción a la Inteligencia Artificial en Colombia"
    keywords = extract_keywords(text)
    assert "inteligencia" in keywords or "artificial" in keywords
    assert "introducción" not in keywords  # stopword

@pytest.mark.asyncio
async def test_search_image():
    # Solo si hay API key configurada
    import os
    if not os.environ.get("UNSPLASH_ACCESS_KEY"):
        pytest.skip("UNSPLASH_ACCESS_KEY not configured")

    result = await search_image("technology")
    assert result is not None
    assert "url" in result
    assert "photographer_name" in result
```

### Test Manual

```bash
# Con API key configurada
curl "https://api.unsplash.com/search/photos?query=business&per_page=1" \
  -H "Authorization: Client-ID YOUR_KEY"
```

---

## Checklist de Implementación

- [ ] Crear `backend/open_webui/utils/image_service.py` (cliente unificado)
- [ ] Agregar `UNSPLASH_ACCESS_KEY` y `PEXELS_API_KEY` a `config.py`
- [ ] Implementar búsqueda con fallback Unsplash → Pexels
- [ ] Implementar cache en memoria (LRU, 50 imágenes)
- [ ] Implementar placeholder para cuando no hay imagen
- [ ] Modificar `presentations.py` para usar image_service
- [ ] Agregar tests unitarios para ambas APIs
- [ ] Configurar API keys en Railway
- [ ] Probar generación con imágenes
- [ ] Probar fallback cuando Unsplash falla
- [ ] Verificar atribución cumple ToS

---

## Próximo Paso

→ [Etapa 2: Mejoras de Diseño](./2-design-improvements.md)
