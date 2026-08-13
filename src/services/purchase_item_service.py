from decimal import Decimal
from uuid import UUID
from datetime import datetime, timezone

from src.database.models.stock_movement import StockMovement
from src.database.models.purchase_item import PurchaseItem
from src.repositories.purchase_item_repository import PurchaseItemRepository
from src.repositories.product_repository import ProductRepository
from src.repositories.stock_movement_repository import StockMovementRepository

class PurchaseItemService:
    def __init__(self, 
                 purchase_item_repository: PurchaseItemRepository, 
                 product_repository: ProductRepository, 
                 stock_movement_repository: StockMovementRepository):
        
        self.purchase_item_repository = purchase_item_repository
        self.product_repository = product_repository
        self.stock_movement_repository = stock_movement_repository
        
    def create_purchase_item(self,
                             purchase_id: UUID,
                             product_id: UUID,
                             quantity: int,
                             unit_cost: Decimal
                            ) -> PurchaseItem:
        """
        Create a purchase item.
        
        A purchase item represents a product received as part of a purchase."""
        
        if quantity <= 0:
            raise ValueError("Quantity must be greater tahn zero.")
        
        if unit_cost < 0:
            raise ValueError("Unit cost vannot be negative.")
        
        purchase_item = PurchaseItem(
            purchase_id = purchase_id,
            product_id = product_id,
            quantity = quantity,
            unit_cost = unit_cost
        )
        
        # Increase product qauntity
        product = self.product_repository.get_by_id(product_id)
        
        if product is None:
            raise ValueError(f"Product with ID {product_id} does not exist.")
        
        db = self.purchase_item_repository.db
        
        try:
            self.purchase_item_repository.create(purchase_item)
            
            self.product_repository.increase_stock(product_id, quantity) 
            
            stock_movement = StockMovement(
                product_id = product_id,
                movement_type = "RECEIVED",
                quantity = quantity,
                reference_type = "Purchase",
                reference_id = purchase_id,
                movement_date = datetime.now(timezone.utc)
            )
        
            self.stock_movement_repository.create(stock_movement)
            
            db.commit()
            db.refresh(purchase_item)
            
            return purchase_item
        
        except Exception:
            db.rollback()
            raise
    
    def get_purhcase_item (self, purchase_item_id: UUID) -> PurchaseItem | None:
        """ 
        Retrieve a purchase item by ID
        """
        return self.purchase_item_repository.get_by_id(purchase_item_id)
    
    def get_all_purchase_items(self) -> list[PurchaseItem]:
        """ 
        Retrieve all purchase items
        """
        return self.purchase_item_repository.get_all()
    

