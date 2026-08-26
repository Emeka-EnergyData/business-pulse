from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

from src.services.reports_service import ReportsService


def create_service():
    sales_repository = Mock()
    purchase_repository = Mock()

    service = ReportsService(
        sales_repository=sales_repository,
        purchase_repository=purchase_repository,
    )

    return service, sales_repository, purchase_repository


def test_get_sales_summary():
    service, sales_repository, _ = create_service()

    sales_repository.get_sales_between_dates.return_value = [
        SimpleNamespace(
            total_amount=Decimal("50000.00"),
            amount_paid=Decimal("50000.00"),
            remaining_balance=Decimal("0.00"),
        ),
        SimpleNamespace(
            total_amount=Decimal("30000.00"),
            amount_paid=Decimal("10000.00"),
            remaining_balance=Decimal("20000.00"),
        ),
        SimpleNamespace(
            total_amount=Decimal("20000.00"),
            amount_paid=Decimal("5000.00"),
            remaining_balance=Decimal("15000.00"),
        ),
    ]

    result = service.get_sales_summary(
        date(2026, 8, 1),
        date(2026, 8, 31),
    )

    assert result["number_of_sales"] == 3
    assert result["total_sales"] == Decimal("100000.00")
    assert result["total_paid"] == Decimal("65000.00")
    assert result["total_credit"] == Decimal("35000.00")


def test_get_sales_summary_with_no_sales():
    service, sales_repository, _ = create_service()

    sales_repository.get_sales_between_dates.return_value = []

    result = service.get_sales_summary(
        date(2026, 8, 1),
        date(2026, 8, 31),
    )

    assert result["number_of_sales"] == 0
    assert result["total_sales"] == Decimal("0.00")
    assert result["total_paid"] == Decimal("0.00")
    assert result["total_credit"] == Decimal("0.00")


def test_get_sales_summary_uses_correct_date_range():
    service, sales_repository, _ = create_service()

    sales_repository.get_sales_between_dates.return_value = []

    start_date = date(2026, 8, 1)
    end_date = date(2026, 8, 15)

    service.get_sales_summary(
        start_date,
        end_date,
    )

    sales_repository.get_sales_between_dates.assert_called_once_with(
        start_date,
        end_date,
    )


def test_get_purchase_summary():
    service, _, purchase_repository = create_service()

    purchase_repository.get_purchases_between_dates.return_value = [
        SimpleNamespace(
            items=[
                SimpleNamespace(
                    quantity=10,
                    unit_cost=Decimal("1000.00"),
                ),
                SimpleNamespace(
                    quantity=5,
                    unit_cost=Decimal("2000.00"),
                ),
            ]
        ),
        SimpleNamespace(
            items=[
                SimpleNamespace(
                    quantity=20,
                    unit_cost=Decimal("500.00"),
                ),
            ]
        ),
    ]

    result = service.get_purchase_summary(
        date(2026, 8, 1),
        date(2026, 8, 31),
    )

    assert result["number_of_purchases"] == 2
    assert result["total_purchases"] == Decimal("30000.00")


def test_get_purchase_summary_with_no_purchases():
    service, _, purchase_repository = create_service()

    purchase_repository.get_purchases_between_dates.return_value = []

    result = service.get_purchase_summary(
        date(2026, 8, 1),
        date(2026, 8, 31),
    )

    assert result["number_of_purchases"] == 0
    assert result["total_purchases"] == Decimal("0.00")


def test_get_purchase_summary_uses_correct_date_range():
    service, _, purchase_repository = create_service()

    purchase_repository.get_purchases_between_dates.return_value = []

    start_date = date(2026, 8, 1)
    end_date = date(2026, 8, 15)

    service.get_purchase_summary(
        start_date,
        end_date,
    )

    purchase_repository.get_purchases_between_dates.assert_called_once_with(
        start_date,
        end_date,
    )


def test_get_business_summary():
    service, sales_repository, purchase_repository = create_service()

    sales_repository.get_sales_between_dates.return_value = [
        SimpleNamespace(
            total_amount=Decimal("100000.00"),
            amount_paid=Decimal("70000.00"),
            remaining_balance=Decimal("30000.00"),
        ),
    ]

    purchase_repository.get_purchases_between_dates.return_value = [
        SimpleNamespace(
            items=[
                SimpleNamespace(
                    quantity=10,
                    unit_cost=Decimal("5000.00"),
                ),
            ]
        ),
    ]

    result = service.get_business_summary(
        date(2026, 8, 1),
        date(2026, 8, 31),
    )

    assert result["number_of_sales"] == 1
    assert result["total_sales"] == Decimal("100000.00")
    assert result["total_paid"] == Decimal("70000.00")
    assert result["total_credit"] == Decimal("30000.00")

    assert result["number_of_purchases"] == 1
    assert result["total_purchases"] == Decimal("50000.00")


def test_get_business_summary_with_no_data():
    service, sales_repository, purchase_repository = create_service()

    sales_repository.get_sales_between_dates.return_value = []
    purchase_repository.get_purchases_between_dates.return_value = []

    result = service.get_business_summary(
        date(2026, 8, 1),
        date(2026, 8, 31),
    )

    assert result == {
        "number_of_sales": 0,
        "total_sales": Decimal("0.00"),
        "total_paid": Decimal("0.00"),
        "total_credit": Decimal("0.00"),
        "number_of_purchases": 0,
        "total_purchases": Decimal("0.00"),
    }