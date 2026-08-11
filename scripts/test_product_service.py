import uuid
from decimal import Decimal

from src.database.connection import SessionLocal

from src.repositories.product_repository import ProductRepository

from src.services.product_service import ProductService

db = SessionLocal()

try:
    repository = ProductRepository(db)
    service = ProductService(repository)
    
    product = service.deactivate_product(
        product_id = uuid.UUID("303215e4-27a0-4dff-bee7-99fd8ac99a85")
        )
    
    db.commit()
    
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    db.close()
    
