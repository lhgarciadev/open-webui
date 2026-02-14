"""
Image Service for Presentations.

Provides image search functionality using Wikimedia Commons (free, no API key).
Falls back to branded placeholders when no image is found.
"""

import httpx
import logging
from typing import Optional, Dict, Any
from collections import OrderedDict
from urllib.parse import quote

log = logging.getLogger(__name__)

WIKIMEDIA_API_URL = "https://commons.wikimedia.org/w/api.php"

# LRU Cache for downloaded images (max 50)
_image_cache: OrderedDict[str, bytes] = OrderedDict()
MAX_CACHE_SIZE = 50


async def _search_wikimedia(query: str) -> Optional[Dict[str, Any]]:
    """
    Search for an image on Wikimedia Commons (free, no API key required).

    Args:
        query: Search terms

    Returns:
        Dict with url, photographer_name, source
        None if no results or error
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Search for images matching the query
            response = await client.get(
                WIKIMEDIA_API_URL,
                params={
                    "action": "query",
                    "format": "json",
                    "generator": "search",
                    "gsrnamespace": "6",  # File namespace
                    "gsrsearch": f"filetype:bitmap {query}",
                    "gsrlimit": "5",
                    "prop": "imageinfo",
                    "iiprop": "url|user|extmetadata",
                    "iiurlwidth": "800",  # Request thumbnail at 800px width
                },
                headers={
                    "User-Agent": "CognitiaAI/1.0 (Presentation Generator)"
                }
            )
            response.raise_for_status()
            data = response.json()

            pages = data.get("query", {}).get("pages", {})
            if not pages:
                log.debug(f"No Wikimedia results for query: {query}")
                return None

            # Get first valid image
            for page_id, page in pages.items():
                if page_id == "-1":
                    continue

                imageinfo = page.get("imageinfo", [])
                if not imageinfo:
                    continue

                info = imageinfo[0]
                thumb_url = info.get("thumburl") or info.get("url")

                if not thumb_url:
                    continue

                # Get photographer/author from metadata
                metadata = info.get("extmetadata", {})
                artist = metadata.get("Artist", {}).get("value", "")
                # Clean HTML tags from artist name
                if "<" in artist:
                    import re
                    artist = re.sub(r'<[^>]+>', '', artist).strip()

                photographer = artist or info.get("user", "Wikimedia Commons")

                return {
                    "url": thumb_url,
                    "photographer_name": photographer[:50],  # Limit length
                    "source": "wikimedia",
                }

            log.debug(f"No valid images found for query: {query}")
            return None

    except Exception as e:
        log.warning(f"Wikimedia search error for '{query}': {e}")
        return None


async def search_image(query: str, size: str = "regular") -> Optional[Dict[str, Any]]:
    """
    Search for an image using Wikimedia Commons.

    Args:
        query: Search terms
        size: Ignored (Wikimedia returns appropriate size)

    Returns:
        Dict with url, photographer_name, source
        None if no results
    """
    if not query or not query.strip():
        return None

    # Try Wikimedia Commons
    result = await _search_wikimedia(query)
    if result:
        log.debug(f"Found Wikimedia image for '{query}'")
        return result

    log.debug(f"No images found for query: {query}")
    return None


async def download_image(url: str) -> Optional[bytes]:
    """
    Download an image from URL with LRU caching.

    Args:
        url: Image URL to download

    Returns:
        Image bytes or None on error
    """
    if not url:
        return None

    # Check cache first
    if url in _image_cache:
        # Move to end (most recently used)
        _image_cache.move_to_end(url)
        return _image_cache[url]

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                headers={
                    "User-Agent": "CognitiaAI/1.0 (Presentation Generator)"
                },
                follow_redirects=True
            )
            response.raise_for_status()

            # Verify it's an image
            content_type = response.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                log.warning(f"URL did not return image: {content_type}")
                return None

            image_bytes = response.content

            # Add to cache
            if len(_image_cache) >= MAX_CACHE_SIZE:
                # Remove oldest (first) item
                _image_cache.popitem(last=False)
            _image_cache[url] = image_bytes

            return image_bytes

    except Exception as e:
        log.warning(f"Error downloading image from {url}: {e}")
        return None


def extract_keywords(text: str, max_words: int = 3) -> str:
    """
    Extract relevant keywords from text for image search.

    Strategy:
    1. Remove stopwords (Spanish and English)
    2. Prioritize nouns and technical terms
    3. Limit to max_words unique words

    Args:
        text: Input text to extract keywords from
        max_words: Maximum number of keywords to return

    Returns:
        Space-separated keywords string
    """
    if not text:
        return ""

    # Stopwords for Spanish and English
    stopwords = {
        # Spanish
        'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del',
        'en', 'con', 'por', 'para', 'como', 'que', 'qué', 'es', 'son', 'y',
        'o', 'a', 'al', 'se', 'su', 'sus', 'este', 'esta', 'estos', 'estas',
        'muy', 'más', 'menos', 'sobre', 'entre', 'sin', 'cada', 'todo', 'toda',
        'lo', 'le', 'les', 'nos', 'me', 'te', 'si', 'no', 'pero', 'ya', 'bien',
        'ser', 'estar', 'tener', 'hacer', 'poder', 'decir', 'ir', 'ver', 'dar',
        'saber', 'querer', 'llegar', 'pasar', 'deber', 'poner', 'parecer',
        # English
        'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'and',
        'or', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
        'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
        'might', 'can', 'this', 'that', 'these', 'those', 'it', 'its', 'we',
        'you', 'your', 'they', 'their', 'he', 'she', 'him', 'her', 'our', 'us',
        'my', 'me', 'who', 'what', 'when', 'where', 'why', 'how', 'which',
        'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some',
        'such', 'than', 'too', 'very', 'just', 'also', 'now', 'only', 'then',
        # Presentation-specific stopwords
        'presentación', 'slide', 'diapositiva', 'contenido', 'introducción',
        'conclusión', 'resumen', 'puntos', 'clave', 'principales', 'agenda',
        'overview', 'summary', 'introduction', 'conclusion', 'key', 'main',
        'slide', 'presentation', 'content', 'points', 'next', 'steps',
    }

    # Tokenize and clean
    words = text.lower().split()
    words = [w.strip('.,;:!?()[]{}"\'-/\\') for w in words]
    words = [w for w in words if w and len(w) > 2 and w not in stopwords and not w.isdigit()]

    # Take first unique words
    seen = set()
    keywords = []
    for w in words:
        if w not in seen:
            seen.add(w)
            keywords.append(w)
            if len(keywords) >= max_words:
                break

    return ' '.join(keywords)
