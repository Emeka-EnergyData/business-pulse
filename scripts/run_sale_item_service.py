from decimal import Decimal
from uuid import UUID, uuid4

from src.database.connection import SessionLocal

from src.repositories.sale_item_repository import SaleItemRepository
from src.repositories.sales_repository import SalesRepository
from src.repositories.product_repository import ProductRepository
from src.repositories.stock_movement_repository import StockMovementRepository

from src.services.sale_item_services import SaleItemService


db = SessionLocal()

try:
    # REPOSITORIES

    sale_item_repository = SaleItemRepository(db)
    sales_repository = SalesRepository(db)
    product_repository = ProductRepository(db)
    stock_movement_repository = StockMovementRepository(db)

    # SERVICE

    service = SaleItemService(
        sale_item_repository=sale_item_repository,
        product_repository=product_repository,
        stock_movement_repository=stock_movement_repository,
        sales_repository=sales_repository
    )

    # GET EXISTING SALE

    print("\nGetting existing sale...")

    sales = sales_repository.get_all()

    if not sales:
        raise RuntimeError(
            "No sales exist in the database. "
            "Create a sale before running this test."
        )

    sale = sales[0]

    print(f"Using sale: {sale.id}")


    # GET EXISTING ACTIVE PRODUCT WITH STOCK

    print("\nGetting existing product...")

    products = product_repository.get_active()

    product = None

    for p in products:
        if p.current_stock > 0:
            product = p
            break

    if product is None:
        raise RuntimeError(
            "No active product with stock available. "
            "Add stock before running this test."
        )

    print(f"Using product: {product.id}")
    print(f"Product: {product.name}")
    print(f"Current stock: {product.current_stock}")
    print(f"Cost price: {product.cost_price}")


    # SAVE ORIGINAL STOCK

    original_stock = product.current_stock


    # 1. CREATE SALE ITEM

    print("\n1. CREATE SALE ITEM")

    quantity = 1
    unit_price = Decimal("15000.00")

    sale_item = service.create_sale_item(
        sale_id=sale.id,
        product_id=product.id,
        quantity=quantity,
        unit_price=unit_price,
    )

    print(f"Sale item ID: {sale_item.id}")
    print(f"Product ID: {sale_item.product_id}")
    print(f"Quantity: {sale_item.quantity}")
    print(f"Unit price: {sale_item.unit_price}")
    print(f"Cost price: {sale_item.cost_price}")
    print(f"Line total: {sale_item.line_total}")

    assert sale_item.sale_id == sale.id
    assert sale_item.product_id == product.id
    assert sale_item.quantity == quantity
    assert sale_item.unit_price == unit_price
    assert sale_item.cost_price == product.cost_price
    assert sale_item.line_total == unit_price * quantity

    print("PASSED")


    # 2. VERIFY STOCK DECREASED

    print("\n2. VERIFY STOCK DECREASE")

    updated_product = product_repository.get_by_id(product.id)

    expected_stock = original_stock - quantity

    assert updated_product.current_stock == expected_stock

    print(f"Original stock: {original_stock}")
    print(f"New stock: {updated_product.current_stock}")
    print("PASSED")


    # 3. VERIFY STOCK MOVEMENT

    print("\n3. VERIFY STOCK MOVEMENT")

    movements = stock_movement_repository.get_all()

    matching_movement = None

    for movement in movements:
        if (
            movement.product_id == product.id
            and movement.reference_id == sale.id
            and movement.movement_type == "SOLD"
        ):
            matching_movement = movement
            break

    assert matching_movement is not None
    assert matching_movement.quantity == quantity
    assert matching_movement.reference_type == "Sale"

    print(f"Movement ID: {matching_movement.id}")
    print(f"Movement type: {matching_movement.movement_type}")
    print(f"Quantity: {matching_movement.quantity}")
    print(f"Reference type: {matching_movement.reference_type}")
    print(f"Reference ID: {matching_movement.reference_id}")
    print("PASSED")


    # 4. GET SALE ITEM

    print("\n4. GET SALE ITEM")

    found_item = service.get_sale_item(sale_item.id)

    assert found_item is not None
    assert found_item.id == sale_item.id

    print(f"Found sale item: {found_item.id}")
    print("PASSED")


    # 5. GET NONEXISTENT SALE ITEM

    print("\n5. GET NONEXISTENT SALE ITEM")

    nonexistent_item = service.get_sale_item(uuid4())

    assert nonexistent_item is None

    print("PASSED")


    # 6. GET ALL SALE ITEMS

    print("\n6. GET ALL SALE ITEMS")

    all_items = service.get_all_sale_items()

    assert sale_item.id in [item.id for item in all_items]

    print(f"Total sale items: {len(all_items)}")
    print("PASSED")


    # 7. QUANTITY MUST BE POSITIVE

    print("\n7. QUANTITY MUST BE POSITIVE")

    try:
        service.create_sale_item(
            sale_id=sale.id,
            product_id=product.id,
            quantity=0,
            unit_price=Decimal("10000.00"),
        )

        print("FAILED: Zero quantity was accepted")

    except ValueError as e:
        print(f"PASSED: {e}")


    # 8. NEGATIVE QUANTITY

    print("\n8. NEGATIVE QUANTITY")

    try:
        service.create_sale_item(
            sale_id=sale.id,
            product_id=product.id,
            quantity=-1,
            unit_price=Decimal("10000.00"),
        )

        print("FAILED: Negative quantity was accepted")

    except ValueError as e:
        print(f"PASSED: {e}")


    # 9. NEGATIVE UNIT PRICE

    print("\n9. NEGATIVE UNIT PRICE")

    try:
        service.create_sale_item(
            sale_id=sale.id,
            product_id=product.id,
            quantity=1,
            unit_price=Decimal("-100.00"),
        )

        print("FAILED: Negative unit price was accepted")

    except ValueError as e:
        print(f"PASSED: {e}")


    # 10. PRODUCT MUST EXIST

    print("\n10. PRODUCT MUST EXIST")

    try:
        service.create_sale_item(
            sale_id=sale.id,
            product_id=uuid4(),
            quantity=1,
            unit_price=Decimal("10000.00"),
        )

        print("FAILED: Nonexistent product was accepted")

    except ValueError as e:
        print(f"PASSED: {e}")


    # 11. SALE MUST EXIST

    print("\n11. SALE MUST EXIST")

    try:
        service.create_sale_item(
            sale_id=uuid4(),
            product_id=product.id,
            quantity=1,
            unit_price=Decimal("10000.00"),
        )

        print("FAILED: Nonexistent sale was accepted")

    except ValueError as e:
        print(f"PASSED: {e}")


    # 12. INSUFFICIENT STOCK

    print("\n12. INSUFFICIENT STOCK")

    current_product = product_repository.get_by_id(product.id)

    try:
        service.create_sale_item(
            sale_id=sale.id,
            product_id=product.id,
            quantity=current_product.current_stock + 1,
            unit_price=Decimal("10000.00"),
        )

        print("FAILED: Insufficient stock was accepted")

    except ValueError as e:
        print(f"PASSED: {e}")


    # 13. GET INACTIVE PRODUCT

    print("\n13. INACTIVE PRODUCT")

    inactive_product = None

    for p in product_repository.get_all():
        if not p.is_active:
            inactive_product = p
            break

    if inactive_product is None:
        print("SKIPPED: No inactive product exists")

    else:
        try:
            service.create_sale_item(
                sale_id=sale.id,
                product_id=inactive_product.id,
                quantity=1,
                unit_price=Decimal("10000.00"),
            )

            print("FAILED: Inactive product was accepted")

        except ValueError as e:
            print(f"PASSED: {e}")


    # FINAL RESULT

    print("\n" + "=" * 60)
    print("ALL SALE ITEM SERVICE TESTS PASSED")
    print("=" * 60)


finally:
    db.close()