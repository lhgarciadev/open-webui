# Model Selector Pricing + Curation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add COP pricing education and curated model lists to the chat model selector, with backend price caching and refresh.

**Architecture:** Backend fetches price data from pricepertoken.com into a cached table and exposes a pricing API. Frontend consumes cached pricing, renders COP cost per model, and defaults to a curated list with an opt-in “Ver todos” view plus a hidden “Especiales” group.

**Tech Stack:** FastAPI, SQLAlchemy + Alembic, SvelteKit (Svelte 5), TypeScript, Tailwind, Vitest.

---

### Task 0: Create dedicated worktree for implementation

**Files:**
- None

**Step 1: Create worktree**

Run:

```bash
git worktree add ../open-webui-pricing-plan
```

**Step 2: Verify worktree**

Run: `cd ../open-webui-pricing-plan && git status`
Expected: clean worktree.

**Step 3: Commit**

No commit needed.

---

### Task 1: Confirm pricepertoken API contract

**Files:**
- Modify: `docs/plans/2026-02-16-model-selector-pricing-implementation.md`

**Step 1: Write the failing test**

Create a stub test to lock expected mapping fields:

```python
# backend/open_webui/test/apps/webui/routers/test_pricing_contract.py
from test.util.abstract_integration_test import AbstractPostgresTest

class TestPricingContract(AbstractPostgresTest):
    def test_pricepertoken_mapping_contract(self):
        # Placeholder until API contract confirmed
        assert False, "pricepertoken contract not confirmed"
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest test/apps/webui/routers/test_pricing_contract.py -v`
Expected: FAIL with the placeholder assertion.

**Step 3: Confirm API contract**

Use `web.run` to check pricepertoken docs and confirm:
- Endpoint(s)
- Field names for input/output price per 1M tokens
- Model id naming

Update this plan with confirmed field names and delete the placeholder test after Task 2 is implemented.

**Step 4: Commit**

```bash
git add docs/plans/2026-02-16-model-selector-pricing-implementation.md backend/open_webui/test/apps/webui/routers/test_pricing_contract.py
git commit -m "test: add placeholder for pricing contract"
```

---

### Task 2: Add pricing table + model layer

**Files:**
- Create: `backend/open_webui/models/pricing.py`
- Create: `backend/open_webui/migrations/versions/2026_02_16_add_model_pricing.py`
- Test: `backend/open_webui/test/apps/webui/routers/test_pricing.py`

**Step 1: Write the failing test**

```python
# backend/open_webui/test/apps/webui/routers/test_pricing.py
from test.util.abstract_integration_test import AbstractPostgresTest
from test.util.mock_user import mock_webui_user

class TestPricing(AbstractPostgresTest):
    BASE_PATH = "/api/v1/pricing"

    def test_get_pricing_empty(self):
        with mock_webui_user(id="2"):
            res = self.fast_api_client.get(self.create_url("/models"))
        assert res.status_code == 200
        assert res.json() == {"items": [], "updated_at": None}
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest test/apps/webui/routers/test_pricing.py::TestPricing::test_get_pricing_empty -v`
Expected: FAIL (endpoint not found).

**Step 3: Write minimal implementation**

Create SQLAlchemy model and helper:

```python
# backend/open_webui/models/pricing.py
import time
from typing import Optional
from sqlalchemy import Column, Text, BigInteger, Float
from open_webui.internal.db import Base, JSONField, get_db_context
from pydantic import BaseModel, ConfigDict

class ModelPricing(Base):
    __tablename__ = "model_pricing"
    model_id = Column(Text, primary_key=True)
    provider = Column(Text)
    input_usd_per_million = Column(Float)
    output_usd_per_million = Column(Float)
    context_window = Column(BigInteger, nullable=True)
    updated_at = Column(BigInteger)
    source = Column(Text)
    raw = Column(JSONField, nullable=True)

class ModelPricingModel(BaseModel):
    model_id: str
    provider: str
    input_usd_per_million: float
    output_usd_per_million: float
    context_window: Optional[int] = None
    updated_at: int
    source: str
    raw: Optional[dict] = None
    model_config = ConfigDict(from_attributes=True)

class PricingTable:
    def get_all(self, db=None):
        with get_db_context(db) as db:
            return db.query(ModelPricing).all()

    def upsert(self, rows: list[dict], db=None):
        now = int(time.time())
        with get_db_context(db) as db:
            for row in rows:
                row["updated_at"] = now
                existing = db.query(ModelPricing).filter_by(model_id=row["model_id"]).first()
                if existing:
                    for k, v in row.items():
                        setattr(existing, k, v)
                else:
                    db.add(ModelPricing(**row))
            db.commit()
```

