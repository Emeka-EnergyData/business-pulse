import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import UUID, ForeignKey, func, String, Numeric, DateTime, Boolean, Integer, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base 

class Product(Base):
    __tablename__ = "products"
    
    __table_args__ = (
        CheckConstraint("cost_price >= 0", name="ck_cost_price_non_negative"),
        CheckConstraint("target_price >= minimum_price", name="ck_target_price_gte_minimum"),
        CheckConstraint("minimum_price >= cost_price", name="ck_minimum_price_gte_cost"),
        CheckConstraint("current_stock >= 0", name="ck_current_stock_non_negative"),
    )
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    target_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    minimum_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    current_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    category: Mapped["Category"] = relationship("Category", back_populates="products")
    purchase_items: Mapped[list["PurchaseItem"]] = relationship(back_populates="product")
    sale_items: Mapped[list["SaleItem"]] = relationship(back_populates="product")
    stock_movements: Mapped[list["StockMovement"]] = relationship(back_populates="product")