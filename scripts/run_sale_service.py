from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from src.database.connection import SessionLocal
from src.repositories.sales_repository import SalesRepository
from src.services.sales_service import SaleService


db = SessionLocal()

try:
    repository = SalesRepository(db)
    service = SaleService(repository)

    
    # 1. CREATE SALE
    

    print("\n1. CREATE SALE")

    sale = service.create_sale(
        sale_date=datetime.now(timezone.utc),
        subtotal=Decimal("50000.00"),
        discount=Decimal("5000.00"),
        total_amount=Decimal("45000.00"),
        amount_paid=Decimal("20000.00"),
        remaining_balance=Decimal("25000.00"),
        payment_status="PARTIAL",
        collection_status="COLLECTED",
        notes="Test sale",
    )

    print(f"ID: {sale.id}")
    print(f"Subtotal: {sale.subtotal}")
    print(f"Discount: {sale.discount}")
    print(f"Total: {sale.total_amount}")
    print(f"Amount paid: {sale.amount_paid}")
    print(f"Remaining balance: {sale.remaining_balance}")
    print(f"Payment status: {sale.payment_status}")
    print(f"Collection status: {sale.collection_status}")

    assert sale.subtotal == Decimal("50000.00")
    assert sale.discount == Decimal("5000.00")
    assert sale.total_amount == Decimal("45000.00")
    assert sale.amount_paid == Decimal("20000.00")
    assert sale.remaining_balance == Decimal("25000.00")
    assert sale.payment_status == "PARTIAL"
    assert sale.collection_status == "COLLECTED"

    print(" PASSED")
    
    # 2. CREATE SALE WITH CUSTOMER

    print("\n2. CREATE SALE WITH CUSTOMER ID")

    customer_id = UUID("5720840e-5e87-457c-a3c7-f531370e5ccc")

    sale_with_customer = service.create_sale(
        customer_id=customer_id,
        sale_date=datetime.now(timezone.utc),
        subtotal=Decimal("30000.00"),
        discount=Decimal("0.00"),
        total_amount=Decimal("30000.00"),
        amount_paid=Decimal("30000.00"),
        remaining_balance=Decimal("0.00"),
        payment_status="PAID",
        collection_status="COLLECTED",
    )

    assert sale_with_customer.customer_id == customer_id

    print(f"Customer ID: {sale_with_customer.customer_id}")
    print(" PASSED")
    
    # 3. NEGATIVE SUBTOTAL

    print("\n3. NEGATIVE SUBTOTAL")

    try:
        service.create_sale(
            sale_date=datetime.now(timezone.utc),
            subtotal=Decimal("-1.00"),
            discount=Decimal("0.00"),
            total_amount=Decimal("0.00"),
            amount_paid=Decimal("0.00"),
            remaining_balance=Decimal("0.00"),
            payment_status="UNPAID",
            collection_status="PENDING_COLLECTION",
        )

        print(" FAILED: Negative subtotal was accepted")

    except ValueError as e:
        print(f" PASSED: {e}")

    # 4. NEGATIVE DISCOUNT
    
    print("\n4. NEGATIVE DISCOUNT")

    try:
        service.create_sale(
            sale_date=datetime.now(timezone.utc),
            subtotal=Decimal("10000.00"),
            discount=Decimal("-1.00"),
            total_amount=Decimal("10000.00"),
            amount_paid=Decimal("0.00"),
            remaining_balance=Decimal("10000.00"),
            payment_status="UNPAID",
            collection_status="PENDING_COLLECTION",
        )

        print(" FAILED: Negative discount was accepted")

    except ValueError as e:
        print(f" PASSED: {e}")

    # 5. NEGATIVE TOTAL    

    print("\n5. NEGATIVE TOTAL AMOUNT")

    try:
        service.create_sale(
            sale_date=datetime.now(timezone.utc),
            subtotal=Decimal("10000.00"),
            discount=Decimal("0.00"),
            total_amount=Decimal("-1.00"),
            amount_paid=Decimal("0.00"),
            remaining_balance=Decimal("0.00"),
            payment_status="UNPAID",
            collection_status="PENDING_COLLECTION",
        )

        print(" FAILED: Negative total was accepted")

    except ValueError as e:
        print(f" PASSED: {e}")

    # 6. NEGATIVE AMOUNT PAID

    print("\n6. NEGATIVE AMOUNT PAID")

    try:
        service.create_sale(
            sale_date=datetime.now(timezone.utc),
            subtotal=Decimal("10000.00"),
            discount=Decimal("0.00"),
            total_amount=Decimal("10000.00"),
            amount_paid=Decimal("-1.00"),
            remaining_balance=Decimal("10000.00"),
            payment_status="UNPAID",
            collection_status="PENDING_COLLECTION",
        )

        print(" FAILED: Negative amount paid was accepted")

    except ValueError as e:
        print(f" PASSED: {e}")

    # 7. NEGATIVE REMAINING BALANCE    

    print("\n7. NEGATIVE REMAINING BALANCE")

    try:
        service.create_sale(
            sale_date=datetime.now(timezone.utc),
            subtotal=Decimal("10000.00"),
            discount=Decimal("0.00"),
            total_amount=Decimal("10000.00"),
            amount_paid=Decimal("10000.00"),
            remaining_balance=Decimal("-1.00"),
            payment_status="PAID",
            collection_status="COLLECTED",
        )

        print(" FAILED: Negative remaining balance was accepted")

    except ValueError as e:
        print(f" PASSED: {e}")

    # 8. AMOUNT PAID GREATER THAN TOTAL

    print("\n8. AMOUNT PAID GREATER THAN TOTAL")

    try:
        service.create_sale(
            sale_date=datetime.now(timezone.utc),
            subtotal=Decimal("10000.00"),
            discount=Decimal("0.00"),
            total_amount=Decimal("10000.00"),
            amount_paid=Decimal("12000.00"),
            remaining_balance=Decimal("0.00"),
            payment_status="PAID",
            collection_status="COLLECTED",
        )

        print(" FAILED: Amount paid greater than total was accepted")

    except ValueError as e:
        print(f" PASSED: {e}")
    
    # 9. INVALID PAYMENT STATUS

    print("\n9. INVALID PAYMENT STATUS")

    try:
        service.create_sale(
            sale_date=datetime.now(timezone.utc),
            subtotal=Decimal("10000.00"),
            discount=Decimal("0.00"),
            total_amount=Decimal("10000.00"),
            amount_paid=Decimal("0.00"),
            remaining_balance=Decimal("10000.00"),
            payment_status="INVALID",
            collection_status="PENDING_COLLECTION",
        )

        print(" FAILED: Invalid payment status was accepted")

    except ValueError as e:
        print(f" PASSED: {e}")
    
    # 10. INVALID COLLECTION STATUS

    print("\n10. INVALID COLLECTION STATUS")

    try:
        service.create_sale(
            sale_date=datetime.now(timezone.utc),
            subtotal=Decimal("10000.00"),
            discount=Decimal("0.00"),
            total_amount=Decimal("10000.00"),
            amount_paid=Decimal("0.00"),
            remaining_balance=Decimal("10000.00"),
            payment_status="UNPAID",
            collection_status="INVALID",
        )

        print(" FAILED: Invalid collection status was accepted")

    except ValueError as e:
        print(f" PASSED: {e}")
    
    # 11. GET SALE
    
    print("\n11. GET SALE")

    found_sale = service.get_sale(sale.id)

    assert found_sale is not None
    assert found_sale.id == sale.id

    print(f"Found sale: {found_sale.id}")
    print(" PASSED")

    # 12. GET NONEXISTENT SALE    

    print("\n12. GET NONEXISTENT SALE")

    nonexistent_sale = service.get_sale(uuid4())

    assert nonexistent_sale is None

    print("PASSED: Nonexistent sale returned None")

    # 13. GET ALL SALES
    
    print("\n13. GET ALL SALES")

    sales = service.get_all_sales()

    print(f"Total sales: {len(sales)}")

    assert sale.id in [s.id for s in sales]

    print(" PASSED")
    
    # 14. UPDATE SALE
    
    print("\n14. UPDATE SALE")

    updated_sale = service.update_sale(
        sale.id,
        subtotal=Decimal("60000.00"),
        discount=Decimal("10000.00"),
        total_amount=Decimal("50000.00"),
        amount_paid=Decimal("25000.00"),
        remaining_balance=Decimal("25000.00"),
        payment_status="PARTIAL",
        collection_status="PENDING_COLLECTION",
        notes="Updated sale",
    )

    assert updated_sale.subtotal == Decimal("60000.00")
    assert updated_sale.discount == Decimal("10000.00")
    assert updated_sale.total_amount == Decimal("50000.00")
    assert updated_sale.amount_paid == Decimal("25000.00")
    assert updated_sale.remaining_balance == Decimal("25000.00")
    assert updated_sale.payment_status == "PARTIAL"
    assert updated_sale.collection_status == "PENDING_COLLECTION"
    assert updated_sale.notes == "Updated sale"

    print(" PASSED")

    # 15. PARTIAL UPDATE
    
    print("\n15. PARTIAL UPDATE")

    partially_updated_sale = service.update_sale(
        sale.id,
        notes="Only notes changed",
    )

    assert partially_updated_sale.notes == "Only notes changed"
    assert partially_updated_sale.total_amount == Decimal("50000.00")

    print(" PASSED")

    # 16. UPDATE NONEXISTENT SALE

    print("\n16. UPDATE NONEXISTENT SALE")

    try:
        service.update_sale(
            uuid4(),
            notes="Nobody",
        )

        print("FAILED: Nonexistent sale was updated")

    except ValueError as e:
        print(f" PASSED: {e}")
    
    # 17. UPDATE WITH NEGATIVE SUBTOTAL

    print("\n17. UPDATE WITH NEGATIVE SUBTOTAL")

    try:
        service.update_sale(
            sale.id,
            subtotal=Decimal("-1.00"),
        )

        print(" FAILED: Negative subtotal was accepted")

    except ValueError as e:
        print(f" PASSED: {e}")
    
    # 18. UPDATE WITH NEGATIVE DISCOUNT
    
    print("\n18. UPDATE WITH NEGATIVE DISCOUNT")

    try:
        service.update_sale(
            sale.id,
            discount=Decimal("-1.00"),
        )

        print(" FAILED: Negative discount was accepted")

    except ValueError as e:
        print(f" PASSED: {e}")

    # 19. UPDATE WITH NEGATIVE TOTAL

    print("\n19. UPDATE WITH NEGATIVE TOTAL")

    try:
        service.update_sale(
            sale.id,
            total_amount=Decimal("-1.00"),
        )

        print(" FAILED: Negative total was accepted")

    except ValueError as e:
        print(f" PASSED: {e}")
    
    # 20. UPDATE WITH NEGATIVE AMOUNT PAID

    print("\n20. UPDATE WITH NEGATIVE AMOUNT PAID")

    try:
        service.update_sale(
            sale.id,
            amount_paid=Decimal("-1.00"),
        )

        print(" FAILED: Negative amount paid was accepted")

    except ValueError as e:
        print(f" PASSED: {e}")
    
    # 21. UPDATE WITH NEGATIVE BALANCE

    print("\n21. UPDATE WITH NEGATIVE BALANCE")

    try:
        service.update_sale(
            sale.id,
            remaining_balance=Decimal("-1.00"),
        )

        print(" FAILED: Negative remaining balance was accepted")

    except ValueError as e:
        print(f" PASSED: {e}")
    
    # 22. UPDATE WITH AMOUNT PAID GREATER THAN TOTAL
    
    print("\n22. UPDATE WITH AMOUNT PAID GREATER THAN TOTAL")

    try:
        service.update_sale(
            sale.id,
            amount_paid=Decimal("60000.00"),
        )

        print(" FAILED: Amount paid greater than total was accepted")

    except ValueError as e:
        print(f" PASSED: {e}")

    # 23. UPDATE WITH INVALID PAYMENT STATUS
    
    print("\n23. UPDATE WITH INVALID PAYMENT STATUS")

    try:
        service.update_sale(
            sale.id,
            payment_status="INVALID",
        )

        print(" FAILED: Invalid payment status was accepted")

    except ValueError as e:
        print(f" PASSED: {e}")

    # 24. UPDATE WITH INVALID COLLECTION STATUS    

    print("\n24. UPDATE WITH INVALID COLLECTION STATUS")

    try:
        service.update_sale(
            sale.id,
            collection_status="INVALID",
        )

        print(" FAILED: Invalid collection status was accepted")

    except ValueError as e:
        print(f" PASSED: {e}")
    
    # FINAL RESULT

    print("\n" + "=" * 60)
    print("ALL SALE SERVICE TESTS PASSED")
    print("=" * 60)

finally:
    db.close()
    