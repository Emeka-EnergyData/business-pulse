from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.database.models.purchase import Purchase

class PurchaseRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, purchase: Purchase) -> Purchase:
        self.db.add(purchase)
        self.db.commit()
        self.db.refresh(purchase)
        
        return purchase
    
    def get_by_id(self, purchase_id: UUID) -> Purchase | None:
        stmt = select(Purchase).where(Purchase.id == purchase_id)
        
        return self.db.scalar(stmt)
    
    def get_all(self) -> list[Purchase]:
        return self.db.query(Purchase).all()
    
    def update(self, purchase: Purchase) -> Purchase:
        self.db.commit()
        self.db.refresh(purchase)
        
        return purchase