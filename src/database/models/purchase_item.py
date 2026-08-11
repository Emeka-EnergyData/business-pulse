import uuid
from decimal import Decimal

from sqlalchemy import Numeric, ForeignKey, CheckConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.database.base import Base

class PurchaseItem(Base):
    __tablename__ = "purchase_items"
    
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_purchase_item_quantity_positive"),
        CheckConstraint("unit_cost >= 0", name="ck_purchase_item_unit_cost_non_negative"),
    )
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    purchase_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("purchases.id"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    purchase: Mapped["Purchase"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="purchase_items")