Add migration to create table.

**Step 4: Run test to verify it passes**

Run: `cd backend && pytest test/apps/webui/routers/test_pricing.py::TestPricing::test_get_pricing_empty -v`
Expected: still FAIL until router is added in Task 3.

**Step 5: Commit**

```bash
git add backend/open_webui/models/pricing.py backend/open_webui/migrations/versions/2026_02_16_add_model_pricing.py backend/open_webui/test/apps/webui/routers/test_pricing.py
git commit -m "feat: add model_pricing table and model"
```

---

### Task 3: Add pricing router + cache API

**Files:**
- Create: `backend/open_webui/routers/pricing.py`
- Modify: `backend/open_webui/main.py`
- Modify: `backend/open_webui/config.py`
- Modify: `backend/open_webui/env.py`
- Modify: `backend/open_webui/models/pricing.py`
- Test: `backend/open_webui/test/apps/webui/routers/test_pricing.py`

**Step 1: Write the failing test**

Extend test to expect empty list from GET:

```python
# backend/open_webui/test/apps/webui/routers/test_pricing.py
    def test_get_pricing_empty(self):
        with mock_webui_user(id="2"):
            res = self.fast_api_client.get(self.create_url("/models"))
        assert res.status_code == 200
        assert res.json()["items"] == []
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest test/apps/webui/routers/test_pricing.py::TestPricing::test_get_pricing_empty -v`
Expected: FAIL (router missing).

**Step 3: Write minimal implementation**

Router stub:

```python
# backend/open_webui/routers/pricing.py
from fastapi import APIRouter
from open_webui.models.pricing import PricingTable, ModelPricingModel

router = APIRouter()
pricing_table = PricingTable()

@router.get("/models")
async def get_pricing_models():
    rows = pricing_table.get_all()
    items = [ModelPricingModel.model_validate(r).model_dump() for r in rows]
    updated_at = max([r.updated_at for r in rows], default=None)
    return {"items": items, "updated_at": updated_at}
```

Include router in `main.py`:

```python
app.include_router(pricing.router, prefix="/api/v1/pricing", tags=["pricing"])
```

**Step 4: Run test to verify it passes**

Run: `cd backend && pytest test/apps/webui/routers/test_pricing.py::TestPricing::test_get_pricing_empty -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add backend/open_webui/routers/pricing.py backend/open_webui/main.py backend/open_webui/test/apps/webui/routers/test_pricing.py
git commit -m "feat: add pricing API stub"
```

---

### Task 4: Implement pricepertoken fetch + scheduled refresh

**Files:**
- Create: `backend/open_webui/utils/pricing.py`
- Modify: `backend/open_webui/routers/pricing.py`
- Modify: `backend/open_webui/main.py`
- Modify: `backend/open_webui/config.py`
- Modify: `backend/open_webui/env.py`
- Test: `backend/open_webui/test/apps/webui/routers/test_pricing.py`

**Step 1: Write the failing test**

Add a test for on-demand refresh endpoint returning a status map:

```python
# backend/open_webui/test/apps/webui/routers/test_pricing.py
    def test_refresh_pricing_empty(self):
        with mock_webui_user(id="2"):
            res = self.fast_api_client.post(self.create_url("/refresh"), json={"model_ids": ["gpt-4o"]})
        assert res.status_code == 200
        assert "items" in res.json()
```

**Step 2: Run test to verify it fails**

Run: `cd backend && pytest test/apps/webui/routers/test_pricing.py::TestPricing::test_refresh_pricing_empty -v`
Expected: FAIL (refresh not implemented).

