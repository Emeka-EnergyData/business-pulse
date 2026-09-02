from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4
import pytest
from src.repositories.categories_repository import CategoryRepository
from src.repositories.product_repository import ProductRepository
from src.repositories.sale_item_repository import SaleItemRepository
from src.repositories.sales_repository import SalesRepository
from src.repositories.stock_movement_repository import StockMovementRepository
from src.services.category_services import CategoryService
from src.services.product_service import ProductService
from src.services.sales_service import SaleService
from src.services.sale_item_services import SaleItemService

def create_services(db_session):
    category_repository = CategoryRepository(db_session)
    product_repository = ProductRepository(db_session)
    sales_repository = SalesRepository(db_session)
    sale_item_repository = SaleItemRepository(db_session)
    stock_movement_repository = StockMovementRepository(db_session)
    
    category_service = CategoryService(category_repository)
    product_service = ProductService(product_repository)
    sale_service = SaleService(sales_repository)    
    sale_item_service = SaleItemService(
        sale_item_repository=sale_item_repository,
        product_repository=product_repository,
        stock_movement_repository=stock_movement_repository,
        sales_repository=sales_repository
        )
    
    return (
        category_service,
        product_service,
        sale_service,
        sale_item_service,
        product_repository,
        stock_movement_repository
        )

def create_category(category_service):
    return category_service.create_category(
        name=f"Test Category {uuid4()}",
        description="Category created for sale item testing"
        )

def create_product(product_service, category_id):
    return product_service.create_product(
        category_id=category_id,
        name=f"Test Product {uuid4()}",
        cost_price=Decimal("10000.00"),
        target_price=Decimal("15000.00"),
        minimum_price=Decimal("12000.00"),
        description="Test product"
        )

def create_sale(sale_service):
    return sale_service.create_sale(
        sale_date=datetime.now(timezone.utc),
        subtotal=Decimal("30000.00"),
        discount=Decimal("0.00"),
        total_amount=Decimal("30000.00"),
        amount_paid=Decimal("30000.00"),
        remaining_balance=Decimal("0.00"),
        payment_status="PAID",
        collection_status="COLLECTED"
        )

def prepare_sale_item_test(db_session, stock=10):
    (
        category_service,
        product_service,
        sale_service,
        sale_item_service,
        product_repository,
        stock_movement_repository
    ) = create_services(db_session)
    
    category = create_category(category_service)
    product = create_product(product_service, category.id)
    sale = create_sale(sale_service)
    
    product_repository.increase_stock(product.id, stock)
    db_session.commit()
    
    return (
        sale_item_service,
        product_repository,
        stock_movement_repository,
        product,
        sale
        )


def test_create_sale_item(db_session):
    (
        sale_item_service,
        product_repository,
        stock_movement_repository,
        product,
        sale
        ) = prepare_sale_item_test(db_session)
    
    sale_item = sale_item_service.create_sale_item(
        sale_id=sale.id,
        product_id=product.id,
        quantity=2,
        unit_price=Decimal("15000.00")
        )
    
    assert sale_item.id is not None
    assert sale_item.sale_id == sale.id
    assert sale_item.product_id == product.id
    assert sale_item.quantity == 2
    assert sale_item.unit_price == Decimal("15000.00")
    assert sale_item.cost_price == Decimal("10000.00")
    assert sale_item.line_total == Decimal("30000.00")

def test_create_sale_item_calculates_line_total(db_session):
    (
        sale_item_service,
        _,
        _,
        product,
        sale
        ) = prepare_sale_item_test(db_session)
    
    sale_item = sale_item_service.create_sale_item(
        sale_id=sale.id,
        product_id=product.id,
        quantity=4,
        unit_price=Decimal("12500.00")
        )
    
    assert sale_item.line_total == Decimal("50000.00")

