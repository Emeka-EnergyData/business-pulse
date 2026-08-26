import streamlit as st

from src.database.session import get_db

from src.repositories.supplier_repository import SupplierRepository
from src.services.supplier_service import SupplierService


st.set_page_config(
    page_title="Suppliers",
    layout="wide",
)

# Session State

if "supplier_success" not in st.session_state:
    st.session_state.supplier_success = None

# Database

db = next(get_db())

try:
    
    # Repository
    
    supplier_repository = SupplierRepository(db)

    # Service
    
    supplier_service = SupplierService(
        supplier_repository
    )
    
    # Load Data
    
    suppliers = supplier_service.get_all_suppliers()

    # Page Header    

    st.title("Suppliers")
    st.write(
        "Manage suppliers and their contact information."
    )

    
    # Add Supplier
    
    st.subheader("Add Supplier")

    with st.form("add_supplier_form"):

        name = st.text_input(
            "Supplier Name",
            placeholder="Enter supplier name",
        )

        phone = st.text_input(
            "Phone",
            placeholder="Optional",
        )

        address = st.text_area(
            "Address",
            placeholder="Optional",
        )

        notes = st.text_area(
            "Notes",
            placeholder="Optional notes about this supplier",
        )

        submitted = st.form_submit_button(
            "Add Supplier",
            type="primary",
            use_container_width=True,
        )

        if submitted:

            try:

                supplier = supplier_service.create_supplier(
                    name=name,
                    phone=phone.strip() or None,
                    address=address.strip() or None,
                    notes=notes.strip() or None,
                )

                st.session_state.supplier_success = (
                    f"Supplier '{supplier.name}' "
                    "added successfully."
                )
                
                # Success Message
                    
                if st.session_state.supplier_success:
                
                    st.success(
                        st.session_state.supplier_success
                        )
                
                    st.session_state.supplier_success = None
                

                st.rerun()

            except ValueError as e:

                st.error(str(e))

            except Exception as e:

                st.error(
                    f"Could not add supplier: {e}"
                )

    
    # Supplier List    

    st.divider()

    st.subheader("Suppliers")

    if not suppliers:

        st.info(
            "No suppliers have been added yet."
        )

    else:

        for supplier in suppliers:

            with st.expander(
                supplier.name
            ):

                
                # Supplier Information
                

                col1, col2 = st.columns(2)

                with col1:

                    st.write(
                        f"**Phone:** "
                        f"{supplier.phone or 'Not provided'}"
                    )

                    st.write(
                        f"**Address:** "
                        f"{supplier.address or 'Not provided'}"
                    )

                with col2:

                    st.write(
                        f"**Notes:** "
                        f"{supplier.notes or 'None'}"
                    )

                    st.write(
                        f"**Created:** "
                        f"{supplier.created_at.strftime('%Y-%m-%d')}"
                    )

                # Edit Supplier                

                st.divider()

                st.write("### Edit Supplier")

                with st.form(
                    f"edit_supplier_form_{supplier.id}"
                ):

                    edit_name = st.text_input(
                        "Supplier Name",
                        value=supplier.name,
                        key=f"edit_name_{supplier.id}",
                    )

                    edit_phone = st.text_input(
                        "Phone",
                        value=supplier.phone or "",
                        key=f"edit_phone_{supplier.id}",
                    )

                    edit_address = st.text_area(
                        "Address",
                        value=supplier.address or "",
                        key=f"edit_address_{supplier.id}",
                    )

                    edit_notes = st.text_area(
                        "Notes",
                        value=supplier.notes or "",
                        key=f"edit_notes_{supplier.id}",
                    )

                    update = st.form_submit_button(
                        "Save Changes",
                        use_container_width=True,
                    )

                    if update:

                        try:

                            updated_supplier = (
                                supplier_service.update_supplier(
                                    supplier_id=supplier.id,
                                    name=edit_name,
                                    phone=edit_phone.strip() or None,
                                    address=edit_address.strip() or None,
                                    notes=edit_notes.strip() or None,
                                )
                            )

                            st.session_state.supplier_success = (
                                f"Supplier '{updated_supplier.name}' "
                                "updated successfully."
                            )

                            st.rerun()

                        except ValueError as e:

                            st.error(str(e))

                        except Exception as e:

                            st.error(
                                f"Could not update supplier: {e}"
                            )

                # Delete Supplier

                st.divider()

                st.write("### Delete Supplier")

                has_purchase_history = (
                    supplier_repository.has_purchase_history(
                        supplier.id
                    )
                )

                if has_purchase_history:

                    st.warning(
                        "This supplier cannot be deleted "
                        "because purchase history exists."
                    )

                else:

                    delete_confirm = st.checkbox(
                        "I understand that this supplier has no purchase history.",
                        key=f"delete_confirm_{supplier.id}",
                    )

                    if st.button(
                        "Delete Supplier",
                        key=f"delete_supplier_{supplier.id}",
                        use_container_width=True,
                        disabled=not delete_confirm,
                    ):

                        try:

                            deleted = (
                                supplier_service.delete_supplier(
                                    supplier.id
                                )
                            )

                            if deleted:

                                st.session_state.supplier_success = (
                                    f"Supplier '{supplier.name}' "
                                    "deleted successfully."
                                )
                                
                                

                                st.rerun()
                                
                                

                            else:

                                st.error(
                                    "Supplier could not be deleted."
                                )

                        except ValueError as e:

                            st.error(str(e))

                        except Exception as e:

                            st.error(
                                f"Could not delete supplier: {e}"
                            )
                    # Success Message
                        
        if st.session_state.supplier_success:
                    
            st.success(
                st.session_state.supplier_success
                        )
                    
            st.session_state.supplier_success = None
                        
finally:

    db.close()