import time
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Boolean, Column, Numeric, Text, func
from sqlalchemy.orm import Session

from open_webui.internal.db import Base, get_db_context


####################
# UserBudget DB Schema
####################


class UserBudget(Base):
    __tablename__ = "user_budget"

    user_id = Column(Text, primary_key=True)
    initial_budget = Column(Numeric(12, 6), nullable=False)
    current_balance = Column(Numeric(12, 6), nullable=False)
    hard_limit = Column(Boolean, nullable=False, default=True)
    created_at = Column(BigInteger, nullable=False)
    updated_at = Column(BigInteger, nullable=False)


class UserBudgetModel(BaseModel):
    user_id: str
    initial_budget: float
    current_balance: float
    hard_limit: bool
    created_at: int
    updated_at: int

    model_config = ConfigDict(from_attributes=True)


class UserBudgetResponse(UserBudgetModel):
    percent_remaining: float


####################
# SpendingTransaction DB Schema
####################


class SpendingTransaction(Base):
    __tablename__ = "spending_transaction"

    id = Column(Text, primary_key=True)
    user_id = Column(Text, nullable=False, index=True)
    chat_id = Column(Text, nullable=False, index=True)
    message_id = Column(Text, nullable=False)
    model_id = Column(Text, nullable=False)
    input_tokens = Column(BigInteger, nullable=False, default=0)
    output_tokens = Column(BigInteger, nullable=False, default=0)
    input_cost_usd = Column(Numeric(12, 6), nullable=False, default=0)
    output_cost_usd = Column(Numeric(12, 6), nullable=False, default=0)
    total_cost_usd = Column(Numeric(12, 6), nullable=False, default=0)
    created_at = Column(BigInteger, nullable=False)


class SpendingTransactionModel(BaseModel):
    id: str
    user_id: str
    chat_id: str
    message_id: str
    model_id: str
    input_tokens: int
    output_tokens: int
    input_cost_usd: float
    output_cost_usd: float
    total_cost_usd: float
    created_at: int

    model_config = ConfigDict(from_attributes=True)


####################
# Request/Response Forms
####################


class SetBudgetForm(BaseModel):
    initial_budget: float
    hard_limit: bool = True
    reset_balance: bool = False


class SpendingResponse(BaseModel):
    transactions: list[SpendingTransactionModel]
    total_spent_usd: float
    count: int


class AllBudgetsItem(BaseModel):
    user_id: str
    user_name: str
    user_email: str
    initial_budget: float
    current_balance: float
    hard_limit: bool
    percent_remaining: float
    total_spent_usd: float
    created_at: int
    updated_at: int


class AllBudgetsResponse(BaseModel):
    budgets: list[AllBudgetsItem]
    total: int


####################
# Table Operations
####################


