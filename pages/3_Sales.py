import streamlit as st
from datetime import datetime, timezone
from decimal import Decimal

from src.database.session import get_db

from src.repositories.sales_repository import SalesRepository
from src.repositories.sale_item_repository import SaleItemRepository
from src.repositories.product_repository import ProductRepository
from src.repositories.stock_movement_repository import StockMovementRepository
from src.repositories.customer_repository import CustomerRepository
from src.repositories.payment_repository import PaymentRepository

from src.services.payment_service import PaymentService
from src.services.sales_service import SaleService
from src.services.sale_item_services import SaleItemService


st.set_page_config(
    page_title="Sales",
    layout="wide",
)

# Session State

if "sale_items" not in st.session_state:
    st.session_state.sale_items = []

if "sale_success" not in st.session_state:
    st.session_state.sale_success = None

# Database

db = next(get_db())

try:

    # Repositories    

    sales_repository = SalesRepository(db)
    sale_item_repository = SaleItemRepository(db)
    product_repository = ProductRepository(db)
    stock_movement_repository = StockMovementRepository(db)
    customer_repository = CustomerRepository(db)
    payment_repository = PaymentRepository(db)

    # Services    

    sale_service = SaleService(
        sales_repository
    )

    sale_item_service = SaleItemService(
        sale_item_repository=sale_item_repository,
        product_repository=product_repository,
        stock_movement_repository=stock_movement_repository,
        sales_repository=sales_repository,
    )
    
    payment_service = PaymentService(
        payment_repository = payment_repository, 
        sales_repository= sales_repository
        )
    
    # Load Data

    products = product_repository.get_active()
    customers = customer_repository.get_all()
    
    # Page Header

    st.title("Sales")
    st.write(
        "Record customer sales and update inventory."
    )

    # Sale Entry
    
    if not products:

        st.warning(
            "No active products found. Create an active product first."
        )

    else:

        st.subheader("Sale Information")

        # Customer
        

        customer_options = {
            "Walk-in Customer": None
        }

        for customer in customers:
            customer_options[customer.name] = customer.id

        customer_name = st.selectbox(
            "Customer",
            options=list(customer_options.keys()),
        )


        # Sale Date
        

        sale_date = st.date_input(
            "Sale Date",
            value=datetime.now().date(),
        )
        
        # Collection Status

        collection_status = st.selectbox(
            "Collection Status",
            options=[
                "COLLECTED",
                "PENDING_COLLECTION",
            ],
            format_func=lambda value: (
                "Collected"
                if value == "COLLECTED"
                else "Pending Collection"
            ),
        )
        # Notes
    
        notes = st.text_area(
            "Notes",
            placeholder="Optional notes about this sale",
        )
        
        # Add Products

        st.divider()

        st.subheader("Add Products")

        product_options = {
            product.name: product.id
            for product in products
        }

        product_name = st.selectbox(
            "Product",
            options=list(product_options.keys()),
        )

        selected_product = next(
            product
            for product in products
            if product.id == product_options[product_name]
        )

        st.caption(
            f"Available stock: {selected_product.current_stock}"
        )

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            max_value=max(
                selected_product.current_stock,
                1
            ),
            step=1,
            value=1,
        )

        unit_price = st.number_input(
            "Unit Selling Price",
            min_value=0.01,
            step=100.0,
            value=float(selected_product.target_price),
        )

        # Add Item
        
        if st.button(
            "Add Item",
            use_container_width=True,
        ):

            existing_quantity = sum(
                item["quantity"]
                for item in st.session_state.sale_items
                if item["product_id"] == selected_product.id
            )

            if (
                existing_quantity + quantity
                > selected_product.current_stock
            ):

                st.error(
                    f"Insufficient stock. "
                    f"Available: {selected_product.current_stock}. "
                    f"Already added: {existing_quantity}."
                )

            else:

                item = {
                    "product_id": selected_product.id,
                    "product_name": selected_product.name,
                    "quantity": int(quantity),
                    "unit_price": Decimal(
                        str(unit_price)
                    ),
                }

                st.session_state.sale_items.append(
                    item
                )

                st.rerun()

        # Sale Items
        
        if (
            st.session_state.sale_success
            or st.session_state.sale_items
        ):
            
            # Success Message  

            if st.session_state.sale_success:

                st.success(
                    st.session_state.sale_success
                )

                st.session_state.sale_success = None

            # Items            

            if st.session_state.sale_items:

                st.divider()

                st.subheader("Items")

                header1, header2, header3, header4, header5 = st.columns([3, 1, 2, 2, 1])
                
                with header1:
                    st.write("**Product**")
                    
                with header2:
                    st.write("**Qty**")
                    
                with header3:
                    st.write("**Unit Price**")
                    
                with header4:
                    st.write("**Total Price**")
                
                subtotal = Decimal("0.00")

                for index, item in enumerate(
                    st.session_state.sale_items
                ):

                    item_total = (
                        item["quantity"]
                        * item["unit_price"]
                    )

                    subtotal += item_total

                    col1, col2, col3, col4, col5 = st.columns(
                        [3, 1, 2, 2, 1]
                    )

                    with col1:

                        st.write(
                            item["product_name"]
                        )

                    with col2:

                        st.write(
                            item["quantity"]
                        )

                    with col3:

                        st.write(
                            f"₦{item['unit_price']:,.2f}"
                        )

                    with col4:

                        st.write(
                            f"₦{item_total:,.2f}"
                        )

                    with col5:

                        if st.button(
                            "Remove",
                            key=f"remove_sale_item_{index}",
                        ):

                            st.session_state.sale_items.pop(
                                index
                            )

                            st.rerun()
                
                # Totals

                st.divider()

                col1, col2 = st.columns(2)

                with col1:

                    st.write(
                        f"**Subtotal: ₦{subtotal:,.2f}**"
                    )

                with col2:

                    discount = st.number_input(
                        "Discount",
                        min_value=0.0,
                        max_value=float(subtotal),
                        step=100.0,
                        value=0.0,
                    )

                discount = Decimal(
                    str(discount)
                )

                total_amount = (
                    subtotal - discount
                )

                st.divider()

                st.write(
                    f"### Total: ₦{total_amount:,.2f}"
                )
                
                # Payment

                amount_paid = st.number_input(
                    "Amount Paid",
                    min_value=0.0,
                    max_value=float(total_amount),
                    step=100.0,
                    value=float(total_amount),
                )

                amount_paid = Decimal(
                    str(amount_paid)
                )

                remaining_balance = (
                    total_amount - amount_paid
                )

                # Determine payment status

                if amount_paid == total_amount:

                    payment_status = "PAID"

                elif amount_paid > Decimal("0.00"):

                    payment_status = "PARTIAL"

                else:

                    payment_status = "UNPAID"

                st.write(
                    f"**Amount Paid: ₦{amount_paid:,.2f}**"
                )

                st.write(
                    f"**Remaining Balance: ₦{remaining_balance:,.2f}**"
                )

                st.write(
                    f"**Payment Status: {payment_status}**"
                )
                
                payment_method = st.selectbox(
                    "Payment Method",
                    options=[
                        "Cash",
                        "Bank Transfer",
                        "POS",
                        "Other"
                    ]
                )

                # Complete Sale                

                if st.button(
                    "Complete Sale",
                    type="primary",
                    use_container_width=True,
                ):

                    try:

                        # Create Sale Header                        

                        sale = sale_service.create_sale(
                            customer_id=customer_options[
                                customer_name
                            ],
                            sale_date=datetime.combine(
                                sale_date,
                                datetime.min.time(),
                                tzinfo=timezone.utc,
                            ),
                            subtotal=subtotal,
                            discount=discount,
                            total_amount=total_amount,
                            amount_paid=amount_paid,
                            remaining_balance=remaining_balance,
                            payment_status=payment_status,
                            collection_status=collection_status,
                            notes=notes or None,
                        )

                        # Create Sale Items                        

                        for item in st.session_state.sale_items:

                            sale_item_service.create_sale_item(
                                sale_id=sale.id,
                                product_id=item["product_id"],
                                quantity=item["quantity"],
                                unit_price=item["unit_price"],
                            )
                            
                        if amount_paid > Decimal("0.00"):
                            payment_service.create_payment(
                                sale_id = sale.id,
                                amount = amount_paid,
                                payment_method=payment_method,
                                payment_date = datetime.now(timezone.utc),
                                notes = "Initial payment"
                                )
                            
                        db.commit()
                        
                        # Clear Cart

                        st.session_state.sale_items = []
                        
                        # Success Message

                        st.session_state.sale_success = (
                            "Sale recorded successfully. "
                            "Stock has been updated."
                        )

                        st.rerun()

                    except Exception as e:
                        db.rollback()

                        st.error(
                            f"Could not record sale: {e}"
                        )

        else:

            st.info(
                "No products have been added to this sale yet."
            )
    
    # Sales History    

    st.divider()

    st.subheader("Sales History")

    sales = sales_repository.get_all()


    if not sales:

        st.info(
            "No sales have been recorded yet."
        )

    else:

        # Show newest sales first

        sales = sorted(
            sales,
            key=lambda sale: sale.sale_date,
            reverse=True,
        )

        for sale in sales:
                # Customer Name
            
            if sale.customer:

                display_customer = sale.customer.name

            else:

                display_customer = "Walk-in Customer"

                # Number of Items
            
            item_count = len(sale.items)


            # Sale Header
            
            with st.expander(
                f"{sale.sale_date.strftime('%d %b %Y')}  |  "
                f"{display_customer}  |  "
                f"₦{sale.total_amount:,.2f}  |  "
                f"{sale.payment_status}"
            ):
    
                # Sale Information                

                st.write("### Sale Information")

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.write(
                        f"**Customer:** {display_customer}"
                    )

                    st.write(
                        f"**Date:** "
                        f"{sale.sale_date.strftime('%d %b %Y')}"
                    )

                with col2:

                    st.write(
                        f"**Payment Status:** "
                        f"{sale.payment_status}"
                    )

                    st.write(
                        f"**Collection Status:** "
                        f"{sale.collection_status}"
                    )

                with col3:

                    st.write(
                        f"**Items:** {item_count}"
                    )

                    st.write(
                        f"**Notes:** "
                        f"{sale.notes or 'None'}"
                    )

                # Products Sold                

                st.divider()

                st.write("### Products Sold")

                for item in sale.items:

                    line_total = item.line_total

                    col1, col2, col3, col4 = st.columns(
                        [3, 1, 2, 2]
                    )

                    with col1:

                        st.write(
                            item.product.name
                        )

                    with col2:

                        st.write(
                            f"Qty: {item.quantity}"
                        )

                    with col3:

                        st.write(
                            f"₦{item.unit_price:,.2f}"
                        )

                    with col4:

                        st.write(
                            f"₦{line_total:,.2f}"
                        )
                
                # Sale Summary                

                st.divider()

                st.write("### Summary")

                col1, col2, col3, col4 = st.columns(4)

                with col1:

                    st.write(
                        f"**Subtotal**  \n"
                        f"₦{sale.subtotal:,.2f}"
                    )

                with col2:

                    st.write(
                        f"**Discount**  \n"
                        f"₦{sale.discount:,.2f}"
                    )

                with col3:

                    st.write(
                        f"**Total**  \n"
                        f"₦{sale.total_amount:,.2f}"
                    )

                with col4:

                    st.write(
                        f"**Paid**  \n"
                        f"₦{sale.amount_paid:,.2f}"
                    )

                st.write(
                    f"**Remaining Balance: "
                    f"₦{sale.remaining_balance:,.2f}**"
                )

finally:

    db.close()