from uuid import UUID
from datetime import date,datetime, time, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.database.models.sales import Sale

class SalesRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create(self, sale: Sale) -> Sale:
        self.db.add(sale)
        self.db.flush()
        self.db.refresh(sale)
        
        return sale
    
    def get_by_id(self, sale_id: UUID) -> Sale | None:
        stmt = select(Sale).where(Sale.id == sale_id)
        
        return self.db.scalar(stmt)
    
    def get_all(self) -> list[Sale]:
        return self.db.query(Sale).all()
    
    def update(self, sale: Sale) -> Sale:
        self.db.flush()
        self.db.refresh(sale)
        
        return sale
        
    def get_credit_sales(self, customer_id: UUID) -> list[Sale]:
        stmt = (
            select(Sale)
            .where(Sale.customer_id == customer_id,
                   Sale.remaining_balance > 0)
            .order_by(Sale.sale_date.asc())
        )
        
        return list(self.db.scalars(stmt).all())
    
    def get_sales_between_dates(self, start_date: date, end_date: date) -> list[Sale]:
        start_datetime = datetime.combine(
                start_date,
                time.min,
                tzinfo=timezone.utc,
            )

        end_datetime = datetime.combine(
                end_date,
                time.max,
                tzinfo=timezone.utc,
            )

        stmt = (
                select(Sale)
                .where(
                    Sale.sale_date >= start_datetime,
                    Sale.sale_date <= end_datetime,
                )
                .order_by(Sale.sale_date.asc())
            )

        return list(self.db.scalars(stmt).all())