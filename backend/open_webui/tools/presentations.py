"""
Cognitia Slides - Reveal.js Presentation Generator

Generates professional HTML presentations using Reveal.js framework.
Clean, modern design with smooth animations and full browser compatibility.
"""

import json
import logging
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import Request

log = logging.getLogger(__name__)

# =============================================================================
# BRAND CONFIGURATION - Cognitia
# =============================================================================

BRAND_COLORS = {
    "primary": "#3b82f6",      # Blue 500
    "primary_dark": "#1e40af", # Blue 800
    "primary_light": "#60a5fa", # Blue 400
    "surface": "#0f172a",      # Slate 900
    "surface_light": "#1e293b", # Slate 800
    "text_primary": "#f8fafc", # Slate 50
    "text_secondary": "#94a3b8", # Slate 400
    "accent": "#22c55e",       # Green 500
    "white": "#ffffff",
}

# =============================================================================
# REVEAL.JS HTML TEMPLATE
# =============================================================================

REVEALJS_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>

    <!-- Reveal.js CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/theme/black.css">

    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

    <style>
        :root {{
            --r-background-color: {surface};
            --r-main-font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --r-heading-font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --r-main-color: {text_primary};
            --r-heading-color: {white};
            --r-link-color: {primary};
            --r-link-color-hover: {primary_light};
            --r-selection-background-color: {primary};
        }}

        .reveal {{
            font-family: var(--r-main-font);
        }}

        .reveal h1, .reveal h2, .reveal h3 {{
            font-weight: 600;
            text-transform: none;
            letter-spacing: -0.02em;
        }}

        .reveal h1 {{
            font-size: 2.8em;
            background: linear-gradient(135deg, {primary_light}, {primary});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .reveal h2 {{
            font-size: 1.8em;
            color: {white};
            margin-bottom: 0.8em;
        }}

        .reveal h3 {{
            font-size: 1.3em;
            color: {primary_light};
        }}

        .reveal p, .reveal li {{
            font-size: 1.1em;
            line-height: 1.6;
            color: {text_secondary};
        }}

        .reveal ul {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .reveal li {{
            position: relative;
            padding-left: 1.5em;
            margin-bottom: 0.6em;
        }}

        .reveal li::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0.5em;
            width: 8px;
            height: 8px;
            background: {primary};
            border-radius: 50%;
        }}

        /* Title Slide */
        .slide-title {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100%;
            text-align: center;
        }}

        .slide-title h1 {{
            font-size: 3.2em;
            margin-bottom: 0.3em;
        }}

        .slide-title .subtitle {{
            font-size: 1.4em;
            color: {text_secondary};
            font-weight: 300;
        }}

        .slide-title .brand {{
            position: absolute;
            bottom: 40px;
            font-size: 0.9em;
            color: {text_secondary};
            opacity: 0.7;
        }}

        /* Content Slide */
        .slide-content {{
            text-align: left;
            padding: 0 2em;
        }}

        .slide-content h2 {{
            border-bottom: 3px solid {primary};
            padding-bottom: 0.3em;
            display: inline-block;
        }}

        /* Stats Slide */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2em;
            margin-top: 1.5em;
        }}

        .stat-card {{
            background: linear-gradient(135deg, {surface_light}, {surface});
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 16px;
            padding: 2em;
            text-align: center;
        }}

        .stat-value {{
            font-size: 3em;
            font-weight: 700;
            background: linear-gradient(135deg, {primary_light}, {accent});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .stat-label {{
            font-size: 1em;
            color: {text_secondary};
            margin-top: 0.5em;
        }}

        /* Quote Slide */
        .slide-quote {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 0 3em;
        }}

        .slide-quote blockquote {{
            font-size: 1.6em;
            font-style: italic;
            color: {text_primary};
            border-left: 4px solid {primary};
            padding-left: 1em;
            margin: 0;
        }}

        .slide-quote .author {{
            margin-top: 1.5em;
            font-size: 1.1em;
            color: {primary_light};
        }}

        /* Section Slide */
        .slide-section {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100%;
            background: linear-gradient(135deg, {primary_dark}, {surface});
        }}

        .slide-section h2 {{
            font-size: 2.5em;
            margin-bottom: 0.3em;
        }}

        /* Closing Slide */
        .slide-closing {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }}

        .slide-closing h2 {{
            font-size: 2.8em;
            background: linear-gradient(135deg, {primary_light}, {accent});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        /* Two Column Layout */
        .two-columns {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3em;
            text-align: left;
        }}

        .column h3 {{
            margin-bottom: 0.8em;
        }}

        /* Footer */
        .slide-footer {{
            position: absolute;
            bottom: 20px;
            left: 0;
            right: 0;
            display: flex;
            justify-content: space-between;
            padding: 0 40px;
            font-size: 0.7em;
            color: {text_secondary};
            opacity: 0.6;
        }}

        /* Progress bar */
        .reveal .progress {{
            background: rgba(255,255,255,0.1);
            height: 4px;
        }}

        .reveal .progress span {{
            background: linear-gradient(90deg, {primary}, {accent});
        }}

        /* Controls */
        .reveal .controls {{
            color: {primary};
        }}

        /* Animations */
        .reveal .slides section .fragment {{
            transition: all 0.3s ease;
        }}

        .reveal .slides section .fragment.visible {{
            opacity: 1;
            transform: none;
        }}

        .reveal .slides section .fragment.fade-up {{
            transform: translateY(20px);
        }}
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">
{slides_html}
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.js"></script>
    <script>
        Reveal.initialize({{
            hash: true,
            controls: true,
            progress: true,
            center: true,
            transition: 'slide',
            transitionSpeed: 'default',
            backgroundTransition: 'fade',
            viewDistance: 3,
            width: 1280,
            height: 720,
            margin: 0.1,
        }});
    </script>
</body>
</html>
"""

# =============================================================================
# SLIDE GENERATORS
# =============================================================================

def _generate_title_slide(title: str, subtitle: str = "") -> str:
    """Generate title slide HTML."""
    subtitle_html = f'<p class="subtitle">{_escape_html(subtitle)}</p>' if subtitle else ''
    return f"""
            <section>
                <div class="slide-title">
                    <h1>{_escape_html(title)}</h1>
                    {subtitle_html}
                    <p class="brand">Generado con Cognitia AI</p>
                </div>
            </section>"""


def _generate_content_slide(title: str, bullets: List[str], slide_num: int, total: int) -> str:
    """Generate content slide with bullet points."""
    bullets_html = "\n".join([
        f'                        <li class="fragment fade-up">{_escape_html(b)}</li>'
        for b in bullets
    ])

    return f"""
            <section>
                <div class="slide-content">
                    <h2>{_escape_html(title)}</h2>
                    <ul>
{bullets_html}
                    </ul>
                </div>
                <div class="slide-footer">
                    <span>Cognitia</span>
                    <span>{slide_num}/{total}</span>
                </div>
            </section>"""


def _generate_stats_slide(title: str, stats: List[Dict], slide_num: int, total: int) -> str:
    """Generate statistics slide with cards."""
    stats_html = "\n".join([
        f'''                        <div class="stat-card fragment fade-up">
                            <div class="stat-value">{_escape_html(str(s.get("value", "")))}</div>
                            <div class="stat-label">{_escape_html(s.get("label", ""))}</div>
                        </div>'''
        for s in stats[:4]  # Max 4 stats
    ])

    return f"""
            <section>
                <div class="slide-content">
                    <h2>{_escape_html(title)}</h2>
                    <div class="stats-grid">
{stats_html}
                    </div>
                </div>
                <div class="slide-footer">
                    <span>Cognitia</span>
                    <span>{slide_num}/{total}</span>
                </div>
            </section>"""


def _generate_quote_slide(quote: str, author: str = "", role: str = "") -> str:
    """Generate quote slide."""
    author_html = ""
    if author:
        author_html = f'<p class="author">— {_escape_html(author)}'
        if role:
            author_html += f', {_escape_html(role)}'
        author_html += '</p>'

    return f"""
            <section>
                <div class="slide-quote">
                    <blockquote>"{_escape_html(quote)}"</blockquote>
                    {author_html}
                </div>
            </section>"""


def _generate_section_slide(title: str, subtitle: str = "") -> str:
    """Generate section divider slide."""
    subtitle_html = f'<p class="subtitle">{_escape_html(subtitle)}</p>' if subtitle else ''
    return f"""
            <section data-background="linear-gradient(135deg, {BRAND_COLORS['primary_dark']}, {BRAND_COLORS['surface']})">
                <div class="slide-section">
                    <h2>{_escape_html(title)}</h2>
                    {subtitle_html}
                </div>
            </section>"""


def _generate_two_column_slide(title: str, left_items: List[str], right_items: List[str],
                                left_title: str = "", right_title: str = "",
                                slide_num: int = 0, total: int = 0) -> str:
    """Generate two-column layout slide."""
    left_bullets = "\n".join([f'<li class="fragment">{_escape_html(item)}</li>' for item in left_items])
    right_bullets = "\n".join([f'<li class="fragment">{_escape_html(item)}</li>' for item in right_items])

    left_header = f'<h3>{_escape_html(left_title)}</h3>' if left_title else ''
    right_header = f'<h3>{_escape_html(right_title)}</h3>' if right_title else ''

    return f"""
            <section>
                <div class="slide-content">
                    <h2>{_escape_html(title)}</h2>
                    <div class="two-columns">
                        <div class="column">
                            {left_header}
                            <ul>{left_bullets}</ul>
                        </div>
                        <div class="column">
                            {right_header}
                            <ul>{right_bullets}</ul>
                        </div>
                    </div>
                </div>
                <div class="slide-footer">
                    <span>Cognitia</span>
                    <span>{slide_num}/{total}</span>
                </div>
            </section>"""


def _generate_closing_slide(title: str, subtitle: str = "", contact: str = "") -> str:
    """Generate closing/thank you slide."""
    subtitle_html = f'<p class="subtitle">{_escape_html(subtitle)}</p>' if subtitle else ''
    contact_html = f'<p style="margin-top: 2em; color: {BRAND_COLORS["text_secondary"]};">{_escape_html(contact)}</p>' if contact else ''

    return f"""
            <section>
                <div class="slide-closing">
                    <h2>{_escape_html(title)}</h2>
                    {subtitle_html}
                    {contact_html}
                    <p class="brand" style="margin-top: 3em; opacity: 0.6;">Powered by Cognitia AI</p>
                </div>
            </section>"""


# =============================================================================
# UTILITIES
# =============================================================================

def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    if not text:
        return ""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))


def _get_presentations_dir() -> Path:
    """Get the presentations output directory."""
    base_dir = Path(os.environ.get("DATA_DIR", "/app/backend/data"))
    presentations_dir = base_dir / "presentations"
    presentations_dir.mkdir(parents=True, exist_ok=True)
    return presentations_dir


def _auto_generate_slides(title: str) -> List[Dict]:
    """Auto-generate template slides when only title is provided."""
    return [
        {"type": "title", "title": title, "subtitle": "Presentacion generada automaticamente"},
        {"type": "content", "title": "Introduccion", "bullets": [
            f"Contexto y relevancia de: {title}",
            "Objetivos principales",
            "Estructura del contenido"
        ]},
        {"type": "content", "title": "Puntos Clave", "bullets": [
            "Punto principal 1",
            "Punto principal 2",
            "Punto principal 3",
            "Punto principal 4"
        ]},
        {"type": "stats", "title": "Datos Relevantes", "stats": [
            {"value": "---", "label": "Metrica 1"},
            {"value": "---", "label": "Metrica 2"},
            {"value": "---", "label": "Metrica 3"}
        ]},
        {"type": "content", "title": "Recomendaciones", "bullets": [
            "Accion recomendada 1",
            "Accion recomendada 2",
            "Proximos pasos"
        ]},
        {"type": "closing", "title": "Gracias", "subtitle": title}
    ]


def _parse_slides_input(slides) -> List[Dict]:
    """Parse slides input - handles string, list, or dict."""
    if not slides:
        return []

    if isinstance(slides, str):
        try:
            parsed = json.loads(slides)
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict):
                return [parsed]
        except json.JSONDecodeError:
            return []

    if isinstance(slides, list):
        return slides

    if isinstance(slides, dict):
        return [slides]

    return []


# =============================================================================
# MAIN GENERATOR FUNCTION
# =============================================================================

async def generate_presentation(
    title: str,
    slides: Optional[List[Dict]] = None,
    author: str = "Cognitia AI",
    __request__: Optional[Request] = None
) -> str:
    """
    Generate an HTML presentation using Reveal.js.

    Args:
        title: Presentation title (required)
        slides: List of slide definitions with type and content
        author: Author name for metadata
        __request__: FastAPI request for URL building

    Returns:
        JSON with view_url for the presentation

    Slide types:
        - title: {"type": "title", "title": "...", "subtitle": "..."}
        - content: {"type": "content", "title": "...", "bullets": ["...", "..."]}
        - stats: {"type": "stats", "title": "...", "stats": [{"value": "X", "label": "Y"}]}
        - quote: {"type": "quote", "quote": "...", "author": "...", "role": "..."}
        - section: {"type": "section", "title": "...", "subtitle": "..."}
        - two_column: {"type": "two_column", "title": "...", "left_items": [...], "right_items": [...]}
        - closing: {"type": "closing", "title": "...", "subtitle": "..."}

    Example:
        generate_presentation(
            title="AI en Colombia",
            slides=[
                {"type": "title", "title": "AI en Colombia", "subtitle": "Estado 2024"},
                {"type": "content", "title": "Adopcion", "bullets": ["45% empresas", "Sector financiero lidera"]},
                {"type": "stats", "title": "Metricas", "stats": [{"value": "45%", "label": "Adopcion"}]},
                {"type": "closing", "title": "Gracias"}
            ]
        )
    """
    try:
        # Parse slides input
        parsed_slides = _parse_slides_input(slides)

        # Auto-generate if no slides provided
        if not parsed_slides and title.strip():
            log.info(f"Auto-generating slides for: {title}")
            parsed_slides = _auto_generate_slides(title)

        if not parsed_slides:
            return json.dumps({
                "success": False,
                "error": "No slides provided and title is empty"
            }, ensure_ascii=False)

        # Generate HTML for each slide
        slides_html_parts = []
        total_slides = len(parsed_slides)

        for idx, slide_def in enumerate(parsed_slides, 1):
            slide_type = slide_def.get("type", "content")

            if slide_type == "title":
                slides_html_parts.append(_generate_title_slide(
                    slide_def.get("title", title),
                    slide_def.get("subtitle", "")
                ))

            elif slide_type == "content":
                slides_html_parts.append(_generate_content_slide(
                    slide_def.get("title", ""),
                    slide_def.get("bullets", []),
                    idx, total_slides
                ))

            elif slide_type == "stats":
                slides_html_parts.append(_generate_stats_slide(
                    slide_def.get("title", ""),
                    slide_def.get("stats", []),
                    idx, total_slides
                ))

            elif slide_type == "quote":
                slides_html_parts.append(_generate_quote_slide(
                    slide_def.get("quote", ""),
                    slide_def.get("author", ""),
                    slide_def.get("role", "")
                ))

            elif slide_type == "section":
                slides_html_parts.append(_generate_section_slide(
                    slide_def.get("title", ""),
                    slide_def.get("subtitle", "")
                ))

            elif slide_type == "two_column":
                slides_html_parts.append(_generate_two_column_slide(
                    slide_def.get("title", ""),
                    slide_def.get("left_items", []),
                    slide_def.get("right_items", []),
                    slide_def.get("left_title", ""),
                    slide_def.get("right_title", ""),
                    idx, total_slides
                ))

            elif slide_type == "closing":
                slides_html_parts.append(_generate_closing_slide(
                    slide_def.get("title", "Gracias"),
                    slide_def.get("subtitle", ""),
                    slide_def.get("contact", "")
                ))

        # Combine all slides
        slides_html = "\n".join(slides_html_parts)

        # Generate complete HTML
        html_content = REVEALJS_TEMPLATE.format(
            title=_escape_html(title),
            slides_html=slides_html,
            primary=BRAND_COLORS["primary"],
            primary_dark=BRAND_COLORS["primary_dark"],
            primary_light=BRAND_COLORS["primary_light"],
            surface=BRAND_COLORS["surface"],
            surface_light=BRAND_COLORS["surface_light"],
            text_primary=BRAND_COLORS["text_primary"],
            text_secondary=BRAND_COLORS["text_secondary"],
            accent=BRAND_COLORS["accent"],
            white=BRAND_COLORS["white"]
        )

        # Save file
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()
        safe_title = re.sub(r'\s+', '_', safe_title)[:50]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_title}_{timestamp}.html"

        output_dir = _get_presentations_dir()
        filepath = output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Build URL
        view_path = f"/api/v1/files/presentations/{filename}"
        base_url = ""

        if __request__:
            try:
                base_url = str(__request__.base_url).rstrip('/')
            except Exception:
                pass

            if not base_url or base_url == "http://testserver":
                try:
                    webui_url = __request__.app.state.config.WEBUI_URL
                    if webui_url:
                        base_url = webui_url.rstrip('/')
                except Exception:
                    pass

        full_url = f"{base_url}{view_path}" if base_url else view_path

        return json.dumps({
            "success": True,
            "view_url": full_url,
            "filename": filename,
            "slides_count": total_slides,
            "format": "html",
            "message": f"Presentacion '{title}' creada con {total_slides} slides. Ver en: {full_url}"
        }, ensure_ascii=False)

    except Exception as e:
        log.exception(f"generate_presentation error: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)


# =============================================================================
# ADDITIONAL TOOL FUNCTIONS (required by Open WebUI)
# =============================================================================

def get_available_templates() -> str:
    """
    Get available slide templates/types for presentations.

    Returns:
        JSON string with available templates and their descriptions.
    """
    templates = {
        "title": {
            "name": "Title Slide",
            "description": "Opening slide with title and subtitle",
            "fields": ["title", "subtitle"]
        },
        "content": {
            "name": "Content Slide",
            "description": "Standard slide with title and bullet points",
            "fields": ["title", "bullets"]
        },
        "stats": {
            "name": "Statistics Slide",
            "description": "Display key metrics with visual cards",
            "fields": ["title", "stats"]
        },
        "quote": {
            "name": "Quote Slide",
            "description": "Feature a quote with attribution",
            "fields": ["quote", "author", "role"]
        },
        "section": {
            "name": "Section Divider",
            "description": "Visual break between sections",
            "fields": ["title", "subtitle"]
        },
        "two_column": {
            "name": "Two Column Layout",
            "description": "Side-by-side comparison or content",
            "fields": ["title", "left_items", "right_items", "left_title", "right_title"]
        },
        "closing": {
            "name": "Closing Slide",
            "description": "Thank you or conclusion slide",
            "fields": ["title", "subtitle", "contact"]
        }
    }
    return json.dumps(templates, ensure_ascii=False)


def get_available_icons() -> str:
    """
    Get available icons for presentations.

    Note: Reveal.js uses CSS for styling rather than PowerPoint icons.
    This returns semantic icon categories that can be used for theming.

    Returns:
        JSON string with available icon/style options.
    """
    icons = {
        "bullet_styles": [
            {"id": "circle", "name": "Circle", "description": "Standard circular bullet"},
            {"id": "square", "name": "Square", "description": "Square bullet marker"},
            {"id": "dash", "name": "Dash", "description": "Horizontal line marker"}
        ],
        "themes": [
            {"id": "dark", "name": "Dark Mode", "description": "Dark background with light text (default)"},
            {"id": "light", "name": "Light Mode", "description": "Light background with dark text"}
        ],
        "animations": [
            {"id": "fade-up", "name": "Fade Up", "description": "Content fades in from below (default)"},
            {"id": "fade-in", "name": "Fade In", "description": "Simple fade animation"},
            {"id": "slide-in", "name": "Slide In", "description": "Content slides from side"}
        ]
    }
    return json.dumps(icons, ensure_ascii=False)


def get_story_spec_template() -> str:
    """
    Get a template for creating a complete presentation story specification.

    Returns:
        JSON string with a template structure for planning presentations.
    """
    template = {
        "description": "Template for planning a complete presentation",
        "example": {
            "title": "Your Presentation Title",
            "author": "Presenter Name",
            "slides": [
                {
                    "type": "title",
                    "title": "Main Title",
                    "subtitle": "Supporting tagline or date"
                },
                {
                    "type": "content",
                    "title": "Introduction",
                    "bullets": [
                        "Key point one",
                        "Key point two",
                        "Key point three"
                    ]
                },
                {
                    "type": "stats",
                    "title": "Key Metrics",
                    "stats": [
                        {"value": "85%", "label": "Success Rate"},
                        {"value": "2.5x", "label": "Growth"},
                        {"value": "$1.2M", "label": "Revenue"}
                    ]
                },
                {
                    "type": "two_column",
                    "title": "Comparison",
                    "left_title": "Before",
                    "left_items": ["Old approach", "Manual process"],
                    "right_title": "After",
                    "right_items": ["New solution", "Automated workflow"]
                },
                {
                    "type": "quote",
                    "quote": "A memorable quote that supports your message",
                    "author": "Quote Author",
                    "role": "Position or Company"
                },
                {
                    "type": "closing",
                    "title": "Thank You",
                    "subtitle": "Questions?",
                    "contact": "email@example.com"
                }
            ]
        },
        "tips": [
            "Start with a compelling title slide",
            "Limit bullet points to 4-5 per slide",
            "Use stats slides to highlight key numbers",
            "Include a clear call to action in closing"
        ]
    }
    return json.dumps(template, ensure_ascii=False)


# =============================================================================
# TOOL METADATA (for Open WebUI)
# =============================================================================

class Tools:
    """Cognitia Slides - Professional HTML Presentations"""

    def __init__(self):
        self.valves = None

    async def generate_presentation(
        self,
        title: str,
        slides: Optional[List[Dict]] = None,
        author: str = "Cognitia AI",
        __request__: Optional[Request] = None
    ) -> str:
        """Generate a professional HTML presentation using Reveal.js."""
        return await generate_presentation(title, slides, author, __request__)
