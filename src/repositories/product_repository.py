from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models.product import Product

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.flush()
        self.db.refresh(product)
        
        return product
        
    def get_by_id(self, product_id: UUID) -> Product | None:
        stmt = select(Product).where(Product.id == product_id)
        return self.db.scalar(stmt)
    
    def get_all(self) -> list[Product]:
        return self.db.query(Product).all()
    
    def get_active(self) -> list[Product]:
        stmt = select(Product).where(Product.is_active.is_(True))
        return list(self.db.scalars(stmt).all())
    
    def update(self, product: Product) -> Product:
        self.db.flush()
        self.db.refresh(product)
        return product
    