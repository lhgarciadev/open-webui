# Etapa 2: Mejoras de Diseño PPTX

## Objetivo

Implementar mejoras visuales en las presentaciones: gradientes, formas decorativas, mejor tipografía y layouts modernos.

**Documento previo:** [1-unsplash-integration.md](./1-unsplash-integration.md)

---

## Mejoras Planificadas

### 0. Footer de Branding (Premium Touch)

Agregar footer consistente en todas las slides con indicador de progreso y branding.

```python
def _add_branded_footer(slide, slide_num: int, total_slides: int, show_branding: bool = True):
    """
    Agrega footer profesional con:
    - Indicador de progreso (1/10) a la izquierda
    - Branding "Powered by Cognitia" a la derecha
    """
    from pptx.util import Inches, Pt
    from pptx.enum.text import PP_ALIGN

    # Indicador de progreso (izquierda)
    progress_box = slide.shapes.add_textbox(
        Inches(0.3), Inches(6.85), Inches(0.8), Inches(0.25)
    )
    p = progress_box.text_frame.paragraphs[0]
    p.text = f"{slide_num}/{total_slides}"
    p.font.size = Pt(9)
    p.font.color.rgb = RGBColor(156, 163, 175)  # gray-400
    p.alignment = PP_ALIGN.LEFT

    # Branding (derecha) - opcional
    if show_branding:
        brand_box = slide.shapes.add_textbox(
            Inches(7.5), Inches(6.85), Inches(2), Inches(0.25)
        )
        bp = brand_box.text_frame.paragraphs[0]
        bp.text = "Powered by Cognitia"
        bp.font.size = Pt(9)
        bp.font.color.rgb = RGBColor(156, 163, 175)  # gray-400
        bp.alignment = PP_ALIGN.RIGHT
```

### 1. Fondos con Gradiente

#### Implementación

```python
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn
from pptx.oxml import parse_xml
from lxml import etree

def _apply_gradient_background(slide, color1_hex: str, color2_hex: str, angle: int = 90):
    """
    Aplica un gradiente de fondo a un slide.

    Args:
        slide: Slide de python-pptx
        color1_hex: Color inicial (ej: "3b82f6")
        color2_hex: Color final (ej: "1e40af")
        angle: Ángulo del gradiente en grados (0=horizontal, 90=vertical)
    """
    # Acceder al elemento de fondo
    background = slide.background
    fill = background.fill
    fill.gradient()

    # Configurar stops del gradiente
    fill.gradient_stops[0].color.rgb = RGBColor.from_string(color1_hex)
    fill.gradient_stops[1].color.rgb = RGBColor.from_string(color2_hex)

    # Configurar ángulo
    fill.gradient_angle = angle * 60000  # PowerPoint usa EMUs
```

#### Paleta de Gradientes Predefinidos

```python
GRADIENT_PRESETS = {
    "brand_primary": {
        "color1": "60a5fa",  # brand-400
        "color2": "1e40af",  # brand-800
        "angle": 135
    },
    "brand_dark": {
        "color1": "1e40af",  # brand-800
        "color2": "1e3a8a",  # brand-900
        "angle": 180
    },
    "brand_light": {
        "color1": "dbeafe",  # brand-100
        "color2": "bfdbfe",  # brand-200
        "angle": 90
    },
    "sunset": {
        "color1": "f97316",  # orange-500
        "color2": "dc2626",  # red-600
        "angle": 135
    },
    "ocean": {
        "color1": "06b6d4",  # cyan-500
        "color2": "3b82f6",  # blue-500
        "angle": 135
    }
}
```

### 2. Formas Decorativas

#### Círculos Semi-Transparentes

```python
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches

def _add_decorative_circle(slide, left: float, top: float, size: float, color_hex: str, opacity: float = 0.15):
    """
    Agrega un círculo decorativo semi-transparente.

    Args:
        left, top: Posición en pulgadas
        size: Diámetro en pulgadas
        color_hex: Color del círculo
        opacity: Opacidad (0.0 a 1.0)
    """
    circle = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(left), Inches(top),
        Inches(size), Inches(size)
    )

    # Sin borde
    circle.line.fill.background()

    # Relleno con opacidad
    fill = circle.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor.from_string(color_hex)

    # Opacidad via XML (python-pptx no soporta directamente)
    spPr = circle._sp.spPr
    solidFill = spPr.find(qn('a:solidFill'))
    if solidFill is not None:
        srgbClr = solidFill.find(qn('a:srgbClr'))
        if srgbClr is not None:
            alpha = etree.SubElement(srgbClr, qn('a:alpha'))
            alpha.set('val', str(int(opacity * 100000)))
```

#### Líneas Decorativas

```python
from pptx.enum.shapes import MSO_CONNECTOR

def _add_accent_line(slide, x1: float, y1: float, x2: float, y2: float, color_hex: str, width: float = 3):
    """
    Agrega una línea decorativa de acento.
    """
    connector = slide.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT,
        Inches(x1), Inches(y1),
        Inches(x2), Inches(y2)
    )
    connector.line.color.rgb = RGBColor.from_string(color_hex)
    connector.line.width = Pt(width)
```

