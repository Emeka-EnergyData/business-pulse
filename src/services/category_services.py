from uuid import UUID

from src.database.models.category import Category
from src.repositories.categories_repository import CategoryRepository

class CategoryService:
    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository
        
    def create_category(self, name:str, description:str | None = None) -> Category:
        """Create a new category.
        :param name: The category name. 
        :param description:Optional category description
        :return: The created Category object
        """
        
        name= name.strip()
        
        if not name:
            raise ValueError("Category name cannot be empty")
        
        category = Category(
            name = name,
            description = description
        )
        
        return self.category_repository.create(category)
    
    def get_category(self, category_id:UUID) -> Category | None:
        """
        Retrieve all categories
        """
        
        return self.category_repository.get_by_id(category_id)
    
    def get_all_categories(self) -> list[Category]:
        return self.category_repository.get_all()
    
    def update_category(
        self,
        category_id: UUID,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> Category:
        """
        Update an existing category
        """
        category = self.category_repository.get_by_id(category_id)
        
        if category is None:
            raise ValueError(f"Category with ID {category_id} does not exist")
        
        if name is not None:
            name = name.strip()
            
            if not name:
                raise ValueError("Category name cannot be empty")
            
            category.name = name
            
        if description is not None:
            category.description = description
            
        return self.category_repository.update(category)
    
    def delete_category(self, category_id: UUID) -> bool:
        """
        Delete a category by ID
        """
        
        category = self.category_repository.get_by_id(category_id)
        
        if category is None:
            raise ValueError(f"Category with ID {category_id} does not exist")
        
        return self.category_repository.delete(category_id)
                    
            
        
        