import pytest
from backend.app.database import Base, engine, SessionLocal
from backend.app.seed_data import seed

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Seed data
    seed()

    yield

    # Drop tables after tests (optional cleanup)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Provides a fresh database session for each test."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()