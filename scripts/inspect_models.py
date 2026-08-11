from src.database.models import StockMovement

def inspect_stock_movement():
    table = StockMovement.__table__
    
    print(f"Table Name: {table.name}")
    print("Columns:")
    for column in table.columns:
        print(f"  - {column.name} ({column.type})")
        print(f"    Primary Key: {column.primary_key}")
        print(f"    Nullable: {column.nullable}")
        
    print("\nConstraints:")
    for constraint in table.constraints:
        print(f"  - {constraint.name}: {constraint}")

if __name__ == "__main__":
    inspect_stock_movement()