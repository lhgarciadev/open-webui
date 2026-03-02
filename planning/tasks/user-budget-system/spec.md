# Specification: Per-User Budget/Credit System

## 1. Overview

This feature adds a per-user USD budget and credit tracking system to Cognitia. Administrators can assign a USD spending cap to any user. After each LLM response, the system calculates the cost (using the existing `model_pricing` table and token counts from `chat_message.usage`) and debits it from the user's balance. When the balance reaches zero, the user is blocked from sending further messages until an admin tops up their budget.

The feature builds directly on three already-existing subsystems:
- Token tracking: `chat_message.usage` JSON column (`input_tokens`, `output_tokens`)
- Model pricing: `model_pricing` table with `input_usd_per_million` / `output_usd_per_million`
- Auth guards: `get_admin_user` / `get_verified_user` dependency functions in `utils/auth.py`

---

## 2. Requirements

### 2.1 Functional Requirements

- FR1: An admin can assign a USD budget (e.g., `$5.00`) to any user by `user_id`.
- FR2: An admin can top up (increase) an existing balance, or replace it entirely by setting a new `initial_budget`.
- FR3: After every successful LLM assistant response, the system computes the message cost and deducts it from the user's `current_balance`.
- FR4: Before forwarding an LLM request, the system checks whether the requesting user has an active budget with `current_balance > 0`. If the balance is zero or negative, the request is rejected with HTTP 402 Payment Required.
- FR5: Each debit is recorded in the `spending_transaction` table for auditing.
- FR6: Users without a `user_budget` row are unrestricted (budget system is opt-in per user).
- FR7: An admin can view spending history for a single user (`GET /api/v1/users/{user_id}/spending`).
- FR8: An admin can list budget status for all users (`GET /api/v1/admin/budgets`).
- FR9: The authenticated user can fetch their own budget summary (`GET /api/v1/users/me/budget`).
- FR10: The chat UI shows the user's remaining balance as a small indicator when they have a budget assigned.
- FR11: The chat UI shows a yellow warning when the remaining balance is below 20% of the initial budget.
- FR12: The chat UI shows a red "Budget exhausted" banner and disables the send button when `current_balance <= 0`.
- FR13: The admin panel has a "Budgets" tab inside the Users admin section for managing per-user budgets.

### 2.2 Non-Functional Requirements

- NFR1: Cost debit and transaction insert must occur within a single database transaction to prevent phantom debits on rollback.
- NFR2: The pre-flight budget check must add no more than 5 ms latency to request processing (single indexed DB lookup).
- NFR3: Users with no `user_budget` row must experience zero additional latency (short-circuit path).
- NFR4: `current_balance` is stored as `Numeric(12,6)` (cents-level precision) to avoid floating-point drift.
- NFR5: The admin endpoints must require `role == "admin"` (via existing `get_admin_user` dependency).
- NFR6: The user's own budget endpoint must work with `get_verified_user` and must only return data for `user.id`.
- NFR7: All monetary values exchanged via the API are represented in USD as a float rounded to 6 decimal places.

---

## 3. Technical Design

### 3.1 Architecture Changes

#### 3.1.1 New Python Files

| File | Purpose |
|------|---------|
| `backend/open_webui/models/budgets.py` | SQLAlchemy ORM models for `user_budget` and `spending_transaction`, Pydantic response models, and the `BudgetsTable` data-access class |
| `backend/open_webui/routers/budgets.py` | FastAPI router with all budget API endpoints |
| `backend/open_webui/utils/budget.py` | Pure utility functions: cost calculation, balance check, debit helper |
| `backend/open_webui/migrations/versions/<rev>_add_budget_tables.py` | Alembic migration |
| `src/lib/apis/budgets.ts` | Typed SvelteKit API client for budget endpoints |
| `src/lib/components/budget/BalanceIndicator.svelte` | Small chat navbar balance badge |
| `src/lib/components/admin/Users/BudgetManager.svelte` | Admin panel budget management tab component |

#### 3.1.2 Modified Files

| File | Change |
|------|--------|
| `backend/open_webui/main.py` | Register `budgets.router` under `/api/v1/users` and `/api/v1/admin` |
| `backend/open_webui/routers/openai.py` | Add pre-flight check before forwarding completions; add post-completion debit hook |
| `backend/open_webui/routers/ollama.py` | Same pre-flight check and post-completion debit hook |
| `src/lib/stores/index.ts` | Add `userBudget: Writable<UserBudget | null>` store |
| `src/lib/components/chat/Navbar.svelte` | Mount `BalanceIndicator` component |
| `src/lib/components/admin/Users.svelte` | Add "Budgets" tab that renders `BudgetManager` |

