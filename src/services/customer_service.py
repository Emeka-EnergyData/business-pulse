from uuid import UUID

from src.database.models.customer import Customer
from src.repositories.customer_repository import CustomerRepository

class CustomerService:
    def __init__(self, customer_repository:CustomerRepository):
        self.customer_repository = customer_repository
        
    def create_customer(
        self,
        name: str,
        phone: str | None = None,
        address: str | None = None,
        notes: str | None = None,
    ) -> Customer:
        """
        Create a new customer
        """
        
        name = name.strip()
        
        if not name:
            raise ValueError("Customer name cannot be empty.")
        
        customer = Customer(
            name = name,
            phone = phone,
            address = address,
            notes = notes,
        )
        
        return self.customer_repository.create(customer)
    
    def get_customer(self, customer_id: UUID) -> Customer | None:
        """
        Get one customer
        """
        return self.customer_repository.get_by_id(customer_id)
    
    def get_all_customers(self) -> list[Customer]:
        """
        Retrieve all customers.
        """
        return self.customer_repository.get_all()
    
    def update_customer(
        self,
        customer_id: UUID,
        *,
        name: str | None = None,
        phone: str | None = None,
        address: str | None = None,
        notes: str | None = None,
    ) -> Customer:
        """
        Update an existing customer.
        """
        
        customer = self.customer_repository.get_by_id(customer_id)
        
        if customer is None:
            raise ValueError(f"Customer with ID {customer_id} does not exist.")
        
        if name is not None:
            name = name.strip()
            
            if not name:
                raise ValueError("Customer name cannot be empty.")
            
            customer.name = name
            
        if phone is not None:
            customer.phone = phone
            
        if address is not None:
            customer.address = address
            
        if notes is not None:
            customer.notes = notes
            
        return self.customer_repository.update(customer)
        
    def delete_customer(self, customer_id:UUID) -> bool:
        """ 
        Delete a customer only if thry have no sales
        """

        customer = self.customer_repository.get_by_id(customer_id)
        
        if customer is None:
            raise ValueError(f"Customer with ID {customer_id} does not exist")
        
        if self.customer_repository.has_sales(customer_id):
            raise ValueError("Customer cannot be deleted because purchase history exists")
        
        return self.customer_repository.delete(customer_id)