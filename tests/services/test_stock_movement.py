from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from src.repositories.stock_movement_repository import StockMovementRepository
from src.services.stock_movement_service import StockMovementService
from src.repositories.product_repository import ProductRepository
from src.repositories.categories_repository import CategoryRepository
from src.services.product_service import ProductService
from src.services.category_services import CategoryService
from src.database.models.stock_movement import StockMovement


def create_services(db_session):
    stock_movement_repository = StockMovementRepository(db_session)

    category_repository = CategoryRepository(db_session)
    product_repository = ProductRepository(db_session)

    category_service = CategoryService(category_repository)
    product_service = ProductService(product_repository)
    stock_movement_service = StockMovementService(stock_movement_repository)

    return (
        category_service,
        product_service,
        stock_movement_service,
    )


def create_product(category_service, product_service):
    category = category_service.create_category(
        name=f"Test Category {uuid4()}",
        description="Category for stock movement testing",
    )

    product = product_service.create_product(
        category_id=category.id,
        name=f"Test Product {uuid4()}",
        cost_price=Decimal("10000.00"),
        target_price=Decimal("15000.00"),
        minimum_price=Decimal("12000.00"),
    )

    return product


def create_stock_movement(db_session, product_id):
    movement = StockMovement(
        product_id=product_id,
        movement_type="RECEIVED",
        quantity=10,
        reference_type="Purchase",
        reference_id=uuid4(),
        movement_date=datetime.now(timezone.utc),
        notes="Test stock movement",
    )

    repository = StockMovementRepository(db_session)

    return repository.create(movement)


def test_get_stock_movement(db_session):
    category_service, product_service, stock_movement_service = create_services(
        db_session
    )

    product = create_product(category_service, product_service)

    movement = create_stock_movement(
        db_session,
        product.id,
    )

    retrieved = stock_movement_service.get_stock_movement(movement.id)

    assert retrieved is not None
    assert retrieved.id == movement.id
    assert retrieved.product_id == product.id
    assert retrieved.movement_type == "RECEIVED"
    assert retrieved.quantity == 10
    assert retrieved.reference_type == "Purchase"
    assert retrieved.reference_id == movement.reference_id


def test_get_stock_movement_returns_none_for_nonexistent_movement(db_session):
    _, _, stock_movement_service = create_services(db_session)

    result = stock_movement_service.get_stock_movement(uuid4())

    assert result is None


def test_get_all_stock_movements(db_session):
    category_service, product_service, stock_movement_service = create_services(
        db_session
    )

    product = create_product(category_service, product_service)

    first = create_stock_movement(
        db_session,
        product.id,
    )

    second = create_stock_movement(
        db_session,
        product.id,
    )

    movements = stock_movement_service.get_all_stock_movement()

    movement_ids = {movement.id for movement in movements}

    assert first.id in movement_ids
    assert second.id in movement_ids