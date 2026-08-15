from datetime import datetime, timezone

from src.database.connection import SessionLocal
from src.repositories.stock_movement_repository import StockMovementRepository
from src.services.stock_movement_service import StockMovementService


def main():
    db = SessionLocal()

    try:
        repository = StockMovementRepository(db)
        service = StockMovementService(repository)

        # Test 1: Get all stock movements

        movements = service.get_all_stock_movement()

        print(f"Total stock movements: {len(movements)}")

        for movement in movements:
            print(
                movement.id,
                movement.product_id,
                movement.movement_type,
                movement.quantity,
                movement.reference_type,
                movement.reference_id,
                movement.movement_date,
            )

        # Test 2: Get one stock movement

        if movements:
            movement_id = movements[0].id

            movement = service.get_stock_movement(movement_id)

            print("\nRetrieved stock movement:")
            print(
                movement.id,
                movement.product_id,
                movement.movement_type,
                movement.quantity,
                movement.reference_type,
                movement.reference_id,
                movement.movement_date,
            )

        else:
            print("\nNo stock movements found to test get_stock_movement().")

        # Test 3: Try an ID that does not exist

        from uuid import uuid4

        fake_id = uuid4()

        result = service.get_stock_movement(fake_id)

        print("\nNon-existent movement:")
        print(result)

    finally:
        db.close()


if __name__ == "__main__":
    main()