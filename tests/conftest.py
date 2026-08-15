import pytest
from sqlalchemy.orm import Session

from src.database.connection import TestSessionLocal

@pytest.fixture

def db_session() -> Session:
    
    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()