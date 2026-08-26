import streamlit as st

from src.database.session import get_db

from src.repositories.customer_repository import CustomerRepository


st.set_page_config(
    page_title="Customers",
    layout="wide",
)

# Session State

if "customer_success" not in st.session_state:
    st.session_state.customer_success = None

# Database

db = next(get_db())

try:

    customer_repository = CustomerRepository(db)

    # Page Header
    
    st.title("Customers")
    st.write("Manage customers and view their business activity.")

    # Add Customer
    
    st.subheader("Add Customer")

    with st.form("add_customer_form"):

        customer_name = st.text_input(
            "Customer Name",
            placeholder="Enter customer name",
        )

        phone = st.text_input(
            "Phone Number",
            placeholder="Optional",
        )

        address = st.text_area(
            "Address",
            placeholder="Optional",
        )

        submitted = st.form_submit_button(
            "Add Customer",
            use_container_width=True,
        )

        if submitted:

            if not customer_name.strip():

                st.error("Customer name is required.")

            else:

                try:

                    # Adjust these fields if your Customer
                    # model uses different column names.
                    from src.database.models.customer import Customer

                    customer = Customer(
                        name=customer_name.strip(),
                        phone=phone.strip() or None,
                        address=address.strip() or None,
                    )

                    customer_repository.create(customer)

                    st.session_state.customer_success = (
                        "Customer added successfully."
                    )
                    
                    # Success Message
                    if st.session_state.customer_success:
                    
                        st.success(st.session_state.customer_success)
                        st.session_state.customer_success = None
                                        
                    st.rerun()
                    
                except Exception as e:

                    db.rollback()

                    st.error(
                        f"Could not add customer: {e}"
                    )

    # Customer List
    
    st.divider()

    st.subheader("Customers")

    customers = customer_repository.get_all()

    if not customers:

        st.info(
            "No customers have been added yet."
        )

    else:

        for customer in customers:

            with st.container(border=True):

                col1, col2, col3, col4 = st.columns(
                    [3, 2, 3, 1]
                )

                with col1:

                    st.write(
                        f"**{customer.name}**"
                    )

                with col2:

                    st.write(
                        customer.phone
                        if customer.phone
                        else "No phone"
                    )

                with col3:

                    st.write(
                        customer.address
                        if customer.address
                        else "No address"
                    )

                with col4:

                    view_key = (
                        f"view_customer_{customer.id}"
                    )

                    if st.button(
                        "View",
                        key=view_key,
                        use_container_width=True,
                    ):

                        st.session_state[
                            "selected_customer_id"
                        ] = customer.id

                        st.rerun()

    
    # Selected Customer
    
    selected_customer_id = st.session_state.get(
        "selected_customer_id"
    )

    if selected_customer_id:

        customer = customer_repository.get_by_id(
            selected_customer_id
        )

        if customer:

            st.divider()

            st.subheader(
                f"Customer: {customer.name}"
            )

            # Customer Information
            
            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    f"**Phone:** "
                    f"{customer.phone or 'Not provided'}"
                )

            with col2:

                st.write(
                    f"**Address:** "
                    f"{customer.address or 'Not provided'}"
                )

            # Customer Actions
            
            st.divider()

            st.subheader("Customer Actions")

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "Edit Customer",
                    use_container_width=True,
                ):

                    st.session_state[
                        "editing_customer_id"
                    ] = customer.id

                    st.rerun()

            with col2:

                has_sales = customer_repository.has_sales(
                    customer.id
                )

                if has_sales:

                    st.caption(
                        "Customers with sales history "
                        "cannot be deleted."
                    )

                else:

                    if st.button(
                        "Delete Customer",
                        use_container_width=True,
                    ):

                        try:

                            customer_repository.delete(
                                customer.id
                            )

                            st.session_state[
                                "selected_customer_id"
                            ] = None

                            st.session_state[
                                "customer_success"
                            ] = (
                                "Customer deleted successfully."
                            )

                            st.rerun()

                        except Exception as e:

                            db.rollback()

                            st.error(
                                f"Could not delete customer: {e}"
                            )
            
            if st.session_state.customer_success:
                                        
                st.success(st.session_state.customer_success)
                st.session_state.customer_success = None
                                        
    
    # Edit Customer
    

    editing_customer_id = st.session_state.get(
        "editing_customer_id"
    )

    if editing_customer_id:

        customer = customer_repository.get_by_id(
            editing_customer_id
        )

        if customer:

            st.divider()

            st.subheader("Edit Customer")

            with st.form("edit_customer_form"):

                edited_name = st.text_input(
                    "Customer Name",
                    value=customer.name,
                )

                edited_phone = st.text_input(
                    "Phone Number",
                    value=customer.phone or "",
                )

                edited_address = st.text_area(
                    "Address",
                    value=customer.address or "",
                )

                col1, col2 = st.columns(2)

                with col1:

                    save_changes = st.form_submit_button(
                        "Save Changes",
                        use_container_width=True,
                    )

                with col2:

                    cancel_edit = st.form_submit_button(
                        "Cancel",
                        use_container_width=True,
                    )

                if cancel_edit:

                    st.session_state[
                        "editing_customer_id"
                    ] = None

                    st.rerun()

                if save_changes:

                    if not edited_name.strip():

                        st.error(
                            "Customer name is required."
                        )

                    else:

                        try:

                            customer.name = (
                                edited_name.strip()
                            )

                            customer.phone = (
                                edited_phone.strip()
                                or None
                            )

                            customer.address = (
                                edited_address.strip()
                                or None
                            )

                            customer_repository.update(
                                customer
                            )

                            st.session_state[
                                "editing_customer_id"
                            ] = None

                            st.session_state.customer_success = (
                                "Customer updated successfully."
                            )
                            
                                                
                            st.rerun()

                        except Exception as e:

                            db.rollback()

                            st.error(
                                f"Could not update customer: {e}"
                            )

finally:

    db.close()