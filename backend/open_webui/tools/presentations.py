"""
Cognitia Slides - Presentation generation tool.

Enables AI agents to create professional PowerPoint presentations
with brand-consistent templates and styling.
"""

import json
import logging
import os
import uuid
from datetime import datetime
from typing import Optional, List
from pathlib import Path

from fastapi import Request
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RgbColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

log = logging.getLogger(__name__)

# =============================================================================
# BRAND CONFIGURATION - Cognitia
# =============================================================================

BRAND_COLORS = {
    "primary": RgbColor(59, 130, 246),      # #3b82f6 - Blue 500
    "primary_dark": RgbColor(30, 64, 175),   # #1e40af - Blue 800
    "surface": RgbColor(15, 23, 42),         # #0f172a - Slate 900
    "surface_light": RgbColor(30, 41, 59),   # #1e293b - Slate 800
    "text_primary": RgbColor(248, 250, 252), # #f8fafc - Slate 50
    "text_secondary": RgbColor(148, 163, 184), # #94a3b8 - Slate 400
    "accent_success": RgbColor(34, 197, 94),  # #22c55e - Green 500
    "accent_warning": RgbColor(245, 158, 11), # #f59e0b - Amber 500
    "accent_error": RgbColor(239, 68, 68),    # #ef4444 - Red 500
    "white": RgbColor(255, 255, 255),
    "black": RgbColor(0, 0, 0),
}

AVAILABLE_ICONS = [
    {"name": "chart", "description": "Bar chart icon for data/analytics"},
    {"name": "users", "description": "People icon for team/users"},
    {"name": "rocket", "description": "Rocket icon for launch/growth"},
    {"name": "target", "description": "Target icon for goals/objectives"},
    {"name": "lightbulb", "description": "Lightbulb icon for ideas/innovation"},
    {"name": "shield", "description": "Shield icon for security/protection"},
    {"name": "globe", "description": "Globe icon for global/international"},
    {"name": "clock", "description": "Clock icon for time/schedule"},
    {"name": "check", "description": "Checkmark icon for completion/success"},
    {"name": "star", "description": "Star icon for highlights/favorites"},
    {"name": "heart", "description": "Heart icon for favorites/health"},
    {"name": "gear", "description": "Gear icon for settings/technical"},
    {"name": "database", "description": "Database icon for data/storage"},
    {"name": "cloud", "description": "Cloud icon for cloud services"},
    {"name": "lock", "description": "Lock icon for security/privacy"},
]

SLIDE_TEMPLATES = [
    "title",           # Title slide with subtitle
    "content",         # Title + bullet points
    "two_column",      # Two column layout
    "section",         # Section divider
    "image",           # Title + image placeholder
    "comparison",      # Side by side comparison
    "quote",           # Quote/testimonial
    "stats",           # Statistics/metrics display
    "timeline",        # Timeline/roadmap
    "closing",         # Thank you/closing slide
]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _get_presentations_dir() -> Path:
    """Get the presentations output directory."""
    base_dir = Path(os.environ.get("DATA_DIR", "/app/backend/data"))
    presentations_dir = base_dir / "presentations"
    presentations_dir.mkdir(parents=True, exist_ok=True)
    return presentations_dir


