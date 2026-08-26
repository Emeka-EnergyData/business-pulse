from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.database.models.sale_item import SaleItem

class SaleItemRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, sale_item: SaleItem) -> SaleItem:
        self.db.add(sale_item)
        self.db.flush()
        
        return sale_item
    
    def get_by_id(self, sale_item_id: UUID) -> SaleItem | None:
        stmt = select(SaleItem).where(SaleItem.id == sale_item_id)
        
        return self.db.scalar(stmt)
    
    def get_all(self) -> list[SaleItem]:
        return self.db.query(SaleItem).all()    
        