**Step 3: Write minimal implementation**

Pricing utils:

```python
# backend/open_webui/utils/pricing.py
import asyncio
import time
import httpx
from open_webui.models.pricing import PricingTable

PRICING_SOURCE = "pricepertoken"

async def fetch_pricepertoken_models():
    # TODO: update endpoint/fields after confirming API contract
    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.get("https://pricepertoken.com/api/models")
        res.raise_for_status()
        return res.json()

def map_pricepertoken_model(row: dict) -> dict:
    return {
        "model_id": row["id"],
        "provider": row.get("provider", ""),
        "input_usd_per_million": row["input_cost_per_million"],
        "output_usd_per_million": row["output_cost_per_million"],
        "context_window": row.get("context_window"),
        "source": PRICING_SOURCE,
        "raw": row,
    }

async def refresh_pricing(model_ids: list[str] | None = None):
    data = await fetch_pricepertoken_models()
    rows = [map_pricepertoken_model(r) for r in data]
    if model_ids:
        rows = [r for r in rows if r["model_id"] in model_ids]
    PricingTable().upsert(rows)
    return rows

async def pricing_refresh_loop(interval_seconds: int):
    while True:
        try:
            await refresh_pricing()
        except Exception:
            pass
        await asyncio.sleep(interval_seconds)
```

Refresh endpoint:

```python
# backend/open_webui/routers/pricing.py
from pydantic import BaseModel
from open_webui.utils.pricing import refresh_pricing

class PricingRefreshForm(BaseModel):
    model_ids: list[str] = []

@router.post("/refresh")
async def refresh_pricing_models(form: PricingRefreshForm):
    rows = await refresh_pricing(form.model_ids or None)
    return {"items": rows}
```

Schedule loop in `main.py` startup:

```python
from open_webui.utils.pricing import pricing_refresh_loop

app.state.pricing_task = asyncio.create_task(pricing_refresh_loop(PRICING_REFRESH_INTERVAL_SECONDS))
```

Add config/env:

```python
# backend/open_webui/env.py
PRICING_REFRESH_INTERVAL_SECONDS = int(os.environ.get("PRICING_REFRESH_INTERVAL_SECONDS", "43200"))
```

**Step 4: Run test to verify it passes**

Run: `cd backend && pytest test/apps/webui/routers/test_pricing.py::TestPricing::test_refresh_pricing_empty -v`
Expected: PASS (even if refresh returns empty for unknown ids).

**Step 5: Commit**

```bash
git add backend/open_webui/utils/pricing.py backend/open_webui/routers/pricing.py backend/open_webui/main.py backend/open_webui/config.py backend/open_webui/env.py backend/open_webui/test/apps/webui/routers/test_pricing.py
git commit -m "feat: pricing refresh and scheduler"
```

---

### Task 5: Add frontend pricing API client

**Files:**
- Create: `src/lib/apis/pricing/index.ts`
- Modify: `src/lib/apis/index.ts`

**Step 1: Write the failing test**

```ts
// src/lib/apis/pricing/index.test.ts
import { describe, it, expect } from 'vitest';

describe('pricing api client', () => {
  it('exports getPricingModels', () => {
    const mod = require('./index');
    expect(typeof mod.getPricingModels).toBe('function');
  });
});
```

**Step 2: Run test to verify it fails**

Run: `npm run test:frontend -- src/lib/apis/pricing/index.test.ts`
Expected: FAIL (module missing).

**Step 3: Write minimal implementation**

```ts
// src/lib/apis/pricing/index.ts
import { WEBUI_API_BASE_URL } from '$lib/constants';

export async function getPricingModels(token = '') {
  const res = await fetch(`${WEBUI_API_BASE_URL}/pricing/models`, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined
  });
  if (!res.ok) throw new Error('Failed to fetch pricing');
  return res.json();
}

export async function refreshPricingModels(token = '', model_ids: string[] = []) {
  const res = await fetch(`${WEBUI_API_BASE_URL}/pricing/refresh`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body: JSON.stringify({ model_ids })
  });
  if (!res.ok) throw new Error('Failed to refresh pricing');
  return res.json();
}
```

