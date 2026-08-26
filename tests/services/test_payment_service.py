import pytest
from decimal import Decimal
from datetime import datetime, timezone
from uuid import uuid4

from src.repositories.payment_repository import PaymentRepository
from src.repositories.sales_repository import SalesRepository
from src.services.payment_service import PaymentService
from src.services.sales_service import SaleService


def create_services(db_session):
    payment_repository = PaymentRepository(db_session)
    sales_repository = SalesRepository(db_session)

    payment_service = PaymentService(
        payment_repository=payment_repository,
        sales_repository=sales_repository,
    )

    sale_service = SaleService(sales_repository)

    return payment_service, sale_service


def create_sale(sale_service):
    return sale_service.create_sale(
        sale_date=datetime.now(timezone.utc),
        subtotal=Decimal("50000.00"),
        discount=Decimal("0.00"),
        total_amount=Decimal("50000.00"),
        amount_paid=Decimal("0.00"),
        remaining_balance=Decimal("50000.00"),
        payment_status="UNPAID",
        collection_status="COLLECTED",
    )


def create_partial_sale(sale_service):
    return sale_service.create_sale(
        sale_date=datetime.now(timezone.utc),
        subtotal=Decimal("50000.00"),
        discount=Decimal("0.00"),
        total_amount=Decimal("50000.00"),
        amount_paid=Decimal("20000.00"),
        remaining_balance=Decimal("30000.00"),
        payment_status="PARTIAL",
        collection_status="COLLECTED",
    )


def test_create_payment(db_session):
    payment_service, sale_service = create_services(db_session)

    sale = create_sale(sale_service)

    payment = payment_service.create_payment(
        sale_id=sale.id,
        amount=Decimal("10000.00"),
        payment_method="Cash",
        payment_date=datetime.now(timezone.utc),
    )

    assert payment.id is not None
    assert payment.sale_id == sale.id
    assert payment.amount == Decimal("10000.00")
    assert payment.payment_method == "Cash"


def test_create_payment_updates_sale_amount_paid(db_session):
    payment_service, sale_service = create_services(db_session)

    sale = create_sale(sale_service)

    payment_service.create_payment(
        sale_id=sale.id,
        amount=Decimal("10000.00"),
        payment_method="Cash",
        payment_date=datetime.now(timezone.utc),
    )

    updated_sale = sale_service.get_sale(sale.id)

    assert updated_sale.amount_paid == Decimal("10000.00")


def test_create_payment_updates_remaining_balance(db_session):
    payment_service, sale_service = create_services(db_session)

    sale = create_sale(sale_service)

    payment_service.create_payment(
        sale_id=sale.id,
        amount=Decimal("10000.00"),
        payment_method="Cash",
        payment_date=datetime.now(timezone.utc),
    )

    updated_sale = sale_service.get_sale(sale.id)

    assert updated_sale.remaining_balance == Decimal("40000.00")


def test_create_payment_sets_partial_status(db_session):
    payment_service, sale_service = create_services(db_session)

    sale = create_sale(sale_service)

    payment_service.create_payment(
        sale_id=sale.id,
        amount=Decimal("10000.00"),
        payment_method="Cash",
        payment_date=datetime.now(timezone.utc),
    )

    updated_sale = sale_service.get_sale(sale.id)

    assert updated_sale.payment_status == "PARTIAL"


def test_create_payment_sets_paid_status_when_fully_paid(db_session):
    payment_service, sale_service = create_services(db_session)

    sale = create_sale(sale_service)

    payment_service.create_payment(
        sale_id=sale.id,
        amount=Decimal("50000.00"),
        payment_method="Cash",
        payment_date=datetime.now(timezone.utc),
    )

    updated_sale = sale_service.get_sale(sale.id)

    assert updated_sale.amount_paid == Decimal("50000.00")
    assert updated_sale.remaining_balance == Decimal("0.00")
    assert updated_sale.payment_status == "PAID"


def test_create_payment_adds_to_existing_amount_paid(db_session):
    payment_service, sale_service = create_services(db_session)

    sale = create_partial_sale(sale_service)

    payment_service.create_payment(
        sale_id=sale.id,
        amount=Decimal("10000.00"),
        payment_method="Cash",
        payment_date=datetime.now(timezone.utc),
    )

    updated_sale = sale_service.get_sale(sale.id)

    assert updated_sale.amount_paid == Decimal("30000.00")
    assert updated_sale.remaining_balance == Decimal("20000.00")
    assert updated_sale.payment_status == "PARTIAL"


