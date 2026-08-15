from uuid import uuid4

from src.database.connection import SessionLocal
from src.repositories.customer_repository import CustomerRepository
from src.services.customer_service import CustomerService


db = SessionLocal()

try:
    repository = CustomerRepository(db)
    service = CustomerService(repository)

    # 1. CREATE CUSTOMER

    customer = service.create_customer(
        name=" John Doe ",
        phone="08012345678",
        address="Lagos",
        notes="Regular customer",
    )

    print("\n1. CREATE CUSTOMER")
    print(f"ID: {customer.id}")
    print(f"Name: {customer.name}")
    print(f"Phone: {customer.phone}")
    print(f"Address: {customer.address}")
    print(f"Notes: {customer.notes}")

    assert customer.name == "John Doe"
    assert customer.phone == "08012345678"

    print("Test Passed")
    
    # 2. CREATE CUSTOMER WITH EMPTY NAME
    
    print("\n2. TEST EMPTY CUSTOMER NAME")

    try:
        service.create_customer(name=" ")
        print("FAILED: Empty name was accepted")
    except ValueError as e:
        print(f"PASSED: {e}")
    
    # 3. GET CUSTOMER BY ID
    
    print("\n3. GET CUSTOMER")

    found_customer = service.get_customer(customer.id)

    print(f"Found: {found_customer.name}")

    assert found_customer is not None
    assert found_customer.id == customer.id
    assert found_customer.name == "John Doe"

    print("PASSED")

    # 4. GET NONEXISTENT CUSTOMER
    
    print("\n4. GET NONEXISTENT CUSTOMER")

    nonexistent_customer = service.get_customer(uuid4())

    assert nonexistent_customer is None

    print("PASSED: Nonexistent customer returned None")

    # 5. GET ALL CUSTOMERS
    
    print("\n5. GET ALL CUSTOMERS")

    customers = service.get_all_customers()

    print(f"Total customers: {len(customers)}")

    assert customer.id in [c.id for c in customers]

    print("PASSED")
    
    # 6. UPDATE CUSTOMER

    print("\n6. UPDATE CUSTOMER")

    updated_customer = service.update_customer(
        customer.id,
        name=" John Updated ",
        phone="08123456789",
        address="Abuja",
        notes="Updated customer",
    )

    print(f"Name: {updated_customer.name}")
    print(f"Phone: {updated_customer.phone}")
    print(f"Address: {updated_customer.address}")
    print(f"Notes: {updated_customer.notes}")

    assert updated_customer.name == "John Updated"
    assert updated_customer.phone == "08123456789"
    assert updated_customer.address == "Abuja"
    assert updated_customer.notes == "Updated customer"

    print("PASSED")
    
    # 7. UPDATE CUSTOMER WITH EMPTY NAME

    print("\n7. TEST UPDATE WITH EMPTY NAME")

    try:
        service.update_customer(
            customer.id,
            name=" ",
        )

        print("FAILED: Empty name was accepted")

    except ValueError as e:
        print(f"PASSED: {e}")

    # 8. UPDATE NONEXISTENT CUSTOMER

    print("\n8. UPDATE NONEXISTENT CUSTOMER")

    try:
        service.update_customer(
            uuid4(),
            name="Nobody",
        )

        print("FAILED: Nonexistent customer was updated")

    except ValueError as e:
        print(f"PASSED: {e}")
    
    # 9. DELETE NONEXISTENT CUSTOMER

    print("\n9. DELETE NONEXISTENT CUSTOMER")

    try:
        service.delete_customer(uuid4())

        print("FAILED: Nonexistent customer was deleted")

    except ValueError as e:
        print(f"PASSED: {e}")

    # 10. DELETE CUSTOMER WITHOUT SALES

    print("\n10. DELETE CUSTOMER WITHOUT SALES")

    customer_to_delete = service.create_customer(
        name="Customer To Delete",
        phone="08000000000",
    )

    deleted = service.delete_customer(customer_to_delete.id)

    assert deleted is True

    # Verify that it is actually gone
    deleted_customer = service.get_customer(customer_to_delete.id)

    assert deleted_customer is None

    print("PASSED: Customer deleted successfully")

    # FINAL RESULT

    print("\n" + "=" * 60)
    print("ALL CUSTOMER SERVICE TESTS PASSED")
    print("=" * 60)

finally:
    db.close()