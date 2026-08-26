from datetime import datetime
from decimal import Decimal
from uuid import UUID

from src.database.models.payment import Payment
from src.repositories.payment_repository import PaymentRepository
from src.repositories.sales_repository import SalesRepository

class PaymentService:
    def __init__(self, 
                 payment_repository:PaymentRepository,
                 sales_repository: SalesRepository):
        self.payment_repository = payment_repository
        self.sales_repository = sales_repository
    
    def create_payment(
        self,
        sale_id: UUID,
        amount: Decimal,
        payment_method: str,
        payment_date: datetime,
        reference: str | None = None,
        notes: str | None = None
        ) -> Payment:
        """
        Record a payment against a sale
        """
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero")
        
        if not payment_method.strip():
            raise ValueError("Payment method is required")
        
        sale = self.sales_repository.get_by_id(sale_id)
        
        if sale is None:
            raise ValueError(f"Sale with ID {sale_id} does not exist.")
        
        payment = Payment(
            sale_id=sale_id,
            amount = amount,
            payment_method = payment_method.strip(),
            payment_date=payment_date,
            reference = reference,
            notes = notes,
        )
        
        db = self.payment_repository.db
        
        try:
            self.payment_repository.create(payment)
            
            db.commit()
            db.refresh(payment)
            
            return payment
    
        except Exception:
    
            db.rollback()
            raise
        
                    
    def record_payment(
        self,
        sale_id: UUID,
        amount: Decimal,
        payment_method: str,
        payment_date: datetime,
        reference: str | None = None,
        notes: str | None = None
    ) -> Payment:
        """
        Record a payment against a sale
        
        Recording a payment:
        - creates a permanent Payment record
        - increases Sale.amount_paid
        - decreases Sale.remaining_balance
        - updates Sale.payment_status
        """
        
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero")
        
        if not payment_method.strip():
            raise ValueError("Payment method is required")
        
        sale = self.sales_repository.get_by_id(sale_id)
        
        if sale is None:
            raise ValueError(f"Sale with ID {sale_id} does not exist.")
        
        new_amount_paid = sale.amount_paid + amount
        
        if new_amount_paid > sale.total_amount:
            raise ValueError("Payment amount would exceed the sale's remaining balance.")
        
        new_remaining_balance = sale.total_amount - new_amount_paid
        
        if new_remaining_balance == 0:
            new_payment_status = "PAID"
            
        elif new_amount_paid > 0:
            new_payment_status = "PARTIAL"
            
        else:
            new_payment_status = "UNPAID"
            
        payment = Payment(
            sale_id=sale_id,
            amount = amount,
            payment_method = payment_method.strip(),
            payment_date=payment_date,
            reference = reference,
            notes = notes,
        )
        
        db = self.payment_repository.db
        
        try:
            self.payment_repository.create(payment)
            
            sale.amount_paid = new_amount_paid
            sale.remaining_balance=new_remaining_balance
            sale.payment_status=new_payment_status
            
            self.sales_repository.update(sale)
            
            db.commit()
            db.refresh(payment)
            
            return payment
        except Exception:
            db.rollback()
            raise
    
    def get_payment(
        self,
        payment_id:UUID,
    ) -> Payment | None:
        """
        Retrieve a payment by ID.
        """
        return self.payment_repository.get_by_id(payment_id)
    
    def get_all_payment(self) -> list[Payment]:
        """
        Retrieve all purchase record.
        """
        
        return self.payment_repository.get_all()