from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.database.models.stock_movement import StockMovement

class StockMovementRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, stock_movement: StockMovement) -> StockMovement:
        self.db.add(stock_movement)
        self.db.commit()
        self.db.refresh(stock_movement)
        
        return stock_movement
    
    def get_by_id(self, stock_id: UUID) -> StockMovement | None:
        stmt = select(StockMovement).where(StockMovement.id == stock_id)
        
        return self.db.scalar(stmt)
    
    def get_all(self) -> list[StockMovement]:
        return self.db.query(StockMovement).all()
    
    def update(self, stock_movement: StockMovement) -> StockMovement:
        self.db.commit()
        self.db.refresh(stock_movement)
        
        return stock_movement
    
    def delete(self, stock_id:UUID) -> bool:
        stock = self.get_by_id(stock_id)
        
        if stock is None:
            return False
        
        self.db.delete(stock)
        self.db.commit()
        
        return True
        
        