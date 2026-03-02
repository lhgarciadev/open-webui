from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from open_webui.models.budgets import (
    AllBudgetsItem,
    AllBudgetsResponse,
    Budgets,
    SetBudgetForm,
    SpendingResponse,
    UserBudgetResponse,
)
from open_webui.models.users import Users
from open_webui.utils.auth import get_admin_user, get_verified_user

router = APIRouter()


def _budget_to_response(budget) -> UserBudgetResponse:
    """Convert a UserBudgetModel to a UserBudgetResponse with percent_remaining."""
    if budget.initial_budget > 0:
        percent_remaining = round(
            (budget.current_balance / budget.initial_budget) * 100, 2
        )
    else:
        percent_remaining = 0.0

    return UserBudgetResponse(
        user_id=budget.user_id,
        initial_budget=budget.initial_budget,
        current_balance=budget.current_balance,
        hard_limit=budget.hard_limit,
        percent_remaining=max(percent_remaining, 0.0),
        created_at=budget.created_at,
        updated_at=budget.updated_at,
    )


####################
# User endpoints
####################


@router.get("/me/budget")
async def get_my_budget(user=Depends(get_verified_user)):
    budget = Budgets.get_budget_by_user_id(user.id)
    if not budget:
        raise HTTPException(status_code=404, detail="No budget assigned")
    return _budget_to_response(budget)


####################
# Admin endpoints
####################


@router.get("/admin/budgets")
async def get_all_budgets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user=Depends(get_admin_user),
):
    result = Budgets.get_all_budgets(skip=skip, limit=limit)

    items = []
    for budget in result["budgets"]:
        user_info = Users.get_user_by_id(budget.user_id)
        total_spent = Budgets.get_total_spent_by_user_id(budget.user_id)

        if budget.initial_budget > 0:
            percent_remaining = round(
                (budget.current_balance / budget.initial_budget) * 100, 2
            )
        else:
            percent_remaining = 0.0

        items.append(
            AllBudgetsItem(
                user_id=budget.user_id,
                user_name=user_info.name if user_info else "Unknown",
                user_email=user_info.email if user_info else "Unknown",
                initial_budget=budget.initial_budget,
                current_balance=budget.current_balance,
                hard_limit=budget.hard_limit,
                percent_remaining=max(percent_remaining, 0.0),
                total_spent_usd=total_spent,
                created_at=budget.created_at,
                updated_at=budget.updated_at,
            )
        )

    return AllBudgetsResponse(budgets=items, total=result["total"])


@router.get("/{user_id}/budget")
async def get_user_budget(user_id: str, user=Depends(get_admin_user)):
    target_user = Users.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    budget = Budgets.get_budget_by_user_id(user_id)
    if not budget:
        raise HTTPException(status_code=404, detail="No budget assigned")

    return _budget_to_response(budget)


@router.post("/{user_id}/budget")
async def set_user_budget(
    user_id: str,
    form_data: SetBudgetForm,
    user=Depends(get_admin_user),
):
    target_user = Users.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    budget = Budgets.upsert_budget(user_id, form_data)
    if not budget:
        raise HTTPException(status_code=500, detail="Failed to set budget")

    return _budget_to_response(budget)


@router.get("/{user_id}/spending")
async def get_user_spending(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    user=Depends(get_admin_user),
):
    target_user = Users.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    result = Budgets.get_transactions_by_user_id(
        user_id=user_id,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )

    return SpendingResponse(
        transactions=result["transactions"],
        total_spent_usd=result["total_spent_usd"],
        count=result["count"],
    )
