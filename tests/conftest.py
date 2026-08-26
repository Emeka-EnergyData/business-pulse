import pytest
from collections.abc import Generator

from src.database.connection import TestSessionLocal

@pytest.fixture

def db_session() -> Generator:

    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()