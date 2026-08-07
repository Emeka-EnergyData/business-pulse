from sqlalchemy import text
from src.database.connection import engine

def test_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        print(result.scalar())
        
if __name__ == "__main__":
    test_connection()