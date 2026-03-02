# Stage Report: IMPLEMENTATION

Date: 2026-03-02
Task: user-budget-system
Status: COMPLETED

## Completed

- [x] Created SQLAlchemy ORM models: `UserBudget`, `SpendingTransaction`, plus Pydantic schemas and `BudgetsTable` operations
- [x] Created budget utility functions: `calculate_message_cost`, `check_user_budget`, `debit_user_budget`
- [x] Created FastAPI router with 5 endpoints (1 user-facing, 4 admin)
- [x] Created Alembic migration `d4e5f6a7b8c9` for `user_budget` and `spending_transaction` tables
- [x] Created TypeScript API client at `src/lib/apis/budgets/index.ts` (5 functions, 7 interfaces)
- [x] Created `BalanceIndicator.svelte` — reactive pill showing balance with warning/exhausted states
- [x] Created `BudgetManager.svelte` — full admin CRUD table with inline edit and spending history modal
- [x] Added `userBudget` writable store to `src/lib/stores/index.ts`
- [x] Integrated budget load on app mount in `src/routes/(app)/+layout.svelte`
- [x] Mounted `BalanceIndicator` in `src/lib/components/chat/Navbar.svelte`
- [x] Added budget-exhausted gate to `src/lib/components/chat/MessageInput.svelte` (disables send button + renders warning)
- [x] Wired `check_user_budget` pre-flight check in `backend/open_webui/routers/openai.py` (line 946)
- [x] Wired `debit_user_budget` post-completion debit in `backend/open_webui/routers/openai.py` (lines 1135, 1178)
- [x] Wired `check_user_budget` pre-flight check in `backend/open_webui/routers/ollama.py` (lines 1303, 1514)
- [x] Registered budgets router in `backend/open_webui/main.py` at prefix `/api/v1/budgets`
- [x] Added `Budgets` tab to `src/lib/components/admin/Users.svelte` (tab id: `budgets`, route: `/admin/users/budgets`)
- [x] Created unit tests covering 12 scenarios across all three utility functions
- [x] Tests: 12/12 passing

## Files Created

| File | Type | Description |
| ---- | ---- | ----------- |
| `backend/open_webui/models/budgets.py` | New | ORM models, Pydantic schemas, `BudgetsTable` class (8 methods) |
| `backend/open_webui/utils/budget.py` | New | `calculate_message_cost`, `check_user_budget`, `debit_user_budget` |
| `backend/open_webui/routers/budgets.py` | New | FastAPI router — 5 endpoints |
| `backend/open_webui/migrations/versions/d4e5f6a7b8c9_add_budget_tables.py` | New | Alembic migration — creates `user_budget` and `spending_transaction` |
| `backend/open_webui/test/utils/test_budget.py` | New | 12 unit tests (mocked DB layer) |
| `src/lib/apis/budgets/index.ts` | New | TypeScript API client with typed interfaces |
| `src/lib/components/budget/BalanceIndicator.svelte` | New | User-facing balance pill component |
| `src/lib/components/admin/Users/BudgetManager.svelte` | New | Admin budget management table + spending modal |

## Files Modified

| File | Change |
| ---- | ------ |
| `backend/open_webui/main.py` | Imported `budgets` router; registered at `/api/v1/budgets` (line 73, 1487) |
| `backend/open_webui/routers/openai.py` | Added `check_user_budget` pre-flight (line 946); added `debit_user_budget` post-completion in streaming path (lines 1135, 1178) |
| `backend/open_webui/routers/ollama.py` | Added `check_user_budget` pre-flight at two generate endpoints (lines 1303, 1514) |
| `src/lib/stores/index.ts` | Added `userBudget: Writable<UserBudget | null>` store (line 83) |
| `src/routes/(app)/+layout.svelte` | Added `getUserBudget` call on mount; sets or clears `userBudget` store (lines 148-151) |
| `src/lib/components/chat/Navbar.svelte` | Imported and mounted `<BalanceIndicator />` in navbar (lines 36, 223) |
| `src/lib/components/chat/MessageInput.svelte` | Added budget guard: disables send button and shows warning banner when `$userBudget.current_balance <= 0` (lines 1143, 1928, 1933) |
| `src/lib/components/admin/Users.svelte` | Added `BudgetManager` import; added `budgets` tab with route `/admin/users/budgets` (lines 11, 19, 115, 149) |

## Decisions Made

