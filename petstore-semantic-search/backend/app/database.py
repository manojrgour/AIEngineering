import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()
#DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./petstore.db")
DATABASE_URL = os.environ["DATABASE_URL"]

print("Using database:", DATABASE_URL)

if DATABASE_URL.startswith("sqlite"):
    # SQLite needs check_same_thread=False
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Postgres (and other DBs) should not use connect_args
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()