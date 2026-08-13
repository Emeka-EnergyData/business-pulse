from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.database.models.stock_movement import StockMovement

class StockMovementRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, movement: StockMovement) -> StockMovement:
        self.db.add(movement)
        self.db.flush()
        
        return movement
    
    def get_by_id(self, stock_id: UUID) -> StockMovement | None:
        stmt = select(StockMovement).where(StockMovement.id == stock_id)
        
        return self.db.scalar(stmt)
    
    def get_all(self) -> list[StockMovement]:
        return self.db.query(StockMovement).all()    
        