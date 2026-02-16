import asyncio
import logging
import time
from typing import Iterable, Optional

from open_webui.env import (
    PRICEPERTOKEN_MCP_URL,
    PRICING_CACHE_TTL_SECONDS,
    PRICING_REFRESH_INTERVAL_SECONDS,
)
from open_webui.models.pricing import PricingTable
from open_webui.utils.mcp.client import MCPClient

log = logging.getLogger(__name__)

PRICING_SOURCE = "pricepertoken"
PRICING_SOURCE_FALLBACK = "static"

# Fallback pricing data for common models when MCP is unavailable
# Prices are in USD per million tokens (as of Feb 2026)
FALLBACK_PRICING_DATA = [
    # OpenAI models
    {"model_id": "gpt-4o", "provider": "openai", "input_cost_per_million": 2.50, "output_cost_per_million": 10.00, "context_window": 128000},
    {"model_id": "gpt-4o-mini", "provider": "openai", "input_cost_per_million": 0.15, "output_cost_per_million": 0.60, "context_window": 128000},
    {"model_id": "gpt-4.5-preview", "provider": "openai", "input_cost_per_million": 75.00, "output_cost_per_million": 150.00, "context_window": 128000},
    {"model_id": "gpt-4-turbo", "provider": "openai", "input_cost_per_million": 10.00, "output_cost_per_million": 30.00, "context_window": 128000},
    {"model_id": "gpt-3.5-turbo", "provider": "openai", "input_cost_per_million": 0.50, "output_cost_per_million": 1.50, "context_window": 16385},
    {"model_id": "o1", "provider": "openai", "input_cost_per_million": 15.00, "output_cost_per_million": 60.00, "context_window": 200000},
    {"model_id": "o1-mini", "provider": "openai", "input_cost_per_million": 3.00, "output_cost_per_million": 12.00, "context_window": 128000},
    {"model_id": "o1-pro", "provider": "openai", "input_cost_per_million": 150.00, "output_cost_per_million": 600.00, "context_window": 200000},
    {"model_id": "o3-mini", "provider": "openai", "input_cost_per_million": 1.10, "output_cost_per_million": 4.40, "context_window": 200000},
    # Anthropic models
    {"model_id": "claude-3-5-sonnet-20241022", "provider": "anthropic", "input_cost_per_million": 3.00, "output_cost_per_million": 15.00, "context_window": 200000},
    {"model_id": "claude-3-5-haiku-20241022", "provider": "anthropic", "input_cost_per_million": 0.80, "output_cost_per_million": 4.00, "context_window": 200000},
    {"model_id": "claude-3-opus-20240229", "provider": "anthropic", "input_cost_per_million": 15.00, "output_cost_per_million": 75.00, "context_window": 200000},
    {"model_id": "claude-opus-4-20250514", "provider": "anthropic", "input_cost_per_million": 15.00, "output_cost_per_million": 75.00, "context_window": 200000},
    {"model_id": "claude-sonnet-4-20250514", "provider": "anthropic", "input_cost_per_million": 3.00, "output_cost_per_million": 15.00, "context_window": 200000},
    # Google models
    {"model_id": "gemini-2.0-flash", "provider": "google", "input_cost_per_million": 0.10, "output_cost_per_million": 0.40, "context_window": 1048576},
    {"model_id": "gemini-1.5-pro", "provider": "google", "input_cost_per_million": 1.25, "output_cost_per_million": 5.00, "context_window": 2097152},
    {"model_id": "gemini-1.5-flash", "provider": "google", "input_cost_per_million": 0.075, "output_cost_per_million": 0.30, "context_window": 1048576},
    # DeepSeek models
    {"model_id": "deepseek-chat", "provider": "deepseek", "input_cost_per_million": 0.27, "output_cost_per_million": 1.10, "context_window": 64000},
    {"model_id": "deepseek-reasoner", "provider": "deepseek", "input_cost_per_million": 0.55, "output_cost_per_million": 2.19, "context_window": 64000},
    # Local/Free models (cognitia)
    {"model_id": "cognitia_llm_zerogpu.phi3", "provider": "cognitia", "input_cost_per_million": 0.0, "output_cost_per_million": 0.0, "context_window": 4096},
    {"model_id": "cognitia_llm_zerogpu.qwen2.5-7b", "provider": "cognitia", "input_cost_per_million": 0.0, "output_cost_per_million": 0.0, "context_window": 32768},
    {"model_id": "cognitia_llm_zerogpu.smollm2", "provider": "cognitia", "input_cost_per_million": 0.0, "output_cost_per_million": 0.0, "context_window": 8192},
    {"model_id": "cognitia_llm_zerogpu.mistral-7b", "provider": "cognitia", "input_cost_per_million": 0.0, "output_cost_per_million": 0.0, "context_window": 32768},
]


def _extract_mcp_json(content):
    if content is None:
        return None
    if isinstance(content, (dict, list)):
        return content
    return None


