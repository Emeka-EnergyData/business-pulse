import streamlit as st
from datetime import datetime, timezone
from decimal import Decimal

from src.database.session import get_db

from src.repositories.sales_repository import SalesRepository
from src.repositories.payment_repository import PaymentRepository
from src.repositories.customer_repository import CustomerRepository

from src.services.payment_service import PaymentService


st.set_page_config(
    page_title="Credit",
    layout="wide",
)

# Session State

if "credit_success" not in st.session_state:
    st.session_state.credit_success = None

# Database

db = next(get_db())

try:
    
    # Repositories
    
    sales_repository = SalesRepository(db)
    payment_repository = PaymentRepository(db)
    customer_repository = CustomerRepository(db)

    # Services    

    payment_service = PaymentService(
        payment_repository=payment_repository,
        sales_repository=sales_repository,
    )

    # Page Header
    
    st.title("Credit")
    st.write(
        "Track outstanding customer balances and record payments."
    )

    # Success Message

    if (
        st.session_state.credit_success
    ):

        st.success(
            st.session_state.credit_success
        )

        st.session_state.credit_success = None
    
    # Load Customers    

    customers = customer_repository.get_all()


    # Find customers with outstanding credit

    credit_customers = []

    for customer in customers:

        credit_sales = [
            sale
            for sale in sales_repository.get_all()
            if (
                sale.customer_id == customer.id
                and sale.remaining_balance > 0
            )
        ]

        if credit_sales:
            credit_customers.append(
                customer
            )

    # Credit Summary
    
    all_credit_sales = [
        sale
        for sale in sales_repository.get_all()
        if sale.remaining_balance > 0
        and sale.customer_id is not None
    ]

    total_credit = sum(
        (
            sale.remaining_balance
            for sale in all_credit_sales
        ),
        Decimal("0.00"),
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Customers With Credit",
            len(credit_customers),
        )

    with col2:

        st.metric(
            "Outstanding Sales",
            len(all_credit_sales),
        )

    with col3:

        st.metric(
            "Total Outstanding Credit",
            f"₦{total_credit:,.2f}",
        )
    
    # No Credit
    
    if not credit_customers:

        st.info(
            "There are no outstanding customer credits."
        )

    else:

        st.divider()

        st.subheader("Customers With Outstanding Credit")

        # Customer Selection        

        customer_options = {
            customer.name: customer.id
            for customer in credit_customers
        }

        selected_customer_name = st.selectbox(
            "Customer",
            options=list(customer_options.keys()),
        )

        selected_customer_id = (
            customer_options[
                selected_customer_name
            ]
        )

        selected_customer = (
            customer_repository.get_by_id(
                selected_customer_id
            )
        )
        
        # Customer Credit
        
        customer_sales = [
            sale
            for sale in sales_repository.get_all()
            if (
                sale.customer_id == selected_customer_id
                and sale.remaining_balance > 0
            )
        ]

        customer_balance = sum(
            (
                sale.remaining_balance
                for sale in customer_sales
            ),
            Decimal("0.00"),
        )

        st.write(
            f"### {selected_customer.name}"
        )

        st.metric(
            "Outstanding Balance",
            f"₦{customer_balance:,.2f}",
        )
        
        # Outstanding Sales        

        st.divider()

        st.subheader("Outstanding Sales")

        for sale in customer_sales:

            with st.expander(
                f"{sale.sale_date.strftime('%d %b %Y')}  |  "
                f"Total: ₦{sale.total_amount:,.2f}  |  "
                f"Balance: ₦{sale.remaining_balance:,.2f}"
            ):

                # Sale Information
                
                col1, col2, col3 = st.columns(3)

                with col1:

                    st.write(
                        f"**Sale Total**  \n"
                        f"₦{sale.total_amount:,.2f}"
                    )

                with col2:

                    st.write(
                        f"**Amount Paid**  \n"
                        f"₦{sale.amount_paid:,.2f}"
                    )

                with col3:

                    st.write(
                        f"**Remaining**  \n"
                        f"₦{sale.remaining_balance:,.2f}"
                    )
                
                # Products
                
                st.write("**Products**")

                for item in sale.items:

                    line_total = (
                        item.quantity
                        * item.unit_price
                    )

                    col1, col2, col3 = st.columns(3)

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
                            f"₦{line_total:,.2f}"
                        )
                
                # Record Payment
                
                st.divider()

                st.write("**Record Payment**")

                payment_amount = st.number_input(
                    "Payment Amount",
                    min_value=0.01,
                    max_value=float(
                        sale.remaining_balance
                    ),
                    step=100.0,
                    value=float(
                        sale.remaining_balance
                    ),
                    key=f"payment_amount_{sale.id}",
                )

                payment_method = st.selectbox(
                    "Payment Method",
                    options=[
                        "Cash",
                        "Transfer",
                        "POS",
                        "Other",
                    ],
                    key=f"payment_method_{sale.id}",
                )

                payment_date = st.date_input(
                    "Payment Date",
                    value=datetime.now().date(),
                    key=f"payment_date_{sale.id}",
                )

                reference = st.text_input(
                    "Reference",
                    placeholder="Optional payment reference",
                    key=f"payment_reference_{sale.id}",
                )

                payment_notes = st.text_area(
                    "Payment Notes",
                    placeholder="Optional notes about this payment",
                    key=f"payment_notes_{sale.id}",
                )

                if st.button(
                    "Record Payment",
                    type="primary",
                    use_container_width=True,
                    key=f"record_payment_{sale.id}",
                ):

                    try:

                        payment_service.record_payment(
                            sale_id=sale.id,
                            amount=Decimal(
                                str(payment_amount)
                            ),
                            payment_method=payment_method,
                            payment_date=datetime.combine(
                                payment_date,
                                datetime.min.time(),
                                tzinfo=timezone.utc,
                            ),
                            reference=reference or None,
                            notes=payment_notes or None,
                        )

                        st.session_state.credit_success = (
                            f"₦{payment_amount:,.2f} payment "
                            f"recorded for "
                            f"{selected_customer.name}."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Could not record payment: {e}"
                        )
    
    # Payment History

    st.divider()

    st.subheader("Payment History")

    payments = payment_service.get_all_payment()

    if not payments:

        st.info(
            "No payments have been recorded yet."
        )

    else:

        payments = sorted(
            payments,
            key=lambda payment: payment.payment_date,
            reverse=True,
        )

        for payment in payments:

            sale = sales_repository.get_by_id(
                payment.sale_id
            )

            if sale is None:
                continue

            if sale.customer:
                customer_name = sale.customer.name

            else:
                customer_name = "Walk-in Customer"

            with st.expander(
                f"{payment.payment_date.strftime('%d %b %Y')}  |  "
                f"{customer_name}  |  "
                f"₦{payment.amount:,.2f}"
            ):

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.write(
                        f"**Customer**  \n"
                        f"{customer_name}"
                    )

                with col2:

                    st.write(
                        f"**Amount**  \n"
                        f"₦{payment.amount:,.2f}"
                    )

                with col3:

                    st.write(
                        f"**Method**  \n"
                        f"{payment.payment_method}"
                    )

                st.write(
                    f"**Payment Date:** "
                    f"{payment.payment_date.strftime('%d %b %Y')}"
                )

                if payment.reference:

                    st.write(
                        f"**Reference:** "
                        f"{payment.reference}"
                    )

                if payment.notes:

                    st.write(
                        f"**Notes:** "
                        f"{payment.notes}"
                    )

finally:

    db.close()