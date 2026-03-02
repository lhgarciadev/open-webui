"""Unit tests for the budget utility functions.

These tests mock the database layer and focus on testing the pure logic
of calculate_message_cost, check_user_budget, and debit_user_budget.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from open_webui.utils.budget import (
    calculate_message_cost,
    check_user_budget,
    debit_user_budget,
)


class MockPricingRow:
    """Mock for a ModelPricing row."""

    def __init__(self, input_usd_per_million=2.50, output_usd_per_million=10.00):
        self.input_usd_per_million = input_usd_per_million
        self.output_usd_per_million = output_usd_per_million


class MockBudget:
    """Mock for a UserBudgetModel."""

    def __init__(self, user_id="user-1", current_balance=5.0, hard_limit=True, initial_budget=5.0):
        self.user_id = user_id
        self.current_balance = current_balance
        self.hard_limit = hard_limit
        self.initial_budget = initial_budget


class TestCalculateMessageCost:
    @patch("open_webui.utils.budget.pricing_table")
    def test_known_model_returns_correct_cost(self, mock_pricing_table):
        """calculate_message_cost with known pricing returns correct USD amounts."""
        mock_pricing_table.get_by_ids.return_value = [
            MockPricingRow(input_usd_per_million=2.50, output_usd_per_million=10.00)
        ]

        input_cost, output_cost, total_cost = calculate_message_cost(
            "gpt-4o", input_tokens=1000, output_tokens=500
        )

        # (1000 / 1_000_000) * 2.50 = 0.0025
        # (500 / 1_000_000) * 10.00 = 0.005
        # total = 0.0075
        assert input_cost == 0.0025
        assert output_cost == 0.005
        assert total_cost == 0.0075

    @patch("open_webui.utils.budget.pricing_table")
    def test_unknown_model_returns_zeros(self, mock_pricing_table):
        """calculate_message_cost with unknown model_id returns (0, 0, 0)."""
        mock_pricing_table.get_by_ids.return_value = []

        input_cost, output_cost, total_cost = calculate_message_cost(
            "unknown-model", input_tokens=1000, output_tokens=500
        )

        assert input_cost == 0.0
        assert output_cost == 0.0
        assert total_cost == 0.0

    @patch("open_webui.utils.budget.pricing_table")
    def test_zero_tokens_returns_zeros(self, mock_pricing_table):
        """calculate_message_cost with zero tokens returns (0, 0, 0)."""
        mock_pricing_table.get_by_ids.return_value = [
            MockPricingRow(input_usd_per_million=2.50, output_usd_per_million=10.00)
        ]

        input_cost, output_cost, total_cost = calculate_message_cost(
            "gpt-4o", input_tokens=0, output_tokens=0
        )

        assert input_cost == 0.0
        assert output_cost == 0.0
        assert total_cost == 0.0

    @patch("open_webui.utils.budget.pricing_table")
    def test_large_token_count(self, mock_pricing_table):
        """calculate_message_cost with large token counts works correctly."""
        mock_pricing_table.get_by_ids.return_value = [
            MockPricingRow(input_usd_per_million=2.50, output_usd_per_million=10.00)
        ]

        input_cost, output_cost, total_cost = calculate_message_cost(
            "gpt-4o", input_tokens=1_000_000, output_tokens=1_000_000
        )

        assert input_cost == 2.5
        assert output_cost == 10.0
        assert total_cost == 12.5


class TestCheckUserBudget:
    @patch("open_webui.utils.budget.Budgets")
    def test_raises_402_when_balance_zero_and_hard_limit(self, mock_budgets):
        """check_user_budget raises HTTPException(402) when balance=0 and hard_limit=True."""
        mock_budgets.get_budget_by_user_id.return_value = MockBudget(
            current_balance=0.0, hard_limit=True
        )

        with pytest.raises(HTTPException) as exc_info:
            check_user_budget("user-1")

        assert exc_info.value.status_code == 402
        assert exc_info.value.detail == "Budget exhausted"

    @patch("open_webui.utils.budget.Budgets")
    def test_raises_402_when_balance_negative(self, mock_budgets):
        """check_user_budget raises HTTPException(402) when balance is negative."""
        mock_budgets.get_budget_by_user_id.return_value = MockBudget(
            current_balance=-0.5, hard_limit=True
        )

        with pytest.raises(HTTPException) as exc_info:
            check_user_budget("user-1")

        assert exc_info.value.status_code == 402

    @patch("open_webui.utils.budget.Budgets")
    def test_does_not_raise_when_no_budget_row(self, mock_budgets):
        """check_user_budget does not raise when user has no budget row."""
        mock_budgets.get_budget_by_user_id.return_value = None

        # Should not raise
        check_user_budget("user-1")

    @patch("open_webui.utils.budget.Budgets")
    def test_does_not_raise_when_hard_limit_false(self, mock_budgets):
        """check_user_budget does not raise when hard_limit=False even at zero balance."""
        mock_budgets.get_budget_by_user_id.return_value = MockBudget(
            current_balance=0.0, hard_limit=False
        )

        # Should not raise
        check_user_budget("user-1")

    @patch("open_webui.utils.budget.Budgets")
    def test_does_not_raise_when_balance_positive(self, mock_budgets):
        """check_user_budget does not raise when balance is positive."""
        mock_budgets.get_budget_by_user_id.return_value = MockBudget(
            current_balance=3.5, hard_limit=True
        )

        # Should not raise
        check_user_budget("user-1")


class TestDebitUserBudget:
    @patch("open_webui.utils.budget.Budgets")
    @patch("open_webui.utils.budget.calculate_message_cost")
    def test_debits_and_returns_balance(self, mock_calc, mock_budgets):
        """debit_user_budget decrements balance and returns new value."""
        mock_calc.return_value = (0.0025, 0.005, 0.0075)
        mock_budgets.debit_and_record.return_value = 4.9925

        new_balance = debit_user_budget(
            user_id="user-1",
            model_id="gpt-4o",
            chat_id="chat-1",
            message_id="msg-1",
            input_tokens=1000,
            output_tokens=500,
        )

        assert new_balance == 4.9925
        mock_budgets.debit_and_record.assert_called_once_with(
            user_id="user-1",
            chat_id="chat-1",
            message_id="msg-1",
            model_id="gpt-4o",
            input_tokens=1000,
            output_tokens=500,
            input_cost_usd=0.0025,
            output_cost_usd=0.005,
            total_cost_usd=0.0075,
            db=None,
        )

    @patch("open_webui.utils.budget.Budgets")
    @patch("open_webui.utils.budget.calculate_message_cost")
    def test_returns_none_when_no_budget(self, mock_calc, mock_budgets):
        """debit_user_budget returns None if user has no budget."""
        mock_calc.return_value = (0.0025, 0.005, 0.0075)
        mock_budgets.debit_and_record.return_value = None

        result = debit_user_budget(
            user_id="user-1",
            model_id="gpt-4o",
            chat_id="chat-1",
            message_id="msg-1",
            input_tokens=1000,
            output_tokens=500,
        )

        assert result is None

    @patch("open_webui.utils.budget.Budgets")
    @patch("open_webui.utils.budget.calculate_message_cost")
    def test_catches_exception_and_returns_none(self, mock_calc, mock_budgets):
        """debit_user_budget catches exception and does not re-raise."""
        mock_calc.side_effect = Exception("DB error")

        result = debit_user_budget(
            user_id="user-1",
            model_id="gpt-4o",
            chat_id="chat-1",
            message_id="msg-1",
            input_tokens=1000,
            output_tokens=500,
        )

        assert result is None
