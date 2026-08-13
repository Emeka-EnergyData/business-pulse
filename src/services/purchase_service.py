from datetime import date
from uuid import UUID

from src.database.models.purchase import Purchase
from src.repositories.purchase_repository import PurchaseRepository

class PurchaseService:
    def __init__(self, purchase_repository:PurchaseRepository):
        self.purchase_repository = purchase_repository
        
    def create_supplier(
        self,
        supplier_id: UUID,
        purchase_date: date,
        notes: str | None = None
    ) -> Purchase:
        """
        Create a new purchase record
        
        A purchase represents a shipment or receipt from a supplier
        
        Products are added separately through PurchaseItem
        """
        
        if supplier_id is None:
            raise ValueError("Supplier_id is required")
        
        if purchase_date is None:
            raise ValueError("Purchase date is required")
        
        purchase = Purchase(
            supplier_id=supplier_id,
            purchase_date = purchase_date,
            notes = notes,
        )
        
        return self.purchase_repository.create(purchase)
    
    def get_all_purchases(self) -> list[Purchase]:
        """
        Retrieve all purchase record.
        """
        
        return self.purchase_repository.get_all()
    
    def update_supplier(
        self,
        purchase_id: UUID,
        *,
        supplier_id: UUID | None = None,
        purchase_date: date | None = None,
        notes: str | None = None
    ) -> Purchase:
        """
        Update an existing purchase.
        """
      
        purchase = self.purchase_repository.get_by_id(purchase_id)
        
        if purchase is None:
            raise ValueError(f"Purchase with ID {purchase_id} does not exist.")
        
        if supplier_id is not None:
            purchase.supplier_id =supplier_id
            
        if purchase_date is not None:
            purchase.purchase_date = purchase_date
            
        if notes is not None:
            purchase.notes = notes
            
        return self.purchase_repository.update(purchase)