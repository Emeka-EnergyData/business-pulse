from uuid import uuid4

from src.database.connection import SessionLocal
from src.repositories.supplier_repository import SupplierRepository
from src.services.supplier_service import SupplierService


def main():
    db = SessionLocal()

    try:
        repository = SupplierRepository(db)
        service = SupplierService(repository)

        # --------------------------------------------------
        # 1. Create supplier
        # --------------------------------------------------

        supplier = service.create_supplier(
            name="Test China Supplier",
            phone="08012345678",
            address="Lagos",
            notes="Supplier service test"
        )

        print("\n1. Supplier created")
        print(f"ID: {supplier.id}")
        print(f"Name: {supplier.name}")
        print(f"Phone: {supplier.phone}")
        print(f"Address: {supplier.address}")
        print(f"Notes: {supplier.notes}")

        # --------------------------------------------------
        # 2. Get supplier by ID
        # --------------------------------------------------

        retrieved = service.get_supplier(supplier.id)

        if retrieved is None:
            raise AssertionError("Supplier could not be retrieved")

        print("\n2. Supplier retrieved")
        print(f"ID: {retrieved.id}")
        print(f"Name: {retrieved.name}")

        # --------------------------------------------------
        # 3. Get all suppliers
        # --------------------------------------------------

        suppliers = service.get_all_suppliers()

        print("\n3. All suppliers")

        for item in suppliers:
            print(
                f"- {item.id} | "
                f"{item.name} | "
                f"{item.phone}"
            )

        # --------------------------------------------------
        # 4. Update supplier
        # --------------------------------------------------

        updated = service.update_supplier(
            supplier.id,
            name="Updated China Supplier",
            phone="08098765432",
            address="Lagos Island",
            notes="Updated supplier information"
        )

        print("\n4. Supplier updated")
        print(f"Name: {updated.name}")
        print(f"Phone: {updated.phone}")
        print(f"Address: {updated.address}")
        print(f"Notes: {updated.notes}")

        # --------------------------------------------------
        # 5. Test empty supplier name on create
        # --------------------------------------------------

        try:
            service.create_supplier(
                name="   "
            )

            raise AssertionError(
                "Empty supplier name was incorrectly accepted"
            )

        except ValueError as e:
            print("\n5. Empty supplier name correctly rejected")
            print(f"Error: {e}")

        # --------------------------------------------------
        # 6. Test empty supplier name on update
        # --------------------------------------------------

        try:
            service.update_supplier(
                supplier.id,
                name="   "
            )

            raise AssertionError(
                "Empty supplier name was incorrectly accepted during update"
            )

        except ValueError as e:
            print("\n6. Empty supplier name on update correctly rejected")
            print(f"Error: {e}")

        # --------------------------------------------------
        # 7. Test nonexistent supplier retrieval
        # --------------------------------------------------

        nonexistent_id = uuid4()

        nonexistent = service.get_supplier(nonexistent_id)

        if nonexistent is not None:
            raise AssertionError(
                "Nonexistent supplier was unexpectedly retrieved"
            )

        print("\n7. Nonexistent supplier correctly returned None")

        # --------------------------------------------------
        # 8. Test nonexistent supplier update
        # --------------------------------------------------

        try:
            service.update_supplier(
                nonexistent_id,
                name="Should Fail"
            )

            raise AssertionError(
                "Updating nonexistent supplier did not fail"
            )

        except ValueError as e:
            print("\n8. Nonexistent supplier update correctly rejected")
            print(f"Error: {e}")

        # --------------------------------------------------
        # 9. Test nonexistent supplier deletion
        # --------------------------------------------------

        try:
            service.delete_supplier(nonexistent_id)

            raise AssertionError(
                "Deleting nonexistent supplier did not fail"
            )

        except ValueError as e:
            print("\n9. Nonexistent supplier deletion correctly rejected")
            print(f"Error: {e}")

        # --------------------------------------------------
        # 10. Delete supplier with no purchase history
        # --------------------------------------------------

        deleted = service.delete_supplier(supplier.id)

        if deleted is not True:
            raise AssertionError(
                "Supplier with no purchase history was not deleted"
            )

        print("\n10. Supplier with no purchase history deleted")
        print(f"Deleted: {deleted}")

        # --------------------------------------------------
        # 11. Verify deleted supplier cannot be retrieved
        # --------------------------------------------------

        deleted_supplier = service.get_supplier(supplier.id)

        if deleted_supplier is not None:
            raise AssertionError(
                "Deleted supplier can still be retrieved"
            )

        print("\n11. Deleted supplier correctly no longer exists")
       
    finally:
        db.close()


if __name__ == "__main__":
    main()