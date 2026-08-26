from uuid import UUID
from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from src.database.models.purchase import Purchase

class PurchaseRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, purchase: Purchase) -> Purchase:
        self.db.add(purchase)
        self.db.flush()
        self.db.refresh(purchase)
        
        return purchase
    
    def get_by_id(self, purchase_id: UUID) -> Purchase | None:
        stmt = (select(Purchase)
                .where(Purchase.id == purchase_id)
                .options(selectinload(Purchase.items))
        )
        
        return self.db.scalar(stmt)
    
    def get_all(self) -> list[Purchase]:
        stmt = (
            select(Purchase)
            .options(selectinload(Purchase.items))
                )
                
        return list(self.db.scalars(stmt).all())
            
    def update(self, purchase: Purchase) -> Purchase:
        self.db.commit()
        self.db.refresh(purchase)
        
        return purchase
    
    def get_purchases_between_dates(self, start_date:date, end_date:date) -> list[Purchase]:
        stmt = (
            select(Purchase)
            .where(Purchase.purchase_date >= start_date,
                   Purchase.purchase_date <= end_date)
            .options(selectinload(Purchase.items))
            .order_by(Purchase.purchase_date.asc())
        )
        
        return list(self.db.scalars(stmt).all())