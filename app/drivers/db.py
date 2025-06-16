from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from app.config import settings
from typing import AsyncGenerator

engine = create_async_engine(settings.DB_URL, pool_pre_ping=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@asynccontextmanager
async def db_context():
    async with AsyncSessionLocal() as session:
        yield session

@asynccontextmanager
async def db_transaction(expunge_all=True,flush=True)->AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session  
            if flush:
                await session.flush()
            if expunge_all:
                session.expunge_all()
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e


@asynccontextmanager
async def db_readonly()->AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def create_db_if_not_exists():
    from urllib.parse import urlparse
    from sqlalchemy import text
    url = urlparse(settings.DB_URL)
    db = url.path.lstrip('/')
    # no transaction
    engine = create_async_engine(url._replace(path='').geturl() , echo=True, future=True)
    # create db if not exists
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
            {"db_name": db}
        )
        exists = result.scalar()
        if not exists:
            async with engine.connect() as conn1:
                sql = text(f'CREATE DATABASE "{db}"')
                await conn1.execution_options(isolation_level="AUTOCOMMIT")
                await conn1.execute(sql)
        else:
            print(f"Database {db} already exists")
    await engine.dispose()


if __name__ == "__main__":
    import asyncio
    asyncio.run(create_db_if_not_exists())