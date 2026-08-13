from uuid import UUID

from src.database.models.supplier import Supplier
from src.repositories.supplier_repository import SupplierRepository

class SupplierService:
    def __init__(self, supplier_repository:SupplierRepository):
        self.supplier_repository = supplier_repository
        
    def create_supplier(
        self,
        name: str,
        phone: str | None = None,
        address: str | None = None,
        notes: str | None = None,
    ) -> Supplier:
        """
        Create a new supplier
        """
        
        name = name.strip()
        
        if not name:
            raise ValueError("Supplier name cannot be empty.")
        
        supplier = Supplier(
            name = name,
            phone = phone,
            address = address,
            notes = notes,
        )
        
        return self.supplier_repository.create_supplier(supplier)
    
    def get_supplier(self, supplier_id: UUID) -> Supplier | None:
        return self.supplier_repository.get_by_id(supplier_id)
    
    def get_all_suppliers(self) -> list[Supplier]:
        """
        Retrieve all suppliers.
        """
        
        return self.supplier_repository.get_all()
    
    def update_supplier(
        self,
        supplier_id: UUID,
        *,
        name: str | None = None,
        phone: str | None = None,
        address: str | None = None,
        notes: str | None = None,
    ) -> Supplier:
        """
        Update an existing supplier.
        """
        
        supplier = self.supplier_repository.get_by_id(supplier_id)
        
        if supplier is None:
            raise ValueError(f"Supplier with ID {supplier_id} does not exist.")
        
        if name is not None:
            name = name.strip()
            
            if not name:
                raise ValueError("Supplier name cannot be empty.")
            
            supplier.name = name
            
        if phone is not None:
            supplier.phone = phone
            
        if address is not None:
            supplier.address = address
            
        if notes is not None:
            supplier.notes = notes
            
        return self.supplier_repository.update(supplier)
        
    def delete_supplier(self, supplier_id:UUID) -> bool:
        supplier = self.supplier_repository.get_by_id(supplier_id)
        
        if supplier is None:
            raise ValueError(f"Supplier with ID {supplier_id} does not exist")
        
        if self.supplier_repository.has_purchase_history(supplier_id):
            raise ValueError("Supplier cannot be deleted because purchase history exists")
        
        return self.supplier_repository.delete(supplier_id)