from datetime import date
from decimal import Decimal

from src.repositories.sales_repository import SalesRepository
from src.repositories.purchase_repository import PurchaseRepository


class ReportsService:
    def __init__(
        self,
        sales_repository: SalesRepository,
        purchase_repository: PurchaseRepository,
    ):
        self.sales_repository = sales_repository
        self.purchase_repository = purchase_repository

    def get_sales_summary(
        self,
        start_date: date,
        end_date: date,
    ) -> dict:
        sales = self.sales_repository.get_sales_between_dates(
            start_date,
            end_date,
        )

        total_sales = Decimal("0.00")
        total_paid = Decimal("0.00")
        total_credit = Decimal("0.00")

        for sale in sales:
            total_sales += sale.total_amount
            total_paid += sale.amount_paid
            total_credit += sale.remaining_balance

        return {
            "number_of_sales": len(sales),
            "total_sales": total_sales,
            "total_paid": total_paid,
            "total_credit": total_credit,
        }

    def get_purchase_summary(
        self,
        start_date: date,
        end_date: date,
    ) -> dict:
        purchases = self.purchase_repository.get_purchases_between_dates(
            start_date,
            end_date,
        )

        total_purchases = Decimal("0.00")

        for purchase in purchases:
            for item in purchase.items:
                total_purchases += (
                    item.quantity * item.unit_cost
                )

        return {
            "number_of_purchases": len(purchases),
            "total_purchases": total_purchases,
        }

    def get_business_summary(
        self,
        start_date: date,
        end_date: date,
    ) -> dict:
        sales_summary = self.get_sales_summary(
            start_date,
            end_date,
        )

        purchase_summary = self.get_purchase_summary(
            start_date,
            end_date,
        )

        return {
            **sales_summary,
            **purchase_summary,
        }