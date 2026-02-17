# Compliance Checklist (Branding + Quality Gate)

## Scope

This checklist is mandatory before merging any branch to `main`.

## Preconditions

- Working branch is clean and up to date.
- You are on the integration branch (e.g., `sync/upstream-YYYYMMDD`) or a feature branch.
- Legal decision path (A or B) is recorded per planning/legal_compliance.md.

## Step 1: Branding Compliance (Blocking)

1. Run branding verification script:
   ```bash
   chmod +x scripts/verify_compliance.sh
   ./scripts/verify_compliance.sh
   ```
2. Expected result: exit code 0 and no matches in UI source.
3. If it fails:
   - Inspect the output paths.
   - Remove or replace any "Open WebUI" strings in the UI layer.
   - Re-run until clean.

## Step 2: Frontend Build (Blocking)

1. Install dependencies (if not already installed):
   ```bash
   npm install
   ```
2. Build:
   ```bash
   npm run build
   ```
3. Expected result: build completes without errors.
4. If it fails:
   - Fix TypeScript/Svelte errors.
   - Re-run build until clean.

## Step 3: Backend Sanity (Blocking)

1. Ensure the backend starts:
   ```bash
   bash start.sh
   ```
2. Confirm server responds on expected port.
3. If it fails:
   - Check logs.
   - Fix configuration or dependency issues.

## Step 4: UI Smoke Tests (Blocking)

1. Login (or create admin if env vars are set).
2. Create a new chat and send a simple prompt.
3. Confirm the response streams and persists.
4. Check the page title and visible UI text for any branding leakage.

## Step 5: Record Results (Blocking)

- Record test results in the PR or change log.
- If any step fails, do not merge.

## Notes

- Do not skip this checklist for hotfixes. If time constrained, run a minimal subset and document the risk.
