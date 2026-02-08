# Technical Specifications

## 1. Frontend Specifications (SvelteKit)
### Global Replacement Strategy
- **Target String**: `Open WebUI` (Case insensitive search).
- **Replacement Scope**:
    - `src/app.html`: Meta tags, title.
    - `src/routes/+layout.svelte`: Main layout headers/footers.
    - `static/`: Favicons, manifest.json.
    - `src/lib/`: Components containing textual references.
    - `i18n`: Localization files (en.json, etc.).

### Visual Identity System (Design Tokens)
- **File**: `src/app.css` / `tailwind.config.js`.
- **Palette**: Define generic semantic names (`--color-brand-primary`, `--color-surface-base`) to decouple from stock colors.
- **Typography**: Switch to a premium sans-serif (e.g., Inter, Plus Jakarta Sans) via Google Fonts or generic system stack improvements.

## 2. Backend Specifications (FastAPI)
### Static Asset Serving
- Ensure `backend/static` does not serve old branded compilation during dev.
- Update `backend/main.py` (or equivalent entry point) if it defines custom titles for Swagger UI / Redoc.

### Verification Scripts
- **Script**: `scripts/verify_branding.sh`
- **Logic**:
    - recursive grep for "Open WebUI" in `src/`.
    - Exclude: `LICENSE`, `planning/`, `README.md` (where attribution might be legally required or historical).
    - Fail build if match found in UI code.

## 3. Agentic Workflow Specs
- **Task**: Every implementation step must start with `task_boundary`.
- **Artifacts**: New features require updating `planning/` artifacts first.