### 3. Smart Bullets (Iconografía Contextual)

Bullets que cambian según el contenido para mayor impacto visual.

```python
BULLET_ICONS = {
    "default": "•",
    "check": "✓",
    "arrow": "→",
    "star": "★",
    "point": "◆",
    "circle": "○",
    "warning": "⚠",
    "idea": "💡",
    "target": "🎯",
}

KEYWORD_BULLET_MAP = {
    # Completado/Logrado
    ("completado", "listo", "done", "logrado", "terminado", "cumplido"): "check",
    # Siguiente/Próximo paso
    ("siguiente", "próximo", "next", "paso", "entonces", "luego"): "arrow",
    # Importante/Destacado
    ("importante", "clave", "destacado", "crítico", "esencial"): "star",
    # Advertencia
    ("advertencia", "cuidado", "riesgo", "warning", "alerta"): "warning",
    # Ideas
    ("idea", "sugerencia", "propuesta", "recomendación"): "idea",
    # Objetivos
    ("objetivo", "meta", "target", "goal"): "target",
}

def _get_smart_bullet(content: str) -> str:
    """Selecciona bullet basado en keywords del contenido."""
    content_lower = content.lower()
    for keywords, bullet_key in KEYWORD_BULLET_MAP.items():
        if any(kw in content_lower for kw in keywords):
            return BULLET_ICONS[bullet_key]
    return BULLET_ICONS["default"]
```

### 4. Tipografía Mejorada

#### Sistema de Fuentes

```python
FONT_SYSTEM = {
    "title": {
        "name": "Calibri Light",
        "size": 44,
        "bold": False,
        "color": "1e40af"  # brand-800
    },
    "subtitle": {
        "name": "Calibri",
        "size": 24,
        "bold": False,
        "color": "3b82f6"  # brand-500
    },
    "heading": {
        "name": "Calibri",
        "size": 32,
        "bold": True,
        "color": "1e3a8a"  # brand-900
    },
    "body": {
        "name": "Calibri",
        "size": 18,
        "bold": False,
        "color": "1f2937"  # gray-800
    },
    "caption": {
        "name": "Calibri",
        "size": 12,
        "bold": False,
        "color": "6b7280"  # gray-500
    }
}

def _apply_font_style(paragraph, style_name: str):
    """Aplica un estilo de fuente predefinido a un párrafo."""
    style = FONT_SYSTEM.get(style_name, FONT_SYSTEM["body"])

    paragraph.font.name = style["name"]
    paragraph.font.size = Pt(style["size"])
    paragraph.font.bold = style["bold"]
    paragraph.font.color.rgb = RGBColor.from_string(style["color"])
```

### 4. Layouts Modernos

#### Layout: Título con Imagen de Fondo

```python
def _add_title_slide_modern(prs, slide_def: dict, image_bytes: Optional[bytes] = None):
    """
    Slide de título moderno con imagen de fondo difuminada.
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank

    # Agregar imagen de fondo si existe
    if image_bytes:
        image_stream = io.BytesIO(image_bytes)
        pic = slide.shapes.add_picture(
            image_stream,
            Inches(0), Inches(0),
            width=prs.slide_width, height=prs.slide_height
        )
        # Enviar al fondo
        spTree = slide.shapes._spTree
        spTree.insert(2, pic._element)

        # Agregar overlay oscuro para legibilidad
        overlay = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0), Inches(0),
            prs.slide_width, prs.slide_height
        )
        overlay.fill.solid()
        overlay.fill.fore_color.rgb = RGBColor(0, 0, 0)
        _set_shape_opacity(overlay, 0.5)
        overlay.line.fill.background()

    # Texto centrado
    title_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(2.5), Inches(9), Inches(1.5)
    )
    tf = title_box.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = slide_def.get("title", "")
    p.font.size = Pt(48)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255) if image_bytes else RGBColor(30, 64, 175)
    p.alignment = PP_ALIGN.CENTER

    # Subtítulo
    if slide_def.get("subtitle"):
        p2 = tf.add_paragraph()
        p2.text = slide_def["subtitle"]
        p2.font.size = Pt(24)
        p2.font.color.rgb = RGBColor(219, 234, 254) if image_bytes else RGBColor(59, 130, 246)
        p2.alignment = PP_ALIGN.CENTER
```

#### Layout: Estadísticas con Iconos