def _extract_model_id(row: dict) -> Optional[str]:
    for key in ("model_id", "id", "model", "name", "slug"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _extract_context_window(row: dict) -> Optional[int]:
    for key in ("context_window", "context_length", "max_context", "max_context_window"):
        value = row.get(key)
        if isinstance(value, (int, float)) and value > 0:
            return int(value)
    return None


def _extract_price(row: dict, keys: Iterable[str]) -> Optional[float]:
    for key in keys:
        if key not in row:
            continue
        value = row.get(key)
        if value is None:
            continue
        try:
            value = float(value)
        except Exception:
            continue

        lower_key = key.lower()
        if "per_token" in lower_key:
            return value * 1_000_000
        if "per_1k" in lower_key or "per_1000" in lower_key:
            return value * 1000
        # Assume per-million if unit not specified
        return value

    return None


def map_pricepertoken_model(row: dict, source: str = PRICING_SOURCE) -> Optional[dict]:
    model_id = _extract_model_id(row)
    if not model_id:
        return None

    input_usd = _extract_price(
        row,
        (
            "input_cost_per_million",
            "input_cost_per_million_tokens",
            "input_usd_per_million",
            "input_price",
            "price_input",
            "input_cost",
            "input_cost_per_1k",
            "input_cost_per_1000",
            "input_cost_per_token",
        ),
    )
    output_usd = _extract_price(
        row,
        (
            "output_cost_per_million",
            "output_cost_per_million_tokens",
            "output_usd_per_million",
            "output_price",
            "price_output",
            "output_cost",
            "output_cost_per_1k",
            "output_cost_per_1000",
            "output_cost_per_token",
        ),
    )

    if input_usd is None and output_usd is None:
        return None

    provider = row.get("provider") or row.get("vendor") or row.get("owned_by") or ""
    return {
        "model_id": model_id,
        "provider": provider,
        "input_usd_per_million": input_usd or 0.0,
        "output_usd_per_million": output_usd or 0.0,
        "context_window": _extract_context_window(row),
        "source": source,
        "raw": row,
    }


def get_fallback_pricing_data() -> list[dict]:
    """Return static fallback pricing data when MCP is unavailable."""
    return [
        {
            "model_id": row["model_id"],
            "provider": row["provider"],
            "input_cost_per_million": row["input_cost_per_million"],
            "output_cost_per_million": row["output_cost_per_million"],
            "context_window": row.get("context_window"),
        }
        for row in FALLBACK_PRICING_DATA
    ]


async def fetch_pricepertoken_models() -> tuple[list[dict], str]:
    """Fetch pricing data from MCP, falling back to static data on failure.

    Returns:
        Tuple of (data, source) where source is 'pricepertoken' or 'static'
    """
    try:
        client = MCPClient()
        await client.connect(url=PRICEPERTOKEN_MCP_URL)
        try:
            content = await client.call_tool("get_all_models", {})
            payload = _extract_mcp_json(content)
            if isinstance(payload, dict):
                if "models" in payload and isinstance(payload["models"], list):
                    return payload["models"], PRICING_SOURCE
                if "items" in payload and isinstance(payload["items"], list):
                    return payload["items"], PRICING_SOURCE
            if isinstance(payload, list):
                return payload, PRICING_SOURCE
            log.warning("MCP returned unexpected format, using fallback data")
            return get_fallback_pricing_data(), PRICING_SOURCE_FALLBACK
        finally:
            await client.disconnect()
    except Exception as exc:
        log.warning("MCP pricing fetch failed (%s), using fallback data", exc)
        return get_fallback_pricing_data(), PRICING_SOURCE_FALLBACK


async def refresh_pricing(model_ids: Optional[list[str]] = None) -> list[dict]:
    data, source = await fetch_pricepertoken_models()
    rows = []
    for row in data:
        if not isinstance(row, dict):
            continue
        mapped = map_pricepertoken_model(row, source=source)
        if not mapped:
            continue
        if model_ids and mapped["model_id"] not in model_ids:
            continue
        rows.append(mapped)

    if rows:
        PricingTable().upsert(rows)
        log.info("Refreshed %d pricing entries from %s", len(rows), source)
    return rows


async def refresh_missing_or_expired(model_ids: list[str]) -> list[str]:
    if not model_ids:
        return []
    table = PricingTable()
    rows = table.get_by_ids(model_ids)
    now = int(time.time())

    existing = {row.model_id: row for row in rows}
    missing_or_expired = []
    for model_id in model_ids:
        row = existing.get(model_id)
        if not row:
            missing_or_expired.append(model_id)
            continue
        if row.updated_at is None:
            missing_or_expired.append(model_id)
            continue
        if now - row.updated_at > PRICING_CACHE_TTL_SECONDS:
            missing_or_expired.append(model_id)

    if missing_or_expired:
        await refresh_pricing(missing_or_expired)
    return missing_or_expired


async def pricing_refresh_loop():
    while True:
        try:
            await refresh_pricing()
        except Exception as exc:
            log.warning("Pricing refresh failed: %s", exc)
        await asyncio.sleep(PRICING_REFRESH_INTERVAL_SECONDS)
