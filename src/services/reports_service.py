from datetime import date, timedelta
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
            
        number_of_sales = len(sales)
            
        if number_of_sales > 0:
            average_sale = total_sales/number_of_sales
                
        else:
            average_sale = Decimal("0.00")
                
        if total_sales > 0:
            collection_rate =(total_paid/total_sales) * Decimal("100")
                
            credit_rate = (total_credit/total_sales) * Decimal("100")
                
        else:
            collection_rate = Decimal("0.00")
            credit_rate = Decimal("0.00")

        return {
            "number_of_sales": len(sales),
            "total_sales": total_sales,
            "total_paid": total_paid,
            "total_credit": total_credit,
            "average_sale": average_sale,
            "collection_rate":collection_rate,
            "credit_rate":credit_rate
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
        
    def get_daily_sale(
        self,
        start_date: date,
        end_date: date
    ) -> list[dict]:
        """
        Return daily sales totals for the selected date range
        """
        
        results = self.sales_repository.get_daily_sales_between_dates(start_date, end_date)
        
        sales_by_date = {
            sale_day: total_sales for sale_day, total_sales in results
        }
        
        daily_sales = []
        
        current_date = start_date
        
        while current_date <= end_date:
            daily_sales.append(
                {
                    "date": current_date,
                    "total_sales": sales_by_date.get(current_date, Decimal("0.00"))
                    }
                )
            
            current_date += timedelta(days=1)
        
        return daily_sales 