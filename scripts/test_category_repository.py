import uuid

from src.database.connection import SessionLocal
from src.repositories.categories_repository import CategoryRepository
from src.database.models.category import Category

db = SessionLocal()

try:
    repository = CategoryRepository(db)
    
    category = Category(
        name = "Tessdasety Cateo2",
        description = "Repsitory test category"
    )
    
    created_category = repository.create(category)
    
    found_category = repository.get_by_id(created_category.id)
    
    print(f"ID: {found_category.created_at}")
    
    all_category = repository.get_all()
    
    print(all_category)
    
    for category in all_category:
        print(category.created_at)
        
    found_category.name = "Updated Category"
    found_category.description = "Updated description"
        
    update_category = repository.update(category)
    
finally:
    db.close()