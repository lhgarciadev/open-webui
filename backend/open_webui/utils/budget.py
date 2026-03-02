import logging
from typing import Optional

from fastapi import HTTPException

from open_webui.models.budgets import Budgets
from open_webui.models.pricing import PricingTable

log = logging.getLogger(__name__)

pricing_table = PricingTable()


def calculate_message_cost(
    model_id: str,
    input_tokens: int,
    output_tokens: int,
    db=None,
) -> tuple[float, float, float]:
    """
    Returns (input_cost_usd, output_cost_usd, total_cost_usd).
    Looks up model_pricing table; returns (0, 0, 0) if model not found.
    Tries exact match first, then strips provider prefix (e.g. openai/gpt-4o -> gpt-4o).
    """
    rows = pricing_table.get_by_ids([model_id], db=db)
    if not rows and "/" in model_id:
        # OpenRouter-style IDs: try stripping provider prefix
        bare_id = model_id.split("/", 1)[1]
        rows = pricing_table.get_by_ids([bare_id], db=db)
    if not rows:
        return (0.0, 0.0, 0.0)

    pricing = rows[0]
    input_rate = pricing.input_usd_per_million or 0.0
    output_rate = pricing.output_usd_per_million or 0.0

    input_cost = (input_tokens / 1_000_000) * input_rate
    output_cost = (output_tokens / 1_000_000) * output_rate
    total_cost = input_cost + output_cost

    return (
        round(input_cost, 6),
        round(output_cost, 6),
        round(total_cost, 6),
    )


def check_user_budget(user_id: str, db=None) -> None:
    """
    Raises HTTPException(402) if user has a hard-limit budget with balance <= 0.
    No-ops if user has no budget row.
    """
    budget = Budgets.get_budget_by_user_id(user_id, db=db)
    if budget is None:
        return

    if budget.hard_limit and budget.current_balance <= 0:
        raise HTTPException(
            status_code=402,
            detail="Budget exhausted",
        )


def debit_user_budget(
    user_id: str,
    model_id: str,
    chat_id: str,
    message_id: str,
    input_tokens: int,
    output_tokens: int,
    db=None,
) -> Optional[float]:
    """
    Calculates cost, debits from user_budget, inserts spending_transaction.
    All within a single DB transaction.
    Returns new current_balance, or None if user has no budget.
    Errors are caught and logged; never raises to caller.
    """
    try:
        input_cost, output_cost, total_cost = calculate_message_cost(
            model_id, input_tokens, output_tokens, db=db
        )

        new_balance = Budgets.debit_and_record(
            user_id=user_id,
            chat_id=chat_id,
            message_id=message_id,
            model_id=model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost_usd=input_cost,
            output_cost_usd=output_cost,
            total_cost_usd=total_cost,
            db=db,
        )

        if new_balance is not None:
            log.info(
                "Budget debit: user=%s model=%s cost=$%.6f balance=$%.6f",
                user_id,
                model_id,
                total_cost,
                new_balance,
            )

        return new_balance
    except Exception:
        log.exception("Failed to debit budget for user=%s", user_id)
        return None
