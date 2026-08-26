import pytest
from decimal import Decimal
from uuid import uuid4

from src.repositories.categories_repository import CategoryRepository
from src.repositories.product_repository import ProductRepository
from src.services.category_services import CategoryService

from src.services.product_service import ProductService


def create_services(db_session):
    category_repository = CategoryRepository(db_session)
    product_repository = ProductRepository(db_session)

    category_service = CategoryService(category_repository)
    product_service = ProductService(product_repository)

    return category_service, product_service


def create_category(category_service):
    return category_service.create_category(
        name=f"Test Category {uuid4()}",
        description="Category created for product testing",
    )


def create_product(product_service, category_id):
    return product_service.create_product(
        category_id=category_id,
        name=f"Test Product {uuid4()}",
        cost_price=Decimal("10000.00"),
        target_price=Decimal("15000.00"),
        minimum_price=Decimal("12000.00"),
        description="Test product",
    )


def test_create_product(db_session):
    category_service, product_service = create_services(db_session)

    category = create_category(category_service)

    product = product_service.create_product(
        category_id=category.id,
        name="Test Sneakers",
        cost_price=Decimal("10000.00"),
        target_price=Decimal("15000.00"),
        minimum_price=Decimal("12000.00"),
        description="Test product",
    )

    assert product.id is not None
    assert product.category_id == category.id
    assert product.name == "Test Sneakers"
    assert product.cost_price == Decimal("10000.00")
    assert product.target_price == Decimal("15000.00")
    assert product.minimum_price == Decimal("12000.00")
    assert product.current_stock == 0
    assert product.is_active is True


def test_get_product(db_session):
    category_service, product_service = create_services(db_session)

    category = create_category(category_service)
    product = create_product(product_service, category.id)

    retrieved = product_service.get_product(product.id)

    assert retrieved is not None
    assert retrieved.id == product.id
    assert retrieved.name == product.name
    assert retrieved.category_id == category.id


def test_get_product_returns_none_for_nonexistent_product(db_session):
    _, product_service = create_services(db_session)

    retrieved = product_service.get_product(uuid4())

    assert retrieved is None


def test_get_all_products(db_session):
    category_service, product_service = create_services(db_session)

    category = create_category(category_service)

    first = create_product(product_service, category.id)
    second = create_product(product_service, category.id)

    products = product_service.get_all_products()

    product_ids = {product.id for product in products}

    assert first.id in product_ids
    assert second.id in product_ids


def test_get_active_products(db_session):
    category_service, product_service = create_services(db_session)

    category = create_category(category_service)

    active_product = create_product(product_service, category.id)
    inactive_product = create_product(product_service, category.id)

    product_service.deactivate_product(inactive_product.id)

    active_products = product_service.get_active_products()

    active_product_ids = {product.id for product in active_products}

    assert active_product.id in active_product_ids
    assert inactive_product.id not in active_product_ids


def test_update_product(db_session):
    category_service, product_service = create_services(db_session)

    category = create_category(category_service)
    product = create_product(product_service, category.id)

    updated = product_service.update_product(
        product.id,
        name="Updated Test Sneakers",
        description="Updated product description",
        target_price=Decimal("16000.00"),
        minimum_price=Decimal("13000.00"),
    )

    assert updated.id == product.id
    assert updated.name == "Updated Test Sneakers"
    assert updated.description == "Updated product description"
    assert updated.cost_price == Decimal("10000.00")
    assert updated.target_price == Decimal("16000.00")
    assert updated.minimum_price == Decimal("13000.00")


def test_update_product_rejects_nonexistent_product(db_session):
    _, product_service = create_services(db_session)

    product_id = uuid4()

    with pytest.raises(
        ValueError,
        match=f"Product with ID {product_id} does not exist.",
    ):
        product_service.update_product(
            product_id,
            name="Updated Product",
        )


def test_create_product_rejects_minimum_price_below_cost(db_session):
    category_service, product_service = create_services(db_session)

    category = create_category(category_service)

    with pytest.raises(
        ValueError,
        match="Minimum price cannot be less than cost price.",
    ):
        product_service.create_product(
            category_id=category.id,
            name="Invalid Product",
            cost_price=Decimal("10000.00"),
            target_price=Decimal("15000.00"),
            minimum_price=Decimal("9000.00"),
        )


def test_create_product_rejects_target_price_below_minimum(db_session):
    category_service, product_service = create_services(db_session)

    category = create_category(category_service)

    with pytest.raises(
        ValueError,
        match="Target price cannot be less than minimum price.",
    ):
        product_service.create_product(
            category_id=category.id,
            name="Invalid Product",
            cost_price=Decimal("10000.00"),
            target_price=Decimal("11000.00"),
            minimum_price=Decimal("12000.00"),
        )


def test_update_product_rejects_minimum_price_below_cost(db_session):
    category_service, product_service = create_services(db_session)

    category = create_category(category_service)
    product = create_product(product_service, category.id)

    with pytest.raises(
        ValueError,
        match="Minimum price cannot be less than cost price.",
    ):
        product_service.update_product(
            product.id,
            minimum_price=Decimal("9000.00"),
        )


def test_update_product_rejects_target_price_below_minimum(db_session):
    category_service, product_service = create_services(db_session)

    category = create_category(category_service)
    product = create_product(product_service, category.id)

    with pytest.raises(
        ValueError,
        match="Target price cannot be lower than minimum price",
    ):
        product_service.update_product(
            product.id,
            target_price=Decimal("11000.00"),
        )


def test_deactivate_product(db_session):
    category_service, product_service = create_services(db_session)

    category = create_category(category_service)
    product = create_product(product_service, category.id)

    deactivated = product_service.deactivate_product(product.id)

    assert deactivated.id == product.id
    assert deactivated.is_active is False


def test_deactivate_nonexistent_product(db_session):
    _, product_service = create_services(db_session)

    with pytest.raises(ValueError, match="Product not found"):
        product_service.deactivate_product(uuid4())