from sqlalchemy import create_engine
from app.models.models import Base
from app.config import settings
from argparse import ArgumentParser
from urllib.parse import urlparse

def create_db_if_not_exists(drop=False):
    url = urlparse(settings.DATABASE_URL)
    db = url.path.strip('/')
    engine = create_engine(url._replace(path='').geturl(), isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        result = conn.exec_driver_sql(f"SELECT datname FROM pg_database where datname like '{db}'")
        if result.rowcount == 0:
            print(f"Database {db} does not exist, creating it")
            conn.exec_driver_sql(f"CREATE DATABASE {db}")
        elif drop:
            print(f"Database {db} exists, dropping it")
            conn.exec_driver_sql(f"DROP DATABASE {db}")

def init_db(drop=False):
    create_db_if_not_exists(drop)
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    argparser = ArgumentParser(prog="init_db", description="Initialize database.")
    argparser.add_argument("--drop", action="store_true", help="Drop database")
    args = argparser.parse_args()
    init_db(args.drop)