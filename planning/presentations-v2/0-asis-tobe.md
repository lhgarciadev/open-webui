# Etapa 0: Análisis AS-IS / TO-BE

## Objetivo

Documentar el estado actual del generador de presentaciones y definir el estado objetivo con mejoras visuales.

---

## AS-IS (Estado Actual)

### Arquitectura Actual

```
[Usuario] → [Chat LLM] → [Tool: generate_presentation] → [python-pptx] → [.pptx file]
                              ↓
                    [Templates básicos]
                              ↓
                    [Colores sólidos únicamente]
```

### Características Actuales

| Aspecto        | Estado Actual                      | Limitaciones                            |
| -------------- | ---------------------------------- | --------------------------------------- |
| **Contenido**  | Texto plano con bullets            | Sin imágenes, sin gráficos              |
| **Diseño**     | Colores sólidos (#3b82f6, #1e40af) | Sin gradientes, sin formas decorativas  |
| **Tipografía** | Arial básico                       | Sin jerarquía visual clara              |
| **Layouts**    | 7 tipos de slides                  | Estructura rígida                       |
| **Imágenes**   | No soportado                       | No hay integración con APIs de imágenes |
| **Descarga**   | URL relativa → sandbox: prefix     | Bug conocido en producción              |

### Tipos de Slides Disponibles

1. `title` - Slide de título principal
2. `content` - Contenido con bullets
3. `two_column` - Dos columnas
4. `section` - Divisor de sección
5. `stats` - Estadísticas (números grandes)
6. `quote` - Cita destacada
7. `closing` - Slide de cierre

### Código Relevante - Generación de Slide de Contenido

```python
def _add_content_slide(prs, slide_def: dict):
    """Slide con bullets - implementación actual"""
    layout = prs.slide_layouts[1]  # Layout básico
    slide = prs.slides.add_slide(layout)

    # Solo texto, colores sólidos
    title = slide.shapes.title
    title.text = slide_def.get("title", "Contenido")

    # Bullets simples
    body = slide.shapes.placeholders[1]
    tf = body.text_frame
    for bullet in slide_def.get("bullets", []):
        p = tf.add_paragraph()
        p.text = bullet
        p.level = 0
```

### Problemas Identificados

1. **Presentaciones "planas"** - Sin elementos visuales atractivos
2. **Sin imágenes** - Todo es texto
3. **Colores limitados** - Paleta básica sin gradientes
4. **Sin branding dinámico** - Logo y estilos fijos
5. **URL sandbox:** - Bug en enlaces de descarga (fix en progreso)

---

## TO-BE (Estado Objetivo)

### Arquitectura Propuesta

```
[Usuario] → [Chat LLM] → [Tool: generate_presentation]
                              ↓
                    [Generador PPTX Mejorado]
                              ↓
              ┌──────────────────────────────────┐
              │                                  │
        [Unsplash API]              [Templates Avanzados]
              │                                  │
              ↓                                  ↓
        [Imágenes HD]               [Gradientes + Shapes]
              │                                  │
              └──────────────┬───────────────────┘
                             ↓
                    [.pptx file profesional]
```

### Características Objetivo

| Aspecto         | Estado Objetivo                   | Beneficio                     |
| --------------- | --------------------------------- | ----------------------------- |
| **Contenido**   | Texto + imágenes contextuales     | Presentaciones más atractivas |
| **Diseño**      | Gradientes, shapes decorativos    | Look moderno tipo Gamma       |
| **Tipografía**  | Jerarquía clara, fuentes modernas | Mejor legibilidad             |
| **Layouts**     | Layouts con áreas de imagen       | Mayor flexibilidad            |
| **Imágenes**    | Unsplash + Pexels (backup)        | Imágenes HD con fallback      |
| **Descarga**    | URLs absolutas                    | Sin bugs en producción        |
| **Branding**    | Footer "Powered by Cognitia"      | Refuerzo de marca             |
| **Iconografía** | Emojis Unicode + bullets custom   | Visual sin costo adicional    |
| **Navegación**  | Indicador de progreso (1/10)      | Mejor UX en presentación      |
| **Fallbacks**   | Placeholders con gradiente        | Graceful degradation          |

### Nuevas Capacidades

#### 1. Integración de Imágenes Automáticas

```python
# Ejemplo de flujo propuesto
async def _get_relevant_image(topic: str) -> bytes:
    """Busca imagen relevante en Unsplash"""
    query = _extract_keywords(topic)
    response = await unsplash_client.search(query)
    return await download_image(response.urls.regular)
```

#### 2. Gradientes de Fondo

```python
# Ejemplo: Fondo con gradiente
def _apply_gradient_background(slide, color1, color2):
    background = slide.background
    fill = background.fill
    fill.gradient()
    fill.gradient_stops[0].color.rgb = RGBColor.from_string(color1)
    fill.gradient_stops[1].color.rgb = RGBColor.from_string(color2)
```

#### 3. Shapes Decorativos

```python
# Círculos y líneas decorativas
def _add_decorative_elements(slide):
    # Círculo semi-transparente
    circle = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        left=Inches(-1), top=Inches(-1),
        width=Inches(3), height=Inches(3)
    )
    circle.fill.solid()
    circle.fill.fore_color.rgb = RGBColor(59, 130, 246)  # brand-500
    circle.fill.fore_color.brightness = 0.3  # Semi-transparente
```

#### 4. Footer de Branding (Premium Touch)

```python
def _add_branded_footer(slide, slide_num: int, total_slides: int):
    """Agrega footer con branding y número de slide."""
    # Indicador de progreso
    progress_box = slide.shapes.add_textbox(
        Inches(0.3), Inches(6.8), Inches(1), Inches(0.3)
    )
    progress_box.text_frame.paragraphs[0].text = f"{slide_num}/{total_slides}"

    # Branding
    brand_box = slide.shapes.add_textbox(
        Inches(7), Inches(6.8), Inches(2.5), Inches(0.3)
    )
    brand_box.text_frame.paragraphs[0].text = "Powered by Cognitia"
```

#### 5. Bullets Personalizados con Emojis

```python
BULLET_ICONS = {
    "default": "•",
    "check": "✓",
    "arrow": "→",
    "star": "★",
    "point": "◆",
    "circle": "○"
}

def _get_smart_bullet(content: str) -> str:
    """Selecciona bullet basado en contenido."""
    content_lower = content.lower()
    if any(w in content_lower for w in ["completado", "listo", "done", "logrado"]):
        return BULLET_ICONS["check"]
    if any(w in content_lower for w in ["siguiente", "próximo", "next", "paso"]):
        return BULLET_ICONS["arrow"]
    if any(w in content_lower for w in ["importante", "clave", "destacado"]):
        return BULLET_ICONS["star"]
    return BULLET_ICONS["default"]
```

#### 6. Placeholder de Imagen (Fallback Elegante)

```python
def _add_image_placeholder(slide, left, top, width, height, theme_color):
    """Placeholder cuando la imagen no está disponible."""
    # Rectángulo con gradiente
    placeholder = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left), Inches(top),
        Inches(width), Inches(height)
    )
    _apply_gradient_fill(placeholder, theme_color, "lighter")

    # Icono de imagen
    icon_box = slide.shapes.add_textbox(...)
    icon_box.text_frame.paragraphs[0].text = "📷"  # Emoji placeholder
```

### Mockup Visual - Comparación

```
┌────────────────────────────────────────────────────────────────────┐
│                         AS-IS (Actual)                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  ████████████████████████████████████████████████████████    │  │
│  │  █                                                      █    │  │
│  │  █   Título de la Presentación                          █    │  │
│  │  █   ─────────────────────────                          █    │  │
│  │  █   • Bullet 1                                         █    │  │
│  │  █   • Bullet 2                                         █    │  │
│  │  █   • Bullet 3                                         █    │  │
│  │  █                                                      █    │  │
│  │  ████████████████████████████████████████████████████████    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│               [Fondo sólido, solo texto]                            │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                         TO-BE (Objetivo)                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  ░░▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██    │  │
│  │  ░░                    ┌──────────┐                     ██    │  │
│  │  ░░  Título            │  IMAGEN  │                     ██    │  │
│  │  ░░  ───────           │  HD      │                     ██    │  │
│  │  ░░                    │  Unsplash│                     ██    │  │
│  │  ░░  • Bullet 1        └──────────┘                     ██    │  │
│  │  ░░  • Bullet 2             ◯ decorativo                ██    │  │
│  │  ░░  • Bullet 3                                         ██    │  │
│  │  ░░▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│        [Gradiente de fondo, imagen HD, elementos decorativos]      │
└────────────────────────────────────────────────────────────────────┘
```

---

## Métricas de Éxito

| Métrica                   | Actual | Objetivo | Método de Medición |
| ------------------------- | ------ | -------- | ------------------ |
| Tiempo generación         | ~3s    | <10s     | Logs del servidor  |
| Imágenes por presentación | 0      | 2-4      | Conteo en archivo  |
| Costo por presentación    | $0     | $0       | Monitoreo APIs     |
| Satisfacción visual       | Baja   | Alta     | Feedback usuarios  |
| Descargas exitosas        | ~80%   | 100%     | Métricas Railway   |

---

## Dependencias Técnicas

### Nuevas Dependencias

```python
# requirements.txt adicionales
httpx>=0.24.0      # Cliente HTTP async para Unsplash
pillow>=10.0.0     # Procesamiento de imágenes (ya instalado)
```

### APIs Externas

| API      | Costo  | Rate Limit                           | Uso                        |
| -------- | ------ | ------------------------------------ | -------------------------- |
| Unsplash | Gratis | 50 req/hora (demo), 5000/hora (prod) | Imágenes stock (principal) |
| Pexels   | Gratis | 200 req/hora                         | Imágenes stock (backup)    |

> **Nota:** Pexels se usa como fallback cuando Unsplash no retorna resultados o está rate-limited.

### Configuración Requerida

```bash
# Variables de entorno nuevas
UNSPLASH_ACCESS_KEY=your_access_key_here
```

---

## Riesgos y Mitigaciones

| Riesgo                 | Probabilidad | Impacto | Mitigación                         |
| ---------------------- | ------------ | ------- | ---------------------------------- |
| Rate limiting Unsplash | Media        | Alto    | Cache de imágenes por keywords     |
| Imágenes no relevantes | Media        | Medio   | Mejorar extracción de keywords     |
| Tamaño archivo grande  | Baja         | Bajo    | Comprimir imágenes a 800px         |
| API Unsplash caída     | Baja         | Medio   | Fallback a presentación sin imagen |

---

## Próximo Paso

→ [Etapa 1: Integración Unsplash](./1-unsplash-integration.md)
