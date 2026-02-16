from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from open_webui.models.pricing import ModelPricingModel, PricingTable
from open_webui.utils.pricing import refresh_missing_or_expired, fetch_pricepertoken_models
from open_webui.utils.auth import get_verified_user, get_admin_user

router = APIRouter()
pricing_table = PricingTable()


@router.get("/models")
async def get_pricing_models(user=Depends(get_verified_user)):
    rows = pricing_table.get_all()
    items = [ModelPricingModel.model_validate(r).model_dump() for r in rows]
    updated_at = max([r.updated_at for r in rows], default=None)
    return {"items": items, "updated_at": updated_at}


class PricingRefreshForm(BaseModel):
    model_ids: list[str] = []


@router.post("/refresh")
async def refresh_pricing_models(form: PricingRefreshForm, user=Depends(get_verified_user)):
    refreshed = await refresh_missing_or_expired(form.model_ids)
    return {"items": refreshed}


@router.get("/debug/sample")
async def debug_pricepertoken_sample(
    limit: int = Query(1, ge=1, le=5),
    user=Depends(get_admin_user),
):
    rows = await fetch_pricepertoken_models()
    sample = rows[:limit]
    keys = sorted({key for row in sample if isinstance(row, dict) for key in row.keys()})
    return {
        "count": len(rows),
        "sample_count": len(sample),
        "keys": keys,
        "sample": sample,
    }
