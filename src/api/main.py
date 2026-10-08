from fastapi import FastAPI
from datetime import datetime, timezone, timedelta
from src.database.session import get_db

from src.repositories.sales_repository import SalesRepository
from src.repositories.sale_item_repository import SaleItemRepository
from src.repositories.purchase_repository import PurchaseRepository
from src.repositories.product_repository import ProductRepository
from src.repositories.customer_repository import CustomerRepository
from src.repositories.supplier_repository import SupplierRepository

from src.services.reports_service import ReportsService

app = FastAPI(
    title="Business Pulse API",
    description="API for the Business Pulse application",
    version="1.0.0"
    )

@app.get("/api/health")
def health_check():
    return {"status":"ok"}

@app.get("/api/dashboard")
def get_dashboard():
    db = next(get_db())
    
    try:
        sales_repository = SalesRepository(db)
        sale_item_repository = SaleItemRepository(db)
        purchase_repository = PurchaseRepository(db)
        product_repository = ProductRepository(db)
        customer_repository = CustomerRepository(db)
        supplier_repository = SupplierRepository(db)

        reports_service = ReportsService(
            sales_repository=sales_repository,
            purchase_repository=purchase_repository,
        )

        today = datetime.now(timezone.utc).date()
        seven_days_ago = today - timedelta(days=6)

        sales = sales_repository.get_all()
        sale_items = sale_item_repository.get_all()
        purchases = purchase_repository.get_all()
        products = product_repository.get_all()
        customers = customer_repository.get_all()
        suppliers = supplier_repository.get_all()

        # Today's sales
        todays_sales = [
            sale
            for sale in sales
            if sale.sale_date.date() == today
        ]

        todays_revenue = sum(
            sale.total_amount
            for sale in todays_sales
        )

        todays_sale_ids = {
            sale.id
            for sale in todays_sales
        }

        todays_sale_items = [
            item
            for item in sale_items
            if item.sale_id in todays_sale_ids
        ]

        todays_profit = sum(
            (item.unit_price - item.cost_price) * item.quantity
            for item in todays_sale_items
        )

        # Outstanding credit
        outstanding_credit = sum(
            sale.remaining_balance
            for sale in sales
            if sale.remaining_balance > 0
        )

        # Inventory
        low_stock_threshold = 5

        active_products = [
            product
            for product in products
            if product.is_active
        ]

        low_stock_products = [
            product
            for product in active_products
            if product.current_stock <= low_stock_threshold
        ]

        total_stock_units = sum(
            product.current_stock
            for product in active_products
        )

        inventory_value = sum(
            product.current_stock * product.cost_price
            for product in active_products
        )

        # Seven-day sales performance
        daily_sales = reports_service.get_daily_sale(
            start_date=seven_days_ago,
            end_date=today,
        )

        # Recent sales
        recent_sales = sorted(
            sales,
            key=lambda sale: sale.sale_date,
            reverse=True,
        )[:10]

        # Recent purchases
        recent_purchases = sorted(
            purchases,
            key=lambda purchase: purchase.purchase_date,
            reverse=True,
        )[:10]

        return {
            "today": today,
            "snapshot": {
                "sales_count": len(todays_sales),
                "revenue": todays_revenue,
                "gross_profit": todays_profit,
                "outstanding_credit": outstanding_credit,
            },
            "sales_performance": daily_sales,
            "business_position": {
                "customers": len(customers),
                "suppliers": len(suppliers),
                "products": len(active_products),
                "low_stock_products": len(low_stock_products),
                "stock_units": total_stock_units,
                "inventory_value": inventory_value,
            },
            "low_stock_products": [
                {
                    "id": str(product.id),
                    "name": product.name,
                    "current_stock": product.current_stock,
                }
                for product in low_stock_products
            ],
            "recent_sales": [
                {
                    "id": str(sale.id),
                    "date": sale.sale_date,
                    "customer": (
                        sale.customer.name
                        if sale.customer
                        else "Walk-in Customer"
                    ),
                    "status": sale.payment_status,
                    "amount": sale.total_amount,
                }
                for sale in recent_sales
            ],
            "recent_purchases": [
                {
                    "id": str(purchase.id),
                    "date": purchase.purchase_date,
                    "supplier": (
                        purchase.supplier.name
                        if purchase.supplier
                        else None
                    ),
                    "amount": sum(
                        item.quantity * item.unit_cost
                        for item in purchase.items
                    ),
                }
                for purchase in recent_purchases
            ],
        }

    finally:
        db.close()