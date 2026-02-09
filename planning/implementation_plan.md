# Agentic Implementation Plan: Genesis

## User Review Required
> [!IMPORTANT]
> **Branding Removal**: This plan involves aggressive removal of "Open WebUI" branding from the frontend. This is IRREVERSIBLE for the identity of the fork. Ensure you have backups if you wish to revert to the stock look.

> [!WARNING]
> **Updates**: Merging upstream changes from `open-webui/open-webui` will be difficult after these changes. We are effectively detaching the frontend identity.

## Proposed Changes

### Upstream Sync and Compliance Gates
**Objective**: Define the required workflow for syncing upstream changes and enforcing compliance.

- **Playbook**: Follow [planning/upstream_sync_playbook.md](planning/upstream_sync_playbook.md) for all upstream merges.
- **Checklist**: Execute [planning/compliance_checklist.md](planning/compliance_checklist.md) before merging any branch to `main`.

### Legal Decision Gate (Required)
**Objective**: Confirm the license path before any branding changes.

- Record Path A or Path B as defined in [planning/legal_compliance.md](planning/legal_compliance.md).
- If Path B applies, do not remove visible branding; adapt Phase 1 accordingly.

### Phase 1: The Clean Slate (Compliance & Formatting)
**Objective**: Eradicate "Open WebUI" branding from the frontend to comply with Clause 4/5 and prepare for new identity.

#### [NEW] [scripts/verify_compliance.sh](scripts/verify_compliance.sh)
- A script to recursively search for forbidden strings in the build output and source code (excluding `LICENSE` and `planning/`).

#### [MODIFY] [Frontend Source Code](src)
- **Files**: `src/app.html`, `src/routes/+layout.svelte`, `src/lib/components/**/*.svelte`
- **Action**: Replace hardcoded "Open WebUI" strings with dynamic import from a new constant file or i18n keys.

#### [NEW] [src/lib/constants/identity.ts](src/lib/constants/identity.ts)
- Define `APP_NAME`, `BRAND_COLOR`, etc.

### Phase 2: Identity Injection (The Soul)
**Objective**: Inject the new "Agentic" aesthetic and brand.

#### [MODIFY] [Design System](src/app.css)
- **Action**: Overhaul CSS variables to use a premium, high-contrast "Agentic" palette (Deep blues/purples/obsidian or requested style).

#### [MODIFY] [Assets](static)
- **Files**: `favicon.png`, `manifest.json`.
- **Action**: Generate and replace default assets.

### Phase 3: Core Integration
**Objective**: Ensure the backend remains compliant but works with the new frontend.

#### [MODIFY] [Backend Config](backend/config.py)
- **Action**: Check for default branding strings sent via API and make them configurable.

## Verification Plan

### Automated Tests
- **Compliance Check**:
    - Use the required steps in [planning/compliance_checklist.md](planning/compliance_checklist.md).

- **Frontend Build**:
    ```bash
    npm install
    npm run build
    ```
    *Expectation*: Build completes without errors.

### Manual Verification
1.  **Launch the App**: Run `npm run dev` and `bash start.sh`.
2.  **Visual Inspection**:
    - Check Tab Title.
    - Check Loading Screen.
    - Check Sidebar / Header.
    - **Pass Condition**: No "Open WebUI" logo or text visible.
