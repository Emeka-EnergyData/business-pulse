from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.database.models.category import Category

class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, category: Category) -> Category:
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        
        return category
    
    def get_by_id(self, category_id: UUID) -> Category | None:
        stmt = select(Category).where(Category.id == category_id)
        
        return self.db.scalar(stmt)
    
    def get_all(self) -> list[Category]:
        return self.db.query(Category).all()
    
    def update(self, category: Category) -> Category:
        self.db.commit()
        self.db.refresh(category)
        
        return category
    
    def delete(self, category_id:UUID) -> bool:
        category = self.get_by_id(category_id)
        
        if category is None:
            return False
        
        self.db.delete(category)
        self.db.commit()
        
        return True
        
        