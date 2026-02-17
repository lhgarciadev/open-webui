# Agentic Prompts for Execution

These prompts are designed to be used by an autonomous agent to execute the [Implementation Plan](implementation_plan.md).

## Phase 1: The Clean Slate (Compliance & Formatting)

### Prompt 1.1: Creation (Remove Branding)

```text
**Task**: Execute Phase 1 of the implementation plan: "The Clean Slate".
**Objective**: Remove "Open WebUI" branding to comply with strict license requirements.

**Steps**:
0.  **Legal Decision Gate**: Confirm Path A in planning/legal_compliance.md. If Path B applies, stop and adapt Phase 1 to retain visible branding.
1.  **Create Identity Constant**: Create `src/lib/constants/identity.ts` exporting `APP_NAME = "Agentic WebUI"` (or placeholder) and branding colors.
2.  **Create Verification Script**: Create `scripts/verify_compliance.sh`. Content: valid bash script that recursively greps `src/` for "Open WebUI" (case-insensitive) and fails if found. Make it executable.
3.  **Refactor Frontend**:
    - Iterate through `src/app.html`, `src/routes/+layout.svelte`, and `src/lib/components/**/*.svelte`.
    - Replace hardcoded occurrences of "Open WebUI" with the imported `APP_NAME` from your new constant file.
    - BE CAREFUL: Do not break variable names or imports, only display strings.

**Context**:
- Plan: `planning/implementation_plan.md`
- License: `LICENSE` (Clause 4 requires this).
```

### Prompt 1.2: Validation (Verify Compliance)

```text
**Task**: Validate Phase 1 changes.
**Objective**: Ensure no branding remains and the app still builds.

**Steps**:
1.  **Run Compliance Script**: Execute `./scripts/verify_compliance.sh`.
    - If it fails, fix the remaining instances of "Open WebUI" it finds.
    - Repeat until it passes (exit code 0).
2.  **Test Build**: Run `npm run build`.
    - Fix any syntax errors caused by the refactor.
3.  **Report**: Output the specific files that were modified and the result of the compliance script.
```

---

## Phase 2: Identity Injection (The Soul)

### Prompt 2.1: Creation (Refine Aesthetics)

```text
**Task**: Execute Phase 2: "Identity Injection".
**Objective**: Apply a "Premium Agentic" design system.

**Steps**:
1.  **Update CSS Variables**: Edit `src/app.css` (or main tailwind file).
    - Replace default colors with a "Deep Space" palette (Obsidian #0a0a0a, Electric Blue accent #3b82f6, etc.).
    - Update font-family to use a system stack or a premium font if available.
2.  **Update Config**: check `tailwind.config.js` to ensure it uses the new CSS variables.
3.  **Replace Assets**:
    - Generate a new simple geometric favicon (SVG/PNG).
    - Overwrite `static/favicon.png` and update `static/manifest.json` short_name/name.

**Style Guide**: Minimalist, Dark Mode default, High Contrast.
```

### Prompt 2.2: Validation (Visual Check)

```text
**Task**: Validate Phase 2 Aesthetics.
**Objective**: Confirm the new identity is active.

**Steps**:
1.  **Check Manifest**: Read `static/manifest.json`. Confirm "Open WebUI" is NOT the name.
2.  **Check Styles**: Read `src/app.css`. Confirm variables are updated.
3.  **Browser Check (Optional)**: If available, take a screenshot of the login page to confirm new colors and title.
```

---

## Phase 3: Core Integration

### Prompt 3.1: Creation (Backend Config)

```text
**Task**: Execute Phase 3: "Core Integration".
**Objective**: Ensure backend doesn't serve old branding.

**Steps**:
1.  **Analyze Backend**: Read `backend/config.py` and `backend/main.py`.
2.  **Update Settings**: Look for `WEBUI_NAME` or similar environment variables/constants. Change default from "Open WebUI" to "Agentic WebUI".
3.  **Swagger UI**: Ensure API docs title is updated in `FastAPI()` initiation.
```

### Prompt 3.2: Validation (System Health)

```text
**Task**: Validate System Integrity.
**Objective**: Final check before release.

**Steps**:
1.  **Startup Check**: Run `./start.sh` (background) or check `start.sh` logic.
2.  **Endpoint Check**: Curl the main page `localhost:8080`.
    - Grep response for `<title>`. It should NOT be "Open WebUI".
3.  **Cleanup**: Ensure no broken git locks or temporary files remain.
```
