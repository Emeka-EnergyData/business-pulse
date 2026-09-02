import streamlit as st
from datetime import datetime, timezone, timedelta
from decimal import Decimal

import altair as alt
import pandas as pd

from src.database.session import get_db

from src.repositories.sales_repository import SalesRepository
from src.repositories.sale_item_repository import SaleItemRepository
from src.repositories.purchase_repository import PurchaseRepository
from src.repositories.purchase_item_repository import PurchaseItemRepository
from src.repositories.product_repository import ProductRepository
from src.repositories.customer_repository import CustomerRepository
from src.repositories.supplier_repository import SupplierRepository

from src.services.reports_service import ReportsService

# PAGE CONFIGURATION

st.set_page_config(
    page_title="Business Pulse",
    layout="wide")

# VISUAL STYLING

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;        
        padding-bottom: 3rem;
        }
        
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 12px;
        padding: 16px 18px;
        min-height: 105px;
        }
        
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        font-weight: 600;
        }
        
    div[data-testid="stMetricValue"] {
        font-size: 1.55rem;
        font-weight: 700;
        }
        
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        }
    h2, h3, h4 {
        margin-bottom: 0.2rem;
        }
    </style>
    """,
    unsafe_allow_html=True)

# PAGE HEADER

st.title("Business Pulse")

# DATABASE

db = next(get_db())

try:
    # REPOSITORIES
    
    sales_repository = SalesRepository(db)
    sale_item_repository = SaleItemRepository(db)
    
    purchase_repository = PurchaseRepository(db)
    purchase_item_repository = PurchaseItemRepository(db)
    
    product_repository = ProductRepository(db)
    customer_repository = CustomerRepository(db)
    supplier_repository = SupplierRepository(db)
    
    reports_service = ReportsService(
        sales_repository=sales_repository,
        purchase_repository=purchase_repository
        )
    
    # DATE
    
    today = datetime.now(timezone.utc).date()
    
    seven_days_ago = today - timedelta(days=6)
    
    st.caption(
        f"Dashboard for {today.strftime('%d %b %Y')}"
        )
    
    # LOAD DATA
    
    sales = sales_repository.get_all()
    sale_items = sale_item_repository.get_all()
    
    purchases = purchase_repository.get_all()
    purchase_items = purchase_item_repository.get_all()
    
    products = product_repository.get_all()
    customers = customer_repository.get_all()
    suppliers = supplier_repository.get_all()
    
    # TODAY'S SALES
    
    todays_sales = [
        sale for sale in sales if sale.sale_date.date() == today
        ]
    
    todays_revenue = sum(
        (
            sale.total_amount for sale in todays_sales
            ),
        Decimal("0.00")
        )
 
    todays_sale_count = len(todays_sales)

    # TODAY'S PROFIT
    
    todays_sale_ids = {
        sale.id
        for sale in todays_sales
        }
    
    todays_sale_items = [
        item for item in sale_items if item.sale_id in todays_sale_ids
        ]
    
    todays_profit = sum(
        (
            item.line_total - (item.cost_price * item.quantity)
            for item in todays_sale_items
            ),
        Decimal("0.00")
        )

    # OUTSTANDING CREDIT
    outstanding_credit = sum(
        (
         sale.remaining_balance for sale in sales if sale.remaining_balance > 0
         ),
        Decimal("0.00")
        )
    
    # LOW STOCK
    LOW_STOCK_THRESHOLD = 5
    low_stock_products = [
        product for product in products
        if product.is_active
        and product.current_stock <= LOW_STOCK_THRESHOLD
        ]

    # INVENTORY
    active_products = [
        product for product in products if product.is_active
        ]
    
    total_stock_units = sum(
        product.current_stock
        for product in active_products
        )
    
    inventory_value = sum(
        (
            product.current_stock * product.cost_price for product in active_products
            ),
        Decimal("0.00")
        )

    # SALES PERFORMANCE
    
    daily_sales = reports_service.get_daily_sale(
        start_date=seven_days_ago,
        end_date=today,
        )
    
    sales_by_date =  {
        row["date"]: row["total_sales"] for row in daily_sales
        }
    
    sales_chart_data = [
        {
            "date": current_date,
            "sales": float(sales_by_date.get(current_date, Decimal("0.00")))
        } for current_date in (seven_days_ago + timedelta(days=i) for i in range(7))
    ]
    
    sales_chart_df = pd.DataFrame(sales_chart_data)

    # TODAY'S SNAPSHOT
    
    st.subheader("Today's Snapshot")
    
    st.caption(
        "Key indicators showing what is happening today."
        )
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Sales",
            todays_sale_count,
            )
        
    with col2:
        st.metric(
            "Revenue",
            f"₦{todays_revenue:,.2f}",
            )
        
    with col3:
        st.metric(
            "Gross Profit",
            f"₦{todays_profit:,.2f}"
            )
    
    with col4:
        st.metric(
            "Outstanding Credit",
            f"₦{outstanding_credit:,.2f}",
            )
        
    
    st.divider()

    
    # SALES PERFORMANCE
    
    st.subheader("Sales Performance")
    st.caption(
        "Daily sales revenue over the last 7 days."
        )
    if sales_chart_data:
        chart = (
            alt.Chart(
                sales_chart_df
                ).mark_line(
                    point=True,
                    strokeWidth=3
                    )
                .encode(
                    x=alt.X(
                        "date:T", 
                        title=None,
                        axis=alt.Axis(format="%d %b", labelAngle=0)
                        ),
                    
                    y=alt.Y(
                        "sales:Q",
                        title="Revenue (₦)",
                        axis=alt.Axis(format=",.2f")
                        ),
                    
                    tooltip=[
                        alt.Tooltip("date:T", title="Date", format="%d %b %Y"),
                        alt.Tooltip("sales:Q", title="Revenue (₦)", format=",.2f")
                    ]
                )
                .properties(
                    height =320
                    )
            )
        
        st.altair_chart(
            chart,
            use_container_width=True
            )

    else:
        st.info(
            "No sales recorded in the last 7 days."
            )

    st.divider()
    
    # BUSINESS POSITION 
    st.subheader("Business Position")
    
    st.caption(
            "Current inventory and business records."
            )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Customers",
            len(customers),
        )
        st.metric(
            "Suppliers",
            len(suppliers)
            )
                        
    with col2:          
        st.metric(
            "Products",
            len(active_products)
            )
        
        st.metric(
            "Low Stock Products",
            len(low_stock_products)
            )
                
    with col3:  
        st.metric(
            "Stock Units",
            total_stock_units
            )  
        
        st.metric(
            "Inventory Value",
            f"₦{inventory_value:,.2f}"
            )
    
    st.divider()

    # INVENTORY ALERTS
    
    st.subheader("Inventory Alerts")
    st.caption(
        "Products requiring attention because their stock "
               f"is {LOW_STOCK_THRESHOLD} units or less."
               )
    
    if low_stock_products:
        
        low_stock_data = [
            {
                "Product": product.name,
                "Stock": product.current_stock,
                "Status": "Low stock",
                }
            for product in sorted(
                low_stock_products,
                key=lambda product: product.current_stock,
                )
            ]
        
        st.dataframe(
            low_stock_data,
            width="stretch",
            hide_index=True,
            height=220,
            )
        
        st.warning(
            f"{len(low_stock_products)} product(s) are low on stock."
            )
                        
    else:
        st.success(
            "Inventory looks healthy. "
            "No products are currently low on stock."
            )

    st.divider()

    
    # RECENT SALES
    
    st.subheader("Recent Sales")
    st.caption(
        "The latest customer transactions recorded."
        )
    recent_sales = sorted(
        sales,
        key=lambda sale: sale.sale_date,
        reverse=True,
        )[:10]
    if recent_sales:
        recent_sales_data = []
        for sale in recent_sales:
            customer_name = "Walk-in Customer"
            if sale.customer is not None:
                customer_name = sale.customer.name
            recent_sales_data.append(
                {
                    "Date": sale.sale_date.strftime(
                        "%d %b %Y"
                        ),
                    "Customer": customer_name,
                    "Status": sale.payment_status,
                    "Amount": f"₦{sale.total_amount:,.2f}",
                    }
                )
        st.dataframe(
            recent_sales_data,
            width="stretch",
            hide_index=True,
            height=300,
            )
    else:
        st.info(
            "No sales have been recorded yet."
            )

    st.divider()

     
    # RECENT PURCHASES  
    
    st.subheader("Recent Purchases")
    st.caption(
        "The latest inventory purchases recorded."
        )
    recent_purchases = sorted(
        purchases,
        key=lambda purchase: purchase.purchase_date,
        reverse=True
        )[:10]
    if recent_purchases:
        recent_purchase_data = []
        for purchase in recent_purchases:
            supplier_name = "Unknown Supplier"
            if purchase.supplier is not None:
                supplier_name = purchase.supplier.name
            purchase_total = sum(
                (
                    item.quantity * item.unit_cost
                    for item in purchase.items
                    ),
                Decimal("0.00")
                )
            recent_purchase_data.append(
                {
                    "Date": purchase.purchase_date.strftime(
                        "%d %b %Y"
                        ),
                    "Supplier": supplier_name,
                    "Amount": f"₦{purchase_total:,.2f}",
                    }
                )
        st.dataframe(
            recent_purchase_data,
            width="stretch",
            hide_index=True,
            height=300,
            )
    else:
        st.info(
            "No purchases have been recorded yet."
            )

finally:
    db.close()