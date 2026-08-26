import streamlit as st

from src.database.session import get_db
from src.repositories.categories_repository import CategoryRepository
from src.services.category_services import CategoryService


st.set_page_config(
    page_title="Categories | Business Pulse",
    layout="wide",
)


st.title("Categories")
st.caption("Organize your products into categories.")


db = next(get_db())

try:
    category_repository = CategoryRepository(db)
    category_service = CategoryService(category_repository)

    # Add Category

    st.subheader("Add Category")

    with st.form("add_category_form"):

        name = st.text_input("Category name")

        description = st.text_area(
            "Description",
            placeholder="Optional",
        )

        submitted = st.form_submit_button("Add Category")

        if submitted:

            try:
                category = category_service.create_category(
                    name=name,
                    description=description.strip() or None,
                )

                db.commit()

                st.success(
                    f"Category '{category.name}' was created."
                )

                st.rerun()

            except ValueError as error:
                db.rollback()
                st.error(str(error))

    # Categories

    st.divider()

    st.subheader("Categories")

    categories = category_service.get_all_categories()

    if not categories:
        st.info("No categories found.")

    else:

        for category in categories:

            with st.container(border=True):

                st.write(f"**{category.name}**")

                if category.description:
                    st.caption(category.description)
                else:
                    st.caption("No description")

finally:
    db.close()