from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.database.models.customer import Customer
from src.database.models.sales import Sale

class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, customer: Customer) -> Customer:
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        
        return customer
    
    def get_by_id(self, customer_id: UUID) -> Customer | None:
        stmt = select(Customer).where(Customer.id == customer_id)
        
        return self.db.scalar(stmt)
    
    def get_all(self) -> list[Customer]:
        return self.db.query(Customer).all()
    
    def update(self, customer: Customer) -> Customer:
        self.db.commit()
        self.db.refresh(customer)
        
        return customer
    
    def has_sales(self, customer_id: UUID) -> bool:
        stmt = (select(Sale.id).where(Sale.customer_id == customer_id).limit(1))
        return self.db.scalar(stmt) is not None
    
    def delete(self, customer_id:UUID) -> bool:
        customer = self.get_by_id(customer_id)
        
        if customer is None:
            return False
        
        self.db.delete(customer)
        self.db.commit()
        
        return True
        
    def get_customers_with_credit(self) -> list[Customer]:
        stmt = (select(Customer)
                .join(Sale, Sale.customer_id == Customer.id)
                .where(Sale.remaining_balance > 0)
                .distinct())
        
        return list(self.db.scalars(stmt).all())