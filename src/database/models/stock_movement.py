import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, func, Text, CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.base import Base

class StockMovement(Base):
    __tablename__ = "stock_movements"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), nullable=False)
    movement_type: Mapped[str] = mapped_column(String(30), nullable=False)  # e.g., 'in' or 'out'
    quantity: Mapped[int] = mapped_column(nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(30), nullable=False)
    reference_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    movement_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    product: Mapped["Product"] = relationship(back_populates="stock_movements")
    
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_stock_movement_quantity_positive"),
        CheckConstraint("movement_type IN ('RECEIVED', 'SOLD', 'DAMAGE', 'STOLEN', 'ADJUSTMENT')", name="ck_stock_movement_movement_type"),
    )