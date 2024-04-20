from sqlalchemy import create_engine, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

Base = declarative_base()
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL


class DBSession:
    def __init__(self):
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            poolclass=pool.QueuePool,
            pool_size=10000,
            max_overflow=8000,
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.db = SessionLocal()

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()


def get_db():
    with DBSession() as db:
        yield db
