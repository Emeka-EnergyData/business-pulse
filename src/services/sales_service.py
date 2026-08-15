from decimal import Decimal
from uuid import UUID
from datetime import datetime

from src.database.models.sales import Sale
from src.repositories.sales_repository import SalesRepository

class SaleService:
    def __init__(self, sales_repository: SalesRepository):
        self.sales_repository = sales_repository

    def create_sale(
        self,       
        sale_date: datetime,
        subtotal: Decimal, 
        discount: Decimal,
        total_amount: Decimal, 
        amount_paid: Decimal,
        remaining_balance: Decimal,
        payment_status: str,
        collection_status: str,
        customer_id: UUID | None = None, 
        notes: str|None = None) -> Sale:
        """
        Create a new sale.

        :param customer_id: The ID of the customer to which the sale belongs.
        :param sale_date: Date and time sale occured.
        :param subtotal: Total price of all sale before discount
        :param discount: Amount deducted from the subtotal
        :param total_amount: Final amount the customer owes after the discount
        :param amount_paid: Total amount the customer has paid so far
        :param remaining_balance: Amount still owed by the customer
        :param payment_status: Payment stae: PAID, PARTIAL, UNPAID
        :param collection_status: Whether the goods have collected
        :param notes: Optional additional info about the sale.
        
        :return: The created Sale object.
        """
        if subtotal < 0:
            raise ValueError("Subtotal cannot be negative")
        if discount < 0:
            raise ValueError("Discount cannot be negative")
        if total_amount < 0:
            raise ValueError("Total amount cannot be negative")
        if amount_paid < 0:
            raise ValueError("Amount paid cannot be negative")
        if remaining_balance < 0:
            raise ValueError("Remaining balance cannot be negative")
        if amount_paid > total_amount:
            raise ValueError("Amount paud cannot be greater than total amount")
        if payment_status not in {"PAID", "PARTIAL", "UNPAID"}:
            raise ValueError(f"Invalid payment status: {payment_status}")
        if collection_status not in {"COLLECTED", "PENDING_COLLECTION"}:
            raise ValueError(f"Invalid collection_status: {collection_status}")
        
        sale = Sale(
            customer_id=customer_id, 
            sale_date=sale_date, 
            subtotal=subtotal, 
            discount=discount,  
            total_amount=total_amount,
            amount_paid=amount_paid,
            remaining_balance=remaining_balance,
            payment_status=payment_status,
            collection_status=collection_status,
            notes=notes)
        
        return self.sales_repository.create(sale)

    def get_sale(self, sale_id: UUID) -> Sale | None:
        """
        Retrieve a sale by its ID.

        :param product_id: The ID of the product to retrieve.
        :return: The Product object if found, else None.
        """
        return self.sales_repository.get_by_id(sale_id)
    
    def get_all_sales(self) -> list[Sale]:
        """
        Retrieve all sales.

        :return: A list of all Sale objects.
        """
        return self.sales_repository.get_all()
    
    def update_sale(self, 
                       sale_id: UUID,
                       *,      
                       subtotal: Decimal | None=None, 
                       discount: Decimal | None=None,
                       total_amount: Decimal | None=None, 
                       amount_paid: Decimal | None=None,
                       remaining_balance: Decimal | None = None,
                       payment_status: str | None=None,
                       collection_status: str | None=None,
                       notes: str|None = None) -> Sale:
        """
        Update an existing sale.
        
        Payment related fields should eventually be updated through PaymentService.
        """
        
        sale = self.sales_repository.get_by_id(sale_id)
        
        if sale is None:
            raise ValueError(f"Sale with ID {sale_id} does not exist.")
        
        new_subtotal = (subtotal if subtotal is not None else sale.subtotal)
        new_discount = (discount if discount is not None else sale.discount)
        new_total = (total_amount if total_amount is not None else sale.total_amount)
        new_paid = (amount_paid if amount_paid is not None else sale.amount_paid)
        new_balance = (remaining_balance if remaining_balance is not None else sale.remaining_balance)
        new_payment_status = (payment_status if payment_status is not None else sale.payment_status)
        new_collection_status = (collection_status if collection_status is not None else sale.collection_status)
        
        if new_subtotal < 0:
            raise ValueError("Subtotal cannot be negative.")
        
        if new_discount < 0:
            raise ValueError("Discount cannot be negative")
        
        if new_total < 0:
            raise ValueError("Total amount cannot be negative")
        
        if new_paid < 0:
            raise ValueError("Amount paid cannot be negative")
        
        if new_balance < 0:
            raise ValueError("Remaining balance cannot be negative")
         
        if new_paid > new_total:
            raise ValueError("Amount paid cannot be greater than total amount")

        if new_payment_status not in {"PAID", "PARTIAL", "UNPAID"}:
            raise ValueError(f"Invalid payment status: {new_payment_status}")
        
        if new_collection_status not in {"COLLECTED", "PENDING_COLLECTION"}:
            raise ValueError(f"Invalid collection_status: {new_collection_status}")
                    
        if subtotal is not None:
            sale.subtotal = subtotal
            
        if discount is not None:
            sale.discount = discount
            
        if total_amount is not None:
            sale.total_amount = total_amount
            
        if amount_paid is not None:
            sale.amount_paid = amount_paid
            
        if remaining_balance is not None:
            sale.remaining_balance = remaining_balance
            
        if payment_status is not None:
            sale.payment_status = payment_status
            
        if collection_status is not None:
            sale.collection_status = collection_status
            
        if notes is not None:
            sale.notes = notes
            
        return self.sales_repository.update(sale)