import streamlit as st
from datetime import datetime, timezone
from decimal import Decimal

from src.database.session import get_db
from src.repositories.sales_repository import SalesRepository
from src.repositories.sale_item_repository import SaleItemRepository
from src.repositories.purchase_repository import PurchaseRepository
from src.repositories.purchase_item_repository import PurchaseItemRepository
from src.repositories.product_repository import ProductRepository
from src.repositories.customer_repository import CustomerRepository
from src.repositories.supplier_repository import SupplierRepository

st.set_page_config(
    page_title="Business Pulse",
    layout = "wide"
)

# Page Header

st.title("Business Pulse")

st.write(
        "Your business at a glance."
    )

# Database

db = next(get_db())

try:
    
    # Repositories

    sales_repository = SalesRepository(db)
    sale_item_repository = SaleItemRepository(db)

    purchase_repository = PurchaseRepository(db)
    purchase_item_repository = PurchaseItemRepository(db)

    product_repository = ProductRepository(db)
    customer_repository = CustomerRepository(db)
    supplier_repository = SupplierRepository(db)
    
    # Load Data
    
    sales = sales_repository.get_all()
    sale_items = sale_item_repository.get_all()

    purchases = purchase_repository.get_all()
    purchase_items = purchase_item_repository.get_all()

    products = product_repository.get_all()
    customers = customer_repository.get_all()
    suppliers = supplier_repository.get_all()

    # Date
    
    today = datetime.now(timezone.utc).date()

    # Dashboard Calculations
    
    # Today's sales

    todays_sales = [
        sale
        for sale in sales
        if sale.sale_date.date() == today
    ]


    todays_revenue = sum(
        (sale.total_amount for sale in todays_sales),
        Decimal("0.00"),
    )


    todays_sale_count = len(todays_sales)

    # Outstanding credit

    outstanding_credit = sum(
        (
            sale.remaining_balance
            for sale in sales
            if sale.remaining_balance > 0
        ),
        Decimal("0.00"),
    )

    # Low stock

    # For now, use 5 units as the low-stock threshold.
    low_stock_products = [
        product
        for product in products
        if product.is_active
        and product.current_stock <= 5
    ]

    # Inventory

    active_products = [
        product
        for product in products
        if product.is_active
    ]

    total_stock_units = sum(
        product.current_stock
        for product in active_products
    )

    inventory_value = sum(
        (
            product.current_stock * product.cost_price
            for product in active_products
        ),
        Decimal("0.00"),
    )
    
    # Profit    

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
        (
            item.line_total
            - (
                item.cost_price
                * item.quantity
            )
            for item in todays_sale_items
        ),
        Decimal("0.00"),
    )
    
    # Top Metrics   
    st.subheader("Top Metrics")
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Today's Sales",
            todays_sale_count,
        )

    with col2:

        st.metric(
            "Today's Revenue",
            f"₦{todays_revenue:,.2f}",
        )

    with col3:

        st.metric(
            "Outstanding Credit",
            f"₦{outstanding_credit:,.2f}",
        )

    with col4:

        st.metric(
            "Low Stock",
            len(low_stock_products),
        )

    st.divider()
    
    # Business Overview    

    st.subheader("Business Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Products",
            len(active_products),
        )

    with col2:

        st.metric(
            "Customers",
            len(customers),
        )


    with col3:

        st.metric(
            "Suppliers",
            len(suppliers),
        )

    with col4:

        st.metric(
            "Stock Units",
            total_stock_units,
        )

    st.write(
        f"**Inventory Value:** "
        f"₦{inventory_value:,.2f}"
    )

    st.divider()
    
    # Today's Performance
    
    st.subheader("Today's Performance")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Revenue",
            f"₦{todays_revenue:,.2f}",
        )

    with col2:

        st.metric(
            "Gross Profit",
            f"₦{todays_profit:,.2f}",
        )

    st.divider()
    
    # Low Stock Products   

    st.subheader("Low Stock Products")

    if low_stock_products:

        for product in sorted(
            low_stock_products,
            key=lambda product: product.current_stock,
        ):

            col1, col2, col3 = st.columns([4, 2, 2])

            with col1:

                st.write(
                    f"**{product.name}**"
                )

            with col2:

                st.write(
                    f"{product.current_stock} units"
                )


            with col3:

                st.write(
                    "Low stock"
                )

    else:

        st.success(
            "No products are currently low on stock."
        )


    st.divider()
    
    # Recent Sales
    
    st.subheader("Recent Sales")

    recent_sales = sorted(
        sales,
        key=lambda sale: sale.sale_date,
        reverse=True,
    )[:5]

    if recent_sales:

        for sale in recent_sales:

            customer_name = "Walk-in Customer"

            if sale.customer is not None:
                customer_name = sale.customer.name

            col1, col2, col3, col4 = st.columns(
                [2, 3, 2, 2]
            )

            with col1:

                st.write(
                    sale.sale_date.strftime(
                        "%d %b %Y"
                    )
                )

            with col2:

                st.write(
                    customer_name
                )

            with col3:

                st.write(
                    sale.payment_status
                )

            with col4:

                st.write(
                    f"₦{sale.total_amount:,.2f}"
                )

    else:

        st.info(
            "No sales recorded yet."
        )

    st.divider()
    
    # Recent Purchases
    
    st.subheader("Recent Purchases")

    recent_purchases = sorted(
        purchases,
        key=lambda purchase: purchase.purchase_date,
        reverse=True,
    )[:5]

    if recent_purchases:

        for purchase in recent_purchases:

            supplier_name = "Unknown Supplier"

            if purchase.supplier is not None:
                supplier_name = purchase.supplier.name

            col1, col2, col3 = st.columns(
                [2, 3, 2]
            )

            with col1:

                st.write(
                    purchase.purchase_date.strftime(
                        "%d %b %Y"
                    )
                )

            with col2:

                st.write(
                    supplier_name
                )

            with col3:

                purchase_total = sum(
                    (
                        item.quantity
                        * item.unit_cost
                        for item in purchase.items
                    ),
                    Decimal("0.00"),
                )

                st.write(
                    f"₦{purchase_total:,.2f}"
                )

    else:

        st.info(
            "No purchases recorded yet."
        )

finally:

    db.close()