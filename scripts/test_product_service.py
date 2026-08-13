from decimal import Decimal
from uuid import uuid4

from src.database.connection import SessionLocal
from src.services.category_services import CategoryService
from src.repositories.categories_repository import CategoryRepository
from src.repositories.product_repository import ProductRepository
from src.services.product_service import ProductService


def main():
    db = SessionLocal()

    try:
        category_repository = CategoryRepository(db)
        product_repository = ProductRepository(db)

        category_service = CategoryService(category_repository)
        product_service = ProductService(product_repository)

        # --------------------------------------------------
        # 1. Create a category for the product
        # --------------------------------------------------

        category = category_service.create_category(
            name="Test Shoes",
            description="Category for product service testing"
        )

        print("\n1. Category created")
        print(f"ID: {category.id}")
        print(f"Name: {category.name}")

        # --------------------------------------------------
        # 2. Create product
        # --------------------------------------------------

        product = product_service.create_product(
            category_id=category.id,
            name="Test Sneakers",
            cost_price=Decimal("10000.00"),
            target_price=Decimal("15000.00"),
            minimum_price=Decimal("12000.00"),
            description="Test product"
        )

        print("\n2. Product created")
        print(f"ID: {product.id}")
        print(f"Name: {product.name}")
        print(f"Cost price: {product.cost_price}")
        print(f"Target price: {product.target_price}")
        print(f"Minimum price: {product.minimum_price}")
        print(f"Current stock: {product.current_stock}")
        print(f"Active: {product.is_active}")

        # --------------------------------------------------
        # 3. Get product by ID
        # --------------------------------------------------

        retrieved = product_service.get_product(product.id)

        print("\n3. Product retrieved")
        print(f"ID: {retrieved.id}")
        print(f"Name: {retrieved.name}")

        # --------------------------------------------------
        # 4. Get all products
        # --------------------------------------------------

        products = product_service.get_all_products()

        print("\n4. All products")
        for item in products:
            print(
                f"- {item.id} | "
                f"{item.name} | "
                f"Stock: {item.current_stock} | "
                f"Active: {item.is_active}"
            )

        # --------------------------------------------------
        # 5. Get active products
        # --------------------------------------------------

        active_products = product_service.get_active_products()

        print("\n5. Active products")
        for item in active_products:
            print(
                f"- {item.id} | "
                f"{item.name} | "
                f"Active: {item.is_active}"
            )

        # --------------------------------------------------
        # 6. Update product
        # --------------------------------------------------

        updated = product_service.update_product(
            product.id,
            name="Updated Test Sneakers",
            description="Updated product description",
            target_price=Decimal("16000.00"),
            minimum_price=Decimal("13000.00")
        )

        print("\n6. Product updated")
        print(f"Name: {updated.name}")
        print(f"Description: {updated.description}")
        print(f"Cost price: {updated.cost_price}")
        print(f"Target price: {updated.target_price}")
        print(f"Minimum price: {updated.minimum_price}")

        # --------------------------------------------------
        # 7. Deactivate product
        # --------------------------------------------------

        deactivated = product_service.deactivate_product(product.id)

        print("\n7. Product deactivated")
        print(f"Name: {deactivated.name}")
        print(f"Active: {deactivated.is_active}")

        # --------------------------------------------------
        # 8. Verify inactive product is not in active products
        # --------------------------------------------------

        active_products_after_deactivation = (
            product_service.get_active_products()
        )

        found = any(
            item.id == product.id
            for item in active_products_after_deactivation
        )

        print("\n8. Active product verification")
        print(f"Product still active: {found}")

        # --------------------------------------------------
        # 9. Test invalid minimum price
        # --------------------------------------------------

        try:
            product_service.create_product(
                category_id=category.id,
                name="Invalid Product 1",
                cost_price=Decimal("10000.00"),
                target_price=Decimal("15000.00"),
                minimum_price=Decimal("9000.00")
            )

        except ValueError as e:
            print("\n9. Invalid minimum price correctly rejected")
            print(f"Error: {e}")

        # --------------------------------------------------
        # 10. Test invalid target price
        # --------------------------------------------------

        try:
            product_service.create_product(
                category_id=category.id,
                name="Invalid Product 2",
                cost_price=Decimal("10000.00"),
                target_price=Decimal("11000.00"),
                minimum_price=Decimal("12000.00")
            )

        except ValueError as e:
            print("\n10. Invalid target price correctly rejected")
            print(f"Error: {e}")

        # --------------------------------------------------
        # 11. Test invalid update
        # --------------------------------------------------

        try:
            product_service.update_product(
                product.id,
                minimum_price=Decimal("9000.00")
            )

        except ValueError as e:
            print("\n11. Invalid product update correctly rejected")
            print(f"Error: {e}")

        # --------------------------------------------------
        # 12. Test deactivating nonexistent product
        # --------------------------------------------------

       

        try:
            product_service.deactivate_product(uuid4())

        except ValueError as e:
            print("\n12. Nonexistent product correctly rejected")
            print(f"Error: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    main()