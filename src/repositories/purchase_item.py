from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.database.models.purchase_item import PurchaseItem

class PurchaseItemRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, purchase_item: PurchaseItem) -> PurchaseItem:
        self.db.add(purchase_item)
        self.db.commit()
        self.db.refresh(purchase_item)
        
        return purchase_item
    
    def get_by_id(self, purchase_item_id: UUID) -> PurchaseItem | None:
        stmt = select(PurchaseItem).where(PurchaseItem.id == purchase_item_id)
        
        return self.db.scalar(stmt)
    
    def get_all(self) -> list[PurchaseItem]:
        return self.db.query(PurchaseItem).all()
    
    def update(self, purchase_item: PurchaseItem) -> PurchaseItem:
        self.db.commit()
        self.db.refresh(purchase_item)
        
        return purchase_item
    
    def delete(self, purchase_item_id:UUID) -> bool:
        purchase_item = self.get_by_id(purchase_item_id)
        
        if purchase_item is None:
            return False
        
        self.db.delete(purchase_item)
        self.db.commit()
        
        return True
        
        