# Initialization: Custom Core Integration

## 1. Project Identity & Vision
**Objective**: Transform the Open WebUI fork into a distinct, premium, and agentic-focused platform.
**Current State**: Fork of Open WebUI (BSD 3-Clause).
**Target State**: Independent brand identity, compliant with Open WebUI attribution requirements but visually distinct.

## 2. Compliance Strategy
### Backend (BSD 3-Clause)
- **Requirement**: Retain original copyright notices.
- **Action**: Ensure `LICENSE` file remains. Verify backend source code headers if present.
- **Verification**: Agentic check of backend files for copyright retention.

### Frontend (Branding Restriction)
- **Requirement**: COMPLETE removal of "Open WebUI" branding (name, logo, visual identifiers).
- **Action**:
    - Replace all logos (favicon, banners, UI elements).
    - Rename application title and meta tags.
    - Modify distinct visual elements (color palette, typography) to avoid resemblance.
- **Verification**: visual and grep search for "Open WebUI" in `src/` and `static/`.

## 3. Core Architecture
- **Frontend**: SvelteKit + TailwindCSS (Custom Design System).
- **Backend**: Python/FastAPI (Existing Logic + Custom Extensions).
- **Data**: SQLAlchemy / Peewee (Preserve existing schema compatibility).

## 4. Agentic Workflow
All changes must flow through the planning directory:
1.  Update `planning/` context.
2.  Review against `planning/base.md`.
3.  Implement changes.
4.  Verify compliance.
