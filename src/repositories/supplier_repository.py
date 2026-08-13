from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.database.models.supplier import Supplier
from src.database.models.purchase import Purchase

class SupplierRepository:
    
    def __int__(self, db: Session):
        self.db = db
        
    def create_supplier(self, supplier:Supplier) -> Supplier:
        self.db.add(supplier)
        self.db.commit()
        self.db.refresh(supplier)
        
        return supplier
    
    def get_by_id(self, supplier_id:UUID):
        stmt = select(Supplier).where(Supplier.id == supplier_id)
       
        return self.db.scalar(stmt)
    
    def get_all(self) -> list[Supplier]:
        return self.db.query(Supplier).all()
    
    def update(self, supplier: Supplier) -> Supplier:
        self.db.commit()
        self.db.refresh(supplier)
        
        return supplier
        
    def delete(self, supplier_id: UUID) -> bool:
        supplier = self.get_by_id(supplier_id)
        
        if supplier is None:
            return False        
        self.db.delete(supplier)
        self.db.commit()
        
        return True
    
    def has_purchase_history(self, supplier_id: UUID) -> bool:
        stmt = (select(Purchase.id)
                .where(Purchase.supplier_id == supplier_id)
                .limit(1))
        
        return self.db.scalar(stmt) is not None