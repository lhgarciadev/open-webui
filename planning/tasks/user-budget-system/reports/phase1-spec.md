# Stage Report: SPEC_CREATION

Date: 2026-03-02
Task: user-budget-system
Status: COMPLETED

## Completed

- [x] Defined functional requirements (FR1-FR13): admin budget assignment, balance debit after LLM response, pre-flight blocking at zero balance, audit trail, user self-service read, frontend indicators
- [x] Defined non-functional requirements (NFR1-NFR7): single-transaction atomicity, <5ms pre-flight latency, zero latency for unbudgeted users, decimal precision, RBAC enforcement
- [x] Designed database schema: two new tables (`user_budget`, `spending_transaction`) with indexes
- [x] Specified all API contracts: 5 endpoints with full request/response shapes
- [x] Specified execution flow: pre-flight check (blocking) + post-completion debit (non-raising)
- [x] Specified utility function signatures for `utils/budget.py`
- [x] Specified SQLAlchemy ORM pattern for `models/budgets.py`
- [x] Designed frontend changes: store, API client, BalanceIndicator, BudgetManager admin component
- [x] Defined testing strategy: unit, integration, and E2E test scenarios
- [x] Documented risks and mitigations (6 risks identified)

## Decisions Made

| Decision | Rationale | Impact |
| -------- | --------- | ------ |
| `NUMERIC(12,6)` for monetary columns | Avoids floating-point drift; supports balances up to $999,999 with micro-dollar precision | Alembic migration must use `sa.Numeric(12, 6)`; Python intermediates may use `float` |
| Budget is opt-in per user (no row = unrestricted) | Zero additional latency for users without a budget; avoids global enforcement overhead | Short-circuit path in `check_user_budget` when no row exists |
| No FK constraint on `user_budget.user_id` | Avoids cascade complexity; application layer validates user existence before insert | Router must call `Users.get_user_by_id` before upsert |
| Post-completion debit is non-raising | Debit failure must never surface as an error to the user; LLM response is already delivered | All exceptions in `debit_user_budget` are caught and logged only |
| Balance delta on budget update (not forced reset) | Admin top-ups should add to existing balance by default; full reset is opt-in via `reset_balance=true` | `upsert_budget` must compute `current_balance += (new_initial - old_initial)` when `reset_balance=False` |
| `hard_limit=True` default | Current enforcement model is always hard-block at zero; soft-limit mode is reserved for future use | `check_user_budget` only blocks when `hard_limit=True` |
| Debit called inside streaming generator's `finally` block | Ensures debit fires after full stream is consumed without blocking the response to the user | Requires accumulating token counts across streaming chunks |
| ORM pattern follows `models/pricing.py` and `models/users.py` exactly | Consistency with existing codebase conventions | `BudgetsTable` class with `get_db_context(db)`, `int(time.time())` timestamps, Pydantic `ConfigDict(from_attributes=True)` |
| Alembic migration uses `get_existing_tables()` guard | Makes upgrade idempotent; safe to run twice (matches every other migration in the project) | `down_revision` must point to `9a2b3c4d5e6f` (`add_model_pricing`) |

## Learnings

- The system already has token tracking (`chat_message.usage`) and model pricing (`model_pricing` table) — the budget feature composes these rather than reimplementing them
- OpenAI streaming responses require `stream_options: {"include_usage": true}` to get token counts in the final chunk; without this flag, debit must be skipped and a warning logged
- Race conditions on near-zero balances are accepted as a design trade-off: atomic DB `UPDATE ... SET current_balance = current_balance - cost` can go slightly negative, which is tolerable given the pre-flight check semantics
- Frontend budget state is loaded once on app mount via `GET /api/v1/users/me/budget`; 404 means no budget (store stays `null`, no UI rendered)

## Artifacts Created

- `planning/tasks/user-budget-system/spec.md` — full feature specification (458 lines)
- `planning/tasks/user-budget-system/reports/phase1-spec.md` — this report

