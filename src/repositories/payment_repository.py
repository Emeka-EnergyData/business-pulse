from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.database.models.payment import Payment

class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, payment: Payment) -> Payment:
        self.db.add(payment)
        self.db.flush()
        
        return payment
    
    def get_by_id(self, payment_id: UUID) -> Payment | None:
        stmt = select(Payment).where(Payment.id == payment_id)
        
        return self.db.scalar(stmt)
    
    def get_all(self) -> list[Payment]:
        return self.db.query(Payment).all()    
        