def test_create_sale_item_captures_current_cost_price(db_session):
    (
        sale_item_service,
        _,
        _,
        product,
        sale
        ) = prepare_sale_item_test(db_session)
    
    sale_item = sale_item_service.create_sale_item(
        sale_id=sale.id,
        product_id=product.id,
        quantity=2,
        unit_price=Decimal("15000.00")
        )
    
    assert sale_item.cost_price == product.cost_price

def test_create_sale_item_decreases_stock(db_session):
    (
        sale_item_service,
        product_repository,
        _,
        product,
        sale
        ) = prepare_sale_item_test(db_session, stock=10)
    
    sale_item_service.create_sale_item(
        sale_id=sale.id,
        product_id=product.id,
        quantity=3,
        unit_price=Decimal("15000.00")
        )
    
    updated_product = product_repository.get_by_id(product.id)
    
    assert updated_product.current_stock == 7

def test_create_sale_item_creates_sold_stock_movement(db_session):
    (
        sale_item_service,
        _,
        stock_movement_repository,
        product,
        sale
        ) = prepare_sale_item_test(db_session)
    
    sale_item_service.create_sale_item(
        sale_id=sale.id,
        product_id=product.id,
        quantity=3,
        unit_price=Decimal("15000.00")
        )
    
    movements = stock_movement_repository.get_all()
    matching_movements = [
        movement
        for movement in movements
        if movement.product_id == product.id
        and movement.movement_type == "SOLD"
        and movement.reference_id == sale.id
        ]
    
    assert len(matching_movements) == 1
    movement = matching_movements[0]
    assert movement.quantity == 3
    assert movement.reference_type == "Sale"
    assert movement.movement_date == sale.sale_date

def test_get_sale_item(db_session):
    (
        sale_item_service,
        _,
        _,
        product,
        sale
        ) = prepare_sale_item_test(db_session)
    
    sale_item = sale_item_service.create_sale_item(
        sale_id=sale.id,
        product_id=product.id,
        quantity=2,
        unit_price=Decimal("15000.00")
        )
    
    retrieved = sale_item_service.get_sale_item(sale_item.id)
    
    assert retrieved is not None
    assert retrieved.id == sale_item.id
    assert retrieved.sale_id == sale.id
    assert retrieved.product_id == product.id

def test_get_sale_item_returns_none_for_nonexistent_sale_item(db_session):
    (
        sale_item_service,
        _,
        _,
        _,
        _
        ) = prepare_sale_item_test(db_session)
    
    retrieved = sale_item_service.get_sale_item(uuid4())
    
    assert retrieved is None

def test_get_all_sale_items(db_session):
    (
        sale_item_service,
        _,
        _,
        product,
        sale
        ) = prepare_sale_item_test(db_session)
    
    first = sale_item_service.create_sale_item(
        sale_id=sale.id,
        product_id=product.id,
        quantity=2,
        unit_price=Decimal("15000.00")
        )
    
    second = sale_item_service.create_sale_item(
        sale_id=sale.id,
        product_id=product.id,
        quantity=1,
        unit_price=Decimal("14000.00")
        )
    
    sale_items = sale_item_service.get_all_sale_items()
    sale_item_ids = {item.id for item in sale_items}
    
    assert first.id in sale_item_ids
    assert second.id in sale_item_ids

def test_create_sale_item_rejects_zero_quantity(db_session):
    (
        sale_item_service,
        _,
        _,
        product,
        sale
        ) = prepare_sale_item_test(db_session)
    
    with pytest.raises(
        ValueError,
        match="Quantity must be greater than zero."
        ):
        sale_item_service.create_sale_item(
            sale_id=sale.id,
            product_id=product.id,
            quantity=0,
            unit_price=Decimal("15000.00")
            )

def test_create_sale_item_rejects_negative_quantity(db_session):
    (
        sale_item_service,
        _,
        _,
        product,
        sale
        ) = prepare_sale_item_test(db_session)
    
    with pytest.raises(
        ValueError,
        match="Quantity must be greater than zero."
        ):
        
        sale_item_service.create_sale_item(
            sale_id=sale.id,
            product_id=product.id,
            quantity=-1,
            unit_price=Decimal("15000.00")
            )