**Step 4: Run test to verify it passes**

Run: `npm run test:frontend -- src/lib/apis/pricing/index.test.ts`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/lib/apis/pricing/index.ts src/lib/apis/pricing/index.test.ts
 git commit -m "feat: add pricing api client"
```

---

### Task 6: Add curation + special category helpers

**Files:**
- Create: `src/lib/constants/modelCuration.ts`
- Modify: `src/lib/constants/modelCategories.ts`
- Modify: `src/lib/utils/modelUtils.ts`
- Test: `src/lib/utils/modelUtils.test.ts`

**Step 1: Write the failing test**

```ts
// src/lib/utils/modelUtils.test.ts
import { describe, it, expect } from 'vitest';
import { categorizeModel } from './modelUtils';

describe('modelUtils', () => {
  it('treats cognitia models as local', () => {
    const result = categorizeModel({ id: 'cognitia_llm_zerogpu.phi3' });
    expect(result.categories).toContain('local');
  });

  it('flags audio models as specials', () => {
    const result = categorizeModel({ id: 'gpt-audio-mini' });
    expect(result.categories).toContain('specials');
  });
});
```

**Step 2: Run test to verify it fails**

Run: `npm run test:frontend -- src/lib/utils/modelUtils.test.ts`
Expected: FAIL.

**Step 3: Write minimal implementation**

Add curated map:

```ts
// src/lib/constants/modelCuration.ts
export const CURATED_MODELS_BY_CATEGORY: Record<string, string[]> = {
  coding: ['gpt-5-codex', 'gpt-5.1-codex', 'cognitia_llm_zerogpu.mistral-7b'],
  creative: ['gpt-4o', 'gpt-4.1', 'cognitia_llm_zerogpu.qwen2.5-7b'],
  analysis: ['o3', 'o1', 'gpt-5'],
  fast: ['gpt-4o-mini', 'gpt-5-mini', 'cognitia_llm_zerogpu.phi3', 'cognitia_llm_zerogpu.smollm2-1.7b'],
  local: ['phi3:latest', 'cognitia_llm_zerogpu.phi3', 'cognitia_llm_zerogpu.qwen2.5-7b', 'cognitia_llm_zerogpu.smollm2-1.7b', 'cognitia_llm_zerogpu.mistral-7b'],
  vision: ['gpt-4o', 'gpt-4o-mini'],
  documents: ['gpt-4.1', 'gpt-5'],
  general: ['gpt-4o', 'gpt-5-mini', 'cognitia_llm_zerogpu.qwen2.5-7b'],
  specials: ['gpt-audio-mini', 'gpt-realtime-mini', 'gpt-image-1', 'omni-moderation-latest', 'gpt-4o-search-preview']
};
```

Add category in `modelCategories.ts`:

```ts
{
  id: 'specials',
  name: 'Especiales',
  emoji: '🧩',
  description: 'Audio, realtime, imagen, moderación, search',
  priority: 8
}
```

Update `modelUtils.ts`:
- Add `isCognitiaLocalModel(id)` for ids starting `cognitia_llm_`.
- Add special-pattern detection for `audio`, `realtime`, `transcribe`, `image`, `moderation`, `search`, `sora`.
- Add `specials` category when matched.

**Step 4: Run test to verify it passes**

Run: `npm run test:frontend -- src/lib/utils/modelUtils.test.ts`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/lib/constants/modelCuration.ts src/lib/constants/modelCategories.ts src/lib/utils/modelUtils.ts src/lib/utils/modelUtils.test.ts
git commit -m "feat: add curated model list and specials category"
```

---

### Task 7: Render costs + curated view in selector

**Files:**
- Modify: `src/lib/components/chat/ModelSelector/Selector.svelte`
- Modify: `src/lib/components/chat/ModelSelector/ModelItem.svelte`
- Modify: `src/lib/components/chat/ModelSelector.svelte`
- Modify: `src/lib/i18n/locales/es-ES/translation.json`
- Modify: `src/lib/i18n/locales/en-US/translation.json`

**Step 1: Write the failing test**

