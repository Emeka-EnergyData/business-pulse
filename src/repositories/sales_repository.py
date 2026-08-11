from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.database.models.sales import Sale

class SalesRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, sale: Sale) -> Sale:
        self.db.add(sale)
        self.db.commit()
        self.db.refresh(sale)
        
        return sale
    
    def get_by_id(self, sale_id: UUID) -> Sale | None:
        stmt = select(Sale).where(Sale.id == sale_id)
        
        return self.db.scalar(stmt)
    
    def get_all(self) -> list[Sale]:
        return self.db.query(Sale).all()
    
    def update(self, sale: Sale) -> Sale:
        self.db.commit()
        self.db.refresh(Sale)
        
        return sale
    
    def delete(self, sale_id:UUID) -> bool:
        sale = self.get_by_id(sale_id)
        
        if sale is None:
            return False
        
        self.db.delete(sale)
        self.db.commit()
        
        return True
        
        