def test_create_sale_item_rejects_negative_unit_price(db_session):
    (
        sale_item_service,
        _,
        _,
        product,
        sale
        ) = prepare_sale_item_test(db_session)
    
    with pytest.raises(
        ValueError,
        match="Unit price must be greater than zero."
        ):
        
        sale_item_service.create_sale_item(
            sale_id=sale.id,
            product_id=product.id,
            quantity=2,
            unit_price=Decimal("0")
            )

def test_create_sale_item_rejects_nonexistent_product(db_session):
    (
        sale_item_service,
        _,
        _,
        _,
        sale
        ) = prepare_sale_item_test(db_session)
    
    product_id = uuid4()
    
    with pytest.raises(
        ValueError,
        match=f"Product with ID {product_id} does not exist"
        ):
        
        sale_item_service.create_sale_item(
            sale_id=sale.id,
            product_id=product_id,
            quantity=2,
            unit_price=Decimal("15000.00")
            )

def test_create_sale_item_rejects_inactive_product(db_session):
    (
        sale_item_service,
        product_repository,
        _,
        product,
        sale
        ) = prepare_sale_item_test(db_session)
    
    product.is_active = False
    product_repository.update(product)
    
    with pytest.raises(
        ValueError,
        match="Cannot sell an inactive product"
        ):
        
        sale_item_service.create_sale_item(
            sale_id=sale.id,
            product_id=product.id,
            quantity=2,
            unit_price=Decimal("15000.00")
            )

def test_create_sale_item_rejects_insufficient_stock(db_session):
    (
        sale_item_service,
        _,
        _,
        product,
        sale
        ) = prepare_sale_item_test(db_session, stock=3)
    
    with pytest.raises(
        ValueError,
        match="Insufficient stock"
        ):
        
        sale_item_service.create_sale_item(
            sale_id=sale.id,
            product_id=product.id,
            quantity=4,
            unit_price=Decimal("15000.00")
            )

def test_create_sale_item_rejects_nonexistent_sale(db_session):
    (
        sale_item_service,
        _,
        _,
        product,
        _,
        ) = prepare_sale_item_test(db_session)
    
    sale_id = uuid4()
    
    with pytest.raises(
        ValueError,
        match=f"Sale with ID {sale_id} does not exist"
        ):
        
        sale_item_service.create_sale_item(
            sale_id=sale_id,
            product_id=product.id,
            quantity=2,
            unit_price=Decimal("15000.00")
            )

def test_failed_sale_item_does_not_reduce_stock(db_session):
    (
        sale_item_service,
        product_repository,
        _,
        product,
        sale
        ) = prepare_sale_item_test(db_session, stock=3)
    
    with pytest.raises(ValueError, match="Insufficient stock"):
        sale_item_service.create_sale_item(
            sale_id=sale.id,
            product_id=product.id,
            quantity=5,
            unit_price=Decimal("15000.00")
            )
        
        updated_product = product_repository.get_by_id(product.id)
        assert updated_product.current_stock == 3

def test_failed_sale_item_does_not_create_stock_movement(db_session):
    (
        sale_item_service,
        _,
        stock_movement_repository,
        product,
        sale,
        ) = prepare_sale_item_test(db_session, stock=3)
    
    with pytest.raises(ValueError, match="Insufficient stock"):
        sale_item_service.create_sale_item(
            sale_id=sale.id,
            product_id=product.id,
            quantity=5,
            unit_price=Decimal("15000.00")
            )
        
        movements = stock_movement_repository.get_all()
        matching_movements = [
            movement
            for movement in movements
            if movement.product_id == product.id
            and movement.reference_id == sale.id
            and movement.movement_type == "SOLD"
            ]
        assert matching_movements == []