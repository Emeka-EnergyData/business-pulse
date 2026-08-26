from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4
import pytest
from src.repositories.sales_repository import SalesRepository
from src.services.sales_service import SaleService
from src.repositories.customer_repository import CustomerRepository
from src.services.customer_service import CustomerService

def create_service(db_session):
    repository = SalesRepository(db_session)
    return SaleService(repository)

def create_valid_sale(service):
    return service.create_sale(
        sale_date=datetime.now(timezone.utc),
        subtotal=Decimal("50000.00"),
        discount=Decimal("5000.00"),
        total_amount=Decimal("45000.00"),
        amount_paid=Decimal("20000.00"),
        remaining_balance=Decimal("25000.00"),
        payment_status="PARTIAL",
        collection_status="COLLECTED",
        notes="Test sale"
        )

def test_create_sale(db_session):
    service = create_service(db_session)
    sale = create_valid_sale(service)
    
    assert sale.id is not None
    assert sale.subtotal == Decimal("50000.00")
    assert sale.discount == Decimal("5000.00")
    assert sale.total_amount == Decimal("45000.00")
    assert sale.amount_paid == Decimal("20000.00")
    assert sale.remaining_balance == Decimal("25000.00")
    assert sale.payment_status == "PARTIAL"
    assert sale.collection_status == "COLLECTED"
    assert sale.notes == "Test sale"

def test_create_sale_with_customer(db_session):
    
    customer_service =CustomerService(CustomerRepository(db_session))
    
    customer = customer_service.create_customer(
        name= f"Test Customer{uuid4()}",
        phone ="08012345678"
    )
    
    service = create_service(db_session)
        
    sale = service.create_sale(
        customer_id=customer.id,
        sale_date=datetime.now(timezone.utc),
        subtotal=Decimal("30000.00"),
        discount=Decimal("0.00"),
        total_amount=Decimal("30000.00"),
        amount_paid=Decimal("30000.00"),
        remaining_balance=Decimal("0.00"),
        payment_status="PAID",
        collection_status="COLLECTED",
        )
    assert sale.customer_id == customer.id

@pytest.mark.parametrize(
    "field,value,error_message",
    [
        (
            "subtotal",
            Decimal("-1.00"),
            "Subtotal cannot be negative",
            ),
        (
            "discount",
            Decimal("-1.00"),
            "Discount cannot be negative",
            ),
        (
            "total_amount",
            Decimal("-1.00"),
            "Total amount cannot be negative"
            ),
        (
            "amount_paid",
            Decimal("-1.00"),
            "Amount paid cannot be negative"
            ),
        (
            "remaining_balance",
            Decimal("-1.00"),
            "Remaining balance cannot be negative"
            ),
        ]
    )

def test_create_sale_rejects_negative_values(
    db_session,
    field,
    value,
    error_message):
    
    service = create_service(db_session)
    values = {
        "subtotal": Decimal("10000.00"),
        "discount": Decimal("0.00"),
        "total_amount": Decimal("10000.00"),
        "amount_paid": Decimal("0.00"),
        "remaining_balance": Decimal("10000.00"),
        "payment_status": "UNPAID",
        "collection_status": "PENDING_COLLECTION",
        }
    
    values[field] = value
    
    with pytest.raises(ValueError, match=error_message):
        service.create_sale(
            sale_date=datetime.now(timezone.utc),
            **values
            )

def test_create_sale_rejects_amount_paid_greater_than_total(db_session):
    service = create_service(db_session)
    with pytest.raises(
        ValueError,
        match="Amount paid cannot be greater than total amount"
        ):
        service.create_sale(
            sale_date=datetime.now(timezone.utc),
            subtotal=Decimal("10000.00"),
            discount=Decimal("0.00"),
            total_amount=Decimal("10000.00"),
            amount_paid=Decimal("12000.00"),
            remaining_balance=Decimal("0.00"),
            payment_status="PAID",
            collection_status="COLLECTED"
            )

@pytest.mark.parametrize(
    "payment_status",
    ["INVALID", "", "CANCELLED"]
    )
def test_create_sale_rejects_invalid_payment_status(
    db_session,
    payment_status):
    
    service = create_service(db_session)
    
    with pytest.raises(
        ValueError,
        match="Invalid payment status"
        ):
        
        service.create_sale(
            sale_date=datetime.now(timezone.utc),
            subtotal=Decimal("10000.00"),
            discount=Decimal("0.00"),
            total_amount=Decimal("10000.00"),
            amount_paid=Decimal("0.00"),
            remaining_balance=Decimal("10000.00"),
            payment_status=payment_status,
            collection_status="PENDING_COLLECTION"
            )

@pytest.mark.parametrize(
    "collection_status",
    ["INVALID", "", "DELIVERED"]
    )

