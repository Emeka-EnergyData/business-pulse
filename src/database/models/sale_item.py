import uuid
from decimal import Decimal

from sqlalchemy import CheckConstraint, Numeric, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

class SaleItem(Base):
    __tablename__ = "sale_items"
    
    __table_args__ = (
        CheckConstraint(
            "quantity > 0", name="ck_sale_item_quantity_positive"),
        CheckConstraint(
            "unit_price > 0", name="ck_sale_item_unit_price_positive"),
        CheckConstraint(
            "cost_price >= 0", name="ck_sale_item_cost_price_non_negative"),
        CheckConstraint(
            "line_total >= 0", name="ck_sale_item_line_total_non_negative"),
    )
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sale_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sales.id"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    sale: Mapped["Sale"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="sale_items")