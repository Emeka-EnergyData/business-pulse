from decimal import Decimal
from uuid import UUID

from src.database.models.stock_movement import StockMovement
from src.database.models.sale_item import SaleItem
from src.repositories.sale_item_repository import SaleItemRepository
from src.repositories.sales_repository import SalesRepository
from src.repositories.product_repository import ProductRepository
from src.repositories.stock_movement_repository import StockMovementRepository

class SaleItemService:
    def __init__(self, 
                 sale_item_repository: SaleItemRepository, 
                 product_repository: ProductRepository, 
                 stock_movement_repository: StockMovementRepository,
                 sales_repository: SalesRepository):
        
        self.sale_item_repository = sale_item_repository
        self.product_repository = product_repository
        self.stock_movement_repository = stock_movement_repository
        self.sales_repository = sales_repository 
        
    def create_sale_item(self,
                         sale_id: UUID,
                         product_id: UUID,
                         quantity: int,
                         unit_price: Decimal
                         ) -> SaleItem:
        """
        Create a sale item.
        
        A sale item represents a product sold as part of a sale.
        """
        
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        
        if unit_price <= 0:
            raise ValueError("Unit price must be greater than zero.")
        
        # get time of sale
        sale = self.sales_repository.get_by_id(sale_id)
                
        if sale is None:
            raise ValueError(f"Sale with ID {sale_id} does not exist")
        
        # To get cost price
        
        product = self.product_repository.get_by_id(product_id)
        
        if product is None:
            raise ValueError(f"Product with ID {product_id} does not exist")
        
        if not product.is_active:
            raise ValueError("Cannot sell an inactive product")
        
        if product.current_stock < quantity:
            raise ValueError(f"Insufficient stock. Available: {product.current_stock}, requested: {quantity}.")
            
        cost_price = product.cost_price
        
        line_total = unit_price * quantity
        
        sale_item = SaleItem(
            sale_id = sale_id,
            product_id = product_id,
            quantity = quantity,
            unit_price = unit_price,
            cost_price = cost_price,
            line_total = line_total
        )        
        
        self.sale_item_repository.create(sale_item)
                    
        self.product_repository.decrease_stock(product_id, quantity) 
              
        stock_movement = StockMovement(
            product_id = product_id,
            movement_type = "SOLD",
            quantity = quantity,
            reference_type = "Sale",
            reference_id = sale_id,
            movement_date = sale.sale_date
            )
        
        self.stock_movement_repository.create(stock_movement)
            
        return sale_item
        

    
    def get_sale_item (self, sale_item_id: UUID) -> SaleItem | None:
        """ 
        Retrieve a sale item by ID
        """
        return self.sale_item_repository.get_by_id(sale_item_id)
    
    def get_all_sale_items(self) -> list[SaleItem]:
        """ 
        Retrieve all purchase items
        """
        return self.sale_item_repository.get_all()