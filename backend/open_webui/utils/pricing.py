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


def map_pricepertoken_model(row: dict) -> Optional[dict]:
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
        "source": PRICING_SOURCE,
        "raw": row,
    }


async def fetch_pricepertoken_models() -> list[dict]:
    client = MCPClient()
    await client.connect(url=PRICEPERTOKEN_MCP_URL)
    try:
        content = await client.call_tool("get_all_models", {})
        payload = _extract_mcp_json(content)
        if isinstance(payload, dict):
            if "models" in payload and isinstance(payload["models"], list):
                return payload["models"]
            if "items" in payload and isinstance(payload["items"], list):
                return payload["items"]
        if isinstance(payload, list):
            return payload
        return []
    finally:
        await client.disconnect()


async def refresh_pricing(model_ids: Optional[list[str]] = None) -> list[dict]:
    data = await fetch_pricepertoken_models()
    rows = []
    for row in data:
        if not isinstance(row, dict):
            continue
        mapped = map_pricepertoken_model(row)
        if not mapped:
            continue
        if model_ids and mapped["model_id"] not in model_ids:
            continue
        rows.append(mapped)

    if rows:
        PricingTable().upsert(rows)
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