## Files to Be Created (Implementation Phase)

### Backend (new)
- `backend/open_webui/models/budgets.py`
- `backend/open_webui/routers/budgets.py`
- `backend/open_webui/utils/budget.py`
- `backend/open_webui/migrations/versions/<rev>_add_budget_tables.py`
- `backend/tests/utils/test_budget.py`
- `backend/tests/models/test_budgets.py`
- `backend/tests/routers/test_budgets.py`

### Frontend (new)
- `src/lib/apis/budgets.ts`
- `src/lib/components/budget/BalanceIndicator.svelte`
- `src/lib/components/admin/Users/BudgetManager.svelte`

### Backend (modified)
- `backend/open_webui/main.py` — register budgets router
- `backend/open_webui/routers/openai.py` — pre-flight check + post-completion debit
- `backend/open_webui/routers/ollama.py` — pre-flight check + post-completion debit

### Frontend (modified)
- `src/lib/stores/index.ts` — add `userBudget` store
- `src/lib/components/chat/Navbar.svelte` — mount BalanceIndicator
- `src/lib/components/chat/MessageInput.svelte` — budget exhausted gate
- `src/lib/components/admin/Users.svelte` — add Budgets tab

## Context for Next Stage (Architecture Review)

Key questions the architecture reviewer should verify:

1. **Migration chain**: Confirm that `9a2b3c4d5e6f` is indeed the current head migration in `backend/open_webui/migrations/versions/`. If not, update `down_revision` before implementation.
2. **Streaming debit placement**: Verify that both `openai.py` and `ollama.py` streaming generators have a `finally` block where the debit hook can be inserted without holding the response open.
3. **`get_db_context` availability**: Confirm this context manager is importable from the same location used in `models/pricing.py` — implementation must import from the identical source.
4. **`model_pricing` lookup interface**: Confirm the exact method name and signature on the existing `ModelPricingTable` that returns pricing for a given `model_id`, so `calculate_message_cost` can call it correctly.
5. **Router prefix registration in `main.py`**: Confirm the existing prefix patterns for `/api/v1/users` and `/api/v1/admin` so the budgets router is mounted without conflicts.
6. **Frontend root layout file**: Identify the correct SvelteKit layout file (likely `src/routes/(app)/+layout.svelte`) where the `getUserBudget` call should be placed on app mount.
7. **`MessageInput.svelte` submit path**: Confirm the exact condition and variable name used to disable the send button, so the budget gate integrates cleanly without duplicating logic.

## Issues Encountered

- None. Spec was created cleanly against the existing codebase subsystems.

## Handoff to Architecture Review

### What Was Done

A complete feature specification for a per-user USD budget/credit system was written. The spec covers database schema, API contracts, execution flow, ORM patterns, utility function signatures, frontend state management, component design, testing strategy, and risk mitigations.

### What You Need to Know

- The feature is entirely additive — no existing tables are altered, only new ones added plus hooks inserted into `openai.py` and `ollama.py`.
- The opt-in design (no row = unrestricted) means zero risk to existing users during rollout.
- Monetary precision uses `NUMERIC(12,6)` throughout — this must be enforced in SQLAlchemy column definitions, not just Python-side.
- The debit function must never raise; it wraps everything in try/except and logs errors.

### Files to Review

- `planning/tasks/user-budget-system/spec.md` — the complete specification
- `backend/open_webui/models/pricing.py` — ORM pattern to replicate exactly
- `backend/open_webui/migrations/versions/` — to confirm current head migration revision
- `backend/open_webui/routers/openai.py` — to locate streaming generator structure
- `backend/open_webui/routers/ollama.py` — to locate streaming generator structure
- `backend/open_webui/main.py` — to verify router prefix conventions

### Decisions Already Made

All decisions in the table above are final and should not be re-debated during architecture review. The reviewer's job is to validate feasibility and identify any integration blockers, not to redesign the approach.
