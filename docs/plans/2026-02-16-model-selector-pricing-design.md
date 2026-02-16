# Model Selector Pricing + Curation (Cognitia)

Date: 2026-02-16

## Goals
- Make the model selector educational: show cost in COP alongside capabilities.
- Reduce noise by curating 1-9 models per category by default.
- Keep pricing fresh via scheduled sync and on-demand fallback.

## Non-Goals
- Do not expose pricepertoken directly to the client.
- Do not make curation admin-configurable yet.

## Architecture
Backend-centric integration:
- Backend service syncs pricing from pricepertoken.com.
- Cached data served via API to frontend.
- Frontend only renders costs and triggers fallback refresh if needed.

## Data Model
New table: model_pricing
- model_id (PK)
- provider
- input_usd_per_million
- output_usd_per_million
- context_window (optional)
- updated_at
- source (pricepertoken)
- raw (json, optional)

Cache/TTL:
- Logical TTL: 24h (configurable)
- Scheduled job refreshes all.
- On-demand refresh updates only missing/expired models.

## Data Flow
Backend:
1. Scheduled job pulls pricing and updates model_pricing.
2. GET /api/pricing/models returns cached data.
3. POST /api/pricing/refresh refreshes only missing/expired models.

Frontend:
1. Selector fetches pricing map on open.
2. COP cost derived with fixed rate: 1 USD = 4000 COP.
3. Missing price shows "Sin precio aun" and triggers background refresh.

## UI/UX
- Each model item shows an extra cost line:
  - Costo aprox: COP X / 1K tokens (input)
  - Costo aprox: COP Y / 1K tokens (output)
- Educational note above list:
  - "Precios estimados. 1 USD = 4000 COP. Costos por 1M tokens"
- Curated view default: 1-9 models per category, with "Ver todos" toggle.
- Subcategoría "Especiales" (audio/realtime/imagen/moderación/search), oculta por defecto y visible al activar "Ver todos".

## Error Handling
Backend:
- Job failures keep last known cache and log error.
- GET returns cached data even if stale.
- POST returns per-model status.

Frontend:
- If pricing fetch fails, selector works without prices.
- Missing price shows "Sin precio aun" and does not block selection.

## Testing
Backend:
- Unit tests for pricepertoken mapping.
- Tests for job refresh logic, TTL, fallback.

Frontend:
- Unit tests for cost rendering (with and without price).
- Tests for curated view vs "ver todos" toggle.

## Open Questions
- Exact refresh interval (default proposal: every 12h).
- Which curated models per category (initial list in code).
