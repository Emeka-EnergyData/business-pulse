from src.database.base import Base 
import src.database.models

for table in Base.metadata.sorted_tables:
    print(f"Table: {table.name}")