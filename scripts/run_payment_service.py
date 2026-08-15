from decimal import Decimal
from datetime import datetime, timezone

from src.database.connection import SessionLocal
from src.repositories.payment_repository import PaymentRepository
from src.repositories.sales_repository import SalesRepository
from src.services.payment_service import PaymentService


db = SessionLocal()

try:
    # Repositories
    payment_repository = PaymentRepository(db)
    sales_repository = SalesRepository(db)

    # Service
    payment_service = PaymentService(
        payment_repository=payment_repository,
        sales_repository=sales_repository,
    )

    # 1. Get an existing sale

    sales = sales_repository.get_all()

    if not sales:
        raise RuntimeError(
            "No sales found in the database. "
            "Create a sale before testing PaymentService."
        )

    sale = sales[0]

    print("\nExisting sale:")
    print(f"Sale ID: {sale.id}")
    print(f"Total amount: {sale.total_amount}")
    print(f"Amount paid: {sale.amount_paid}")
    print(f"Remaining balance: {sale.remaining_balance}")
    print(f"Payment status: {sale.payment_status}")
    
    old_amount_paid = sale.amount_paid

    # 2. Record a payment

    payment_amount = Decimal("1000.00")

    # Make sure the test payment does not exceed
    # the remaining balance.
    if payment_amount > sale.remaining_balance:
        payment_amount = sale.remaining_balance

    if payment_amount <= 0:
        raise RuntimeError(
            "Selected sale has no remaining balance to test a payment."
        )

    payment = payment_service.create_payment(
        sale_id=sale.id,
        amount=payment_amount,
        payment_method="Cash",
        payment_date=datetime.now(timezone.utc),
        reference="TEST-PAYMENT-001",
        notes="PaymentService test",
    )

    print("\nPayment created successfully:")
    print(f"Payment ID: {payment.id}")
    print(f"Sale ID: {payment.sale_id}")
    print(f"Amount: {payment.amount}")
    print(f"Payment method: {payment.payment_method}")
    print(f"Payment date: {payment.payment_date}")

    # 3. Retrieve the updated sale

    updated_sale = sales_repository.get_by_id(sale.id)

    print("\nUpdated sale:")
    print(f"Total amount: {updated_sale.total_amount}")
    print(f"Amount paid: {updated_sale.amount_paid}")
    print(f"Remaining balance: {updated_sale.remaining_balance}")
    print(f"Payment status: {updated_sale.payment_status}")

    # 4. Verify the calculations

    expected_amount_paid = old_amount_paid + payment_amount
    expected_remaining_balance = (
        sale.total_amount - expected_amount_paid
    )

    assert updated_sale.amount_paid == expected_amount_paid
    assert updated_sale.remaining_balance == expected_remaining_balance

    if expected_remaining_balance == 0:
        assert updated_sale.payment_status == "PAID"
    else:
        assert updated_sale.payment_status == "PARTIAL"

    print("\n✓ PaymentService test passed.")

finally:
    db.close()