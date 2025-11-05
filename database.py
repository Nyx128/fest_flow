from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace with your actual PostgreSQL connection string
DATABASE_URL = "postgresql://fest_dev:dev_123@localhost/fest_flow"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This is the Base you imported in models.py
Base = declarative_base()