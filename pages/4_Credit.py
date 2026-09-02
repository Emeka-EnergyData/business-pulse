import streamlit as st
from datetime import datetime, timezone
from decimal import Decimal

import pandas as pd

from src.database.session import get_db

from src.repositories.sales_repository import SalesRepository
from src.repositories.payment_repository import PaymentRepository
from src.repositories.customer_repository import CustomerRepository

from src.services.payment_service import PaymentService


# PAGE CONFIGURATION
st.set_page_config(
    page_title="Credit",
    layout="wide",
)


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
    unsafe_allow_html=True,
)


# SESSION STATE
if "credit_success" not in st.session_state:
    st.session_state.credit_success = None


# DATABASE
db = next(get_db())

try:

    # REPOSITORIES
    sales_repository = SalesRepository(db)
    payment_repository = PaymentRepository(db)
    customer_repository = CustomerRepository(db)


    # SERVICE
    payment_service = PaymentService(
        payment_repository=payment_repository,
        sales_repository=sales_repository,
    )


    # PAGE HEADER
    st.title("Credit")

    st.caption(
        "Track outstanding customer balances and record payments."
    )


    # SUCCESS MESSAGE
    if st.session_state.credit_success:

        st.success(
            st.session_state.credit_success
        )

        st.session_state.credit_success = None


    # LOAD DATA
    customers = customer_repository.get_all()
    sales = sales_repository.get_all()


    # FIND CUSTOMERS WITH OUTSTANDING CREDIT
    credit_customers = []

    for customer in customers:

        customer_credit_sales = [
            sale
            for sale in sales
            if (
                sale.customer_id == customer.id
                and sale.remaining_balance > 0
            )
        ]

        if customer_credit_sales:

            credit_customers.append(customer)


    # OUTSTANDING CREDIT SALES
    all_credit_sales = [
        sale
        for sale in sales
        if (
            sale.remaining_balance > 0
            and sale.customer_id is not None
        )
    ]


    # TOTAL OUTSTANDING CREDIT
    total_credit = sum(
        (
            sale.remaining_balance
            for sale in all_credit_sales
        ),
        Decimal("0.00"),
    )


    # CREDIT OVERVIEW
    st.subheader("Credit Overview")

    st.caption(
        "Current customer balances requiring collection."
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


    # CUSTOMER CREDIT
    if credit_customers:

        st.divider()

        st.subheader("Customer Credit")

        st.caption(
            "Select a customer to view their outstanding sales "
            "and record payments."
        )


        # CUSTOMER SELECTION
        customer_options = {
            customer.name: customer.id
            for customer in credit_customers
        }

        selected_customer_name = st.selectbox(
            "Customer",
            options=list(customer_options.keys()),
        )

        selected_customer_id = customer_options[
            selected_customer_name
        ]


        # SELECTED CUSTOMER
        selected_customer = customer_repository.get_by_id(
            selected_customer_id
        )


        # CUSTOMER SALES
        customer_sales = [
            sale
            for sale in sales
            if (
                sale.customer_id == selected_customer_id
                and sale.remaining_balance > 0
            )
        ]


        # CUSTOMER BALANCE
        customer_balance = sum(
            (
                sale.remaining_balance
                for sale in customer_sales
            ),
            Decimal("0.00"),
        )

        # OUTSTANDING SALES
        st.subheader("Outstanding Sales")

        st.caption(
            "Open a sale to view its products and record a payment."
        )


        for sale in sorted(
            customer_sales,
            key=lambda sale: sale.sale_date,
        ):

            with st.expander(
                f"{sale.sale_date.strftime('%d %b %Y')} | "
                f"Total: ₦{sale.total_amount:,.2f} | "
                f"Balance: ₦{sale.remaining_balance:,.2f}"
            ):

                # SALE SUMMARY
                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "Sale Total",
                        f"₦{sale.total_amount:,.2f}",
                    )

                with col2:

                    st.metric(
                        "Amount Paid",
                        f"₦{sale.amount_paid:,.2f}",
                    )

                with col3:

                    st.metric(
                        "Remaining",
                        f"₦{sale.remaining_balance:,.2f}",
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
                

                st.divider()


                # RECORD PAYMENT
                st.markdown("**Record Payment**")

                col1, col2 = st.columns(2)

                with col1:

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

                with col2:

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


                col1, col2 = st.columns(2)

                with col1:

                    payment_date = st.date_input(
                        "Payment Date",
                        value=datetime.now().date(),
                        key=f"payment_date_{sale.id}",
                    )

                with col2:

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


                    except Exception as exc:

                        st.error(
                            f"Could not record payment: {exc}"
                        )


    else:

        st.divider()

        st.success(
            "Credit looks healthy. There are no outstanding "
            "customer balances."
        )


    # PAYMENT HISTORY
    st.divider()

    st.subheader("Payment History")

    st.caption(
        "Recent payments recorded against customer credit."
    )


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


        payment_history = []

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


            payment_history.append(
                {
                    "Date": payment.payment_date.strftime(
                        "%d %b %Y"
                    ),
                    "Customer": customer_name,
                    "Amount": (
                        f"₦{payment.amount:,.2f}"
                    ),
                    "Method": payment.payment_method,
                    "Reference": (
                        payment.reference
                        if payment.reference
                        else "-"
                    ),
                }
            )


        if payment_history:

            payment_history_df = pd.DataFrame(
                payment_history
            )

            st.dataframe(
                payment_history_df,
                width="stretch",
                hide_index=True,
                height=350,
            )

        else:

            st.info(
                "No valid payment records were found."
            )


finally:

    db.close()