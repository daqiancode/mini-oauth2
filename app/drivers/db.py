from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from app.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 

@contextmanager
def db_context():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def db_transaction():
    db = SessionLocal()
    try:
        yield db
        db.flush()
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

@contextmanager
def db_readonly():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