def _apply_brand_background(slide, dark: bool = True):
    """Apply brand background color to slide."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = BRAND_COLORS["surface"] if dark else BRAND_COLORS["white"]


def _add_title_shape(slide, text: str, top: float = 0.5, font_size: int = 44, dark: bool = True):
    """Add a styled title to the slide."""
    left = Inches(0.5)
    top = Inches(top)
    width = Inches(9)
    height = Inches(1)

    shape = slide.shapes.add_textbox(left, top, width, height)
    text_frame = shape.text_frame
    text_frame.word_wrap = True

    p = text_frame.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = True
    p.font.color.rgb = BRAND_COLORS["text_primary"] if dark else BRAND_COLORS["surface"]
    p.alignment = PP_ALIGN.LEFT


def _add_subtitle_shape(slide, text: str, top: float = 1.5, dark: bool = True):
    """Add a styled subtitle to the slide."""
    left = Inches(0.5)
    top = Inches(top)
    width = Inches(9)
    height = Inches(0.75)

    shape = slide.shapes.add_textbox(left, top, width, height)
    text_frame = shape.text_frame
    text_frame.word_wrap = True

    p = text_frame.paragraphs[0]
    p.text = text
    p.font.size = Pt(24)
    p.font.color.rgb = BRAND_COLORS["text_secondary"] if dark else BRAND_COLORS["surface_light"]
    p.alignment = PP_ALIGN.LEFT


def _add_bullets(slide, items: List[str], top: float = 2.5, dark: bool = True):
    """Add bullet points to the slide."""
    left = Inches(0.5)
    top = Inches(top)
    width = Inches(9)
    height = Inches(4)

    shape = slide.shapes.add_textbox(left, top, width, height)
    text_frame = shape.text_frame
    text_frame.word_wrap = True

    for i, item in enumerate(items):
        if i == 0:
            p = text_frame.paragraphs[0]
        else:
            p = text_frame.add_paragraph()
        p.text = f"• {item}"
        p.font.size = Pt(20)
        p.font.color.rgb = BRAND_COLORS["text_primary"] if dark else BRAND_COLORS["surface"]
        p.space_before = Pt(12)
        p.space_after = Pt(6)


def _add_brand_footer(slide, dark: bool = True):
    """Add Cognitia brand footer."""
    left = Inches(0.5)
    top = Inches(7)
    width = Inches(2)
    height = Inches(0.3)

    shape = slide.shapes.add_textbox(left, top, width, height)
    text_frame = shape.text_frame
    p = text_frame.paragraphs[0]
    p.text = "Cognitia"
    p.font.size = Pt(10)
    p.font.color.rgb = BRAND_COLORS["primary"]
    p.font.bold = True


def _add_accent_bar(slide):
    """Add brand accent bar at top of slide."""
    left = Inches(0)
    top = Inches(0)
    width = Inches(10)
    height = Inches(0.1)

    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = BRAND_COLORS["primary"]
    shape.line.fill.background()


# =============================================================================
# SLIDE CREATION FUNCTIONS
# =============================================================================

def _create_title_slide(prs: Presentation, title: str, subtitle: str = ""):
    """Create a title slide."""
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)
    _apply_brand_background(slide, dark=True)

    # Centered title
    left = Inches(0.5)
    top = Inches(2.5)
    width = Inches(9)
    height = Inches(1.5)

    shape = slide.shapes.add_textbox(left, top, width, height)
    text_frame = shape.text_frame
    text_frame.word_wrap = True

    p = text_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(54)
    p.font.bold = True
    p.font.color.rgb = BRAND_COLORS["text_primary"]
    p.alignment = PP_ALIGN.CENTER

    if subtitle:
        # Subtitle
        left = Inches(0.5)
        top = Inches(4.2)
        width = Inches(9)
        height = Inches(1)

        shape = slide.shapes.add_textbox(left, top, width, height)
        text_frame = shape.text_frame
        p = text_frame.paragraphs[0]
        p.text = subtitle
        p.font.size = Pt(28)
        p.font.color.rgb = BRAND_COLORS["text_secondary"]
        p.alignment = PP_ALIGN.CENTER

    _add_accent_bar(slide)
    return slide


def _create_content_slide(prs: Presentation, title: str, bullets: List[str]):
    """Create a content slide with title and bullets."""
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)
    _apply_brand_background(slide, dark=True)
    _add_accent_bar(slide)

    _add_title_shape(slide, title, top=0.5)
    _add_bullets(slide, bullets, top=1.8)
    _add_brand_footer(slide)

    return slide


def _create_two_column_slide(prs: Presentation, title: str, left_items: List[str], right_items: List[str], left_title: str = "", right_title: str = ""):
    """Create a two-column slide."""
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)
    _apply_brand_background(slide, dark=True)
    _add_accent_bar(slide)

    _add_title_shape(slide, title, top=0.5)

    # Left column title
    if left_title:
        left = Inches(0.5)
        top = Inches(1.6)
        width = Inches(4.2)
        height = Inches(0.5)
        shape = slide.shapes.add_textbox(left, top, width, height)
        p = shape.text_frame.paragraphs[0]
        p.text = left_title
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.color.rgb = BRAND_COLORS["primary"]

    # Left column items
    left = Inches(0.5)
    top = Inches(2.2)
    width = Inches(4.2)
    height = Inches(4)
    shape = slide.shapes.add_textbox(left, top, width, height)
    text_frame = shape.text_frame
    for i, item in enumerate(left_items):
        if i == 0:
            p = text_frame.paragraphs[0]
        else:
            p = text_frame.add_paragraph()
        p.text = f"• {item}"
        p.font.size = Pt(18)
        p.font.color.rgb = BRAND_COLORS["text_primary"]
        p.space_before = Pt(8)

    # Right column title
    if right_title:
        left = Inches(5.2)
        top = Inches(1.6)
        width = Inches(4.2)
        height = Inches(0.5)
        shape = slide.shapes.add_textbox(left, top, width, height)
        p = shape.text_frame.paragraphs[0]
        p.text = right_title
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.color.rgb = BRAND_COLORS["primary"]

    # Right column items
    left = Inches(5.2)
    top = Inches(2.2)
    width = Inches(4.2)
    height = Inches(4)
    shape = slide.shapes.add_textbox(left, top, width, height)
    text_frame = shape.text_frame
    for i, item in enumerate(right_items):
        if i == 0:
            p = text_frame.paragraphs[0]
        else:
            p = text_frame.add_paragraph()
        p.text = f"• {item}"
        p.font.size = Pt(18)
        p.font.color.rgb = BRAND_COLORS["text_primary"]
        p.space_before = Pt(8)

    _add_brand_footer(slide)
    return slide


def _create_section_slide(prs: Presentation, title: str, subtitle: str = ""):
    """Create a section divider slide."""
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)

    # Use primary color as background
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = BRAND_COLORS["primary"]

    # Centered title
    left = Inches(0.5)
    top = Inches(3)
    width = Inches(9)
    height = Inches(1.5)

    shape = slide.shapes.add_textbox(left, top, width, height)
    text_frame = shape.text_frame
    p = text_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(48)
    p.font.bold = True
    p.font.color.rgb = BRAND_COLORS["white"]
    p.alignment = PP_ALIGN.CENTER

    if subtitle:
        left = Inches(0.5)
        top = Inches(4.5)
        width = Inches(9)
        height = Inches(0.75)

        shape = slide.shapes.add_textbox(left, top, width, height)
        p = shape.text_frame.paragraphs[0]
        p.text = subtitle
        p.font.size = Pt(24)
        p.font.color.rgb = BRAND_COLORS["white"]
        p.alignment = PP_ALIGN.CENTER

    return slide


def _create_stats_slide(prs: Presentation, title: str, stats: List[dict]):
    """Create a statistics slide. Stats format: [{"value": "50%", "label": "Growth"}]"""
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)
    _apply_brand_background(slide, dark=True)
    _add_accent_bar(slide)

    _add_title_shape(slide, title, top=0.5)

    # Calculate positions for stats (max 4)
    num_stats = min(len(stats), 4)
    total_width = 9
    stat_width = total_width / num_stats

    for i, stat in enumerate(stats[:4]):
        left = Inches(0.5 + i * stat_width)
        top = Inches(2.5)
        width = Inches(stat_width - 0.2)
        height = Inches(3)

        # Value
        shape = slide.shapes.add_textbox(left, top, width, Inches(1.5))
        p = shape.text_frame.paragraphs[0]
        p.text = str(stat.get("value", ""))
        p.font.size = Pt(48)
        p.font.bold = True
        p.font.color.rgb = BRAND_COLORS["primary"]
        p.alignment = PP_ALIGN.CENTER

        # Label
        shape = slide.shapes.add_textbox(left, Inches(4), width, Inches(1))
        p = shape.text_frame.paragraphs[0]
        p.text = str(stat.get("label", ""))
        p.font.size = Pt(18)
        p.font.color.rgb = BRAND_COLORS["text_secondary"]
        p.alignment = PP_ALIGN.CENTER

    _add_brand_footer(slide)
    return slide


def _create_quote_slide(prs: Presentation, quote: str, author: str = "", role: str = ""):
    """Create a quote/testimonial slide."""
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)
    _apply_brand_background(slide, dark=True)

    # Quote
    left = Inches(1)
    top = Inches(2)
    width = Inches(8)
    height = Inches(3)

    shape = slide.shapes.add_textbox(left, top, width, height)
    text_frame = shape.text_frame
    text_frame.word_wrap = True
    p = text_frame.paragraphs[0]
    p.text = f'"{quote}"'
    p.font.size = Pt(32)
    p.font.italic = True
    p.font.color.rgb = BRAND_COLORS["text_primary"]
    p.alignment = PP_ALIGN.CENTER

    # Author
    if author:
        left = Inches(1)
        top = Inches(5.5)
        width = Inches(8)
        height = Inches(0.75)

        shape = slide.shapes.add_textbox(left, top, width, height)
        p = shape.text_frame.paragraphs[0]
        author_text = f"— {author}"
        if role:
            author_text += f", {role}"
        p.text = author_text
        p.font.size = Pt(20)
        p.font.color.rgb = BRAND_COLORS["primary"]
        p.alignment = PP_ALIGN.CENTER

    _add_brand_footer(slide)
    return slide


def _create_closing_slide(prs: Presentation, title: str = "Thank You", subtitle: str = "", contact: str = ""):
    """Create a closing/thank you slide."""
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)
    _apply_brand_background(slide, dark=True)

    # Title
    left = Inches(0.5)
    top = Inches(2.5)
    width = Inches(9)
    height = Inches(1.5)

    shape = slide.shapes.add_textbox(left, top, width, height)
    p = shape.text_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(54)
    p.font.bold = True
    p.font.color.rgb = BRAND_COLORS["text_primary"]
    p.alignment = PP_ALIGN.CENTER

    if subtitle:
        left = Inches(0.5)
        top = Inches(4.2)
        width = Inches(9)
        height = Inches(0.75)

        shape = slide.shapes.add_textbox(left, top, width, height)
        p = shape.text_frame.paragraphs[0]
        p.text = subtitle
        p.font.size = Pt(24)
        p.font.color.rgb = BRAND_COLORS["text_secondary"]
        p.alignment = PP_ALIGN.CENTER

    if contact:
        left = Inches(0.5)
        top = Inches(5.5)
        width = Inches(9)
        height = Inches(0.5)

        shape = slide.shapes.add_textbox(left, top, width, height)
        p = shape.text_frame.paragraphs[0]
        p.text = contact
        p.font.size = Pt(18)
        p.font.color.rgb = BRAND_COLORS["primary"]
        p.alignment = PP_ALIGN.CENTER

    _add_accent_bar(slide)
    return slide


# =============================================================================
# PUBLIC TOOL FUNCTIONS
# =============================================================================

async def get_available_templates(
    __request__: Request = None,
    __user__: dict = None,
) -> str:
    """
    Get a list of available presentation slide templates.

    :return: JSON with available templates and their descriptions
    """
    templates = [
        {"type": "title", "description": "Title slide with main heading and subtitle"},
        {"type": "content", "description": "Content slide with title and bullet points"},
        {"type": "two_column", "description": "Two column layout for comparisons"},
        {"type": "section", "description": "Section divider with accent color background"},
        {"type": "stats", "description": "Statistics display with large numbers"},
        {"type": "quote", "description": "Quote or testimonial slide"},
        {"type": "closing", "description": "Thank you / closing slide"},
    ]

    return json.dumps({
        "templates": templates,
        "brand": "Cognitia",
        "color_scheme": "Blue corporate theme"
    }, ensure_ascii=False)


async def get_available_icons(
    __request__: Request = None,
    __user__: dict = None,
) -> str:
    """
    Get a list of available icons that can be used in presentations.

    :return: JSON with available icon names and descriptions
    """
    return json.dumps({
        "icons": AVAILABLE_ICONS,
        "note": "Icons are represented as styled shapes in presentations"
    }, ensure_ascii=False)


async def generate_presentation(
    title: str,
    slides: List[dict],
    author: str = "Cognitia AI",
    __request__: Request = None,
    __user__: dict = None,
) -> str:
    """
    Generate a professional PowerPoint presentation with Cognitia branding.

    :param title: The presentation title (used for filename and title slide)
    :param slides: List of slide definitions. Each slide is a dict with:
        - type: "title" | "content" | "two_column" | "section" | "stats" | "quote" | "closing"
        - title: Slide title
        - subtitle: (optional) Subtitle text
        - bullets: (for content) List of bullet point strings
        - left_items, right_items: (for two_column) Lists for each column
        - left_title, right_title: (for two_column) Column headers
        - stats: (for stats) List of {"value": "X", "label": "Y"} dicts
        - quote, author, role: (for quote) Quote text and attribution
        - contact: (for closing) Contact information
    :param author: Author name for metadata
    :return: JSON with file path and presentation details

    Example slides parameter:
    [
        {"type": "title", "title": "Quarterly Report", "subtitle": "Q4 2024 Results"},
        {"type": "content", "title": "Key Highlights", "bullets": ["Revenue up 25%", "New markets entered", "Team grew to 50"]},
        {"type": "stats", "title": "By the Numbers", "stats": [{"value": "25%", "label": "Growth"}, {"value": "50", "label": "Team Size"}]},
        {"type": "closing", "title": "Questions?", "contact": "team@cognitia.ai"}
    ]
    """
    try:
        # Create presentation
        prs = Presentation()
        prs.slide_width = Inches(10)
        prs.slide_height = Inches(7.5)

        # Set metadata
        prs.core_properties.title = title
        prs.core_properties.author = author
        prs.core_properties.comments = "Generated by Cognitia AI"

        # Process each slide
        for slide_def in slides:
            slide_type = slide_def.get("type", "content")

            if slide_type == "title":
                _create_title_slide(
                    prs,
                    slide_def.get("title", title),
                    slide_def.get("subtitle", "")
                )

            elif slide_type == "content":
                _create_content_slide(
                    prs,
                    slide_def.get("title", ""),
                    slide_def.get("bullets", [])
                )

            elif slide_type == "two_column":
                _create_two_column_slide(
                    prs,
                    slide_def.get("title", ""),
                    slide_def.get("left_items", []),
                    slide_def.get("right_items", []),
                    slide_def.get("left_title", ""),
                    slide_def.get("right_title", "")
                )

            elif slide_type == "section":
                _create_section_slide(
                    prs,
                    slide_def.get("title", ""),
                    slide_def.get("subtitle", "")
                )

            elif slide_type == "stats":
                _create_stats_slide(
                    prs,
                    slide_def.get("title", ""),
                    slide_def.get("stats", [])
                )

            elif slide_type == "quote":
                _create_quote_slide(
                    prs,
                    slide_def.get("quote", ""),
                    slide_def.get("author", ""),
                    slide_def.get("role", "")
                )

            elif slide_type == "closing":
                _create_closing_slide(
                    prs,
                    slide_def.get("title", "Thank You"),
                    slide_def.get("subtitle", ""),
                    slide_def.get("contact", "")
                )

        # Generate filename and save
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')[:50]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_title}_{timestamp}.pptx"

        output_dir = _get_presentations_dir()
        filepath = output_dir / filename
        prs.save(str(filepath))

        # Return result
        return json.dumps({
            "success": True,
            "file_path": str(filepath),
            "filename": filename,
            "slides_count": len(slides),
            "download_url": f"/api/v1/files/presentations/{filename}",
            "message": f"Presentation '{title}' created successfully with {len(slides)} slides."
        }, ensure_ascii=False)

    except Exception as e:
        log.exception(f"generate_presentation error: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)