class BudgetsTable:
    def get_budget_by_user_id(
        self, user_id: str, db: Optional[Session] = None
    ) -> Optional[UserBudgetModel]:
        with get_db_context(db) as db:
            budget = db.query(UserBudget).filter_by(user_id=user_id).first()
            if budget:
                return UserBudgetModel.model_validate(budget)
            return None

    def upsert_budget(
        self,
        user_id: str,
        form_data: SetBudgetForm,
        db: Optional[Session] = None,
    ) -> Optional[UserBudgetModel]:
        now = int(time.time())
        with get_db_context(db) as db:
            existing = db.query(UserBudget).filter_by(user_id=user_id).first()
            if existing:
                old_initial = float(existing.initial_budget)
                new_initial = form_data.initial_budget

                if form_data.reset_balance:
                    existing.current_balance = new_initial
                else:
                    delta = new_initial - old_initial
                    existing.current_balance = float(existing.current_balance) + delta

                existing.initial_budget = new_initial
                existing.hard_limit = form_data.hard_limit
                existing.updated_at = now
                db.commit()
                db.refresh(existing)
                return UserBudgetModel.model_validate(existing)
            else:
                budget = UserBudget(
                    user_id=user_id,
                    initial_budget=form_data.initial_budget,
                    current_balance=form_data.initial_budget,
                    hard_limit=form_data.hard_limit,
                    created_at=now,
                    updated_at=now,
                )
                db.add(budget)
                db.commit()
                db.refresh(budget)
                return UserBudgetModel.model_validate(budget)

    def get_all_budgets(
        self,
        skip: int = 0,
        limit: int = 50,
        db: Optional[Session] = None,
    ) -> dict:
        with get_db_context(db) as db:
            query = db.query(UserBudget).order_by(UserBudget.updated_at.desc())
            total = query.count()
            budgets = query.offset(skip).limit(limit).all()
            return {
                "budgets": [UserBudgetModel.model_validate(b) for b in budgets],
                "total": total,
            }

    def insert_transaction(
        self,
        user_id: str,
        chat_id: str,
        message_id: str,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
        input_cost_usd: float,
        output_cost_usd: float,
        total_cost_usd: float,
        db: Optional[Session] = None,
    ) -> Optional[SpendingTransactionModel]:
        now = int(time.time())
        with get_db_context(db) as db:
            transaction = SpendingTransaction(
                id=str(uuid.uuid4()),
                user_id=user_id,
                chat_id=chat_id,
                message_id=message_id,
                model_id=model_id,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                input_cost_usd=input_cost_usd,
                output_cost_usd=output_cost_usd,
                total_cost_usd=total_cost_usd,
                created_at=now,
            )
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            return SpendingTransactionModel.model_validate(transaction)

    def debit_and_record(
        self,
        user_id: str,
        chat_id: str,
        message_id: str,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
        input_cost_usd: float,
        output_cost_usd: float,
        total_cost_usd: float,
        db: Optional[Session] = None,
    ) -> Optional[float]:
        """Debit user budget and insert transaction in a single DB transaction.

        Returns the new current_balance, or None if user has no budget.
        """
        now = int(time.time())
        with get_db_context(db) as db:
            budget = db.query(UserBudget).filter_by(user_id=user_id).first()
            if not budget:
                return None

            budget.current_balance = float(budget.current_balance) - total_cost_usd
            budget.updated_at = now

            transaction = SpendingTransaction(
                id=str(uuid.uuid4()),
                user_id=user_id,
                chat_id=chat_id,
                message_id=message_id,
                model_id=model_id,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                input_cost_usd=input_cost_usd,
                output_cost_usd=output_cost_usd,
                total_cost_usd=total_cost_usd,
                created_at=now,
            )
            db.add(transaction)
            db.commit()
            db.refresh(budget)
            return float(budget.current_balance)

    def get_transactions_by_user_id(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
        db: Optional[Session] = None,
    ) -> dict:
        with get_db_context(db) as db:
            query = db.query(SpendingTransaction).filter_by(user_id=user_id)

            if start_date is not None:
                query = query.filter(SpendingTransaction.created_at >= start_date)
            if end_date is not None:
                query = query.filter(SpendingTransaction.created_at <= end_date)

            count = query.count()

            total_spent = (
                db.query(func.coalesce(func.sum(SpendingTransaction.total_cost_usd), 0))
                .filter(SpendingTransaction.user_id == user_id)
                .scalar()
            )

            transactions = (
                query.order_by(SpendingTransaction.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )

            return {
                "transactions": [
                    SpendingTransactionModel.model_validate(t) for t in transactions
                ],
                "total_spent_usd": float(total_spent),
                "count": count,
            }

    def get_total_spent_by_user_id(
        self, user_id: str, db: Optional[Session] = None
    ) -> float:
        with get_db_context(db) as db:
            total = (
                db.query(func.coalesce(func.sum(SpendingTransaction.total_cost_usd), 0))
                .filter(SpendingTransaction.user_id == user_id)
                .scalar()
            )
            return float(total)


Budgets = BudgetsTable()
