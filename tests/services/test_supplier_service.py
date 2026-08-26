import pytest
from uuid import uuid4

from src.repositories.supplier_repository import SupplierRepository
from src.services.supplier_service import SupplierService


def create_service(db_session):
    repository = SupplierRepository(db_session)
    return SupplierService(repository)


def create_supplier(service):
    return service.create_supplier(
        name=f"Test Supplier {uuid4()}",
        phone="08012345678",
        address="Lagos",
        notes="Supplier service test",
    )


def test_create_supplier(db_session):
    service = create_service(db_session)

    supplier = service.create_supplier(
        name="Test China Supplier",
        phone="08012345678",
        address="Lagos",
        notes="Supplier service test",
    )

    assert supplier.id is not None
    assert supplier.name == "Test China Supplier"
    assert supplier.phone == "08012345678"
    assert supplier.address == "Lagos"
    assert supplier.notes == "Supplier service test"


def test_get_supplier(db_session):
    service = create_service(db_session)

    supplier = create_supplier(service)

    retrieved = service.get_supplier(supplier.id)

    assert retrieved is not None
    assert retrieved.id == supplier.id
    assert retrieved.name == supplier.name


def test_get_all_suppliers(db_session):
    service = create_service(db_session)

    first = create_supplier(service)
    second = create_supplier(service)

    suppliers = service.get_all_suppliers()

    supplier_ids = {item.id for item in suppliers}

    assert first.id in supplier_ids
    assert second.id in supplier_ids


def test_update_supplier(db_session):
    service = create_service(db_session)

    supplier = create_supplier(service)

    updated = service.update_supplier(
        supplier.id,
        name="Updated China Supplier",
        phone="08098765432",
        address="Lagos Island",
        notes="Updated supplier information",
    )

    assert updated.id == supplier.id
    assert updated.name == "Updated China Supplier"
    assert updated.phone == "08098765432"
    assert updated.address == "Lagos Island"
    assert updated.notes == "Updated supplier information"


def test_create_supplier_rejects_empty_name(db_session):
    service = create_service(db_session)

    with pytest.raises(
        ValueError,
        match="Supplier name cannot be empty.",
    ):
        service.create_supplier(name="   ")


def test_update_supplier_rejects_empty_name(db_session):
    service = create_service(db_session)

    supplier = create_supplier(service)

    with pytest.raises(
        ValueError,
        match="Supplier name cannot be empty.",
    ):
        service.update_supplier(
            supplier.id,
            name="   ",
        )


def test_get_nonexistent_supplier_returns_none(db_session):
    service = create_service(db_session)

    supplier = service.get_supplier(uuid4())

    assert supplier is None


def test_update_nonexistent_supplier_raises_error(db_session):
    service = create_service(db_session)

    supplier_id = uuid4()

    with pytest.raises(
        ValueError,
        match=f"Supplier with ID {supplier_id} does not exist.",
    ):
        service.update_supplier(
            supplier_id,
            name="Should Fail",
        )


def test_delete_nonexistent_supplier_raises_error(db_session):
    service = create_service(db_session)

    supplier_id = uuid4()

    with pytest.raises(
        ValueError,
        match=f"Supplier with ID {supplier_id} does not exist",
    ):
        service.delete_supplier(supplier_id)


def test_delete_supplier_without_purchase_history(db_session):
    service = create_service(db_session)

    supplier = create_supplier(service)

    deleted = service.delete_supplier(supplier.id)

    assert deleted is True


def test_deleted_supplier_cannot_be_retrieved(db_session):
    service = create_service(db_session)

    supplier = create_supplier(service)

    service.delete_supplier(supplier.id)

    retrieved = service.get_supplier(supplier.id)

    assert retrieved is None