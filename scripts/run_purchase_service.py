from datetime import date
from uuid import UUID

from src.database.connection import SessionLocal
from src.repositories.purchase_repository import PurchaseRepository
from src.services.purchase_service import PurchaseService


def main():
    db = SessionLocal()

    try:
        repository = PurchaseRepository(db)
        service = PurchaseService(repository)

      
        # 1. CREATE PURCHASE
       
        supplier_id = UUID("703cf141-9a0d-4899-9d5d-9bc656d318aa")

        purchase = service.create_purchase(
            supplier_id=supplier_id,
            purchase_date=date.today(),
            notes="Test purchase",
        )

        print("CREATE PURCHASE:")
        print(purchase.id)
        print(purchase.supplier_id)
        print(purchase.purchase_date)
        print(purchase.notes)

       
        # 2. GET ALL PURCHASES
        
        purchases = service.get_all_purchases()

        print("\nALL PURCHASES:")
        for item in purchases:
            print(
                item.id,
                item.supplier_id,
                item.purchase_date,
                item.notes,
            )

      
        # 3. GET PURCHASE BY ID
      
        fetched_purchase = service.get_purhcase(purchase.id)

        print("\nGET PURCHASE:")
        print(fetched_purchase.id)
        print(fetched_purchase.supplier_id)
        print(fetched_purchase.purchase_date)
        print(fetched_purchase.notes)

        # 4. UPDATE PURCHASE
     
        updated_purchase = service.update_purchase(
            purchase.id,
            notes="Updated test purchase",
        )

        print("\nUPDATED PURCHASE:")
        print(updated_purchase.id)
        print(updated_purchase.notes)

        # 5. VERIFY UPDATE
      
        verified_purchase = repository.get_by_id(purchase.id)

        print("\nVERIFIED UPDATE:")
        print(verified_purchase.id)
        print(verified_purchase.notes)

        print("\nPURCHASE SERVICE TEST PASSED")

    finally:
        db.close()


if __name__ == "__main__":
    main()