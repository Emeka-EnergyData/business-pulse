from uuid import UUID

from src.database.models.stock_movement import StockMovement
from src.repositories.stock_movement_repository import StockMovementRepository

class StockMovementService:
    def __init__(self, stock_movement_repository:StockMovementRepository):
        self.stock_movement_repository = stock_movement_repository
         
    def get_all_stock_movement(self) -> list[StockMovement]:
        """
        Retrieve all suppliers.
        """
        return self.stock_movement_repository.get_all()
    
    def get_stock_movement(self, movement_id: UUID) -> StockMovement | None:
        
        return self.stock_movement_repository.get_by_id(movement_id)