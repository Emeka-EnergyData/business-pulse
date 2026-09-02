import streamlit as st
from decimal import Decimal

from src.database.session import get_db
from src.repositories.product_repository import ProductRepository
from src.repositories.categories_repository import CategoryRepository
from src.services.product_service import ProductService
from src.services.category_services import CategoryService

st.set_page_config(
    page_title = "Products | Business Pulse",
    layout= "wide"
)

st.title("Products")
st.write("View products currently in your business.")

db = next(get_db())

try:
    product_repository = ProductRepository(db)
    category_repository = CategoryRepository(db)
    
    product_service = ProductService(product_repository)
    category_service = CategoryService(category_repository)
    
    
    st.subheader("Add Product")
    
    categories = category_service.get_all_categories()
    
    if not categories:
        st.warning("No categories exists yet. Create a category first")
    
    else:
        category_options = {
            category.name: category.id for category in categories
        }
        
        with st.form("add_product_form"):
            category_name = st.selectbox(
                "Category", list(category_options.keys())
            )
            
            name = st.text_input("Product name")
            
            description = st.text_area("Description")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                cost_price = st.number_input(
                    "Cost price", min_value = 0.0, step =100.0
                )
            with col2:
                minimum_price = st.number_input(
                    "Minimum price", min_value=0.0, step=100.0
                )
            with col3:
                target_price = st.number_input(
                    "Target price", min_value =0.0, step = 100.0
                )
                
            submitted = st.form_submit_button("Add Product")
            
            if submitted:
                
                if not name.strip():
                    st.error("Product name is required.")
                    
                else:
                    try:
                        product = product_service.create_product(
                            category_id=category_options[category_name],
                            name=name.strip(),
                            cost_price=Decimal(str(cost_price)),
                            target_price = Decimal(str(target_price)),
                            minimum_price= Decimal(str(minimum_price)),
                            description = description.strip() or None
                        )
                        db.commit()
                        
                        st.success(f"{product.name} was added successfully")
                        
                        st.rerun()
                    except ValueError as error:
                        db.rollback()
                        st.error(str(error))
    
    st.divider() 
    
    st.subheader("Products")
           
    products = product_service.get_all_products()
    
    if not products:
        st.info("No products found.")
        
    else:
        for product in products:
            with st.container(border = True):
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.write("**Product**")
                    st.write(product.name)
                    
                with col2:
                    st.write("**Stock**")
                    st.write(product.current_stock)
                    
                with col3:
                    st.write("**Cost Price**")
                    st.write(f"N {product.cost_price:,.2f}")
                            
                with col4:
                    st.write("**Target**")
                    st.write(f"N {product.target_price:,.2f}")
                with col5:
                    if product.is_active:
                        st.write("**Status**")
                        st.write("🟢 Active")
                        
                        if st.button("Deactivate", key=f"deactivate_{product.id}"):
                            try:
                                product_service.deactivate_product(product.id)
                                
                                db.commit()
                                
                                st.success(f"{product.name} was deactivated.")
                                
                                st.rerun()
                            
                            except ValueError as error:
                                db.rollback()
                                
                                st.error(str(error))
                                
                    else:
                        st.write("**Status**")
                        st.write("🔴 Inactive")
                        
                        if st.button("Reactivate", key=f"reactivate_{product.id}"):
                            
                            try:
                                product_service.reactivate_product(product.id)
                                
                                db.commit()
                                
                                st.success(f"{product.name} was reactivated.")
                                
                                st.rerun()
                                
                            except ValueError as error:
                                db.rollback()
                                st.error(str(error))
                    
finally:
    db.close()