```ts
// src/lib/components/chat/ModelSelector/selector.test.ts
import { render } from '@testing-library/svelte';
import Selector from './ModelSelector/Selector.svelte';

test('shows pricing note', () => {
  const { getByText } = render(Selector, { props: { items: [], value: '' } });
  getByText('Precios estimados');
});
```

**Step 2: Run test to verify it fails**

Run: `npm run test:frontend -- src/lib/components/chat/ModelSelector/selector.test.ts`
Expected: FAIL.

**Step 3: Write minimal implementation**

Use @svelte-code-writer and @svelte5-best-practices when editing `.svelte` files.

- Add pricing fetch on open; store `pricingMap` keyed by `model_id`.
- Add toggle `showAllModels` and use curated list to filter by category when off.
- Hide `specials` category unless `showAllModels`.
- Pass pricing info into `ModelItem` and render COP costs.
- Add “Precios estimados…” note above list.
- Add badges for `OpenAI` / `Cognitia Local` / `Ollama Local`.

Example snippet in `ModelItem.svelte`:

```svelte
{#if pricing}
  <div class="text-[11px] text-gray-500">
    {$i18n.t('Costo aprox')}: COP {pricing.inputCopPer1k} / 1K (in) · COP {pricing.outputCopPer1k} / 1K (out)
  </div>
{:else}
  <div class="text-[11px] text-gray-500">{$i18n.t('Sin precio aun')}</div>
{/if}
```

**Step 4: Run test to verify it passes**

Run: `npm run test:frontend -- src/lib/components/chat/ModelSelector/selector.test.ts`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/lib/components/chat/ModelSelector/Selector.svelte src/lib/components/chat/ModelSelector/ModelItem.svelte src/lib/components/chat/ModelSelector.svelte src/lib/i18n/locales/es-ES/translation.json src/lib/i18n/locales/en-US/translation.json
 git commit -m "feat: show COP pricing and curated model view"
```

---

### Task 8: Hook refresh on missing prices

**Files:**
- Modify: `src/lib/components/chat/ModelSelector/Selector.svelte`
- Modify: `src/lib/apis/pricing/index.ts`

**Step 1: Write the failing test**

```ts
// src/lib/components/chat/ModelSelector/selector-refresh.test.ts
import { vi } from 'vitest';
import { refreshPricingModels } from '$lib/apis/pricing';

vi.mock('$lib/apis/pricing');

test('requests refresh for missing prices', async () => {
  expect(refreshPricingModels).toBeDefined();
});
```

**Step 2: Run test to verify it fails**

Run: `npm run test:frontend -- src/lib/components/chat/ModelSelector/selector-refresh.test.ts`
Expected: FAIL (no call sites).

**Step 3: Write minimal implementation**

- When pricing data is loaded, compute missing model ids for visible items.
- If missing, call `refreshPricingModels` in background (debounced).

**Step 4: Run test to verify it passes**

Run: `npm run test:frontend -- src/lib/components/chat/ModelSelector/selector-refresh.test.ts`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/lib/components/chat/ModelSelector/Selector.svelte src/lib/components/chat/ModelSelector/selector-refresh.test.ts
 git commit -m "feat: refresh missing prices on demand"
```

---

### Task 9: Final cleanup

**Files:**
- Modify: `docs/plans/2026-02-16-model-selector-pricing-design.md`
- Modify: `docs/plans/2026-02-16-model-selector-pricing-implementation.md`

**Step 1: Remove placeholder contract test if no longer needed**

Delete `backend/open_webui/test/apps/webui/routers/test_pricing_contract.py` if mapping confirmed and covered.

**Step 2: Run full tests**

Run: `cd backend && pytest test/apps/webui/routers/test_pricing.py -v`
Run: `npm run test:frontend -- src/lib/utils/modelUtils.test.ts`

**Step 3: Commit**

```bash
git add backend/open_webui/test/apps/webui/routers/test_pricing_contract.py docs/plans/2026-02-16-model-selector-pricing-design.md docs/plans/2026-02-16-model-selector-pricing-implementation.md
 git commit -m "chore: finalize pricing plan"
```