def test_create_sale_rejects_invalid_collection_status(
    db_session,
    collection_status):
    
    service = create_service(db_session)
    
    with pytest.raises(
        ValueError,
        match="Invalid collection_status"
        ):
        service.create_sale(
            sale_date=datetime.now(timezone.utc),
            subtotal=Decimal("10000.00"),
            discount=Decimal("0.00"),
            total_amount=Decimal("10000.00"),
            amount_paid=Decimal("0.00"),
            remaining_balance=Decimal("10000.00"),
            payment_status="UNPAID",
            collection_status=collection_status
            )

def test_get_sale(db_session):
    service = create_service(db_session)
    sale = create_valid_sale(service)
    retrieved = service.get_sale(sale.id)
    
    assert retrieved is not None
    assert retrieved.id == sale.id
    assert retrieved.total_amount == Decimal("45000.00")

def test_get_sale_returns_none_for_nonexistent_sale(db_session):
    service = create_service(db_session)
    retrieved = service.get_sale(uuid4())
    
    assert retrieved is None

def test_get_all_sales(db_session):
    service = create_service(db_session)
    sale = create_valid_sale(service)
    sales = service.get_all_sales()
    
    assert any(item.id == sale.id for item in sales)

def test_update_sale(db_session):
    service = create_service(db_session)
    sale = create_valid_sale(service)
    
    updated = service.update_sale(
        sale.id,
        subtotal=Decimal("60000.00"),
        discount=Decimal("10000.00"),
        total_amount=Decimal("50000.00"),
        amount_paid=Decimal("25000.00"),
        remaining_balance=Decimal("25000.00"),
        payment_status="PARTIAL",
        collection_status="PENDING_COLLECTION",
        notes="Updated sale"
        )
    assert updated.subtotal == Decimal("60000.00")
    assert updated.discount == Decimal("10000.00")
    assert updated.total_amount == Decimal("50000.00")
    assert updated.amount_paid == Decimal("25000.00")
    assert updated.remaining_balance == Decimal("25000.00")
    assert updated.payment_status == "PARTIAL"
    assert updated.collection_status == "PENDING_COLLECTION"
    assert updated.notes == "Updated sale"

def test_update_sale_partial_update(db_session):
    service = create_service(db_session)
    sale = create_valid_sale(service)    
    updated = service.update_sale(
        sale.id,
        notes="Only notes changed"
        )
    
    assert updated.notes == "Only notes changed"
    assert updated.total_amount == Decimal("45000.00")
    assert updated.amount_paid == Decimal("20000.00")

def test_update_sale_rejects_nonexistent_sale(db_session):
    service = create_service(db_session)
    
    with pytest.raises(
        ValueError,
        match="does not exist"
        ):
        
        service.update_sale(
            uuid4(),
            notes="Nobody"
            )

@pytest.mark.parametrize(
    "field,value,error_message",
    [
        (
            "subtotal",
            Decimal("-1.00"),
            "Subtotal cannot be negative"
            ),
        (
            "discount",
            Decimal("-1.00"),
            "Discount cannot be negative",
            ),
        (
            "total_amount",
            Decimal("-1.00"),
            "Total amount cannot be negative"
            ),
        (
            "amount_paid",
            Decimal("-1.00"),
            "Amount paid cannot be negative"
            ),
        (
            "remaining_balance",
            Decimal("-1.00"),
            "Remaining balance cannot be negative"
            ),
        ]
    )

def test_update_sale_rejects_negative_values(
    db_session,
    field,
    value,
    error_message):
    
    service = create_service(db_session)
    sale = create_valid_sale(service)
    
    with pytest.raises(
        ValueError,
        match=error_message
        ):
        
        service.update_sale(
            sale.id,
            **{field: value},
            )

def test_update_sale_rejects_amount_paid_greater_than_total(db_session):
    service = create_service(db_session)
    
    sale = create_valid_sale(service)
    
    with pytest.raises(
        ValueError,
        match="Amount paid cannot be greater than total amount"
        ):
       
        service.update_sale(
            sale.id,
            amount_paid=Decimal("60000.00")
            )

@pytest.mark.parametrize(
    "payment_status",
    ["INVALID", "", "CANCELLED"])

def test_update_sale_rejects_invalid_payment_status(
    db_session,
    payment_status):
    
    service = create_service(db_session)
    sale = create_valid_sale(service)
    
    with pytest.raises(
        ValueError,
        match="Invalid payment status"
        ):
        service.update_sale(
            sale.id,
            payment_status=payment_status,
            )

@pytest.mark.parametrize(
    "collection_status",
    ["INVALID", "", "DELIVERED"])

def test_update_sale_rejects_invalid_collection_status(
    db_session,
    collection_status):
    
    service = create_service(db_session)
    sale = create_valid_sale(service)
    
    with pytest.raises(ValueError, match="Invalid collection_status"):
        service.update_sale(
            sale.id,
            collection_status=collection_status
            )