def test_create_payment_strips_payment_method_whitespace(db_session):
    payment_service, sale_service = create_services(db_session)

    sale = create_sale(sale_service)

    payment = payment_service.create_payment(
        sale_id=sale.id,
        amount=Decimal("10000.00"),
        payment_method="  Cash  ",
        payment_date=datetime.now(timezone.utc),
    )

    assert payment.payment_method == "Cash"


def test_create_payment_stores_reference_and_notes(db_session):
    payment_service, sale_service = create_services(db_session)

    sale = create_sale(sale_service)

    payment = payment_service.create_payment(
        sale_id=sale.id,
        amount=Decimal("10000.00"),
        payment_method="Transfer",
        payment_date=datetime.now(timezone.utc),
        reference="TEST-001",
        notes="Test payment",
    )

    assert payment.reference == "TEST-001"
    assert payment.notes == "Test payment"


@pytest.mark.parametrize(
    "amount",
    [
        Decimal("0.00"),
        Decimal("-1.00"),
        Decimal("-100.00"),
    ],
)
def test_create_payment_rejects_non_positive_amount(
    db_session,
    amount,
):
    payment_service, sale_service = create_services(db_session)

    sale = create_sale(sale_service)

    with pytest.raises(
        ValueError,
        match="Payment amount must be greater than zero",
    ):
        payment_service.create_payment(
            sale_id=sale.id,
            amount=amount,
            payment_method="Cash",
            payment_date=datetime.now(timezone.utc),
        )


@pytest.mark.parametrize(
    "payment_method",
    [
        "",
        " ",
        "   ",
    ],
)
def test_create_payment_rejects_empty_payment_method(
    db_session,
    payment_method,
):
    payment_service, sale_service = create_services(db_session)

    sale = create_sale(sale_service)

    with pytest.raises(
        ValueError,
        match="Payment method is required",
    ):
        payment_service.create_payment(
            sale_id=sale.id,
            amount=Decimal("10000.00"),
            payment_method=payment_method,
            payment_date=datetime.now(timezone.utc),
        )


def test_create_payment_rejects_nonexistent_sale(db_session):
    payment_service, _ = create_services(db_session)

    sale_id = uuid4()

    with pytest.raises(
        ValueError,
        match=f"Sale with ID {sale_id} does not exist.",
    ):
        payment_service.create_payment(
            sale_id=sale_id,
            amount=Decimal("10000.00"),
            payment_method="Cash",
            payment_date=datetime.now(timezone.utc),
        )


def test_create_payment_rejects_payment_exceeding_remaining_balance(
    db_session,
):
    payment_service, sale_service = create_services(db_session)

    sale = create_partial_sale(sale_service)

    with pytest.raises(
        ValueError,
        match="Payment amount would exceed the sale's remaining balance.",
    ):
        payment_service.create_payment(
            sale_id=sale.id,
            amount=Decimal("30000.01"),
            payment_method="Cash",
            payment_date=datetime.now(timezone.utc),
        )


def test_get_payment(db_session):
    payment_service, sale_service = create_services(db_session)

    sale = create_sale(sale_service)

    payment = payment_service.create_payment(
        sale_id=sale.id,
        amount=Decimal("10000.00"),
        payment_method="Cash",
        payment_date=datetime.now(timezone.utc),
    )

    retrieved = payment_service.get_payment(payment.id)

    assert retrieved is not None
    assert retrieved.id == payment.id
    assert retrieved.sale_id == sale.id
    assert retrieved.amount == Decimal("10000.00")


def test_get_payment_returns_none_for_nonexistent_payment(db_session):
    payment_service, _ = create_services(db_session)

    retrieved = payment_service.get_payment(uuid4())

    assert retrieved is None


def test_get_all_payment(db_session):
    payment_service, sale_service = create_services(db_session)

    sale = create_sale(sale_service)

    first_payment = payment_service.create_payment(
        sale_id=sale.id,
        amount=Decimal("10000.00"),
        payment_method="Cash",
        payment_date=datetime.now(timezone.utc),
    )

    second_payment = payment_service.create_payment(
        sale_id=sale.id,
        amount=Decimal("5000.00"),
        payment_method="Transfer",
        payment_date=datetime.now(timezone.utc),
    )

    payments = payment_service.get_all_payment()

    payment_ids = {payment.id for payment in payments}

    assert first_payment.id in payment_ids
    assert second_payment.id in payment_ids