| Decision | Rationale | Impact |
| -------- | --------- | ------ |
| `debit_user_budget` placed in `finally` block of streaming generator | Ensures debit fires after full stream is consumed without blocking the user response | Token counts must be accumulated across streaming chunks before the debit call |
| Ollama debit wiring deferred (pre-flight only) | Ollama streaming does not emit per-chunk usage totals in a consistent format; debit hook added only to OpenAI path where `include_usage` flag is supported | Ollama users are pre-flight blocked but not debited; tracked as known gap |
| `src/lib/apis/budgets/index.ts` uses directory convention | Consistent with other API modules in the project (e.g., `src/lib/apis/index.ts`) | Import paths use `$lib/apis/budgets` |
| `BudgetManager` uses inline row editing (not a modal) for the edit form | Reduces modal nesting depth; inline editing matches pattern used elsewhere in admin UI | Spending history still uses a modal (different UX need: full table view) |
| `BalanceIndicator` reads from `$userBudget` store, not a live API call | Avoids per-render HTTP round trips; store is refreshed on mount and after budget-exhausted event | Balance displayed may lag by one page load; acceptable for current requirements |
| Migration `down_revision = "9a2b3c4d5e6f"` | Confirmed as current head (the `add_model_pricing` migration) before implementation | Migration chain is contiguous; no orphaned revisions |
| Test file at `backend/open_webui/test/utils/test_budget.py` | Matches existing test directory convention in the project | Run with `cd backend && pytest open_webui/test/utils/test_budget.py` |

## Test Results

**12/12 tests passing** in `backend/open_webui/test/utils/test_budget.py`.

| Test Class | Tests | Coverage |
| ---------- | ----- | -------- |
| `TestCalculateMessageCost` | 4 | Known model pricing math; unknown model returns zeros; zero tokens; large token counts |
| `TestCheckUserBudget` | 5 | Raises 402 at zero balance with hard_limit; raises 402 at negative balance; no-ops with no budget row; no-ops when hard_limit=False; no-ops when balance positive |
| `TestDebitUserBudget` | 3 | Debits and returns new balance; returns None when no budget row; catches exceptions and returns None without re-raising |

All tests use `unittest.mock.patch` to mock `Budgets` table and `pricing_table` — no live DB required.

## Integration Points

### Backend Pre-flight (HTTP 402 gate)

- `backend/open_webui/routers/openai.py` line 946: `check_user_budget(user.id)` called before any token processing begins
- `backend/open_webui/routers/ollama.py` line 1303: `check_user_budget(user.id)` at `/ollama/generate`
- `backend/open_webui/routers/ollama.py` line 1514: `check_user_budget(user.id)` at `/ollama/chat`
- Raises `HTTPException(402, "Budget exhausted")` only when `hard_limit=True` and `current_balance <= 0`
- No-ops transparently for users with no budget row (zero overhead path)

### Backend Post-completion Debit

- `backend/open_webui/routers/openai.py` lines 1135, 1178: `debit_user_budget(...)` called inside streaming generator's `finally` block after token counts are accumulated
- Atomic DB operation: balance debit + transaction insert in a single `get_db_context` scope (`debit_and_record`)
- Never raises to caller — all exceptions caught and logged

### Router Registration

- `backend/open_webui/main.py` line 1487: `app.include_router(budgets.router, prefix="/api/v1/budgets", tags=["budgets"])`
- Resulting endpoint paths: `/api/v1/budgets/me/budget`, `/api/v1/budgets/admin/budgets`, `/api/v1/budgets/{user_id}/budget`, `/api/v1/budgets/{user_id}/spending`

### Frontend Store Initialization

- `src/routes/(app)/+layout.svelte`: `getUserBudget()` called on `onMount`; result written to `userBudget` store; 404 response sets store to `null` (no budget assigned)

### Frontend UI Gates

- `src/lib/components/chat/Navbar.svelte`: `<BalanceIndicator />` renders only when `$userBudget` is non-null; shows colored pill with three states (normal / warning at <=20% / exhausted at <=0)
- `src/lib/components/chat/MessageInput.svelte`: Send button disabled and warning banner shown when `$userBudget !== null && $userBudget.current_balance <= 0`

### Admin Panel

- `src/lib/components/admin/Users.svelte`: New `budgets` tab at `/admin/users/budgets` mounts `<BudgetManager />`
- `BudgetManager` renders paginated table of all budgets with inline edit, create-new form, and spending history modal

## Artifacts Created

- `/Users/juan.quiroga/Desktop/Estudio/MAIN/GIT/open-webui/backend/open_webui/models/budgets.py`
- `/Users/juan.quiroga/Desktop/Estudio/MAIN/GIT/open-webui/backend/open_webui/utils/budget.py`
- `/Users/juan.quiroga/Desktop/Estudio/MAIN/GIT/open-webui/backend/open_webui/routers/budgets.py`
- `/Users/juan.quiroga/Desktop/Estudio/MAIN/GIT/open-webui/backend/open_webui/migrations/versions/d4e5f6a7b8c9_add_budget_tables.py`
- `/Users/juan.quiroga/Desktop/Estudio/MAIN/GIT/open-webui/backend/open_webui/test/utils/test_budget.py`
- `/Users/juan.quiroga/Desktop/Estudio/MAIN/GIT/open-webui/src/lib/apis/budgets/index.ts`
- `/Users/juan.quiroga/Desktop/Estudio/MAIN/GIT/open-webui/src/lib/components/budget/BalanceIndicator.svelte`
- `/Users/juan.quiroga/Desktop/Estudio/MAIN/GIT/open-webui/src/lib/components/admin/Users/BudgetManager.svelte`