```python
def _add_stats_slide_modern(prs, slide_def: dict):
    """
    Slide de estadísticas con diseño moderno tipo dashboard.
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank

    # Fondo con gradiente
    _apply_gradient_background(slide, "dbeafe", "ffffff", 90)

    # Título
    title = slide_def.get("title", "Estadísticas")
    _add_centered_title(slide, title)

    # Stats en grid
    stats = slide_def.get("stats", [])
    num_stats = len(stats)

    if num_stats > 0:
        # Calcular posiciones para centrar
        card_width = 2.0
        card_height = 1.8
        spacing = 0.3
        total_width = num_stats * card_width + (num_stats - 1) * spacing
        start_x = (10 - total_width) / 2

        for i, stat in enumerate(stats):
            x = start_x + i * (card_width + spacing)

            # Card de fondo
            card = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(x), Inches(2.5),
                Inches(card_width), Inches(card_height)
            )
            card.fill.solid()
            card.fill.fore_color.rgb = RGBColor(255, 255, 255)
            card.line.color.rgb = RGBColor(219, 234, 254)  # brand-100
            card.line.width = Pt(2)

            # Valor grande
            value_box = slide.shapes.add_textbox(
                Inches(x + 0.1), Inches(2.7),
                Inches(card_width - 0.2), Inches(0.9)
            )
            vp = value_box.text_frame.paragraphs[0]
            vp.text = str(stat.get("value", "N/A"))
            vp.font.size = Pt(36)
            vp.font.bold = True
            vp.font.color.rgb = RGBColor(30, 64, 175)  # brand-800
            vp.alignment = PP_ALIGN.CENTER

            # Label pequeño
            label_box = slide.shapes.add_textbox(
                Inches(x + 0.1), Inches(3.6),
                Inches(card_width - 0.2), Inches(0.5)
            )
            lp = label_box.text_frame.paragraphs[0]
            lp.text = stat.get("label", "")
            lp.font.size = Pt(12)
            lp.font.color.rgb = RGBColor(107, 114, 128)  # gray-500
            lp.alignment = PP_ALIGN.CENTER
```

---

## Antes vs Después - Comparación Visual

### Slide de Título

| Aspecto    | Antes        | Después                         |
| ---------- | ------------ | ------------------------------- |
| Fondo      | Sólido azul  | Gradiente + imagen opcional     |
| Título     | Arial negro  | Calibri Light blanco con sombra |
| Decoración | Ninguna      | Círculos semi-transparentes     |
| Subtítulo  | Pequeño gris | Brand color, mejor contraste    |

### Slide de Contenido

| Aspecto | Antes            | Después                 |
| ------- | ---------------- | ----------------------- |
| Layout  | Full-width texto | 60% texto / 40% imagen  |
| Bullets | Puntos básicos   | Bullets con color brand |
| Imagen  | No hay           | Unsplash relevante      |
| Fondo   | Blanco           | Gradiente sutil         |

### Slide de Stats

| Aspecto | Antes          | Después               |
| ------- | -------------- | --------------------- |
| Números | Texto plano    | Cards con bordes      |
| Layout  | Lista vertical | Grid horizontal       |
| Colores | Monocromático  | Paleta brand completa |

---

## Archivos a Modificar

### `backend/open_webui/tools/presentations.py`

```python
# Estructura propuesta de funciones

# ===== DESIGN SYSTEM =====
GRADIENT_PRESETS = {...}
FONT_SYSTEM = {...}

def _apply_gradient_background(slide, color1, color2, angle): ...
def _add_decorative_circle(slide, left, top, size, color, opacity): ...
def _add_accent_line(slide, x1, y1, x2, y2, color, width): ...
def _apply_font_style(paragraph, style_name): ...
def _set_shape_opacity(shape, opacity): ...

# ===== MODERN LAYOUTS =====
def _add_title_slide_modern(prs, slide_def, image_bytes=None): ...
def _add_content_slide_modern(prs, slide_def, image_bytes=None): ...
def _add_stats_slide_modern(prs, slide_def): ...
def _add_section_slide_modern(prs, slide_def): ...
def _add_quote_slide_modern(prs, slide_def): ...
def _add_closing_slide_modern(prs, slide_def): ...

# ===== MAIN GENERATOR =====
async def _build_presentation_modern(title, slides, theme="brand_primary"): ...
```

---

## Temas Predefinidos

```python
THEMES = {
    "brand_primary": {
        "background_gradient": ("60a5fa", "1e40af"),
        "title_color": "ffffff",
        "text_color": "1f2937",
        "accent_color": "3b82f6",
        "card_bg": "ffffff",
        "card_border": "dbeafe"
    },
    "brand_light": {
        "background_gradient": ("ffffff", "f0f9ff"),
        "title_color": "1e40af",
        "text_color": "1f2937",
        "accent_color": "3b82f6",
        "card_bg": "ffffff",
        "card_border": "bfdbfe"
    },
    "brand_dark": {
        "background_gradient": ("1e3a8a", "0f172a"),
        "title_color": "ffffff",
        "text_color": "e2e8f0",
        "accent_color": "60a5fa",
        "card_bg": "1e40af",
        "card_border": "3b82f6"
    }
}
```

---

## Checklist de Implementación

- [ ] Implementar `_apply_gradient_background()`
- [ ] Implementar `_add_decorative_circle()`
- [ ] Implementar sistema de fuentes `FONT_SYSTEM`
- [ ] Refactorizar `_add_title_slide()` → versión moderna
- [ ] Refactorizar `_add_content_slide()` → versión moderna
- [ ] Refactorizar `_add_stats_slide()` → versión moderna
- [ ] Agregar soporte para temas (`theme` parameter)
- [ ] Testing visual con diferentes tipos de contenido
- [ ] Documentar nuevos parámetros en docstring

---

## Próximo Paso

→ [Etapa 3: Fix de Descarga](./3-download-fix.md)
