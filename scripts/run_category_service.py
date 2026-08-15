from src.database.connection import SessionLocal
from src.repositories.categories_repository import CategoryRepository
from src.services.category_services import CategoryService


def main():
    db = SessionLocal()

    try:
        repository = CategoryRepository(db)
        service = CategoryService(repository)

        category = service.create_category(
            name="wpob",
            description="All types of shoes"
        )

        print("Category created successfully!")
        print(f"ID: {category.id}")
        print(f"Name: {category.name}")
        print(f"Description: {category.description}")
        
        retrieved = service.get_category(category.id)
        print("\nCategory retrieved successfully!")
        print(f"ID: {retrieved.id}")
        print(f"Name: {retrieved.name}")
        print(f"Description: {retrieved.description}")
        
        categories = service.get_all_categories()

        print("\nAll categories:")
        for item in categories:
            print(f"- {item.id} | {item.name}")

        updated = service.update_category(
            category.id,
            name="Peemium Shoes",
            description="Premium footwear"
        )

        print("\nCategory updated successfully!")
        print(f"ID: {updated.id}")
        print(f"Name: {updated.name}")
        print(f"Description: {updated.description}")
        
        deleted = service.delete_category(category.id)

        print("\nCategory deleted successfully!")
        print(f"Deleted: {deleted}")

    finally:
        db.close()


if __name__ == "__main__":
    main()