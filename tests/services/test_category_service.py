from src.repositories.categories_repository import CategoryRepository
from src.services.category_services import CategoryService
from uuid import uuid4

def test_create_category(db_session):
    repository = CategoryRepository(db_session)
    service = CategoryService(repository)
    
    category_name = f"Test Category {uuid4()}"

    category = service.create_category(
        name=category_name,
        description="Category created by pytest",
    )

    assert category.id is not None
    assert category.name == category_name
    assert category.description == "Category created by pytest"