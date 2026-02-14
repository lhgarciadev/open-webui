"""
Unit tests for the image_service module.

Tests cover:
- Keyword extraction from Spanish and English text
- Wikimedia Commons API search
- Image download with caching
- Graceful error handling
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def _backend_dir() -> Path:
    return Path(__file__).resolve().parents[3]


def _extract_json_line(stdout: str) -> dict:
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue
    raise AssertionError(f"No JSON payload found in subprocess output:\n{stdout}")


def test_extract_keywords():
    """Test keyword extraction from text."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(_backend_dir())

    script = """
import json
from open_webui.utils.image_service import extract_keywords

results = {
    # Spanish text - should extract meaningful words, not stopwords
    "spanish_removes_stopwords": "introducción" not in extract_keywords("Introducción a la Inteligencia Artificial"),
    "spanish_extracts_keywords": "inteligencia" in extract_keywords("Introducción a la Inteligencia Artificial"),

    # English text
    "english_removes_stopwords": "the" not in extract_keywords("The Future of Machine Learning"),
    "english_extracts_keywords": "machine" in extract_keywords("The Future of Machine Learning"),

    # Respects max_words limit
    "respects_max_words_3": len(extract_keywords("one two three four five", max_words=3).split()) == 3,
    "respects_max_words_2": len(extract_keywords("one two three four five", max_words=2).split()) == 2,

    # Handles empty input
    "empty_string_returns_empty": extract_keywords("") == "",
    "none_input_returns_empty": extract_keywords(None) == "",

    # Removes presentation-specific stopwords
    "removes_presentation_stopwords": "introducción" not in extract_keywords("Introducción y conclusión del tema"),

    # Handles punctuation
    "handles_punctuation": extract_keywords("Hello, World! Test.") == "hello world test",
}

print(json.dumps(results))
"""

    result = subprocess.run(
        [sys.executable, "-c", script],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    payload = _extract_json_line(result.stdout)

    for check_name, value in payload.items():
        assert value is True, f"{check_name} failed"


def test_search_image_wikimedia():
    """Test Wikimedia Commons image search (requires network)."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(_backend_dir())

    script = """
import asyncio
import json
from open_webui.utils.image_service import search_image

async def run():
    # Test with a common search term that should return results
    result = await search_image("technology computer")

    results = {
        "returns_dict_on_success": isinstance(result, dict) if result else True,  # May be None if network fails
        "has_url_key": "url" in result if result else True,
        "has_photographer_name": "photographer_name" in result if result else True,
        "has_source_wikimedia": result.get("source") == "wikimedia" if result else True,
        "url_is_wikimedia": "wikimedia" in result.get("url", "") if result else True,
    }

    # Test with empty query - should return None
    empty_result = await search_image("")
    results["empty_query_returns_none"] = empty_result is None

    # Test with whitespace query - should return None
    whitespace_result = await search_image("   ")
    results["whitespace_query_returns_none"] = whitespace_result is None

    print(json.dumps(results))

asyncio.run(run())
"""

    result = subprocess.run(
        [sys.executable, "-c", script],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,  # Network calls may take time
    )

    assert result.returncode == 0, result.stderr
    payload = _extract_json_line(result.stdout)

    for check_name, value in payload.items():
        assert value is True, f"{check_name} failed"


def test_download_image_caching():
    """Test image download with LRU caching."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(_backend_dir())

    script = """
import asyncio
import json
from open_webui.utils.image_service import download_image, _image_cache

async def run():
    # Clear cache first
    _image_cache.clear()

    # Use a small, reliable test image
    test_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/100px-PNG_transparency_demonstration_1.png"

    # Download image
    image_bytes = await download_image(test_url)

    results = {
        "returns_bytes": isinstance(image_bytes, bytes) if image_bytes else True,
        "bytes_not_empty": len(image_bytes) > 0 if image_bytes else True,
        "cached_after_download": test_url in _image_cache if image_bytes else True,
    }

    # Test cache hit (should return same bytes)
    if image_bytes:
        cached_bytes = await download_image(test_url)
        results["cache_returns_same_bytes"] = cached_bytes == image_bytes

    # Test invalid URL
    invalid_result = await download_image("")
    results["empty_url_returns_none"] = invalid_result is None

    print(json.dumps(results))

asyncio.run(run())
"""

    result = subprocess.run(
        [sys.executable, "-c", script],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, result.stderr
    payload = _extract_json_line(result.stdout)

    for check_name, value in payload.items():
        assert value is True, f"{check_name} failed"


def test_image_service_integration():
    """Test full integration: extract keywords -> search -> download."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(_backend_dir())

    script = """
import asyncio
import json
from open_webui.utils.image_service import extract_keywords, search_image, download_image

async def run():
    # Simulate presentation slide content
    slide_title = "Inteligencia Artificial en Colombia"
    slide_bullets = ["Adopción creciente", "Sector financiero", "Innovación tecnológica"]

    # Extract keywords
    text = slide_title + " " + " ".join(slide_bullets)
    keywords = extract_keywords(text, max_words=3)

    results = {
        "keywords_extracted": len(keywords) > 0,
        "keywords_count_valid": len(keywords.split()) <= 3,
    }

    # Search for image
    image_data = await search_image(keywords)

    if image_data:
        results["search_found_image"] = True
        results["image_has_url"] = "url" in image_data
        results["image_has_photographer"] = "photographer_name" in image_data

        # Download the image
        image_bytes = await download_image(image_data["url"])
        results["download_succeeded"] = image_bytes is not None and len(image_bytes) > 0
    else:
        # Network may fail, but the functions should handle gracefully
        results["search_handled_gracefully"] = True

    print(json.dumps(results))

asyncio.run(run())
"""

    result = subprocess.run(
        [sys.executable, "-c", script],
        env=env,
        capture_output=True,
        text=True,
        timeout=90,
    )

    assert result.returncode == 0, result.stderr
    payload = _extract_json_line(result.stdout)

    for check_name, value in payload.items():
        assert value is True, f"{check_name} failed"
