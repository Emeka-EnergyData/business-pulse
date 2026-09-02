import streamlit as st
from datetime import date, timedelta
from decimal import Decimal

import altair as alt
import pandas as pd

from src.database.session import get_db

from src.repositories.sales_repository import SalesRepository
from src.repositories.purchase_repository import PurchaseRepository

from src.services.reports_service import ReportsService
from src.ai.ollama_client import OllamaClient
from src.ai.insights import InsightsService
from src.ai.chatbot import BusinessChatService


# PAGE CONFIGURATION
st.set_page_config(
    page_title="Reports",
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


# PAGE HEADER
st.title("Reports")

st.caption(
    "Analyze sales, purchases, collections, and credit activity "
    "for a selected period."
)


# DATABASE
db = next(get_db())

try:

    # REPOSITORIES
    sales_repository = SalesRepository(db)
    purchase_repository = PurchaseRepository(db)

    # SERVICE
    reports_service = ReportsService(
        sales_repository=sales_repository,
        purchase_repository=purchase_repository,
    )


    # REPORT PERIOD
    st.subheader("Report Period")

    st.caption(
        "Choose the period you want to analyze."
    )

    col1, col2, col3 = st.columns([1, 1, 0.7])

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

    with col3:
        st.write("")
        st.write("")
        generate_report = st.button(
            "Generate Report",
            type="primary",
            use_container_width=True,
        )


    # VALIDATE DATE RANGE
    if start_date > end_date:

        st.error(
            "Start date cannot be after end date."
        )

    else:

        # GENERATE REPORT
        if generate_report:

            business_summary = reports_service.get_business_summary(
                start_date=start_date,
                end_date=end_date,
            )

            st.session_state.report_summary = business_summary
            st.session_state.report_start_date = start_date
            st.session_state.report_end_date = end_date

            # Clear old AI insights when a new report is generated
            st.session_state.pop("report_insights", None)

            st.rerun()


        # DISPLAY REPORT
        if "report_summary" in st.session_state:

            summary = st.session_state.report_summary

            report_start = st.session_state.report_start_date
            report_end = st.session_state.report_end_date


            # DAILY SALES
            daily_sales = reports_service.get_daily_sale(
                start_date=report_start,
                end_date=report_end,
            )


            # REPORT HEADER
            st.divider()

            st.subheader("Business Summary")

            st.caption(
                f"{report_start.strftime('%d %b %Y')} "
                f"to "
                f"{report_end.strftime('%d %b %Y')}"
            )


            # FINANCIAL CALCULATIONS
            total_sales = summary["total_sales"]
            total_purchases = summary["total_purchases"]

            gross_difference = (
                total_sales - total_purchases
            )


            # SALES AND BUSINESS KPIs
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Revenue",
                    f"₦{total_sales:,.2f}",
                )

            with col2:
                st.metric(
                    "Number of Sales",
                    summary["number_of_sales"],
                )

            with col3:
                st.metric(
                    "Average Sale",
                    f"₦{summary['average_sale']:,.2f}",
                )

            with col4:
                st.metric(
                    "Gross Difference",
                    f"₦{gross_difference:,.2f}",
                )


            # COLLECTION AND CREDIT KPIs
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Amount Collected",
                    f"₦{summary['total_paid']:,.2f}",
                )

            with col2:
                st.metric(
                    "Outstanding Credit",
                    f"₦{summary['total_credit']:,.2f}",
                )

            with col3:
                st.metric(
                    "Collection Rate",
                    f"{summary['collection_rate']:,.1f}%",
                )

            with col4:
                st.metric(
                    "Credit Rate",
                    f"{summary['credit_rate']:,.1f}%",
                )


            st.divider()


            # PURCHASE SUMMARY
            st.subheader("Purchases")

            st.caption(
                "Inventory purchases recorded during the selected period."
            )

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Number of Purchases",
                    summary["number_of_purchases"],
                )

            with col2:
                st.metric(
                    "Total Purchases",
                    f"₦{total_purchases:,.2f}",
                )


            st.info(
                "Gross Difference is the difference between revenue "
                "and recorded purchases for the selected period. "
                "It is an operational measure and is not the "
                "business's final accounting profit."
            )


            st.divider()


            # DAILY SALES
            st.subheader("Daily Sales")

            st.caption(
                "Daily sales revenue throughout the selected period."
            )


            if daily_sales:

                # Convert repository results into a lookup dictionary
                sales_by_date = {
                    row["date"]: row["total_sales"]
                    for row in daily_sales
                }


                # Create every date in the selected period.
                # Days without sales are represented as zero.
                number_of_days = (
                    report_end - report_start
                ).days + 1

                chart_data = [
                    {
                        "date": report_start + timedelta(days=i),
                        "sales": float(
                            sales_by_date.get(
                                report_start + timedelta(days=i),
                                Decimal("0.00"),
                            )
                        ),
                    }
                    for i in range(number_of_days)
                ]


                sales_chart_df = pd.DataFrame(chart_data)


                chart = (
                    alt.Chart(sales_chart_df)
                    .mark_line(
                        point=True,
                        strokeWidth=3,
                    )
                    .encode(
                        x=alt.X(
                            "date:T",
                            title=None,
                            axis=alt.Axis(
                                format="%d %b",
                                labelAngle=0,
                            ),
                        ),
                        y=alt.Y(
                            "sales:Q",
                            title="Revenue (₦)",
                            axis=alt.Axis(
                                format=",.0f",
                            ),
                        ),
                        tooltip=[
                            alt.Tooltip(
                                "date:T",
                                title="Date",
                                format="%d %b %Y",
                            ),
                            alt.Tooltip(
                                "sales:Q",
                                title="Revenue (₦)",
                                format=",.2f",
                            ),
                        ],
                    )
                    .properties(
                        height=320,
                    )
                )

                st.altair_chart(
                    chart,
                    width="stretch"
                )

            else:

                st.info(
                    "No sales recorded during this period."
                )


            st.divider()


            # AI BUSINESS INSIGHTS
            st.subheader("AI Business Insights")

            st.caption(
                "Let Business Pulse analyze the report and highlight "
                "important trends, concerns, and recommendations."
            )


            if st.button(
                "Generate AI Insights",
                type="primary",
            ):

                with st.spinner(
                    "Analyzing your business report..."
                ):

                    try:

                        ollama_client = OllamaClient()

                        insights_service = InsightsService(
                            ollama_client
                        )

                        insights = (
                            insights_service.analyze_business_report(
                                summary
                            )
                        )

                        st.session_state.report_insights = insights

                    except RuntimeError as exc:

                        st.error(
                            f"Unable to generate AI insights: {exc}"
                        )


            # DISPLAY SAVED AI INSIGHTS
            if "report_insights" in st.session_state:

                st.markdown("### Business Insights")

                st.write(
                    st.session_state.report_insights
                )
                
            st.divider()
            
            # ASK BUSINESS PULSE
            st.subheader("Ask Business Pulse")

            st.caption(
                "Ask questions about the selected business report "
                "in plain English."
            )

            # CHAT HISTORY
            if "report_chat_messages" not in st.session_state:

                st.session_state.report_chat_messages = []

            # DISPLAY CHAT HISTORY
            for message in st.session_state.report_chat_messages:

                with st.chat_message(message["role"]):

                    st.write(message["content"])

            # CHAT INPUT
            user_question = st.chat_input(
                "Ask about this report..."
            )

            if user_question:

                # Display user question
                with st.chat_message("user"):

                    st.write(user_question)

                # Save user question
                st.session_state.report_chat_messages.append(
                    {
                        "role": "user",
                        "content": user_question,
                    }
                )

                # Generate AI response
                with st.chat_message("assistant"):
                    with st.spinner("Business Pulse is thinking..."):

                        try:

                            ollama_client = OllamaClient()

                            chat_service = BusinessChatService(
                                ollama_client
                            )

                            response = chat_service.ask(
                                summary=summary,
                                user_question=user_question
                            )

                            st.write(response)

                            # Save AI response
                            st.session_state.report_chat_messages.append(
                                {
                                    "role": "assistant",
                                    "content": response,
                                }
                            )

                        except RuntimeError as exc:
                            st.error(
                                f"Unable to answer your question: {exc}"
                            )

        else:

            st.info(
                "Select a date range and generate a report."
            )


finally:

    db.close()