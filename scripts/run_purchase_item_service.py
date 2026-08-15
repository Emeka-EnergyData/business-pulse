from decimal import Decimal
from datetime import date
from uuid import UUID

from src.database.connection import SessionLocal
from src.database.models.category import Category
from src.database.models.product import Product
from src.database.models.supplier import Supplier
from src.database.models.purchase import Purchase

from src.repositories.purchase_repository import PurchaseRepository
from src.repositories.purchase_item_repository import PurchaseItemRepository
from src.repositories.product_repository import ProductRepository
from src.repositories.stock_movement_repository import StockMovementRepository
from src.services.purchase_item_service import PurchaseItemService

def main():
    db = SessionLocal()
    
       # REPOSITORIES
    purchase_item_repository = PurchaseItemRepository(db)        
    product_repository = ProductRepository(db)
    stock_movement_repository = StockMovementRepository(db)
    purchase_repository = PurchaseRepository(db)
    
    service = PurchaseItemService(
            purchase_item_repository=purchase_item_repository, 
            product_repository=product_repository,
            stock_movement_repository=stock_movement_repository
            )

        # 1. CREATE PURCHASE ITEM 
    quantity = 5    
    unit_cost = Decimal("10500.00")
        
    purchase = purchase_repository.get_by_id(UUID("333b0382-b5bc-4b61-ae9c-0b2ed735086a")) 
    product = product_repository.get_by_id(UUID("ba51f8dd-9405-4072-bf5b-a9d9bfad5623"))

    print(purchase)
    
    
    purchase_item = service.create_purchase_item(
            purchase_id=purchase.id,     
            product_id=product.id,      
            quantity=quantity,      
            unit_cost=unit_cost  
            )

    print("\nCREATE PURCHASE ITEM:")    
    print(f"ID: {purchase_item.id}")    
    print(f"Purchase ID: {purchase_item.purchase_id}")    
    print(f"Product ID: {purchase_item.product_id}")    
    print(f"Quantity: {purchase_item.quantity}")    
    print(f"Unit Cost: {purchase_item.unit_cost}")

 
    # 2. VERIFY PRODUCT STOCK

    print("\nPRODUCT STOCK:")    
    print(f"Stock before: 0")   
    print(f"Stock after: {product.current_stock}")
    
    assert product.current_stock == quantity
    
    # 3. VERIFY STOCK MOVEMENT    
                
    movements = stock_movement_repository.get_all()
    purchase_movement = next(
                    (movement 
                     for movement in movements 
                     if movement.reference_id == purchase.id        
                     and movement.product_id == product.id     
                     ),
                    None,    
                    )
                
    print("\nSTOCK MOVEMENT:")
    
    assert purchase_movement is not None
                
    print(f"ID: {purchase_movement.id}")    
    print(f"Product ID: {purchase_movement.product_id}")    
    print(f"Movement Type: {purchase_movement.movement_type}")    
    print(f"Quantity: {purchase_movement.quantity}")    
    print(f"Reference Type: {purchase_movement.reference_type}")    
    print(f"Reference ID: {purchase_movement.reference_id}")
                
    assert purchase_movement.movement_type == "RECEIVED"    
    assert purchase_movement.quantity == quantity    
    assert purchase_movement.reference_type == "Purchase"    
    assert purchase_movement.reference_id == purchase.id
                
    # 4. GET PURCHASE ITEM  
                
    fetched_item = service.get_purchase_item(purchase_item.id)
                
    print("\nGET PURCHASE ITEM:")    
    print(fetched_item.id)    
    print(fetched_item.product_id)    
    print(fetched_item.quantity)    
    print(fetched_item.unit_cost)
                
    assert fetched_item.id == purchase_item.id
                
    # 5. GET ALL PURCHASE ITEMS
                
    all_items = service.get_all_purchase_items()
    
    print("\nALL PURCHASE ITEMS:")    
    
    for item in all_items:      
        print(
            item.id,        
            item.purchase_id,        
            item.product_id,        
            item.quantity,        
            item.unit_cost
                        )

    assert any(item.id == purchase_item.id for item in all_items)
                
                 
    print("\nPURCHASE ITEM SERVICE TEST PASSED") 
    
           
    db.close()

if __name__ == "__main__": 
    main()