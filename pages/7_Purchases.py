import streamlit as st
from datetime import date
from decimal import Decimal

from src.database.session import get_db

from src.repositories.purchase_repository import PurchaseRepository
from src.repositories.purchase_item_repository import PurchaseItemRepository
from src.repositories.product_repository import ProductRepository
from src.repositories.stock_movement_repository import StockMovementRepository
from src.repositories.supplier_repository import SupplierRepository

from src.services.purchase_service import PurchaseService
from src.services.purchase_item_service import PurchaseItemService


st.set_page_config(
    page_title="Purchases",
    layout="wide",
)

st.title("Purchases")

st.write("Record goods received from suppliers and update inventory.")
    
if "purchase_items" not in st.session_state:
    st.session_state["purchase_items"] = []

if "purchase_success" not in st.session_state:
    st.session_state["purchase_success"] = None

db = next(get_db())

try:
    # Repositories
    purchase_repository = PurchaseRepository(db)
    purchase_item_repository = PurchaseItemRepository(db)
    product_repository = ProductRepository(db)
    stock_movement_repository = StockMovementRepository(db)
    supplier_repository = SupplierRepository(db)

    # Services
    purchase_service = PurchaseService(purchase_repository)

    purchase_item_service = PurchaseItemService(
        purchase_item_repository=purchase_item_repository,
        purchase_repository=purchase_repository,
        product_repository=product_repository,
        stock_movement_repository=stock_movement_repository,
    )

    # Load data
    suppliers = supplier_repository.get_all()
    products = product_repository.get_active()

    st.subheader("Receive Stock")

    if not suppliers:
        st.warning("No suppliers found. Create a supplier first.")

    elif not products:
        st.warning("No active products found. Create an active product first.")

    else:

        supplier_options = {
            supplier.name: supplier.id for supplier in suppliers
        }
        
        supplier_name = st.selectbox(
                    "Supplier",
                    options=list(supplier_options.keys()),
                )
        
        purchase_date = st.date_input(
                    "Purchase Date",
                    value=date.today(),
                )
        
        notes = st.text_area(
                    "Notes",
                    placeholder="Optional notes about this purchase",
                )
        st.divider()

        st.subheader("Add Products")
        
        product_options = {
            f"{product.name}({product.id})": product.id for product in products
        }

        product_name = st.selectbox(
            "Product",
            options=list(product_options.keys()),
        )

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            step=1,
            value=1,
        )

        unit_cost = st.number_input(
            "Unit Cost",
            min_value=0.0,
            step=100.0,
            value=0.0,
        )

        if st.button("Add Item"):
            item = {
                "product_id":product_options[product_name],
                "product_name": product_name,
                "quantity":int(quantity),
                "unit_cost": Decimal(str(unit_cost))
            }
            
            st.session_state.purchase_items.append(item)
                        
            st.success(f"Added {quantity} x {product_name}")
            
        if st.session_state["purchase_items"]:
            
            st.divider()
            
            st.subheader("Items")
            
            total_purchase_value = Decimal("0.00")
            
            for index, item in enumerate(st.session_state["purchase_items"]):
                item_total = (item["quantity"] * item["unit_cost"])
                
                total_purchase_value += item_total
                
                col1, col2, col3, col4, col5 = st.columns([3, 1, 2, 2,1])
                
                with col1:
                    st.write(item["product_name"])
                    
                with col2:
                    st.write(item["quantity"])
            
                with col3:
                    st.write(f"N{item["unit_cost"]:,.2f}")
                    
                with col4:
                    st.write(f"N{item_total:,.2f}")
                
                with col5:
                    if st.button("Remove", key=f"remove_{index}"):
                        st.session_state.purchase_items.pop(index)
                        st.rerun()
            
            st.divider()
            
            st.write(
                f"**Total Purchase Value: "
                f"N {total_purchase_value:,.2f}**"
            )
            
            purchase_result = st.empty()
            if st.button(
                "Receive Purchase",
                type="primary",
                use_container_width=True
            ):
            
                try:
                    # Create purchase header
                    purchase = purchase_service.create_purchase(
                        supplier_id=supplier_options[supplier_name],
                        purchase_date=purchase_date,
                        notes=notes or None,
                    )
                    
                    # Create each purchase item
                    for item in st.session_state["purchase_items"]:
                        purchase_item = purchase_item_service.create_purchase_item(
                            purchase_id=purchase.id,
                            product_id=item["product_id"],
                            quantity=item["quantity"],
                            unit_cost=item["unit_cost"]
                        )
                    
                    st.session_state["purchase_success"] = (
                        "Purchase recorded and stock successfully received."
                                        )
                    st.session_state["purchase_items"] = []
                    
                    st.rerun()       

                except Exception as e:
                    st.error(f"Could not record purchase: {e}")
                    
        else:
            st.info("No products have been added to this purchase yet.")
    
    if st.session_state["purchase_success"]:
        st.divider()
        st.success(st.session_state["purchase_success"])
        st.session_state["purchase_success"] = None
        
    st.divider()
    
    st.subheader("Purchase History")
    
    purchases = purchase_repository.get_all()
    
    if not purchases:
            st.info("No purchase history yet.")
            
    else:
        for purchase in reversed(purchases):
            total_value = Decimal("0.00")
            
            for item in purchase.items:
                total_value += (item.quantity * item.unit_cost)
            
            with st.expander(
                f"{purchase.purchase_date} * " f"{purchase.supplier.name} * N{total_value:,.2f}"
            ):
                st.write(f"**Supplier:** {purchase.supplier.name}")
                st.write(f"**Purchase Date:** {purchase.purchase_date}")
                
                if purchase.notes:
                    st.write(f"**Notes:** {purchase.notes}")
                
                st.divider()
                
                header1, header2, header3, header4 =st.columns([3,1,2,2])
                
                with header1:
                    st.write("**Product**")
                    
                with header2:
                    st.write("**Quantity**")
                    
                with header3:
                    st.write("**Unit Cost**")
                    
                with header4:
                    st.write("**Total**")
                    
                for item in purchase.items:
                    item_total = (item.quantity * item.unit_cost)
                    
                    col1, col2, col3, col4 = st.columns([3, 1, 2, 2])
                
                    with col1:
                        st.write(item.product.name)
                    
                    with col2:
                        st.write(f"Qty: {item.quantity}")
                        
                    with col3:
                        st.write(f"N {item.unit_cost:,.2f}")
                        
                    with col4:
                        st.write(f"N {item_total:,.2f}")
                        
                st.divider()
                
                total_col1, total_col2 =st.columns([4,2])
                    
                with total_col2:
                    st.write(f"**Total Purchase: {total_value:,.2f}**")                    
                
finally:
    db.close()