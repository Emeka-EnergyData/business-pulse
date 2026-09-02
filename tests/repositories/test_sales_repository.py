from datetime import datetime, timezone
from decimal import Decimal

from src.database.models.sales import Sale
from src.repositories.sales_repository import SalesRepository

def test_get_daily_sales_between_dates(db_session):
    repository = SalesRepository(db_session)

    sale_1 = Sale(
        sale_date=datetime(2026, 8, 28, 10, 0, tzinfo=timezone.utc),
        subtotal=Decimal("10000.00"),
        discount=Decimal("0.00"),
        total_amount=Decimal("10000.00"),
        amount_paid=Decimal("10000.00"),
        remaining_balance=Decimal("0.00"),
        payment_status="PAID",
        collection_status="COLLECTED",
    )

    sale_2 = Sale(
        sale_date=datetime(2026, 8, 28, 15, 0, tzinfo=timezone.utc),
        subtotal=Decimal("15000.00"),
        discount=Decimal("0.00"),
        total_amount=Decimal("15000.00"),
        amount_paid=Decimal("15000.00"),
        remaining_balance=Decimal("0.00"),
        payment_status="PAID",
        collection_status="COLLECTED",
    )

    sale_3 = Sale(
        sale_date=datetime(2026, 8, 29, 11, 0, tzinfo=timezone.utc),
        subtotal=Decimal("20000.00"),
        discount=Decimal("0.00"),
        total_amount=Decimal("20000.00"),
        amount_paid=Decimal("20000.00"),
        remaining_balance=Decimal("0.00"),
        payment_status="PAID",
        collection_status="COLLECTED",
    )

    db_session.add_all([sale_1, sale_2, sale_3])
    db_session.commit()

    results = repository.get_daily_sales_between_dates(
        start_date=datetime(2026, 8, 28).date(),
        end_date=datetime(2026, 8, 29).date(),
    )

    assert len(results) == 2

    assert results[0].sale_day.day == 28
    assert results[0].total_sales == sale_1.total_amount + sale_2.total_amount

    assert results[1].sale_day.day == 29
    assert results[1].total_sales == sale_3.total_amount