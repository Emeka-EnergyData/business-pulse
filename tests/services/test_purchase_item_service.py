import pytest

from decimal import Decimal
from datetime import date
from uuid import uuid4
from src.repositories.categories_repository import CategoryRepository
from src.repositories.product_repository import ProductRepository
from src.repositories.supplier_repository import SupplierRepository
from src.repositories.purchase_repository import PurchaseRepository
from src.repositories.purchase_item_repository import PurchaseItemRepository
from src.repositories.stock_movement_repository import StockMovementRepository
from src.services.category_services import CategoryService
from src.services.product_service import ProductService
from src.services.supplier_service import SupplierService
from src.services.purchase_service import PurchaseService
from src.services.purchase_item_service import PurchaseItemService

def create_purchase_item_service(db_session):
    return PurchaseItemService(
        purchase_item_repository=PurchaseItemRepository(db_session),
        product_repository=ProductRepository(db_session),
        stock_movement_repository=StockMovementRepository(db_session),
        purchase_repository=PurchaseRepository(db_session)
        )

def create_product(db_session):
    category_repository = CategoryRepository(db_session)
    category_service = CategoryService(category_repository)
    
    category = category_service.create_category(
        name=f"Test Category {uuid4()}",
        description="Purchase item test category"
        )
    
    product_repository = ProductRepository(db_session)
    product_service = ProductService(product_repository)

    product = product_service.create_product(
        category_id=category.id,
        name=f"Test Product {uuid4()}",
        cost_price=Decimal("10000.00"),
        target_price=Decimal("15000.00"),
        minimum_price=Decimal("12000.00"),
        description="Purchase item test product")
    return product

def create_purchase(db_session):
    supplier_repository = SupplierRepository(db_session)
    supplier_service = SupplierService(supplier_repository)
        
    supplier = supplier_service.create_supplier(
        name=f"Test Supplier {uuid4()}",
        phone="08012345678",
        address="Lagos",
        notes="Purchase item test supplier")
        
    purchase_repository = PurchaseRepository(db_session)
    purchase_service = PurchaseService(purchase_repository)
    purchase = purchase_service.create_purchase(
        supplier_id=supplier.id,
        purchase_date=date.today(),
        notes="Purchase item test purchase",)
    return purchase

def create_test_data(db_session):
    product = create_product(db_session)
    purchase = create_purchase(db_session)
    service = create_purchase_item_service(db_session)
    return service, purchase, product

def test_create_purchase_item(db_session):
    service, purchase, product = create_test_data(db_session)
    purchase_item = service.create_purchase_item(
        purchase_id=purchase.id,
        product_id=product.id,
        quantity=5,
        unit_cost=Decimal("10500.00")
        )
    assert purchase_item.id is not None
    assert purchase_item.purchase_id == purchase.id
    assert purchase_item.product_id == product.id
    assert purchase_item.quantity == 5
    assert purchase_item.unit_cost == Decimal("10500.00")

def test_create_purchase_item_increases_product_stock(db_session):
    service, purchase, product = create_test_data(db_session)
    
    assert product.current_stock == 0
    
    service.create_purchase_item(
        purchase_id=purchase.id,
        product_id=product.id,
        quantity=5,
        unit_cost=Decimal("10500.00"))
    
    db_session.refresh(product)

    assert product.current_stock == 5

def test_create_purchase_item_creates_stock_movement(db_session):
    service, purchase, product = create_test_data(db_session)
    
    service.create_purchase_item(
        purchase_id=purchase.id,
        product_id=product.id,
        quantity=5,
        unit_cost=Decimal("10500.00")
        )
    stock_movement_repository = StockMovementRepository(db_session)
    
    movements = stock_movement_repository.get_all()
    purchase_movement = next(
        (movement
         for movement in movements
         if movement.reference_id == purchase.id
         and movement.product_id == product.id),
        None,)
    
    assert purchase_movement is not None
    assert purchase_movement.movement_type == "RECEIVED"
    assert purchase_movement.quantity == 5
    assert purchase_movement.reference_type == "Purchase"
    assert purchase_movement.reference_id == purchase.id

def test_get_purchase_item(db_session):
    service, purchase, product = create_test_data(db_session)

    purchase_item = service.create_purchase_item(
        purchase_id=purchase.id,
        product_id=product.id,
        quantity=5,
        unit_cost=Decimal("10500.00")
        )
    retrieved = service.get_purchase_item(purchase_item.id)
    
    assert retrieved is not None
    assert retrieved.id == purchase_item.id
    assert retrieved.purchase_id == purchase.id
    assert retrieved.product_id == product.id
    assert retrieved.quantity == 5

def test_get_all_purchase_items(db_session):
    service, purchase, product = create_test_data(db_session)

    first_item = service.create_purchase_item(
        purchase_id=purchase.id,
        product_id=product.id,
        quantity=5,
        unit_cost=Decimal("10500.00")
        )
    
    second_item = service.create_purchase_item(
        purchase_id=purchase.id,
        product_id=product.id,
        quantity=3,
        unit_cost=Decimal("11000.00")
        )
    
    items = service.get_all_purchase_items()
    item_ids = {item.id for item in items}
    
    assert first_item.id in item_ids
    assert second_item.id in item_ids

def test_create_purchase_item_rejects_zero_quantity(db_session):
    service, purchase, product = create_test_data(db_session)

    with pytest.raises(ValueError,
                       match="Quantity must be greater tahn zero.",):
        service.create_purchase_item(purchase_id=purchase.id,
                                     product_id=product.id,
                                     quantity=0,
                                     unit_cost=Decimal("10500.00")
                                     )

def test_create_purchase_item_rejects_negative_quantity(db_session):
    service, purchase, product = create_test_data(db_session)
    
    with pytest.raises(ValueError,
                       match="Quantity must be greater tahn zero."):
        service.create_purchase_item(purchase_id=purchase.id,
                                     product_id=product.id,
                                     quantity=-5,
                                     unit_cost=Decimal("10500.00")
                                     )

def test_create_purchase_item_rejects_negative_unit_cost(db_session):
    service, purchase, product = create_test_data(db_session)
    
    with pytest.raises(ValueError,match="Unit cost vannot be negative."):
        service.create_purchase_item(purchase_id=purchase.id,
                                     product_id=product.id,
                                     quantity=5,
                                     unit_cost=Decimal("-100.00")
                                     )

def test_create_purchase_item_rejects_nonexistent_product(db_session):
    service, purchase, _ = create_test_data(db_session)
    nonexistent_product_id = uuid4()
    
    with pytest.raises(ValueError,
                       match=f"Product with ID {nonexistent_product_id} does not exist.",):
        service.create_purchase_item(purchase_id=purchase.id,
                                     product_id=nonexistent_product_id,
                                     quantity=5,
                                     unit_cost=Decimal("10500.00")
                                     )

def test_create_purchase_item_rolls_back_on_failure(db_session):
    service, purchase, product = create_test_data(db_session)
    
    original_stock = product.current_stock

    
        
    with pytest.raises(ValueError):
        service.create_purchase_item(purchase_id=purchase.id,
                                     product_id=uuid4(),
                                     quantity=5,
                                     unit_cost=Decimal("10500.00"))
    db_session.refresh(product)
    assert product.current_stock == original_stock
    
    purchase_item_repository = PurchaseItemRepository(db_session)
        
    items_before = purchase_item_repository.get_all()
        
    items_after = purchase_item_repository.get_all()
    
    assert len(items_after) == len(items_before)