## Known Gaps / Deferred Items

- **Ollama post-completion debit**: Pre-flight check is wired; debit hook is not. Ollama streaming response format does not include per-chunk usage totals consistently. Debit should be added once Ollama usage reporting is confirmed or a token-counting shim is added.
- **Frontend balance refresh after debit**: The `userBudget` store is not updated reactively after each message. Balance shown in `BalanceIndicator` updates only on next page load or manual refresh. A WebSocket event or polling interval could close this gap in a future iteration.
- **i18n keys**: Budget-related strings (`Budget exhausted`, `Budget updated`, `Budget Management`, etc.) have been added to `en-US` and `es-ES` translation files. Other locales are not yet updated.

## Context for Next Stage (QA Verification)

The QA agent should verify:

1. **Pre-flight blocking**: Send a chat message as a user whose budget `current_balance = 0` and `hard_limit = True` — expect HTTP 402 back to the client.
2. **Transparent passthrough**: Send a chat message as a user with no budget row — expect normal response, no errors, no debit record created.
3. **Post-completion debit**: After a successful OpenAI-path chat completion, confirm a row is created in `spending_transaction` and `user_budget.current_balance` is decremented.
4. **Atomic debit**: Verify that a simulated DB failure during debit does not surface as a user-visible error (response already delivered; only a log entry).
5. **Admin CRUD**: Via `GET /api/v1/budgets/admin/budgets`, `POST /api/v1/budgets/{user_id}/budget`, confirm create/update/reset_balance flows work correctly.
6. **Balance delta on update**: When updating `initial_budget` from $5.00 to $8.00 without `reset_balance=True`, `current_balance` should increase by $3.00, not reset to $8.00.
7. **BalanceIndicator states**: Confirm the pill renders correctly at >20% (gray), <=20% (amber), and <=0 (red/exhausted).
8. **Send button gate**: Confirm the send button is disabled in `MessageInput` when `current_balance <= 0`.
9. **Migration idempotency**: Run `alembic upgrade head` twice — second run should be a no-op (tables already exist).
10. **RBAC enforcement**: Confirm that a non-admin user cannot call `/api/v1/budgets/admin/budgets` or `POST /api/v1/budgets/{user_id}/budget` (expect HTTP 403).

## Issues Encountered

- Migration `down_revision` required confirmation of the existing head revision before setting. Confirmed as `9a2b3c4d5e6f` (`add_model_pricing`) — matches spec assumption.
- Ollama debit could not be completed in this stage due to inconsistent usage reporting in Ollama streaming chunks. Pre-flight check is in place as a partial mitigation.

## Handoff to QA

### What Was Done

Full implementation of the per-user USD budget system. All backend models, utilities, router, and migration are in place. Frontend store, API client, admin panel, navbar indicator, and message input gate are all wired. Unit tests are 12/12 passing.

### What You Need to Know

- The debit path is OpenAI-only for now. Ollama has pre-flight blocking but no post-completion debit.
- Budget is opt-in: users with no `user_budget` row are completely unaffected by any of the new code.
- The atomic `debit_and_record` method in `BudgetsTable` is the single write point — it can go slightly negative under high concurrency (race window between pre-flight and debit), which is an accepted design trade-off from the spec.
- Test runner: `cd backend && pytest open_webui/test/utils/test_budget.py -v`

### Files to Review

- `/Users/juan.quiroga/Desktop/Estudio/MAIN/GIT/open-webui/backend/open_webui/utils/budget.py` — core logic
- `/Users/juan.quiroga/Desktop/Estudio/MAIN/GIT/open-webui/backend/open_webui/models/budgets.py` — DB layer
- `/Users/juan.quiroga/Desktop/Estudio/MAIN/GIT/open-webui/backend/open_webui/routers/budgets.py` — API surface
- `/Users/juan.quiroga/Desktop/Estudio/MAIN/GIT/open-webui/backend/open_webui/routers/openai.py` — integration hooks (lines 59, 946, 1135, 1178)
- `/Users/juan.quiroga/Desktop/Estudio/MAIN/GIT/open-webui/backend/open_webui/routers/ollama.py` — pre-flight hooks (lines 61, 1303, 1514)
- `/Users/juan.quiroga/Desktop/Estudio/MAIN/GIT/open-webui/src/lib/apis/budgets/index.ts` — frontend API client
- `/Users/juan.quiroga/Desktop/Estudio/MAIN/GIT/open-webui/src/lib/components/budget/BalanceIndicator.svelte` — UI indicator
- `/Users/juan.quiroga/Desktop/Estudio/MAIN/GIT/open-webui/planning/tasks/user-budget-system/spec.md` — original acceptance criteria

### Decisions Already Made

All decisions from the spec phase (NUMERIC(12,6), opt-in design, no FK on user_id, non-raising debit, balance delta on update, hard_limit default, debit in finally block) are final and implemented as specified. Do not re-debate these during QA.
