import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, DateTime, func, Text, Numeric, CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

class Sale(Base):
    __tablename__ = "sales"
    
    __table_args__ = (
        CheckConstraint(
            "subtotal >= 0", name="ck_sale_subtotal_non_negative"), 
        CheckConstraint(
            "discount >= 0", name="ck_sale_discount_non_negative"),
        CheckConstraint(
            "total_amount >= 0", name="ck_sale_total_amount_non_negative"),
        CheckConstraint(
            "amount_paid >= 0", name="ck_sale_amount_paid_non_negative"),
        CheckConstraint(
            "remaining_balance >= 0", name="ck_sale_remaining_balance_non_negative"),
        CheckConstraint(
            "amount_paid <= total_amount", name="ck_sale_amount_paid_not_greater_than_total"),
        CheckConstraint(
            "payment_status IN ('PAID', 'PARTIAL', 'UNPAID')", name="ck_sale_payment_status"),
        CheckConstraint(
            "collection_status IN ('COLLECTED', 'PENDING_COLLECTION')", name="ck_sale_collection_status"),
    )
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    sale_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    remaining_balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_status: Mapped[str] = mapped_column(String(20), nullable=False)
    collection_status: Mapped[str] = mapped_column(String(30), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    customer: Mapped["Customer"] = relationship(back_populates="sales")
    items: Mapped[list["SaleItem"]] = relationship(back_populates="sale", cascade="all, delete-orphan")
    payments: Mapped[list["Payment"]] = relationship(back_populates="sale")