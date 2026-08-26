import pytest
from uuid import uuid4

from src.repositories.customer_repository import CustomerRepository
from src.services.customer_service import CustomerService


def create_service(db_session):
    repository = CustomerRepository(db_session)
    return CustomerService(repository)


def test_create_customer(db_session):
    service = create_service(db_session)

    customer = service.create_customer(
        name=" John Doe ",
        phone="08012345678",
        address="Lagos",
        notes="Regular customer",
    )

    assert customer.id is not None
    assert customer.name == "John Doe"
    assert customer.phone == "08012345678"
    assert customer.address == "Lagos"
    assert customer.notes == "Regular customer"


def test_create_customer_rejects_empty_name(db_session):
    service = create_service(db_session)

    with pytest.raises(
        ValueError,
        match="Customer name cannot be empty",
    ):
        service.create_customer(name="   ")


def test_get_customer(db_session):
    service = create_service(db_session)

    customer = service.create_customer(
        name="John Doe",
        phone="08012345678",
    )

    retrieved = service.get_customer(customer.id)

    assert retrieved is not None
    assert retrieved.id == customer.id
    assert retrieved.name == "John Doe"


def test_get_customer_returns_none_for_nonexistent_customer(db_session):
    service = create_service(db_session)

    retrieved = service.get_customer(uuid4())

    assert retrieved is None


def test_get_all_customers(db_session):
    service = create_service(db_session)

    customer = service.create_customer(
        name=f"Customer {uuid4()}",
    )

    customers = service.get_all_customers()

    assert any(item.id == customer.id for item in customers)


def test_update_customer(db_session):
    service = create_service(db_session)

    customer = service.create_customer(
        name="John Doe",
        phone="08012345678",
        address="Lagos",
        notes="Regular customer",
    )

    updated = service.update_customer(
        customer.id,
        name=" John Updated ",
        phone="08123456789",
        address="Abuja",
        notes="Updated customer",
    )

    assert updated.id == customer.id
    assert updated.name == "John Updated"
    assert updated.phone == "08123456789"
    assert updated.address == "Abuja"
    assert updated.notes == "Updated customer"


def test_update_customer_rejects_empty_name(db_session):
    service = create_service(db_session)

    customer = service.create_customer(
        name="John Doe",
    )

    with pytest.raises(
        ValueError,
        match="Customer name cannot be empty",
    ):
        service.update_customer(
            customer.id,
            name="   ",
        )


def test_update_customer_rejects_nonexistent_customer(db_session):
    service = create_service(db_session)

    with pytest.raises(
        ValueError,
        match="does not exist",
    ):
        service.update_customer(
            uuid4(),
            name="Nobody",
        )


def test_delete_customer_rejects_nonexistent_customer(db_session):
    service = create_service(db_session)

    with pytest.raises(
        ValueError,
        match="does not exist",
    ):
        service.delete_customer(uuid4())


def test_delete_customer_without_sales(db_session):
    service = create_service(db_session)

    customer = service.create_customer(
        name="Customer To Delete",
        phone="08000000000",
    )

    deleted = service.delete_customer(customer.id)

    assert deleted is True

    retrieved = service.get_customer(customer.id)

    assert retrieved is None