#### 3.1.3 Execution Flow

**Pre-flight (blocking):**
```
User sends chat message
  -> openai.py / ollama.py route handler
  -> check_user_budget(user.id, db)
     -> if user has budget AND current_balance <= 0: raise HTTP 402
     -> else: continue
  -> forward to LLM
```

**Post-completion (async, non-blocking to user):**
```
LLM response complete
  -> extract usage: {input_tokens, output_tokens, model_id} from response
  -> debit_user_budget(user.id, model_id, chat_id, message_id, input_tokens, output_tokens, db)
     -> look up pricing for model_id (with fallback: $0 if no pricing found)
     -> compute cost = (input_tokens / 1_000_000 * input_usd_per_million)
                     + (output_tokens / 1_000_000 * output_usd_per_million)
     -> within single DB transaction:
        UPDATE user_budget SET current_balance = current_balance - cost, updated_at = now
        INSERT INTO spending_transaction (...)
```

The post-completion debit is called from within the same request handler, after the streaming response has finished (for streaming: inside the generator's finally block or after the last chunk is yielded). It must not raise to the user; errors are logged only.

### 3.2 API Contracts

#### GET /api/v1/users/me/budget
Auth: `get_verified_user` (any logged-in user, own data only)

Response `200`:
```json
{
  "user_id": "string",
  "initial_budget": 5.0,
  "current_balance": 3.241500,
  "hard_limit": true,
  "percent_remaining": 64.83,
  "created_at": 1740000000,
  "updated_at": 1740012345
}
```
Response `404`: `{"detail": "No budget assigned"}` — returned when the user has no budget row.

#### GET /api/v1/users/{user_id}/budget
Auth: `get_admin_user`

Response: same shape as above for the specified user.
Response `404`: user not found or no budget assigned.

#### POST /api/v1/users/{user_id}/budget
Auth: `get_admin_user`

Request body:
```json
{
  "initial_budget": 5.0,
  "hard_limit": true,
  "reset_balance": false
}
```
- `initial_budget` (required): new initial budget in USD.
- `hard_limit` (optional, default `true`): whether to enforce the hard block at zero.
- `reset_balance` (optional, default `false`): if `true`, set `current_balance = initial_budget` (full reset). If `false`, adjust by the delta: `current_balance += (new_initial - old_initial)`. On first creation, `current_balance = initial_budget` always.

Response `200`: the updated `UserBudgetModel`.

#### GET /api/v1/users/{user_id}/spending
Auth: `get_admin_user`

Query params:
- `skip` (int, default 0)
- `limit` (int, default 50, max 200)
- `start_date` (int epoch, optional)
- `end_date` (int epoch, optional)

Response `200`:
```json
{
  "transactions": [
    {
      "id": "uuid",
      "user_id": "string",
      "chat_id": "string",
      "message_id": "string",
      "model_id": "string",
      "input_tokens": 1200,
      "output_tokens": 300,
      "input_cost_usd": 0.000003,
      "output_cost_usd": 0.000003,
      "total_cost_usd": 0.000006,
      "created_at": 1740012345
    }
  ],
  "total_spent_usd": 1.7585,
  "count": 42
}
```

#### GET /api/v1/admin/budgets
Auth: `get_admin_user`

Query params: `skip`, `limit` (default 50, max 200)

Response `200`:
```json
{
  "budgets": [
    {
      "user_id": "string",
      "user_name": "string",
      "user_email": "string",
      "initial_budget": 5.0,
      "current_balance": 2.14,
      "hard_limit": true,
      "percent_remaining": 42.8,
      "total_spent_usd": 2.86,
      "created_at": 1740000000,
      "updated_at": 1740012345
    }
  ],
  "total": 12
}
```

### 3.3 Database Changes

#### 3.3.1 New Table: `user_budget`

```sql
CREATE TABLE user_budget (
    user_id          TEXT        PRIMARY KEY,  -- FK to user.id
    initial_budget   NUMERIC(12,6) NOT NULL,
    current_balance  NUMERIC(12,6) NOT NULL,
    hard_limit       BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at       BIGINT      NOT NULL,
    updated_at       BIGINT      NOT NULL
);

CREATE INDEX idx_user_budget_user_id ON user_budget (user_id);
```

Notes:
- No FK constraint on `user_id` to avoid cascade complexity; the application layer validates user existence before insert.
- `NUMERIC(12,6)` supports balances up to $999,999.999999 with micro-dollar precision.
- `hard_limit = FALSE` is reserved for future "soft limit / notification only" mode; current implementation always enforces the block when `hard_limit = TRUE`.

#### 3.3.2 New Table: `spending_transaction`

```sql
CREATE TABLE spending_transaction (
    id               TEXT        PRIMARY KEY,  -- uuid4
    user_id          TEXT        NOT NULL,
    chat_id          TEXT        NOT NULL,
    message_id       TEXT        NOT NULL,
    model_id         TEXT        NOT NULL,
    input_tokens     BIGINT      NOT NULL DEFAULT 0,
    output_tokens    BIGINT      NOT NULL DEFAULT 0,
    input_cost_usd   NUMERIC(12,6) NOT NULL DEFAULT 0,
    output_cost_usd  NUMERIC(12,6) NOT NULL DEFAULT 0,
    total_cost_usd   NUMERIC(12,6) NOT NULL DEFAULT 0,
    created_at       BIGINT      NOT NULL
);

CREATE INDEX idx_spending_tx_user_id  ON spending_transaction (user_id);
CREATE INDEX idx_spending_tx_created  ON spending_transaction (user_id, created_at);
CREATE INDEX idx_spending_tx_chat_id  ON spending_transaction (chat_id);
```

#### 3.3.3 Alembic Migration

Create file: `backend/open_webui/migrations/versions/<rev>_add_budget_tables.py`

- `down_revision` must point to `9a2b3c4d5e6f` (the latest migration: `add_model_pricing`).
- Use `get_existing_tables()` guard (as in all other migrations) to make the upgrade idempotent.
- `downgrade()` drops both tables and their indexes in reverse order.

#### 3.3.4 SQLAlchemy ORM (`backend/open_webui/models/budgets.py`)

Follow the exact pattern from `models/pricing.py` and `models/users.py`:
- One `Base`-derived ORM class per table (e.g., `UserBudget`, `SpendingTransaction`).
- One `BaseModel`-derived Pydantic class per ORM class with `model_config = ConfigDict(from_attributes=True)`.
- One table operations class (e.g., `BudgetsTable`) with methods: `get_budget_by_user_id`, `upsert_budget`, `get_transactions_by_user_id`, `get_all_budgets`, `insert_transaction`.
- Use `get_db_context(db)` context manager for all DB operations (same as every other model file).
- Use `int(time.time())` for `BigInteger` timestamps.
- Use `from sqlalchemy import Numeric` for the `NUMERIC(12,6)` columns.

### 3.4 Utility Functions (`backend/open_webui/utils/budget.py`)

```python
def calculate_message_cost(
    model_id: str,
    input_tokens: int,
    output_tokens: int,
    db: Optional[Session] = None,
) -> tuple[float, float, float]:
    """
    Returns (input_cost_usd, output_cost_usd, total_cost_usd).
    Looks up model_pricing table; returns (0, 0, 0) if model not found.
    """

def check_user_budget(user_id: str, db: Optional[Session] = None) -> None:
    """
    Raises HTTPException(402) if user has a hard-limit budget with balance <= 0.
    No-ops if user has no budget row.
    """

def debit_user_budget(
    user_id: str,
    model_id: str,
    chat_id: str,
    message_id: str,
    input_tokens: int,
    output_tokens: int,
    db: Optional[Session] = None,
) -> Optional[float]:
    """
    Calculates cost, debits from user_budget, inserts spending_transaction.
    All within a single DB transaction.
    Returns new current_balance, or None if user has no budget.
    Errors are caught and logged; never raises to caller.
    """
```

### 3.5 Router Integration

#### Pre-flight hook location (openai.py)

In `openai.py`, the main chat completions handler is the `/chat/completions` route. The pre-flight check is added at the top of the handler, after user auth resolves:

```python
from open_webui.utils.budget import check_user_budget

# Inside the route handler, before any upstream call:
check_user_budget(user.id, db=db)
```

#### Post-completion hook location (openai.py)

For **non-streaming** responses: call `debit_user_budget(...)` after the upstream response is received and `usage` is available.

For **streaming** responses: wrap the generator. In the `finally` block of the generator, extract the accumulated usage (OpenAI streams include a final `data: [DONE]` chunk with usage when `stream_options: {"include_usage": true}` is set, or accumulate token counts from delta chunks) and call `debit_user_budget(...)`. If token data is unavailable (e.g., provider does not return usage in stream), skip debit and log a warning.

The same pattern applies to `ollama.py`.

### 3.6 Frontend Design

#### Store (`src/lib/stores/index.ts`)

Add:
```typescript
export interface UserBudget {
  user_id: string;
  initial_budget: number;
  current_balance: number;
  hard_limit: boolean;
  percent_remaining: number;
}

export const userBudget: Writable<UserBudget | null> = writable(null);
```

The store is loaded once on app mount (in the root layout) by calling `GET /api/v1/users/me/budget`. If the response is 404, store remains `null` (no budget assigned, no UI shown).

#### API Client (`src/lib/apis/budgets.ts`)

Pattern: identical to other files in `src/lib/apis/` — uses `WEBUI_BASE_URL`, Bearer token, `fetch`, throws on non-ok.

```typescript
export const getUserBudget = async (token: string): Promise<UserBudget | null>
export const getUserBudgetAdmin = async (token: string, userId: string): Promise<UserBudget | null>
export const setUserBudget = async (token: string, userId: string, form: SetBudgetForm): Promise<UserBudget>
export const getUserSpending = async (token: string, userId: string, params?: SpendingQueryParams): Promise<SpendingResponse>
export const getAllBudgets = async (token: string, params?: PaginationParams): Promise<AllBudgetsResponse>
```

#### Balance Indicator Component (`src/lib/components/budget/BalanceIndicator.svelte`)

- Imports `userBudget` store.
- Renders nothing when `$userBudget === null`.
- When balance > 20% of initial: shows a small pill, e.g., `$2.14 left`, in muted gray.
- When balance <= 20% but > 0: shows the pill in amber/yellow with a warning icon.
- When balance <= 0: shows a red pill `Budget exhausted` with an exclamation icon.
- Placed inside `Navbar.svelte` in the right-side controls area.

#### Budget Exhausted Gate

In `src/lib/components/chat/MessageInput.svelte`, check `$userBudget` before allowing message submission:

```svelte
{#if $userBudget && $userBudget.current_balance <= 0}
  <div class="text-red-500 text-sm text-center py-2">
    {$i18n.t('Budget exhausted. Contact your administrator to top up your balance.')}
  </div>
  <!-- submit button disabled -->
{/if}
```

The backend 402 response is also shown as a `toast.error(...)` via the existing error handling in `Chat.svelte`.

#### Admin Budget Manager (`src/lib/components/admin/Users/BudgetManager.svelte`)

- Fetches `GET /api/v1/admin/budgets` on mount.
- Shows a table: User Name, Email, Initial Budget, Current Balance, % Remaining, Total Spent, Actions.
- "Set Budget" button per row opens an inline form: `initial_budget` amount input, `reset_balance` toggle, Save/Cancel.
- "View Spending" button opens a modal with a paginated table of `SpendingTransaction` entries for that user.
- Mounted as a new "Budgets" tab in `src/lib/components/admin/Users.svelte` alongside the existing "Overview" and "Groups" tabs.

---

## 4. Testing Strategy

### Unit Tests (`pytest`, colocated in `backend/`)

- `tests/utils/test_budget.py`:
  - `calculate_message_cost` with known pricing returns correct USD amounts.
  - `calculate_message_cost` with unknown model_id returns `(0, 0, 0)`.
  - `check_user_budget` raises `HTTPException(402)` when `current_balance = 0` and `hard_limit = True`.
  - `check_user_budget` does not raise when user has no budget row.
  - `check_user_budget` does not raise when `hard_limit = False` even at zero balance.
  - `debit_user_budget` decrements balance by calculated cost.
  - `debit_user_budget` inserts one `spending_transaction` record.
  - `debit_user_budget` catches exception and does not re-raise.

- `tests/models/test_budgets.py`:
  - `upsert_budget` creates a new row on first call.
  - `upsert_budget` with `reset_balance=True` sets `current_balance = initial_budget`.
  - `upsert_budget` with `reset_balance=False` applies delta to existing balance.
  - `get_transactions_by_user_id` respects `start_date` / `end_date` filters.

### Integration Tests

- `tests/routers/test_budgets.py` (uses FastAPI `TestClient`):
  - `POST /api/v1/users/{user_id}/budget` as admin succeeds with 200.
  - `POST /api/v1/users/{user_id}/budget` as non-admin returns 401.
  - `GET /api/v1/users/me/budget` returns 404 for user with no budget.
  - `GET /api/v1/users/me/budget` returns correct data after budget is set.
  - `GET /api/v1/admin/budgets` returns paginated list.
  - `GET /api/v1/users/{user_id}/spending` returns transaction history.

### End-to-End Test Scenario

1. Create user `juan.hernandez` (email: `juan.hernandez@test.com`).
2. Admin calls `POST /api/v1/users/{juan_id}/budget` with `{"initial_budget": 5.0}`.
3. Verify `GET /api/v1/users/{juan_id}/budget` returns `current_balance = 5.0`.
4. Simulate an LLM assistant message for `juan.hernandez`: `model_id = "gpt-4o"`, `input_tokens = 1000`, `output_tokens = 500`.
   - Expected cost: `(1000/1e6 * 2.50) + (500/1e6 * 10.00) = $0.002500 + $0.005000 = $0.007500`
5. Verify `current_balance = 4.9925` and one `spending_transaction` row exists.
6. Drain the balance to near zero by inserting synthetic transactions.
7. Attempt to send another message — verify HTTP 402 is returned.
8. Verify frontend shows "Budget exhausted" and send button is disabled.
9. Admin tops up: `POST /api/v1/users/{juan_id}/budget` with `{"initial_budget": 10.0, "reset_balance": true}`.
10. Verify `current_balance = 10.0` and messages are unblocked.

---

## 5. Acceptance Criteria

- [ ] `user_budget` and `spending_transaction` tables are created by Alembic migration; migration is idempotent (safe to run twice).
- [ ] Admin can set budget for a user via `POST /api/v1/users/{user_id}/budget`; endpoint returns the updated `UserBudgetModel`.
- [ ] User `juan.hernandez` assigned $5.00 budget; after one `gpt-4o` message (1000 input, 500 output tokens), `current_balance` decreases by exactly $0.0075.
- [ ] One `spending_transaction` row is created per debited message with correct `total_cost_usd`.
- [ ] When `current_balance <= 0` and `hard_limit = true`, LLM request returns HTTP 402 with `{"detail": "Budget exhausted"}`.
- [ ] Users with no `user_budget` row are not affected; zero additional latency on pre-flight check.
- [ ] `GET /api/v1/users/me/budget` returns 404 for users without a budget row.
- [ ] `GET /api/v1/admin/budgets` returns a list of all users with budgets; accessible only to admins.
- [ ] Frontend balance indicator is visible in the chat navbar when the user has a budget.
- [ ] Frontend shows amber warning when `percent_remaining < 20`.
- [ ] Frontend shows red "Budget exhausted" and the message send button is disabled when `current_balance <= 0`.
- [ ] Admin budget management tab is accessible at `/admin/users/budgets` and displays all users with budgets.
- [ ] All new backend functions have unit tests passing under `pytest`.
- [ ] `npm run check` (TypeScript/Svelte type checking) passes with no new errors.

---

## 6. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Streaming response ends without token usage data (provider does not return usage) | Cost not debited; balance not decremented | Log warning; for streaming, set `stream_options: {"include_usage": true}` for OpenAI-compatible providers. Fallback: skip debit and record zero-cost transaction with a `usage_unavailable = true` flag on the transaction |
| Race condition: two concurrent messages from the same user both pass the pre-flight check when balance is near zero | Double debit below zero | `UPDATE user_budget SET current_balance = current_balance - :cost WHERE user_id = :uid` is atomic at the DB level; balance can go slightly negative. This is acceptable; the pre-flight check blocks new messages once it reads <= 0 |
| User has no pricing entry for a model | Cost calculated as $0; balance not affected | Fallback pricing returns `(0, 0, 0)`; transaction is still logged with zero cost. Admin can manually add pricing via existing `model_pricing` upsert |
| Admin sets budget on a non-existent user_id | Ghost row in `user_budget` | Router validates `Users.get_user_by_id(user_id)` before upsert; returns 404 if user not found |
| High-volume deployments: `spending_transaction` table grows unbounded | Slow queries over time | Index on `(user_id, created_at)` covers the main access patterns. Archival/pruning strategy is out of scope for this spec but the index design supports it |
| `NUMERIC(12,6)` vs `Float` precision | Accumulated rounding errors in balance | Using `Numeric(12,6)` in SQLAlchemy via `sa.Numeric(12, 6)` ensures DB-level decimal arithmetic; Python-side intermediate computation uses `float` which is acceptable given the precision requirement |
