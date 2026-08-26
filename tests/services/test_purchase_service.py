import pytest
from datetime import date
from uuid import uuid4

from src.repositories.purchase_repository import PurchaseRepository
from src.repositories.supplier_repository import SupplierRepository
from src.services.purchase_service import PurchaseService
from src.services.supplier_service import SupplierService


def create_purchase_service(db_session):
    repository = PurchaseRepository(db_session)
    return PurchaseService(repository)


def create_supplier(db_session):
    repository = SupplierRepository(db_session)
    service = SupplierService(repository)

    return service.create_supplier(
        name=f"Test Supplier {uuid4()}",
        phone="08012345678",
        address="Lagos",
        notes="Purchase service test supplier",
    )


def create_purchase(db_session):
    supplier = create_supplier(db_session)
    service = create_purchase_service(db_session)

    purchase = service.create_purchase(
        supplier_id=supplier.id,
        purchase_date=date.today(),
        notes="Test purchase",
    )

    return service, purchase, supplier


def test_create_purchase(db_session):
    service = create_purchase_service(db_session)
    supplier = create_supplier(db_session)

    purchase = service.create_purchase(
        supplier_id=supplier.id,
        purchase_date=date.today(),
        notes="Test purchase",
    )

    assert purchase.id is not None
    assert purchase.supplier_id == supplier.id
    assert purchase.purchase_date == date.today()
    assert purchase.notes == "Test purchase"


def test_get_purchase(db_session):
    service, purchase, supplier = create_purchase(db_session)

    retrieved = service.get_purhcase(purchase.id)

    assert retrieved is not None
    assert retrieved.id == purchase.id
    assert retrieved.supplier_id == supplier.id
    assert retrieved.purchase_date == purchase.purchase_date
    assert retrieved.notes == purchase.notes


def test_get_all_purchases(db_session):
    service, first_purchase, _ = create_purchase(db_session)

    _, second_purchase, _ = create_purchase(db_session)

    purchases = service.get_all_purchases()

    purchase_ids = {item.id for item in purchases}

    assert first_purchase.id in purchase_ids
    assert second_purchase.id in purchase_ids


def test_update_purchase(db_session):
    service, purchase, _ = create_purchase(db_session)

    updated = service.update_purchase(
        purchase.id,
        notes="Updated test purchase",
    )

    assert updated.id == purchase.id
    assert updated.notes == "Updated test purchase"


def test_update_purchase_supplier(db_session):
    service, purchase, _ = create_purchase(db_session)

    new_supplier = create_supplier(db_session)

    updated = service.update_purchase(
        purchase.id,
        supplier_id=new_supplier.id,
    )

    assert updated.supplier_id == new_supplier.id


def test_update_purchase_date(db_session):
    service, purchase, _ = create_purchase(db_session)

    new_date = date(2026, 1, 15)

    updated = service.update_purchase(
        purchase.id,
        purchase_date=new_date,
    )

    assert updated.purchase_date == new_date


def test_create_purchase_requires_supplier_id(db_session):
    service = create_purchase_service(db_session)

    with pytest.raises(
        ValueError,
        match="Supplier_id is required",
    ):
        service.create_purchase(
            supplier_id=None,
            purchase_date=date.today(),
            notes="Invalid purchase",
        )


def test_create_purchase_requires_purchase_date(db_session):
    service = create_purchase_service(db_session)
    supplier = create_supplier(db_session)

    with pytest.raises(
        ValueError,
        match="Purchase date is required",
    ):
        service.create_purchase(
            supplier_id=supplier.id,
            purchase_date=None,
            notes="Invalid purchase",
        )


def test_get_nonexistent_purchase_returns_none(db_session):
    service = create_purchase_service(db_session)

    purchase = service.get_purhcase(uuid4())

    assert purchase is None


def test_update_nonexistent_purchase_raises_error(db_session):
    service = create_purchase_service(db_session)

    purchase_id = uuid4()

    with pytest.raises(
        ValueError,
        match=f"Purchase with ID {purchase_id} does not exist.",
    ):
        service.update_purchase(
            purchase_id,
            notes="Should fail",
        )