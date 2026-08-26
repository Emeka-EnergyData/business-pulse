from decimal import Decimal
from uuid import UUID

from src.database.models.product import Product
from src.repositories.product_repository import ProductRepository

class ProductService:
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
        
    

    def create_product(self, 
                       category_id: UUID, 
                       name: str, 
                       cost_price: Decimal, 
                       target_price: Decimal, 
                       minimum_price: Decimal,
                       description: str|None = None) -> Product:
        """
        Create a new product with the given name and price.

        :param category_id: The ID of the category to which the product belongs.
        :param cost_price: The cost price of the product.
        :param name: The name of the product.
        :param target_price: The target price of the product.
        :param minimum_price: The minimum price of the product.
        :param description: The description of the product.
        :return: The created Product object.
        """
        if self.product_repository.get_by_name(name):
            raise ValueError(f"Product '{name}' already exists")
        if minimum_price < cost_price:
            raise ValueError("Minimum price cannot be less than cost price.")
        if target_price < minimum_price:
            raise ValueError("Target price cannot be less than minimum price.")
        
        new_product = Product(
            category_id=category_id, 
            name=name, 
            cost_price=cost_price, 
            target_price=target_price, 
            minimum_price=minimum_price, 
            description=description)
        
        return self.product_repository.create(new_product)

    def get_product(self, product_id: UUID) -> Product | None:
        """
        Retrieve a product by its ID.

        :param product_id: The ID of the product to retrieve.
        :return: The Product object if found, else None.
        """
        return self.product_repository.get_by_id(product_id)
    
    def get_all_products(self) -> list[Product]:
        """
        Retrieve all products.

        :return: A list of all Product objects.
        """
        return self.product_repository.get_all()
    
    def get_active_products(self) -> list[Product]:
        """
        Retrieve all active products.

        :return: A list of all active Product objects.
        """
        return self.product_repository.get_active()

    def update_product(self, 
                       product_id: UUID,
                       *, 
                       name: str | None = None,
                       description: str | None = None,
                       cost_price: Decimal | None = None,
                       target_price: Decimal | None = None,
                       minimum_price: Decimal | None = None
                       ) -> Product:
        
        product = self.product_repository.get_by_id(product_id)
        
        if product is None:
            raise ValueError(f"Product with ID {product_id} does not exist.")
        
        new_cost = cost_price if cost_price is not None else product.cost_price
        new_target = target_price if target_price is not None else product.target_price
        new_minimum = (minimum_price if minimum_price is not None else product.minimum_price)
        
        if new_minimum < new_cost:
            raise ValueError("Minimum price cannot be less than cost price.")
        
        if new_target < new_minimum:
            raise ValueError("Target price cannot be lower than minimum price")

        if name is not None:
            product.name = name
            
        if description is not None:
            product.description = description
            
        if cost_price is not None:
            product.cost_price = cost_price
            
        if target_price is not None:
            product.target_price = target_price
            
        if minimum_price is not None:
            product.minimum_price = minimum_price
            
        return self.product_repository.update(product)
    
    def deactivate_product(self, product_id: UUID):
        product = self.product_repository.get_by_id(product_id)
        
        if product is None:
            raise ValueError("Product not found")
        
        product.is_active = False
        
        return self.product_repository.update(product)
    
    def reactivate_product(self, product_id: UUID) -> Product:
        product = self.product_repository.get_by_id(product_id)
        
        if product is None:
            raise ValueError("Product not found")
        
        product.is_active = True
        
        return self.product_repository.update(product)