import pytest
from uuid import uuid4
from decimal import Decimal

from src.repositories.categories_repository import CategoryRepository
from src.services.category_services import CategoryService
from src.repositories.product_repository import ProductRepository
from src.services.product_service import ProductService

def create_service(db_session):
    repository = CategoryRepository(db_session)
    return CategoryService(repository)


def test_create_category(db_session):
    service = create_service(db_session)

    category_name = f"Test Category {uuid4()}"

    category = service.create_category(
        name=category_name,
        description="Category created by pytest",
    )

    assert category.id is not None
    assert category.name == category_name
    assert category.description == "Category created by pytest"


def test_create_category_rejects_empty_name(db_session):
    service = create_service(db_session)

    with pytest.raises(ValueError, match="Category name cannot be empty"):
        service.create_category(
            name="",
            description="This should fail",
        )


def test_get_category(db_session):
    service = create_service(db_session)

    category = service.create_category(
        name=f"Category {uuid4()}",
        description="Test category",
    )

    retrieved = service.get_category(category.id)

    assert retrieved is not None
    assert retrieved.id == category.id
    assert retrieved.name == category.name
    assert retrieved.description == category.description


def test_get_category_returns_none_for_nonexistent_category(db_session):
    service = create_service(db_session)

    retrieved = service.get_category(uuid4())

    assert retrieved is None


def test_get_all_categories(db_session):
    service = create_service(db_session)

    first = service.create_category(
        name=f"Category {uuid4()}",
        description="First category",
    )

    second = service.create_category(
        name=f"Category {uuid4()}",
        description="Second category",
    )

    categories = service.get_all_categories()

    category_ids = {category.id for category in categories}

    assert first.id in category_ids
    assert second.id in category_ids


def test_update_category(db_session):
    service = create_service(db_session)

    category = service.create_category(
        name=f"Category {uuid4()}",
        description="Original description",
    )
    
    add = uuid4()

    updated = service.update_category(
        category.id,
        name= f"Updated12{add}",
        description="Updated description",
    )

    assert updated.id == category.id
    assert updated.name == f"Updated12{add}"
    assert updated.description == "Updated description"


def test_update_category_rejects_nonexistent_category(db_session):
    service = create_service(db_session)

    category_id = uuid4()

    with pytest.raises(
        ValueError,
        match=f"Category with ID {category_id} does not exist",
    ):
        service.update_category(
            category_id,
            name="Updated Category",
        )


def test_update_category_rejects_empty_name(db_session):
    service = create_service(db_session)

    category = service.create_category(
        name=f"Category {uuid4()}",
        description="Original description",
    )

    with pytest.raises(ValueError, match="Category name cannot be empty"):
        service.update_category(
            category.id,
            name="",
        )


def test_delete_category(db_session):
    service = create_service(db_session)

    category = service.create_category(
        name=f"Category {uuid4()}",
        description="Category to delete",
    )

    deleted = service.delete_category(category.id)

    assert deleted is True
    assert service.get_category(category.id) is None


def test_delete_category_rejects_nonexistent_category(db_session):
    service = create_service(db_session)

    category_id = uuid4()

    with pytest.raises(
        ValueError,
        match=f"Category with ID {category_id} does not exist",
    ):
        service.delete_category(category_id)


def test_delete_category_rejects_category_with_products(
    db_session,
):
    service = create_service(db_session)

    category = service.create_category(
        name=f"Category {uuid4()}",
        description="Category with products",
    )

    # This test requires a Product associated with the category.
    # We will implement this once we establish the Product test setup.
    
    product_service = ProductService(ProductRepository(db_session))
    product_service.create_product(
        category_id=category.id,
        name=f"Test Product {uuid4()}",
        cost_price=Decimal("10000.00"),
        target_price=Decimal("15000.00"),
        minimum_price=Decimal("12000.00"),
    )

    with pytest.raises(
        ValueError,
        match="Category cannot be deleted because products exist",
    ):
        service.delete_category(category.id)