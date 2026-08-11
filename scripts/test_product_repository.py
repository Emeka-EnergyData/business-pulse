import uuid
from decimal import Decimal

from src.database.connection import SessionLocal
from src.repositories.product_repository import ProductRepository
from src.database.models.product import Product

db = SessionLocal()

try:
    repository = ProductRepository(db)
    
    products = Product(
        category_id=uuid.UUID("67642bd7-2030-479c-b2f3-a2af29b6cedb"), 
        name="Test Product", 
        description="A product for testing", 
        cost_price=Decimal("10.00"), 
        target_price=Decimal("15.00"), 
        minimum_price=Decimal("12.00"), 
        current_stock=100
    )
    
    repository.create(products)
    db.commit()
    
    print(f"- {products.name} (ID: {products.id})")
    
    found_product = repository.get_by_id(products.id)
    if found_product:
        print(f"Found product: {found_product.name} (ID: {found_product.id})")
    else:
        print("Product not found.")
finally:
    db.close()