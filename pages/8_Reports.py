import streamlit as st
from datetime import date

from src.database.session import get_db

from src.repositories.sales_repository import SalesRepository
from src.repositories.purchase_repository import PurchaseRepository

from src.services.reports_service import ReportsService


st.set_page_config(
    page_title="Reports",
    layout="wide",
)

# Database

db = next(get_db())

try:
    
    # Repositories
    
    sales_repository = SalesRepository(db)
    purchase_repository = PurchaseRepository(db)

    # Service
    
    reports_service = ReportsService(
        sales_repository=sales_repository,
        purchase_repository=purchase_repository,
    )

    # Page Header
    
    st.title("Reports")
    st.write(
        "View sales, purchases, payments, and credit activity "
        "for a selected period."
    )

    st.divider()

    # Date Range
    
    st.subheader("Report Period")

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Start Date",
            value=date.today().replace(day=1),
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            value=date.today(),
        )

    if start_date > end_date:
        st.error("Start date cannot be after end date.")

    else:
            
        # Generate Report
    
        if st.button(
            "Generate Report",
            type="primary",
            use_container_width=True,
        ):

            business_summary = reports_service.get_business_summary(
                start_date=start_date,
                end_date=end_date,
            )

            st.session_state.report_summary = business_summary
            st.session_state.report_start_date = start_date
            st.session_state.report_end_date = end_date

            st.rerun()

        # Display Report
        
        if "report_summary" in st.session_state:

            summary = st.session_state.report_summary

            report_start = st.session_state.report_start_date
            report_end = st.session_state.report_end_date

            st.divider()

            st.subheader("Business Summary")

            st.caption(
                f"{report_start.strftime('%d %b %Y')} "
                f"to "
                f"{report_end.strftime('%d %b %Y')}"
            )

            # Sales Metrics
            
            st.markdown("### Sales")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Number of Sales",
                    summary["number_of_sales"],
                )

            with col2:
                st.metric(
                    "Total Sales",
                    f"₦{summary['total_sales']:,.2f}",
                )

            with col3:
                st.metric(
                    "Amount Paid",
                    f"₦{summary['total_paid']:,.2f}",
                )

            with col4:
                st.metric(
                    "Credit",
                    f"₦{summary['total_credit']:,.2f}",
                )

            st.divider()

            # Purchase Metrics
            
            st.markdown("### Purchases")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Number of Purchases",
                    summary["number_of_purchases"],
                )

            with col2:
                st.metric(
                    "Total Purchases",
                    f"₦{summary['total_purchases']:,.2f}",
                )

            st.divider()

            # Simple Financial Overview            

            st.markdown("### Financial Overview")

            total_sales = summary["total_sales"]
            total_purchases = summary["total_purchases"]

            gross_difference = (
                total_sales - total_purchases
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Revenue",
                    f"₦{total_sales:,.2f}",
                )

            with col2:
                st.metric(
                    "Purchases",
                    f"₦{total_purchases:,.2f}",
                )

            with col3:
                st.metric(
                    "Sales − Purchases",
                    f"₦{gross_difference:,.2f}",
                )

            st.info(
                "The Sales − Purchases figure is a simple difference "
                "between sales and purchase costs. It is not the "
                "business's final accounting profit."
            )

        else:

            st.info(
                "Select a date range and generate a report."
            )

finally:

    db.close()