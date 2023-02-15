from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
from psycopg2.extensions import register_adapter, AsIs

#Define DB URL based on .env settings.
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOSTNAME}:{settings.DATABASE_PORT}/{settings.POSTGRES_DB}"

#Create a DB engine from the DB URL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

#Create the local DB session from the DB engine.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#Use this method to get the current DB Session when available.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

