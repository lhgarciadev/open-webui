# Upstream Sync Playbook (Fork Maintenance)

## Goal
Safely integrate changes from `open-webui/open-webui` into this fork while preserving custom identity and compliance.

## Policy
- Use merge-based integration, not rebase.
- Always sync in a dedicated branch.
- Never push to `main` directly.

## Step 0: One-Time Setup
1. Add upstream remote (if missing):
   ```bash
   git remote add upstream https://github.com/open-webui/open-webui.git
   ```
2. Verify remotes:
   ```bash
   git remote -v
   ```

## Step 1: Create Sync Branch
1. Fetch upstream:
   ```bash
   git fetch upstream
   ```
2. Update local `main`:
   ```bash
   git checkout main
   git pull origin main
   ```
3. Create a sync branch:
   ```bash
   git checkout -b sync/upstream-YYYYMMDD
   ```

## Step 2: Merge Upstream
1. Merge upstream main:
   ```bash
   git merge upstream/main
   ```
2. If conflicts occur:
   - Resolve in favor of custom identity and compliance.
   - Keep branding constants and design tokens intact.
   - Prefer upstream logic changes in non-UI backend code.

## Step 3: Conflict Resolution Rules (Priority Order)
1. Brand identity and compliance requirements.
2. Frontend correctness and build stability.
3. Backend compatibility and API stability.
4. Optional UI refinements or new upstream UX.

## Step 4: Run Compliance Checklist
- Follow the required steps in [planning/compliance_checklist.md](planning/compliance_checklist.md).

## Step 5: Final Review
1. Review diff summary:
   ```bash
   git status
   git diff --stat
   ```
2. Ensure no branding regressions.
3. Ensure no unexpected asset reintroductions.

## Step 6: Merge to Main
1. Merge the sync branch into `main` via PR or local merge.
2. Tag the sync version (optional):
   ```bash
   git tag sync-YYYYMMDD
   git push origin sync-YYYYMMDD
   ```

## Emergency Hot Sync (Critical CVE)
1. Create `sync/hotfix-YYYYMMDD`.
2. Cherry-pick only required commits from upstream.
3. Run the full compliance checklist.

## Notes
- Update cadence: every 2-4 weeks.
- Avoid rebase if the fork is shared externally.
- If upstream introduces large UI changes, expect a higher conflict rate.
